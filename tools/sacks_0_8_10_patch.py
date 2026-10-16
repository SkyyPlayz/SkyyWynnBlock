"""Derive SkyySacks/build_skyysacks_0.8.10.py from the SET pin 0.8.9 (the GENERATED build_skyysacks_0.8.9.py; edit THIS file, then
regenerate: python tools/sacks_0_8_10_patch.py; never re-run sacks_0_8_9_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.9 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_10_patch.py   then   python SkyySacks/build_skyysacks_0.8.10.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.10 = FISH INTO THE FISHING BAG (round fish018, 2026-10-16). Skyy (screenshots: SkyyVoid Fishing bag 0 / 150, "Nothing to deposit (or this
category is full)", the inventory holds 2 caught fish): "fish not going in fishing bag." (docs/answered/bags.md 2026-10-16).
WHY: SackDefs.homeOf (the one category table) knew vanilla fish (Fish_*) and raw fish (Food_Fish_Raw*) but not OUR fish: SkyyFishing's
whole fish are SkyyFishing_Fish_<Species> - no rule matched ("SkyyFishing_" is not "Skyy_"), so homeOf answered null = no category: the
sweep, Deposit / Deposit all and auto-pickup skipped them. And a whole fish carries metadata (weight, length, catcher - its sale price and
fillets come from the weight): the pool only counts ids, so taking such a stack in as a plain count would have destroyed that value.
A. THE RULE: SkyyFishing_Fish_* (SackDefs.CATCH, SkyyFishing's own id pattern - every species it adds now or later) -> "Fishing", next to
   the vanilla Fish_* / Food_Fish_Raw* rule. Junk and Lost Property catches are vanilla items and already go to their own categories.
B. THE WEIGHT TRAVELS WITH THE FISH (no loss, no dupe): each whole fish in the Void keeps "grams,mm,catcher" in its profile's pool file
   (one meta line "~fish:<id>" = the entries, newest last; the count line stays the count). In: the fish's metadata must be exactly
   SkyyFishing's (SkyyFishing 0.1.8 fishing:fn:fishOf answers its entry; "" = a fish with no metadata) - anything else, or no SkyyFishing
   0.1.8, = the stack stays in the inventory (as before). Out (the page's take / Pick up all): the newest entry comes back as the same fish
   (fishing:fn:fishDoc rebuilds the document + tooltip: same weight, length, catcher), one fish per slot; a full storage or no SkyyFishing =
   the fish and its entry stay in the Void. More entries than fish (another mod took fish by id through sacks:fn:take - none does today) =
   the oldest entries are dropped at the next move; fewer = the rest come out as plain fish. Count + entries change in ONE SackPool lock.
C. AUTO-PICKUP: a caught fish lands in the HOTBAR (the game's pickup order) and the 2 s sweep only took the main inventory - the automatic
   sweep now also takes whole fish (SackDefs.CATCH only) from the hotbar and backpack, looking there first (a fish you took out lands in
   the main inventory and stays, the new catch goes in); every other item keeps the main-inventory-only rule. The kept rule is unchanged
   (take 3 fish out and 3 stay with you). Deposit all keeps its order (main inventory first).
D. LEVEL: with SkyyCollections the Fishing category's collected total = its total + the fish you LANDED (SkyyFishing 0.1.8
   fishing:fn:pond = the Pond Fish count of the active profile; absent = + 0) - landing fish levels the Fishing bag; taking out and
   depositing again never counts twice (it is the landed count, not deposits).
E. SAVED DATA: one new meta line kind in the pool file (~fish:<id>), only for profiles that store whole fish. ROLLBACK to 0.8.9: the meta
   lines are kept untouched (0.8.9 keeps every "~" line) but 0.8.9 cannot see whole fish as Fishing (they stay in the Void, invisible,
   until 0.8.10 is back) - TAKE FISH OUT before a rollback. Needs SkyyFishing 0.1.8 for B (without it fish stay in the inventory).
F. REVIEW FIXES (round fish018fix): (1) take-out: a throw while the fish is added to the storage = the fish goes back to the Void unless the
   storage count really grew (never lost, never doubled); (2) kept: a fish taken out keeps exactly the fish taken (the hotbar / backpack
   count is NOT made kept for fish - the sweep takes catches from there now, so fresh catches in the hotbar are still swept); (3) the
   hotbar / backpack fish sweep has an owner switch: Server Setup -> The Void -> "Catches go into the Void" (bags.fishSweep, default on;
   off = 0.8.9's main-inventory-only rule for fish too - e.g. to sell whole fish at the Fishing Bench without taking them out first).
   Known, not changed: a fish another mod takes by id (Bazaar bag sale, bag crafting) leaves its weight entry behind until the next move
   drops the oldest one; a fish refunded by id comes back plain (value can only go down, never a dupe).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.9.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.10.py"))
assert P.has('VERSION = "0.8.9"\n') and P.has("SackMig089") and not P.has("fishWithdraw"), "not the live generated SkyySacks 0.8.9"
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.10 = FISH INTO"):].rstrip() + "\n"

# ---------- header + version
P.rep('''   Undo or History puts them back; the marker stops a second run); saved best levels reached under 0.8.9 stay (levels never go down).
"""
''', '''   Undo or History puts them back; the marker stops a second run); saved best levels reached under 0.8.9 stay (levels never go down).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.9"\n', 'VERSION = "0.8.10"\n')
P.rep('''             (INV, "getHotbar"), (INV, "getBackpack"), (PLA, "getWindowManager"), (WM, "getWindows"), ("org.bson.BsonDocument", "isEmpty")):
    B.probe(pool, c, m)
''', '''             (INV, "getHotbar"), (INV, "getBackpack"), (PLA, "getWindowManager"), (WM, "getWindows"), ("org.bson.BsonDocument", "isEmpty")):
    B.probe(pool, c, m)
# 0.8.10: a whole fish's metadata goes through the fish bridge as JSON (BsonDocument.toJson / parse) - the stack is rebuilt with it
for c, m in (("org.bson.BsonDocument", "toJson"), ("org.bson.BsonDocument", "parse")):
    B.probe(pool, c, m)
''')

