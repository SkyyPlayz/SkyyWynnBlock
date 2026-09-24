"""Derive SkyySacks/build_skyysacks_0.7.4.py from 0.7.3 (edit THIS file, then regenerate: python tools/sacks_0_7_4_patch.py).
0.7.4 = THE CAMPFIRE ACCESSORY COMES BACK (Skyy 2026-09-24, HANDOFF "Feedback on the build round"): "add the campfire accessory back
for quick inventory cooking as it already limits what you can make ... 50% xp and 75% of your normal buffs when using it, so its an
emergency cook". SkyyCooking 0.1.1 owns the Grade and the XP (bridge contract in SkyyCooking/build_skyycooking_0.1.1.py docstring);
this mod only shows the tab, crafts from inventory + bags and hands out the id SkyyCooking returns.
 - Campfire tab (id K:camp, after Farming): shown while acc:has:<uuid> lists a Skyy_Accessory_Campfire[_T<n>] (CraftPage.campfireTier -
   a separate parse, so the Campfire stays a RETIRED bench in accessories(): it still unlocks nothing in Crafting / Smithing / Farming,
   search or Collections, and tableOnly() still keeps every cooked dish out of those tabs).
 - Recipes (CraftPage.campRecipes): the Campfire-bench recipes ("Campfire".equals(BenchRequirement.id), the test SkyyCooking's
   isCampfire makes) up to the accessory tier whose primary output is in the bridge String cook:campfire:ids - exactly the dishes
   cook:fn:campfire accepts. Without SkyyCooking (no cook:campfire:ids) every Campfire-bench recipe (the 3 vanilla ones), plain
   output, no XP. recipesFor skips the tableOnly() filter for this tab only.
 - Crafting is instant, the Crafting-tab click path unchanged (inventory + bags, counted removal, surplus returned, storage first,
   crafts.log). After the materials are removed and `done` is known, CraftPage.campCall calls cook:fn:campfire ONCE per click:
   apply(Object[]{UUID, String.valueOf(recipe.getId()), Integer done, settled pkey, Boolean creative}) on the world thread (the contract's
   suggested call). A String answer that names a loaded item replaces the PRIMARY output id (same quantity); a missing Function, null,
   a non-String, an unknown item id or a throw gives the plain output. Cooking XP (x0.5) is paid inside that call by SkyyCooking; the
   Campfire tab does NOT report skill:fn:craftxp (SkyyCooking owns Cooking XP; without it the tab pays no XP at all).
 - Tab text: "Campfire accessory = emergency cook: 50% Cooking XP, 75% of your cooking bonus. A Cooking Bench gives the full Grade and
   XP." (set() text, so the comma and colon are safe); without SkyyCooking it says plain food and no Cooking XP. Each row shows what a
   craft gives right now through a PREVIEW call (crafts 0 = no XP, no chat): "- comes out Grade 4" / "- comes out plain".
 - The click re-checks the accessory and the recipe (acc:has can change while the page is open) before anything moves.
Everything else in 0.7.3 is untouched: tabs, search (Crafting + Smithing + Farming only), settledKey / profile:busy gates, bench link,
Furnace / Tannery queues and Smithing XP, config switch, /craft <words>.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.3.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.4.py")
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


# ---------------- docstring + version ----------------
rep('"""SkyySacks 0.7.3 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.3.py            -> SkyySacks/SkyySacks-0.7.3.jar' + LF
    + '       python build_skyysacks_0.7.3.py --deploy   -> also',
    '"""SkyySacks 0.7.4 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.4.py            -> SkyySacks/SkyySacks-0.7.4.jar' + LF
    + '       python build_skyysacks_0.7.4.py --deploy   -> also')
