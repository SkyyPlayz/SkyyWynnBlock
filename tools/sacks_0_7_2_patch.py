"""Derive SkyySacks/build_skyysacks_0.7.2.py from 0.7.1.
0.7.2: per-profile storage (tools/PROFILES-CONTRACT.md).
 - SackPool gets the contract's bridge()/pkey() helper (verbatim), epoch(uuid) and settledKey(uuid).
 - Rule 1: pools/<pkey>.properties and processing/<pkey>.properties; crafts.log lines carry the pkey instead of the uuid.
 - Rule 2: SackPool.POOLS/DIRTY/EXEMPT, ProcStore.STATES/DIRTY/BROKEN and BagMirror.MIRRORS are keyed by the pkey String.
   A BagMirror remembers the key it was built from, so bench consumption is always deducted from the pool it mirrors; when the
   active key changes, CraftLinkTask retires the old mirror (sync into its own pool, save, drop) and swaps it out of any open
   bench window in the same world-thread run.
 - Every sweep / page / bench / processing path resolves the pkey ONCE per run or click and passes it down.
 - Settle window: for SETTLE_MS (3 s; 6 s since the integration fixes) after the epoch or the key changes, the sweep skips and page item moves are refused (guards a
   non-atomic inventory swap in SkyyProfiles); a page built for another key refuses the click and rebuilds for the new profile.
 - Rule 3: SkyySacks publishes no per-player bridge values; ProcTask (existing 1 s tick) remembers profile:epoch:<uuid> per
   player - on a change it flushes every dirty file off the world thread and logs the switch; an open Sacks/Craft page built
   for another key gets a set()-only "profile changed" notice (the proven live() pattern; the rebuild happens on the next click).
 - Rules 4-6: nothing applied to the live player; vanilla inventory never touched; the Craftable-only toggle stays per player.
Without SkyyProfiles pkey = uuid.toString() = profile 1 and the epoch stays absent (-1): same files, same log lines, same behaviour.
Review fixes (0.7.2 review, same version):
 - HIGH: the bench link (CraftLinkTask) resolves the key with settledKey, not pkey. While a switch settles it only PARKS the bench
   mirror (BagMirror.park: sync what the bench already took into the mirror's own pool, empty the mirror, let the engine re-feed
   its vanilla nearby-chest resources via setValid(false) + getExtraResourcesSection()) - no retireOther, no rebuild, no feeding of
   any key until the switch settles. CraftPage.build() no longer builds a BagMirror for an unsettled key either (viewMats: the
   page shows inventory-only counts while settling); every craft/processing click already threads the ONE settled key it checked.
 - LOW: pool saves from world-thread code (Sacks page clicks, bench link, instant craft, mirror retire/park) use the new
   SackPool.saveSoon(k) (mark dirty + SackSaver on the scheduler thread) instead of the blocking SackPool.save(k).
 - LOW: the PROFILE log lines (epochCheck, retired/parked mirror) are queued with CraftLog.later and written by the SackSaver
   (SackSaver.run now also drains CraftLog.PENDING, so its run() is added below CraftLog); shutdown drains the queue too.
Integration fixes against the pinned SkyyProfiles 0.1 semantics (tools/PROFILES-CONTRACT.md "Semantics of SkyyProfiles 0.1", same
version). settledKey(u) is the one gate every item move goes through (sweep, Sacks page clicks, craft/processing clicks, bench link);
it now returns null (= paused: no sweep, clicks refused, bench mirror parked) also when:
 - HIGH: profile:busy:<uuid> is present (contract 4.5). SkyyProfiles sets it at PlayerConnectEvent while a crash recovery is pending
   and clears it after the recovery loaded the active profile's snapshot on the player's world thread; a sweep in between (the 2 s
   SackTick reaches a player as soon as the entity is in a world) moved items of the pre-recovery inventory into the pool, and the
   recovery then reloaded them from the snapshot: duplicated.
 - MEDIUM: SkyyProfiles is installed (profile:fn:key present) but profile:epoch:<uuid> is absent for this online player. Contract
   4.4 / 5: that means the players file is unreadable with no good copy and the Function falls back to profile 1's key while the live
   inventory may belong to profile N - a sweep would move profile N's items into profile 1's pool. Logged once per episode.
 - MEDIUM: the player's pool file could not be read. Before, pool() cached an EMPTY pool on a read error and the next save replaced
   the real file with it (every stored item lost); the first read of each profile's pool happens right after a switch. Now a failed
   read is not cached (views show it empty, saveNow never writes a key that is not loaded), retried at most every 2 s, logged once.
 - epoch() returns -1 when profile:epoch:<uuid> is absent; a transition from or to "absent" is a baseline, not a change (contract
   4.2), in settledKey and in ProcTask.epochCheck.
 - LOW: SETTLE_MS 3 s -> 6 s. The switch itself is one world-thread task (no inventory race), but acc:has:<uuid> (SkyyAccessories,
   up to its 5 s AccTick) and coll:recipes:<uuid> (SkyyCollections, 5 s saver tick) are republished for the new profile a few seconds
   later; craft clicks in that gap used the previous profile's bench accessories and collection unlocks.
 - LOW: SackPool.saveNow re-marks the key dirty when the write fails (Windows: a rename refused while another process holds the file)
   instead of dropping the change until the next add; SackPool/ProcStore.flushDirty iterate a snapshot of the dirty keys.
 - LOW: plugin shutdown syncs every bench mirror into its own pool (BagMirror.syncAll) before the last flush: bench crafts from bag
   items in the last <= 300 ms before a stop (or since the player disconnected at an open bench) were never debited.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.1.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.2.py")
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
        assert old in b, "anchor missing in block %r: %r" % (sig[:60], old[:80])
        b = b.replace(old, new)
    s = s[:i] + b + s[j:]


# ---------------- docstring + version ----------------
rep('"""SkyySacks 0.1.3 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.6.0.py            -> SkyySacks/SkyySacks-0.1.1.jar' + LF
    + '       python build_skyysacks_0.6.0.py --deploy   -> also',
    '"""SkyySacks 0.7.2 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.2.py            -> SkyySacks/SkyySacks-0.7.2.jar' + LF
    + '       python build_skyysacks_0.7.2.py --deploy   -> also')
