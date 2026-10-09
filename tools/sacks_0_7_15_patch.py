"""Derive SkyySacks/build_skyysacks_0.7.15.py from the SET pin 0.7.14 (edit THIS file, then regenerate: python tools/sacks_0_7_15_patch.py).
0.7.15 = HIDE THE OMNI BAG UNTIL UNLOCKED + T1 BAGS FROM FIBER + the page-update guard (Skyy 2026-10-09: "i see the omni bag, but no
other bags in the crafting table", "yes, hide the omni bag until unlocked (unlocked by unlocking all legendary bags", "lets use fiber
for T1 bags, not wool. make they easy to get.").

1. THE OMNI RECIPE NEEDS KNOWLEDGE. Skyy_Sack_Omni's Recipe gets KnowledgeRequired true (0.7.7-0.7.14: false, so every Workbench showed it
   before any bag was unlocked). KnowSync (the 2 s known-recipe sync that already owns the 20 tiered bag entries) now owns a 21st entry,
   Skyy_Sack_Omni: it is in a player's known set exactly while that set also gets all five Legendary bags (Skyy_Sack_<type>_Large) - so
   free-recipes mode (or no SkyyCollections) = known like every bag; collection mode = known once all five Legendary bag recipes are in
   coll:recipes. UpdateKnownRecipes is still sent only on a change (one helper KnowSync.next does the compare + the new set).
   SkyyCollections 0.2.7 lists no tier for the Omni (bagRank 5, coll:fn:where answers null), so the bag page and /craft say "unlocks with
   all 5 Legendary bags unlocked (k of 5)" instead of a collection tier.
   Players who own or crafted an Omni keep it (KnowSync never touches items). Known-set rule: the Omni entry is RECOMPUTED every sweep like
   the 20 bags - a player who somehow knew it (an admin /recipe learn; nobody learned it through the game before, it needed no knowledge)
   keeps it only while all five Legendary recipes are known. Reason: the bench, /craft and the bag page then always give the same answer
   from the same data, and an Omni already in a bag or inventory is never touched.
   /craft: the Crafting / Smithing / Farming filter (KnowSync.allowed) applies the Omni rule; the Collections tab offers the Omni only while
   it is unlocked AND one Legendary bag of each type is carried (the 0.7.7 carry rule kept); a locked click says why.
   Bag page: the Next line at Legendary and the Mythic ladder row show the Omni's unlock state (free / unlocked + carried n of 5 / unlocks
   with all 5 Legendary bags unlocked, k of 5). The Omni tooltip says how it unlocks.
2. PAGE-UPDATE GUARD (the queued 2026-10-08 suspect "profileNotice updates a page across the profile-switch world move"). Engine facts
   (bytecode, HytaleServer.jar): PageManager.customPage is only cleared by setPage / a client Dismiss; World.onSetupPlayerJoining only resets
   the page acknowledgements (clearCustomPageAcknowledgements); Store.removeEntity invalidates the entity's Ref. So a bag / craft page the
   client lost in a world move stays PageManager.getCustomPage() on the server, and ProcTask's profileNotice (the only SkyySacks page update
   that is not a click answer) would send UpdateCustomPage to a client with no page open = the client warning "Tried to update custom page
   while no custom page was open". Fix: each page remembers the entity Ref it was last built for (builtRef, set first thing in build());
   ProcTask.notice() sends the profile notice only while that Ref is still valid and is the player's current entity (same store + index).
   After a world move the old Ref is invalid -> no update; the next click rebuilds the page as before.
3. T1 BAGS FROM FIBER. The five Normal bags (Skyy_Sack_<type>_Small) = 20 Plant Fiber (Ingredient_Fibre: wild grass, moss, berry bushes)
   + 4 Sticks (Ingredient_Stick: bushes) at a Workbench, the same for every type (0.7.4-0.7.14: 3 Bolt of Wool + 4 of a per-type material:
   Copper Ingot / Oak Log / Bread / Bone Fragments / Light Leather). Unique and up unchanged. The bag table (BAG_BOLTS[0], BAG_MAT, the
   quantities) drives the item JSON AND the page's "how to get one" view, so they cannot disagree; build checks: both ids exist in Assets.zip
   and appear in a Server/Drops list; every Normal recipe is exactly fiber + sticks. Recipes ship in the jar (no saved data).
No saved-data format change; no new command, ECS system, event or setting.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.14.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.15.py")
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


assert 'VERSION = "0.7.14"' in s and "def bag_look(" in s and "omniUnlocked" not in s, "the source must be the generated 0.7.14 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")
GLB0 = s.count("registerGlobal(")

# ================= docstring + version =================
rep('"""SkyySacks 0.7.14 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.14.py           -> SkyySacks/SkyySacks-0.7.14.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.14.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF,
    '"""SkyySacks 0.7.15 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.15.py           -> SkyySacks/SkyySacks-0.7.15.jar   (deploys go through tools/deploy_set.py --yes)' + LF
    + '       python build_skyysacks_0.7.15.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world (never used)' + LF)