# ---------- F(3). the owner switch for the hotbar / backpack fish sweep (bound by the kit + read by SackCfg.linkKeys on every reload)
P.rep('''scfg.addField(CtField.make("public static volatile boolean CHEST_FIX = false;", scfg))
''', '''scfg.addField(CtField.make("public static volatile boolean CHEST_FIX = false;", scfg))
# 0.8.10 review fix: bags.fishSweep (Server Setup "Catches go into the Void", default ON) - the sweep takes whole fish from the hotbar / backpack
scfg.addField(CtField.make("public static volatile boolean FISH_SWEEP = true;", scfg))
''')
P.rep('''public static void linkKeys(java.util.Properties p, boolean first) {
  boolean v = boolKey(p, "bags.benchChests", false);
''', '''public static void linkKeys(java.util.Properties p, boolean first) {
  FISH_SWEEP = boolKey(p, "bags.fishSweep", true);   // 0.8.10 review fix
  boolean v = boolKey(p, "bags.benchChests", false);
''')
P.rep('''    + "," + @PKG@.SackCfg.pdSig();   // 0.8.0: the Void rows (levels, multipliers, gates, Omni)
''', '''    + "," + @PKG@.SackCfg.pdSig()   // 0.8.0: the Void rows (levels, multipliers, gates, Omni)
    + "," + @PKG@.SackCfg.FISH_SWEEP;   // 0.8.10 review fix: the fish sweep switch
''')
P.rep('''     "field:SackCfg.CHEST_FIX@config.properties:bags.benchChests"),
''', '''     "field:SackCfg.CHEST_FIX@config.properties:bags.benchChests"),
    # 0.8.10 review fix: live - the 2 s sweep reads it (and SweepTask.cfgSig re-sweeps on a change)
    ("bags.fishSweep", "Catches go into the Void", "bags", "bool", "true", "", "", "", "", "live",
     "On: caught fish go from the hotbar into the Fishing bag (take out to sell). Off: main inventory only",
     "field:SackCfg.FISH_SWEEP@config.properties:bags.fishSweep"),
''')

# ---------- A. the rule
P.rep('''  if (itemId.startsWith("Skyy_Sack_")) return null;
''', '''  if (itemId.startsWith("Skyy_Sack_")) return null;
  // 0.8.10 (Skyy "fish not going in fishing bag."): SkyyFishing's whole fish (SkyyFishing_Fish_<Species>) are Fishing like vanilla fish
  if (itemId.startsWith("SkyyFishing_Fish_")) return "Fishing";   // = SackDefs.CATCH (declared after homeOf)
''')
P.rep('''defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {''', '''# 0.8.10: SkyyFishing's whole-fish id pattern (its FishDefs.FISH = SkyyFishing_Fish_<Species>) - a catch whose weight the Void keeps
defs.addField(CtField.make('public static final String CATCH = "SkyyFishing_Fish_";', defs))
defs.addMethod(CtNewMethod.make("public static boolean isCatch(String id) { return id != null && id.startsWith(CATCH); }", defs))
defs.addMethod(CtNewMethod.make("""
public static String catOf(String itemId) {''')