rep('offline progress and an output slot (Skyy_SkyySacks/processing/<uuid>.properties); BagMirror.sync idempotent (no double bag deduction).' + LF + '"""',
    'offline progress and an output slot (Skyy_SkyySacks/processing/<uuid>.properties); BagMirror.sync idempotent (no double bag deduction).' + LF
    + '0.7.2: per-profile storage (tools/PROFILES-CONTRACT.md): pools/<pkey>.properties, processing/<pkey>.properties, crafts.log lines' + LF
    + 'carry the pkey; pool/exemption/processing/BagMirror caches keyed by the pkey String; sweep, pages, bench link and processing resolve' + LF
    + 'the pkey once per run (a bench mirror keeps its key and is retired into its own pool on a switch); 6s settle window after a switch' + LF
    + '(no sweep, page item moves refused); ProcTask checks profile:epoch:<uuid> every second (flush saves, log, notice on an open page).' + LF
    + 'Review fixes: the bench link uses settledKey and parks the mirror (bag materials off the open bench) while a switch settles; the craft' + LF
    + 'page never builds a mirror for an unsettled key; world-thread pool saves go through SackPool.saveSoon (SackSaver thread); PROFILE log' + LF
    + 'lines are queued (CraftLog.later) and written by the SackSaver.' + LF
    + 'Integration fixes (SkyyProfiles 0.1 semantics): settledKey also pauses item moves while profile:busy:<uuid> is set (crash recovery' + LF
    + 'at join), while SkyyProfiles is installed but published no epoch for the player (unreadable players file) and while the pool file' + LF
    + 'cannot be read (a failed read is no longer cached as an empty pool that the next save wrote over the file); absent epoch = baseline;' + LF
    + 'settle window 6s (covers the acc:has / coll:recipes republish); failed pool saves stay dirty; shutdown syncs open bench mirrors.' + LF
    + 'Derived by tools/sacks_0_7_2_patch.py. Without SkyyProfiles pkey = uuid = profile 1: same files, same behaviour.' + LF + '"""')
rep('VERSION = "0.7.1"', 'VERSION = "0.7.2"')

# ---------------- SackPool: contract helper, epoch, settle window ----------------
rep('sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))' + LF,
    'sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))' + LF + LF.join([
        '# integration fix: 6 s, not 3 - the switch is one world-thread task, but acc:has / coll:recipes follow the new profile only on',
        '# the next SkyyAccessories / SkyyCollections republish (up to their 5 s ticks); craft clicks wait until those are current.',
        'sp.addField(CtField.make("public static final long SETTLE_MS = 6000L;", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENEPOCH = new java.util.concurrent.ConcurrentHashMap();", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENKEY = new java.util.concurrent.ConcurrentHashMap();", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CHANGEDAT = new java.util.concurrent.ConcurrentHashMap();", sp))',
        '# integration fix: pool keys whose file could not be read (key -> time of the last failed read; never cached as an empty pool) and',
        '# players whose profile state is unknown (SkyyProfiles installed, no profile:epoch published) - both only for warn-once + retry pacing.',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BADPOOL = new java.util.concurrent.ConcurrentHashMap();", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap UNKNOWN = new java.util.concurrent.ConcurrentHashMap();", sp))',
        '# 0.7.2 profile contract (tools/PROFILES-CONTRACT.md): bridge + pkey helper exactly as the contract gives it. Without SkyyProfiles',
        '# pkey(u) = u.toString() = profile 1 (the pre-0.7.2 file names). Per-player bridge values we READ (acc:has, coll:recipes) stay keyed by UUID.',
        'sp.addMethod(CtNewMethod.make("""',
        'public static java.util.Map bridge() {',
        '  Object b = System.getProperties().get("skyy.bridge");',
        '  if (b instanceof java.util.Map) return (java.util.Map) b;',
        '  return java.util.Collections.EMPTY_MAP;',
        '}""", sp))',
        'sp.addMethod(CtNewMethod.make("""',
        'public static String pkey(java.util.UUID u) {',
        '  try {',
        '    Object f = bridge().get("profile:fn:key");',
        '    if (f instanceof java.util.function.Function) {',
        '      Object r = ((java.util.function.Function) f).apply(u);',
        '      if (r instanceof String && ((String) r).length() > 0) return (String) r;',
        '    }',
        '  } catch (Throwable t) { }',
        '  return u.toString();',
        '}""", sp))',
        '# profile:epoch:<uuid> as a long; -1 = absent (SkyyProfiles missing, or it has not published this player: contract 3 "Epoch").',
        '# An absent epoch carries no information - going from or to -1 is never treated as a profile change (contract 4.2).',
        'sp.addMethod(CtNewMethod.make("""',
        'public static long epoch(java.util.UUID u) {',
        '  try {',
        '    Object e = bridge().get("profile:epoch:" + u.toString());',
        '    if (e instanceof Number) return ((Number) e).longValue();',
        '    if (e != null) return Long.parseLong(String.valueOf(e).trim());',
        '  } catch (Throwable t) { }',
        '  return -1L;',
        '}""", sp))',
        '# settledKey(u) is added below pool() (it needs ready(k)); see "integration fixes" further down.',
    ]) + LF)

SPA = 'sp.addField(CtField.make("public static final Object SAVELOCK'
blk('public static void exempt(java.util.UUID u, String item, long ms) {',
    [('java.util.UUID u', 'String k'), ('EXEMPT.get(u)', 'EXEMPT.get(k)'), ('EXEMPT.putIfAbsent(u, m)', 'EXEMPT.putIfAbsent(k, m)')], SPA)
blk('public static boolean isExempt(java.util.UUID u, String item) {',
    [('java.util.UUID u', 'String k'), ('EXEMPT.get(u)', 'EXEMPT.get(k)')], SPA)
blk('public static void clearExempt(java.util.UUID u) {',
    [('java.util.UUID u', 'String k'), ('EXEMPT.remove(u)', 'EXEMPT.remove(k)')], SPA)
blk('public static java.util.Map pool(java.util.UUID u) {',
    [('java.util.UUID u', 'String k'), ('POOLS.get(u)', 'POOLS.get(k)'),
     ('DIR.resolve(u.toString() + ".properties")', 'DIR.resolve(k + ".properties")'),
     ('"could not load pool for " + u', '"could not load pool for " + k'), ('POOLS.putIfAbsent(u, m)', 'POOLS.putIfAbsent(k, m)')], SPA)
blk('public static void saveNow(java.util.UUID u) {',
    [('java.util.UUID u', 'String k'), ('POOLS.get(u)', 'POOLS.get(k)'),
     ('DIR.resolve(u.toString() + ".properties.tmp")', 'DIR.resolve(k + ".properties.tmp")'),
     ('DIR.resolve(u.toString() + ".properties")', 'DIR.resolve(k + ".properties")'),
     ('"could not save pool for " + u', '"could not save pool for " + k')], SPA)
blk('public static void save(java.util.UUID u) {',
    [('java.util.UUID u', 'String k'), ('saveNow(u)', 'saveNow(k)')], SPA)
blk('public static void flushDirty() {',
    [('java.util.UUID u = (java.util.UUID) it.next();', 'String k = (String) it.next();'), ('save(u);', 'save(k);')], SPA)
blk('public static long get(java.util.UUID u, String item) {',
    [('java.util.UUID u', 'String k'), ('pool(u)', 'pool(k)')], SPA)
blk('public static synchronized void add(java.util.UUID u, String item, long n) {',
    [('java.util.UUID u', 'String k'), ('pool(u)', 'pool(k)'), ('DIRTY.put(u, Boolean.TRUE)', 'DIRTY.put(k, Boolean.TRUE)')], SPA)
blk('public static long catTotal(java.util.UUID u, String cat) {{',
    [('java.util.UUID u', 'String k'), ('pool(u)', 'pool(k)')], SPA)