rep("a SwapTo lift (Simple 0.5 s, ItemAnimationId SackLift). Classes, ids, recipes, texts and saved data are 0.7.13's." + LF + '"""' + LF,
    "a SwapTo lift (Simple 0.5 s, ItemAnimationId SackLift). Classes, ids, recipes, texts and saved data are 0.7.13's." + LF
    + "0.7.15 (derived from 0.7.14 by tools/sacks_0_7_15_patch.py - edit the patch, not this file; Skyy 2026-10-09 \"yes, hide the omni bag" + LF
    + "until unlocked (unlocked by unlocking all legendary bags\"): the Omni recipe needs knowledge; KnowSync teaches Skyy_Sack_Omni exactly" + LF
    + "while all five Legendary bag recipes are known (free mode: always), so the Workbench, /craft and the bag page hide it until then; the" + LF
    + "bag page / /craft / tooltip say how it unlocks. Normal bags = 20 Plant Fiber + 4 Sticks (Skyy: \"lets use fiber for T1 bags, not wool\"). Page guard: ProcTask's profile notice only reaches a page built for the player's" + LF
    + "current entity Ref (a page the client lost in a world move gets no update). Saved data unchanged." + LF + '"""' + LF)
rep('VERSION = "0.7.14"', 'VERSION = "0.7.15"')

# ================= KnowSync: the Omni entry =================
rep('''ksync.addField(CtField.make("public static final String[] MANAGED = " + _jarr(MANAGED_IDS) + ";", ksync))
''', '''ksync.addField(CtField.make("public static final String[] MANAGED = " + _jarr(MANAGED_IDS) + ";", ksync))
# 0.7.15 (Skyy 2026-10-09 "hide the omni bag until unlocked (unlocked by unlocking all legendary bags"): the Omni recipe needs knowledge.
# LEGEND = the five Legendary bag ids (the Omni's unlock); SYNCED = MANAGED + the Omni = every known-set entry sync() owns. The Omni entry is
# recomputed every sweep like the bags: known exactly while the wanted set holds all of LEGEND (free mode: always).
LEGEND_IDS = ["Skyy_Sack_%s_%s" % (c, TOP_SUFFIX) for c in BAG_CATS]
assert all(i in MANAGED_IDS for i in LEGEND_IDS) and len(LEGEND_IDS) == len(BAG_CATS)
ksync.addField(CtField.make("public static final String[] LEGEND = " + _jarr(LEGEND_IDS) + ";", ksync))
ksync.addField(CtField.make("public static final String[] SYNCED = " + _jarr(MANAGED_IDS + [BAG_OMNI]) + ";", ksync))
# how many LEGEND ids a set holds (the wanted set of item ids)
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int legendIn(java.util.Set s) {
  if (s == null) return 0;
  int n = 0;
  for (int i = 0; i < LEGEND.length; i++) if (s.contains(LEGEND[i])) n++;
  return n;
}\'\'\'), ksync))
# how many Legendary bag recipes the player has unlocked (coll:recipes holds recipe ids); free mode = all
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int legendKnown(java.util.Set coll) {
  if (@PKG@.SackCfg.effFree()) return LEGEND.length;
  if (coll == null) return 0;
  int n = 0;
  for (int i = 0; i < LEGEND.length; i++) if (coll.contains(@PKG@.SackDefs.recipeOf(LEGEND[i]))) n++;
  return n;
}\'\'\'), ksync))
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean omniUnlocked(java.util.Set coll) {
  return legendKnown(coll) >= LEGEND.length;
}\'\'\'), ksync))
# the Omni's unlock state for the bag page (Next line + Mythic ladder row); carried = Legendary bag types carried (SweepTask.legendCount)
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String omniStatus(java.util.Set coll, int carried) {
  int all = LEGEND.length;
  if (@PKG@.SackCfg.effFree()) return "free on this server - one Legendary bag of each type (you carry " + carried + " of " + all + ")";
  int k = legendKnown(coll);
  if (k >= all) return "UNLOCKED - one Legendary bag of each type (you carry " + carried + " of " + all + ")";
  return "unlocks with all " + all + " Legendary bags unlocked (" + k + " of " + all + ")";
}\'\'\'), ksync))
# the Mythic ladder row on the bag page (one 26 px bold 15 label, no wrap): a short form of omniStatus so the row stays within the
# 0.7.14 row length (about 105 characters) at 1000 px (0.7.15 fixer: the full omniStatus made the row up to 128 characters)
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String omniRow(java.util.Set coll, int carried) {
  int all = LEGEND.length;
  if (@PKG@.SackCfg.effFree()) return "free here - you carry " + carried + " of " + all + " Legendary bag types";
  int k = legendKnown(coll);
  if (k >= all) return "UNLOCKED - you carry " + carried + " of " + all + " Legendary bag types";
  return "needs all " + all + " Legendary bags unlocked (" + k + " of " + all + ")";
}\'\'\'), ksync))
# the /craft answer to an Omni click that is not allowed (locked, or not every Legendary bag carried)
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String omniLockText(java.util.Set coll, int carried) {
  int all = LEGEND.length;
  if (!omniUnlocked(coll)) return "The Mythic Omni Bag unlocks when you have unlocked all " + all + " Legendary bags (" + legendKnown(coll) + " of " + all + ")";
  return "The Mythic Omni Bag needs one Legendary bag of each type (you carry " + carried + " of " + all + ")";
}\'\'\'), ksync))
# the new known set for sync(): null = every SYNCED entry already matches want (nothing to send); else known with each SYNCED entry set
# to want (no other entry touched)
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.HashSet next(java.util.Set known, java.util.Set want) {
  boolean diff = false;
  for (int i = 0; i < SYNCED.length && !diff; i++) {
    boolean has = known != null && known.contains(SYNCED[i]);
    if (has != want.contains(SYNCED[i])) diff = true;
  }
  if (!diff) return null;
  java.util.HashSet ns = known == null ? new java.util.HashSet() : new java.util.HashSet(known);
  for (int i = 0; i < SYNCED.length; i++) {
    if (want.contains(SYNCED[i])) ns.add(SYNCED[i]);
    else ns.remove(SYNCED[i]);
  }
  return ns;
}\'\'\'), ksync))
''')
rep('''  if (@PKG@.SackCfg.effFree()) {
    for (int i = 0; i < MANAGED.length; i++) out.add(MANAGED[i]);
    return out;
  }''', '''  if (@PKG@.SackCfg.effFree()) {
    for (int i = 0; i < MANAGED.length; i++) out.add(MANAGED[i]);
    out.add(@PKG@.SackDefs.OMNI);   // 0.7.15: free mode = the Omni is known like every bag
    return out;
  }''')