rep('Tannery tab has a Refresh button instead of the ~2 s self-refresh (periodic page updates make PageManager drop clicks).' + LF + '"""',
    'Tannery tab has a Refresh button instead of the ~2 s self-refresh (periodic page updates make PageManager drop clicks).' + LF
    + '0.7.4 (derived from 0.7.3 by tools/sacks_0_7_4_patch.py - edit the patch, not this file): Campfire accessory tab (Skyy 2026-09-24:' + LF
    + 'the Campfire accessory is back as an emergency cook) - shown while acc:has lists Skyy_Accessory_Campfire_T<n>, after Farming; lists' + LF
    + 'exactly the Campfire-bench recipes whose output is in SkyyCooking\'s cook:campfire:ids (without SkyyCooking: every Campfire-bench' + LF
    + 'recipe, plain output, no XP); instant from inventory + bags like Crafting; each click calls cook:fn:campfire once after the materials' + LF
    + 'are removed and gives the id it returns instead of the primary output (null / missing / unknown item = plain output); SkyyCooking pays' + LF
    + 'the Cooking XP (x0.5) and grades the dish (x0.75 of the Cooking bonus); the tab does not report skill:fn:craftxp. The Campfire stays a' + LF
    + 'retired bench everywhere else (Crafting / Smithing / Farming / search / Collections keep no cooked food).' + LF + '"""')
rep('VERSION = "0.7.3"', 'VERSION = "0.7.4"')

# ---------------- constants + probes ----------------
rep('BTP = "com.hypixel.hytale.protocol.BenchType"' + LF,
    'BTP = "com.hypixel.hytale.protocol.BenchType"' + LF
    + '# 0.7.4: the creative flag passed to cook:fn:campfire (SkyyCooking 0.1.1 reads the same enum)' + LF
    + 'GM  = "com.hypixel.hytale.protocol.GameMode"' + LF)
rep('             (CTX, "getInputString"), (UCB, "set"), (MQ, "getItemId")):' + LF + '    B.probe(pool, c, m)' + LF,
    '             (CTX, "getInputString"), (UCB, "set"), (MQ, "getItemId")):' + LF + '    B.probe(pool, c, m)' + LF
    + '# 0.7.4: Campfire tab (creative flag for cook:fn:campfire, primary output swap)' + LF
    + 'for c, m in ((PLA, "getGameMode"), (GM, "Creative"), (CRR, "getOutputs"), (CRR, "getPrimaryOutput"), (CRR, "getBenchRequirement")):' + LF
    + '    B.probe(pool, c, m)' + LF)

# ---------------- retiredBench comment: the Campfire keeps being retired in the merged tabs ----------------
rep('# 0.7.3: bench accessories retired with the table-only Alchemy / Cooking call (orchestrator decision 4: the Campfire too - its 3 recipes' + LF
    + '# are cooked food). Their acc:has entries unlock nothing and their recipes never craft instantly.' + LF,
    '# 0.7.3: bench accessories retired with the table-only Alchemy / Cooking call (orchestrator decision 4: the Campfire too - its 3 recipes' + LF
    + '# are cooked food). Their acc:has entries unlock nothing and their recipes never craft instantly.' + LF
    + '# 0.7.4: the Campfire STAYS retired here (Crafting / Smithing / Farming / search / Collections keep no cooked food); its accessory only' + LF
    + '# opens the separate Campfire tab (campfireTier / campRecipes below), where SkyyCooking grades the dish.' + LF)