# ---------- B. the fish entries in the pool file (meta line ~fish:<id>), all under SackPool's lock (the same as add)
P.rep('''# integration fix: true when the pool of key k is loaded''', '''# 0.8.10 THE WEIGHT TRAVELS WITH THE FISH: "~fish:<id>" = the entries ("grams,mm,catcher") of the whole fish of that id, newest last. The
# count line stays THE count; entries beyond it (fish another mod took by id) are dropped oldest first (fishFit), missing ones = plain fish.
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized java.util.ArrayList fishList(String k, String id) {
  java.util.ArrayList l = new java.util.ArrayList();
  pool(k);   // the pool file (count + meta lines) is loaded first - never an empty list read before the file
  java.util.Map mt = (java.util.Map) PMETA.get(k);
  Object v = mt == null ? null : mt.get("~fish:" + id);
  if (v == null) return l;
  String[] a = String.valueOf(v).split(";");
  for (int i = 0; i < a.length; i++) if (a[i].length() > 0) l.add(a[i]);
  return l;
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void fishSet(String k, String id, java.util.ArrayList l) {
  java.util.concurrent.ConcurrentHashMap mt = (java.util.concurrent.ConcurrentHashMap) PMETA.get(k);
  if (mt == null) {
    if (l.isEmpty()) return;
    mt = new java.util.concurrent.ConcurrentHashMap();
    PMETA.put(k, mt);
  }
  if (l.isEmpty()) mt.remove("~fish:" + id);
  else {
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < l.size(); i++) { if (i > 0) sb.append(';'); sb.append((String) l.get(i)); }
    mt.put("~fish:" + id, sb.toString());
  }
  if (mt.isEmpty()) PMETA.remove(k);
  DIRTY.put(k, Boolean.TRUE);
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized java.util.ArrayList fishFit(String k, String id) {
  java.util.ArrayList l = fishList(k, id);
  long have = get(k, id);
  boolean ch = false;
  while (!l.isEmpty() && (long) l.size() > have) { l.remove(0); ch = true; }
  if (ch) fishSet(k, id, l);
  return l;
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void fishIn(String k, String id, String e, long n) {
  if (n <= 0L) return;
  java.util.ArrayList l = fishFit(k, id);
  add(k, id, n);
  if (e == null || e.length() == 0) return;
  for (long i = 0L; i < n; i++) l.add(e);
  fishSet(k, id, l);
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized String fishOut(String k, String id) {
  if (get(k, id) <= 0L) return null;
  java.util.ArrayList l = fishFit(k, id);
  String e = "";
  if (!l.isEmpty()) { e = (String) l.remove(l.size() - 1); fishSet(k, id, l); }
  add(k, id, -1L);
  return e;
}\'\'\'), sp))
sp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static synchronized void fishBack(String k, String id, String e) {
  java.util.ArrayList l = fishFit(k, id);
  add(k, id, 1L);
  if (e == null || e.length() == 0) return;
  l.add(e);
  fishSet(k, id, l);
}\'\'\'), sp))
# integration fix: true when the pool of key k is loaded''')

