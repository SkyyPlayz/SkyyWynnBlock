"""Derive SkyyGear/build_skyygear_0.3.2.py from the LIVE 0.3.1 (build_skyygear_0.3.1.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_1_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_3_2_patch.py      then      python SkyyGear/build_skyygear_0.3.2.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.2.py

0.3.2 = THE EXACT LOST TOOL (lean round). Skyy's words (docs/answered/gear.md 2026-10-13 LOST TOOL, word for word):
  "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"
Built on the LIVE 0.3.1 (the 0.3.1 tier gate is untouched).
1. /pickaxe /hatchet /hoe /sickle (GearLife.reclaimW, world thread) now bring back YOUR lifelong tool:
   a. still in your inventory (any section: hotbar, storage, backpack, tools ...) -> "you still have it" (as before);
   b. NO FREE SLOT -> refused before anything moves (never dropped);
   c. in your Requip -> fetched with wardrobe:fn:fetch (SkyyWardrobe 0.2+, stamp kept like the Smithing page's fetch);
   d. in a window you have open right now (a chest, your Vault, any container window) -> moved into a free slot;
   e. in the chest it was last put in (same world, chunk LOADED - ChunkStore.getChunkSectionReferenceAtBlock never loads a chunk, the
      GearChestOpen lookup pattern live since 0.1.3) -> moved into a free slot; anyone looking into that chest sees it go (the engine's
      own container change event re-sends every window on it);
   f. out of reach (unloaded chunk, another world, broken chest, dropped / despawned, with another player, in a closed Vault) -> an EXACT
      COPY from the snapshot: same item (tier), rarity, rolls / lines, reforge name, perks + Upgrade Points (those live in the registry per
      kind, so they simply carry over) and level (= the skill rule). DECISION: the copy gets a NEW uid (+ "lcu" = the uid it copies) -
      the uid is the guard's identity (GearLL.hit / stale: only the registry's uid works); a second stack with the SAME uid would be a
      second working tool. The copy is a replacement (lrp=1, lrpT = its tier, NEW lrpF = its reforge count), so the 0.3.0 guard applies
      unchanged: when the original turns up it is the tool again and the copy disappears; if the copy was tiered up / reforged AFTER the
      copy (GearLL.invested now compares rfN with lrpF) the original is retired instead. Never two working tools, never a lost one.
      No snapshot (a tool lost before 0.3.2 and never seen since) -> the 0.3.1 answer: a Common tool of the tier it had.
   The lifelong.reclaimSec wait (600 s) applies to COPIES only (a copy is the only new item); bringing your own tool back never waits.
2. WHERE IT WENT, event-driven (no world scan): GearLife.pass (the sweep) notes which kinds' CURRENT tool is in the inventory (GearLL.HERE,
   memory). GearInvSys (InventoryChangeEvent, world thread) asks GearLL.trackMaybe: only with such a tool AND an open item window it queues
   ONE GearTrackTask on the world (coalesced: GearLL.TRACKQ) - it runs after the move is complete, finds the tool in the open window and
   stores the place in the registry (chest: world key + x y z; other windows: their class name, e.g. the Vault) + a fresh snapshot.
   Seeing the tool back in the inventory clears the place. A snapshot (the document minus lvl / lrt, Base64 JSON) is refreshed by the
   sweep whenever the current tool's document changes (reforge, tier-up, swap) - one registry write per real change.
3. ROWS: lifelong.reclaimTier is LEGACY (CONFIG-CONTRACT: keys are never removed; label "Unused (old /pickaxe tier)", nothing reads it);
   lifelong.reclaimSec's label / help say it is the wait between exact copies. No default changes -> no one-time update.
4. TEXTS: the commands' descriptions, the messages, the Tools tab's "Not on you" line, statusText, the manifest sentence.
CRASH SAFETY (the harness crashes at every step): a summon takes the tool out of the source FIRST (verified), then puts it in the free
slot (read back), else back into its source slot; the registry is not changed by a summon (only the place is cleared afterwards), so a
crash that loses the tool from both leaves the registry naming it -> the next /pickaxe makes the exact copy; a crash that keeps it in
both = two stacks with ONE uid: the sweep removes a second one in the inventory and it does nothing for anyone else.
FIX ROUND (critics, 2026-10-14): the tracker survives a stamp task queued before it (pass keeps HERE bits while TRACKQ is set); a copy and
the tool it copies are one family (<kind>.nsw) - /lifelong never swaps between them (no free undo of a paid reforge); keep re-reads .inv
(rollback); snapSet's shortcut checks snapU; SNAPRAW bounded; the Tools tab line is shorter; the migration notice no longer names the Void.
ROLLBACK: 0.3.2 -> 0.3.1 is safe (the new registry keys .snap / .snapId / .snapU / .loc* and the document keys lcu / lrpF are ignored;
0.3.1 counts a reforged exact copy as invested - the original is retired instead of the copy removed: no item lost, no second tool).
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.1.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.2.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.1"' in s and "GENERATED by tools/gear_0_3_1_patch.py" in s and "0.3.2" not in s[:400], "not the generated 0.3.1 script"
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


def span(start, end, new):
    """replace the text from start (included) up to end (excluded); both unique"""
    global s
    assert s.count(start) == 1 and s.count(end) == 1, "span anchors: %d %d" % (s.count(start), s.count(end))
    a, b = s.index(start), s.index(end)
    assert a < b
    CHANGES.append((new, s[a:b]))
    s = s[:a] + new + s[b:]


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.1":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.1" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.1 - build script (javassist via jpype). GENERATED by tools/gear_0_3_1_patch.py from the LIVE 0.3.0 (itself GENERATED by
tools/gear_0_3_0_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.1.py -> SkyyGear/SkyyGear-0.3.1.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.1.py
''', '''"""SkyyGear 0.3.2 - build script (javassist via jpype). GENERATED by tools/gear_0_3_2_patch.py from the LIVE 0.3.1 (itself GENERATED by
tools/gear_0_3_1_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.2.py -> SkyyGear/SkyyGear-0.3.2.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.2.py

0.3.2 = THE EXACT LOST TOOL (Skyy 2026-10-13 "if you can, make it give their exact tool back. (or if its in a chest, summons it to your
inventory.)"; notes: tools/gear_0_3_2_patch.py): /pickaxe /hatchet /hoe /sickle fetch YOUR lifelong tool from Requip, an open window or
the loaded chest it was last put in (tracked when it leaves the inventory for an open window - no world scan); out of reach = an exact
copy (same tier, rarity, rolls, perks, points; a new uid so the 0.3.0 guard retires / removes whichever is not current); a full
inventory is refused; the wait (lifelong.reclaimSec) applies to copies only; lifelong.reclaimTier is a legacy row.

--- 0.3.1 notes ---
''')
rep('VERSION = "0.3.1"\n', 'VERSION = "0.3.2"\n')

# ================================================================================================================ rows
rep('''    ("lifelong.reclaimSec", "Wait between /pickaxe uses", "lifelong", "int", "600", "0", "86400", "", "s", "live",
     "Seconds before /pickaxe, /hatchet, /hoe or /sickle can give that kind of tool again.", "field:GearCfg.LL_RECLAIM"),''',
    '''    # 0.3.2: /pickaxe brings YOUR tool back (Requip, an open window, its loaded chest) without a wait; only an exact copy waits
    ("lifelong.reclaimSec", "Wait between exact copies", "lifelong", "int", "600", "0", "86400", "", "s", "live",
     "Seconds between two exact copies from /pickaxe (and co.). Fetching your own tool never waits.", "field:GearCfg.LL_RECLAIM"),''')
rep('''    ("lifelong.reclaimTier", "/pickaxe gives your skill's tier", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "On: a lost tool comes back at the tier your skill fits (free tier-ups!). Off: the tier it had.", "field:GearCfg.LL_RTIER"),''',
    '''    # 0.3.2: LEGACY - /pickaxe returns the exact tool (or an exact copy) now; nothing reads this row (kept: keys are never removed)
    ("lifelong.reclaimTier", "Unused (old /pickaxe tier)", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "No longer used: since 0.3.2 /pickaxe brings back your own tool or an exact copy of it.", "field:GearCfg.LL_RTIER"),''')

# ================================================================================================================ GearLL (read side)
before('''gll = mk("GearLL")
LIFE_CLASSES = [gll]
''', '''# 0.3.2 THE EXACT LOST TOOL: engine tokens (the open windows that hold items). Every viewer of a container is refreshed by the engine itself:
# WindowManager.setWindow0 registers ItemContainer.registerChangeEvent for each ItemContainerWindow (VERIFIED bytecode 2026-10-13)
LT32 = {"ICWN": "com.hypixel.hytale.server.core.entity.entities.player.windows.ItemContainerWindow"}
for _k in LT32:
    assert _k not in T, "0.3.2 token clashes: " + _k
T.update(LT32)
for _c, _m in ((LT32["ICWN"], "getItemContainer"), (PR, "getReference"), (PR, "getWorldUuid"), (PR, "isValid"),
               (CO["WMGR"], "getWindows"), (CO["BWIN"], "getX"), (CO["BWIN"], "getY"), (CO["BWIN"], "getZ"),
               (PB["CHS"], "getChunkSectionReferenceAtBlock"), (CO["BMOD"], "getBlockEntity"), (IC, "removeItemStackFromSlot"),
               ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson")):
    B.probe(pool, _c, _m)
assert pool.get(CO["CBW"]).subclassOf(pool.get(CO["BWIN"])) and pool.get(CO["CBW"]).subtypeOf(pool.get(LT32["ICWN"])), "ContainerBlockWindow changed"
assert pool.get(WLD).subtypeOf(pool.get("java.util.concurrent.Executor")), "World is no Executor any more"
''')
rep('''  return t > @PKG@.GearData.num(d, "lrpT", t) || @PKG@.GearData.num(d, "rfN", 0) > 0;''',
    '''  // 0.3.2: an exact copy carries the reforge count it was copied with (lrpF) - only a reforge AFTER the copy counts
  return t > @PKG@.GearData.num(d, "lrpT", t) || @PKG@.GearData.num(d, "rfN", 0) > @PKG@.GearData.num(d, "lrpF", 0);''')
before('''M(gll, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  SLOW.remove(u);''', r'''# 0.3.2 WHERE IT WENT (tools/gear_0_3_2_patch.py item 2): HERE = UUID -> "mask:profile key" (the kinds whose CURRENT tool the last look found
# in the inventory - GearLife.pass); TRACKQ = UUID -> Boolean (one track task queued at a time)
F(gll, "public static final java.util.concurrent.ConcurrentHashMap HERE = new java.util.concurrent.ConcurrentHashMap();")
F(gll, "public static final java.util.concurrent.ConcurrentHashMap TRACKQ = new java.util.concurrent.ConcurrentHashMap();")
M(gll, r"""
public static int hereMask(Object hv, String pk) {
  if (!(hv instanceof String) || pk == null) return 0;
  String v = (String) hv;
  int i = v.indexOf(':');
  if (i <= 0 || !pk.equals(v.substring(i + 1))) return 0;
  try { return Integer.parseInt(v.substring(0, i)); } catch (Throwable t) { return 0; }
}""")
# body set by GearLife below (compiled later): queue one GearTrackTask on the player's world
M(gll, "public static void trackHook(@PR@ pr, java.util.concurrent.Executor ex, @WLD@ w) { }")
# GearInvSys (an inventory change, world thread): only with a current lifelong tool in the inventory at the last look AND an open window
# that holds items (a chest, the Vault ...) - the only way a tool leaves for a container. Everything else returns at once.
M(gll, r"""
public static void trackMaybe(@PR@ pr, @ST@ st, @REF@ r, java.util.concurrent.Executor ex, @WLD@ w) {
  try {
    if (!@PKG@.GearCfg.LL_ON || pr == null || st == null || r == null || ex == null) return;
    if (HERE.get(pr.getUuid()) == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    java.util.List ws = p.getWindowManager().getWindows();
    if (ws == null || ws.isEmpty()) return;
    boolean any = false;
    for (int i = 0; i < ws.size() && !any; i++) if (ws.get(i) instanceof @ICWN@) any = true;
    if (any) trackHook(pr, ex, w);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("lltrackq", "the lifelong tool tracker could not look at the open windows: " + t); }
}""")
''')
rep('''  if (u == null) return;
  SLOW.remove(u);
  LAST.remove(u);
''', '''  if (u == null) return;
  SLOW.remove(u);
  LAST.remove(u);
  HERE.remove(u);          // 0.3.2
  TRACKQ.remove(u);
''')
rep('''", /pickaxe /hatchet /hoe /sickle every " + @PKG@.GearCfg.LL_RECLAIM + " s); tool tier gate "''',
    '''", /pickaxe /hatchet /hoe /sickle fetch yours from Requip / an open window / its loaded chest, else an exact copy every " + @PKG@.GearCfg.LL_RECLAIM + " s); tool tier gate "''')

# ================================================================================================================ GearInvSys: the track hook
rep('''    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
    @PKG@.GearStamp.dirty(pr, w);""")''', '''    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
    @PKG@.GearStamp.dirty(pr, w);
    if (w != null) @PKG@.GearLL.trackMaybe(pr, st, r, w, w);          // 0.3.2: a lifelong tool leaving for an open chest / Vault window""")''')

# ================================================================================================================ GearLife (write side)
rep('''gllfn = mk("GearLLFn")
LIFE_CLASSES += [glf, lpg] + llcmds + [tpc, llc, gdrop, gllfn]
''', '''gllfn = mk("GearLLFn")
gtrk = mk("GearTrackTask")          # 0.3.2: where a lifelong tool went (one world task after an inventory change in an open window)
LIFE_CLASSES += [glf, lpg] + llcmds + [tpc, llc, gdrop, gllfn, gtrk]
''')
rep('''F(glf, "public static final long[] N = new long[14];")''',
    '''# 0.3.2: 14 fetched from Requip, 15 fetched from an open window, 16 fetched from its chest, 17 exact copies
F(glf, "public static final long[] N = new long[18];")''')
after('''F(glf, "public static volatile int CRASH_AT = 0;")             # harness only: throw at that step (a crash)
''', '''# 0.3.2 harness only: "world key|x|y|z" -> ItemContainer (the chest lookup without a live World; a missing key = an unloaded chunk) and the
# world key of a null World. Never set by the game (null = the engine path).
F(glf, "public static volatile java.util.Map TEST_CHESTS = null;")
F(glf, "public static volatile String TEST_WKEY = null;")
F(glf, "public static final java.util.concurrent.ConcurrentHashMap SNAPRAW = new java.util.concurrent.ConcurrentHashMap();")   # "pk|kind" -> doc json + id last seen
''')
# ---- the place + the snapshot helpers (before commit / keep, which use them)
before('''M(glf, r"""
public static void clearPend(java.util.Properties P, String K) {''', r'''# ---- 0.3.2 the last place a lifelong tool was put (registry keys <kind>.locK = "chest" / "window:<class>", .locW world key, .locX/Y/Z, .locAt)
M(glf, r"""
public static void setLoc(java.util.Properties P, String K, String kind, String wk, int x, int y, int z) {
  P.setProperty(K + ".locK", kind);
  if (wk != null) P.setProperty(K + ".locW", wk); else P.remove(K + ".locW");
  P.setProperty(K + ".locX", String.valueOf(x));
  P.setProperty(K + ".locY", String.valueOf(y));
  P.setProperty(K + ".locZ", String.valueOf(z));
  P.setProperty(K + ".locAt", String.valueOf(System.currentTimeMillis()));
}""")
M(glf, r"""
public static boolean clearLoc(java.util.Properties P, String K) {
  boolean had = P.getProperty(K + ".locK") != null;
  P.remove(K + ".locK");
  P.remove(K + ".locW");
  P.remove(K + ".locX");
  P.remove(K + ".locY");
  P.remove(K + ".locZ");
  P.remove(K + ".locAt");
  return had;
}""")
M(glf, r"""
public static String locText(java.util.Properties P, String K) {
  String k = P.getProperty(K + ".locK");
  if (k == null) return "unknown";
  if ("chest".equals(k)) return "chest " + @PKG@.GearChestOpen.wname(P.getProperty(K + ".locW")) + " " + P.getProperty(K + ".locX") + " " + P.getProperty(K + ".locY") + " " + P.getProperty(K + ".locZ");
  return k;
}""")
# ---- 0.3.2 THE SNAPSHOT: the current tool's document (minus lvl / lrt / lvU - the level follows the skill) as Base64 JSON (+ its item id and
# uid) - what an exact copy is made from. Refreshed only when the document really changed (SNAPRAW = the json last looked at, memory)
M(glf, r"""
public static String snapText(@BD@ d) {
  @BD@ c = d.clone();
  c.remove("lvl");
  c.remove("lrt");
  c.remove("lvU");
  try { return java.util.Base64.getEncoder().encodeToString(c.toJson().getBytes("UTF-8")); } catch (Throwable t) { return null; }
}""")
M(glf, r"""
public static boolean snapSet(String pk, java.util.Properties P, String K, @BD@ d, String id) {
  if (d == null || id == null) return false;
  try {
    String raw = id + "|" + d.toJson();
    String key = pk + "|" + K;
    String lu = @PKG@.GearLL.uid(d);
    // fix round (safety critic 3): the shortcut only while the snapshot still names THIS uid (a copy's commit may have pointed snapU elsewhere)
    if (raw.equals(SNAPRAW.get(key)) && P.getProperty(K + ".snap") != null && lu.equals(P.getProperty(K + ".snapU"))) return false;
    String t = snapText(d);
    if (t == null) return false;
    if (SNAPRAW.size() > 4096) SNAPRAW.clear();          // fix round (engine critic 2): memory only - bounded (a clear costs one compare each)
    SNAPRAW.put(key, raw);
    if (t.equals(P.getProperty(K + ".snap")) && id.equals(P.getProperty(K + ".snapId")) && lu.equals(P.getProperty(K + ".snapU"))) return false;
    P.setProperty(K + ".snap", t);
    P.setProperty(K + ".snapId", id);
    P.setProperty(K + ".snapU", lu);
    return true;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("llsnap", "lifelong: a tool snapshot could not be made: " + t); return false; }
}""")
# fix round (safety critic 1): <kind>.nsw = the uids an exact copy was made of (newest 16). A copy and the tool it copies are ONE family: once
# one of them is retired it stays retired - /lifelong never swaps between them (else a paid reforge of the copy could be undone for free by
# swapping the original back, and the reforge price would fall back with it)
M(glf, r"""
public static boolean nswHas(java.util.Properties P, String K, String lu) {
  if (lu == null || lu.length() == 0) return false;
  String v = P.getProperty(K + ".nsw");
  return v != null && ("," + v + ",").indexOf("," + lu + ",") >= 0;
}""")
M(glf, r"""
public static void nswAdd(java.util.Properties P, String K, String lu) {
  if (lu == null || lu.length() == 0 || nswHas(P, K, lu)) return;
  String v = P.getProperty(K + ".nsw");
  String nv = v == null || v.length() == 0 ? lu : v + "," + lu;
  if (nv.split(",").length > 16) nv = nv.substring(nv.indexOf(',') + 1);
  P.setProperty(K + ".nsw", nv);
}""")
M(glf, r"""
public static String lcuOf(@BD@ d) {
  if (d == null) return null;
  Object o = d.get("lcu");
  return o instanceof org.bson.BsonString ? ((org.bson.BsonString) o).getValue() : null;
}""")
M(glf, r"""
public static boolean family(java.util.Properties P, String K, @BD@ d) {
  return d != null && (nswHas(P, K, @PKG@.GearLL.uid(d)) || nswHas(P, K, lcuOf(d)));
}""")
# the snapshot of the CURRENT tool (snapU = cur), else null (none yet: a tool lost before 0.3.2 and never seen since)
M(glf, r"""
public static @BD@ snapDoc(java.util.Properties P, String K, String cur) {
  String t = P.getProperty(K + ".snap");
  if (t == null || cur == null || !cur.equals(P.getProperty(K + ".snapU"))) return null;
  try { return @BD@.parse(new String(java.util.Base64.getDecoder().decode(t), "UTF-8")); } catch (Throwable x) { return null; }
}""")
''')
rep('''  P.remove(K + ".seen");
  P.remove(K + ".inv");
  if (xk != null) P.setProperty(xk, xv);''', '''  P.remove(K + ".seen");
  P.remove(K + ".inv");
  clearLoc(P, K);          // 0.3.2: a new uid - the old place is history
  if (xk != null) P.setProperty(xk, xv);''')
rep('''      boolean rc = "reclaim".equals(mode);''', '''      boolean rc = "reclaim".equals(mode) || "copy".equals(mode);          // 0.3.2: an exact copy starts the wait too''')
# ---- give -> give2 (+ the exact copy's source document)
rep('''# give a NEW lifelong tool (mode "give" = the migration's Crude Common one, "reclaim" = /pickaxe ...): 1 given, 0 no free slot, -1 failed
M(glf, r"""
public static int give(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String id, String mode) {''',
    '''# give a NEW lifelong tool (mode "give" = the migration's Crude Common one, "reclaim" = /pickaxe ... (0.3.2: only without a snapshot),
# "copy" = 0.3.2 the EXACT copy of src (the snapshot; cu = the uid it copies)): 1 given, 0 no free slot, -1 failed
M(glf, r"""
public static int give2(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String id, String mode, @BD@ src, String cu) {''')
rep('''  boolean rp = "reclaim".equals(mode);
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int before = @PKG@.GearStamp.countId(all, id);
  if (!journal(pk, P, k, lu, mode, id)) return -1;
  crash(4);
  @BD@ nd = llDoc(null, id, u, pk, lu, rp);''', '''  boolean rp = "reclaim".equals(mode) || "copy".equals(mode);          // 0.3.2: an exact copy is a replacement too (the guard)
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int before = @PKG@.GearStamp.countId(all, id);
  if (src != null && cu != null) nswAdd(P, K, cu);          // fix round (safety critic 1): saved with the journal, before any item exists
  if (!journal(pk, P, k, lu, mode, id)) return -1;
  crash(4);
  @BD@ nd = llDoc(src, id, u, pk, lu, rp);
  if (src != null) {          // 0.3.2: the copy keeps rarity, lines, reforge name; it is never born retired, and only a LATER reforge invests it
    nd.remove("lrt");
    nd.put("lrpF", new org.bson.BsonInt32(@PKG@.GearData.num(src, "rfN", 0)));
    if (cu != null) nd.put("lcu", new org.bson.BsonString(cu));
  }''')
rep('''  @PKG@.GearStamp.selfNote(u, tx);
  crash(5);
  if (!commit(pk, P, k, lu, id, rp, rp ? K + ".reclaimAt" : null, String.valueOf(System.currentTimeMillis()), !"give".equals(mode))) @PKG@.Gear.warn("lifelong: the commit of " + K + " " + lu + " could not be written - the next sweep finishes it");''',
    '''  @PKG@.GearStamp.selfNote(u, tx);
  crash(5);
  if (src != null) P.setProperty(K + ".snapU", lu);          // 0.3.2: the snapshot now describes the copy (same document, its uid)
  if (!commit(pk, P, k, lu, id, rp, rp ? K + ".reclaimAt" : null, String.valueOf(System.currentTimeMillis()), !"give".equals(mode))) @PKG@.Gear.warn("lifelong: the commit of " + K + " " + lu + " could not be written - the next sweep finishes it");''')
rep('''  if (rp) N[7] = N[7] + 1L;
  else N[3] = N[3] + 1L;
  @PKG@.GearLog.line("LL-" + (rp ? "RECLAIM " : "GIVE ") + u + " " + pk + " " + K + " " + lu + " " + id + " lv" + @PKG@.GearLevel.level(id, nd));
  return 1;
}""")''', '''  if (rp) N[7] = N[7] + 1L;
  else N[3] = N[3] + 1L;
  if (src != null) N[17] = N[17] + 1L;
  @PKG@.GearLog.line("LL-" + (src != null ? "COPY " : (rp ? "RECLAIM " : "GIVE ")) + u + " " + pk + " " + K + " " + lu + " " + id + " lv" + @PKG@.GearLevel.level(id, nd) + (cu != null ? " exact copy of " + cu + " [" + @PKG@.GearView.modSummary(nd) + "]" : ""));
  return 1;
}""")
M(glf, r"""
public static int give(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String id, String mode) {
  return give2(pr, inv, pk, P, k, id, mode, null, null);
}""")''')
# ---- keep: the place is cleared + the snapshot refreshed
rep('''  if (!"1".equals(P.getProperty(K + ".seen"))) { P.setProperty(K + ".seen", "1"); ch = true; }
  return ch;
}""")''', '''  if (!"1".equals(P.getProperty(K + ".seen"))) { P.setProperty(K + ".seen", "1"); ch = true; }
  if (clearLoc(P, K)) ch = true;          // 0.3.2: it is here - the last place it was put is history
  if (snapSet(pk, P, K, d, id)) ch = true;          // 0.3.2: what an exact copy is made from if it is ever lost
  return ch;
}""")''')
# ---- pass: which kinds' current tool is here (GearLL.HERE)
rep('''  int rounds = 0;
  while (again && rounds < 2) {
    again = false;
    rounds++;
    java.util.HashSet one = new java.util.HashSet();          // the current uids met in this round (a 2nd stack with one = a copy)''',
    '''  int rounds = 0;
  int here = 0;          // 0.3.2: the kinds whose current tool is in the inventory (GearLL.HERE - the tracker's cheap gate)
  while (again && rounds < 2) {
    again = false;
    rounds++;
    here = 0;
    java.util.HashSet one = new java.util.HashSet();          // the current uids met in this round (a 2nd stack with one = a copy)''')
rep('''          if (!one.add(lu)) { remove(c, i, x, u, "a second stack of your lifelong " + K + " (" + lu + ") - only one exists"); continue; }
          if (keep(c, i, x, d, k, u, pk, P)) dirty = true;''', '''          if (!one.add(lu)) { remove(c, i, x, u, "a second stack of your lifelong " + K + " (" + lu + ") - only one exists"); continue; }
          here = here | (1 << k);
          if (keep(c, i, x, d, k, u, pk, P)) dirty = true;''')
rep('''  if (dirty) @PKG@.GearLL.save(pk, P);
}""")''', '''  // fix round (engine critic 1): a stamp task queued by the same inventory change runs BEFORE the tracker task (FIFO world queue) - while a
  // tracker task is queued (TRACKQ) the kinds that just left stay in HERE, so track still finds them in the open window
  int hm = here;
  if (@PKG@.GearLL.TRACKQ.containsKey(u)) hm = hm | @PKG@.GearLL.hereMask(@PKG@.GearLL.HERE.get(u), pk);
  if (hm != 0) @PKG@.GearLL.HERE.put(u, hm + ":" + pk); else @PKG@.GearLL.HERE.remove(u);
  if (dirty) @PKG@.GearLL.save(pk, P);
}""")''')

# ---- the tracker + the fetch paths + reclaimW (replaces the 0.3.0 reclaim body; reclaim(pr, p, k) stays as the no-world entry)
span('''# /pickaxe /hatchet /hoe /sickle (world thread): "+" given, "-" refused (why). The tier: lifelong.reclaimTier off (the default since fix round
# 2) = the tier you had; on (Skyy G2's literal reading) = the first tier whose band holds your skill level, never below the one you had
M(glf, r"""
public static String reclaim(@PR@ pr, @PLA@ p, int k) {''',
     '''# fix round 2 (safety critic 2): /lifelong on your own RETIRED tool swaps it back (any time): ONE registry write names it; the sweep then''',
     r'''# ---- 0.3.2 THE EXACT LOST TOOL (tools/gear_0_3_2_patch.py)
# the Requip entry id of the lifelong uid lu (wardrobe:fn:list, both spaces; none / no SkyyWardrobe = null)
M(glf, r"""
public static String rqFind(java.util.UUID u, String lu) {
  String[] sp = new String[] { "armor", "items" };
  for (int k = 0; k < sp.length; k++) {
    java.util.ArrayList l = @PKG@.GearSmith.rqList(u, sp[k]);
    for (int i = 0; i < l.size(); i++) {
      Object[] e = (Object[]) l.get(i);
      if (!(e[2] instanceof @BD@)) continue;
      @BD@ d = null;
      try { d = @PKG@.GearData.gearDoc((@BD@) e[2]); } catch (Throwable t) { d = null; }
      if (@PKG@.GearLL.isLL(d) && lu.equals(@PKG@.GearLL.uid(d))) return (String) e[0];
    }
  }
  return null;
}""")
# the lifelong uids of profile pk in this inventory (one scan)
M(glf, r"""
public static java.util.HashSet present(@INV@ inv, String pk) {
  java.util.HashSet out = new java.util.HashSet();
  if (inv == null) return out;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || @PKG@.GearLL.kOf(x.getItemId()) < 0) continue;
      @BD@ d = docOf(x);
      if (@PKG@.GearLL.isLL(d) && pk.equals(@PKG@.GearLL.owner(d))) out.add(@PKG@.GearLL.uid(d));
    }
  }
  return out;
}""")
# the slot of the lifelong stack lu of profile pk in one container (-1 = not there)
M(glf, r"""
public static int slotIn(@IC@ c, String pk, String lu) {
  if (c == null || lu == null) return -1;
  for (int i = 0; i < c.getCapacity(); i++) {
    @IS@ x = c.getItemStack((short) i);
    if (x == null || x.isEmpty() || @PKG@.GearLL.kOf(x.getItemId()) < 0) continue;
    @BD@ d = docOf(x);
    if (@PKG@.GearLL.isLL(d) && lu.equals(@PKG@.GearLL.uid(d)) && pk.equals(@PKG@.GearLL.owner(d))) return i;
  }
  return -1;
}""")
M(glf, "public static String wkOf(@WLD@ w) { return w != null ? @PKG@.GearChestOpen.wkey(w) : TEST_WKEY; }")
# a tool that just arrived (fetched / copied) is "here" at once - the next sweep may be throttled, the tracker must see it leave again
M(glf, r"""
public static void hereAdd(java.util.UUID u, String pk, int k) {
  int m = @PKG@.GearLL.hereMask(@PKG@.GearLL.HERE.get(u), pk) | (1 << k);
  @PKG@.GearLL.HERE.put(u, m + ":" + pk);
}""")
# THE TRACKER (world thread, GearTrackTask): a kind whose current tool was here at the last look but is gone from the inventory while a window
# that holds items is open -> the window holding it is the place (chest: world key + x y z; other windows: their class, e.g. the Vault);
# a fresh snapshot is taken from the stack there. One registry write per departure; the next look that sees the tool clears the place
M(glf, r"""
public static void track(@PR@ pr, @PLA@ p, @WLD@ w) {
  if (!@PKG@.GearCfg.LL_ON || pr == null || p == null) return;
  java.util.UUID u = pr.getUuid();
  Object hv = @PKG@.GearLL.HERE.get(u);
  if (hv == null || @PKG@.Gear.busy(u)) return;
  String pk = @PKG@.Gear.pkey(u);
  int mask = @PKG@.GearLL.hereMask(hv, pk);
  if (mask == 0) { @PKG@.GearLL.HERE.remove(u); return; }
  java.util.List ws = null;
  try { ws = p.getWindowManager().getWindows(); } catch (Throwable t0) { ws = null; }
  if (ws == null || ws.isEmpty()) return;
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return;
  java.util.HashSet have = present(p.getInventory(), pk);
  String wk = null;
  boolean wkDone = false;
  boolean ch = false;
  for (int k = 0; k < 4; k++) {
    if ((mask & (1 << k)) == 0) continue;
    String K = @PKG@.GearLL.KIND[k];
    String cur = P.getProperty(K + ".uid");
    if (cur == null || have.contains(cur)) continue;
    for (int i = 0; i < ws.size(); i++) {
      Object o = ws.get(i);
      if (!(o instanceof @ICWN@)) continue;
      @IC@ c = null;
      try { c = ((@ICWN@) o).getItemContainer(); } catch (Throwable t1) { c = null; }
      int s = slotIn(c, pk, cur);
      if (s < 0) continue;
      @IS@ x = c.getItemStack((short) s);
      if (o instanceof @CBW@) {
        if (!wkDone) { wk = wkOf(w); wkDone = true; }
        @BWIN@ bw = (@BWIN@) o;
        setLoc(P, K, "chest", wk, bw.getX(), bw.getY(), bw.getZ());
      } else setLoc(P, K, "window:" + o.getClass().getSimpleName(), null, 0, 0, 0);
      snapSet(pk, P, K, docOf(x), x.getItemId());
      mask = mask & ~(1 << k);
      ch = true;
      @PKG@.GearLog.line("LL-WHERE " + u + " " + pk + " " + K + " " + cur + " -> " + locText(P, K));
      break;
    }
  }
  if (mask == 0) @PKG@.GearLL.HERE.remove(u); else @PKG@.GearLL.HERE.put(u, mask + ":" + pk);
  if (ch) @PKG@.GearLL.save(pk, P);
}""")
''' + '''# GearTrackTask (world task, queued by GearLL.trackHook): the player of pr on this world -> GearLife.track. w null = harness only (no world check)
gtrk.addInterface(pool.get("java.lang.Runnable"))
F(gtrk, "public @PR@ pr;")
F(gtrk, "public @WLD@ w;")
C(gtrk, r"""
public GearTrackTask(@PR@ pr, @WLD@ w) {
  this.pr = pr;
  this.w = w;
}""")
M(gtrk, r"""
public void run() {
  java.util.UUID u = null;
  try {
    if (this.pr == null) return;
    u = this.pr.getUuid();
    @PKG@.GearLL.TRACKQ.remove(u);
    if (this.w != null) {
      if (!this.pr.isValid()) return;
      java.util.UUID wu = this.pr.getWorldUuid();
      java.util.UUID mine = this.w.getWorldConfig() == null ? null : this.w.getWorldConfig().getUuid();
      if (wu == null || mine == null || !wu.equals(mine)) return;          // changed worlds meanwhile: the next change asks again
    }
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    @PKG@.GearLife.track(this.pr, p, this.w);
  } catch (Throwable t) {
    if (u != null) @PKG@.GearLL.TRACKQ.remove(u);
    @PKG@.Gear.warnOnce("lltrack", "the lifelong tool tracker failed: " + t);
  }
}""")
M(glf, r"""
public static void trackLater(@PR@ pr, java.util.concurrent.Executor ex, @WLD@ w) {
  if (pr == null || ex == null) return;
  java.util.UUID u = pr.getUuid();
  if (@PKG@.GearLL.TRACKQ.putIfAbsent(u, Boolean.TRUE) != null) return;
  try { ex.execute(new @PKG@.GearTrackTask(pr, w)); } catch (Throwable t) { @PKG@.GearLL.TRACKQ.remove(u); }
}""")
# THE MOVE (world thread): the lifelong stack cur at src slot s -> a free inventory slot. Taken out FIRST (checked), then put in (read back),
# else put back where it was. ci = the counter (15 window, 16 chest). Anyone looking into that container sees it go (the engine's own
# container change event re-sends every window on it)
M(glf, r"""
public static String move(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String cur, @IC@ src, int s, String from, int ci) {
  java.util.UUID u = pr.getUuid();
  String K = @PKG@.GearLL.KIND[k];
  @IS@ x = src.getItemStack((short) s);
  @BD@ d = docOf(x);
  if (x == null || x.isEmpty() || x.getQuantity() != 1 || !@PKG@.GearLL.isLL(d) || !cur.equals(@PKG@.GearLL.uid(d)) || !pk.equals(@PKG@.GearLL.owner(d))) return "-Your " + K + " moved before it could be fetched - try again.";
  // the same world thread runs a profile switch, so it cannot happen inside this call - checked anyway
  if (@PKG@.Gear.busy(u) || !pk.equals(@PKG@.Gear.pkey(u))) return "-Your profile is changing - try again in a moment.";
  Object[] fe = @PKG@.GearStamp.firstEmpty(new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() }, null, -1);
  if (fe == null) return "-No room - free one inventory slot and try again.";
  @IC@ dc = (@IC@) fe[0];
  int ds = ((Integer) fe[1]).intValue();
  String undo = @PKG@.GearMerge.json(x);
  @PKG@.GearLog.line("LL-SUMMON-BEGIN " + u + " " + pk + " " + K + " " + cur + " from " + from + " slot " + (s + 1) + " undo: " + undo);
  Object t1 = null;
  Throwable e1 = null;
  try { t1 = src.removeItemStackFromSlot((short) s); } catch (Throwable t) { e1 = t; }
  @IS@ left = src.getItemStack((short) s);
  boolean out = left == null || left.isEmpty();
  if (!out || (e1 == null && t1 instanceof @TXN@ && !((@TXN@) t1).succeeded())) {
    @PKG@.GearLog.line("LL-SUMMON-REFUSED " + u + " " + K + " " + cur + " (" + from + " kept it" + (e1 != null ? ": " + e1 : "") + ")");
    return "-Your " + K + " could not be taken out of " + from + " - nothing moved.";
  }
  crash(7);
  boolean ok = false;
  try {
    Object t2 = dc.setItemStackForSlot((short) ds, x);
    ok = !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded());
    if (ok) @PKG@.GearStamp.selfNote(u, t2);
  } catch (Throwable t) { ok = false; @PKG@.Gear.warn("lifelong: a fetched tool could not be put into the inventory: " + t); }
  if (ok) {
    @BD@ nd = docOf(dc.getItemStack((short) ds));
    ok = nd != null && cur.equals(@PKG@.GearLL.uid(nd));
  }
  if (!ok) {
    boolean back = false;
    try {
      Object t3 = src.setItemStackForSlot((short) s, x);
      back = !(t3 instanceof @TXN@ && !((@TXN@) t3).succeeded()) && slotIn(src, pk, cur) == s;
    } catch (Throwable t) { back = false; }
    if (back) {
      @PKG@.GearLog.line("LL-SUMMON-UNDO " + u + " " + K + " " + cur + " (back in " + from + ")");
      return "-Your " + K + " could not be put into your inventory - it stayed in " + from + ".";
    }
    @PKG@.Gear.warn("LIFELONG TOOL OUT OF PLACE: " + K + " " + cur + " of profile " + pk + " left " + from + " but reached no slot - gear.log has it (LL-SUMMON-LOST)");
    @PKG@.GearLog.line("LL-SUMMON-LOST " + u + " " + pk + " " + K + " " + cur + " from " + from + " undo: " + undo);
    return "-Moving your " + K + " went wrong - an admin has the record (gear.log). /" + K + " makes an exact copy.";
  }
  crash(8);
  if (clearLoc(P, K)) @PKG@.GearLL.save(pk, P);
  hereAdd(u, pk, k);
  if (ci >= 0 && ci < N.length) N[ci] = N[ci] + 1L;
  int[] at = find(inv, pk, cur);
  String wh = at == null ? "inventory" : @PKG@.GearForge.where(at[0], at[1]);
  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from " + from + " -> " + wh);
  return "+Your " + @PKG@.Gear.itemName(x.getItemId()) + " came back from " + from + " into your " + wh + ".";
}""")
# c: Requip (SkyyWardrobe 0.2 wardrobe:fn:fetch: IN -> the first empty storage / hotbar / backpack slot, stamp kept, entry OUT)
M(glf, r"""
public static String fromRequip(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String cur, String eid) {
  java.util.UUID u = pr.getUuid();
  String K = @PKG@.GearLL.KIND[k];
  if (@PKG@.Gear.busy(u) || !pk.equals(@PKG@.Gear.pkey(u))) return "-Your profile is changing - try again in a moment.";
  java.util.function.Function f = @PKG@.Gear.fn("wardrobe:fn:fetch");
  if (f == null) return "-Your lifelong " + K + " is in your Requip, but Requip is not loaded right now - try again later.";
  @PKG@.GearLog.line("LL-SUMMON-BEGIN " + u + " " + pk + " " + K + " " + cur + " from Requip " + eid);
  Object r = null;
  try { r = f.apply(new Object[] { u, eid }); } catch (Throwable t) { r = "Requip did not answer (" + t + ")"; }
  if (!"ok".equals(r)) {
    String rr = r == null ? "Requip did not answer" : String.valueOf(r);
    if (rr.endsWith(".")) rr = rr.substring(0, rr.length() - 1);
    return "-Your lifelong " + K + " is in your Requip, but it could not come out: " + rr + ".";
  }
  crash(9);
  int[] at = find(inv, pk, cur);
  if (at == null) {
    @PKG@.Gear.warn("lifelong: Requip let " + K + " " + cur + " of profile " + pk + " out, but it is not in the inventory");
    return "-Requip let your " + K + " out, but it is not in your inventory - an admin can check requip.log.";
  }
  if (clearLoc(P, K)) @PKG@.GearLL.save(pk, P);
  hereAdd(u, pk, k);
  N[14] = N[14] + 1L;
  String wh = @PKG@.GearForge.where(at[0], at[1]);
  @PKG@.GearLog.line("LL-SUMMON " + u + " " + pk + " " + K + " " + cur + " from Requip " + eid + " -> " + wh);
  return "+Your " + @PKG@.Gear.itemName(@PKG@.GearStamp.at(inv, at[0], at[1]).getItemId()) + " came out of your Requip into your " + wh + ".";
}""")
M(glf, r"""
public static String winName(Object o) {
  if (o instanceof @CBW@) return "the open chest";
  String n = o == null ? "" : o.getClass().getName();
  if (n.indexOf("Vault") >= 0 || n.indexOf("vault") >= 0) return "your open Vault";
  return "the open storage window";
}""")
# d: a window open right now that holds it (a chest, the Vault - any ItemContainerWindow); null = none
M(glf, r"""
public static String fromWindows(@PR@ pr, @PLA@ p, @INV@ inv, String pk, java.util.Properties P, int k, String cur) {
  java.util.List ws = null;
  try { ws = p.getWindowManager().getWindows(); } catch (Throwable t) { ws = null; }
  if (ws == null) return null;
  for (int i = 0; i < ws.size(); i++) {
    Object o = ws.get(i);
    if (!(o instanceof @ICWN@)) continue;
    @IC@ c = null;
    try { c = ((@ICWN@) o).getItemContainer(); } catch (Throwable t) { c = null; }
    int s = slotIn(c, pk, cur);
    if (s < 0) continue;
    return move(pr, inv, pk, P, k, cur, c, s, winName(o), 15);
  }
  return null;
}""")
# the items of the chest at x y z of world w, or null + why[0]. A LOADED chunk only:
# ChunkStore.getChunkSectionReferenceAtBlock is a map lookup (no load); BlockModule.getBlockEntity + ItemContainerBlock = GearChestOpen.process
M(glf, r"""
public static @IC@ chestAt(@WLD@ w, String wk, int x, int y, int z, String[] why) {
  String at = x + " " + y + " " + z;
  java.util.Map tc = TEST_CHESTS;
  if (tc != null) {
    Object o = tc.get(wk + "|" + x + "|" + y + "|" + z);
    if (o instanceof @IC@) return (@IC@) o;
    why[0] = "it is in a chest at " + at + " that is not loaded right now";
    return null;
  }
  if (w == null) return null;
  @CHS@ cs = w.getChunkStore();
  if (cs == null) return null;
  @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (sr == null || !sr.isValid()) { why[0] = "it is in a chest at " + at + " that is not loaded right now"; return null; }
  @ICB@ icb = @PKG@.GearChestOpen.icbOf(@BMOD@.getBlockEntity(w, x, y, z));
  if (icb == null) { why[0] = "the chest at " + at + " it was put in is gone"; return null; }
  return icb.getItemContainer();
}""")
# e: the chest it was last put in (the tracker's place) - this world only; null + why[0] = out of reach
M(glf, r"""
public static String fromChest(@PR@ pr, @INV@ inv, String pk, java.util.Properties P, int k, String cur, @WLD@ w, String[] why) {
  String K = @PKG@.GearLL.KIND[k];
  if (!"chest".equals(P.getProperty(K + ".locK"))) return null;
  String lw = P.getProperty(K + ".locW");
  int x = (int) @PKG@.GearLL.getl(P, K + ".locX", 0L);
  int y = (int) @PKG@.GearLL.getl(P, K + ".locY", 0L);
  int z = (int) @PKG@.GearLL.getl(P, K + ".locZ", 0L);
  String wk = wkOf(w);
  if (lw == null || wk == null || !lw.equals(wk)) {
    why[0] = "it is in a chest at " + x + " " + y + " " + z + (lw == null ? "" : " in " + @PKG@.GearChestOpen.wname(lw)) + " - only a chest in the world you are in can send it";
    return null;
  }
  @IC@ c = chestAt(w, wk, x, y, z, why);
  if (c == null) return null;
  int s = slotIn(c, pk, cur);
  if (s < 0) { why[0] = "it is no longer in the chest at " + x + " " + y + " " + z; return null; }
  return move(pr, inv, pk, P, k, cur, c, s, "the chest at " + x + " " + y + " " + z, 16);
}""")
M(glf, r"""
public static String locWhy(java.util.Properties P, String K) {
  String k = P.getProperty(K + ".locK");
  if (k != null && k.startsWith("window:")) return k.indexOf("Vault") >= 0 || k.indexOf("vault") >= 0 ? "it is in your Vault, which cannot be opened from here" : "it is in a storage that cannot be opened from here";
  return "it is not in your inventory, your Requip or a loaded chest you put it in";
}""")
# /pickaxe /hatchet /hoe /sickle (world thread; w = the command's world, null = no chest lookup): "+" done, "-" refused (why).
# 0.3.2 (Skyy 2026-10-13 "make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"): your own tool comes
# back (Requip, an open window, the loaded chest it was put in); out of reach = an EXACT copy (the lifelong.reclaimSec wait); no free slot
# = refused first. lifelong.reclaimTier is no longer read.
M(glf, r"""
public static String reclaimW(@PR@ pr, @PLA@ p, int k, @WLD@ w) {
  if (!@PKG@.GearCfg.LL_ON) return "-Lifelong tools are switched off on this server.";
  if (pr == null || p == null || k < 0 || k > 3) return "-No player.";
  java.util.UUID u = pr.getUuid();
  if (@PKG@.Gear.busy(u)) return "-Your profile is still loading - try again in a moment.";
  @INV@ inv = p.getInventory();
  String pk = @PKG@.Gear.pkey(u);
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return "-Your lifelong tool list cannot be read right now - an admin can check the server log.";
  sweep0(pr, inv, true);
  String K = @PKG@.GearLL.KIND[k];
  String cur = P.getProperty(K + ".uid");
  if (cur == null) return "-Your lifelong " + K + " is still waiting for a free inventory slot - make room and it arrives.";
  int[] at = find(inv, pk, cur);
  if (at != null) return "-You still have your lifelong " + K + " (" + @PKG@.GearForge.where(at[0], at[1]) + ").";
  if (@PKG@.GearStamp.firstEmpty(new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() }, null, -1) == null) return "-No room - free one inventory slot and try again (nothing is ever dropped).";
  String eid = rqFind(u, cur);
  if (eid != null) return fromRequip(pr, inv, pk, P, k, cur, eid);
  String r = fromWindows(pr, p, inv, pk, P, k, cur);
  if (r != null) return r;
  String[] why = new String[] { null };
  r = fromChest(pr, inv, pk, P, k, cur, w, why);
  if (r != null) return r;
  String where = why[0] != null ? why[0] : locWhy(P, K);
  long now = System.currentTimeMillis();
  long last = @PKG@.GearLL.getl(P, K + ".reclaimAt", 0L);
  long wait = (long) @PKG@.GearCfg.LL_RECLAIM * 1000L - (now - last);
  if (last > 0L && now >= last && wait > 0L) return "-Your " + K + " cannot be reached (" + where + "). You can get an exact copy in " + ((wait + 999L) / 1000L) + " s.";
  @BD@ src = snapDoc(P, K, cur);
  String id = src == null ? null : P.getProperty(K + ".snapId");
  if (src != null && (id == null || @PKG@.Gear.item(id) == null || @PKG@.GearLL.kOf(id) != k)) { src = null; id = null; }
  if (id == null) id = P.getProperty(K + ".id");
  if (id == null || @PKG@.Gear.item(id) == null || @PKG@.GearLL.kOf(id) != k) id = @PKG@.GearLL.KCRUDE[k];
  int g = give2(pr, inv, pk, P, k, id, src != null ? "copy" : "reclaim", src, src != null ? cur : null);
  if (g == 0) return "-No room - free one inventory slot and try again (nothing is ever dropped).";
  if (g < 0) return "-That did not work - nothing was given. Try again in a moment.";
  hereAdd(u, pk, k);
  int lv = @PKG@.GearLL.levelFor(u, id);
  String nm = @PKG@.Gear.itemName(id) + (lv >= 1 ? " [Lv " + lv + "]" : "");
  if (src == null) return "+Here is a new Common " + nm + " (your old one was lost before exact copies existed). If your old one turns up again, it becomes your lifelong " + K + " again and this one disappears.";
  return "+Your " + K + " cannot be reached (" + where + "), so here is an exact copy: " + nm + " - same tier, rarity, rolls, perks and points. If the old one turns up, it is your " + K + " again and this copy disappears.";
}""")
M(glf, "public static String reclaim(@PR@ pr, @PLA@ p, int k) { return reclaimW(pr, p, k, null); }")
''')
rep('''  return "sweeps " + N[0] + ", levels written " + N[1] + ", marked " + N[2] + ", given " + N[3] + ", restored " + N[4] + ", demoted " + N[5] + ", copies removed " + N[6] + ", /pickaxe " + N[7] + ", perks " + N[8] + ", resets " + N[9] + ", adopted " + N[10] + ", journals finished " + N[11] + ", retired " + N[12] + ", swapped back " + N[13];''',
    '''  return "sweeps " + N[0] + ", levels written " + N[1] + ", marked " + N[2] + ", given " + N[3] + ", restored " + N[4] + ", demoted " + N[5] + ", copies removed " + N[6] + ", /pickaxe " + N[7] + ", perks " + N[8] + ", resets " + N[9] + ", adopted " + N[10] + ", journals finished " + N[11] + ", retired " + N[12] + ", swapped back " + N[13] + ", fetched from Requip " + N[14] + " / a window " + N[15] + " / a chest " + N[16] + ", exact copies " + N[17];''')