rep('''    String iid = itemOfRecipe(rid);
    if (isManaged(iid)) out.add(iid);
  }
  return out;
}\'\'\'), ksync))''', '''    String iid = itemOfRecipe(rid);
    if (isManaged(iid)) out.add(iid);
  }
  if (legendIn(out) >= LEGEND.length) out.add(@PKG@.SackDefs.OMNI);   // 0.7.15: all five Legendary bags known -> the Omni
  return out;
}\'\'\'), ksync))''')
rep('''  if (@PKG@.SackCfg.effFree()) return true;
  if (coll == null || bagItemId == null) return false;
  return coll.contains(@PKG@.SackDefs.recipeOf(bagItemId));''', '''  if (@PKG@.SackCfg.effFree()) return true;
  if (coll == null || bagItemId == null) return false;
  if (bagItemId.equals(@PKG@.SackDefs.OMNI)) return omniUnlocked(coll);   // 0.7.15
  return coll.contains(@PKG@.SackDefs.recipeOf(bagItemId));''')
rep('''  @PCD@ d = p.getPlayerConfigData();
  if (d == null) return false;
  java.util.Set known = d.getKnownRecipes();
  boolean diff = false;
  for (int i = 0; i < MANAGED.length && !diff; i++) {
    boolean has = known != null && known.contains(MANAGED[i]);
    if (has != want.contains(MANAGED[i])) diff = true;
  }
  if (!diff) return false;
  java.util.HashSet ns = known == null ? new java.util.HashSet() : new java.util.HashSet(known);
  for (int i = 0; i < MANAGED.length; i++) {
    if (want.contains(MANAGED[i])) ns.add(MANAGED[i]);
    else ns.remove(MANAGED[i]);
  }
  d.setKnownRecipes(ns);''', '''  @PCD@ d = p.getPlayerConfigData();
  if (d == null) return false;
  java.util.HashSet ns = next(d.getKnownRecipes(), want);   // 0.7.15: the 20 bags + the Omni (SYNCED)
  if (ns == null) return false;
  d.setKnownRecipes(ns);''')
