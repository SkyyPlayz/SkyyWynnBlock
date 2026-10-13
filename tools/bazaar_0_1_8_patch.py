"""Derive SkyyBazaar/build_skyybazaar_0.1.8.py from the LIVE 0.1.7 (build_skyybazaar_0.1.7.py = the tools/deploy_set.py SET pin; 0.1.7 and every
older script stay untouched).
Run:  python tools/bazaar_0_1_8_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.8.py   then   python SkyyBazaar/test_skyybazaar_0.1.8.py
(never --deploy: coordinated deploy). Edit THIS patch, never the generated script.

0.1.8 (2026-10-13) = LAG FIXES from the code audit (research/Code-Structure-Audit.md finding #13 + pack-wide pattern 1; Skyy 2026-10-13:
"During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in the smoothest
easiest lag free way possible"). Same prices, same trades, same files - only less work:
 A. LOCK-FREE BRIDGE: BzUtil.bridge() caches the skyy.bridge map in the static volatile BzUtil.BRIDGE (only the first call takes the
    System.class monitor, to create the map exactly as before); the config kit's CfgRows.bridge() does the same (tools/skyycfg.py).
 B. BzTick (every 10 s, scheduler) no longer rewrites market.properties and re-quotes every product forever:
    - decay() still moves every demand factor toward 1.0 exactly as before (same formula, same 1e-4 snap to 1.0, same clamp), but it only
      PUBLISHES the ids whose factor really changed (bazaar:buy:<id> / bazaar:sell:<id>; 0.1.7 re-quoted all ~415 products + rebuilt the
      bazaar:products CSV every tick). An id snapped back to 1.0 is published too. With no factor away from 1.0 a tick publishes nothing.
    - decay() no longer marks market.properties dirty. Decay is a pure function of the saved factors and lastDecayMillis (the next
      start's first decay applies the whole gap since lastDecayMillis, as 0.1.7 did after any stop), so a file written up to 5 minutes
      earlier gives the SAME factors at the next start: decay-only changes (and lastDecayMillis alone) are persisted at most every
      5 minutes (Market.PEND + SAVED). Trades, /bazaaradmin reset and a reload still mark DIRTY and are written by the next tick (<= 10 s,
      as 0.1.7), always together with the current lastDecayMillis. Shutdown writes any pending decay too.
    - publishAll() (catalog / price / spread changes: start, reload, admin price, reset, a premium reprice) only re-puts the
      bazaar:products CSV when its text changed.
    Kept: the Market lock order, every quote / price / spread rule, trades.log, products.properties writes (still only when the catalog is
    dirty), the Catalog.tick premium check. Rolling back to 0.1.7 is safe (same files, same format).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.7.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.8.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.7"' in s and "market:veto" in s and "Market.PEND" not in s, "the source must be the generated 0.1.7 script"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:160])
    s = s.replace(old, new)


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyBazaar 0.1.7 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.7.py            -> SkyyBazaar/SkyyBazaar-0.1.7.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.7 is GENERATED from build_skyybazaar_0.1.6.py by tools/bazaar_0_1_7_patch.py - edit the patch, not this file; 0.1.6 came
       from 0.1.5 by tools/bazaar_0_1_6_patch.py, 0.1.5 from 0.1.4, 0.1.4 from 0.1.3, 0.1.3 from 0.1.2, 0.1.2 from 0.1.1, 0.1.1 from 0.1;
       every older script is kept as it was)
''', '''"""SkyyBazaar 0.1.8 - build script (javassist via jpype). Hypixel-Bazaar-style commodity market, MVP = INSTANT buy/sell against a
server market maker.
Run:   python build_skyybazaar_0.1.8.py            -> SkyyBazaar/SkyyBazaar-0.1.8.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.8 is GENERATED from build_skyybazaar_0.1.7.py by tools/bazaar_0_1_8_patch.py - edit the patch, not this file; 0.1.7 came
       from 0.1.6 by tools/bazaar_0_1_7_patch.py, 0.1.6 from 0.1.5, 0.1.5 from 0.1.4, 0.1.4 from 0.1.3, 0.1.3 from 0.1.2, 0.1.2 from
       0.1.1, 0.1.1 from 0.1; every older script is kept as it was)