# ---------------- CraftPage: Campfire tab helpers (before buildTabs / recipesFor / build / handleDataEvent use them) ----------------
CAMP_HELPERS = r'''# ---- 0.7.4 Campfire accessory tab (Skyy 2026-09-24: the Campfire accessory comes back as an emergency cook; SkyyCooking 0.1.1 contract) ----
cpg.addField(CtField.make("public static long CAMPWARN;", cpg))
# highest Skyy_Accessory_Campfire tier listed in acc:has:<uuid> (0 = none). A separate parse on purpose: accessories() keeps skipping the
# retired Campfire, so it never unlocks recipes in the merged tabs, search or Collections - it only opens the Campfire tab.
cpg.addMethod(CtNewMethod.make("""
public static int campfireTier(java.util.UUID u) {
  int best = 0;
  try {
    Object b = System.getProperties().get("skyy.bridge");
    Object v = (b instanceof java.util.Map) ? ((java.util.Map) b).get("acc:has:" + u.toString()) : null;
    if (v == null) return 0;
    String[] parts = String.valueOf(v).split(",");
    for (int i = 0; i < parts.length; i++) {
      String id = parts[i].trim();
      if (!id.startsWith("Skyy_Accessory_")) continue;
      String tail = id.substring("Skyy_Accessory_".length());
      String bench = tail;
      int tier = 1;
      int ti = tail.lastIndexOf("_T");
      if (ti > 0 && ti + 2 < tail.length()) {
        try { tier = Integer.parseInt(tail.substring(ti + 2)); bench = tail.substring(0, ti); } catch (Throwable e) { }
      }
      if (bench.equalsIgnoreCase("Campfire") && tier > best) best = tier;
    }
  } catch (Throwable x) { }
  return best;
}""", cpg))
# the dish ids SkyyCooking's cook:fn:campfire accepts (bridge String cook:campfire:ids, comma separated); null = SkyyCooking not loaded
cpg.addMethod(CtNewMethod.make("""
public static java.util.HashSet campIds() {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    Object v = (b instanceof java.util.Map) ? ((java.util.Map) b).get("cook:campfire:ids") : null;
    if (!(v instanceof String)) return null;
    java.util.HashSet s = new java.util.HashSet();
    String[] parts = ((String) v).split(",");
    for (int i = 0; i < parts.length; i++) if (parts[i].trim().length() > 0) s.add(parts[i].trim());
    return s;
  } catch (Throwable t) { return null; }
}""", cpg))
# a Campfire-bench recipe: the same test SkyyCooking's isCampfire makes ("Campfire".equals(BenchRequirement.id))
cpg.addMethod(CtNewMethod.make(f"""
public static boolean campfireRecipe({CRR} r) {{
  if (r == null) return false;
  {BRQ}[] br = r.getBenchRequirement();
  for (int i = 0; br != null && i < br.length; i++) if (br[i] != null && "Campfire".equals(br[i].id)) return true;
  return false;
}}""", cpg))
# the Campfire tab's recipe ids: Campfire-bench recipes up to the accessory tier whose primary output is in cook:campfire:ids (exactly the
# dishes cook:fn:campfire accepts); without SkyyCooking every Campfire-bench recipe (the vanilla ones - plain output, no XP)
cpg.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet campRecipes(java.util.UUID u) {{
  java.util.TreeSet ids = new java.util.TreeSet();
  int tier = campfireTier(u);
  if (tier <= 0) return ids;
  java.util.HashSet ok = campIds();
  java.util.Iterator it = {CRR}.getAssetMap().getAssetMap().values().iterator();
  while (it.hasNext()) {{
    {CRR} r = ({CRR}) it.next();
    {BRQ}[] br = r.getBenchRequirement();
    if (br == null) continue;
    boolean fits = false;
    for (int i = 0; i < br.length; i++) {{
      if (br[i] == null || !"Campfire".equals(br[i].id)) continue;
      int need = br[i].requiredTierLevel; if (need <= 0) need = 1;
      if (need <= tier) fits = true;
    }}
    if (!fits) continue;
    if (ok != null) {{
      {MQ} po = r.getPrimaryOutput();
      String oid = po == null ? null : po.getItemId();
      if (oid == null || !ok.contains(oid)) continue;
    }}
    ids.add(r.getId());
  }}
  return ids;
}}""", cpg))
# Grade of a graded dish id (Skyy_Cook_<dish>_G<c>); 0 = plain / not a graded id
cpg.addMethod(CtNewMethod.make("""
public static int gradeOfId(String id) {
  if (id == null || !id.startsWith("Skyy_Cook_")) return 0;
  int g = id.lastIndexOf("_G");
  if (g < 0 || g + 2 >= id.length()) return 0;
  try { return Integer.parseInt(id.substring(g + 2)); } catch (Throwable t) { return 0; }
}""", cpg))
# THE bridge call (SkyyCooking 0.1.1 cook:fn:campfire, its suggested SkyySacks call): world thread, AFTER the materials were removed, once
# per click with the finished crafts (crafts 0 = preview: no XP, no chat). Returns the item id to give INSTEAD of the primary output (same
# quantity), or null = give the plain output (Function missing, null / non-String answer, an id that is not a loaded item, a throw).
# SkyyCooking pays the Cooking XP (x campfire.xpFactor) inside the call and applies its own busy / profile-key / creative rules.
cpg.addMethod(CtNewMethod.make(f"""
public static String campCall({PLA} p, java.util.UUID u, String k, {CRR} r, int crafts) {{
  try {{
    Object f = {PKG}.SackPool.bridge().get("cook:fn:campfire");
    if (!(f instanceof java.util.function.Function)) return null;
    Boolean cr = null;
    try {{ if (p != null) cr = Boolean.valueOf(p.getGameMode() == {GM}.Creative); }} catch (Throwable gm) {{ cr = null; }}
    Object got = ((java.util.function.Function) f).apply(new Object[] {{ u, String.valueOf(r.getId()), Integer.valueOf(crafts), k, cr }});
    if (!(got instanceof String)) return null;
    String id = ((String) got).trim();
    if (id.length() == 0 || {PKG}.ProcBench.item(id) == null) return null;
    return id;
  }} catch (Throwable t) {{
    long now = System.currentTimeMillis();
    if (now - CAMPWARN > 60000L) {{ CAMPWARN = now; {PKG}.SackPool.warn("campfire tab: cook:fn:campfire failed (plain output given): " + t); }}
    return null;
  }}
}}""", cpg))
# what a craft on this row gives right now (PREVIEW call, crafts 0) - appended to the row name
cpg.addMethod(CtNewMethod.make(f"""
public static String campRowNote({PLA} p, java.util.UUID u, String k, {CRR} r) {{
  if (campIds() == null) return "  - plain food (SkyyCooking is not installed)";
  int g = gradeOfId(campCall(p, u, k, r, 0));
  return g > 0 ? ("  - comes out Grade " + g) : "  - comes out plain";
}}""", cpg))
# the tab's emergency-cook line (Skyy: 50% XP, 75% of the buffs the Cooking skill adds); shown with set(), so commas and colons are safe
cpg.addMethod(CtNewMethod.make("""
public static String campNote() {
  if (campIds() == null) return "Campfire accessory = quick emergency cooking: plain food and no Cooking XP (SkyyCooking is not installed).";
  return "Campfire accessory = emergency cook: 50% Cooking XP, 75% of your cooking bonus. A Cooking Bench gives the full Grade and XP.";
}""", cpg))
'''
rep('# collection unlocks published by SkyyCollections via the JVM bridge: "coll:recipes:<uuid>" -> "id,id,id"' + LF,
    CAMP_HELPERS + '# collection unlocks published by SkyyCollections via the JVM bridge: "coll:recipes:<uuid>" -> "id,id,id"' + LF)