# ---------------- ProcStore: keyed by pkey, processing/<pkey>.properties ----------------
PSA = '# ProcStore = per-profile benches'
rep('# ProcStore = per-player benches, persisted in Skyy_SkyySacks/processing/<uuid>.properties (tmp + fsync + atomic move)',
    '# ProcStore = per-profile benches (0.7.2: keyed by pkey), persisted in Skyy_SkyySacks/processing/<pkey>.properties (tmp + fsync + atomic move)')
blk('public static synchronized java.util.Map load(java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'), ('STATES.get(u)', 'STATES.get(k)'),
     ('DIR.resolve(u.toString() + ".properties")', 'DIR.resolve(k + ".properties")'),
     ('BROKEN.put(u, Boolean.TRUE)', 'BROKEN.put(k, Boolean.TRUE)'),
     ('furnace/tannery disabled for " + u + " until restart', 'furnace/tannery disabled for " + k + " until restart'),
     ('STATES.put(u, m)', 'STATES.put(k, m)')], PSA)
blk('public static java.util.Map all(java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'), ('STATES.get(u)', 'STATES.get(k)'), ('load(u)', 'load(k)')], PSA)
blk('public static {PKG}.ProcBench get(java.util.UUID u, String bench) {{',
    [('java.util.UUID u', 'String k'), ('if (u == null', 'if (k == null'), ('all(u)', 'all(k)')], PSA)
blk('public static {PKG}.ProcBench of(java.util.UUID u, String bench) {{',
    [('java.util.UUID u', 'String k'), ('all(u)', 'all(k)')], PSA)
blk('public static boolean pending(java.util.UUID u, String bench) {{',
    [('java.util.UUID u', 'String k'), ('get(u, bench)', 'get(k, bench)')], PSA)
blk('public static void markDirty(java.util.UUID u) { DIRTY.put(u, Boolean.TRUE); }',
    [('java.util.UUID u', 'String k'), ('DIRTY.put(u,', 'DIRTY.put(k,')], PSA)
blk('public static synchronized boolean save(java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'), ('if (u == null', 'if (k == null'), ('BROKEN.containsKey(u)', 'BROKEN.containsKey(k)'),
     ('STATES.get(u)', 'STATES.get(k)'), ('DIRTY.remove(u)', 'DIRTY.remove(k)'),
     ('DIR.resolve(u.toString() + ".properties.tmp")', 'DIR.resolve(k + ".properties.tmp")'),
     ('DIR.resolve(u.toString() + ".properties")', 'DIR.resolve(k + ".properties")'),
     ('DIRTY.put(u, Boolean.TRUE)', 'DIRTY.put(k, Boolean.TRUE)'),
     ('"processing: could not save " + u', '"processing: could not save " + k')], PSA)
blk('public static void flushDirty() {',
    [('java.util.UUID u = (java.util.UUID) it.next();', 'String k = (String) it.next();'), ('save(u);', 'save(k);')], PSA)

# ---------------- SweepTask ----------------
SWA = '# ================= SweepTask'
blk('public static int sweep({PLA} p, java.util.UUID u, String onlyCat, boolean allContainers) {{',
    [('java.util.UUID u', 'String k'), ('isExempt(u, id)', 'isExempt(k, id)'), ('SackPool.get(u, id)', 'SackPool.get(k, id)'),
     ('SackPool.add(u, id, (long) removed)', 'SackPool.add(k, id, (long) removed)')], SWA)
blk('public static int withdraw({PLA} p, java.util.UUID u, String id, int n) {{',
    [('java.util.UUID u', 'String k'), ('SackPool.get(u, id)', 'SackPool.get(k, id)'),
     ('SackPool.add(u, id, -(long) added)', 'SackPool.add(k, id, -(long) added)'),
     ('SackPool.exempt(u, id, 600000L)', 'SackPool.exempt(k, id, 600000L)')], SWA)
rep('    sweep(p, pr.getUuid(), null, false);',
    '    String k = {PKG}.SackPool.settledKey(pr.getUuid());' + LF
    + '    if (k == null) return;' + LF
    + '    sweep(p, k, null, false);')

# ---------------- CraftLog: the pkey in every line (profile 1 = the uuid, so old lines read the same) ----------------
CLA = '# ================= CraftLog'
blk('public static synchronized void write(java.util.UUID u, String recipe,',
    [('java.util.UUID u', 'String k'), ('" " + u + " " + recipe', '" " + k + " " + recipe')], CLA)
blk('public static synchronized void line(java.util.UUID u, String text) {',
    [('java.util.UUID u', 'String k'), ('" " + u + " " + text', '" " + k + " " + text')], CLA)

# ---------------- review fix: queued log lines + SackSaver.run below CraftLog + SackPool.saveSoon ----------------
# SackSaver.run() moves below CraftLog (its constructor stays where it is) so the one off-thread saver also writes queued log lines.
rep('sav.addMethod(CtNewMethod.make(f"""' + LF + 'public void run() {{' + LF
    + '  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}' + LF
    + '  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}' + LF
    + '}}""", sav))' + LF, '')
rep('# CraftPage fields + constructor first (SacksPage references it)',
    LF.join([
        '# 0.7.2 review fix: log lines from world-thread hot paths (a profile switch, a retired or parked bench mirror) are queued here',
        '# (timestamped when queued) and written by the SackSaver on the scheduler thread - no file append inside a world-thread task.',
        'clog.addField(CtField.make("public static final java.util.concurrent.ConcurrentLinkedQueue PENDING = new java.util.concurrent.ConcurrentLinkedQueue();", clog))',
        'clog.addMethod(CtNewMethod.make("""',
        'public static void later(String k, String text) {',
        '  PENDING.offer(new java.util.Date().toString() + " " + k + " " + text + System.lineSeparator());',
        '}""", clog))',
        'clog.addMethod(CtNewMethod.make("""',
        'public static synchronized void drain() {',
        '  try {',
        '    Object o = PENDING.poll();',
        '    if (o == null) return;',
        '    StringBuilder sb = new StringBuilder();',
        '    while (o != null) { sb.append((String) o); o = PENDING.poll(); }',
        '    if (FILE == null) return;',
        '    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);',
        '    java.nio.file.Files.write(FILE, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });',
        '  } catch (Throwable t) { }',
        '}""", clog))',
        '# SackSaver.run() (constructor added above): processing files, pool files, then the queued log lines - all on the scheduler thread.',
        'sav.addMethod(CtNewMethod.make(f"""',
        'public void run() {{',
        '  try {{ {PKG}.ProcStore.flushDirty(); }} catch (Throwable t) {{ }}',
        '  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}',
        '  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}',
        '}}""", sav))',
        '# 0.7.2 review fix: pool saves from world-thread code (Sacks page clicks, bench link, instant craft, mirror retire/park) mark the',
        '# key dirty and run the SackSaver on the scheduler thread right away (same pattern as CraftPage.saveSoon for processing); only',
        '# when the scheduler refuses the task (server shutting down) is it run inline.',
        'sp.addMethod(CtNewMethod.make(f"""',
        'public static void saveSoon(String k) {{',
        '  if (k != null) DIRTY.put(k, Boolean.TRUE);',
        '  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }}',
        '  catch (Throwable t) {{ new {PKG}.SackSaver().run(); }}',
        '}}""", sp))',
        '',
        '# CraftPage fields + constructor first (SacksPage references it)',
    ]))
