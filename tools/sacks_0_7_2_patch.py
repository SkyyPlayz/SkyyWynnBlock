"""Derive SkyySacks/build_skyysacks_0.7.2.py from 0.7.1.
0.7.2: per-profile storage (tools/PROFILES-CONTRACT.md).
 - SackPool gets the contract's bridge()/pkey() helper (verbatim), epoch(uuid) and settledKey(uuid).
 - Rule 1: pools/<pkey>.properties and processing/<pkey>.properties; crafts.log lines carry the pkey instead of the uuid.
 - Rule 2: SackPool.POOLS/DIRTY/EXEMPT, ProcStore.STATES/DIRTY/BROKEN and BagMirror.MIRRORS are keyed by the pkey String.
   A BagMirror remembers the key it was built from, so bench consumption is always deducted from the pool it mirrors; when the
   active key changes, CraftLinkTask retires the old mirror (sync into its own pool, save, drop) and swaps it out of any open
   bench window in the same world-thread run.
 - Every sweep / page / bench / processing path resolves the pkey ONCE per run or click and passes it down.
 - Settle window: for 3 s after the epoch or the key changes, the sweep skips and page item moves are refused (guards a
   non-atomic inventory swap in SkyyProfiles); a page built for another key refuses the click and rebuilds for the new profile.
 - Rule 3: SkyySacks publishes no per-player bridge values; ProcTask (existing 1 s tick) remembers profile:epoch:<uuid> per
   player - on a change it flushes every dirty file off the world thread and logs the switch; an open Sacks/Craft page built
   for another key gets a set()-only "profile changed" notice (the proven live() pattern; the rebuild happens on the next click).
 - Rules 4-6: nothing applied to the live player; vanilla inventory never touched; the Craftable-only toggle stays per player.
Without SkyyProfiles pkey = uuid.toString() = profile 1 and the epoch stays 0: same files, same log lines, same behaviour.
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
    + 'the pkey once per run (a bench mirror keeps its key and is retired into its own pool on a switch); 3s settle window after a switch' + LF
    + '(no sweep, page item moves refused); ProcTask checks profile:epoch:<uuid> every second (flush saves, log, notice on an open page).' + LF
    + 'Derived by tools/sacks_0_7_2_patch.py. Without SkyyProfiles pkey = uuid = profile 1: same files, same behaviour.' + LF + '"""')
rep('VERSION = "0.7.1"', 'VERSION = "0.7.2"')

