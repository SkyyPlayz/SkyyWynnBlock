"""Derive SkyyAccessories/build_skyyaccessories_0.5.6.py from the GENERATED 0.5.5 script (build_skyyaccessories_0.5.5.py = the
tools/deploy_set.py SET pin, written by tools/acc_0_5_5_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.5 script stays
untouched - never re-run acc_0_5_5_patch.py on top of this).
Run:  python tools/acc_0_5_6_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.6.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.6.py   (bare JVM -Xverify:all; the 0.5.5 harness still covers every unchanged class)

0.5.6 = THE LANTERN RECIPES FOLLOW THE TREE SAP COLLECTION (Skyy 2026-10-05, LOCKED, docs/answered/economy.md: "add the lantern
accessory's crafting recipe to the sap collection. so you have to collect a lot to get a legendary lantern"). SkyyCollections 0.2.7 is
the other half (it unlocks the four recipe ids at Tree Sap tiers - Server Setup rows - and publishes coll:lantern while it manages them).
The SkyySacks bag mechanism (0.7.7 KnowSync), for the four Lantern items only:
  - The four Lantern recipes (Skyy_Talisman_Lantern_Common / _Uncommon / _Rare / _Epic = Normal / Unique / Rare / Legendary) are
    "KnowledgeRequired": the engine refuses the craft at a real bench unless the player knows the output (CraftingManager, VERIFIED in
    SkyySacks 0.7.7); SkyySacks' /craft lists a knowledge recipe only when it is known. Inputs, bench, tab, looks, texts: unchanged.
  - New AccKnow (called once a second per player from AccEffects.tick, the world thread; never throws): owns exactly those four ids in
    the player's known-recipe set (PlayerConfigData, saved per PLAYER) and never touches another entry; one UpdateKnownRecipes packet
    only when something changed.
      managed (bridge coll:lantern is a tier String = SkyyCollections 0.2.7+ manages them): a Lantern is known exactly while its recipe
        id is in coll:recipes:<uuid>; no coll:recipes for the player yet = change nothing for 10 s, then no Lantern known (never the
        last profile's set); 6 s after a profile:epoch change = change nothing (the coll:recipes republish, SkyySacks' settle window).
      free (coll:lantern = "off": SkyyCollections without a visible TreeSap collection, also right after a reload; or no coll:lantern
        ever seen in this JVM: SkyyCollections missing or older than 0.2.7): all four known - every Lantern craftable, the 0.5.5 behaviour.
      hold (coll:lantern seen earlier in this JVM and gone now: SkyyCollections shutting down): change nothing.
    A profile still loading (AccStore.moveBlock) = change nothing this second.
  - EXISTING PLAYERS: every Lantern already crafted or owned stays exactly as it is (no item is read, moved or removed; the bag, the
    light and the equip rules are 0.5.5's). Nobody knew a Lantern recipe before (they were not knowledge recipes), so nothing is taken
    back: from now on crafting the next Lantern needs its Tree Sap tier. A player who already reached the tiers gets them at once.
  - HIDDEN LIGHTS ROW TEXT FIX (RESUME: "'Hidden lights: most' 2-3 act like 1"): the solver puts a RING of 3-8 lights around the light
    above (a ring of 1 or 2 can never lift the worst direction's reach - the walk between two ring lights / away from a single one only
    meets the centre light), so 1, 2 and 3 all mean one light. The cheaper correct fix is the TEXT (no light-model change): the row help
    and the config comment now say "1-3 = one light above the wearer; 4-9 = that light + a ring of 3-8 around it". Values, range,
    solver and every saved file unchanged.
  - Config kit KEEP 20 -> 10 (AGENT-BRIEF rule, kit default since 2026-10-05).
UNVERIFIED (in game only): the Workbench tab hiding / greying an unknown Lantern recipe, the knowledge packet reaching an open bench.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.5.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.6.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.5"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.5"\n' in s and "lanRingReach" in s and "AccKnow" not in s, "the source must be the generated 0.5.5 script"

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.5 - build script (derived from the generated build_skyyaccessories_0.5.4.py by tools/acc_0_5_5_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.5.py            -> SkyyAccessories/SkyyAccessories-0.5.5.jar
       python build_skyyaccessories_0.5.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.5.py             (bare JVM -Xverify:all: every 0.5.4 check in the 0.5.4 light layout + the
                                                         soft ring on the real ECS world and entity tracker + the height update + Y)
''', '''"""SkyyAccessories 0.5.6 - build script (derived from the generated build_skyyaccessories_0.5.5.py by tools/acc_0_5_6_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.6.py            -> SkyyAccessories/SkyyAccessories-0.5.6.jar
       python build_skyyaccessories_0.5.6.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.6.py             (bare JVM -Xverify:all: the 0.5.6 changes; test_skyyaccessories_0.5.5.py still
                                                         covers every class 0.5.6 leaves unchanged)
0.5.6: THE LANTERN RECIPES FOLLOW THE TREE SAP COLLECTION (Skyy 2026-10-05: "add the lantern accessory's crafting recipe to the sap
     collection. so you have to collect a lot to get a legendary lantern"; full notes in tools/acc_0_5_6_patch.py):
     - the four Lantern recipes are KnowledgeRequired; AccKnow (1 s, world thread) keeps exactly those four ids in each player's known
       recipes: while SkyyCollections 0.2.7+ publishes coll:lantern, known = the Lantern recipe ids in coll:recipes:<uuid> (Tree Sap
       tiers, Server Setup rows in SkyyCollections); without it every Lantern stays craftable (0.5.5). Owned Lanterns never change.
     - Hidden lights: most - the row help / config comment now say 1-3 = one light, 4-9 = one light + a ring of 3-8 (the solver's rule).
     - config kit KEEP 10.
     - review fixes: coll:lantern "off" = free (no freeze after a reload hides Tree Sap); 6 s settle after a profile switch; no
       coll:recipes for 10 s = no Lantern known.
''')
rep('VERSION = "0.5.5"\n', 'VERSION = "0.5.6"\n')

# ---------------------------------------------------------------------------------------------------------------- hidden lights text
rep('''    "# lantern.lights is the most hidden lights per wearer, 1-9 (just 1 is one big light, as in 0.5.4). lantern.shareReach true shows the",
    "# hidden lights to everyone near the wearer too (their bits near them can glow brightly).",''',
    '''    "# lantern.lights is the most hidden lights per wearer, 1-9: 1-3 give one light above the wearer (as in 0.5.4; a ring needs 3",
    "# more), 4-9 give that light + a ring of 3-8 around it. lantern.shareReach true shows the hidden lights to everyone near the wearer too",
    "# (their bits near them can glow brightly).",''')
rep('''     "live,adv", "Hidden lights per wearer, the one above them included. 1 = one light only (0.5.4).",''',
    '''     "live,adv", "1-3 = one light above the wearer; 4-9 = that light + a ring of 3-8 lights around it.",''')

# ---------------------------------------------------------------------------------------------------------------- KEEP
rep('''RELOAD="AccCfg.reload", KEEP=20,''', '''RELOAD="AccCfg.reload", KEEP=10,''')
rep('''# (KEEP 20, verified by m51Saved before the rewrite)''', '''# (KEEP 10 since 0.5.6, verified by m51Saved before the rewrite)''')

# ---------------------------------------------------------------------------------------------------------------- items
rep('''    _node = item(_iid, icon_of(LAN_LOOKS[_t - 1]), QUAL_IDS[_t], _rin, WB_REQ, visual=_look)
''', '''    _node = item(_iid, icon_of(LAN_LOOKS[_t - 1]), QUAL_IDS[_t], _rin, WB_REQ, visual=_look)
    _node["Recipe"]["KnowledgeRequired"] = True   # 0.5.6: unlocked through the Tree Sap collection (AccKnow follows coll:recipes)
''')
rep('''        assert n["Icon"] == icon_of(LAN_LOOKS[t - 1]) and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)
''', '''        assert n["Icon"] == icon_of(LAN_LOOKS[t - 1]) and "Interactions" not in n and n["PlayerAnimationsId"] == "Item", (i, n)
        assert n["Recipe"].get("KnowledgeRequired") is True, ("0.5.6: a Lantern recipe must be a knowledge recipe", i)
''')
rep('''    assert len(set(items[i]["Icon"] for i in LAN_IDS)) == 4 and len(set(items[i]["Model"] for i in LAN_IDS)) == 4
''', '''    assert len(set(items[i]["Icon"] for i in LAN_IDS)) == 4 and len(set(items[i]["Model"] for i in LAN_IDS)) == 4
    _kr = sorted(i for i, n in items.items() if (n.get("Recipe") or {}).get("KnowledgeRequired"))
    assert _kr == sorted(LAN_IDS), ("0.5.6: exactly the four Lantern recipes are knowledge recipes", _kr)
''')

# ---------------------------------------------------------------------------------------------------------------- AccKnow
rep('''lhd  = pool.makeClass(PKG + ".AccLanternHide", pool.get(ETS))    # 0.5.4: Lantern - the system on every viewer (others' helpers unseen)
''', '''lhd  = pool.makeClass(PKG + ".AccLanternHide", pool.get(ETS))    # 0.5.4: Lantern - the system on every viewer (others' helpers unseen)
kn   = pool.makeClass(PKG + ".AccKnow")                          # 0.5.6: the Lantern recipe knowledge follows SkyyCollections (Tree Sap)
''')
KNOW = r'''
# ================= 0.5.6 AccKnow: the Lantern recipe knowledge (the SkyySacks 0.7.7 KnowSync pattern, the four Lantern ids only) =================
# VERIFIED bytecode (HytaleServer.jar): PlayerConfigData.getKnownRecipes() = an unmodifiable view, setKnownRecipes(Set) stores it and
# marks the data changed (saved with the PLAYER); CraftingPlugin.sendKnownRecipes(Ref, ComponentAccessor) only reads PlayerRef + Player
# and sends UpdateKnownRecipes. Called from AccEffects.tick (world thread, once a second per player). Bridge reads only (java.lang).
KN_PCD = "com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData"
KN_CRF = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
for c, m in ((PLA, "getPlayerConfigData"), (KN_PCD, "getKnownRecipes"), (KN_PCD, "setKnownRecipes"), (KN_CRF, "sendKnownRecipes"),
             (ST, "getComponent")):
    B.probe(pool, c, m)
def KNJ(src):
    return src.replace("@PCD@", KN_PCD).replace("@CRF@", KN_CRF)
JF(kn, 'public static final String SFX = "_Recipe_Generated_0";')
JF(kn, "public static volatile boolean SEEN = false;")
JF(kn, "public static volatile boolean FREENOTE = false;")
JF(kn, "public static volatile long WARNAT = 0L;")
# review fixes: SETTLE_MS after a profile:epoch change = change nothing (SkyyCollections republishes coll:recipes for the new profile in
# that time - the SkyySacks settle window); ABSENT_MS without any coll:recipes for a player (managed, settled) = they know no Lantern
JF(kn, "public static volatile long SETTLE_MS = 6000L;")
JF(kn, "public static volatile long ABSENT_MS = 10000L;")
JF(kn, "public static final java.util.concurrent.ConcurrentHashMap LASTEP = new java.util.concurrent.ConcurrentHashMap();")
JF(kn, "public static final java.util.concurrent.ConcurrentHashMap CHANGEDAT = new java.util.concurrent.ConcurrentHashMap();")
JF(kn, "public static final java.util.concurrent.ConcurrentHashMap ABSENT = new java.util.concurrent.ConcurrentHashMap();")
JM(kn, r"""
public static void warnOnce(String m) {
  long now = System.currentTimeMillis();
  if (now - WARNAT > 60000L) { WARNAT = now; @PKG@.AccStore.warn(m); }
}""")
# "managed" = SkyyCollections 0.2.7+ manages the Lantern recipes (coll:lantern, a tier String); "free" = it says "off" (no visible
# TreeSap, also after a reload) or was never seen (missing, older): all four known; "hold" = seen earlier in this JVM and the key is
# gone (a shutdown in progress: change nothing)
JM(kn, r"""
public static String mode() {
  Object v = null;
  try { v = @PKG@.AccStore.bridge().get("coll:lantern"); } catch (Throwable t) { v = null; }
  if (v instanceof String) {
    SEEN = true;
    if (!"off".equals(v)) return "managed";
    if (!FREENOTE) { FREENOTE = true; @PKG@.AccCfg.info("SkyyCollections does not manage the Lantern recipes (no visible Tree Sap collection) - every Lantern recipe stays craftable"); }
    return "free";
  }
  if (SEEN) return "hold";
  if (!FREENOTE) { FREENOTE = true; @PKG@.AccCfg.info("SkyyCollections does not manage the Lantern recipes (not installed, older than 0.2.7, or no Tree Sap collection) - every Lantern recipe stays craftable"); }
  return "free";
}""")
# review fix: false while a profile switch settles (profile:epoch:<uuid> changed less than SETTLE_MS ago; the first value seen is the
# baseline, an absent epoch is no change - PROFILES-CONTRACT 4.2, as SkyySacks' settledKey)
JM(kn, r"""
public static boolean settled(java.util.UUID u) {
  Object e = null;
  try { e = @PKG@.AccStore.bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { e = null; }
  long now = System.currentTimeMillis();
  if (e != null) {
    Object le = LASTEP.put(u, e);
    if (le != null && !le.equals(e)) { CHANGEDAT.put(u, Long.valueOf(now)); ABSENT.remove(u); }
  }
  Long t = (Long) CHANGEDAT.get(u);
  if (t == null) return true;
  if (now - t.longValue() < SETTLE_MS) return false;
  CHANGEDAT.remove(u);
  return true;
}""")
# the Lantern item ids this player should know; null = change nothing (hold, a profile switch settling, or SkyyCollections has not
# published this player yet - for up to ABSENT_MS; after that, no coll:recipes = no Lantern known, never another profile's)
JM(kn, r"""
public static java.util.HashSet wanted(java.util.UUID u) {
  String m = mode();
  if (m.equals("hold")) return null;
  String[] ids = @PKG@.AccDefs.LAN_IDS;
  java.util.HashSet out = new java.util.HashSet();
  if (m.equals("free")) {
    for (int i = 0; i < ids.length; i++) out.add(ids[i]);
    return out;
  }
  if (u == null) return null;
  if (!settled(u)) return null;
  Object v = null;
  try { v = @PKG@.AccStore.bridge().get("coll:recipes:" + u.toString()); } catch (Throwable t) { v = null; }
  if (v == null) {
    long now = System.currentTimeMillis();
    Long f = (Long) ABSENT.get(u);
    if (f == null) { ABSENT.put(u, Long.valueOf(now)); return null; }
    if (now - f.longValue() < ABSENT_MS) return null;
    return out;
  }
  ABSENT.remove(u);
  if (!(v instanceof String)) return null;
  String[] parts = ((String) v).split(",");
  java.util.HashSet have = new java.util.HashSet();
  for (int i = 0; i < parts.length; i++) { String x = parts[i].trim(); if (x.length() > 0) have.add(x); }
  for (int i = 0; i < ids.length; i++) if (have.contains(ids[i] + SFX)) out.add(ids[i]);
  return out;
}""")
# set exactly the four Lantern ids of the known set to want (every other entry kept); true = it changed (the caller sends the packet)
JM(kn, KNJ(r"""
public static boolean apply(@PCD@ d, java.util.HashSet want) {
  if (d == null || want == null) return false;
  java.util.Set known = d.getKnownRecipes();
  String[] ids = @PKG@.AccDefs.LAN_IDS;
  boolean diff = false;
  for (int i = 0; i < ids.length && !diff; i++) {
    boolean has = known != null && known.contains(ids[i]);
    if (has != want.contains(ids[i])) diff = true;
  }
  if (!diff) return false;
  java.util.HashSet ns = known == null ? new java.util.HashSet() : new java.util.HashSet(known);
  for (int i = 0; i < ids.length; i++) {
    if (want.contains(ids[i])) ns.add(ids[i]);
    else ns.remove(ids[i]);
  }
  d.setKnownRecipes(ns);
  return true;
}"""))
# once a second per player (AccEffects.tick, world thread): -1 skipped (no player / profile loading / change nothing), 0 already right,
# 1 changed + UpdateKnownRecipes sent. Never throws (one WARN a minute).
JM(kn, KNJ(r"""
public static int tick(@REF@ ref, @ST@ store, java.util.UUID u) {
  try {
    if (ref == null || store == null || u == null) return -1;
    if (@PKG@.AccStore.moveBlock(u) != null) return -1;
    java.util.HashSet want = wanted(u);
    if (want == null) return -1;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return -1;
    if (!apply(p.getPlayerConfigData(), want)) return 0;
    @CRF@.sendKnownRecipes(ref, store);
    return 1;
  } catch (Throwable t) { warnOnce("Lantern recipe knowledge sync failed: " + t); return -1; }
}"""))

# ================= AccEffects: accessory stats (EntityTickingSystem on Player entities, runs on each world's thread) ================='''
rep('''
# ================= AccEffects: accessory stats (EntityTickingSystem on Player entities, runs on each world's thread) =================''', KNOW)
rep('''  // 6. the one-time 0.5 notice
  try { @PKG@.AccNotice.check(pr, u); }
  catch (Throwable t) { if (!F_NOTE) { F_NOTE = true; @PKG@.AccStore.warn("the 0.5 notice failed (logged once): " + t); } }
}""".replace(''', '''  // 6. the one-time 0.5 notice
  try { @PKG@.AccNotice.check(pr, u); }
  catch (Throwable t) { if (!F_NOTE) { F_NOTE = true; @PKG@.AccStore.warn("the 0.5 notice failed (logged once): " + t); } }
  // 7. 0.5.6: the Lantern recipe knowledge follows SkyyCollections' Tree Sap tiers (AccKnow never throws)
  @PKG@.AccKnow.tick(ref, store, u);
}""".replace(''')
rep('''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, lmk, lms, lan, lsys, lhs, lhd):   # 0.5.4: the Lantern (AccNv, AccNightVision gone)''',
    '''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, lmk, lms, lan, lsys, lhs, lhd, kn):   # 0.5.4: the Lantern (AccNv, AccNightVision gone); 0.5.6: + AccKnow''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.index("public static int tick(@REF@ ref, @ST@ store, java.util.UUID u)") < s.index("@PKG@.AccKnow.tick(ref, store, u);")
assert s.index("public static void info(String msg)") < s.index("public static String mode()"), "AccCfg.info must compile before AccKnow"
assert "KEEP=20" not in s
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.5 - build script (derived from the generated build_skyyaccessories_0.5.4.py by tools/acc_0_5_5_patch.py - edit',
    "Run:   python build_skyyaccessories_0.5.5.py            -> SkyyAccessories/SkyyAccessories-0.5.5.jar",
    "       python build_skyyaccessories_0.5.5.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world",
    "Test:  python test_skyyaccessories_0.5.5.py             (bare JVM -Xverify:all: every 0.5.4 check in the 0.5.4 light layout + the",
    "                                                         soft ring on the real ECS world and entity tracker + the height update + Y)",
    'VERSION = "0.5.5"',
    '    "# lantern.lights is the most hidden lights per wearer, 1-9 (just 1 is one big light, as in 0.5.4). lantern.shareReach true shows the",',
    '    "# hidden lights to everyone near the wearer too (their bits near them can glow brightly).",',
    '     "live,adv", "Hidden lights per wearer, the one above them included. 1 = one light only (0.5.4).",',
    "# (KEEP 20, verified by m51Saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one",
    'for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear, lmk, lms, lan, lsys, lhs, lhd):   # 0.5.4: the Lantern (AccNv, AccNightVision gone)',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED and "KEEP=20" not in ln and not ln.startswith('"""SkyyAccessories 0.5.5') and "the patch, not this file)" != ln]
assert not _bad, "0.5.5 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.5 had %d)" % (s.count(LF), OLD.count(LF)))