''' + HEAD[HEAD.index("0.1.8 (2026-10-13)"):].strip() + '''
''')
rep('VERSION = "0.1.7"', 'VERSION = "0.1.8"')

# ---- Hytale 0.7.0 data: six NEW bag items (SkyySacks' bag rule now matches them) stop the build's TOTAL guard ("add each to PRODUCTS or a
# SKIP rule"). Pricing new products is Skyy's call, not a lag fix, so this round keeps 0.1.7's catalog exactly: they get their own SKIP
# rule with that reason (the next priced-catalog round removes it and adds rows).
rep('''    (r"^Food_Fish_Raw_(Rare|Epic|Legendary)$|^Plant_Seeds_Test_|^Plant_Test_",
     "never made in survival (their fish-gutting recipes give plain Raw Fish, which is listed; test items)"),
]''', '''    (r"^Food_Fish_Raw_(Rare|Epic|Legendary)$|^Plant_Seeds_Test_|^Plant_Test_",
     "never made in survival (their fish-gutting recipes give plain Raw Fish, which is listed; test items)"),
    (r"^Rock_Kenolite$|^Wood_Sadwillow_Trunk$|^Plant_Crop_Mushroom_Boomshroom_Small$|^Plant_Crop_Mushroom_Common_Lime_Large$|^Plant_Liana_Void$"
     r"|^Plant_Sapling_Sadwillow$",
     "new in Hytale 0.7.0 - not priced yet (0.1.8 keeps 0.1.7's catalog; a later Bazaar round prices them)"),
]''')

# ---- A: lock-free bridge
rep('''utl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", utl))''', '''# 0.1.8 A: lock-free bridge (research/Code-Structure-Audit.md): cached in BRIDGE after the first call; only that call takes the
# System.class monitor (creation exactly as before: get, create if absent, put)
utl.addField(CtField.make("public static volatile java.util.Map BRIDGE;", utl))
utl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""", utl))
utl.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""", utl))''')

# ---- B: Market fields
rep('''mkt.addField(CtField.make("public static boolean DIRTY = false;", mkt))
''', '''mkt.addField(CtField.make("public static boolean DIRTY = false;", mkt))
# 0.1.8 B: PEND = decay moved a factor or lastDecayMillis since the last write (persisted at most every 5 min: decay is reproducible from
# the saved factors + lastDecayMillis); SAVED = when the last snapshot was taken (millis); CSV = the bazaar:products text last put;
# MOVED = how many ids the last decay published (harness / status)
mkt.addField(CtField.make("public static boolean PEND = false;", mkt))
mkt.addField(CtField.make("public static long SAVED = 0L;", mkt))
mkt.addField(CtField.make("public static final long PEND_MS = 300000L;", mkt))
mkt.addField(CtField.make("public static String CSV = null;", mkt))
mkt.addField(CtField.make("public static int MOVED = 0;", mkt))
''')

# ---- B: publishAll only re-puts the CSV when its text changed
rep('''    publish(id);
    if (sb.length() > 0) sb.append(',');
    sb.append(id);
  }}
  {PKG}.BzUtil.bridge().put("bazaar:products", sb.toString());
}}""", mkt))''', '''    publish(id);
    if (sb.length() > 0) sb.append(',');
    sb.append(id);
  }}
  String csv = sb.toString();
  java.util.Map b = {PKG}.BzUtil.bridge();
  if (!csv.equals(CSV) || !csv.equals(b.get("bazaar:products"))) {{ b.put("bazaar:products", csv); CSV = csv; }}
}}""", mkt))''')
rep('''    b.remove("bazaar:sell:" + id); b.remove("bazaar:buy:" + id);
  }}
  b.remove("bazaar:products");
}}""", mkt))''', '''    b.remove("bazaar:sell:" + id); b.remove("bazaar:buy:" + id);
  }}
  b.remove("bazaar:products");
  CSV = null;
}}""", mkt))''')

# ---- B: decay publishes only moved ids and defers decay-only writes
rep('''public static synchronized void decay(long now) {
  if (LAST <= 0L) { LAST = now; DIRTY = true; return; }
  long dt = now - LAST;
  if (dt < 1000L) return;
  if (dt > 604800000L) dt = 604800000L;
  double k = Math.pow(0.5, (double) dt / (HALFLIFE * 60000.0));
  java.util.Iterator it = new java.util.ArrayList(F.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    double f = ((Double) F.get(id)).doubleValue();
    double nf = clampF(Math.exp(Math.log(f) * k));
    if (Math.abs(nf - 1.0) < 0.0001) F.remove(id); else F.put(id, Double.valueOf(nf));
  }
  LAST = now;
  DIRTY = true;
  publishAll();
}''', '''public static synchronized void decay(long now) {
  if (LAST <= 0L) { LAST = now; DIRTY = true; return; }
  long dt = now - LAST;
  if (dt < 1000L) return;
  if (dt > 604800000L) dt = 604800000L;
  double k = Math.pow(0.5, (double) dt / (HALFLIFE * 60000.0));
  java.util.ArrayList moved = new java.util.ArrayList();
  java.util.Iterator it = new java.util.ArrayList(F.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    double f = ((Double) F.get(id)).doubleValue();
    double nf = clampF(Math.exp(Math.log(f) * k));
    if (Math.abs(nf - 1.0) < 0.0001) { F.remove(id); moved.add(id); }
    else if (nf != f) { F.put(id, Double.valueOf(nf)); moved.add(id); }
  }
  LAST = now;
  PEND = true;
  if (now - SAVED >= PEND_MS) DIRTY = true;
  for (int i = 0; i < moved.size(); i++) publish((String) moved.get(i));
  MOVED = moved.size();
}
''' + '''""", mkt))
# 0.1.8 B: shutdown writes a pending decay too (the next start would recompute it anyway - this keeps the file current)
mkt.addMethod(CtNewMethod.make("""
public static synchronized void forcePending() {
  if (PEND) DIRTY = true;
}''')
rep('''public static synchronized java.util.Properties snapshot() {
  if (!DIRTY) return null;
  DIRTY = false;''', '''public static synchronized java.util.Properties snapshot() {
  if (!DIRTY) return null;
  DIRTY = false;
  PEND = false;
  SAVED = System.currentTimeMillis();''')
rep('''    LAST = last;
    F.clear(); BOUGHT.clear(); SOLD.clear();''', '''    LAST = last;
    PEND = false;
    F.clear(); BOUGHT.clear(); SOLD.clear();''')

# ---- shutdown: pending decay is written
rep('''  try { @PKG@.Market.decay(System.currentTimeMillis()); @PKG@.Market.flush(); } catch (Throwable t) { }''',
    '''  try { @PKG@.Market.decay(System.currentTimeMillis()); @PKG@.Market.forcePending(); @PKG@.Market.flush(); } catch (Throwable t) { }''')

assert "synchronized (java.lang.System.class) {\n" not in s, "no old-style bridge left"
assert not os.path.exists(dst), dst + " already exists - delete it first (it is generated)"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
