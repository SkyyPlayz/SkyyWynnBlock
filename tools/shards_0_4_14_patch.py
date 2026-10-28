"""Derive SkyyShards/build_skyyshards_0.4.14.py from the GENERATED SkyyShards 0.4.13 (build_skyyshards_0.4.13.py = the tools/deploy_set.py SET
pin, made by tools/shards_0_4_13_patch.py - edit the patch, never the generated file). Every anchor is asserted once; at the end every change
is undone on a copy and compared with 0.4.13 (tools/soundpass_gen.Patch). Line endings kept.
Run:   python tools/shards_0_4_14_patch.py   then   python SkyyShards/build_skyyshards_0.4.14.py   (never --deploy)
Check: python SkyyShards/test_skyyshards_0.4.14.py

0.4.14 (2026-10-27) = LOCK DISCIPLINE: NO OTHER MOD IS EVER CALLED WHILE THE SHARD DATA LOCK IS HELD (RESUME queue items 1, 2 + 4;
  Skyy 2026-10-27: "sounds good" + "work through your whole que"). The 2026-10-25 02:38 island freeze was a world thread stuck on
  ShStore.LOCK while its holder sat inside another mod's bridge; 0.4.13 made the lock timed (the safety net, kept) - 0.4.14 removes the cause.
  1. PAY OUTSIDE, RECORD UNDER THE LOCK. Every cost path - Storage / Auto-Compactor / Time Compressor (purchase), Grow / island / sub-upgrade
     / Automation / Offline Harvest (purchaseM), Add modifier, Add booster, a placed totem's Tier up, the Totem Bench upgrade, Craft (a
     shard's crafted mark) - now runs: DECIDE under the lock (the checks + a reservation: ShStore.ver(k), the profile file's save counter,
     or the totem entry exactly as checked) -> PAY with the lock released (inventory + SkyySacks take, SkyyCoins take) -> COMMIT under the
     lock (the reservation must still hold: same save counter / same entry; settle, write, save) -> COMMIT THE BAG PART or REFUND with the
     lock released again. A busy lock at the commit (ShBusy, 50 ms on a world thread) or a profile that changed meanwhile = EVERYTHING
     BACK (inventory, bags, coins) and the click says so; nothing is ever both kept and paid, nothing paid is ever dropped. grow0 asks
     SkyyCollections (collTier) between two short locks instead of unlocking in the middle; craft asks SkyyProfiles (pkey) before any lock.
  2. ISLANDS ASKED BEFORE THE LOCK. ShPlace.decide (placing a shard) and ShDoor.door (shard:fn:door, called BY SkyyIslands) read the
     "placed" record, ask island:world:key:fn (ShRole.stale) with the lock released, then re-check the record under the lock (it changed
     meanwhile = treated as not stale - the old, safe answer). The totem page asks SkyyArmory (costAt -> essence) after its lock.
  3. THE COLLECT CREDITS (owed / owedXp, the re-review 10-27 LOW): the file's waiting count is RESERVED first - taken out of the collector's
     file and saved under the lock - then paid to SkyyCollections / SkyySkills with the lock released; only a refused part is written
     back (lock busy / save refused = memory, MEM_OWED). A busy lock after paying + a server restart can never pay a credit twice (the
     file no longer holds it). ShTick (our own thread, 1.5 s lock wait) moves memory credits back into the file every second, and the
     plugin shutdown does it once more - a clean restart loses nothing either. MEM_OWED updates are atomic (memAdd).
     AT MOST ONCE, ON PURPOSE (fixer, critics 10-27): a HARD kill (crash / power loss) between the reserve's save and the payment loses that
     one waiting credit instead of paying it twice; every reserve writes "RESERVED" to collect.log and the payment "PAID" right after, so an
     admin can see a RESERVED line with no PAID line after a crash and give it by hand. (ShPay.coll / xp catch every Throwable, so a bridge
     that throws is a refusal - written back - not a loss.)
  4. A RUNTIME GUARD: every bridge lookup (ShCfg.fn / fnT / ShPay.f) checks ShStore.LOCK.isHeldByCurrentThread(); a hit counts in
     ShCfg.UNDER (+ UNDER_LAST) and WARNs once per bridge key - the harness runs every action with it and expects 0.
  5. THE SHARED EXECUTOR (queue item 4): SkyyShards runs nothing on HytaleServer.SCHEDULED_EXECUTOR since 0.4.13 (ShTick = its own daemon
     thread SkyyShards-tick); the flush in 3. runs on our own thread. Fixer (critic 10-27): Enter Shard's world-load callback (ShHop.accept)
     ran on WHICHEVER thread finished the engine's world load and there read the profile + took the shard lock for the paint prep (1.5 s
     wait off a world thread) - it now only hops: the profile read + the paint prep run on the shard world's own thread (ShHop.paintNow),
     the teleport on the player's world thread as before. ShOpened (the other load callback) takes no lock. Paints / chunk loads already
     completed on world threads (ShFill.accept -> world.execute).
  6. SMALL COSTS (fixer): a Combat totem's essence is asked from SkyyArmory at most once a minute per tier (ESS_AT; a new bridge function =
     asked again), not 5-6 times on every page fill; flushOwed retries a credit whose collector file is unreadable once a minute, not
     every second.
  7. FIXER 2 (re-critics 10-27): Enter Shard's paint step (ShHop.paintNow) takes the lock around the profile read AND ShFill.region, so a
     busy lock always tells the player instead of reaching paintAsync's catch-all (which completed the paint = a teleport into an unpainted
     region). owed / owedXp skip the reserve when SkyyCollections (coll:fn:add) / SkyySkills (skill:fn:addxp) is absent: nothing could be
     paid, so the file part stays in the file (one save, no RESERVED / PAID lines, no backlog at risk). The new timings (50 ms commit wait,
     ESS_AT 60 s, BAD_TRY 60 s) are internal safety timings, deliberately not in Server Setup.
  NOT in this round: payInvBags through sacks:fn:takeOpen (the Sacks bridge is being built; a later Shards round adopts it).
  SAVED DATA: no format change, no migration. ROLLBACK 0.4.14 -> 0.4.13: alone (no data or config change).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

HERE = os.path.join(ROOT, "SkyyShards")
P = G.Patch(os.path.join(HERE, "build_skyyshards_0.4.13.py"), os.path.join(HERE, "build_skyyshards_0.4.14.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.4.13"\n') and P.has("GENERATED by tools/shards_0_4_13_patch.py") and not P.has("commitKeys"), "not the generated SkyyShards 0.4.13"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.4.14 (2026-10-27)"):].rstrip() + "\n"


def block(header, cls=None):
    """the whole M(<cls>, r\"\"\" ... }\"\"\")\\n block whose method header line is `header` (asserted once)"""
    assert P.s.count(header) == 1, ("header", P.s.count(header), header[:90])
    h = P.s.index(header)
    a = P.s.rindex("M(", 0, h)
    assert P.s[a:h].endswith('r"""\n'), P.s[a:h]
    if cls:
        assert P.s[a:h] == 'M(%s, r"""\n' % cls, P.s[a:h]
    e = P.s.index('}""")', h)
    e = P.s.index("\n", e) + 1   # the block's line, a trailing comment included
    return P.s[a:e]


def rep_in(header, pairs, cls=None):
    """local edits inside one method block (each old text asserted once in that block)"""
    b = block(header, cls)
    n = b
    for o, w in pairs:
        assert n.count(o) == 1, ("in", header[:60], n.count(o), o[:120])
        n = n.replace(o, w, 1)
    P.rep(b, n)


# ---------------------------------------------------------------------------------------------------- 0. header + version
P.rep('''"""SkyyShards 0.4.13 - build script (javassist via jpype). GENERATED by tools/shards_0_4_13_patch.py from build_skyyshards_0.4.12.py
(generated by tools/shards_0_4_12_patch.py from 0.4.11, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.13" / "0.4.12" / "0.4.11" / "0.4.10" / "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.13.py   -> SkyyShards/SkyyShards-0.4.13.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.13.py
''', '''"""SkyyShards 0.4.14 - build script (javassist via jpype). GENERATED by tools/shards_0_4_14_patch.py from build_skyyshards_0.4.13.py
(generated by tools/shards_0_4_13_patch.py from 0.4.12, ... back to tools/shards_0_4_patch.py from 0.3.2; edit the patch, never this file).
Changes are marked "0.4.14" / "0.4.13" / "0.4.12" / "0.4.11" / "0.4.10" / "0.4.9" / "0.4.8" / "0.4.7" / "0.4.6" / "0.4.5" / "0.4.4" / "0.4.3" / "0.4.2" / "0.4.1" / "0.4".
Run:   python SkyyShards/build_skyyshards_0.4.14.py   -> SkyyShards/SkyyShards-0.4.14.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.4.14.py
''' + NOTE + '''
0.4.13 notes:
''')
P.rep('VERSION = "0.4.13"\n', 'VERSION = "0.4.14"\n')

# ---------------------------------------------------------------------------------------------------- 4. the runtime guard (ShCfg.under)
P.rep('''M(cfg, r"""
public static java.util.function.Function fn(String key) {
  Object o = bridge().get(key);
  return o instanceof java.util.function.Function ? (java.util.function.Function) o : null;
}""")''', '''F(cfg, "public static final java.util.concurrent.atomic.AtomicLong UNDER = new java.util.concurrent.atomic.AtomicLong();")   # 0.4.14: bridge lookups while holding ShStore.LOCK (must stay 0)
F(cfg, 'public static volatile String UNDER_LAST = "";')
M(cfg, "public static void under(String key) { }")   # 0.4.14: the body is set below (after ShStore: it reads ShStore.LOCK)
M(cfg, r"""
public static java.util.function.Function fn(String key) {
  under(key);   // 0.4.14: never while holding the shard data lock
  Object o = bridge().get(key);
  return o instanceof java.util.function.Function ? (java.util.function.Function) o : null;
}""")
M(cfg, r"""
public static java.util.function.Function fnT(java.util.function.Function t, String key) {
  if (t == null) return fn(key);
  under(key);
  return t;
}""")   # 0.4.14: a harness stand-in or the bridge - the guard counts both''')
_TP = re.compile(r"([A-Za-z@.]*_TEST) != null \? \1 : (?:@PKG@\.ShCfg\.)?fn\(")
_hits = list(_TP.finditer(P.s))
assert len(_hits) == 9, len(_hits)
for _m in reversed(_hits):   # every "X_TEST != null ? X_TEST : fn(" -> fnT(X_TEST, (each line asserted once)
    _ls = P.s.rindex("\n", 0, _m.start()) + 1
    _le = P.s.index("\n", _m.end())
    _line = P.s[_ls:_le]
    P.rep(_line + "\n", _line.replace(_m.group(0), "@PKG@.ShCfg.fnT(" + _m.group(1) + ", ") + "\n")
P.rep('''public static java.util.function.Function f(String key) {
  java.util.Map t = TEST_FNS;''', '''public static java.util.function.Function f(String key) {
  @PKG@.ShCfg.under(key);   // 0.4.14: the guard
  java.util.Map t = TEST_FNS;''')

# ---------------------------------------------------------------------------------------------------- 1. the reservation: the profile file's save counter
P.rep('''# null = written; else the reason. An unreadable file is never overwritten.''', '''F(st, "public static final java.util.concurrent.ConcurrentHashMap VER = new java.util.concurrent.ConcurrentHashMap();")   # 0.4.14: profile -> Long saves so far (memory only)
M(st, r"""
public static long ver(String k) {
  Object o = k == null ? null : VER.get(k);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")   # 0.4.14: a decision made at ver(k) still holds while ver(k) is unchanged (every save counts)
# null = written; else the reason. An unreadable file is never overwritten.''')
P.rep('''    moveInto(tmp, DIR.resolve(k + ".properties"));
    WRITES.incrementAndGet();
    return null;''', '''    moveInto(tmp, DIR.resolve(k + ".properties"));
    WRITES.incrementAndGet();
    VER.put(k, Long.valueOf(ver(k) + 1L));   // 0.4.14 (save is synchronized: one writer at a time)
    return null;''')
P.rep('''st.getDeclaredMethod("migrate").setBody(jv(r"""{''', '''cfg.getDeclaredMethod("under").setBody(jv(r"""{
  if (@PKG@.ShStore.LOCK.isHeldByCurrentThread()) {
    UNDER.incrementAndGet();
    UNDER_LAST = $1;
    warnOnce("under:" + $1, "a cross-mod call (" + $1 + ") ran while holding the shard data lock - 0.4.14 never should; please report it (logged once per bridge)");
  }
}"""))   # 0.4.14: the runtime guard (see the patch note 4)
st.getDeclaredMethod("migrate").setBody(jv(r"""{''')

# ---------------------------------------------------------------------------------------------------- 3. the Collect credits: reserve, pay, write back what was refused
P.rep('''M(core, r"""
public static long memTake(String ck, String key) {''', '''M(core, r"""
public static void memAdd(String mk, long v) {
  if (v == 0L) return;
  for (int i = 0; i < 1000; i++) {
    Object o = MEM_OWED.get(mk);
    if (o == null) { if (MEM_OWED.putIfAbsent(mk, Long.valueOf(v)) == null) return; continue; }
    long nv = ((Long) o).longValue() + v;
    if (nv == 0L) { if (MEM_OWED.remove(mk, o)) return; }
    else if (MEM_OWED.replace(mk, o, Long.valueOf(nv))) return;
  }
  @PKG@.ShCfg.warn("a waiting collection / XP credit could not be kept in memory (" + mk + " " + v + ") - collect.log");
  @PKG@.ShStore.log(mk + " " + v + " LOST (memory update kept failing)");
}""")   # 0.4.14: atomic (the tick thread flushes MEM_OWED while world threads add to it)
M(core, r"""
public static long memTake(String ck, String key) {''')
P.rep(block("public static void memKeep(String ck, String key, long left, java.util.UUID u) {", "core"), '''M(core, r"""
public static void memKeep(String ck, String key, long left, java.util.UUID u) {
  if (left <= 0L) return;
  memAdd(ck + "|" + key, left);   // 0.4.14: atomic
  @PKG@.ShCfg.warnOnce("memowed:" + ck, "the collector file of " + ck + " could not be read - " + key + " " + left + " waits in memory until the next Collect (collect.log)");
  @PKG@.ShStore.log(u + " " + ck + " " + key + " " + left + " WAITS IN MEMORY (collector file unreadable)");
}""")
''')
P.rep(block("public static void memAdj(String ck, String key, long d, java.util.UUID u) {", "core"), '''M(core, r"""
public static void memAdj(String ck, String key, long d, java.util.UUID u) {
  if (d == 0L) return;
  memAdd(ck + "|" + key, d);   // 0.4.14: atomic
  @PKG@.ShStore.log(u + " " + ck + " " + key + " " + d + " KEPT IN MEMORY (shard data busy) - settled on the next Collect or moved into the file within a second");
}""")   # 0.4.13 review: the busy-lock twin of memKeep
''')
P.rep('''# the collection credit for `add` new items of `item` + whatever waited from earlier refusals (owed.coll.<item> in the COLLECTOR's file)''',
      '''# 0.4.14: the file's waiting count of `key` TAKEN OUT of the collector's file (saved) under the lock before it is paid with the lock released:
# a busy write-back + a restart can never pay it twice. -1 = the lock was busy (nothing taken), else the amount reserved (a refused save
# = 0: it stays in the file for a later Collect)
M(core, r"""
public static long reserve(String ck, java.util.Properties q, String key) {
  if (q == null) return 0L;
  try { @PKG@.ShStore.LOCK.lock(); } catch (@PKG@.ShBusy b) { return -1L; }
  try {
    long fh = @PKG@.ShStore.lng(q, key, 0L);
    if (fh <= 0L) return 0L;
    q.remove(key);
    String e = @PKG@.ShStore.save(ck, q);
    if (e == null) { @PKG@.ShStore.log(ck + " " + key + " " + fh + " RESERVED (taken out of the collector file to be paid now - no PAID line after it = lost in a crash, give it by hand)"); return fh; }   // fixer: at most once, visible
    q.setProperty(key, String.valueOf(fh));
    @PKG@.ShCfg.warnOnce("reserve:" + ck, "the waiting credit of " + ck + " could not be taken out of its file (" + e + ") - it stays there for a later Collect (logged once)");
    return 0L;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# 0.4.14: what a bridge refused goes back into the file (added to whatever is there); busy lock / refused save = memory (moved into the file
# by the tick within a second)
M(core, r"""
public static void back(String ck, java.util.Properties q, String key, long left, java.util.UUID u) {
  if (left <= 0L) return;
  if (q == null) { memKeep(ck, key, left, u); return; }
  boolean lk = false;
  try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { lk = false; }
  if (!lk) { memAdj(ck, key, left, u); return; }
  String e = null;
  try {
    long had = @PKG@.ShStore.lng(q, key, 0L);
    q.setProperty(key, String.valueOf(had + left));
    e = @PKG@.ShStore.save(ck, q);
    if (e != null) { if (had > 0L) q.setProperty(key, String.valueOf(had)); else q.remove(key); }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (e != null) { @PKG@.ShCfg.warn("a waiting credit (" + key + ") could not be saved: " + e + " - it waits in memory"); memAdj(ck, key, left, u); }
}""")
# 0.4.14: memory credits -> their collector files (ShTick every second on OUR thread + the plugin shutdown; a busy lock = next time).
# Each unit is in exactly one place: memory (removed atomically before it is written) or the file. Fixer: an unreadable collector file
# (ShStore.BAD) is tried again once a minute (BAD_TRY), not re-read every second.
F(core, "public static volatile long BAD_TRY;")   # 0 = never tried (no initialiser: <clinit> unchanged)
M(core, r"""
public static int flushOwed() {
  if (MEM_OWED.isEmpty() || @PKG@.ShStore.DIR == null) return 0;
  int n = 0;
  long t0 = System.currentTimeMillis();
  boolean retry = t0 - BAD_TRY >= 60000L;
  boolean tried = false;
  java.util.Iterator it = new java.util.ArrayList(MEM_OWED.keySet()).iterator();
  while (it.hasNext()) {
    String mk = (String) it.next();
    int bar = mk.indexOf('|');
    if (bar <= 0) continue;
    String ck = mk.substring(0, bar);
    String key = mk.substring(bar + 1);
    if (@PKG@.ShStore.BAD.containsKey(ck)) { if (!retry) continue; tried = true; }   // fixer: once a minute
    java.util.Properties q;
    try { q = @PKG@.ShStore.get(ck); } catch (@PKG@.ShBusy b) { continue; }
    if (q == null) continue;   // unreadable: it waits in memory (memKeep said so)
    boolean lk = false;
    try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { lk = false; }
    if (!lk) continue;
    long v = 0L;
    String e = null;
    try {
      Object o = MEM_OWED.remove(mk);
      v = o instanceof Long ? ((Long) o).longValue() : 0L;
      if (v > 0L) {
        long had = @PKG@.ShStore.lng(q, key, 0L);
        q.setProperty(key, String.valueOf(had + v));
        e = @PKG@.ShStore.save(ck, q);
        if (e != null) { if (had > 0L) q.setProperty(key, String.valueOf(had)); else q.remove(key); }
      }
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (v < 0L || e != null) { memAdd(mk, v); continue; }
    if (v > 0L) { n++; @PKG@.ShStore.log(ck + " " + key + " " + v + " moved from memory into the collector file"); }
  }
  if (tried) BAD_TRY = t0;
  return n;
}""")
# the collection credit for `add` new items of `item` + whatever waited from earlier refusals (owed.coll.<item> in the COLLECTOR's file)''')
P.rep(block("public static long owed(java.util.UUID u, String item, long add) {", "core"), '''M(core, r"""
public static long owed(java.util.UUID u, String item, long add) {
  String ck = @PKG@.ShCfg.pkey(u);
  java.util.Properties q;
  try { q = @PKG@.ShStore.get(ck); } catch (@PKG@.ShBusy b0) { q = null; }   // 0.4.13 review: a busy first load = this credit waits in memory
  long due = add;
  String key = "owed.coll." + item;
  due += memTake(ck, key);   // fix2
  if (@PKG@.ShPay.f("coll:fn:add") == null) {   // fixer 2: SkyyCollections absent / too old = nothing can be paid: the file part stays put (no reserve, no log lines)
    long fh0 = q == null ? 0L : @PKG@.ShStore.lng(q, key, 0L);
    back(ck, q, key, due, u);
    return due + fh0 > 0L ? due + fh0 : 0L;
  }
  long fh = reserve(ck, q, key);   // 0.4.14: the file's part leaves the file BEFORE it is paid (never twice after a restart)
  if (fh < 0L) { memAdj(ck, key, due, u); return due > 0L ? due : 0L; }   // 0.4.13 review: busy = all of it waits
  due += fh;
  if (due <= 0L) return 0L;
  long done = @PKG@.ShPay.coll(u, item, due);   // 0.4.14: SkyyCollections with the shard lock released
  long left = due - done;
  if (fh > 0L) @PKG@.ShStore.log(ck + " " + key + " PAID " + done + " of " + due + " (" + fh + " reserved)" + (left > 0L ? " - " + left + " go back" : ""));   // fixer: closes the RESERVED line
  back(ck, q, key, left, u);   // 0.4.14: only a refused part goes back (file, else memory)
  return left;
}""")
''')
P.rep(block("public static long owedXp(java.util.UUID u, String skill, long add) {", "core"), '''M(core, r"""
public static long owedXp(java.util.UUID u, String skill, long add) {
  String ck = @PKG@.ShCfg.pkey(u);
  java.util.Properties q;
  try { q = @PKG@.ShStore.get(ck); } catch (@PKG@.ShBusy b0) { q = null; }   // 0.4.13 review: a busy first load = this credit waits in memory
  long due = add;
  String key = "Farming".equals(skill) ? "owed.xp" : "owed.xp." + skill;
  due += memTake(ck, key);   // fix2
  if (@PKG@.ShPay.f("skill:fn:addxp") == null) {   // fixer 2: SkyySkills absent / too old = nothing can be paid: the file part stays put
    long fh0 = q == null ? 0L : @PKG@.ShStore.lng(q, key, 0L);
    back(ck, q, key, due, u);
    return due + fh0 > 0L ? due + fh0 : -1L;
  }
  long fh = reserve(ck, q, key);   // 0.4.14: reserved before it is paid
  if (fh < 0L) { memAdj(ck, key, due, u); return due > 0L ? due : -1L; }   // 0.4.13 review: busy = all of it waits
  due += fh;
  if (due <= 0L) return -1L;
  long left = @PKG@.ShPay.xp(u, skill, due, "shard:" + skill.toLowerCase()) ? 0L : due;   // 0.4.14: SkyySkills with the lock released
  if (fh > 0L) @PKG@.ShStore.log(ck + " " + key + " PAID " + (due - left) + " of " + due + " (" + fh + " reserved)" + (left > 0L ? " - " + left + " go back" : ""));   // fixer
  back(ck, q, key, left, u);
  return left;
}""")
''')
P.rep('''    TICKS.incrementAndGet();
    long now = System.currentTimeMillis();
    @PKG@.ShWorlds.idle(now);''', '''    TICKS.incrementAndGet();
    long now = System.currentTimeMillis();
    try { @PKG@.ShCore.flushOwed(); } catch (Throwable t0) { @PKG@.ShCfg.warnOnce("flushowed", "moving waiting Collect credits into their files failed (logged once): " + t0); }   // 0.4.14
    @PKG@.ShWorlds.idle(now);''')
P.rep('''  try { if (this.exec != null) this.exec.shutdownNow(); } catch (Throwable t) { }   // 0.4.13
''', '''  try { if (this.exec != null) this.exec.shutdownNow(); } catch (Throwable t) { }   // 0.4.13
  try { @PKG@.ShCore.flushOwed(); } catch (Throwable t) { }   // 0.4.14: memory credits into their files before the server stops
''')

# ---------------------------------------------------------------------------------------------------- 1. pay outside, record under the lock
P.rep('''# 0.3: one purchase on shard kd (caller holds ShStore.LOCK): `item` x qty taken first (counted), then coins (items back when they fail),''',
      '''# 0.4.14 THE COMMIT of a purchase: under the lock, only when the profile file is still at the save count `ver` the decision was made at
# (else "#changed"; a busy lock = "#busy"): settled, keys = vals written, saved (a refused save = the file's reason, p undone). The
# payment happens BEFORE it with the lock released; the caller refunds on any non-null answer.
M(core, r"""
public static String commitKeys(String k, int kd, java.util.Properties p, String[] keys, String[] vals, long ver) {
  try { @PKG@.ShStore.LOCK.lock(); } catch (@PKG@.ShBusy b) { return "#busy"; }
  try {
    if (@PKG@.ShStore.ver(k) != ver) return "#changed";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    @PKG@.ShMath.settleAll(kd, p, now());   // production up to now at the old numbers
    for (int i = 0; i < keys.length; i++) p.setProperty(keys[i], vals[i]);
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); }
    return e;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
M(core, "public static boolean lockish(String e) { return \\"#busy\\".equals(e) || \\"#changed\\".equals(e) || \\"#have\\".equals(e); }")   # 0.4.14
M(core, r"""
public static String logTxt(String e) {
  if ("#busy".equals(e)) return "SHARD DATA BUSY";
  if ("#changed".equals(e)) return "CHANGED MEANWHILE";
  return "SAVE FAILED " + e;
}""")   # 0.4.14: the collect.log / totem.log word for a refused commit
M(core, r"""
public static String failTxt(String e, boolean rc, long coins) {
  String s = "#busy".equals(e) ? "-The shard is busy right now - everything is back, try again in a moment." : "-That changed meanwhile - everything is back, open it again.";
  return rc ? s : s + " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).";
}""")   # 0.4.14: the click's answer when the commit met a busy lock / a changed profile (the payment went back)
# 0.3: one purchase on shard kd (0.4.14: the caller does NOT hold ShStore.LOCK - it decided at save count `ver`; commitKeys writes): `item` x qty taken first (counted), then coins (items back when they fail),''')
P.rep(block("public static String purchase(java.util.UUID u, String k, int kd, java.util.Properties p, @IC@[] cs, String item, long qty, long coins, String key, String val, String tag, String what) {", "core"), '''M(core, r"""
public static String purchase(java.util.UUID u, String k, int kd, java.util.Properties p, @IC@[] cs, String item, long qty, long coins, String key, String val, String tag, String what, long ver) {
  long have = qty > 0L ? haveAll(u, cs, item) : 0L;   // 0.4.12: inventory + bags
  String nm = @PKG@.ShTotem.pretty(item);
  if (have < qty) return "-You need " + qty + " " + nm + " (you have " + have + pausedTxt(u, item) + ").";
  long purse = @PKG@.ShPay.coins(u);
  if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
  java.util.ArrayList kept = new java.util.ArrayList();   // fix (critic shards03): exact refunds of stacks with data
  String[] ids = new String[] { item };
  long[] bag = new long[1];
  long[] inv = payInvBags(u, cs, ids, new long[] { qty }, kept, bag);   // 0.4.12: inventory first, then bags; all or nothing. 0.4.14: the lock released
  if (inv == null) return "-The " + nm + " could not be taken - nothing was bought.";
  long got = inv[0] + bag[0];
  if (!@PKG@.ShPay.takeCoins(u, coins)) { String lost = refundPaid(u, cs, ids, inv, bag, kept); @PKG@.ShStore.log(u + " " + k + " " + tag + " refund " + (lost.length() == 0 ? String.valueOf(got) : "SHORT" + lost) + " of " + got + " " + item); return "-The coins could not be taken - your " + nm + " is back."; }
  String e = commitKeys(k, kd, p, new String[] { key }, new String[] { val }, ver);   // 0.4.14: the record under the lock (still at ver)
  if (e != null) {   // fix (critic): not saved = undone + everything paid goes back
    String lost = refundPaid(u, cs, ids, inv, bag, kept);
    boolean rc = @PKG@.ShPay.addCoins(u, coins);
    @PKG@.ShStore.log(u + " " + k + " " + what + " " + logTxt(e) + " - refund " + (lost.length() == 0 ? String.valueOf(got) : "SHORT" + lost) + " of " + got + " " + item + ", coins " + (rc ? coins : 0L) + " of " + coins);
    if (lockish(e)) return failTxt(e, rc, coins);
    @PKG@.ShCfg.warn(tag + " not saved, refunded: " + e);
    return "-The upgrade could not be saved - your " + nm + (rc ? " and coins are" : " is") + " back." + (rc ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
  }
  @PKG@.ShStore.log(u + " " + k + " " + what + " paid " + coins + " coins + " + got + " " + item + commitBags(u, ids, bag) + @PKG@.ShInv.keptText(kept));   // 0.4.12: the bag part committed once saved
  return null;
}""")
''')
_BUY = '''M(core, r"""
public static String @NAME@(java.util.UUID u, String k, int kd, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);   // 0.4.2: the owner only
  if (no != null) return no;
@PRE@  int c; long ver;
  @PKG@.ShStore.LOCK.lock(); try { c = @GET@; ver = @PKG@.ShStore.ver(k); } finally { @PKG@.ShStore.LOCK.unlock(); }   // 0.4.14: decide under the lock, pay outside it
@BODY@
}""")
'''
P.rep(block("public static String buyStorage(java.util.UUID u, String k, int kd, @IC@[] cs) {", "core"), _BUY.replace("@NAME@", "buyStorage").replace("@PRE@", "").replace("@GET@", "@PKG@.ShMath.storageTier(kd, p)").replace("@BODY@", '''  if (c >= 5) return "=Storage is at the highest tier.";
  int nt = c + 1;
  String r = purchase(u, k, kd, p, cs, @PKG@.ShKind.UPG[kd], (long) @PKG@.ShCfg.storeEnch(nt), @PKG@.ShCfg.storeCoins(nt), @PKG@.ShMath.kk(kd, "storage"), String.valueOf(nt), "storage", (kd == FK ? "" : @PKG@.ShKind.KEYS[kd] + " ") + "storage " + c + " -> " + nt, ver);
  if (r != null) return r;
  return "+Storage is now tier " + nt + ": " + @PKG@.ShCfg.num(@PKG@.ShMath.cap(kd, p)) + " items a new island (more with island upgrades).";'''))
P.rep(block("public static String buyCompactor(java.util.UUID u, String k, int kd, @IC@[] cs) {", "core"), _BUY.replace("@NAME@", "buyCompactor").replace("@PRE@", '''  if (@PKG@.ShKind.ENCH[kd].length() == 0 && @PKG@.ShKind.SMELT_ENCH[kd].length() == 0) return "-Nothing this shard makes has an Enchanted form yet - it has no Auto-Compactor.";
''').replace("@GET@", "@PKG@.ShMath.compactor(kd, p)").replace("@BODY@", '''  if (c >= 2) return "=The Auto-Compactor is at its highest tier.";
  int nc = c + 1;
  String r = purchase(u, k, kd, p, cs, @PKG@.ShKind.UPG[kd], (long) @PKG@.ShCfg.CMP_ITEMS[nc], @PKG@.ShCfg.CMP_COINS[nc], @PKG@.ShMath.kk(kd, "compactor"), String.valueOf(nc), "compactor", @PKG@.ShKind.KEYS[kd] + " compactor " + c + " -> " + nc, ver);
  if (r != null) return r;
  return nc == 1 ? "+Auto-Compactor I: Collect now gives the Enchanted form of every 100." : "+Auto-Compactor II: each island stores " + @PKG@.ShCfg.CMP_STORE + " % more.";'''))
P.rep(block("public static String buyCompressor(java.util.UUID u, String k, int kd, @IC@[] cs) {", "core"), _BUY.replace("@NAME@", "buyCompressor").replace("@PRE@", "").replace("@GET@", "@PKG@.ShMath.compressor(kd, p)").replace("@BODY@", '''  if (c >= 3) return "=The Time Compressor is at its highest tier.";
  int nc = c + 1;
  String r = purchase(u, k, kd, p, cs, "Ingredient_Void_Essence", (long) @PKG@.ShCfg.TC_VOID[nc], @PKG@.ShCfg.TC_COINS[nc], @PKG@.ShMath.kk(kd, "compressor"), String.valueOf(nc), "compressor", @PKG@.ShKind.KEYS[kd] + " compressor " + c + " -> " + nc, ver);
  if (r != null) return r;
  return "+Time Compressor " + @PKG@.ShTotem.ROMAN[nc - 1] + ": this shard makes x" + @PKG@.ShCfg.dec(@PKG@.ShCfg.TC_MULT[nc]) + " now.";'''))
P.rep(block("public static String purchaseM(java.util.UUID u, String k, int kd, java.util.Properties p, @IC@[] cs, Object[] mats, long coins, String[] keys, String[] vals, String tag, String what) {", "core"), '''M(core, r"""
public static String purchaseM(java.util.UUID u, String k, int kd, java.util.Properties p, @IC@[] cs, Object[] mats, long coins, String[] keys, String[] vals, String tag, String what, long ver) {
  String[] ids = (String[]) mats[0];
  long[] q = (long[]) mats[1];
  String need = needTxt(u, cs, ids, q);   // 0.4.12: inventory + bags (paused = said)
  if (need != null) return need;
  long purse = @PKG@.ShPay.coins(u);
  if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
  java.util.ArrayList kept = new java.util.ArrayList();
  long[] bag = new long[ids.length];
  long[] took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags; all or nothing. 0.4.14: the lock released
  if (took == null) return "-The items could not be taken - nothing was bought.";
  if (!@PKG@.ShPay.takeCoins(u, coins)) {
    String lost = refundPaid(u, cs, ids, took, bag, kept);
    @PKG@.ShStore.log(u + " " + k + " " + tag + " coins refused - refund " + (lost.length() == 0 ? String.valueOf(sumOf(took, bag)) : "SHORT" + lost) + " items");
    return "-The coins could not be taken - your items are back.";
  }
  String e = commitKeys(k, kd, p, keys, vals, ver);   // 0.4.14: the record under the lock (still at ver)
  if (e != null) {
    String lost = refundPaid(u, cs, ids, took, bag, kept);
    boolean rc = @PKG@.ShPay.addCoins(u, coins);
    @PKG@.ShStore.log(u + " " + k + " " + what + " " + logTxt(e) + " - refund " + (lost.length() == 0 ? String.valueOf(sumOf(took, bag)) : "SHORT" + lost) + " items, coins " + (rc ? coins : 0L) + " of " + coins);
    if (lockish(e)) return failTxt(e, rc, coins);
    @PKG@.ShCfg.warn(tag + " not saved, refunded: " + e);
    return "-It could not be saved - your items" + (rc ? " and coins are" : " are") + " back." + (rc ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
  }
  @PKG@.ShStore.log(u + " " + k + " " + what + " paid " + coins + " coins + " + @PKG@.ShIsl.matsText(mats) + commitBags(u, ids, bag) + @PKG@.ShInv.keptText(kept));   // 0.4.12
  return null;
}""")
''')
P.rep(block("public static String grow0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {", "core"), '''M(core, r"""
public static String grow0(java.util.UUID u, String k, int kd, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gateOwn(u, k, kd, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  int t0; int sz; int a; int d; int i;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot)) return "-That island is not yours yet.";
    t0 = @PKG@.ShIsl.ty(kd, p, slot);
    sz = @PKG@.ShMath.size(kd, p, slot);
    a = @PKG@.ShIsl.sub(p, kd, slot, 0); d = @PKG@.ShIsl.sub(p, kd, slot, 1); i = @PKG@.ShIsl.sub(p, kd, slot, 2);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (sz >= 3) return "=That island is fully grown.";
  if (a < 5 || d < 5 || i < 5) return "-Max all 3 upgrades first: " + @PKG@.ShIsl.subName(kd, 0) + " " + a + "/5, " + @PKG@.ShIsl.subName(kd, 1) + " " + d + "/5, " + @PKG@.ShIsl.subName(kd, 2) + " " + i + "/5.";
  double cv = @PKG@.ShCfg.curve(@PKG@.ShIsl.band(@PKG@.ShIsl.TIER[t0]));   // the bridges asked outside the lock
  int need = sz == 1 ? @PKG@.ShCfg.GM_COLL : @PKG@.ShCfg.GL_COLL;
  if (need > 0) {
    int ct = @PKG@.ShPay.collTier(u, @PKG@.ShKind.COLL[kd]);   // 0.4.14: between two short locks (0.4.13 unlocked in the middle of one)
    if (ct < need) return "-Needs " + @PKG@.ShKind.CNAME[kd] + " collection " + need + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ").";
  }
  long ver;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0 || @PKG@.ShMath.size(kd, p, slot) != sz) return "-That island changed meanwhile - open the menu again.";
    ver = @PKG@.ShStore.ver(k);   // 0.4.14: the decision; purchaseM commits only while nothing was saved since
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.growH(sz + 1), cv);
  Object[] mats = @PKG@.ShIsl.mats(kd, t0, @PKG@.ShCfg.MAT_GROW, sz - 1, 1L);
  String[] keys = new String[] { @PKG@.ShMath.ik(kd, slot, "size"), @PKG@.ShIsl.ik(kd, slot, "amt"), @PKG@.ShIsl.ik(kd, slot, "deco"), @PKG@.ShIsl.ik(kd, slot, "irr") };
  String[] vals = new String[] { String.valueOf(sz + 1), "0", "0", "0" };
  String r = purchaseM(u, k, kd, p, cs, mats, coins, keys, vals, "grow", @PKG@.ShKind.KEYS[kd] + " grow slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " " + sz + " -> " + (sz + 1), ver);
  if (r != null) return r;
  @PKG@.ShWorld2.repaint(k, kd);
  return "+The " + @PKG@.ShIsl.tname(t0) + " island grew to " + (sz == 1 ? "Medium" : "Large") + " - its 3 upgrades start again (what they gave stays).";
}""")
''')
rep_in("public static String buyIsland0(java.util.UUID u, String k, int kd, int ti, @IC@[] cs) {", [
    ('''  String res;
  int slot;
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShIsl.slotOf(kd, p, t) >= 0)''', '''  int slot;
  long ver;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock, pay outside it (purchaseM commits while nothing was saved since)
    if (@PKG@.ShIsl.slotOf(kd, p, t) >= 0)'''),
    ('''    if (slot < 0) return "=This shard has no room for another island.";
    long coins = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, cv);
    Object[] mats = @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
    long tn = now();
    String[] keys = new String[] { @PKG@.ShMath.ik(kd, slot, "type"), @PKG@.ShMath.ik(kd, slot, "size"), @PKG@.ShMath.ik(kd, slot, "last"), @PKG@.ShMath.ik(kd, slot, "stored") };
    String[] vals = new String[] { @PKG@.ShIsl.KEY[t], "1", String.valueOf(tn), "0" };
    String r = purchaseM(u, k, kd, p, cs, mats, coins, keys, vals, "island", @PKG@.ShKind.KEYS[kd] + " buy " + @PKG@.ShIsl.KEY[t] + " island in slot " + (slot + 1));
    if (r != null) return r;
    res = "+The " + @PKG@.ShIsl.tname(t) + " island is yours (Small). Put a worker totem on it (Totems tab) so it makes items.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);
  return res;''', '''    if (slot < 0) return "=This shard has no room for another island.";
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long coins = @PKG@.ShIsl.coins(@PKG@.ShCfg.BUY_H, cv);
  Object[] mats = @PKG@.ShIsl.mats(kd, t, @PKG@.ShCfg.BUY_ITEMS[kd], 0, 1L);
  long tn = now();
  String[] keys = new String[] { @PKG@.ShMath.ik(kd, slot, "type"), @PKG@.ShMath.ik(kd, slot, "size"), @PKG@.ShMath.ik(kd, slot, "last"), @PKG@.ShMath.ik(kd, slot, "stored") };
  String[] vals = new String[] { @PKG@.ShIsl.KEY[t], "1", String.valueOf(tn), "0" };
  String r = purchaseM(u, k, kd, p, cs, mats, coins, keys, vals, "island", @PKG@.ShKind.KEYS[kd] + " buy " + @PKG@.ShIsl.KEY[t] + " island in slot " + (slot + 1), ver);
  if (r != null) return r;
  @PKG@.ShWorld2.repaint(k, kd);
  return "+The " + @PKG@.ShIsl.tname(t) + " island is yours (Small). Put a worker totem on it (Totems tab) so it makes items.";''')], "core")
rep_in("public static String buySub0(java.util.UUID u, String k, int kd, int slot, int which, @IC@[] cs) {", [
    ('''  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0) return "-That island changed meanwhile - open the menu again.";
    int sz = @PKG@.ShMath.size(kd, p, slot);
    int lv = @PKG@.ShIsl.sub(p, kd, slot, which);
    String nm = @PKG@.ShIsl.subName(kd, which);
    if (lv >= 5) return sz >= 3 ? "=" + nm + " is at its highest level." : "=" + nm + " is 5/5 at this size - grow the island to go on.";
    int nl = lv + 1;
    long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, nl), cv);
    String tm = @PKG@.ShCombat.subMat(kd, which);   // 0.4.11: combat islands = combat.mat.*
    Object[] mats = @PKG@.ShIsl.mats(kd, t0, tm, sz - 1, (long) nl);
    String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.ik(kd, slot, @PKG@.ShIsl.SUBK[which]) }, new String[] { String.valueOf(nl) },
                         "sub", @PKG@.ShKind.KEYS[kd] + " " + @PKG@.ShIsl.SUBK[which] + " slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " size " + sz + " " + lv + " -> " + nl);
    if (r != null) return r;
    res = "+" + nm + " " + nl + "/5 on the " + @PKG@.ShIsl.tname(t0) + " island (+" + @PKG@.ShCfg.dec((@PKG@.ShIsl.mult(kd, p, slot, sz) - 1.0) * 100.0) + " % output from its upgrades).";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k, kd);
  return res;''', '''  int sz; int lv; long ver;
  String nm = @PKG@.ShIsl.subName(kd, which);
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock, pay outside it (purchaseM commits while nothing was saved since)
    if (!@PKG@.ShMath.hasIsland(kd, p, slot) || @PKG@.ShIsl.ty(kd, p, slot) != t0) return "-That island changed meanwhile - open the menu again.";
    sz = @PKG@.ShMath.size(kd, p, slot);
    lv = @PKG@.ShIsl.sub(p, kd, slot, which);
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (lv >= 5) return sz >= 3 ? "=" + nm + " is at its highest level." : "=" + nm + " is 5/5 at this size - grow the island to go on.";
  int nl = lv + 1;
  long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.subH(sz, nl), cv);
  String tm = @PKG@.ShCombat.subMat(kd, which);   // 0.4.11: combat islands = combat.mat.*
  Object[] mats = @PKG@.ShIsl.mats(kd, t0, tm, sz - 1, (long) nl);
  String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.ik(kd, slot, @PKG@.ShIsl.SUBK[which]) }, new String[] { String.valueOf(nl) },
                       "sub", @PKG@.ShKind.KEYS[kd] + " " + @PKG@.ShIsl.SUBK[which] + " slot " + slot + " " + @PKG@.ShIsl.KEY[t0] + " size " + sz + " " + lv + " -> " + nl, ver);
  if (r != null) return r;
  String res = "+" + nm + " " + nl + "/5 on the " + @PKG@.ShIsl.tname(t0) + " island (+" + @PKG@.ShCfg.dec((@PKG@.ShIsl.mult(kd, p, slot, sz) - 1.0) * 100.0) + " % output from its upgrades).";   // a read for the message (no lock: a done purchase never answers "busy")
  @PKG@.ShWorld2.repaint(k, kd);
  return res;''')], "core")
rep_in("public static String buyAuto0(java.util.UUID u, String k, int kd, @IC@[] cs) {", [
    ('''  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShIsl.auto(kd, p)) return "=This shard is automated already.";
    long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(step), cv);
    Object[] mats = @PKG@.ShIsl.mats(kd, @PKG@.ShIsl.LAD0[kd], @PKG@.ShCfg.AUTO_ITEMS[kd], 0, 1L);
    String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.kk(kd, "auto") }, new String[] { "1" }, "auto", @PKG@.ShKind.KEYS[kd] + " automation");
    if (r != null) return r;
  } finally { @PKG@.ShStore.LOCK.unlock(); }''', '''  long ver;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock, pay outside it
    if (@PKG@.ShIsl.auto(kd, p)) return "=This shard is automated already.";
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long coins = @PKG@.ShIsl.coins(@PKG@.ShIsl.stepH(step), cv);
  Object[] mats = @PKG@.ShIsl.mats(kd, @PKG@.ShIsl.LAD0[kd], @PKG@.ShCfg.AUTO_ITEMS[kd], 0, 1L);
  String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.kk(kd, "auto") }, new String[] { "1" }, "auto", @PKG@.ShKind.KEYS[kd] + " automation", ver);
  if (r != null) return r;''')], "core")
rep_in("public static String buyOffline0(java.util.UUID u, String k, int kd, @IC@[] cs) {", [
    ('''  int nl;
  @PKG@.ShStore.LOCK.lock(); try {
    int lv = @PKG@.ShIsl.offLv(kd, p);
    if (lv != lv0) return "-Offline Harvest changed meanwhile - open the menu again.";
    nl = lv + 1;
    long coins = offCoins(lv, cv);
    long q = offEnch(lv);
    String it = @PKG@.ShKind.UPG[kd];
    Object[] mats = (q > 0L && it.length() > 0) ? new Object[] { new String[] { it }, new long[] { q } } : new Object[] { new String[0], new long[0] };
    String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.kk(kd, "offline") }, new String[] { String.valueOf(nl) },
                         "offline", @PKG@.ShKind.KEYS[kd] + " offline harvest " + lv + " -> " + nl);
    if (r != null) return r;
  } finally { @PKG@.ShStore.LOCK.unlock(); }''', '''  long ver;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock, pay outside it
    if (@PKG@.ShIsl.offLv(kd, p) != lv0) return "-Offline Harvest changed meanwhile - open the menu again.";
    ver = @PKG@.ShStore.ver(k);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  int lv = lv0;
  int nl = lv + 1;
  long coins = offCoins(lv, cv);
  long q = offEnch(lv);
  String it = @PKG@.ShKind.UPG[kd];
  Object[] mats = (q > 0L && it.length() > 0) ? new Object[] { new String[] { it }, new long[] { q } } : new Object[] { new String[0], new long[0] };
  String r = purchaseM(u, k, kd, p, cs, mats, coins, new String[] { @PKG@.ShIsl.kk(kd, "offline") }, new String[] { String.valueOf(nl) },
                       "offline", @PKG@.ShKind.KEYS[kd] + " offline harvest " + lv + " -> " + nl, ver);
  if (r != null) return r;''')], "core")

# Add modifier / Add booster: the entry as checked is the reservation (the commit needs exactly it)
P.rep(block("public static String addMod(java.util.UUID u, String k, int kd, int slot, int pad, int mi, @IC@[] cs) {", "core"), '''M(core, r"""
public static String addMod(java.util.UUID u, String k, int kd, int slot, int pad, int mi, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, kd, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  if (mi < 0 || mi >= @PKG@.ShTotem.MOD_ITEMS.length) return "-You have no totem modifiers - craft them on the Craft tab.";
  String mid = @PKG@.ShTotem.MOD_ITEMS[mi];
  String e0;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock (the entry as checked), pay outside it, record under it
    String[] f = at(kd, p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    if (f[2].length() != 0 && f[3].length() != 0) return "-Both modifier slots are full - remove one first.";
    e0 = @PKG@.ShTotem.fmt(f);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (haveAll(u, cs, mid) < 1L) return "-You have no " + @PKG@.ShTotem.MOD_NAMES[mi] + " modifier" + pausedTxt(u, mid) + ".";   // 0.4.12: inventory + bags
  String[] ids = new String[] { mid };
  long[] bag = new long[1];
  java.util.ArrayList kept = new java.util.ArrayList();
  long[] inv = payInvBags(u, cs, ids, new long[] { 1L }, kept, bag);
  if (inv == null) return "-The modifier could not be taken.";
  String err = null;
  String[] f = null;
  boolean lk = false;
  try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { err = "#busy"; }
  if (lk) {
    try {
      f = at(kd, p, slot, pad);
      if (f == null || !@PKG@.ShTotem.fmt(f).equals(e0)) err = "#changed";
      else {
        int which = f[2].length() == 0 ? 2 : 3;
        @PKG@.ShMath.settle(kd, p, slot, now());
        java.util.Properties old = new java.util.Properties();
        old.putAll(p);
        f[which] = @PKG@.ShTotem.MOD_KEYS[mi];
        put(kd, p, slot, pad, f);
        err = @PKG@.ShStore.save(k, p);
        if (err != null) { p.clear(); p.putAll(old); }
      }
    } finally { @PKG@.ShStore.LOCK.unlock(); }
  }
  if (err != null) {
    String lost = refundPaid(u, cs, ids, inv, bag, kept);
    tlog(u + " " + k + " addmod " + mid + " " + logTxt(err) + " - back " + (lost.length() == 0 ? "1" : "SHORT" + lost));
    return lockish(err) ? failTxt(err, true, 0L) : "-Could not be saved - your modifier is back.";
  }
  tlog(u + " " + k + " addmod slot " + slot + " pad " + pad + " " + mid + " -> " + @PKG@.ShTotem.fmt(f) + commitBags(u, ids, bag));
  return "+" + @PKG@.ShTotem.MOD_NAMES[mi] + " added to " + @PKG@.ShTotem.name(f) + " (" + @PKG@.ShTotem.MOD_DESC[mi] + ").";
}""")
''')
P.rep(block("public static String addBooster(java.util.UUID u, String k, int kd, int slot, int pad, @IC@[] cs) {", "core"), '''M(core, r"""
public static String addBooster(java.util.UUID u, String k, int kd, int slot, int pad, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, kd, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  long now = now();
  String bid = null;
  for (int i = 0; i < @PKG@.ShTotem.BOOSTERS.length && bid == null; i++) if (@PKG@.ShInv.count(cs, @PKG@.ShTotem.BOOSTERS[i]) > 0L) bid = @PKG@.ShTotem.BOOSTERS[i];
  for (int i = 0; i < @PKG@.ShTotem.BOOSTERS.length && bid == null; i++) if (bagCount(u, @PKG@.ShTotem.BOOSTERS[i]) > 0L) bid = @PKG@.ShTotem.BOOSTERS[i];   // 0.4.12: then the bags
  if (bid == null) return "-A booster is 1 Life, Water or Void Essence - you have none" + pausedTxt(u, @PKG@.ShTotem.BOOSTERS[0]) + ".";
  String e0;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.14: decide under the lock (the entry as checked), pay outside it, record under it
    String[] f = at(kd, p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    if (@PKG@.ShTotem.boosted(f, now)) return "=A booster is already burning in this totem.";
    e0 = @PKG@.ShTotem.fmt(f);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String[] ids = new String[] { bid };
  long[] bag = new long[1];
  java.util.ArrayList kept = new java.util.ArrayList();
  long[] inv = payInvBags(u, cs, ids, new long[] { 1L }, kept, bag);   // 0.4.12: inventory first, then bags
  if (inv == null) return "-The essence could not be taken.";
  String err = null;
  String[] f = null;
  boolean lk = false;
  try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { err = "#busy"; }
  if (lk) {
    try {
      f = at(kd, p, slot, pad);
      if (f == null || !@PKG@.ShTotem.fmt(f).equals(e0) || @PKG@.ShTotem.boosted(f, now)) err = "#changed";
      else {
        @PKG@.ShMath.settle(kd, p, slot, now);
        java.util.Properties old = new java.util.Properties();
        old.putAll(p);
        f[4] = String.valueOf(now + 1000L * (long) @PKG@.ShCfg.BOOST_SEC);
        put(kd, p, slot, pad, f);
        err = @PKG@.ShStore.save(k, p);
        if (err != null) { p.clear(); p.putAll(old); }
      }
    } finally { @PKG@.ShStore.LOCK.unlock(); }
  }
  if (err != null) {
    String lost = refundPaid(u, cs, ids, inv, bag, kept);
    tlog(u + " " + k + " booster " + logTxt(err) + " - back " + (lost.length() == 0 ? "1" : "SHORT" + lost));
    return lockish(err) ? failTxt(err, true, 0L) : "-Could not be saved - your essence is back.";
  }
  tlog(u + " " + k + " booster slot " + slot + " pad " + pad + " " + bid + " until " + f[4] + commitBags(u, ids, bag));
  return "+Booster burning for " + (@PKG@.ShCfg.BOOST_SEC / 60) + " min: +2 range and +" + @PKG@.ShCfg.BOOST_PCT + " % for " + @PKG@.ShTotem.name(f) + ".";
}""")
''')
# craft: pay outside; a shard's crafted mark + the shard item under the lock (the mark re-checked there)
_c = block("public static String craft(java.util.UUID u, int ri, @IC@[] cs) {", "core")
_ca = _c.index("  boolean lk = false;\n  if (sk >= 0) { @PKG@.ShStore.LOCK.lock(); lk = true; }")
P.rep(_c[_ca:], r'''  String pk = @PKG@.ShCfg.pkey(u);   // 0.4.14: the profile bridge asked before any lock
  java.util.ArrayList kept = new java.util.ArrayList();   // fix (critic shards03): stacks with data taken (a stamped Soul Orb) = exact refunds
  long[] bag = new long[ids.length];
  long[] took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags; a short take = everything back already. 0.4.14: the lock released
  if (took == null) return "-The items or coins could not be taken - everything is back.";
  if (!@PKG@.ShPay.takeCoins(u, coins)) { refundPaid(u, cs, ids, took, bag, kept); return "-The items or coins could not be taken - everything is back."; }
  String id = @PKG@.ShCfg.CRAFT_ID[ri];
  int ti = @PKG@.ShTotem.itemIdx(id);
  boolean out = false;
  String what = "";
  String why = null;
  if (ti >= 0) {
    String[] f = new String[] { @PKG@.ShTotem.KEYS[ti], "1", "", "", "0", @PKG@.ShTotem.newUid() };
    out = @PKG@.ShInv.giveStack(cs, @PKG@.ShTotem.stack(f, now()));
    what = @PKG@.ShTotem.name(f);
  } else if (sk >= 0) {
    boolean lk = false;
    try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { why = "#busy"; }   // 0.4.14: busy = everything back below
    if (lk) {
      try {   // the mark re-checked, saved before the shard exists, taken back when it does not fit - one lock hold
        if (hasShard(pk, sk)) why = "#have";
        else if (!markCrafted(pk, sk, true)) why = "#save";   // fix4
        else {
          out = @PKG@.ShInv.give(cs, id, 1L) >= 1L;
          what = @PKG@.ShTotem.pretty(id);
          if (!out) markCrafted(pk, sk, false);   // fix4: no shard handed out = no mark
        }
      } finally { @PKG@.ShStore.LOCK.unlock(); }
    }
  } else {
    out = @PKG@.ShInv.give(cs, id, 1L) >= 1L;
    what = @PKG@.ShTotem.pretty(id);
  }
  if (out) {
    tlog(u + " craft " + id + " paid " + coins + " coins + " + @PKG@.ShCfg.CRAFT[ri] + commitBags(u, ids, bag) + @PKG@.ShInv.keptText(kept));   // 0.4.12: the bag part committed once handed out
    return "+Crafted " + what + ".";
  }
  boolean rc = @PKG@.ShPay.addCoins(u, coins);
  refundPaid(u, cs, ids, took, bag, kept);   // 0.4.12: inventory + bags back
  String ex = rc ? "." : " except " + @PKG@.ShCfg.num(coins) + " coins (ask an admin, totem.log).";
  if ("#busy".equals(why)) { tlog(u + " craft " + id + " SHARD DATA BUSY - refund items, coins " + (rc ? coins : 0L) + " of " + coins); return "-The shard is busy right now - everything is back" + ex; }
  if ("#have".equals(why)) { tlog(u + " craft " + id + " ALREADY HAS THAT SHARD - refund items, coins " + (rc ? coins : 0L) + " of " + coins); return "-" + haveShard(sk) + " Everything is back" + ex; }
  if ("#save".equals(why)) { tlog(u + " craft " + id + " NOT SAVED - refund items, coins " + (rc ? coins : 0L) + " of " + coins); return "-Your shard file could not be saved - everything is back" + ex; }
  tlog(u + " craft " + id + " NO ROOM - refund items, coins " + (rc ? coins : 0L) + " of " + coins);
  return "-Make room in your inventory first - everything is back" + ex;
}""")
''')
# a placed totem's Tier up: pay before the lock; a busy lock at the record = the cost back (the existing refund tail)
rep_in("public static String tierUpPlaced0(java.util.UUID u, String k, int kd, int slot, int pad, int seen, String type, String uid, @IC@[] cs) {", [
    ('''  long[] inv = null;
  String res = null;
  String[] nf = null;
  java.util.Properties old = null;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.13 review: the lock BEFORE paying (a busy lock = nothing taken; it was: paid, then the lock gave up = lost)
    inv = payInvBags(u, cs, ids, q, kept, bag);
    if (inv == null) return "-The cost could not be taken - everything is back.";
    try {''', '''  long[] inv = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.14: paid with the lock released (SkyySacks is never called while we hold it)
  if (inv == null) return "-The cost could not be taken - everything is back.";
  String res = null;
  String[] nf = null;
  java.util.Properties old = null;
  boolean lk = false;
  try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { res = "-The shard is busy right now - "; }   // 0.4.14: busy = the cost back below
  if (lk) { try {
    try {'''),
    ('''      res = "-Something went wrong - ";
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }''', '''      res = "-Something went wrong - ";
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); } }''')], "core")
# the bench upgrade: pay before the lock; the timer written only while nothing was saved since the decision
rep_in("public static String benchUp(java.util.UUID u, String k, int kd, @IC@[] cs) {", [
    ('''  int tier; long at; int to;
  @PKG@.ShStore.LOCK.lock(); try { tier = benchTier(kd, p, now); at = benchAt(kd, p); to = benchTo(kd, p); } finally { @PKG@.ShStore.LOCK.unlock(); }''',
     '''  int tier; long at; int to; long ver;
  @PKG@.ShStore.LOCK.lock(); try { tier = benchTier(kd, p, now); at = benchAt(kd, p); to = benchTo(kd, p); ver = @PKG@.ShStore.ver(k); } finally { @PKG@.ShStore.LOCK.unlock(); }   // 0.4.14: + the decision's save count'''),
    ('''  long[] took = null;
  int sec = @PKG@.ShCfg.BENCH_SEC[nt];
  String e;
  @PKG@.ShStore.LOCK.lock(); try {   // 0.4.13 review: the lock BEFORE paying (a busy lock = nothing taken; it was: paid, then the lock gave up = lost)
    took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags
    if (took == null) return "-The items could not be taken - nothing was bought.";
    if (!@PKG@.ShPay.takeCoins(u, coins)) { refundPaid(u, cs, ids, took, bag, kept); return "-The coins could not be taken - your items are back."; }
    java.util.Properties old = new java.util.Properties();''', '''  int sec = @PKG@.ShCfg.BENCH_SEC[nt];
  long[] took = payInvBags(u, cs, ids, q, kept, bag);   // 0.4.12: inventory first, then bags. 0.4.14: paid with the lock released
  if (took == null) return "-The items could not be taken - nothing was bought.";
  if (!@PKG@.ShPay.takeCoins(u, coins)) { refundPaid(u, cs, ids, took, bag, kept); return "-The coins could not be taken - your items are back."; }
  String e = null;
  boolean lk = false;
  try { @PKG@.ShStore.LOCK.lock(); lk = true; } catch (@PKG@.ShBusy b) { e = "#busy"; }   // 0.4.14: busy = everything back below
  if (lk) { try {
    if (@PKG@.ShStore.ver(k) != ver) e = "#changed";
    else {
    java.util.Properties old = new java.util.Properties();'''),
    ('''    e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); }
  } finally { @PKG@.ShStore.LOCK.unlock(); }''', '''    e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); }
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); } }'''),
    ('''    tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " bench " + tier + " -> " + nt + " SAVE FAILED " + e + " - refund items " + ri + ", coins " + (rcn ? coins : 0L) + " of " + coins);
    return''', '''    tlog(u + " " + k + " " + @PKG@.ShKind.KEYS[kd] + " bench " + tier + " -> " + nt + " " + logTxt(e) + " - refund items " + ri + ", coins " + (rcn ? coins : 0L) + " of " + coins);
    if (lockish(e)) return failTxt(e, rcn, coins);
    return''')], "core")

# ---------------------------------------------------------------------------------------------------- 2. islands asked before the lock
rep_in("public static String decide(java.util.UUID u, int kd, String world, int x, int y, int z, long now) {", [
    ('''  @PKG@.ShStore.LOCK.lock(); try {
    String placed = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "placed"));
    if (@PKG@.ShRole.stale(placed, owner)) {''', '''  String placed0;
  @PKG@.ShStore.LOCK.lock(); try { placed0 = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "placed")); } finally { @PKG@.ShStore.LOCK.unlock(); }
  boolean stale0 = placed0.length() > 0 && @PKG@.ShRole.stale(placed0, owner);   // 0.4.14: SkyyIslands asked with the lock released
  @PKG@.ShStore.LOCK.lock(); try {
    String placed = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "placed"));
    if (stale0 && placed.equals(placed0)) {   // 0.4.14: changed meanwhile = not stale (the safe answer)''')], "place")
rep_in("public static String door(java.util.UUID owner, String pkey, String kind, String world, int x, int y, int z) {", [
    ('''  boolean take = false;
  @PKG@.ShStore.LOCK.lock(); try {''', '''  boolean take = false;
  String placed0;
  @PKG@.ShStore.LOCK.lock(); try { placed0 = @PKG@.ShStore.str(p, @PKG@.ShMath.kk(kd, "placed")); } finally { @PKG@.ShStore.LOCK.unlock(); }
  boolean stale0 = placed0.length() > 0 && @PKG@.ShRole.stale(placed0, pkey);   // 0.4.14: SkyyIslands (our caller) asked with the lock released
  @PKG@.ShStore.LOCK.lock(); try {'''),
    ('''    take = placed.length() == 0 || placed.equals(door) || @PKG@.ShRole.stale(placed, pkey);''',
     '''    take = placed.length() == 0 || placed.equals(door) || (stale0 && placed.equals(placed0));   // 0.4.14: changed meanwhile = not stale''')], "dfn")
# the totem page: SkyyArmory's essence (costAt) after the lock
rep_in("public void fillTotemPage(String k, @IC@[] cs) {", [
    ('''double ench = 0.0; String cost = "";''', '''double ench = 0.0; String cost = ""; int cti = -1;'''),
    ('''      if (ti0 >= 0 && @PKG@.ShTotem.tierOf(f[1]) < 5) cost = @PKG@.ShTotem.costAt(kd, @PKG@.ShTotem.ITEMS[ti0], @PKG@.ShTotem.doc(f, now).toJson());
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (f == null) { this.dHas = false; return; }''', '''      if (ti0 >= 0 && @PKG@.ShTotem.tierOf(f[1]) < 5) cti = ti0;
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (f == null) { this.dHas = false; return; }
  if (cti >= 0) cost = @PKG@.ShTotem.costAt(kd, @PKG@.ShTotem.ITEMS[cti], @PKG@.ShTotem.doc(f, now).toJson());   // 0.4.14: SkyyArmory (a Combat totem's essence) asked after the lock''')], "page")

# the Totems tab's Tier up rows (fillTotems -> tierRows, inside fill's lock): the bag counts from the page's ONE sacks:fn:all read (hav, asked
# before the lock) instead of sacks:fn:count per item; a Combat totem's essence (SkyyArmory) from a cache warmed before the lock
rep_in("public void tierRows(java.util.Properties p, @IC@[] cs, int kd, String[] f, int ti, long now) {", [
    ('''    long h = cs == null ? -1L : @PKG@.ShCore.haveAll(this.me, cs, ids[i]);''',
     '''    long h = cs == null ? -1L : hav(cs, ids[i]);   // 0.4.14: the page's bag read (taken before the lock) - no SkyySacks call under it''')], "page")
P.rep(block("public static String essence(int kd, int tier) {", "tot"), '''F(tot, "public static final java.util.concurrent.ConcurrentHashMap ESS = new java.util.concurrent.ConcurrentHashMap();")   # 0.4.14: tier -> the last essence SkyyArmory named
F(tot, "public static final java.util.concurrent.ConcurrentHashMap ESS_AT = new java.util.concurrent.ConcurrentHashMap();")   # fixer: tier -> { the bridge function asked, Long when }
M(tot, r"""
public static String essence(int kd, int tier) {
  if (kd == 5) {
    if (@PKG@.ShStore.LOCK.isHeldByCurrentThread()) {   // 0.4.14: no SkyyArmory call under the lock - the answer warmed before it (warmEss)
      Object c = ESS.get(Integer.valueOf(tier));
      return c instanceof String ? (String) c : "Ingredient_Life_Essence";
    }
    String es = "Ingredient_Life_Essence";
    try {
      java.util.function.Function g = @PKG@.ShCfg.fnT(SOUL_TEST, "armory:fn:soulcage");
      long now = System.currentTimeMillis();
      Object c0 = ESS.get(Integer.valueOf(tier));
      Object a0 = ESS_AT.get(Integer.valueOf(tier));
      if (g != null && c0 instanceof String && a0 instanceof Object[] && ((Object[]) a0)[0] == g && now - ((Long) ((Object[]) a0)[1]).longValue() < 60000L) return (String) c0;   // fixer: once a minute per tier
      Object r = g == null ? null : g.apply(new Object[] { "essence", Integer.valueOf(tier) });
      if (r instanceof String && ((String) r).length() > 0) es = (String) r;
      if (g != null) ESS_AT.put(Integer.valueOf(tier), new Object[] { g, Long.valueOf(now) });
    } catch (Throwable t) { }
    ESS.put(Integer.valueOf(tier), es);
    return es;
  }
  return "Ingredient_Life_Essence";
}""")
M(tot, r"""
public static void warmEss(int kd) {
  if (kd != 5 || @PKG@.ShStore.LOCK.isHeldByCurrentThread()) return;
  for (int t = 1; t <= 5; t++) essence(kd, t);
}""")   # 0.4.14: asked before a page fill takes the lock
''')
rep_in("public void fill(String k, @IC@[] cs) {", [
    ('''  String upg = @PKG@.ShKind.UPG[kd];
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now);''', '''  String upg = @PKG@.ShKind.UPG[kd];
  @PKG@.ShTotem.warmEss(kd);   // 0.4.14: a Combat totem's tier-up essence (SkyyArmory) asked before the lock
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(kd, p, now);''')], "page")

# ---------------------------------------------------------------------------------------------------- 5. fixer: Enter Shard's load callback only hops
P.rep('''F(hop, "public int kind;")      # 0.3: the region painted before the teleport
''', '''F(hop, "public int kind;")      # 0.3: the region painted before the teleport
F(hop, "public boolean paint;")   # 0.4.14 fixer: run() = the paint step (on the shard world's thread), else the teleport
''')
P.rep('''M(hop, r"""
public void run() {
  try {
    if (this.ref == null || !this.ref.isValid()) return;''', '''# 0.4.14 fixer: on the SHARD world's thread: the profile read (may migrate under the lock) + the paint prep (takes the lock, 50 ms on a world
# thread) - never on whatever thread finished the engine's world load. A busy lock = the player is told (no teleport into an unpainted region).
# Fixer 2: the lock is taken HERE around the profile read and ShFill.region (whose paint prep locks again - reentrant), so a busy lock can
# never reach paintAsync's catch-all (that completes the paint normally = a teleport into an unpainted region); the wait is outside it.
M(hop, r"""
public void paintNow() {
  try {
    java.util.concurrent.CompletableFuture f = null;
    try { @PKG@.ShStore.LOCK.lock(); } catch (@PKG@.ShBusy b) { @PKG@.ShSay.toPlayer(this.u, "[Shards] Your shard is busy right now - press Enter Shard again in a moment.", "#ff6b6b"); return; }
    try {
      java.util.Properties p = @PKG@.ShStore.get(this.key);
      this.key = null;
      if (p != null) f = @PKG@.ShFill.region(this.to, p, this.kind);
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (f != null) { f.whenComplete(this); return; }
    if (this.from == null || !this.from.isAlive()) return;
    this.from.execute(this);
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard enter failed: " + t); }
}""")
M(hop, r"""
public void run() {
  if (this.paint) { this.paint = false; paintNow(); return; }   // 0.4.14 fixer
  try {
    if (this.ref == null || !this.ref.isValid()) return;''')
P.rep('''# the shard world is open (any thread): paint the region, then hop to the player's world thread for the teleport
M(hop, r"""
public void accept(Object res, Object err) {
  try {
    if (err != null || !(res instanceof @WLD@)) { @PKG@.ShSay.toPlayer(this.u, "[Shards] Your shard could not be opened - try again in a minute.", "#ff6b6b"); return; }
    this.to = (@WLD@) res;
    if (this.key != null) {
      java.util.Properties p = @PKG@.ShStore.get(this.key);
      if (p != null) { this.key = null; @PKG@.ShFill.region(this.to, p, this.kind).whenComplete(this); return; }
    }
    if (this.from == null || !this.from.isAlive()) return;''', '''# the shard world is open (any thread): 0.4.14 fixer: ONLY hops - the paint step to the shard world's thread (paintNow), then (the paint's
# own completion, a world thread) the teleport to the player's world thread
M(hop, r"""
public void accept(Object res, Object err) {
  try {
    if (err != null || !(res instanceof @WLD@)) { @PKG@.ShSay.toPlayer(this.u, "[Shards] Your shard could not be opened - try again in a minute.", "#ff6b6b"); return; }
    this.to = (@WLD@) res;
    if (this.key != null) { this.paint = true; this.to.execute(this); return; }   // 0.4.14 fixer: no profile read / lock on the loader's thread
    if (this.from == null || !this.from.isAlive()) return;''')

# ---------------------------------------------------------------------------------------------------- the ready line
P.rep('''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.13: the totem page''',
      '''getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.14: no other mod is called while the shard data lock is held (pay outside, record under it; Collect credits reserved before they are paid); 0.4.13: the totem page''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
assert "try {   // 0.4.13 review: the lock BEFORE paying" not in P.s and "ShRole.stale(placed, owner)" not in P.s and "ShRole.stale(placed, pkey)" not in P.s, "0.4.13's pay-under-lock left"
assert P.s.count("ver = @PKG@.ShStore.ver(k)") == 9, P.s.count("ver = @PKG@.ShStore.ver(k)")
_k = P.s.index
assert _k("public static void memAdd(") < _k("public static void memKeep(") < _k("public static long reserve(") < _k("public static long owed(java.util.UUID u, String item")
assert _k("public static String commitKeys(") < _k("public static String purchase(") < _k("public static String purchaseM(")
assert _k("public static long ver(String k)") < _k("public static synchronized String save(") and _k("public static void under(String key)") < _k("public static java.util.function.Function fnT(")
assert _k('cfg.getDeclaredMethod("under").setBody(') > _k('lockc = mk("ShLock"') and _k('cfg.getDeclaredMethod("under").setBody(') > _k("LOCK = new @PKG@.ShLock()")
P.finish()