# ---------- B / C. the stack side (SweepTask, before the sweep that uses it)
P.rep('''# sweep matching items into the pool. onlyCat == null''', '''# 0.8.10: a whole fish's entry through SkyyFishing 0.1.8's fishing:fn:fishOf ({id, metadata JSON}): "grams,mm,catcher", "" = no metadata
# (a plain fish), null = leave this stack alone (other metadata, or no SkyyFishing 0.1.8 to read it)
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String fishEntry(@IS@ it) {
  if (it == null || it.isEmpty() || !@PKG@.SackDefs.isCatch(it.getItemId())) return null;
  org.bson.BsonDocument md = it.getMetadata();
  if (md == null || md.isEmpty()) return "";
  Object b = System.getProperties().get("skyy.bridge");
  Object f = (b instanceof java.util.Map) ? ((java.util.Map) b).get("fishing:fn:fishOf") : null;
  if (!(f instanceof java.util.function.Function)) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { it.getItemId(), md.toJson() });
    return (r instanceof String) ? (String) r : null;
  } catch (Throwable t) { return null; }
}\'\'\'), swp))
# the fish of an entry: "" = a plain fish; else fishing:fn:fishDoc rebuilds its metadata (null = no SkyyFishing 0.1.8 - it stays in the Void)
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @IS@ fishStack(String id, String e) {
  if (id == null || e == null) return null;
  if (e.length() == 0) return new @IS@(id, 1);
  Object b = System.getProperties().get("skyy.bridge");
  Object f = (b instanceof java.util.Map) ? ((java.util.Map) b).get("fishing:fn:fishDoc") : null;
  if (!(f instanceof java.util.function.Function)) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { id, e });
    if (!(r instanceof String)) return null;
    return new @IS@(id, 1, org.bson.BsonDocument.parse((String) r));
  } catch (Throwable t) { return null; }
}\'\'\'), swp))
# how many fish of id the Void may take from storage + hotbar + backpack (stacks whose entry reads)
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long fishHave(@INV@ inv, String id) {
  if (inv == null || id == null) return 0L;
  @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  long n = 0L;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId()) || fishEntry(it) == null) continue;
      n += (long) it.getQuantity();
    }
  }
  return n;
}\'\'\'), swp))
# take up to n fish of id out of the slots (read back per slot) and book each with its entry; returns how many went in
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long fishTake(@IC@[] cs, String k, String id, long n) {
  long got = 0L;
  for (int c = 0; c < cs.length && got < n; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short sl = 0; sl < cap && got < n; sl++) {
      @IS@ it = cs[c].getItemStack(sl);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      String e = fishEntry(it);
      if (e == null) continue;
      int q = it.getQuantity();
      int want = (long) q < n - got ? q : (int) (n - got);
      @ISS@ tx = cs[c].removeItemStackFromSlot(sl, want);
      if (tx == null || !tx.succeeded()) continue;
      @IS@ rem = tx.getRemainder();
      int r = want - (rem == null ? 0 : rem.getQuantity());
      if (r > 0) { @PKG@.SackPool.fishIn(k, id, e, (long) r); got += (long) r; }
    }
  }
  return got;
}\'\'\'.replace("@ISS@", ISS)), swp))
# sweep matching items into the pool. onlyCat == null''')
P.rep('''  {IC}[] conts = allContainers ? new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }} : new {IC}[] {{ inv.getStorage() }};''',
      '''  // 0.8.10: the automatic sweep also takes whole fish from the hotbar + backpack (a catch lands in the hotbar; looked at FIRST, so a fish you
  // took out into the storage stays with you and the new catch goes in); everything else: storage only. Deposit all: storage first as before
  {IC}[] conts = allContainers ? new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }} : new {IC}[] {{ inv.getHotbar(), inv.getBackpack(), inv.getStorage() }};''')
P.rep('''      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      if (onlyCat != null && !onlyCat.equals(cat)) continue;''', '''      String cat = {PKG}.SackDefs.catOf(id);
      if (cat == null) continue;
      if (!allContainers && c < 2 && (!{PKG}.SackDefs.isCatch(id) || !{PKG}.SackCfg.FISH_SWEEP)) continue;   // 0.8.10: hotbar / backpack = fish only (switch: bags.fishSweep)
      if (onlyCat != null && !onlyCat.equals(cat)) continue;''')
P.rep('''      if (take <= 0) continue;
''', '''      if (take <= 0) continue;
      String fe = null;   // 0.8.10: a whole fish goes in with its entry (weight, length, catcher) or not at all
      if ({PKG}.SackDefs.isCatch(id)) {{ fe = fishEntry(it); if (fe == null) continue; }}
''')
P.rep('''        {PKG}.SackPool.add(k, id, (long) removed);
        used[ci] = used[ci] + (long) removed;''', '''        if (fe != null) {PKG}.SackPool.fishIn(k, id, fe, (long) removed);   // 0.8.10: count + entries in one lock
        else {PKG}.SackPool.add(k, id, (long) removed);
        used[ci] = used[ci] + (long) removed;''')

