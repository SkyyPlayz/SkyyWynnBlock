"""SkyyCollections 0.1.5 - build script
0.1.5: per-profile storage (tools/PROFILES-CONTRACT.md). Counts are kept per SkyyProfiles profile: counts/<pkey>.properties,
       pkey = the contract helper (profile 1 = <uuid> = every existing file, profile N = <uuid>-pN); the count cache and the
       dirty set are keyed by that pkey String, so a switch just resolves to another entry and the old profile's unsaved
       counts are flushed under their own key. coll:recipes:<uuid> stays keyed by UUID (it describes the ACTIVE profile) and
       is republished when profile:epoch:<uuid> or the active pkey differs from the last publish. Without SkyyProfiles:
       pkey = uuid, no epoch -> same files and bridge output as 0.1.4.
       Integration check against the pinned SkyyProfiles 0.1 semantics (end of PROFILES-CONTRACT.md), fixed in place:
       - Breaks are counted in a World.execute task and only when BreakBlockEvent.isCancelled() is still false (SkyySkills
         pattern). Before, breaks cancelled by SkyyIslands' island protection still counted: visitors could farm collections
         and recipe unlocks on someone else's island. The profile key is resolved when the block breaks.
       - Saver tick 1 s (was 5 s): epoch/key check + first publish of players who just joined; flush every 10 s as before.
         coll:recipes:<uuid> (SkyySacks Collections craft tab, SkyyMenu tooltip) follows a switch within ~1 s and appears
         ~1 s after a join. The first publish of a session is the baseline; the first counted break publishes it first, so a
         milestone's "+N recipe(s)" counts only new unlocks. The CollRecheck fast rechecks are gone (SkyyProfiles flips its
         key function before it bumps the epoch, so a new epoch always comes with the new key).
       - An unreadable counts file is no longer cached as empty (the next flush overwrote it = all counts of that profile
         lost): retried every 2 s while needed, breaks meanwhile not counted, file left untouched, coll:recipes:<uuid>
         removed until it reads. A failed save is retried at the next flush. Reads and writes share one lock (CollIO) and the
         replace is retried 5x 20 ms. No disk I/O inside the publish or bump monitors.
       Derived by tools/coll_0_1_5_patch.py.
0.1.4: command rules (engine-verified 2026-09-23). /collections (alias /coll) is open to every player (permission group
       hytale:Adventurer; before, only "*" admins held the auto node). "/collections unlocks" (alias recipes) and
       "/collections reload" are real subcommands now (optional args are not positional, so the 0.1.3 forms failed with
       wrongNumberRequiredParameters). unlocks = Adventurer group; reload = requirePermission("skyycollections.admin") plus
       setPermissionGroups(new String[0]) so it does NOT inherit the parent's Adventurer group (putRecursivePermissionGroups
       would otherwise grant skyycollections.admin to every player). "--action unlocks|reload" still works.
       Derived by tools/coll_0_1_4_patch.py.
0.1.3: recipe unlocks published to the bridge (coll:recipes:<uuid>), auto rule + unlocks.properties, /collections unlocks|reload. (javassist via jpype).
Run:   python build_skyycollections_0.1.5.py            -> SkyyCollections/SkyyCollections-0.1.5.jar
       python build_skyycollections_0.1.5.py --deploy   -> also copies to Mods/SkyyCollections.jar and enables it in the HUD mod world
Fixes vs 0.1 (code review 2026-09-22): page build() is public and fully inline (no .ui files, no underscores in IDs), saver cancelled + final
flush on shutdown, race-free counts() load, atomic file writes, streams closed on error paths, BlockType id cast,
friendlier names in chat/page, failures logged.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.5"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
BBE = "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent"
QRY = "com.hypixel.hytale.component.query.Query"
BTY = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
CEV = "com.hypixel.hytale.component.system.CancellableEcsEvent"

for c, m in ((CRR, "getInput"), (CRR, "getAssetMap"), (MQ, "getItemId"), (UNI, "getPlayers"), (PR, "hasPermission"), ("com.hypixel.hytale.server.core.command.system.CommandContext", "provided"),
             (BBE, "getBlockType"), (BTY, "getId"), (ACH, "getReferenceTo"), (HSV, "SCHEDULED_EXECUTOR"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), ("com.hypixel.hytale.component.Archetype", "empty"),
             (AC, "setPermissionGroups"), (AC, "addSubCommand"), (AC, "requirePermission"), (AC, "addAliases"),
             (ST, "getExternalData"), (EST, "getWorld"), (WLD, "execute"), (CEV, "isCancelled"), (PR, "isValid")):
    B.probe(pool, c, m)

PKG = "com.skyy.collections"
store = pool.makeClass(PKG + ".CollStore")
sysc  = pool.makeClass(PKG + ".CollSystem", pool.get(EES))
unl   = pool.makeClass(PKG + ".CollUnlocks")
sav   = pool.makeClass(PKG + ".CollSaver")
cio   = pool.makeClass(PKG + ".CollIO")
brk   = pool.makeClass(PKG + ".CollBreakTask")
ccmp  = pool.makeClass(PKG + ".CollCmp")
page  = pool.makeClass(PKG + ".CollPage", pool.get(PAGE))
ulc   = pool.makeClass(PKG + ".CollUnlocksCmd", pool.get(APC))
rlc   = pool.makeClass(PKG + ".CollReloadCmd", pool.get(APC))
cmd   = pool.makeClass(PKG + ".CollCmd", pool.get(APC))
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'   # vanilla /help /who /ping pattern (SkyyEssentials 0.1)
pl    = pool.makeClass(PKG + ".SkyyCollectionsPlugin", pool.get(JP))
ROWS = 14

# ================= CollStore =================
store.addField(CtField.make("public static java.nio.file.Path DIR;", store))
store.addField(CtField.make(f"public static {LOG} LOG;", store))
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();", store))
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", store))
store.addField(CtField.make("public static final long[] TIERS = new long[] { 50L, 250L, 1000L, 5000L, 20000L };", store))
store.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCollections] " + msg); } catch (Throwable t) { }
}""", store))
store.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", store))
# tools/PROFILES-CONTRACT.md storage-key helper, verbatim: active profile's key, uuid.toString() (= profile 1) without SkyyProfiles
store.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", store))
# per pkey: when its counts file last failed to read (Long millis). A failed read is never cached as empty; retried at most every 2 s
store.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();", store))
# Every counts-file read and write holds CollIO.class (a leaf lock: nothing else is taken inside it). On Windows an open reader
# makes a concurrent replace fail, and the shutdown flush can overlap a saver flush that is still running (same .tmp file).
# The replace is retried 5x 20 ms (sharing violations from scanners/indexers) before the save counts as failed.
cio.addMethod(CtNewMethod.make("""
public static synchronized java.util.Properties read(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  }
  return p;
}""", cio))
cio.addMethod(CtNewMethod.make("""
public static synchronized void write(java.nio.file.Path dir, String key, java.util.Properties p) throws java.io.IOException {
  java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dir.resolve(key + ".properties.tmp");
  java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
  try { p.store(out, "SkyyCollections"); } finally { out.close(); }
  java.nio.file.Path f = dir.resolve(key + ".properties");
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""", cio))
store.addMethod(CtNewMethod.make("""
public static java.util.Map countsKey(String key) {
  java.util.Map m = (java.util.Map) DATA.get(key);
  if (m != null) return m;
  m = new java.util.concurrent.ConcurrentHashMap();
  Long bad = (Long) BROKEN.get(key);
  if (bad != null && System.currentTimeMillis() - bad.longValue() < 2000L) return m;
  try {
    java.util.Properties p = com.skyy.collections.CollIO.read(DIR.resolve(key + ".properties"));
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {
      String k = (String) en.nextElement();
      try { m.put(k, Long.valueOf(Long.parseLong(p.getProperty(k).trim()))); } catch (Throwable t) { }
    }
  } catch (Throwable t) {
    if (BROKEN.put(key, Long.valueOf(System.currentTimeMillis())) == null) warn("could not read counts/" + key + ".properties - breaks for that profile are not counted and the file is left untouched until it reads again (retried every 2 s while needed): " + t);
    return new java.util.concurrent.ConcurrentHashMap();
  }
  if (BROKEN.remove(key) != null) warn("counts/" + key + ".properties reads again");
  java.util.Map prev = (java.util.Map) DATA.putIfAbsent(key, m);
  return prev != null ? prev : m;
}""", store))
store.addMethod(CtNewMethod.make("""
public static java.util.Map counts(java.util.UUID u) {
  return countsKey(pkey(u));
}""", store))
store.addMethod(CtNewMethod.make("""
public static boolean save(String key) {
  try {
    java.util.Map m = (java.util.Map) DATA.get(key);
    if (m == null) return true;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), String.valueOf(((Long) e.getValue()).longValue()));
    }
    com.skyy.collections.CollIO.write(DIR, key, p);
    return true;
  } catch (Throwable t) { warn("could not save counts/" + key + ".properties (retried at the next flush): " + t); return false; }
}""", store))
store.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.ArrayList failed = new java.util.ArrayList();
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    it.remove();
    if (!save(key)) failed.add(key);
  }
  for (int i = 0; i < failed.size(); i++) DIRTY.put(failed.get(i), Boolean.TRUE);
}""", store))
store.addMethod(CtNewMethod.make("""
public static int tierOf(long n) {
  int t = 0;
  for (int i = 0; i < TIERS.length; i++) if (n >= TIERS[i]) t = i + 1;
  return t;
}""", store))
store.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "0", "I", "II", "III", "IV", "V" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""", store))
store.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ');
  int q = s.indexOf(':');
  if (q >= 0 && q + 1 < s.length()) s = s.substring(q + 1);
  return s;
}""", store))
# returns new tier if a milestone was crossed, else 0
store.addMethod(CtNewMethod.make("""
public static synchronized int bumpLocked(String key, String id, long n) {
  java.util.Map m = countsKey(key);
  Long v = (Long) m.get(id);
  long oldv = v == null ? 0L : v.longValue();
  long newv = oldv + n;
  m.put(id, Long.valueOf(newv));
  DIRTY.put(key, Boolean.TRUE);
  int ot = tierOf(oldv); int nt = tierOf(newv);
  return nt > ot ? nt : 0;
}""", store))
# the counts file is loaded BEFORE the bump monitor (the world thread never waits on disk I/O while holding it)
store.addMethod(CtNewMethod.make("""
public static int bumpKey(String key, String id, long n) {
  countsKey(key);
  return bumpLocked(key, id, n);
}""", store))

# ================= CollUnlocks (bridge publisher) =================
unl.addField(CtField.make("public static java.nio.file.Path FILE;", unl))
unl.addField(CtField.make("public static volatile boolean AUTO = true;", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap TABLE = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", unl))
# per UUID: profile:epoch value (Long, -1 = absent) and pkey (String) the last publish was computed for
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBKEY = new java.util.concurrent.ConcurrentHashMap();", unl))
unl.addMethod(CtNewMethod.make(f"""
public static java.util.Map bridge() {{
  return {PKG}.CollStore.bridge();
}}""", unl))
unl.addMethod(CtNewMethod.make("""
public static long epochOf(java.util.UUID u) {
  try {
    Object o = bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) return ((Number) o).longValue();
    if (o != null) return Long.parseLong(String.valueOf(o).trim());
  } catch (Throwable t) { }
  return -1L;
}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static synchronized void load() {{
  TABLE.clear();
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String text = "# SkyyCollections recipe unlocks\\n"
        + "# auto=true : a recipe unlocks when one of its inputs reaches tier I (50 collected) and every input you have started\\n"
        + "#             collecting is at tier I or better (inputs you never collected are ignored)\\n"
        + "# explicit  : <CollectionId>.<tier 1-5>=RecipeId,RecipeId   e.g.  Rock_Stone.2=Rock_Stone_Brick\\n"
        + "# collection ids are the BLOCK ids you break (see /collections); recipe ids are CraftingRecipe asset ids (/craft shows names)\\n"
        + "auto=true\\n";
      java.nio.file.Files.write(FILE, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    AUTO = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("auto", "true")).trim());
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {{
      String k = ((String) en.nextElement()).trim();
      if (k.equals("auto")) continue;
      int dot = k.lastIndexOf('.');
      if (dot <= 0) continue;
      try {{
        int tier = Integer.parseInt(k.substring(dot + 1));
        if (tier < 1 || tier > 5) continue;
        TABLE.put(k, p.getProperty(k).trim());
      }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("could not load unlocks.properties: " + t); }}
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static java.util.TreeSet compute(java.util.Map counts) {{
  java.util.TreeSet out = new java.util.TreeSet();
  if (counts == null || counts.isEmpty()) return out;
  try {{
    java.util.Iterator it = TABLE.entrySet().iterator();
    while (it.hasNext()) {{
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      String k = (String) e.getKey();
      int dot = k.lastIndexOf('.');
      String coll = k.substring(0, dot);
      int tier = Integer.parseInt(k.substring(dot + 1));
      Long c = (Long) counts.get(coll);
      if (c == null || {PKG}.CollStore.tierOf(c.longValue()) < tier) continue;
      String[] ids = ((String) e.getValue()).split(",");
      for (int i = 0; i < ids.length; i++) if (ids[i].trim().length() > 0) out.add(ids[i].trim());
    }}
    if (!AUTO) return out;
    long t1 = {PKG}.CollStore.TIERS[0];
    java.util.Iterator rit = {CRR}.getAssetMap().getAssetMap().values().iterator();
    while (rit.hasNext()) {{
      {CRR} r = ({CRR}) rit.next();
      if (r == null) continue;
      {MQ}[] in = r.getInput();
      if (in == null || in.length == 0) continue;
      boolean anyTier = false; boolean blocked = false;
      for (int i = 0; i < in.length; i++) {{
        if (in[i] == null) continue;
        String id = in[i].getItemId();
        if (id == null) continue;
        Long c = (Long) counts.get(id);
        if (c == null || c.longValue() <= 0L) continue;
        if (c.longValue() >= t1) anyTier = true; else blocked = true;
      }}
      if (anyTier && !blocked) {{ String rid = (String) r.getId(); if (rid != null) out.add(rid); }}
    }}
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("unlock compute failed: " + t); }}
  return out;
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static synchronized int publishLocked(java.util.UUID u) {{
  try {{
    int n = 0;
    for (int pass = 0; pass < 3; pass++) {{
      long ep = epochOf(u);
      String key = {PKG}.CollStore.pkey(u);
      java.util.Map counts = {PKG}.CollStore.countsKey(key);
      if (!{PKG}.CollStore.DATA.containsKey(key)) {{
        bridge().remove("coll:recipes:" + u.toString());
        PUBLISHED.remove(u);
        EPOCH.remove(u);
        PUBKEY.remove(u);
        return 0;
      }}
      java.util.TreeSet ids = compute(counts);
      StringBuilder sb = new StringBuilder();
      java.util.Iterator it = ids.iterator();
      while (it.hasNext()) {{ if (sb.length() > 0) sb.append(','); sb.append((String) it.next()); }}
      bridge().put("coll:recipes:" + u.toString(), sb.toString());
      PUBLISHED.put(u, Integer.valueOf(ids.size()));
      EPOCH.put(u, Long.valueOf(ep));
      PUBKEY.put(u, key);
      n = ids.size();
      if (key.equals({PKG}.CollStore.pkey(u))) break;
    }}
    return n;
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("publish failed for " + u + ": " + t); return 0; }}
}}""", unl))
# The counts file is loaded BEFORE the publish monitor, so the monitor never waits on disk I/O (safe from the world thread).
# A key whose counts file cannot be read publishes nothing: coll:recipes:<uuid> is removed (never another profile's list) and the
# player is dropped from PUBLISHED, so publishOnline retries every tick until it reads.
unl.addMethod(CtNewMethod.make(f"""
public static int publish(java.util.UUID u) {{
  try {{ {PKG}.CollStore.countsKey({PKG}.CollStore.pkey(u)); }} catch (Throwable t) {{ }}
  return publishLocked(u);
}}""", unl))
# Republish an already-published player when the active profile changed since the last publish: profile:epoch:<uuid> moved or
# pkey() now differs from the key publish computed for. SkyyProfiles 0.1 commits its key function BEFORE it bumps the epoch
# (PROFILES-CONTRACT.md "Key flip timing"), so a moved epoch always comes with the new key; the pkey comparison covers the
# one-call window where the key already flipped and the epoch has not. Epoch bumps that keep the key (first profile, a new
# profile before its switch, setclass) republish the same list: harmless. Never-published players are left to baseline() /
# publishOnline(): their first publish is the baseline (absent -> value is not a change), nothing switch-like happens.
unl.addMethod(CtNewMethod.make(f"""
public static boolean syncEpoch(java.util.UUID u) {{
  try {{
    if (u == null || !PUBLISHED.containsKey(u)) return false;
    Long seen = (Long) EPOCH.get(u);
    String key = (String) PUBKEY.get(u);
    if (seen != null && seen.longValue() == epochOf(u) && key != null && key.equals({PKG}.CollStore.pkey(u))) return false;
    publish(u);
    return true;
  }} catch (Throwable t) {{ return false; }}
}}""", unl))
# first sight of a player in this session publishes the baseline; after that only a changed epoch/key republishes
unl.addMethod(CtNewMethod.make("""
public static void baseline(java.util.UUID u) {
  if (u == null) return;
  if (!PUBLISHED.containsKey(u)) publish(u); else syncEpoch(u);
}""", unl))
unl.addMethod(CtNewMethod.make("""
public static void checkEpochs() {
  try {
    java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
    while (it.hasNext()) syncEpoch((java.util.UUID) it.next());
  } catch (Throwable t) { }
}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) publish(u);
    }}
    PUBLISHED.keySet().retainAll(online);
    EPOCH.keySet().retainAll(online);
    PUBKEY.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", unl))
unl.addMethod(CtNewMethod.make("""
public static void republishAll() {
  java.util.Iterator it = new java.util.ArrayList(PUBLISHED.keySet()).iterator();
  while (it.hasNext()) publish((java.util.UUID) it.next());
}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static void sendUnlocks({PR} pr) {{
  java.util.TreeSet ids = compute({PKG}.CollStore.counts(pr.getUuid()));
  publish(pr.getUuid());
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = ids.iterator(); int n = 0;
  while (it.hasNext() && n < 12) {{ if (sb.length() > 0) sb.append(", "); sb.append({PKG}.CollStore.pretty((String) it.next())); n++; }}
  pr.sendMessage({MSG}.raw("[Collections] " + ids.size() + " recipe(s) unlocked" + (ids.size() > 0 ? ": " + sb + (ids.size() > 12 ? ", ..." : "") + "  -> /craft (Collections tab)" : ". Break blocks to reach tier I (50) of a material.")));
}}""", unl))
unl.addMethod(CtNewMethod.make(f"""
public static void reloadAndReport({PR} pr) {{
  load();
  republishAll();
  pr.sendMessage({MSG}.raw("[Collections] unlocks.properties reloaded (" + TABLE.size() + " explicit rule(s), auto=" + AUTO + ")"));
}}""", unl))

# ================= CollBreakTask (deferred count, SkyySkills BreakTask pattern) =================
# World.execute always queues, so when run() starts every other system (SkyyIslands' GuardBreak, whose order relative to ours is
# unknown) has handled the event. The engine creates a new BreakBlockEvent per break, so holding it is safe.
brk.addInterface(pool.get("java.lang.Runnable"))
brk.addField(CtField.make(f"public {BBE} ev;", brk))
brk.addField(CtField.make(f"public {PR} pr;", brk))
brk.addField(CtField.make("public java.util.UUID u;", brk))
brk.addField(CtField.make("public String key;", brk))
brk.addField(CtField.make("public String id;", brk))
brk.addConstructor(CtNewConstructor.make(f"""
public CollBreakTask({BBE} ev, {PR} pr, java.util.UUID u, String key, String id) {{
  this.ev = ev; this.pr = pr; this.u = u; this.key = key; this.id = id;
}}""", brk))
# key = the profile that broke the block. If a switch ran between the break and this task (both world-thread tasks), the break
# still counts for that profile, silently (no milestone line, no publish: coll:recipes describes the ACTIVE profile).
brk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    boolean active = this.key.equals({PKG}.CollStore.pkey(this.u));
    if (active) {PKG}.CollUnlocks.baseline(this.u);
    int newTier = {PKG}.CollStore.bumpKey(this.key, this.id, 1L);
    if (newTier <= 0 || !active) return;
    Object was = {PKG}.CollUnlocks.PUBLISHED.get(this.u);
    int before = was instanceof Integer ? ((Integer) was).intValue() : 0;
    int now = {PKG}.CollUnlocks.publish(this.u);
    if (this.pr != null && this.pr.isValid()) this.pr.sendMessage({MSG}.raw("Collection milestone! " + {PKG}.CollStore.pretty(this.id) + " " + {PKG}.CollStore.roman(newTier) + (now > before ? "  +" + (now - before) + " recipe(s) unlocked - /craft" : "")));
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("break count failed: " + t); }}
}}""", brk))

# ================= CollSystem (BreakBlockEvent listener) =================
sysc.addConstructor(CtNewConstructor.make(f"public CollSystem() {{ super({BBE}.class); }}", sysc))
sysc.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return com.hypixel.hytale.component.Archetype.empty();
}}""", sysc))
sysc.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    {BBE} e = ({BBE}) ev;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    {BTY} bt = e.getBlockType();
    if (bt == null) return;
    String id = (String) bt.getId();
    if (id == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    w.execute(new {PKG}.CollBreakTask(e, pr, u, {PKG}.CollStore.pkey(u), id));
  }} catch (Throwable t) {{ {PKG}.CollStore.warn("break handler failed: " + t); }}
}}""", sysc))

sav.addInterface(pool.get("java.lang.Runnable"))
sav.addField(CtField.make("public int ticks;", sav))
sav.addConstructor(CtNewConstructor.make("public CollSaver() { }", sav))
sav.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{ {PKG}.CollUnlocks.checkEpochs(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollUnlocks.publishOnline(); }} catch (Throwable t) {{ }}
  this.ticks = this.ticks + 1;
  if (this.ticks % 10 != 0) return;
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
}}""", sav))