# ---------------- tabs: Campfire after Farming ----------------
rep('  if (accTier(acc, "Farmingbench") > 0) t.add(new String[] {{ "A:farm", "Farming" }});' + LF,
    '  if (accTier(acc, "Farmingbench") > 0) t.add(new String[] {{ "A:farm", "Farming" }});' + LF
    + '  // 0.7.4: the Campfire accessory (emergency cook through SkyyCooking) - its own tab, never merged' + LF
    + '  if (campfireTier(u) > 0) t.add(new String[] {{ "K:camp", "Campfire" }});' + LF)

# ---------------- recipesFor: Campfire tab, no tableOnly filter for it only ----------------
blk('public java.util.ArrayList recipesFor(String tabId, java.util.UUID u) {{', [
    ('  }} else if (tabId.startsWith("C:")) {{' + LF + '    ids.addAll(collectionRecipes(u));' + LF + '  }}' + LF,
     '  }} else if (tabId.startsWith("C:")) {{' + LF + '    ids.addAll(collectionRecipes(u));' + LF
     + '  }} else if (tabId.equals("K:camp")) {{' + LF + '    ids.addAll(campRecipes(u));' + LF + '  }}' + LF),
    ('  boolean timed = tabId.startsWith("P:");' + LF,
     '  boolean timed = tabId.startsWith("P:");' + LF
     + '  // 0.7.4: the Campfire tab is the ONE instant tab that shows Campfire (timed, retired-bench) recipes - campRecipes picked them' + LF
     + '  boolean camp = tabId.equals("K:camp");' + LF),
    ('    if (!timed && tableOnly(rc)) continue;' + LF,
     '    if (!timed && !camp && tableOnly(rc)) continue;' + LF
     + '    if (camp && !campfireRecipe(rc)) continue;' + LF),
])