# ---------------- SackPool: contract helper, epoch, settle window ----------------
rep('sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))' + LF,
    'sp.addField(CtField.make("public static final Object SAVELOCK = new Object();", sp))' + LF + LF.join([
        'sp.addField(CtField.make("public static final long SETTLE_MS = 3000L;", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENEPOCH = new java.util.concurrent.ConcurrentHashMap();", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEENKEY = new java.util.concurrent.ConcurrentHashMap();", sp))',
        'sp.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CHANGEDAT = new java.util.concurrent.ConcurrentHashMap();", sp))',
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
        'sp.addMethod(CtNewMethod.make("""',
        'public static long epoch(java.util.UUID u) {',
        '  try {',
        '    Object e = bridge().get("profile:epoch:" + u.toString());',
        '    if (e instanceof Number) return ((Number) e).longValue();',
        '    if (e != null) return Long.parseLong(String.valueOf(e).trim());',
        '  } catch (Throwable t) { }',
        '  return 0L;',
        '}""", sp))',
        '# the active key, or null for SETTLE_MS after the epoch or the key changed (sweep skips, page item moves are refused) so an',
        '# inventory swap and a key switch that do not land in the same world-thread task cannot move items across profiles.',
        '# Without SkyyProfiles the epoch stays 0 and the key stays the uuid: never unsettled.',
        'sp.addMethod(CtNewMethod.make("""',
        'public static String settledKey(java.util.UUID u) {',
        '  long e = epoch(u);',
        '  String k = pkey(u);',
        '  Long le = (Long) SEENEPOCH.put(u, Long.valueOf(e));',
        '  String lk = (String) SEENKEY.put(u, k);',
        '  long now = System.currentTimeMillis();',
        '  if (le != null && lk != null && (le.longValue() != e || !lk.equals(k))) CHANGEDAT.put(u, Long.valueOf(now));',
        '  Long t = (Long) CHANGEDAT.get(u);',
        '  if (t != null) {',
        '    if (now - t.longValue() < SETTLE_MS) return null;',
        '    CHANGEDAT.remove(u);',
        '  }',
        '  return k;',
        '}""", sp))',
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

# ---------------- page fields (key = the pkey the page was last built for) ----------------
rep('cpg.addField(CtField.make("public String[] fuelIds;", cpg))',
    'cpg.addField(CtField.make("public String[] fuelIds;", cpg))' + LF
    + 'cpg.addField(CtField.make("public String key;", cpg))' + LF
    + 'cpg.addField(CtField.make("public String noticeKey;", cpg))')
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
      + '    if (k == null) {{ this.info = "switching profiles - try again in a moment"; rebuild(); return; }}' + LF
      + '    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; rebuild(); return; }}' + LF
      + '    for (int i = 0; i < 36; i++) {{' + LF),
     ('SweepTask.withdraw(player, u, this.cells[i], n)', 'SweepTask.withdraw(player, k, this.cells[i], n)'),
     ('SweepTask.withdraw(player, u, this.cells[i], 64)', 'SweepTask.withdraw(player, k, this.cells[i], 64)'),
     ('SackPool.save(u);', 'SackPool.save(k);'),
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
        '  if (c > 0) {PKG}.SackPool.save(old);',
        '  {PKG}.CraftLog.line(old, "PROFILE bench mirror retired - active key now " + k + " consumed=" + c);',
        '  return m;',
        '}}""", mir))',
        'mir.addMethod(CtNewMethod.make(f"""',
        'public {IQ}[] quantities() {{',
    ]))

# ---------------- CraftLinkTask ----------------
CLT = '# ================= CraftLinkTask'
blk('public void run() {{',
    [('    java.util.UUID u = pr.getUuid();' + LF + '    {WM} wm = p.getWindowManager();',
      '    java.util.UUID u = pr.getUuid();' + LF
      + '    String k = {PKG}.SackPool.pkey(u);' + LF
      + '    {PKG}.BagMirror stale = {PKG}.BagMirror.retireOther(u, k);' + LF
      + '    {WM} wm = p.getWindowManager();'),
     ('{PKG}.BagMirror m = {PKG}.BagMirror.of(u);' + LF + '      int consumed = m.sync(u);',
      '{PKG}.BagMirror m = {PKG}.BagMirror.of(k);' + LF + '      int consumed = m.sync();'),
     ('String sig = m.rebuild(u, caps);', 'String sig = m.rebuild(caps);'),
     ('      {IC} existing = sec.getItemContainer();' + LF,
      '      {IC} existing = sec.getItemContainer();' + LF
      + '      if (stale != null && existing != null && (existing == stale.combined || existing == stale.cont)) existing = ({IC}) stale.vanilla;' + LF),
     ('      if (consumed > 0) {PKG}.SackPool.save(u);', '      if (consumed > 0) {PKG}.SackPool.save(k);'),
     ('{PKG}.BagMirror.MIRRORS.get(u);' + LF
      + '      if (m != null) {{ int c = m.sync(u); if (c > 0) {PKG}.SackPool.save(u); {PKG}.BagMirror.MIRRORS.remove(u); }}',
      '{PKG}.BagMirror.MIRRORS.get(k);' + LF
      + '      if (m != null) {{ int c = m.sync(); if (c > 0) {PKG}.SackPool.save(k); {PKG}.BagMirror.MIRRORS.remove(k); }}')], CLT)