ccmp.addInterface(pool.get("java.util.Comparator"))
ccmp.addConstructor(CtNewConstructor.make("public CollCmp() { }", ccmp))
ccmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((java.util.Map.Entry) a).getValue()).longValue();
  long y = ((Long) ((java.util.Map.Entry) b).getValue()).longValue();
  if (x != y) return x > y ? -1 : 1;
  return ((String) ((java.util.Map.Entry) a).getKey()).compareTo((String) ((java.util.Map.Entry) b).getKey());
}""", ccmp))

# ================= CollPage (static file + sets only) =================
page.addConstructor(CtNewConstructor.make(f"public CollPage({PR} pr) {{ super(pr, {LIFE}.CanDismiss); }}", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  java.util.ArrayList entries = new java.util.ArrayList({PKG}.CollStore.counts(u).entrySet());
  java.util.Collections.sort(entries, new {PKG}.CollCmp());
  int n = entries.size() < {ROWS} ? entries.size() : {ROWS};
  String summary = entries.size() == 0 ? "Nothing collected yet - go break some blocks!" : (entries.size() + " collections tracked" + (entries.size() > {ROWS} ? " (top {ROWS} shown)" : ""));
  b.appendInline((String) null, "Group #SkyyColl {{ Anchor: (Width: 560, Height: 460); Background: #0b1524(0.94); Padding: (Horizontal: 14, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyColl", "Group {{ Anchor: (Height: 2); Background: #b48fe0; }}");
  b.appendInline("#SkyyColl", "Label {{ Anchor: (Height: 26); Text: \\"Collections\\"; Style: (FontSize: 15, RenderBold: true, TextColor: #f0e6ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyColl", "Label {{ Anchor: (Height: 16); Text: \\"" + summary + "\\"; Style: (FontSize: 11, TextColor: #c0b3d6, HorizontalAlignment: Center); }}");
  for (int i = 0; i < n; i++) {{
    java.util.Map.Entry e = (java.util.Map.Entry) entries.get(i);
    String id = (String) e.getKey();
    long cnt = ((Long) e.getValue()).longValue();
    int tier = {PKG}.CollStore.tierOf(cnt);
    long next = tier < 5 ? {PKG}.CollStore.TIERS[tier] : 0L;
    String prog = tier >= 5 ? "MAX" : (cnt + " / " + next);
    String name = {PKG}.CollStore.pretty(id).replace("\\"", "");
    b.appendInline("#SkyyColl", "Group #SkyyCRow" + i + " {{ Anchor: (Height: 24); LayoutMode: Left; }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 330, Height: 20); Text: \\"" + name + "  " + {PKG}.CollStore.roman(tier) + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyCRow" + i, "Label {{ Anchor: (Width: 170, Height: 20); Text: \\"" + prog + "\\"; Style: (FontSize: 11, TextColor: #9fd8a2, VerticalAlignment: Center); }}");
  }}
}}""", page))