rep('  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}' + LF + '  super.shutdown();',
    '  try {{ {PKG}.SackPool.flushDirty(); }} catch (Throwable t) {{ }}' + LF
    + '  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}' + LF + '  super.shutdown();')

# ---------------- page fields (key = the pkey the page was last built for) ----------------
rep('cpg.addField(CtField.make("public String[] fuelIds;", cpg))',
    'cpg.addField(CtField.make("public String[] fuelIds;", cpg))' + LF
    + 'cpg.addField(CtField.make("public String key;", cpg))' + LF
    + 'cpg.addField(CtField.make("public String noticeKey;", cpg))' + LF
    + 'cpg.addField(CtField.make("public boolean settling;", cpg))')
rep('page.addField(CtField.make("public String info;", page))',
    'page.addField(CtField.make("public String info;", page))' + LF
    + 'page.addField(CtField.make("public String key;", page))' + LF
    + 'page.addField(CtField.make("public String noticeKey;", page))')

# ---------------- SacksPage ----------------
SPG = '# ================= SacksPage'
blk('public String pickCat(java.util.UUID u, java.util.HashMap caps) {{',
    [('java.util.UUID u', 'String k'), ('catTotal(u, cats[c])', 'catTotal(k, cats[c])')], SPG)
blk('public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{',
    [('  java.util.UUID u = this.playerRef.getUuid();' + LF,
      '  java.util.UUID u = this.playerRef.getUuid();' + LF + '  String k = {PKG}.SackPool.pkey(u);' + LF + '  this.key = null;' + LF),
     ('this.cat = pickCat(u, caps);', 'this.cat = pickCat(k, caps);'),
     ('  Integer capObj = (Integer) caps.get(this.cat);', '  this.key = k;' + LF + '  Integer capObj = (Integer) caps.get(this.cat);'),
     ('SackPool.catTotal(u, this.cat)', 'SackPool.catTotal(k, this.cat)'),
     ('SackPool.pool(u).entrySet()', 'SackPool.pool(k).entrySet()')], SPG)
blk('public void handleDataEvent({REF} ref, {ST} st, String data) {{',
    [('    if (player == null) return;' + LF + '    for (int i = 0; i < 36; i++) {{' + LF,
      '    if (player == null) return;' + LF
      + '    String k = {PKG}.SackPool.settledKey(u);' + LF
      + '    if (k == null) {{ this.info = "bags paused (profile loading or switching) - try again in a moment"; rebuild(); return; }}' + LF
      + '    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; rebuild(); return; }}' + LF
      + '    for (int i = 0; i < 36; i++) {{' + LF),
     ('SweepTask.withdraw(player, u, this.cells[i], n)', 'SweepTask.withdraw(player, k, this.cells[i], n)'),
     ('SweepTask.withdraw(player, u, this.cells[i], 64)', 'SweepTask.withdraw(player, k, this.cells[i], 64)'),
     ('SackPool.save(u);', 'SackPool.saveSoon(k);'),
     ('SackPool.clearExempt(u);', 'SackPool.clearExempt(k);'),
     ('SweepTask.sweep(player, u, this.cat, true)', 'SweepTask.sweep(player, k, this.cat, true)')], SPG)
rep('# ================= SacksCmd =================',
    LF.join([
        '# 0.7.2: the active profile changed while this page is open (ProcTask, world thread). set() only on a label the last build',
        '# created (same pattern as CraftPage.live - no re-append from a tick); the next click rebuilds for the new profile.',
        'page.addMethod(CtNewMethod.make(f"""',
        'public void profileNotice(String k) {{',
        '  if (this.key == null || k == null || k.equals(this.noticeKey)) return;',
        '  this.noticeKey = k;',
        '  {UCB} c = new {UCB}();',
        '  c.set("#SkyySInfo.Text", "Your profile changed - click a tab to refresh this page");',
        '  sendUpdate(c, false);',
        '}}""", page))',
        '',
        '# ================= SacksCmd =================',
    ]))

# ---------------- BagMirror: keyed by pkey, remembers its key ----------------
BMA = '# ================= BagMirror'
rep('mir.addField(CtField.make("public String sig;", mir))',
    'mir.addField(CtField.make("public String sig;", mir))' + LF
    + 'mir.addField(CtField.make("public String key;", mir))' + LF
    + 'mir.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTKEY = new java.util.concurrent.ConcurrentHashMap();", mir))')
blk('public BagMirror() {{', [('public BagMirror() {{', 'public BagMirror(String key) {{' + LF + '  this.key = key;')], BMA)
blk('public static {PKG}.BagMirror of(java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'), ('MIRRORS.get(u)', 'MIRRORS.get(k)'), ('new {PKG}.BagMirror()', 'new {PKG}.BagMirror(k)'),
     ('MIRRORS.putIfAbsent(u, m)', 'MIRRORS.putIfAbsent(k, m)')], BMA)
blk('public int sync(java.util.UUID u) {{',
    [('public int sync(java.util.UUID u) {{', 'public int sync() {{'),
     ('SackPool.add(u, this.slotIds[i]', 'SackPool.add(this.key, this.slotIds[i]')], BMA)
blk('public String rebuild(java.util.UUID u, java.util.HashMap caps) {{',
    [('java.util.UUID u, java.util.HashMap caps', 'java.util.HashMap caps'),
     ('SackPool.pool(u).entrySet()', 'SackPool.pool(this.key).entrySet()')], BMA)