rep('''# ones: Bronze armor, pies, ...) only when the player's known set holds its output (fixes spec 12.1). The Omni needs no knowledge.
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean allowed(@CRR@ r, java.util.UUID u, java.util.Set known, java.util.Set coll) {
  if (r == null) return false;
  if (!r.isKnowledgeRequired()) return true;
  @MQ@ po = r.getPrimaryOutput();
  String oid = po == null ? null : po.getItemId();
  if (oid == null) return false;
  if (isManaged(oid)) return @PKG@.SackCfg.effFree() || (coll != null && coll.contains(String.valueOf(r.getId())));
  return known != null && known.contains(oid);
}\'\'\'), ksync))''', '''# ones: Bronze armor, pies, ...) only when the player's known set holds its output (fixes spec 12.1). 0.7.15: the Omni (knowledge now)
# only while all five Legendary bag recipes are unlocked (omniUnlocked - the same answer sync() teaches the bench). allowedOut = the test
# on plain values (the harness runs it); allowed = it on a recipe.
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean allowedOut(boolean kr, String oid, String rid, java.util.Set known, java.util.Set coll) {
  if (!kr) return true;
  if (oid == null) return false;
  if (oid.equals(@PKG@.SackDefs.OMNI)) return omniUnlocked(coll);
  if (isManaged(oid)) return @PKG@.SackCfg.effFree() || (coll != null && coll.contains(rid));
  return known != null && known.contains(oid);
}\'\'\'), ksync))
ksync.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean allowed(@CRR@ r, java.util.UUID u, java.util.Set known, java.util.Set coll) {
  if (r == null) return false;
  if (!r.isKnowledgeRequired()) return true;
  @MQ@ po = r.getPrimaryOutput();
  String oid = po == null ? null : po.getItemId();
  return allowedOut(true, oid, String.valueOf(r.getId()), known, coll);
}\'\'\'), ksync))''')

# ================= bag page texts =================
rep('''  if (rank >= top) {
    int n = player == null ? 0 : @PKG@.SweepTask.legendCount(player.getInventory());
    return "Next: the Mythic Omni Bag - one Legendary bag of each type (you carry " + n + " of " + @PKG@.SackDefs.CATS.length + ")";
  }''', '''  if (rank >= top) {
    int n = player == null ? 0 : @PKG@.SweepTask.legendCount(player.getInventory());
    return "Next: the Mythic Omni Bag - " + @PKG@.KnowSync.omniStatus(@PKG@.KnowSync.collSet(u), n);   // 0.7.15: its unlock state
  }''')
rep('''  b.set("#SkyySNbL" + top + ".Text", @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) + " - " + num((long) @PKG@.SackDefs.CAP_OMNI) + " of each item, every bag type - one Legendary bag of each type (you carry " + lc + " of " + @PKG@.SackDefs.CATS.length + ")");''',
    '''  b.set("#SkyySNbL" + top + ".Text", @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) + " - " + num((long) @PKG@.SackDefs.CAP_OMNI) + " of each item, every bag type - " + @PKG@.KnowSync.omniRow(coll, lc));   // 0.7.15 (short form: the row has no wrap)''')

# ================= /craft =================
rep('''  this.omniOk = {PKG}.SweepTask.legendCount(p.getInventory()) >= {PKG}.SackDefs.CATS.length;''',
    '''  // 0.7.15: the Omni joins the Collections tab only while it is unlocked (all five Legendary bag recipes) AND every Legendary bag is carried
  this.omniOk = {PKG}.SweepTask.legendCount(p.getInventory()) >= {PKG}.SackDefs.CATS.length && {PKG}.KnowSync.omniUnlocked(this.coll);''')
rep('''      okR = collectionRecipes(u).contains(rid) || (rid.equals({PKG}.SackDefs.recipeOf({PKG}.SackDefs.OMNI)) && {PKG}.SweepTask.legendCount(p.getInventory()) >= {PKG}.SackDefs.CATS.length);''',
    '''      okR = collectionRecipes(u).contains(rid) || (rid.equals({PKG}.SackDefs.recipeOf({PKG}.SackDefs.OMNI)) && {PKG}.SweepTask.legendCount(p.getInventory()) >= {PKG}.SackDefs.CATS.length && {PKG}.KnowSync.omniUnlocked(collectionRecipes(u)));''')