# ================= command =================
# /collections unlocks (alias recipes) - every player
ulc.addConstructor(CtNewConstructor.make(f"""
public CollUnlocksCmd() {{
  super("unlocks", "List the recipes your collections have unlocked");
  addAliases(new String[] {{ "recipes" }});
  {ADV}
}}""", ulc))
ulc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PKG}.CollUnlocks.sendUnlocks(pr);
  }} catch (Throwable t) {{
    {PKG}.CollStore.warn("/collections unlocks failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyCollections] could not open the page"));
  }}
}}""", ulc))
# /collections reload - admin. Empty group list = do NOT inherit the parent's hytale:Adventurer group (see docstring).
rlc.addConstructor(CtNewConstructor.make(f"""
public CollReloadCmd() {{
  super("reload", "Reload unlocks.properties and republish recipe unlocks (admin)");
  requirePermission("skyycollections.admin");
  setPermissionGroups(new String[0]);
}}""", rlc))
rlc.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PKG}.CollUnlocks.reloadAndReport(pr);
  }} catch (Throwable t) {{
    {PKG}.CollStore.warn("/collections reload failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyCollections] could not open the page"));
  }}
}}""", rlc))
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public CollCmd() {{
  super("collections", "View your collections; /collections unlocks | reload");
  addAliases(new String[] {{ "coll" }});
  this.actionArg = withOptionalArg("action", "unlocks | reload", {ATY}.STRING);
  {ADV}
  addSubCommand(new {PKG}.CollUnlocksCmd());
  addSubCommand(new {PKG}.CollReloadCmd());
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (ctx.provided(this.actionArg)) {{
      String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
      if (a.equals("unlocks") || a.equals("recipes")) {{
        {PKG}.CollUnlocks.sendUnlocks(pr);
        return;
      }}
      if (a.equals("reload")) {{
        if (!pr.hasPermission("skyycollections.admin")) {{ pr.sendMessage({MSG}.raw("[Collections] no permission")); return; }}
        {PKG}.CollUnlocks.reloadAndReport(pr);
        return;
      }}
    }}
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.CollPage(pr));
  }} catch (Throwable t) {{
    {PKG}.CollStore.warn("/collections failed: " + t);
    pr.sendMessage({MSG}.raw("[SkyyCollections] could not open the page"));
  }}
}}""", cmd))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture saver;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyCollectionsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.CollStore.LOG = getLogger();
  {PKG}.CollStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyCollections").resolve("counts");
  {PKG}.CollUnlocks.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCollections").resolve("unlocks.properties");
  {PKG}.CollUnlocks.load();
  getEntityStoreRegistry().registerSystem(new {PKG}.CollSystem());
  getCommandRegistry().registerCommand(new {PKG}.CollCmd());
  this.saver = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CollSaver(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] {VERSION} ready - break blocks, /collections to view, per-profile counts, unlocks auto=" + {PKG}.CollUnlocks.AUTO + " explicit=" + {PKG}.CollUnlocks.TABLE.size());
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.saver != null) this.saver.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CollStore.flushDirty(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (cio, store, unl, brk, sysc, sav, ccmp, page, ulc, rlc, cmd, pl):
    c.writeFile(OUT)
print("classes written")

rows = "\n".join("""    Group #c_row_%d {
      Anchor: (Height: 24);
      LayoutMode: Left;
      Visible: false;
      Label #c_name_%d { Anchor: (Width: 330, Height: 20); Style: (FontSize: 11, RenderBold: true, TextColor: #ffffff); Text: ""; }
      Label #c_prog_%d { Anchor: (Width: 170, Height: 20); Style: (FontSize: 11, TextColor: #9fd8a2); Text: ""; }
    }""" % (i, i, i) for i in range(ROWS))
COLL_UI = """Group {
  Anchor: (Full: 0);
  Group #SkyyCollections {
    Anchor: (Horizontal: 0, Vertical: 0, Width: 560, Height: 460);
    Background: #0b1524(0.94);
    Padding: (Horizontal: 14, Vertical: 10);
    LayoutMode: Top;
    Group { Anchor: (Height: 2); Background: #b48fe0; }
    Label { Anchor: (Height: 26); Style: (FontSize: 15, RenderBold: true, TextColor: #f0e6ff, Alignment: Center); Text: "Collections"; }
    Label #c_summary { Anchor: (Height: 16); Style: (FontSize: 11, TextColor: #c0b3d6, Alignment: Center); Text: ""; }
%s
  }
}
""" % rows

jar = os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyCollections", VERSION, "SkyWynn collections: every block you break counts toward per-item milestones (I-V). /collections to view. Collection tiers unlock recipes for the SkyySacks craft page (auto rule + unlocks.properties). Counts are per profile when SkyyProfiles is installed.", PKG + ".SkyyCollectionsPlugin"),
           OUT, {})  # page built inline (no .ui files: see memory hytale-ui-rules)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCollections.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCollections" % VERSION, disable_prefix="Skyy:")