rep('mir.addMethod(CtNewMethod.make(f"""' + LF + 'public {IQ}[] quantities() {{',
    LF.join([
        '# 0.7.2: a bench mirror belongs to ONE profile key. When the active key changes, the old mirror is synced into its own pool',
        '# (what a bench took before the switch), saved and dropped; CraftLinkTask swaps it out of any open bench window in the same run.',
        'mir.addMethod(CtNewMethod.make(f"""',
        'public static {PKG}.BagMirror retireOther(java.util.UUID u, String k) {{',
        '  String old = (String) LASTKEY.put(u, k);',
        '  if (old == null || old.equals(k)) return null;',
        '  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.remove(old);',
        '  if (m == null) return null;',
        '  int c = m.sync();',
        '  {PKG}.CraftLog.later(old, "PROFILE bench mirror retired - active key now " + k + " consumed=" + c);',
        '  {PKG}.SackPool.saveSoon(old);',
        '  return m;',
        '}}""", mir))',
        '# 0.7.2 review fix: drop everything the mirror offers (call sync() first - it accounts what the bench already took).',
        'mir.addMethod(CtNewMethod.make(f"""',
        'public void empty() {{',
        '  try {{ this.cont.clear(); }} catch (Throwable t) {{ }}',
        '  for (int i = 0; i < 36; i++) {{ this.slotIds[i] = null; this.slotQty[i] = 0; }}',
        '  this.sig = "";',
        '}}""", mir))',
        'mir.addMethod(CtNewMethod.make("""',
        'public boolean holds() {',
        '  for (int i = 0; i < 36; i++) if (this.slotIds[i] != null) return true;',
        '  return false;',
        '}""", mir))',
        '# 0.7.2 review fix (settle window): while SackPool.settledKey(u) is null CraftLinkTask calls only this. The player\'s last bench',
        '# mirror (LASTKEY) is synced into its OWN pool; if it still offers anything it is emptied, and every open bench it is attached to',
        '# gets setValid(false), which makes BenchWindow.getExtraResourcesSection() re-feed the vanilla nearby-chest resources',
        '# (CraftingManager.feedExtraResourcesSection; every MaterialContainerWindow is a BenchWindow); if no re-feed happened the emptied',
        '# mirror stays attached with no extra materials. An emptied mirror returns right away on the next 300ms runs (no repeat updates).',
        '# No key is fed and no mirror is rebuilt until the switch settles, so a bench cannot use bag items across profiles.',
        'mir.addMethod(CtNewMethod.make(f"""',
        'public static int park({WM} wm, java.util.List wins, java.util.UUID u) {{',
        '  String lk = (String) LASTKEY.get(u);',
        '  if (lk == null) return 0;',
        '  {PKG}.BagMirror m = ({PKG}.BagMirror) MIRRORS.get(lk);',
        '  if (m == null) return 0;',
        '  int consumed = m.sync();',
        '  if (consumed > 0) {PKG}.SackPool.saveSoon(lk);',
        '  if (!m.holds()) return consumed;',
        '  m.empty();',
        '  int parked = 0;',
        '  for (int i = 0; wins != null && i < wins.size(); i++) {{',
        '    Object w = wins.get(i);',
        '    if (!(w instanceof {MCW})) continue;',
        '    {MERS} sec = (({MCW}) w).getExtraResourcesSection();',
        '    if (sec == null) continue;',
        '    {IC} existing = sec.getItemContainer();',
        '    if (existing == null || (existing != m.combined && existing != m.cont)) continue;',
        '    parked++;',
        '    sec.setValid(false);',
        '    sec = (({MCW}) w).getExtraResourcesSection();',
        '    if (sec != null && !sec.isValid()) {{ sec.setExtraMaterials(new {IQ}[0]); sec.setValid(true); }}',
        '    if (wm != null) {{',
        '      try {{ wm.updateWindow(({WIN}) w); }} catch (Throwable t) {{ {PKG}.SackPool.warn("craft link: park updateWindow failed: " + t); }}',
        '    }}',
        '  }}',
        '  if (parked > 0) {{',
        '    {PKG}.SackPool.warn("craft link: profile switch settling - bag materials taken off " + parked + " open bench window(s) (key " + lk + ", consumed=" + consumed + ")");',
        '    {PKG}.CraftLog.later(lk, "PROFILE switch settling - bag materials taken off " + parked + " open bench window(s) consumed=" + consumed);',
        '  }}',
        '  return consumed;',
        '}}""", mir))',
        'mir.addMethod(CtNewMethod.make(f"""',
        'public {IQ}[] quantities() {{',
    ]))

# ---------------- CraftLinkTask ----------------
CLT = '# ================= CraftLinkTask'
rep('# ================= CraftLinkTask (world thread, every 300ms per player) =================',
    '# ================= CraftLinkTask (world thread, every 300ms per player) =================' + LF
    + '# 0.7.2 review fix: the key comes from SackPool.settledKey. While a profile switch settles (null) the task only parks the mirror' + LF
    + '# (BagMirror.park) and returns: no retireOther, no rebuild, nothing fed to the bench for ANY key until the switch has settled.')
blk('public void run() {{',
    [('    java.util.UUID u = pr.getUuid();' + LF + '    {WM} wm = p.getWindowManager();',
      '    java.util.UUID u = pr.getUuid();' + LF
      + '    String k = {PKG}.SackPool.settledKey(u);' + LF
      + '    if (k == null) {{' + LF
      + '      {WM} wm0 = p.getWindowManager();' + LF
      + '      java.util.List wins0 = null;' + LF
      + '      if (wm0 != null) wins0 = wm0.getWindows();' + LF
      + '      {PKG}.BagMirror.park(wm0, wins0, u);' + LF
      + '      return;' + LF
      + '    }}' + LF
      + '    {PKG}.BagMirror stale = {PKG}.BagMirror.retireOther(u, k);' + LF
      + '    {WM} wm = p.getWindowManager();'),
     ('{PKG}.BagMirror m = {PKG}.BagMirror.of(u);' + LF + '      int consumed = m.sync(u);',
      '{PKG}.BagMirror m = {PKG}.BagMirror.of(k);' + LF + '      int consumed = m.sync();'),
     ('String sig = m.rebuild(u, caps);', 'String sig = m.rebuild(caps);'),
     ('      {IC} existing = sec.getItemContainer();' + LF,
      '      {IC} existing = sec.getItemContainer();' + LF
      + '      if (stale != null && existing != null && (existing == stale.combined || existing == stale.cont)) existing = ({IC}) stale.vanilla;' + LF),
     ('      if (consumed > 0) {PKG}.SackPool.save(u);', '      if (consumed > 0) {PKG}.SackPool.saveSoon(k);'),
     ('{PKG}.BagMirror.MIRRORS.get(u);' + LF
      + '      if (m != null) {{ int c = m.sync(u); if (c > 0) {PKG}.SackPool.save(u); {PKG}.BagMirror.MIRRORS.remove(u); }}',
      '{PKG}.BagMirror.MIRRORS.get(k);' + LF
      + '      if (m != null) {{ int c = m.sync(); if (c > 0) {PKG}.SackPool.saveSoon(k); {PKG}.BagMirror.MIRRORS.remove(k); }}')], CLT)

# ---------------- CraftPage ----------------
CPA = '# ================= CraftPage (inventory crafting v1'
blk('public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{',
    [('buildTabs({PLA} p, java.util.UUID u)', 'buildTabs({PLA} p, java.util.UUID u, String k)'),
     ('ProcStore.pending(u, bn)', 'ProcStore.pending(k, bn)')], CPA)
blk('public static {CIC} materials({PLA} p, java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'),
     ('BagMirror.of(u);' + LF + '  m.sync(u);' + LF + '  m.rebuild(u, ', 'BagMirror.of(k);' + LF + '  m.sync();' + LF + '  m.rebuild(')], CPA)
# review fix: the page view never builds a BagMirror for an unsettled key (build() sets this.settling from SackPool.settledKey)
rep('cpg.addMethod(CtNewMethod.make(f"""' + LF + 'public static int limit({CRR} r, {IC} c) {{',
    LF.join([
        '# 0.7.2 review fix: counts for the page VIEW. While a profile switch settles (this.settling, set by build() from',
        '# SackPool.settledKey) only the inventory is counted and no BagMirror is built or synced for the not-yet-settled key; every',
        '# click that moves items calls materials(p, k) itself with the one settled key it checked.',
        'cpg.addMethod(CtNewMethod.make(f"""',
        'public {CIC} viewMats({PLA} p, String k) {{',
        '  if (this.settling) return new {CIC}(new {IC}[] {{ p.getInventory().getCombinedBackpackStorageHotbar() }});',
        '  return materials(p, k);',
        '}}""", cpg))',
        'cpg.addMethod(CtNewMethod.make(f"""',
        'public static int limit({CRR} r, {IC} c) {{',
    ]))