rep('''    if (!okR) {{ this.info = "You have not unlocked this recipe"; rebuild(); return; }}''',
    '''    if (!okR) {{
      // 0.7.15: an Omni click says what is missing (all five Legendary bags unlocked / one of each carried)
      this.info = String.valueOf(r.getId()).equals({PKG}.SackDefs.recipeOf({PKG}.SackDefs.OMNI)) ? {PKG}.KnowSync.omniLockText(collectionRecipes(u), {PKG}.SweepTask.legendCount(p.getInventory())) : "You have not unlocked this recipe";
      rebuild();
      return;
    }}''')
rep('''    // 0.7.7 (spec 4): the Omni recipe (no knowledge needed) joins this tab while all five Legendary bags are carried - inventory crafting''',
    '''    // 0.7.7 (spec 4): the Omni recipe joins this tab while all five Legendary bags are carried - inventory crafting (0.7.15: and unlocked)''')

# ================= page guard: builtRef + ProcTask.notice =================
rep('''cpg.addField(CtField.make("public boolean omniOk;", cpg))
''', '''cpg.addField(CtField.make("public boolean omniOk;", cpg))
# 0.7.15 page guard: the entity Ref this page was last built for (ProcTask.notice updates the page only while it is the player's current one)
cpg.addField(CtField.make("public " + REF + " builtRef;", cpg))
''')
rep('''page.addField(CtField.make("public boolean carried;", page))
''', '''page.addField(CtField.make("public boolean carried;", page))
# 0.7.15 page guard (see CraftPage.builtRef)
page.addField(CtField.make("public " + REF + " builtRef;", page))
''')
rep('''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.SackPool.pkey(u);''', '''public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.SackPool.pkey(u);''')
rep('''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());''', '''public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  this.builtRef = ref;   // 0.7.15 page guard
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());''')
GUARD = '''# 0.7.15 PAGE GUARD (tools/sacks_0_7_15_patch.py docstring 2): PageManager keeps a page the client lost in a world move (customPage is only
# cleared by setPage / a client Dismiss; World.onSetupPlayerJoining only resets the acknowledgements) and Store.removeEntity invalidates the
# old entity Ref. sameEntry = the Ref a page was built for is still valid and is the player's current entity (same store + index).
ptk.addMethod(CtNewMethod.make(f"""
public static boolean sameEntry({REF} built, {REF} now) {{
  if (built == null || now == null) return false;
  if (built == now) return true;
  try {{ return built.isValid() && now.isValid() && built.getStore() == now.getStore() && built.getIndex() == now.getIndex(); }} catch (Throwable t) {{ return false; }}
}}""", ptk))
# the profile notice (the only SkyySacks page update that is not a click answer): 0 = no notice due, 1 = sent, 2 = skipped (stale page)
ptk.addMethod(CtNewMethod.make(f"""
public static int notice(Object pg, String k, {REF} r) {{
  if (pg instanceof {PKG}.CraftPage) {{
    {PKG}.CraftPage cp = ({PKG}.CraftPage) pg;
    if (cp.key == null || cp.key.equals(k)) return 0;
    if (!sameEntry(cp.builtRef, r)) return 2;
    cp.profileNotice(k);
    return 1;
  }}
  if (pg instanceof {PKG}.SacksPage) {{
    {PKG}.SacksPage sk = ({PKG}.SacksPage) pg;
    if (sk.key == null || sk.key.equals(k)) return 0;
    if (!sameEntry(sk.builtRef, r)) return 2;
    sk.profileNotice(k);
    return 1;
  }}
  return 0;
}}""", ptk))
'''
rep('''ptk.addMethod(CtNewMethod.make(f"""
public void run() {{''', GUARD + '''ptk.addMethod(CtNewMethod.make(f"""
public void run() {{''')
rep('''    Object pg = p.getPageManager().getCustomPage();
    if (pg instanceof {PKG}.CraftPage) {{
      {PKG}.CraftPage cp = ({PKG}.CraftPage) pg;
      if (cp.key != null && !cp.key.equals(k)) cp.profileNotice(k);
    }} else if (pg instanceof {PKG}.SacksPage) {{
      {PKG}.SacksPage sk = ({PKG}.SacksPage) pg;
      if (sk.key != null && !sk.key.equals(k)) sk.profileNotice(k);
    }}''', '''    notice(p.getPageManager().getCustomPage(), k, r);   // 0.7.15: only a page built for this entity Ref (never one lost in a world move)''')