rep('''  else if (x == null) w = "Not on you - in a chest or Requip? Lost: /" + K;''',
    '''  else if (x == null) w = "Not on you - /" + K + " brings it back";''')          # fix round (fidelity critic 2): fits the 340 px column
# ---- fix round (safety critic 2): a 0.3.1 rollback marks an unchanged exact copy invested (0.3.1 counts the copied reforges) - keep re-reads it
rep('''  if ("1".equals(P.getProperty(K + ".rp")) && !"1".equals(P.getProperty(K + ".inv")) && @PKG@.GearLL.invested(id, d)) { P.setProperty(K + ".inv", "1"); ch = true; }''',
    '''  if ("1".equals(P.getProperty(K + ".rp"))) {
    boolean iv = @PKG@.GearLL.invested(id, d);
    boolean on = "1".equals(P.getProperty(K + ".inv"));
    if (iv && !on) { P.setProperty(K + ".inv", "1"); ch = true; }
    else if (!iv && on) { P.remove(K + ".inv"); ch = true; }          // fix round: 0.3.2 counts only reforges after the copy (lrpF)
  }''')
# ---- fix round (safety critic 1): /lifelong never swaps inside a copy family; settle says so
rep('''    if (!@PKG@.GearLL.isRt(d)) return "-That " + K + " is still being sorted out - try again in a moment.";''',
    '''    if (!@PKG@.GearLL.isRt(d)) return "-That " + K + " is still being sorted out - try again in a moment.";
    if (family(P, K, d)) return "-That " + K + " and your lifelong one are exact copies of each other, so the retired one stays retired (it keeps its rolls but breaks nothing).";''')