# ---------- B. out: one fish per slot, rebuilt from its entry (before withdraw, after the live-mirror declarations it calls)
P.rep('''# withdraw up to n of an item into STORAGE; returns how many actually left the pool''', '''# 0.8.10: whole fish out of the Void, one per slot, each rebuilt from its entry; a full storage / no SkyyFishing 0.1.8 = it stays in the Void
swp.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int fishWithdraw(@PLA@ p, String k, String id, int n) {
  @IC@ stor = p.getInventory().getStorage();
  int added = 0;
  for (int i = 0; i < n; i++) {
    String e = @PKG@.SackPool.fishOut(k, id);
    if (e == null) break;
    @IS@ st = fishStack(id, e);
    if (st == null) { @PKG@.SackPool.fishBack(k, id, e); break; }
    int before = countIn(stor, id);
    boolean ok = false;
    try {
      @IST@ tx = stor == null ? null : stor.addItemStack(st);
      @IS@ rem = tx == null ? null : tx.getRemainder();
      ok = tx != null && tx.succeeded() && (rem == null || rem.isEmpty());   // one fish: all or nothing
    } catch (Throwable t) {
      // review fix: the add threw - the fish is in the storage only if the storage count really grew; else it goes back (never lost / doubled)
      try { ok = countIn(stor, id) > before; } catch (Throwable t2) { ok = false; }
    }
    if (!ok) { @PKG@.SackPool.fishBack(k, id, e); break; }
    added++;
  }
  if (added > 0) {
    @PKG@.BagMirror.afterTake(k, id);
    // review fix: kept = exactly the fish taken (no hotbar / backpack raise: the sweep takes fresh catches from there for fish)
    @PKG@.SackPool.keep(k, id, (long) added);
  }
  return added;
}\'\'\'.replace("@IST@", IST)), swp))
# withdraw up to n of an item into STORAGE; returns how many actually left the pool''')
P.rep('''  int take = (long) n < have ? n : (int) have;
  {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, take));''', '''  if ({PKG}.SackDefs.isCatch(id)) return fishWithdraw(p, k, id, n);   // 0.8.10: each fish with its own weight
  int take = (long) n < have ? n : (int) have;
  {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, take));''')

# ---------- B. the page's Deposit (depositInv)
P.rep('''  long have = (long) countIn(inv, id, true);''', '''  boolean fish = @PKG@.SackDefs.isCatch(id);   // 0.8.10: whole fish go in with their entries
  long have = fish ? @PKG@.SweepTask.fishHave(inv, id) : (long) countIn(inv, id, true);''')
P.rep('''  long got = takePlain(conts(inv), id, want);
  if (got > 0L) {
    @PKG@.SackPool.add(k, id, got);''', '''  long got = fish ? @PKG@.SweepTask.fishTake(conts(inv), k, id, want) : takePlain(conts(inv), id, want);
  if (got > 0L) {
    if (!fish) @PKG@.SackPool.add(k, id, got);   // 0.8.10: fishTake booked the fish (count + entries) itself''')

# ---------- D. the Fishing level counts the fish you landed (SkyyFishing 0.1.8 fishing:fn:pond)
P.rep('''vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long total(java.util.UUID u, String k, int ci) {
  long t = collTotal(u, @PKG@.SackDefs.CATS[ci]);
  if (t >= 0L) return t;''', '''# 0.8.10: the fish LANDED on the active profile (SkyyFishing 0.1.8 fishing:fn:pond) for the Fishing category, 0 for the others / absent
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long landed(java.util.UUID u, int ci) {
  if (u == null || ci < 0 || ci >= @PKG@.SackDefs.CATS.length || !"Fishing".equals(@PKG@.SackDefs.CATS[ci])) return 0L;
  try {
    Object b = System.getProperties().get("skyy.bridge");
    Object f = (b instanceof java.util.Map) ? ((java.util.Map) b).get("fishing:fn:pond") : null;
    if (!(f instanceof java.util.function.Function)) return 0L;
    Object r = ((java.util.function.Function) f).apply(u);
    return (r instanceof Number) ? Math.max(0L, ((Number) r).longValue()) : 0L;
  } catch (Throwable t) { return 0L; }
}\'\'\'), vst))
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long total(java.util.UUID u, String k, int ci) {
  long t = collTotal(u, @PKG@.SackDefs.CATS[ci]);
  if (t >= 0L) return t + landed(u, ci);   // 0.8.10: + the fish you landed''')

assert P.s.count("FISH_SWEEP") == 5 and P.s.count("fishWithdraw(") == 2 and P.s.count("SackPool.fishIn(") == 2 and P.s.count("isCatch(") >= 6
P.finish()