# ================= the Omni item: KnowledgeRequired true + tooltip =================
rep('''    # 0.7.7: KnowledgeRequired sits in the item's Recipe block (the vanilla Armor_Bronze_Chest shape): true for the 20 tiered bags (taught
    # by KnowSync from the collection unlocks), false for the Omni.''', '''    # 0.7.7: KnowledgeRequired sits in the item's Recipe block (the vanilla Armor_Bronze_Chest shape): true for the 20 tiered bags (taught
    # by KnowSync from the collection unlocks); 0.7.15: true for the Omni too (KnowSync teaches it with all five Legendary bags).''')
rep('''# 0.7.7 the Mythic Omni Bag (spec 4): one Legendary bag of each type at a Workbench, no knowledge gate
_omni_in = [{"ItemId": "Skyy_Sack_%s_%s" % (c, TOP_SUFFIX), "Quantity": 1} for c in BAG_CATS]
files["Server/Item/Items/Utility/%s.json" % BAG_OMNI] = json.dumps(sack_item(BAG_OMNI, BAG_RARITY[-1][0], _omni_in, False, "SkyySacks"), indent=2)''',
    '''# 0.7.7 the Mythic Omni Bag (spec 4): one Legendary bag of each type at a Workbench; 0.7.15: KnowledgeRequired (Skyy 2026-10-09 "hide the
# omni bag until unlocked (unlocked by unlocking all legendary bags") - KnowSync teaches it while all five Legendary bag recipes are known
_omni_in = [{"ItemId": "Skyy_Sack_%s_%s" % (c, TOP_SUFFIX), "Quantity": 1} for c in BAG_CATS]
files["Server/Item/Items/Utility/%s.json" % BAG_OMNI] = json.dumps(sack_item(BAG_OMNI, BAG_RARITY[-1][0], _omni_in, True, "SkyySacks"), indent=2)''')
rep('''"bag you need to carry. Right-click to reach in; every bag type keeps its own tab."''',
    '''"bag you need to carry. Right-click to reach in; every bag type keeps its own tab. Unlocks when you have unlocked all %s Legendary bags."''')
rep('''          % (_NUMW.get(len(BAG_CATS), str(len(BAG_CATS))), format(CAPD["bag.omni"], ","), ", ".join(BAG_CATS[:-1]), BAG_CATS[-1]))''',
    '''          % (_NUMW.get(len(BAG_CATS), str(len(BAG_CATS))), format(CAPD["bag.omni"], ","), ", ".join(BAG_CATS[:-1]), BAG_CATS[-1],
             _NUMW.get(len(BAG_CATS), str(len(BAG_CATS)))))''')
rep('''# holds the previous tier; KnowledgeRequired true on exactly the 20 tiered bags and false on the Omni; the Omni takes one Legendary bag of''',
    '''# holds the previous tier; KnowledgeRequired true on all 21 bags (0.7.15: the Omni too); the Omni takes one Legendary bag of''')
rep('''    if sorted(i for i, n in items.items() if n["Recipe"]["KnowledgeRequired"]) != sorted(MANAGED_IDS) or items[BAG_OMNI]["Recipe"]["KnowledgeRequired"]:
        raise SystemExit("0.7.7 asset check: KnowledgeRequired must be true on exactly the 20 tiered bags and false on the Omni")''',
    '''    if sorted(i for i, n in items.items() if n["Recipe"]["KnowledgeRequired"] is True) != sorted(MANAGED_IDS + [BAG_OMNI]):
        raise SystemExit("0.7.15 asset check: KnowledgeRequired must be true on all 21 bags (the Omni too)")''')
rep('''    print("assets checked: %d bag items (20 knowledge-gated + the Omni), %d qualities, %d lang lines" % (len(items), len(quals), len(lang)))''',
    '''    print("assets checked: %d bag items (all knowledge-gated, the Omni too), %d qualities, %d lang lines" % (len(items), len(quals), len(lang)))''')