rep('''hold it and type /lifelong to swap them.", 5000L);''',
    '''" + (family(P, K, d) ? "your " + K + " is an exact copy of it, so the old one stays retired." : "hold it and type /lifelong to swap them."), 5000L);''')
# ---- fix round (fidelity critic 4): the Void can never hold a tool
rep('''Is a better tool in a chest, the Void or your Vault?''', '''Is a better tool in a chest or your Vault?''')
# ---- the commands
for _K, _N in (("pickaxe", "PickaxeCmd"), ("hatchet", "HatchetCmd"), ("hoe", "HoeCmd"), ("sickle", "SickleCmd")):
    rep('''public %s() {
  super("%s", "Lost your lifelong %s? Get a new Common one at your level and tier (only when you have none)");''' % (_N, _K, _K),
        '''public %s() {
  super("%s", "Lost your lifelong %s? Brings it back from a chest or Requip, or makes an exact copy (only when you have none)");''' % (_N, _K, _K))
rep('''    String r = @PKG@.GearLife.reclaim(pr, p, %d);''', '''    String r = @PKG@.GearLife.reclaimW(pr, p, %d, world);          // 0.3.2: the world (its loaded chests)''')
rep('''gll.getDeclaredMethod("sweepHook").setBody(J("{ @PKG@.GearLife.sweep($1, $2, false); }"))
''', '''gll.getDeclaredMethod("sweepHook").setBody(J("{ @PKG@.GearLife.sweep($1, $2, false); }"))
gll.getDeclaredMethod("trackHook").setBody(J("{ @PKG@.GearLife.trackLater($1, $2, $3); }"))          # 0.3.2
''')
# ---- the manifest sentence
rep('''(never crafted, dropped, sold or salvaged; /pickaxe, /hatchet, /hoe, /sickle replace a lost one)''',
    '''(never crafted, dropped, sold or salvaged; /pickaxe, /hatchet, /hoe, /sickle bring a lost one back from a chest or Requip, or make an exact copy)''')

assert "LL_RTIER)" not in s.split("# ---- 0.3.2 THE EXACT LOST TOOL")[1].split("# fix round 2 (safety critic 2): /lifelong on your own")[0], "reclaimTier still read"
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote %s (%d changes, %d -> %d lines)" % (DST, len(CHANGES), OLD.count(LF), s.count(LF)))