blk('public static void saveSoon(java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'), ('markDirty(u)', 'markDirty(k)')], CPA)
PROC_COMMON = [('java.util.UUID u', 'String k'), ('BROKEN.containsKey(u)', 'BROKEN.containsKey(k)'),
               ('ProcStore.of(u, bench)', 'ProcStore.of(k, bench)'), ('materials(p, u)', 'materials(p, k)'),
               ('BagMirror.of(u);' + LF + '  int consumed = m.sync(u);', 'BagMirror.of(k);' + LF + '  int consumed = m.sync();'),
               ('saveSoon(u);', 'saveSoon(k);'), ('CraftLog.line(u, ', 'CraftLog.line(k, ')]
blk('public static String procQueue({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench, int tier,', PROC_COMMON, CPA)
blk('public static String procFuel({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench, String id) {{', PROC_COMMON, CPA)
blk('public static String procCollect({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench) {{',
    [('java.util.UUID u', 'String k'), ('ProcStore.get(u, bench)', 'ProcStore.get(k, bench)'), ('markDirty(u)', 'markDirty(k)'),
     ('saveSoon(u);', 'saveSoon(k);'), ('CraftLog.line(u, ', 'CraftLog.line(k, ')], CPA)
for name in ("procCancel", "procUnload"):
    blk('public static String %s({PLA} p, {ST} st, {REF} ref, java.util.UUID u, String bench) {{' % name,
        [('java.util.UUID u', 'String k'), ('ProcStore.get(u, bench)', 'ProcStore.get(k, bench)'), ('saveSoon(u);', 'saveSoon(k);'),
         ('CraftLog.line(u, ', 'CraftLog.line(k, '), ('procCollect(p, st, ref, u, bench)', 'procCollect(p, st, ref, k, bench)')], CPA)
blk('public void buildProc({UCB} b, {UEB} ev, {PLA} p, java.util.UUID u) {{',
    [('buildProc({UCB} b, {UEB} ev, {PLA} p, java.util.UUID u)', 'buildProc({UCB} b, {UEB} ev, {PLA} p, java.util.UUID u, String k)'),
     ('BROKEN.containsKey(u)', 'BROKEN.containsKey(k)'), ('ProcStore.get(u, bench)', 'ProcStore.get(k, bench)'),
     ('markDirty(u)', 'markDirty(k)'), ('materials(p, u)', 'viewMats(p, k)')], CPA)
blk('public void live({REF} ref, {ST} st) {{',
    [('  java.util.UUID u = this.playerRef.getUuid();' + LF + '  String bench = this.tab.substring(2);' + LF
      + '  {PKG}.ProcBench pb = {PKG}.ProcStore.get(u, bench);',
      '  java.util.UUID u = this.playerRef.getUuid();' + LF
      + '  String k = {PKG}.SackPool.pkey(u);' + LF
      + '  if (this.key == null || !this.key.equals(k)) return;' + LF
      + '  String bench = this.tab.substring(2);' + LF
      + '  {PKG}.ProcBench pb = {PKG}.ProcStore.get(k, bench);')], CPA)
blk('public boolean handleProc({REF} ref, {ST} st, {PLA} p, java.util.UUID u, String data) {{',
    [('java.util.UUID u, String data', 'java.util.UUID u, String k, String data'),
     ('procCollect(p, st, ref, u, bench)', 'procCollect(p, st, ref, k, bench)'),
     ('procCancel(p, st, ref, u, bench)', 'procCancel(p, st, ref, k, bench)'),
     ('procUnload(p, st, ref, u, bench)', 'procUnload(p, st, ref, k, bench)'),
     ('procFuel(p, st, ref, u, bench, ', 'procFuel(p, st, ref, k, bench, '),
     ('procQueue(p, st, ref, u, bench, tier', 'procQueue(p, st, ref, k, bench, tier')], CPA)
HPA = 'public boolean handleProc({REF} ref'
blk('public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{',
    [('  this.liveOn = false;' + LF + '  if (p == null) return;' + LF + '  this.tabs = buildTabs(p, u);',
      '  this.liveOn = false;' + LF + '  this.key = null;' + LF + '  this.settling = false;' + LF + '  if (p == null) return;' + LF
      + '  String k = {PKG}.SackPool.settledKey(u);' + LF
      + '  if (k == null) {{' + LF
      + '    this.settling = true;' + LF
      + '    k = {PKG}.SackPool.pkey(u);' + LF
      + '    if (this.info == null || this.info.length() == 0) this.info = "bags paused (profile loading or switching) - bag counts come back in a moment";' + LF
      + '  }} else if (this.info != null && this.info.startsWith("bags paused")) this.info = "";' + LF
      + '  this.key = k;' + LF + '  this.tabs = buildTabs(p, u, k);'),
     ('buildProc(b, ev, p, u); return;', 'buildProc(b, ev, p, u, k); return;'),
     ('{CIC} mats = materials(p, u);', '{CIC} mats = viewMats(p, k);')], HPA)
blk('public void handleDataEvent({REF} ref, {ST} st, String data) {{',
    [('    if (handleProc(ref, st, p, u, data)) return;',
      '    String k = {PKG}.SackPool.settledKey(u);' + LF
      + '    if (k == null) {{ this.info = "bags paused (profile loading or switching) - try again in a moment"; rebuild(); return; }}' + LF
      + '    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; this.pageNo = 0; rebuild(); return; }}' + LF
      + '    if (handleProc(ref, st, p, u, k, data)) return;'),
     ('{CIC} mats = materials(p, u);', '{CIC} mats = materials(p, k);'),
     ('{PKG}.BagMirror m = {PKG}.BagMirror.of(u);' + LF + '    int consumed = m.sync(u);' + LF + '    if (consumed > 0) {PKG}.SackPool.save(u);',
      '{PKG}.BagMirror m = {PKG}.BagMirror.of(k);' + LF + '    int consumed = m.sync();' + LF + '    if (consumed > 0) {PKG}.SackPool.saveSoon(k);'),
     ('CraftLog.write(u, ', 'CraftLog.write(k, ')], HPA)
rep('# ================= CraftCmd (/craft) =================',
    LF.join([
        '# 0.7.2: the active profile changed while the craft page is open (ProcTask, world thread): set() only, live() stops for the',
        '# old key (it checks this.key); the next click rebuilds the page for the new profile.',
        'cpg.addMethod(CtNewMethod.make(f"""',
        'public void profileNotice(String k) {{',
        '  if (this.key == null || k == null || k.equals(this.noticeKey)) return;',
        '  this.noticeKey = k;',
        '  {UCB} c = new {UCB}();',
        '  c.set("#SkyyCInfo.Text", "Your profile changed - click a tab to refresh this page");',
        '  sendUpdate(c, false);',
        '}}""", cpg))',
        '',
        '# ================= CraftCmd (/craft) =================',
    ]))