# ================= T1 BAGS FROM FIBER (Skyy 2026-10-09 "lets use fiber for T1 bags, not wool. make they easy to get.") =================
# The five Normal bags (Skyy_Sack_<type>_Small): BAG_BOLT_QTY Plant Fiber (Ingredient_Fibre - wild grass, moss, berry bushes) +
# BAG_MAT_QTY Sticks (Ingredient_Stick - bushes), the same for every type; no wool, no copper, no per-type material. Unique and up are
# unchanged (the previous bag + 6 mob-dropped fabric scraps). The Java "how to get one" view reads the same table (SackDefs.BOLT[0] /
# BOLTQ / BOLTN[0] = the fiber, MAT / MATQ / MATN = the sticks), so no class logic changes for this part.
rep('''# accessories. Normal = BAG_BOLT_QTY Bolt of Wool + BAG_MAT_QTY BAG_MAT (the 0.7.4 recipe; Wool Scraps drop from sheep -> Furniture Bench).''',
    '''# accessories. Normal = BAG_BOLT_QTY Bolt of Wool + BAG_MAT_QTY BAG_MAT (the 0.7.4 recipe; Wool Scraps drop from sheep -> Furniture Bench).
# 0.7.15 (Skyy 2026-10-09 "lets use fiber for T1 bags, not wool. make they easy to get."): Normal = 20 Plant Fiber + 4 Sticks for every
# type (BAG_BOLTS[0] = Ingredient_Fibre, BAG_MAT = Ingredient_Stick everywhere) - both drop from plants in the world, no mob, no bench.''')
rep('''BAG_MAT = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread", "Combat": "Ingredient_Bone_Fragment",
           "Smithing": "Ingredient_Leather_Light"}
BAG_BOLTS = ("Ingredient_Bolt_Wool", "Ingredient_Fabric_Scrap_Linen", "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Cindercloth")
BAG_BOLT_QTY, BAG_MAT_QTY = 3, 4     # the Normal recipe (unchanged since 0.7.4); SackDefs.BOLTQ / MATQ for the "how to get one" view''',
    '''T1_FIBRE, T1_STICK = "Ingredient_Fibre", "Ingredient_Stick"   # 0.7.15: Assets.zip ids (server.lang "Plant Fiber" / "Stick")
BAG_MAT = dict((c, T1_STICK) for c in ("Mining", "Foraging", "Farming", "Combat", "Smithing"))
BAG_BOLTS = (T1_FIBRE, "Ingredient_Fabric_Scrap_Linen", "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Cindercloth")
BAG_BOLT_QTY, BAG_MAT_QTY = 20, 4    # 0.7.15: the Normal recipe = 20 Plant Fiber + 4 Sticks; SackDefs.BOLTQ / MATQ for the "how to get one" view''')
rep('''ITEM_NAME = {"Ingredient_Bar_Copper": "Copper Ingot", "Wood_Oak_Trunk": "Oak Log", "Food_Bread": "Bread",
             "Ingredient_Bone_Fragment": "Bone Fragments", "Ingredient_Leather_Light": "Light Leather",
             "Ingredient_Bolt_Wool": "Bolt of Wool", "Ingredient_Fabric_Scrap_Linen": "Linen Scraps",''',
    '''ITEM_NAME = {"Ingredient_Fibre": "Plant Fiber", "Ingredient_Stick": "Stick", "Ingredient_Fabric_Scrap_Linen": "Linen Scraps",''')
rep('''assert cooked_py(BAG_MAT["Farming"]), "the Farming bag material (Food_Bread) is cooked food - it stays in the inventory (0.7.8)"''',
    '''assert not any(cooked_py(i) for i in list(BAG_MAT.values()) + list(BAG_BOLTS)), "0.7.15: no bag recipe material is food"''')
# the NPC-drop rule stays for the rarity-step scraps (Unique and up); the Normal materials must be in a world drop list instead
rep('''        unob = [i for i in BAG_BOLTS if i in ids and not _obtainable(i)]''',
    '''        unob = [i for i in BAG_BOLTS[1:] if i in ids and not _obtainable(i)]
        # 0.7.15: the Normal materials (fiber + sticks) drop from plants: each must be in some Server/Drops/ list (not only NPCs)
        _drops = [z.read(n).decode("utf-8-sig", "replace") for n in z.namelist() if n.startswith("Server/Drops/") and n.endswith(".json")]
        t1bad = [i for i in (T1_FIBRE, T1_STICK) if not any('"%s"' % i in t for t in _drops)]
        if t1bad:
            raise SystemExit("0.7.15: Normal bag material(s) no drop list gives: " + ", ".join(t1bad))
        print("Normal bag materials from world drops: %s in %d drop lists, %s in %d" % (ITEM_NAME[T1_FIBRE], sum('"%s"' % T1_FIBRE in t for t in _drops),
              ITEM_NAME[T1_STICK], sum('"%s"' % T1_STICK in t for t in _drops)))''')
rep('''    print("bag step materials obtainable from NPC drops: " + ", ".join(ITEM_NAME[i] for i in BAG_BOLTS))''',
    '''    print("bag step materials obtainable from NPC drops: " + ", ".join(ITEM_NAME[i] for i in BAG_BOLTS[1:]))''')