# ---------------- build(): the emergency-cook line, per-row preview, empty text ----------------
blk('public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{', [
    (r'''  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 22); Text: \\"Materials are counted from your inventory and your magic bags.\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");''' + LF,
     r'''  b.appendInline("#SkyyCraft", "Label {{ Anchor: (Height: 22); Text: \\"Materials are counted from your inventory and your magic bags.\\"; Style: (FontSize: 13, TextColor: #9fb8d0, HorizontalAlignment: Center); }}");
  // 0.7.4 Campfire tab: the emergency-cook line (text by set(), so the comma and colon are safe - the search info label pattern)
  boolean campTab = this.tab != null && this.tab.equals("K:camp");
  if (campTab) {{
    b.appendInline("#SkyyCraft", "Label #SkyyCCampNote {{ Anchor: (Height: 24); Text: \\"\\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffc080, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.set("#SkyyCCampNote.Text", campNote());
  }}
'''),
    ('    int lim = limit(r, mats);' + LF + '    StringBuilder need = new StringBuilder();' + LF,
     '    int lim = limit(r, mats);' + LF
     + '    // 0.7.4: what a Campfire-tab craft gives right now (cook:fn:campfire preview - no XP, no chat)' + LF
     + '    String cnote = campTab ? campRowNote(p, u, k, r) : "";' + LF
     + '    StringBuilder need = new StringBuilder();' + LF),
    ('{PKG}.SacksPage.safe(pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : ""))',
     '{PKG}.SacksPage.safe(pretty(outId) + (outq != null && outq.getQuantity() > 1 ? " x" + outq.getQuantity() : "") + cnote)'),
    (': "No recipes here yet.")',
     ': (campTab ? "No campfire dishes are loaded." : "No recipes here yet."))'),
], after='public boolean handleProc(')

# ---------------- handleDataEvent: re-check, cook:fn:campfire, output swap, no craftxp for the Campfire tab ----------------
blk('public void handleDataEvent({REF} ref, {ST} st, String data) {{', [
    ('    {CRR} r = ({CRR}) this.rows.get(idx);' + LF,
     '    {CRR} r = ({CRR}) this.rows.get(idx);' + LF
     + '    // 0.7.4 Campfire tab: still equipped and still a Campfire-bench recipe at click time (acc:has can change while the page is open)' + LF
     + '    boolean campTab = "K:camp".equals(this.tab);' + LF
     + '    if (campTab && (campfireTier(u) <= 0 || !campfireRecipe(r))) {{ this.info = "equip the Campfire accessory in your accessory bag to cook here"; rebuild(); return; }}' + LF),
    ('    if ((outs == null || outs.length == 0) && outq != null) outs = new {MQ}[] {{ outq }};' + LF + '    int given = 0;' + LF,
     '    if ((outs == null || outs.length == 0) && outq != null) outs = new {MQ}[] {{ outq }};' + LF
     + '    // 0.7.4: ONE cook:fn:campfire call per click, after the materials were removed, with the finished crafts and the settled key;' + LF
     + '    // its String answer replaces the primary output id (same quantity). null = plain output. SkyyCooking pays the Cooking XP.' + LF
     + '    String campId = null;' + LF
     + '    if (campTab && done > 0) campId = campCall(p, u, k, r, done);' + LF
     + '    int given = 0;' + LF),
    ('        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(outs[k].getItemId(), (int) total));' + LF,
     '        String gid = outs[k].getItemId();' + LF
     + '        if (campId != null && outq != null && gid.equals(outq.getItemId())) gid = campId;' + LF
     + '        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(gid, (int) total));' + LF),
    ('    {PKG}.CraftLog.write(k, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());' + LF,
     '    if (campTab) audit.append(" campfire=").append(campId == null ? "plain" : campId);' + LF
     + '    {PKG}.CraftLog.write(k, String.valueOf(r.getId()), qty, done, flag, given, audit.toString());' + LF),
    ('    if (done > 0) {{' + LF + '      try {{' + LF + '        Object xf = {PKG}.SackPool.bridge().get("skill:fn:craftxp");' + LF,
     '    // 0.7.4: not for the Campfire tab - SkyyCooking pays its Cooking XP inside cook:fn:campfire (and without SkyyCooking it pays none)' + LF
     + '    if (done > 0 && !campTab) {{' + LF + '      try {{' + LF + '        Object xf = {PKG}.SackPool.bridge().get("skill:fn:craftxp");' + LF),
    ('    String nm = pretty(outq == null ? "?" : outq.getItemId());' + LF,
     '    String nm = pretty(outq == null ? "?" : outq.getItemId());' + LF
     + '    if (campTab) {{ int cg = gradeOfId(campId); nm = nm + (cg > 0 ? " Grade " + cg : " (plain)"); }}' + LF),
], after='public boolean handleProc(')