# ---------------- ProcTask: epoch check (contract rule 3) + per-key processing ----------------
PTA = '# ================= ProcTask'
rep('ptk.addField(CtField.make("public static long LASTWARN;", ptk))',
    'ptk.addField(CtField.make("public static long LASTWARN;", ptk))' + LF
    + 'ptk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", ptk))')
rep('ptk.addConstructor(CtNewConstructor.make(f"public ProcTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", ptk))',
    LF.join([
        'ptk.addConstructor(CtNewConstructor.make(f"public ProcTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", ptk))',
        '# 0.7.2 profile contract rule 3: remember the last profile:epoch:<uuid> seen per player. SkyySacks publishes no per-player bridge',
        '# values, so "republish" = flush every dirty pool/processing file (the old profile\'s included) off the world thread right away and',
        '# log the switch; an open page built for another key is told in run(). Without SkyyProfiles the epoch stays absent: never fires.',
        '# Integration fix: an absent epoch (-1) is not remembered, so the first published value is a baseline (contract 4.2), not a change.',
        '# Review fix: the log line is queued (CraftLog.later) BEFORE the SackSaver is scheduled, which writes it off the world thread.',
        'ptk.addMethod(CtNewMethod.make(f"""',
        'public static boolean epochCheck(java.util.UUID u, String k) {{',
        '  long ep = {PKG}.SackPool.epoch(u);',
        '  if (ep < 0L) return false;',
        '  Long last = (Long) EPOCH.put(u, Long.valueOf(ep));',
        '  if (last == null || last.longValue() == ep) return false;',
        '  {PKG}.CraftLog.later(k, "PROFILE epoch " + last + " -> " + ep + " - bags, furnace and tannery now use this key");',
        '  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }} catch (Throwable t) {{ }}',
        '  return true;',
        '}}""", ptk))',
    ]))
blk('public void run() {{',
    [('    java.util.UUID u = pr.getUuid();' + LF
      + '    if ({PKG}.ProcStore.BROKEN.containsKey(u)) return;' + LF
      + '    java.util.Map m = {PKG}.ProcStore.all(u);' + LF
      + '    if (m.isEmpty()) return;' + LF
      + '    long now = System.currentTimeMillis();' + LF
      + '    java.util.Iterator it = m.values().iterator();',
      '    java.util.UUID u = pr.getUuid();' + LF
      + '    String k = {PKG}.SackPool.pkey(u);' + LF
      + '    epochCheck(u, k);' + LF
      + '    java.util.Map m = null;' + LF
      + '    if (!{PKG}.ProcStore.BROKEN.containsKey(k)) m = {PKG}.ProcStore.all(k);' + LF
      + '    long now = System.currentTimeMillis();' + LF
      + '    java.util.Iterator it = m == null ? java.util.Collections.EMPTY_LIST.iterator() : m.values().iterator();'),
     ('ProcStore.markDirty(u);', 'ProcStore.markDirty(k);'),
     ('CraftLog.line(u, "DONE "', 'CraftLog.line(k, "DONE "'),
     ('    if (pg instanceof {PKG}.CraftPage) (({PKG}.CraftPage) pg).live(r, st);',
      '    if (pg instanceof {PKG}.CraftPage) {{' + LF
      + '      {PKG}.CraftPage cp = ({PKG}.CraftPage) pg;' + LF
      + '      if (cp.key != null && !cp.key.equals(k)) cp.profileNotice(k); else cp.live(r, st);' + LF
      + '    }} else if (pg instanceof {PKG}.SacksPage) {{' + LF
      + '      {PKG}.SacksPage sk = ({PKG}.SacksPage) pg;' + LF
      + '      if (sk.key != null && !sk.key.equals(k)) sk.profileNotice(k);' + LF
      + '    }}')], PTA)

# ---------------- plugin: data folder comment + ready line ----------------
rep('  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - /pd, /craft (Crafting, Alchemy, timed Furnace/Tannery queues), right-click a magic bag; workbenches craft from your bags");',
    '  getLogger().at(java.util.logging.Level.INFO).log("[SkyySacks] {VERSION} ready - /pd, /craft (Crafting, Alchemy, timed Furnace/Tannery queues), right-click a magic bag; workbenches craft from your bags; storage per profile (pkey)");')

# ---------------- integration fixes (pinned SkyyProfiles 0.1 semantics; notes in the docstring above) ----------------
# pool(k): a failed read is NOT cached (it used to cache an empty pool that the next save wrote over the real file)
blk('public static java.util.Map pool(String k) {',
    [('  } catch (Throwable t) { warn("could not load pool for " + k + ": " + t); }' + LF,
      '  } catch (Throwable t) {' + LF
      + '    java.util.Map again = (java.util.Map) POOLS.get(k);' + LF
      + '    if (again != null) return again;' + LF
      + '    if (BADPOOL.put(k, Long.valueOf(System.currentTimeMillis())) == null) warn("could not load pool for " + k + " - file left untouched, item moves for this profile paused until it reads (retry every 2s): " + t);' + LF
      + '    return m;' + LF
      + '  }' + LF
      + '  if (BADPOOL.remove(k) != null) warn("pool for " + k + " reads again - item moves resumed");' + LF)], SPA)
# a failed pool write stays dirty (retried by the next SackSaver run) instead of waiting for the next add
blk('public static void saveNow(String k) {',
    [('  } catch (Throwable t) { warn("could not save pool for " + k + ": " + t); }',
      '  } catch (Throwable t) { DIRTY.put(k, Boolean.TRUE); warn("could not save pool for " + k + " (kept dirty - retried by the next save): " + t); }')], SPA)
# flushDirty iterates a snapshot (a failed save re-marks its key; re-inserting while iterating the live key set could revisit it)
blk('public static void flushDirty() {',
    [('  java.util.Iterator it = DIRTY.keySet().iterator();' + LF
      + '  while (it.hasNext()) {' + LF
      + '    String k = (String) it.next();' + LF
      + '    it.remove();' + LF
      + '    save(k);' + LF
      + '  }',
      '  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());' + LF
      + '  for (int i = 0; i < ks.size(); i++) {' + LF
      + '    String k = (String) ks.get(i);' + LF
      + '    DIRTY.remove(k);' + LF
      + '    save(k);' + LF
      + '  }')], SPA)
blk('public static void flushDirty() {',
    [('  java.util.Iterator it = DIRTY.keySet().iterator();' + LF
      + '  while (it.hasNext()) {' + LF
      + '    String k = (String) it.next();' + LF
      + '    save(k);' + LF
      + '  }',
      '  java.util.ArrayList ks = new java.util.ArrayList(DIRTY.keySet());' + LF
      + '  for (int i = 0; i < ks.size(); i++) save((String) ks.get(i));')], PSA)