# ---------------- CraftPage ----------------
CPA = '# ================= CraftPage (inventory crafting v1'
blk('public java.util.ArrayList buildTabs({PLA} p, java.util.UUID u) {{',
    [('buildTabs({PLA} p, java.util.UUID u)', 'buildTabs({PLA} p, java.util.UUID u, String k)'),
     ('ProcStore.pending(u, bn)', 'ProcStore.pending(k, bn)')], CPA)
blk('public static {CIC} materials({PLA} p, java.util.UUID u) {{',
    [('java.util.UUID u', 'String k'),
     ('BagMirror.of(u);' + LF + '  m.sync(u);' + LF + '  m.rebuild(u, ', 'BagMirror.of(k);' + LF + '  m.sync();' + LF + '  m.rebuild(')], CPA)
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
     ('markDirty(u)', 'markDirty(k)'), ('materials(p, u)', 'materials(p, k)')], CPA)
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
      '  this.liveOn = false;' + LF + '  this.key = null;' + LF + '  if (p == null) return;' + LF
      + '  String k = {PKG}.SackPool.pkey(u);' + LF + '  this.key = k;' + LF + '  this.tabs = buildTabs(p, u, k);'),
     ('buildProc(b, ev, p, u); return;', 'buildProc(b, ev, p, u, k); return;'),
     ('{CIC} mats = materials(p, u);', '{CIC} mats = materials(p, k);')], HPA)
blk('public void handleDataEvent({REF} ref, {ST} st, String data) {{',
    [('    if (handleProc(ref, st, p, u, data)) return;',
      '    String k = {PKG}.SackPool.settledKey(u);' + LF
      + '    if (k == null) {{ this.info = "switching profiles - try again in a moment"; rebuild(); return; }}' + LF
      + '    if (this.key != null && !this.key.equals(k)) {{ this.info = "your profile changed - this page now shows it"; this.pageNo = 0; rebuild(); return; }}' + LF
      + '    if (handleProc(ref, st, p, u, k, data)) return;'),
     ('{CIC} mats = materials(p, u);', '{CIC} mats = materials(p, k);'),
     ('{PKG}.BagMirror m = {PKG}.BagMirror.of(u);' + LF + '    int consumed = m.sync(u);' + LF + '    if (consumed > 0) {PKG}.SackPool.save(u);',
      '{PKG}.BagMirror m = {PKG}.BagMirror.of(k);' + LF + '    int consumed = m.sync();' + LF + '    if (consumed > 0) {PKG}.SackPool.save(k);'),
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
        '# log the switch; an open page built for another key is told in run(). Without SkyyProfiles the epoch stays 0: never fires.',
        'ptk.addMethod(CtNewMethod.make(f"""',
        'public static boolean epochCheck(java.util.UUID u, String k) {{',
        '  long ep = {PKG}.SackPool.epoch(u);',
        '  Long last = (Long) EPOCH.put(u, Long.valueOf(ep));',
        '  if (last == null || last.longValue() == ep) return false;',
        '  try {{ {HSV}.SCHEDULED_EXECUTOR.execute(new {PKG}.SackSaver()); }} catch (Throwable t) {{ }}',
        '  {PKG}.CraftLog.line(k, "PROFILE epoch " + last + " -> " + ep + " - bags, furnace and tannery now use this key");',
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

# every storage call must now take the pkey - fail the derivation if a UUID-keyed call survived
for bad in ("SackPool.save(u)", "SackPool.pool(u)", "SackPool.get(u,", "SackPool.add(u,", "SackPool.catTotal(u,", "ProcStore.get(u,",
            "ProcStore.of(u,", "ProcStore.all(u)", "ProcStore.markDirty(u)", "ProcStore.BROKEN.containsKey(u)", "BagMirror.of(u)",
            "BagMirror.MIRRORS.get(u)", "CraftLog.line(u,", "CraftLog.write(u,", "m.sync(u)", "saveSoon(u)", "materials(p, u)"):
    assert bad not in s, "UUID-keyed storage call left: " + bad

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