# MATN = the stick name in the plural for the page sentence ("20 Plant Fiber + 4 Sticks"); ITEM_NAME keeps the server.lang singular
rep('''defs.addField(CtField.make("public static final String[] MATN = " + _jarr([ITEM_NAME[BAG_MAT[c]] for c in BAG_CATS]) + ";", defs))''',
    '''ITEM_PLURAL = {"Ingredient_Stick": "Sticks"}   # 0.7.15
defs.addField(CtField.make("public static final String[] MATN = " + _jarr([ITEM_PLURAL.get(BAG_MAT[c], ITEM_NAME[BAG_MAT[c]]) for c in BAG_CATS]) + ";", defs))''')
rep('''# 0.7.5 / 0.7.7: the bag table (BAG_CATS / BAG_MAT / BAG_TIERS / BAG_HOLDS near the top). Normal = 3 Bolt of Wool + 4 BAG_MAT (the 0.7.4
# Small recipe),''', '''# 0.7.5 / 0.7.7: the bag table (BAG_CATS / BAG_MAT / BAG_TIERS / BAG_HOLDS near the top). Normal = 20 Plant Fiber + 4 Sticks (0.7.15;
# was 3 Bolt of Wool + 4 BAG_MAT),''')
# build check: every Normal recipe is exactly the fiber + sticks (no wool, no copper)
rep('''    if sorted(x["ItemId"] for x in items[BAG_OMNI]["Recipe"]["Input"]) != sorted("Skyy_Sack_%s_%s" % (c, TOP_SUFFIX) for c in BAG_CATS):''',
    '''    for cat in BAG_CATS:
        _t1 = sorted((x["ItemId"], x["Quantity"]) for x in items["Skyy_Sack_%s_%s" % (cat, BAG_TIERS[0][0])]["Recipe"]["Input"])
        if _t1 != sorted([(T1_FIBRE, BAG_BOLT_QTY), (T1_STICK, BAG_MAT_QTY)]):
            raise SystemExit("0.7.15 asset check: the Normal %s recipe must be %d Plant Fiber + %d Sticks, is %r" % (cat, BAG_BOLT_QTY, BAG_MAT_QTY, _t1))
    if sorted(x["ItemId"] for x in items[BAG_OMNI]["Recipe"]["Input"]) != sorted("Skyy_Sack_%s_%s" % (c, TOP_SUFFIX) for c in BAG_CATS):''')
# KnowSync header comment: it owns 21 entries now
rep('''# SkyySacks owns exactly the 20 tiered bag item ids (MANAGED) in every player's known-recipe set''',
    '''# SkyySacks owns exactly the 20 tiered bag item ids (MANAGED; 0.7.15: + Skyy_Sack_Omni = SYNCED) in every player's known-recipe set''')

# ================= self-checks =================
assert "Ingredient_Bolt_Wool" not in s[s.index("BAG_CATS = ("):s.index("BAG_HOLDS = {")], "0.7.15: no wool in the T1 table"
assert 'VERSION = "0.7.15"' in s and s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0 and s.count("registerGlobal(") == GLB0, \
    "no new command, ECS system or event"
assert "MANAGED.length && !diff" not in s and s.count("next(d.getKnownRecipes(), want)") == 1
assert "profileNotice(k)" in s and s.count("cp.profileNotice(k);") == 1 and s.count("sk.profileNotice(k);") == 1, "profileNotice only through notice()"
for _a, _b in (("public static final String[] LEGEND", "public static int legendIn("), ("public static int legendIn(", "public static java.util.HashSet wanted("),
               ("public static int legendKnown(", "public static boolean omniUnlocked("), ("public static boolean omniUnlocked(", "public static String omniStatus("),
               ("public static boolean omniUnlocked(", "public static String omniLockText("), ("public static java.util.HashSet next(", "public static boolean sync("),
               ("public static boolean omniUnlocked(", "public static boolean unlocked("), ("public static boolean allowedOut(", "public static boolean allowed("),
               ("public static String omniStatus(", "public static String nextLine("), ("public static String omniStatus(", "public static String omniRow("), ("public static String omniRow(", "KnowSync.omniRow(coll, lc)"), ("public static String omniLockText(", 'okR = {PKG}.KnowSync.allowed'),
               ("public static boolean sameEntry(", "public static int notice("), ("public static int notice(", "    notice(p.getPageManager().getCustomPage(), k, r);"),
               ('cpg.addField(CtField.make("public " + REF + " builtRef;"', "public void build({REF} ref"), ('page.addField(CtField.make("public " + REF + " builtRef;"', "public void build(@REF@ ref")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:60], _b[:60])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