# ready(k) + settledKey(u), below pool() (javassist: callee before caller). settledKey is the gate of every item move.
rep('# ================= Processing (0.7.0)',
    LF.join([
        '# integration fix: true when the pool of key k is loaded (or its file does not exist yet). A pool whose file could not be read is',
        '# retried at most every 2 s; until it reads, settledKey pauses every item move for that key (nothing can be written over the file).',
        'sp.addMethod(CtNewMethod.make("""',
        'public static boolean ready(String k) {',
        '  if (k == null) return false;',
        '  if (POOLS.containsKey(k)) return true;',
        '  Long bad = (Long) BADPOOL.get(k);',
        '  if (bad != null && System.currentTimeMillis() - bad.longValue() < 2000L) return false;',
        '  pool(k);',
        '  return POOLS.containsKey(k);',
        '}""", sp))',
        '# The ONE gate of every item move between the live inventory and a pool (sweep, Sacks page clicks, craft/processing clicks, bench',
        '# link): the active key, or null = paused (sweep skips, clicks are refused, the bench mirror is parked). Paused while:',
        '#  - SkyyProfiles is installed (profile:fn:key) but published no profile:epoch:<uuid> for this player: unreadable players file with no',
        '#    good copy, where the Function falls back to profile 1 while the live inventory may be profile N (contract 4.4 / 5);',
        '#  - SETTLE_MS after the epoch or the key changed (baseline = first value seen; absent epochs are no change, contract 4.2) - the other',
        '#    mods republish acc:has / coll:recipes for the new profile in that time;',
        '#  - profile:busy:<uuid> is present (contract 4.5): a crash recovery is pending at join and will reload the inventory from a snapshot,',
        '#    so a sweep before it would duplicate items (a switch sets it too, but inside one world-thread task we never run in);',
        '#  - the pool file of the key cannot be read (ready).',
        '# Without SkyyProfiles: no epoch, no busy flag, key = uuid - only the pool-file check applies.',
        'sp.addMethod(CtNewMethod.make("""',
        'public static String settledKey(java.util.UUID u) {',
        '  if (u == null) return null;',
        '  java.util.Map b = bridge();',
        '  long e = epoch(u);',
        '  String k = pkey(u);',
        '  if (e < 0L && (b.get("profile:fn:key") instanceof java.util.function.Function)) {',
        '    if (UNKNOWN.putIfAbsent(u, Boolean.TRUE) == null) warn("SkyyProfiles is installed but published no profile:epoch for " + u + " (unreadable players file, or SkyyProfiles failed to start) - bag item moves paused for this player until it does");',
        '    return null;',
        '  }',
        '  if (UNKNOWN.remove(u) != null) warn("profile state of " + u + " is known again - bag item moves resumed");',
        '  Long le = (Long) SEENEPOCH.put(u, Long.valueOf(e));',
        '  String lk = (String) SEENKEY.put(u, k);',
        '  long now = System.currentTimeMillis();',
        '  boolean moved = le != null && le.longValue() >= 0L && e >= 0L && le.longValue() != e;',
        '  if (moved || (lk != null && !lk.equals(k))) CHANGEDAT.put(u, Long.valueOf(now));',
        '  Long t = (Long) CHANGEDAT.get(u);',
        '  if (t != null) {',
        '    if (now - t.longValue() < SETTLE_MS) return null;',
        '    CHANGEDAT.remove(u);',
        '  }',
        '  if (b.get("profile:busy:" + u.toString()) != null) return null;',
        '  if (!ready(k)) return null;',
        '  return k;',
        '}""", sp))',
        '',
        '# ================= Processing (0.7.0)']))
# shutdown: every bench mirror is synced into its own pool first (bench crafts from bag items since the last 300 ms link run - or
# since the player disconnected at an open bench - were never debited), then the files are flushed.
rep('  return out;' + LF + '}}""", mir))' + LF,
    '  return out;' + LF + '}}""", mir))' + LF + LF.join([
        'mir.addMethod(CtNewMethod.make(f"""',
        'public static int syncAll() {{',
        '  int n = 0;',
        '  java.util.Iterator it = MIRRORS.values().iterator();',
        '  while (it.hasNext()) {{',
        '    try {{ n += (({PKG}.BagMirror) it.next()).sync(); }} catch (Throwable t) {{ }}',
        '  }}',
        '  return n;',
        '}}""", mir))',
    ]) + LF)
rep('  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}' + LF,
    '  try {{ if (this.procTicker != null) this.procTicker.cancel(false); }} catch (Throwable t) {{ }}' + LF
    + '  try {{ int c = {PKG}.BagMirror.syncAll(); if (c > 0) {PKG}.SackPool.warn("shutdown: " + c + " bag items used by open benches debited"); }} catch (Throwable t) {{ }}' + LF)

# every storage call must now take the pkey - fail the derivation if a UUID-keyed call survived
for bad in ("SackPool.save(u)", "SackPool.pool(u)", "SackPool.get(u,", "SackPool.add(u,", "SackPool.catTotal(u,", "ProcStore.get(u,",
            "ProcStore.of(u,", "ProcStore.all(u)", "ProcStore.markDirty(u)", "ProcStore.BROKEN.containsKey(u)", "BagMirror.of(u)",
            "BagMirror.MIRRORS.get(u)", "CraftLog.line(u,", "CraftLog.write(u,", "m.sync(u)", "saveSoon(u)", "materials(p, u)"):
    assert bad not in s, "UUID-keyed storage call left: " + bad
# review fixes: no blocking pool save from world-thread code, the bench link uses the settle window, no inline PROFILE log line
assert "SackPool.save(" not in s, "blocking SackPool.save( call left (use SackPool.saveSoon)"
assert "CraftLog.line(k, \"PROFILE" not in s and "CraftLog.line(old," not in s, "PROFILE log line still written inline"
assert s.count("{PKG}.SackPool.pkey(u);") == 4, "unexpected pkey() call sites: %d" % s.count("{PKG}.SackPool.pkey(u);")
assert "    String k = {PKG}.SackPool.settledKey(u);" + LF + "    if (k == null) {{" + LF + "      {WM} wm0" in s, "CraftLinkTask not on settledKey"
assert s.index("public static void saveSoon(String k) {{" + LF + "  if (k != null)") > s.index("sav.addConstructor("), "saveSoon before SackSaver ctor"
# integration fixes: settledKey (the item-move gate) is defined once, below pool(), and honours busy / unknown state / unreadable pools
assert s.count("public static String settledKey(java.util.UUID u) {") == 1, "settledKey defined more than once"
assert s.index("public static String settledKey(java.util.UUID u) {") > s.index("public static boolean ready(String k) {") > s.index("public static java.util.Map pool(String k) {"), "settledKey/ready before pool"
assert 'b.get("profile:busy:" + u.toString()) != null) return null;' in s, "settledKey ignores profile:busy"
assert "if (!ready(k)) return null;" in s and "SETTLE_MS = 6000L" in s and "return -1L;" in s, "integration fixes missing"
assert "switching profiles" not in s, "old pause message left"

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
