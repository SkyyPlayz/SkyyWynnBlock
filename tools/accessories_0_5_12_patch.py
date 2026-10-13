"""Derive SkyyAccessories/build_skyyaccessories_0.5.12.py from the GENERATED 0.5.11 script (build_skyyaccessories_0.5.11.py = the
tools/deploy_set.py SET pin, written by tools/accessories_0_5_11_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.11 script
stays untouched - never re-run accessories_0_5_11_patch.py on top of this).
Run:  python tools/accessories_0_5_12_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.12.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.12.py

0.5.12 = THE LANTERN HIDE WITHOUT THE WALK (research/Code-Structure-Audit.md finding 3b, sev 4; Skyy 2026-10-13: "lets audit the code
structure, and make sure they are working together in the smoothest easiest lag free way possible"). No behaviour change for players.
  1. AccLanternHide.tick (the entity tracker's find-visible group, every viewer, every tick) walked each viewer's WHOLE visible-entity set
     and looked up every entity's archetype (150k-450k lookups a second at 50 players). Now the system tick builds ONCE per store per tick
     the list of the Lantern helper refs AccLantern already records (HELPER = the light above, RING = the ring lights; key = the wearer,
     the same uuid the helper's AccLanternMark carries) that are valid and live in THIS store (AccLantern.helpersIn), and each viewer only
     removes those refs (AccLantern.hideKnown: Set.remove per foreign helper - never an iteration of the visible set). The rule is the
     0.5.4 / fix-round rule unchanged: the wearer keeps their own; lantern.shareReach on = only a viewer who hid the wearer (/hide) loses it.
     SAFETY NET: when the store holds MORE marked entities than the recorded refs (store.getEntityCountFor(marker) > the list - an orphan /
     a parked copy AccLanternHelp has not removed yet), that tick uses the old full walk (hideFrom) for every viewer, so nothing a viewer
     should not see ever reaches them. The list travels from the system tick to the entity ticks in a ThreadLocal (the group is sequential:
     isParallel stays false, the entity ticks run on the same thread inside super.tick) and is cleared after super.tick.
  2. AccLantern.step: OWNER.put(u, ref) ran for every player every tick (a ConcurrentHashMap write = a node write + a volatile store). Now
     get first and put only when the entity ref changed (join, world change, respawn). `moved` is computed from the same prev as before.
Config, saves, bridge keys, items, assets: unchanged. Classes changed: AccLantern (2 methods added, step body), AccLanternHide (system
tick + entity tick bodies, 1 field). Everything else = 0.5.11 (version constants only; the config kit classes follow whatever
tools/skyycfg.py is in the tree at build time).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.11.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.12.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.11"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.11"\n' in s and "LAN_TEX_REL" in s and "hideKnown" not in s, "the source must be the generated 0.5.11 script"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.11 - build script (derived from the generated build_skyyaccessories_0.5.10.py by tools/accessories_0_5_11_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.11.py            -> SkyyAccessories/SkyyAccessories-0.5.11.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.11.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.11.py             (bare JVM -Xverify:all: class compare 0.5.10 -> 0.5.11 = no class change, the jar
       diff = the 4 Lantern textures, start twice on a live copy; JVM 2: the engine asset validators)
''', '''"""SkyyAccessories 0.5.12 - build script (derived from the generated build_skyyaccessories_0.5.11.py by tools/accessories_0_5_12_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.12.py            -> SkyyAccessories/SkyyAccessories-0.5.12.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.12.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.12.py             (bare JVM -Xverify:all: class compare 0.5.11 -> 0.5.12, hideKnown = hideFrom on
       random sets, the real entity tracker run on BOTH jars with the same results, start twice on a live copy)
0.5.12: THE LANTERN HIDE WITHOUT THE WALK (audit 3b; full notes in tools/accessories_0_5_12_patch.py): AccLanternHide removes only the
     recorded helper refs of the store from each viewer's visible set (one list per store per tick) instead of walking every visible
     entity; the old walk stays as the safety net when the store holds unrecorded marked entities. AccLantern.step writes OWNER only when
     the player's entity ref changed. No behaviour change.
''')
rep('VERSION = "0.5.11"\n', 'VERSION = "0.5.12"\n')

# ---------------------------------------------------------------------------------------------------------------- 2. OWNER.put only on change
rep('''  Object prev = OWNER.put(u, ref);
  boolean moved = prev != ref;
''', '''  Object prev = OWNER.get(u);
  boolean moved = prev != ref;
  if (moved) OWNER.put(u, ref);   // 0.5.12: no map write per player per tick - only when the entity ref changed
''')

# ---------------------------------------------------------------------------------------------------------------- 1. the recorded helpers
rep('''JM(lan, r"""
public static void prune(java.util.Set online) {
''', '''# 0.5.12 (audit 3b) THE RECORDED HELPERS OF ONE STORE (AccLanternHide's system tick, once per store per tick): every helper ref HELPER and
# RING hold that is valid and lives in this store, with its wearer (the map key = the uuid its AccLanternMark carries). Returns
# Object[] { Ref[] refs, UUID[] owners, Boolean full } - full = the store holds no marked entity outside the list (getEntityCountFor), so
# removing the listed refs is the whole job; false = an unrecorded marked entity exists this tick -> the old walk (hideFrom) for safety.
JM(lan, LANJ(r"""
public static Object[] helpersIn(@ST@ store) {
  java.util.ArrayList rl = new java.util.ArrayList();
  java.util.ArrayList ol = new java.util.ArrayList();
  java.util.Iterator it = HELPER.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object o = e.getValue();
    if (!(o instanceof @REF@)) continue;
    @REF@ r = (@REF@) o;
    if (!r.isValid() || r.getStore() != store) continue;
    rl.add(r);
    ol.add(e.getKey());
  }
  java.util.Iterator rt = RING.entrySet().iterator();
  while (rt.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) rt.next();
    Object o = e.getValue();
    if (!(o instanceof Object[])) continue;
    Object[] rs = (Object[]) o;
    for (int i = 0; i < rs.length; i++) {
      if (!(rs[i] instanceof @REF@)) continue;
      @REF@ r = (@REF@) rs[i];
      if (!r.isValid() || r.getStore() != store) continue;
      rl.add(r);
      ol.add(e.getKey());
    }
  }
  int n = rl.size();
  @REF@[] refs = new @REF@[n];
  java.util.UUID[] owners = new java.util.UUID[n];
  for (int i = 0; i < n; i++) { refs[i] = (@REF@) rl.get(i); owners[i] = (java.util.UUID) ol.get(i); }
  boolean full = false;
  try { full = T_MARK != null && store.getEntityCountFor((@QRY@) T_MARK) <= n; } catch (Throwable t) { full = false; }
  return new Object[] { refs, owners, Boolean.valueOf(full) };
}"""))
# 0.5.12: the same rule as hideFrom on the recorded list only: every listed helper that is not the viewer's own leaves the viewer's visible
# set (Set.remove - the set is never iterated); lantern.shareReach on = only for a viewer who hid that wearer. Returns how many went.
JM(lan, LANJ(r"""
public static int hideKnown(java.util.UUID me, @HPM@ hm, java.util.Set vis, Object[] known) {
  if (vis == null || known == null || vis.isEmpty()) return 0;
  @REF@[] refs = (@REF@[]) known[0];
  java.util.UUID[] owners = (java.util.UUID[]) known[1];
  boolean share = @PKG@.AccDefs.LAN_SHARE;
  int n = 0;
  for (int i = 0; i < refs.length; i++) {
    java.util.UUID ow = owners[i];
    if (ow != null && ow.equals(me)) continue;
    if (share && ow != null) {
      boolean hid = false;
      if (hm != null) hid = hm.isPlayerHidden(ow);
      if (!hid) continue;
    }
    if (vis.remove(refs[i])) n++;
  }
  if (n > 0) HIDDEN.addAndGet((long) n);
  return n;
}"""))
JM(lan, r"""
public static void prune(java.util.Set online) {
''')

# ---------------------------------------------------------------------------------------------------------------- AccLanternHide
rep('''JF(lhd, "public static boolean FAILED = false;")
''', '''JF(lhd, "public static boolean FAILED = false;")
# 0.5.12: the store's recorded helpers (AccLantern.helpersIn) from the system tick to its entity ticks - same thread (sequential group)
JF(lhd, "public static final java.lang.ThreadLocal KNOWN = new java.lang.ThreadLocal();")
JF(lhd, "public static final java.util.concurrent.atomic.AtomicLong FAST = new java.util.concurrent.atomic.AtomicLong();")
JF(lhd, "public static final java.util.concurrent.atomic.AtomicLong WALKS = new java.util.concurrent.atomic.AtomicLong();")
''')
rep('''public void tick(float dt, int systemIndex, @ST@ store) {
  if (@PKG@.AccLantern.T_MARK == null || @PKG@.AccLantern.T_EV == null || store == null) return;
  if (store.getEntityCountFor((@QRY@) @PKG@.AccLantern.T_MARK) == 0) return;
  super.tick(dt, systemIndex, store);
}""")''', '''public void tick(float dt, int systemIndex, @ST@ store) {
  if (@PKG@.AccLantern.T_MARK == null || @PKG@.AccLantern.T_EV == null || store == null) return;
  if (store.getEntityCountFor((@QRY@) @PKG@.AccLantern.T_MARK) == 0) return;
  Object[] k = null;
  try { k = @PKG@.AccLantern.helpersIn(store); } catch (Throwable t) { k = null; }
  KNOWN.set(k);
  super.tick(dt, systemIndex, store);
  KNOWN.set(null);
}""")''')
rep('''    @PKG@.AccLantern.hideFrom(me, hm, v.visible, cb);
  } catch (Throwable t) {''', '''    Object[] k = (Object[]) KNOWN.get();
    if (k != null && ((Boolean) k[2]).booleanValue()) {
      FAST.incrementAndGet();
      @PKG@.AccLantern.hideKnown(me, hm, v.visible, k);
    } else {
      WALKS.incrementAndGet();
      @PKG@.AccLantern.hideFrom(me, hm, v.visible, cb);   // the safety net: an unrecorded marked entity in this store this tick
    }
  } catch (Throwable t) {''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s.index("public static Object[] helpersIn") < s.index("lhd.addConstructor"), "AccLantern methods before AccLanternHide uses them"
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.11 - build script (derived from the generated build_skyyaccessories_0.5.10.py by tools/accessories_0_5_11_patch.py -',
    "Run:   python build_skyyaccessories_0.5.11.py            -> SkyyAccessories/SkyyAccessories-0.5.11.jar   (deploys go through tools/deploy_set.py --yes)",
    "       python build_skyyaccessories_0.5.11.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)",
    "Test:  python test_skyyaccessories_0.5.11.py             (bare JVM -Xverify:all: class compare 0.5.10 -> 0.5.11 = no class change, the jar",
    "       diff = the 4 Lantern textures, start twice on a live copy; JVM 2: the engine asset validators)",
    'VERSION = "0.5.11"',
    "  Object prev = OWNER.put(u, ref);",
    "    @PKG@.AccLantern.hideFrom(me, hm, v.visible, cb);",
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.11 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.11 had %d)" % (s.count(LF), OLD.count(LF)))
