"""Derive SkyyGuilds/build_skyyguilds_0.1.7.py from the LIVE 0.1.6 (build_skyyguilds_0.1.6.py = the tools/deploy_set.py SET pin; 0.1.6 and every
older script stay untouched).
Run:  python tools/guilds_0_1_7_patch.py   then   python SkyyGuilds/build_skyyguilds_0.1.7.py   then   python SkyyGuilds/test_skyyguilds_0.1.7.py
(never --deploy: coordinated deploy). Edit THIS patch, never the generated script.

0.1.7 (2026-10-13) = LAG FIXES from the code audit (research/Code-Structure-Audit.md finding #14 + pack-wide pattern 1; Skyy 2026-10-13:
"During/ before we consolidate the mods together, lets audit the code structure, and make sure they are working together in the smoothest
easiest lag free way possible"). Same guilds, same bank rules, same files, same texts:
 A. LOCK-FREE BRIDGE: GuildStore.bridge() caches the skyy.bridge map in the static volatile GuildStore.BRIDGE (only the first call takes the
    System.class monitor, to create the map exactly as before); the config kit's CfgRows.bridge() does the same (tools/skyycfg.py).
    Config kit KEEP 20 -> 10 (AGENT-BRIEF: every rebuilt mod; Skyy 2026-10-05).
 B. GuildTick (every 5 s) no longer fsync-writes guild files INSIDE the one GuildStore lock: GuildStore.takeFlush() takes each due guild's
    snapshot (propsOf) under the lock and hands it to ONE private writer thread "SkyyGuilds-IO" that writes it OUTSIDE the lock. XP-only
    changes (guild XP, a member's new display name) are flushed at most every 60 s per guild (GuildStore.XP_FLUSH_MS); a guild whose
    write failed is retried by the next tick (urgent). Bank, membership, rank, tag and limit changes are still written AT ONCE by the
    command itself (saveGuild, the write-first rules of 0.1.1 - 0.1.6 unchanged), and shutdown writes every dirty guild synchronously
    after the writer has stopped.
    WRITE ORDER: every guild file write carries a generation (Guild.gen, taken under the GuildStore lock with its snapshot) and is done
    under the guild's own file monitor (Guild.io); a write whose generation is not newer than the one already on disk (Guild.written) is
    skipped, so an older tick snapshot can never land over a newer bank write, the disband file, or (after archive: written = MAX) bring
    an archived guild's file back.
 C. Bridge publishing: guild:info:<uuid> is rebuilt only when what it shows changed (xp, online count, member count, rank, name, tag -
    GuildStore.pubMember; also re-put if the bridge value was removed or replaced). The tick counts each guild's online members ONCE
    (one pass over the online players) instead of once per online member (0.1.6: O(members^2) Universe lookups per tick); addXp
    republishes with that count (live count when none yet).
 D. COIN CALLS OUTSIDE THE GUILD LOCK (deposit / withdraw, the player-driven bank moves): reserve -> call -> commit / rollback.
    deposit: the purse is read (coins:fn:get) before the lock; depositBegin (lock) checks everything 0.1.6 checked and RESERVES (Guild.busy
    + Guild.pendIn, counted against the bank cap); coins:fn:take runs outside the lock; depositEnd (lock) commits (bank + net + log + write,
    0.1.6's order) or, when the take was refused, only releases the reservation. withdraw: withdrawBegin (lock) checks the limits, lowers
    the bank + raises the day count + WRITES (0.1.6's write-first rule) and reserves; coins:fn:add runs outside the lock; withdrawEnd
    (lock) logs + writes, or puts the exact amount and the old day count back and writes again (0.1.6's rollback). While a guild has a
    move in flight (busy > 0) a disband (/guild disband, the last member's leave, /guildadmin delete), a leave and a kick are refused
    with "A guild bank move is in progress ... try again" (nothing changed) - so the guild, the member and the bank a move reserved
    cannot vanish under it. The disband payouts and the leave / kick refunds keep 0.1.6's code (their coin calls stay inside the lock;
    with SkyyCoins 0.1.6 those are memory-only calls).
 E. FIX ROUND (critic findings, 2026-10-13):
    - CRASH WINDOW vs SkyyCoins 0.1.6 write-behind: coinsTake / coinsAdd call coins:fn:flush right after a successful take / add (when
      SkyyCoins offers it; 0.1.5 writes at once anyway), so the purse file is on disk BEFORE the guild bank file is credited (deposit)
      and right after the bank file was debited (withdraw, disband payouts, leave / kick refunds). A hard crash can no longer leave the
      coins in both the purse file and the bank file.
    - WITHDRAW DAY COUNT: a refused coins:fn:add takes back only ITS OWN amount from the member's day count (the exact 0.1.6 restore
      when nothing else changed it meanwhile), so a second withdraw in flight keeps its count.
    - LEVEL CURVE: pubMember also rebuilds guild:info when GCfg.BASE / STEP changed (Server Setup / reload), not only on the next XP.
Rolling back to 0.1.6 is safe (same files, same format; 0.1.6 reads everything 0.1.7 writes).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyGuilds", "build_skyyguilds_0.1.6.py")
dst = os.path.join(ROOT, "SkyyGuilds", "build_skyyguilds_0.1.7.py")
CR, LF = chr(13), chr(10)
raw = open(src, encoding="utf8", newline="").read()
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.1.6"' in s and "GENERATED by tools/guilds_0_1_6_patch.py" in s and "takeFlush" not in s, "the source must be the generated 0.1.6"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:200])
    s = s.replace(old, new)


def rep_m(head, new_src):
    """replace the whole M(gs-like, r'''...''') block whose Java starts with head"""
    global s
    a = s.index(head)
    a = s.rindex('\nM(', 0, a) + 1
    b = s.index('\n}""")', a) + len('\n}""")')
    assert s.count(head) == 1, "method head count %d: %s" % (s.count(head), head)
    s = s[:a] + new_src.strip("\n") + s[b:]


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGuilds 0.1.6 - build script (javassist via jpype). GENERATED by tools/guilds_0_1_6_patch.py from the LIVE 0.1.5
(build_skyyguilds_0.1.5.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyguilds_0.1.6.py          -> SkyyGuilds/SkyyGuilds-0.1.6.jar
''', '''"""SkyyGuilds 0.1.7 - build script (javassist via jpype). GENERATED by tools/guilds_0_1_7_patch.py from the LIVE 0.1.6
(build_skyyguilds_0.1.6.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyguilds_0.1.7.py          -> SkyyGuilds/SkyyGuilds-0.1.7.jar

''' + HEAD[HEAD.index("0.1.7 (2026-10-13)"):].strip() + '''

''')
rep('VERSION = "0.1.6"', 'VERSION = "0.1.7"')
rep('RELOAD="GCfg.reloadAll", KEEP=20,', 'RELOAD="GCfg.reloadAll", KEEP=10,')

# ---------------------------------------------------------------- fields (GMember: last published info; Guild: write order, reservations)
rep('''          "public long contrib;", "public long wdDay;", "public long wdUsed;"):
    F(mem, f)''', '''          "public long contrib;", "public long wdDay;", "public long wdUsed;",
          # 0.1.7 C: what guild:info:<uuid> was last built from (pubMember rebuilds it only when one of these changed)
          "public String pInfo;", "public long pXp;", "public int pOnl;", "public int pSize;", "public int pRank;",
          "public String pGName;", "public String pTag;",
          # 0.1.7 E: the level curve (GCfg.BASE / STEP) the info was built with
          "public long pBase;", "public long pStep;"):
    F(mem, f)''')
rep('''          "public java.util.HashMap net;", "public String netSeed;"):
    F(gld, f)''', '''          "public java.util.HashMap net;", "public String netSeed;",
          # 0.1.7 B: io = this guild's file monitor; gen = the newest snapshot generation (GuildStore lock); written = the generation on
          # disk (io monitor; MAX after archive); urgent = flush at the next tick (a failed write); flushedAt = last snapshot (millis);
          # onl = online members counted by the last tick (-1 = not counted yet). 0.1.7 D: busy = bank moves in flight, pendIn =
          # coins of reserved deposits
          "public Object io;", "public long gen;", "public long written;", "public boolean urgent;", "public long flushedAt;",
          "public int onl;", "public int busy;", "public long pendIn;"):
    F(gld, f)''')
rep('''  this.net = new java.util.HashMap();
  this.netSeed = null;
}""")''', '''  this.net = new java.util.HashMap();
  this.netSeed = null;
  this.io = new Object();
  this.onl = -1;
}""")''')

# ---------------------------------------------------------------- A: lock-free bridge
rep('''M(gs, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")''', '''# 0.1.7 A: lock-free bridge (research/Code-Structure-Audit.md): cached in BRIDGE after the first call; only that call takes the
# System.class monitor (creation exactly as before: get, create if absent, put)
F(gs, "public static volatile java.util.Map BRIDGE;")
# 0.1.7 B: the SkyyGuilds-IO writer (null = not started: the tick writes inline, outside the lock) and the XP flush interval
F(gs, "public static volatile java.util.concurrent.ExecutorService IO;")
F(gs, "public static final long XP_FLUSH_MS = 60000L;")
F(gs, "public static volatile long WRITES = 0L;")
M(gs, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(gs, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")''')

# ---------------------------------------------------------------- C: publish only on change
rep_m('public static synchronized void publishGuild(@PKG@.Guild g) {', r'''
# 0.1.7 C: one member's guild:<uuid> + guild:info:<uuid>, rebuilt only when what the info shows changed (or the bridge lost / replaced
# the value); every caller holds the GuildStore lock
M(gs, r"""
public static void pubMember(java.util.Map b, @PKG@.Guild g, @PKG@.GMember m, int onl) {
  int size = g.members.size();
  String tag = g.tag == null ? "" : g.tag;
  if (m.pInfo != null && m.pXp == g.xp && m.pOnl == onl && m.pSize == size && m.pRank == m.rank && g.name.equals(m.pGName)
      && tag.equals(m.pTag) && m.pBase == @PKG@.GCfg.BASE && m.pStep == @PKG@.GCfg.STEP
      && m.pInfo.equals(b.get("guild:info:" + m.uuid)) && g.name.equals(b.get("guild:" + m.uuid))) return;
  long cb = @PKG@.GCfg.BASE;
  long cs = @PKG@.GCfg.STEP;
  String info = infoString(g, m, onl);
  b.put("guild:" + m.uuid, g.name);
  b.put("guild:info:" + m.uuid, info);
  m.pInfo = info;
  m.pXp = g.xp;
  m.pOnl = onl;
  m.pSize = size;
  m.pRank = m.rank;
  m.pGName = g.name;
  m.pTag = tag;
  m.pBase = cb;
  m.pStep = cs;
}""")
M(gs, r"""
public static synchronized void publishGuildN(@PKG@.Guild g, int onl) {
  if (g == null) return;
  g.onl = onl;
  java.util.Map b = bridge();
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) pubMember(b, g, (@PKG@.GMember) it.next(), onl);
}""")
M(gs, r"""
public static synchronized void publishGuild(@PKG@.Guild g) {
  if (g == null) return;
  publishGuildN(g, onlineCount(g));
}""")''')
rep('''  if (m != null) m.contrib = m.contrib + n;
  g.dirty = true;
  publishGuild(g);''', '''  if (m != null) m.contrib = m.contrib + n;
  g.dirty = true;
  publishGuildN(g, g.onl >= 0 ? g.onl : onlineCount(g));''')
rep_m('public static synchronized boolean touch(java.util.UUID u, String uname) {', r'''
# tick (every 5 s) for each online player: stored name refresh + republish (0.1.7 C: onl = the tick's count of this player's guild,
# -1 = count it here; the info is rebuilt only on change); true = in a guild
M(gs, r"""
public static synchronized boolean touchN(java.util.UUID u, String uname, int onl) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) { unpublish(us); return false; }
  @PKG@.GMember m = g.member(us);
  if (uname != null && uname.length() > 0 && !uname.equals(m.name)) { m.name = uname; g.dirty = true; }
  pubMember(bridge(), g, m, onl >= 0 ? onl : onlineCount(g));
  return true;
}""")
M(gs, r"""
public static boolean touch(java.util.UUID u, String uname) {
  return touchN(u, uname, -1);
}""")
# 0.1.7 C: the tick's per-guild online counts (gid -> Integer; a guild not listed has 0 online)
M(gs, r"""
public static synchronized void setOnline(java.util.HashMap cnt) {
  java.util.Iterator it = GUILDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.Guild g = (@PKG@.Guild) it.next();
    Object c = cnt.get(g.id);
    g.onl = c instanceof Integer ? ((Integer) c).intValue() : 0;
  }
}""")''')
# the tick's comment above touch() moved into the new block
rep('''# tick (every 5 s) for each online player: stored name refresh + republish; true = in a guild
# tick (every 5 s)''', '''# tick (every 5 s)''')

# ---------------------------------------------------------------- B: ordered writes (generation + the guild's own file monitor)
rep_m('public static synchronized boolean saveGuild(@PKG@.Guild g) {', r'''
# 0.1.7 B: one guild file write with generation gen, the caller holds g.io: skipped (null) when the disk already has gen or newer
# (an older tick snapshot never lands over a newer write); else the error text or null
M(gs, r"""
public static String writeGen0(@PKG@.Guild g, java.util.Properties p, long gen, String header) {
  if (gen <= g.written) return null;
  try {
    writeProps(GDIR.resolve(g.id + ".properties"), p, header);
    g.written = gen;
    WRITES = WRITES + 1L;
    return null;
  } catch (Throwable t) { return String.valueOf(t); }
}""")
M(gs, r"""
public static String writeGen(@PKG@.Guild g, java.util.Properties p, long gen, String header) {
  synchronized (g.io) { return writeGen0(g, p, gen, header); }
}""")
M(gs, r"""
public static synchronized boolean saveGuild(@PKG@.Guild g) {
  String err = null;
  try {
    java.util.Properties p = propsOf(g);
    g.gen = g.gen + 1L;
    err = writeGen(g, p, g.gen, "SkyyGuilds guild file - edit only while the server is stopped");
  } catch (Throwable t) { err = String.valueOf(t); }
  if (err == null) {
    g.dirty = false;
    g.urgent = false;
    g.flushedAt = System.currentTimeMillis();
    return true;
  }
  g.dirty = true;
  g.urgent = true;
  warn("could not save guild " + g.id + " (kept in memory, retried every 5 s): " + err);
  return false;
}""")
# 0.1.7 B: the tick's snapshots - every dirty guild that is urgent (a failed write) or whose last snapshot is >= 60 s old (XP-only
# changes); the writes happen OUTSIDE this lock (writeJobs). Object[]{Guild, Properties, Long gen}
M(gs, r"""
public static synchronized java.util.ArrayList takeFlush(long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = GUILDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.Guild g = (@PKG@.Guild) it.next();
    if (!g.dirty) continue;
    if (!g.urgent && now - g.flushedAt < XP_FLUSH_MS) continue;
    try {
      java.util.Properties p = propsOf(g);
      g.gen = g.gen + 1L;
      g.dirty = false;
      g.urgent = false;
      g.flushedAt = now;
      out.add(new Object[] { g, p, Long.valueOf(g.gen) });
    } catch (Throwable t) { warn("could not snapshot guild " + g.id + " (retried): " + t); }
  }
  return out;
}""")
M(gs, r"""
public static synchronized void writeFailed(@PKG@.Guild g, String err) {
  if (GUILDS.get(g.id) == g) { g.dirty = true; g.urgent = true; }
  warn("could not save guild " + g.id + " (kept in memory, retried every 5 s): " + err);
}""")
# runs on SkyyGuilds-IO (or inline on the tick thread when the writer is not running) - never inside the GuildStore lock
M(gs, r"""
public static void writeAll(java.util.ArrayList jobs) {
  for (int i = 0; i < jobs.size(); i++) {
    Object[] j = (Object[]) jobs.get(i);
    @PKG@.Guild g = (@PKG@.Guild) j[0];
    String err = writeGen(g, (java.util.Properties) j[1], ((Long) j[2]).longValue(), "SkyyGuilds guild file - edit only while the server is stopped");
    if (err != null) writeFailed(g, err);
  }
}""")''')

# archive: the final write + move happen under the guild's file monitor and set written = MAX first, so no older snapshot can recreate
# the file after it moved to deleted/
rep_m('public static synchronized boolean archive(@PKG@.Guild g) {', r'''
M(gs, r"""
public static boolean archive0(@PKG@.Guild g, java.util.Properties p, long now) {
  java.nio.file.Path f = GDIR.resolve(g.id + ".properties");
  try {
    g.written = Long.MAX_VALUE;
    writeProps(f, p, "SkyyGuilds guild file - DISBANDED, kept for the record only");
    java.nio.file.Path dd = GDIR.resolve("deleted");
    java.nio.file.Files.createDirectories(dd, new java.nio.file.attribute.FileAttribute[0]);
    replaceFile(f, dd.resolve(g.id + "-" + now + ".properties"));
    return true;
  } catch (Throwable t) {
    warn("could not archive guild file " + g.id + " (if it still exists it is marked disbanded and will not load): " + t);
    return false;
  }
}""")
M(gs, r"""
public static synchronized boolean archive(@PKG@.Guild g) {
  long now = System.currentTimeMillis();
  java.util.Properties p = null;
  try {
    p = propsOf(g);
    p.setProperty("disbanded", String.valueOf(now));
  } catch (Throwable t) {
    warn("could not archive guild file " + g.id + " (if it still exists it is marked disbanded and will not load): " + t);
    return false;
  }
  synchronized (g.io) { return archive0(g, p, now); }
}""")''')
# disbandNow's first write (disbanded, bank 0) goes through the generation too
rep('''    writeProps(GDIR.resolve(g.id + ".properties"), p, "SkyyGuilds guild file - DISBANDED (" + amt + " bank coins paid back to the members by contribution), kept for the record only");''',
    '''    g.gen = g.gen + 1L;
    String derr = writeGen(g, p, g.gen, "SkyyGuilds guild file - DISBANDED (" + amt + " bank coins paid back to the members by contribution), kept for the record only");
    if (derr != null) throw new java.io.IOException(derr);''')

# ---------------------------------------------------------------- D: a bank move in flight blocks disband / leave / kick
rep('''public static synchronized String disbandNow(@PKG@.Guild g, String actorU, String by) {
  long amt = g.bank;''', '''public static synchronized String disbandNow(@PKG@.Guild g, String actorU, String by) {
  if (g.busy > 0) return "-A guild bank move is in progress, so " + g.name + " was NOT disbanded (nothing changed). Try again in a moment.";
  long amt = g.bank;''')
rep('''public static synchronized String leave(java.util.UUID u, String uname, boolean confirmed) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";''', '''public static synchronized String leave(java.util.UUID u, String uname, boolean confirmed) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.busy > 0) return "-A guild bank move is in progress - nothing changed. Try again in a moment.";''')
rep('''public static synchronized String kick(java.util.UUID u, String uname, String who) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";''', '''public static synchronized String kick(java.util.UUID u, String uname, String who) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.busy > 0) return "-A guild bank move is in progress - nothing changed. Try again in a moment.";''')

# ---------------------------------------------------------------- E: coinsTake / coinsAdd make the purse change durable at once
rep('''M(gs, r"""
public static Object coinsTake(java.util.UUID u, long n) {
  try {
    Object f = bridge().get("coins:fn:take");
    if (!(f instanceof java.util.function.Function)) return null;
    return ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
  } catch (Throwable t) { warn("coins:fn:take failed: " + t); return null; }
}""")
M(gs, r"""
public static boolean coinsAdd(java.util.UUID u, long n) {
  try {
    Object f = bridge().get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    return r instanceof Number;
  } catch (Throwable t) { warn("coins:fn:add failed: " + t); return false; }
}""")''', '''# 0.1.7 E: SkyyCoins 0.1.6 writes purses behind (<= 1 s); coins:fn:flush writes them NOW. Called after every successful take / add
# so the purse file is on disk before (deposit) / right after (withdraw, payouts, refunds) the guild file - a hard crash can no longer
# leave the coins on both sides. Absent (SkyyCoins 0.1.5 writes at once) = nothing to do; a failure only logs (SkyyCoins retries).
M(gs, r"""
public static void coinsFlush() {
  try {
    Object f = bridge().get("coins:fn:flush");
    if (!(f instanceof java.util.function.Function)) return;
    Object r = ((java.util.function.Function) f).apply(null);
    if (r instanceof Number && ((Number) r).intValue() < 0) warn("coins:fn:flush could not write the purse yet (SkyyCoins retries every second)");
  } catch (Throwable t) { warn("coins:fn:flush failed: " + t); }
}""")
M(gs, r"""
public static Object coinsTake(java.util.UUID u, long n) {
  try {
    Object f = bridge().get("coins:fn:take");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    if (Boolean.TRUE.equals(r)) coinsFlush();
    return r;
  } catch (Throwable t) { warn("coins:fn:take failed: " + t); return null; }
}""")
M(gs, r"""
public static boolean coinsAdd(java.util.UUID u, long n) {
  try {
    Object f = bridge().get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    if (r instanceof Number) coinsFlush();
    return r instanceof Number;
  } catch (Throwable t) { warn("coins:fn:add failed: " + t); return false; }
}""")''')

# ---------------------------------------------------------------- D: deposit = read purse -> begin (reserve) -> take -> end (commit)
rep_m('public static synchronized String deposit(java.util.UUID u, String uname, String amountText) {', r'''
# 0.1.7 D: the checks of 0.1.6's deposit + a reservation (busy, pendIn counted against the bank cap); String = refused, nothing moved;
# Object[]{Guild, Long n} = reserved. purse = coins:fn:get read by the caller OUTSIDE this lock
M(gs, r"""
public static synchronized Object depositBegin(java.util.UUID u, String uname, String amountText, Long purse) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (!coinsReady()) return "-SkyyCoins is not loaded, so the guild bank cannot move coins.";
  if (purse == null) return "-Your purse cannot be read right now - nothing moved. Try again.";
  long n;
  try { n = parseAmount(amountText, purse.longValue()); }
  catch (Throwable t) { return "-That is not an amount. Use e.g. 500, 2k, 1.5m or all."; }
  if (n <= 0L) return "-Nothing to deposit (your purse has " + purse + " coins).";
  if (n > purse.longValue()) return "-Not enough coins in your purse (" + purse + ").";
  if (g.bank > @PKG@.GCfg.MAX_BANK - n - g.pendIn) return "-The guild bank can hold at most " + @PKG@.GCfg.MAX_BANK + " coins (it has " + g.bank + ").";
  g.busy = g.busy + 1;
  g.pendIn = g.pendIn + n;
  return new Object[] { g, Long.valueOf(n) };
}""")
# 0.1.7 D: after coins:fn:take (r) - the reservation is released; a TRUE take is committed exactly as 0.1.6 did it (bank, net, log,
# write, broadcast). The guild still exists: disbandNow refuses while busy. String[1] = the result, String[2] = {before, after} the purse
M(gs, r"""
public static synchronized String[] depositEnd(java.util.UUID u, String uname, @PKG@.Guild g, long n, Object r) {
  g.busy = g.busy - 1;
  g.pendIn = g.pendIn - n;
  String us = u.toString();
  if (!(r instanceof Boolean)) return new String[] { "-SkyyCoins could not take the coins (purse unreadable?) - nothing moved." };
  if (!((Boolean) r).booleanValue()) return new String[] { "-Not enough coins in your purse." };
  g.bank = g.bank + n;
  netAdd(g, us, n, 0L);
  addLog(g, uname, "deposit", n);
  saveGuild(g);
  broadcast(g, "[Guild] " + uname + " deposited " + n + " coins. Guild bank: " + g.bank + ".", "#ffd070", us);
  return new String[] { "+Deposited " + n + " coins. Guild bank: " + g.bank + " - your purse: ", "." };
}""")
# deposit: take from the purse FIRST (coins:fn:take must say TRUE), then add to the bank - 0.1.7: every coin call outside the lock
M(gs, r"""
public static String deposit(java.util.UUID u, String uname, String amountText) {
  Long purse = null;
  if (coinsReady() && gidOf(u.toString()) != null) purse = coinsGet(u);
  Object b = depositBegin(u, uname, amountText, purse);
  if (!(b instanceof Object[])) return (String) b;
  Object[] a = (Object[]) b;
  @PKG@.Guild g = (@PKG@.Guild) a[0];
  long n = ((Long) a[1]).longValue();
  Object r = null;
  try { r = coinsTake(u, n); } catch (Throwable t) { r = null; }
  String[] e = depositEnd(u, uname, g, n, r);
  if (e.length == 1) return e[0];
  Long after = coinsGet(u);
  return e[0] + (after == null ? "?" : String.valueOf(after)) + e[1];
}""")''')
rep('''# deposit: take from the purse FIRST (coins:fn:take must say TRUE), then add to the bank
# 0.1.7 D:''', '''# 0.1.7 D:''')

# ---------------------------------------------------------------- D: withdraw = begin (write-first + reserve) -> add -> end
rep_m('public static synchronized String withdraw(java.util.UUID u, String uname, String amountText) {', r'''
# 0.1.7 D: 0.1.6's withdraw up to its write-first save (limits, lower bank + raised day count WRITTEN, restored on a failed write) + a
# reservation (busy). String = refused, nothing moved; Object[]{Guild, GMember, Long n, Long oldDay, Long oldUsed, Long lim} = reserved
M(gs, r"""
public static synchronized Object withdrawBegin(java.util.UUID u, String uname, String amountText) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  @PKG@.GMember me = g.member(us);
  long lim = limitFor(g, me.rank);
  if (lim == 0L) return "-" + rankPlural(me.rank) + " can't withdraw from the guild bank (daily limit 0). The Leader can set one with /guild bank limit " + (me.rank == 1 ? "admin" : "member") + " <amount>.";
  if (!coinsReady()) return "-SkyyCoins is not loaded, so the guild bank cannot move coins.";
  long day = day();
  if (lim > 0L && day < 0L) return "-The game day is " + dayUnknownText() + ", so limited withdrawals wait. Try again in a few seconds.";
  long used = usedToday(me, day);
  long left = lim > 0L ? lim - used : Long.MAX_VALUE;
  if (left < 0L) left = 0L;
  if (lim > 0L && left == 0L) return "-You reached today's withdraw limit (" + num(used) + " / " + num(lim) + " coins). It starts again on the next game day.";
  long cap = g.bank < left ? g.bank : left;
  long n;
  try { n = parseAmount(amountText, cap); }
  catch (Throwable t) { return "-That is not an amount. Use e.g. 500, 2k, 1.5m or all."; }
  if (n <= 0L) return "-Nothing to withdraw (the guild bank has " + g.bank + " coins).";
  if (n > g.bank) return "-The guild bank only has " + g.bank + " coins.";
  if (lim > 0L && n > left) return "-You can take " + num(left) + " more coins today (" + num(used) + " / " + num(lim) + "). The count starts again on the next game day.";
  long oldDay = me.wdDay;
  long oldUsed = me.wdUsed;
  g.bank = g.bank - n;
  netAdd(g, us, 0L, n);
  if (day >= 0L) { me.wdDay = day; me.wdUsed = used + n; }
  if (!saveGuild(g)) {
    g.bank = g.bank + n;
    netAdd(g, us, 0L, -n);
    me.wdDay = oldDay;
    me.wdUsed = oldUsed;
    return "-The guild file could not be written - nothing moved (guild bank: " + g.bank + "). Try again.";
  }
  g.busy = g.busy + 1;
  return new Object[] { g, me, Long.valueOf(n), Long.valueOf(oldDay), Long.valueOf(oldUsed), Long.valueOf(lim), Long.valueOf(day), Long.valueOf(me.wdUsed) };
}""")
# 0.1.7 D: after coins:fn:add (ok) - 0.1.6's tail: a refused add puts the exact amount and the old day count back and writes again
# (0.1.7 E: the exact 0.1.6 restore when the count is still what begin set; else - another withdraw of the same member raised it
# meanwhile - only this withdraw's n is taken off the same day's count);
# else the log line + write + broadcast. String[1] = the result, String[2] = {before, after} the purse
M(gs, r"""
public static synchronized String[] withdrawEnd(java.util.UUID u, String uname, Object[] a, boolean ok) {
  @PKG@.Guild g = (@PKG@.Guild) a[0];
  @PKG@.GMember me = (@PKG@.GMember) a[1];
  long n = ((Long) a[2]).longValue();
  long lim = ((Long) a[5]).longValue();
  g.busy = g.busy - 1;
  String us = u.toString();
  if (!ok) {
    g.bank = g.bank + n;
    netAdd(g, us, 0L, -n);
    long day = ((Long) a[6]).longValue();
    if (me.wdDay == day && me.wdUsed == ((Long) a[7]).longValue()) {
      me.wdDay = ((Long) a[3]).longValue();
      me.wdUsed = ((Long) a[4]).longValue();
    } else if (day >= 0L && me.wdDay == day) {
      me.wdUsed = me.wdUsed - n;
      if (me.wdUsed < 0L) me.wdUsed = 0L;
    }
    saveGuild(g);
    warn("withdraw of " + n + " for " + uname + " (" + us + ") from " + g.id + " refused by SkyyCoins - bank restored to " + g.bank);
    return new String[] { "-SkyyCoins could not put the coins in your purse - nothing moved (guild bank: " + g.bank + ")." };
  }
  addLog(g, uname, "withdraw", n);
  saveGuild(g);
  broadcast(g, "[Guild] " + uname + " withdrew " + n + " coins. Guild bank: " + g.bank + ".", "#ffd070", us);
  String lt = lim > 0L ? " Today: " + num(me.wdUsed) + " / " + num(lim) + " (" + dayText() + ")." : "";
  return new String[] { "+Withdrew " + n + " coins. Guild bank: " + g.bank + " - your purse: ", "." + lt };
}""")
# withdraw: (0.1.1) the rank's daily limit is checked first; then the lower bank AND the member's raised day count are WRITTEN first
# (a failed write = nothing moved, both restored), then coins:fn:add; if SkyyCoins did not add, the exact amount and the old day count
# go back and are written again. The file never shows coins that already left the bank. 0.1.7: coins:fn:add runs outside the lock.
M(gs, r"""
public static String withdraw(java.util.UUID u, String uname, String amountText) {
  Object b = withdrawBegin(u, uname, amountText);
  if (!(b instanceof Object[])) return (String) b;
  Object[] a = (Object[]) b;
  boolean ok = false;
  try { ok = coinsAdd(u, ((Long) a[2]).longValue()); } catch (Throwable t) { ok = false; }
  String[] e = withdrawEnd(u, uname, a, ok);
  if (e.length == 1) return e[0];
  Long after = coinsGet(u);
  return e[0] + (after == null ? "?" : String.valueOf(after)) + e[1];
}""")''')
rep('''# withdraw: (0.1.1) the rank's daily limit is checked first; then the lower bank AND the member's raised day count are WRITTEN first
# (a failed write = nothing moved, both restored), then coins:fn:add; if SkyyCoins did not add, the exact amount and the old day count
# go back and are written again. The file never shows coins that already left the bank.
# 0.1.7 D:''', '''# 0.1.7 D:''')

# ---------------------------------------------------------------- B + C: the tick (count online per guild once; snapshots -> writer)
rep('''    java.util.HashSet online = new java.util.HashSet();
    java.util.HashMap refs = new java.util.HashMap();
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      refs.put(u, pr);
      boolean member = false;
      try { member = @PKG@.GuildStore.touch(u, pr.getUsername()); } catch (Throwable t) { }
      if (member && poll) dispatch(pr);
    }''', '''    java.util.HashSet online = new java.util.HashSet();
    java.util.HashMap refs = new java.util.HashMap();
    java.util.ArrayList order = new java.util.ArrayList();
    java.util.HashMap cnt = new java.util.HashMap();
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      if (!online.add(u)) continue;
      refs.put(u, pr);
      order.add(pr);
      String gid = @PKG@.GuildStore.gidOf(u.toString());
      if (gid != null) {
        Object c = cnt.get(gid);
        cnt.put(gid, Integer.valueOf((c instanceof Integer ? ((Integer) c).intValue() : 0) + 1));
      }
    }
    try { @PKG@.GuildStore.setOnline(cnt); } catch (Throwable t) { }
    for (int i = 0; i < order.size(); i++) {
      @PR@ pr = (@PR@) order.get(i);
      java.util.UUID u = pr.getUuid();
      String gid = @PKG@.GuildStore.gidOf(u.toString());
      Object c = gid == null ? null : cnt.get(gid);
      boolean member = false;
      try { member = @PKG@.GuildStore.touchN(u, pr.getUsername(), c instanceof Integer ? ((Integer) c).intValue() : -1); } catch (Throwable t) { }
      if (member && poll) dispatch(pr);
    }''')
rep('''    @PKG@.GuildStore.flushDirty();
    if (@PKG@.XpTask.BASE.size() > 20000)''', '''    @PKG@.GuildStore.submitWrites(@PKG@.GuildStore.takeFlush(now));
    if (@PKG@.XpTask.BASE.size() > 20000)''')

# the writer (Runnable + its ThreadFactory) and the submit / stop helpers; compiled before GuildTick (the tick calls submitWrites)
rep('''# ================= GuildTick (scheduler, every 5 s) =================''', '''# ================= 0.1.7 B: GWriter - the SkyyGuilds-IO thread (one daemon thread) and its job (a list of tick snapshots) =================
gwr = pool.makeClass(PKG + ".GWriter")
ALL.append(gwr)
gwr.addInterface(pool.get("java.lang.Runnable"))
gwr.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
F(gwr, "public java.util.ArrayList jobs;")
C(gwr, "public GWriter(java.util.ArrayList jobs) { this.jobs = jobs; }")
M(gwr, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyGuilds-IO");
  t.setDaemon(true);
  return t;
}""")
M(gwr, r"""
public void run() {
  try { if (this.jobs != null) @PKG@.GuildStore.writeAll(this.jobs); } catch (Throwable t) { @PKG@.GuildStore.warn("guild writer failed: " + t); }
}""")
M(gs, r"""
public static void submitWrites(java.util.ArrayList jobs) {
  if (jobs == null || jobs.size() == 0) return;
  java.util.concurrent.ExecutorService e = IO;
  if (e != null) {
    try { e.execute(new @PKG@.GWriter(jobs)); return; } catch (Throwable t) { }
  }
  writeAll(jobs);
}""")
M(gs, r"""
public static void stopIO() {
  java.util.concurrent.ExecutorService e = IO;
  IO = null;
  if (e == null) return;
  try { e.shutdown(); e.awaitTermination(10L, java.util.concurrent.TimeUnit.SECONDS); } catch (Throwable t) { }
}""")

# ================= GuildTick (scheduler, every 5 s) =================''')
rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.GuildTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);''',
    '''  @PKG@.GuildStore.IO = java.util.concurrent.Executors.newSingleThreadExecutor(new @PKG@.GWriter(null));
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.GuildTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);''')
rep('''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.GuildStore.flushDirty(); } catch (Throwable t) { }''', '''  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.GuildStore.stopIO(); } catch (Throwable t) { }
  try { @PKG@.GuildStore.flushDirty(); } catch (Throwable t) { }''')

assert "synchronized (java.lang.System.class) {\n" not in s, "no old-style bridge left"
assert not os.path.exists(dst), dst + " already exists - delete it first (it is generated)"
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