# ---------------- plugin ready line ----------------
rep('ready - /pd, /craft (Crafting, Smithing, Farming, search, timed Furnace/Tannery queues - Furnace pays Smithing XP, Collections), right-click',
    'ready - /pd, /craft (Crafting, Smithing, Farming, Campfire accessory tab - emergency cook graded by SkyyCooking cook:fn:campfire, search, timed Furnace/Tannery queues - Furnace pays Smithing XP, Collections), right-click')

# ---------------- checks ----------------
assert 'VERSION = "0.7.4"' in s
assert s.count('"K:camp"') == 5, "K:camp tab id count (buildTabs, recipesFor x2, build, handleDataEvent): %d" % s.count('"K:camp"')
i_camp = s.index("public static int campfireTier(java.util.UUID u) {")
for later in ("public java.util.ArrayList buildTabs(", "public java.util.ArrayList recipesFor(", "public void build({REF} ref,",
              "public void handleDataEvent({REF} ref,"):
    # CraftPage's build / handleDataEvent (SacksPage has methods with the same signatures earlier in the file)
    assert i_camp < s.index(later, s.index("public boolean handleProc(") if later.startswith("public void") else 0), \
        "campfire helpers must come before " + later
assert s.index("public static java.util.HashSet campIds() {") < s.index("public static java.util.TreeSet campRecipes(")
assert s.index("public static int gradeOfId(String id) {") < s.index("public static String campRowNote(")
assert s.index("public static String campCall(") < s.index("public static String campRowNote(")
assert s.index("public static boolean campfireRecipe(") < s.index("public static java.util.TreeSet campRecipes(")
assert s.index('cpg.addField(CtField.make("public static long CAMPWARN;", cpg))') < s.index("public static String campCall(")
assert s.index("public static String settledKey(java.util.UUID u) {") < i_camp
# the Campfire stays retired everywhere else: merged tabs, search, Collections keep no cooked food
assert 'id.equalsIgnoreCase("Campfire"));' in s and "    if (retiredBench(bench)) continue;" in s, "Campfire no longer retired in accessories()"
assert "    if (!timed && !camp && tableOnly(rc)) continue;" in s
assert s.count("    if (tableOnly(rc)) continue;") == 1, "search lost its tableOnly filter"
assert "if (done > 0 && !campTab) {{" in s and s.count('get("skill:fn:craftxp")') == 2, "craftxp call (instant craft + Furnace drain)"
assert s.count('get("cook:fn:campfire")') == 1 and s.count("campCall(p, u, k, r, done)") == 1 and s.count("campCall(p, u, k, r, 0)") == 1
assert "#SkyyCCampNote" in s and "#Skyy_" not in s
# every 0.7.3 profile / busy rule untouched
assert s.count("public static String settledKey(java.util.UUID u) {") == 1, "settledKey changed"
assert 'b.get("profile:busy:" + u.toString()) != null) return null;' in s, "busy gate lost"
assert "    String k = {PKG}.SackPool.settledKey(u);" + LF + "    if (k == null) {{ this.info = \"bags paused" in s, "craft click not on settledKey"
assert s.count("{BT}.Validating") == 1 and s.count('.append("@SearchQuery", "#SkyyCSearch.Value")') == 2, "search bindings"
assert "cp.live(" not in s and "public void live(" not in s, "periodic refresh came back"

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
