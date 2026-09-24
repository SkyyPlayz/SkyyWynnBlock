"""SkyyBank 0.1.2 - build script (javassist via jpype).
Run:   python build_skyybank_0.1.2.py            -> SkyyBank/SkyyBank-0.1.2.jar
       python build_skyybank_0.1.2.py --deploy   -> also copies to Mods/SkyyBank.jar and enables it in the HUD mod world
SkyBlock-style bank: /bank (status), /bank balance, /bank deposit <n|all|2k|1.5m>, /bank withdraw <n|all>.
Bank coins are death-safe by construction (SkyyCoins' death penalty only touches the purse).
Interest: every intervalMinutes (default 60 real minutes, counted from the last payout even across restarts)
every account earns interestPercent (default 2%) on min(balance, maxPrincipal 10,000,000). Offline players earn too.
Coins move through the SkyyCoins bridge functions (System property "skyy.bridge": coins:fn:get/add/take) -> zero deps;
if SkyyCoins is not loaded the commands say so. Publishes "bank:<uuid>" -> Long for a future HUD widget.
Admin: /bankconfig (show), /bankconfig <percent> <minutes>, /bankconfig <percent> <minutes> <maxPrincipal>
       (permission skyybank.admin on the command and on each variant).

0.1.1: command fixes (engine rules re-verified in HytaleServer.jar bytecode 2026-09-23; HANDOFF "COMMAND RULES"):
  - Permissions: 0.1 /bank never called requirePermission(), so CommandRegistry -> AbstractCommand.setOwner() gave it the auto
    node "<plugin base permission>.command.bank" (the version is part of it), which hytale:Adventurer players do not have, so only
    "*" admins could run it. /bank and both of its usage variants now call setPermissionGroups(new String[] { "hytale:Adventurer" })
    (vanilla /help /who /ping pattern, SkyyEssentials 0.1). Checked: generatePermission() gives a variant (name null) its parent's
    node; putRecursivePermissionGroups() grants the parent's node to the group; AbstractCommand.hasPermission() on a variant that has
    permission groups checks only that node. /bankconfig and its two variants stay admin: requirePermission("skyybank.admin") on each
    (a variant without groups also re-checks its parent), no permission groups.
  - Positional forms: 0.1 used optional args, which are not positional (acceptCall0 requires the pre-optional token count to EQUAL
    totalNumRequiredParameters), so "/bank deposit all" failed with server.commands.parsing.error.wrongNumberRequiredParameters.
    Now usage variants (description-only constructor + withRequiredArg, parent addUsageVariant). Checked: checkForExecutingSubcommands
    runs variantCommands.get(tokenCount) whenever the parent's own required count differs from the token count (addUsageVariant keys
    the map by the variant's required count), and falls through to the parent's own execute() for "/bank" and "/bankconfig" typed
    with no tokens (parent required count 0).
      /bank                          -> BankCmd        (status)
      /bank <action>                 -> BankActionCmd  (balance|bal; deposit/withdraw alone asks "how much?")
      /bank <action> <amount>        -> BankAmountCmd  (deposit|dep|d|put, withdraw|with|w|take; amount 500, 2k, 1.5m, 1,000, all|max)
      /bankconfig                    -> BankConfigCmd        (show)
      /bankconfig <pct> <min>        -> BankConfigSetCmd     (maxPrincipal unchanged)
      /bankconfig <pct> <min> <max>  -> BankConfigSetMaxCmd
    Any other token count gets the engine's usage error. The 0.1 flag forms still work because the parents keep their optional args
    (0 positional tokens -> the parent itself): /bank --action deposit --amount all, /bankconfig --percent 3 --minutes 30.
    Every path goes through BankCmd.run / BankConfigCmd.apply, so messages, amount parsing and limits are identical to 0.1.
  - Review fix: a ctx.get() failure in /bankconfig or either of its variants now goes through BankConfigCmd.failed(pr, t), which
    logs "/bankconfig failed: <throwable>" via BankStore.warn before replying with the usage line (same as BankCmd.failed on the
    /bank side). Bad number input is still handled inside BankConfigCmd.apply with the unlogged usage reply, exactly as in 0.1.

0.1.2: per-profile storage (tools/PROFILES-CONTRACT.md):
  - One account per profile. BankStore.pkey(uuid) is the contract helper, verbatim: it asks the SkyyProfiles bridge function
    "profile:fn:key" for the storage key of the player's ACTIVE profile. Profile 1 = "<uuid>" (every existing
    accounts/<uuid>.properties is profile 1, no migration); profile N = "<uuid>-pN" -> accounts/<uuid>-pN.properties.
    Without SkyyProfiles pkey = uuid, so files, balances, messages and interest are exactly 0.1.1.
  - In-memory caches BAL / LOADED are keyed by that key String (rule 2), so a profile switch simply resolves to another entry.
    New key-level API: loadKey/getKey/setKey(String); get/set(UUID) are thin wrappers over pkey.
  - Transfers vs profile switches (review fix): deposit/withdraw resolve the bank key once, but the purse side goes through
    coins:fn:take/add, and SkyyCoins resolves pkey(uuid) AGAIN inside that call. Two mods resolving at two instants cannot be made
    atomic from the bank alone, so a switch that lands between the bank's read and SkyyCoins' read would split one transfer across
    two profiles (reproduced with a fake SkyyProfiles + SkyyCoins against the 0.1.2 jar). The bank now brackets the purse call:
    it reads profile:epoch:<uuid> then the key before, and the key then the epoch after (sound whichever order SkyyProfiles
    updates them in, and it catches A->B->A). deposit/withdraw return an int:
      1 = done, nothing switched: both sides provably used the same profile.
      0 = not enough coins (purse for deposit, bank for withdraw) or SkyyCoins refused; nothing moved.
      3 = the profile switched before any coins moved (checked right before the purse call): nothing moved, the player is told
          "Your profile changed, nothing was moved. Try again."
      2 = the profile switched while the purse call ran. The purse side is already done and the bridge cannot say which profile
          SkyyCoins resolved, so the bank side is booked on the profile the transfer STARTED on (the one the player typed /bank on),
          the player is told so, and a WARNING logs uuid, both keys and both epochs for an admin. Why not refund + fail: SkyyCoins
          resolves its key first thing in take/add and then spends milliseconds in its ledger lock and file write, so a switch
          landing inside the purse call almost always lands AFTER SkyyCoins resolved the start profile; booking the start profile is
          then exactly right, while a refund through coins:fn:add would land on the NEW profile's purse (a cross-profile move in the
          common case). The only remaining split is a switch completing inside the microseconds between the bank's key read and
          SkyyCoins' own read; closing that needs a key-pinned coins bridge function (SkyyCoins + contract change, not this mod).
    In practice none of this can fire: /bank is an AbstractPlayerCommand, whose executeAsync runs execute() via
    runAsync(ctx, runnable, world) on the player's world thread (HytaleServer.jar bytecode), and SkyyProfiles has to switch on
    that same thread (it swaps the vanilla inventory, rule 5), so the two are serialised; the check is the backstop.
  - Interest still pays EVERY account file, offline profiles included: allAccounts() now returns storage keys and accepts
    "<uuid>.properties" (UUID.fromString, canonicalised exactly like 0.1.1) and "<uuid>-p<digits>.properties". The online
    "[Bank] You earned ..." message reports the player's active profile only.
  - Bridge "bank:<uuid>" stays keyed by UUID and always shows the ACTIVE profile (rule 3): loading or saving a key publishes only
    when that key is pkey(owner) (interest on an offline profile file no longer overwrites it). Epoch check: BankTick now runs
    every 1 s (integration check below; was 5 s); each run compares "profile:epoch:<uuid>" of every online player with the last
    epoch seen (BankStore.EPOCH, pruned to online players) and republishes bank:<uuid> from the new profile on a change. The
    interest check runs on every 30th run (30 s after start, then every 30 s: the 0.1.1 cadence). No epoch key (SkyyProfiles
    absent) -> the check does nothing.
  - Review fix: the interest tick's "[Bank] You earned" loop now null-checks Universe.get() like epochs() does (payouts were
    already saved before it; only the messages were at risk).
  - Rule 4 n/a (no stats or movement in this mod); rule 5: the vanilla inventory is never touched.
  Integration check against the pinned SkyyProfiles 0.1 semantics (tools/PROFILES-CONTRACT.md, 2026-09-23; fixed in place, still 0.1.2):
  - Already right: caches keyed by the storage key, one key per transfer (the bank side never re-resolves), writes are synchronous
    (no dirty data to flush at a switch), first sight of an epoch is a plain republish (baseline, no switch-like action), pkey is
    called under the bank lock only (SkyyProfiles never calls out, SkyyCoins never calls the bank: no lock cycle), no disconnect
    state besides EPOCH (pruned), bank:<uuid> kept after disconnect like SkyyProfiles' own keys. No item moves, so profile:busy
    does not concern this mod.
  - FIX interest lost a deposit: the interest loop read a balance (getKey) and wrote balance+gain (setKey) in two separate lock
    holds, so a /bank deposit or withdraw on the world thread landing between them was overwritten (coins gone from the purse,
    never booked). Now BankStore.payInterest(key, ...) compounds all due periods and writes once inside ONE lock hold.
  - FIX an unreadable account file was overwritten: a failed read left the key unloaded with balance 0, and the next deposit or
    setKey wrote 0 + n over the real balance (a transient Windows read failure would also do it: setKey's own loadKey then read the
    old value and the stale 0 + n replaced it). Now setKey refuses to write a key it could not read, deposit/withdraw return 4
    before any coins move, /bank says the account cannot be read, interest skips it, and bank:<uuid> is removed instead of
    showing 0 (SkyyMenu then shows "not loaded yet").
  - FIX stale bank:<uuid> after a switch for up to 5 s (SkyyMenu's Bank page and profile tooltip read it right after the switch
    closes the profile page): the epoch check now runs every 1 s, like SkyyCoins' CoinTick. One player's failure no longer skips
    the rest of the online list.
  - Hardening: the atomic rename of an account file is retried 5 x 20 ms on a FileSystemException (Windows: a scanner or editor
    holding the file; see replaceFile), the SkyyProfiles 0.1 pattern; before, one failure left the file stale and a restart lost
    that deposit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.2"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
LOG = "com.hypixel.hytale.logger.HytaleLogger"

for c, m in ((HSV, "SCHEDULED_EXECUTOR"), (CTX, "provided"), (UNI, "getPlayers"), (PR, "getUuid"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             (AC, "setPermissionGroups"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "withOptionalArg"),
             (CTX, "get"), (ATY, "STRING")):
    B.probe(pool, c, m)

PKG = "com.skyy.bank"
bs   = pool.makeClass(PKG + ".BankStore")
cfg  = pool.makeClass(PKG + ".BankConfig")
tick = pool.makeClass(PKG + ".BankTick")
cmd  = pool.makeClass(PKG + ".BankCmd", pool.get(APC))
cmdA = pool.makeClass(PKG + ".BankActionCmd", pool.get(APC))      # usage variant: /bank <action>
cmdN = pool.makeClass(PKG + ".BankAmountCmd", pool.get(APC))      # usage variant: /bank <action> <amount>
adm  = pool.makeClass(PKG + ".BankConfigCmd", pool.get(APC))
admS = pool.makeClass(PKG + ".BankConfigSetCmd", pool.get(APC))   # usage variant: /bankconfig <pct> <min>
admM = pool.makeClass(PKG + ".BankConfigSetMaxCmd", pool.get(APC))  # usage variant: /bankconfig <pct> <min> <max>

# Player-facing commands: grant the auto-generated permission node to the default player group (see docstring 0.1.1).
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'
pl   = pool.makeClass(PKG + ".SkyyBankPlugin", pool.get(JP))

# ================= BankStore =================
bs.addField(CtField.make("public static java.nio.file.Path DIR;", bs))
bs.addField(CtField.make(f"public static {LOG} LOG;", bs))
bs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAL = new java.util.concurrent.ConcurrentHashMap();", bs))
bs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOADED = new java.util.concurrent.ConcurrentHashMap();", bs))
# 0.1.2: last profile:epoch:<uuid> seen per online player (UUID -> epoch object), for republishing bank:<uuid>
bs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", bs))
bs.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", bs))
# 0.1.2: profile contract helper (tools/PROFILES-CONTRACT.md), verbatim. Storage key of the ACTIVE profile; uuid = profile 1.
bs.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyBank] " + msg); } catch (Throwable t) { }
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyBank] " + msg); } catch (Throwable t) { }
}""", bs))
# ---- coins bridge helpers (null-safe: SkyyCoins may be absent)
bs.addMethod(CtNewMethod.make("""
public static boolean coinsReady() {
  return bridge().get("coins:fn:get") instanceof java.util.function.Function
      && bridge().get("coins:fn:add") instanceof java.util.function.Function
      && bridge().get("coins:fn:take") instanceof java.util.function.Function;
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static long purse(java.util.UUID u) {
  Object f = bridge().get("coins:fn:get");
  if (!(f instanceof java.util.function.Function)) return 0L;
  Object r = ((java.util.function.Function) f).apply(u);
  return r instanceof Number ? ((Number) r).longValue() : 0L;
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static boolean purseTake(java.util.UUID u, long n) {
  Object f = bridge().get("coins:fn:take");
  if (!(f instanceof java.util.function.Function)) return false;
  Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
  return r instanceof Boolean && ((Boolean) r).booleanValue();
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static boolean purseAdd(java.util.UUID u, long n) {
  Object f = bridge().get("coins:fn:add");
  if (!(f instanceof java.util.function.Function)) return false;
  Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
  return r instanceof Number;
}""", bs))
# ---- ledger (0.1.2: keyed by the profile storage key "<uuid>" / "<uuid>-pN"; see docstring)
# owner(k): the player UUID of a storage key "<uuid>" or "<uuid>-p<digits>", null for anything else.
bs.addMethod(CtNewMethod.make("""
public static java.util.UUID owner(String k) {
  try {
    int i = k.indexOf("-p");
    if (i < 0) return java.util.UUID.fromString(k);
    String n = k.substring(i + 2);
    if (n.length() == 0) return null;
    for (int j = 0; j < n.length(); j++) {
      char c = n.charAt(j);
      if (c < '0' || c > '9') return null;
    }
    return java.util.UUID.fromString(k.substring(0, i));
  } catch (Throwable t) { return null; }
}""", bs))
# keyOf(file base name): canonical storage key (UUID part canonicalised like 0.1.1's UUID.fromString(..).toString()), or null.
bs.addMethod(CtNewMethod.make("""
public static String keyOf(String base) {
  java.util.UUID u = owner(base);
  if (u == null) return null;
  int i = base.indexOf("-p");
  return i < 0 ? u.toString() : u.toString() + base.substring(i);
}""", bs))
# bank:<uuid> always describes the ACTIVE profile: publish only when k is the owner's active key (callers hold the class lock).
bs.addMethod(CtNewMethod.make("""
public static synchronized void publishIfActive(String k) {
  java.util.UUID u = owner(k);
  if (u == null || !k.equals(pkey(u))) return;
  Long cur = (Long) BAL.get(k);
  bridge().put("bank:" + u.toString(), cur == null ? Long.valueOf(0L) : cur);
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized void loadKey(String k) {
  if (LOADED.containsKey(k)) return;
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      String v = p.getProperty("balance");
      if (v != null) BAL.put(k, Long.valueOf(Long.parseLong(v.trim())));
    }
    LOADED.put(k, Boolean.TRUE);
    publishIfActive(k);
  } catch (Throwable t) { warn("could not load account " + k + ": " + t); }
}""", bs))
# integration check: ready(k) = the account is loaded (a missing file counts: balance 0). false = the file exists but cannot be read;
# then nothing may write it (setKey), move coins through it (deposit/withdraw) or pay interest on it.
bs.addMethod(CtNewMethod.make("""
public static synchronized boolean ready(String k) {
  loadKey(k);
  return LOADED.containsKey(k);
}""", bs))
# integration check: Windows refuses to replace a file another handle has open (scanner, editor): retry the rename 5 x 20 ms
# (SkyyProfiles 0.1 atomicWrite pattern) before the save counts as failed. Tested on the game JRE: a handle opened through NIO
# gives AccessDeniedException, a java.io / non-share-delete handle (what scanners and editors use) gives a plain
# FileSystemException (sharing violation), so every FileSystemException except a missing tmp file is retried.
bs.addMethod(CtNewMethod.make("""
public static void replaceFile(java.nio.file.Path tmp, java.nio.file.Path f) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.NoSuchFileException e) {
      throw e;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized long getKey(String k) {
  loadKey(k);
  Long v = (Long) BAL.get(k);
  return v == null ? 0L : v.longValue();
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized void setKey(String k, long v) {
  if (v < 0L) v = 0L;
  if (!ready(k)) { warn("account " + k + " could not be read, NOT overwriting it with " + v + " (fix or remove the file)"); return; }
  BAL.put(k, Long.valueOf(v));
  publishIfActive(k);
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("balance", String.valueOf(v));
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyBank"); } finally { out.close(); }
    replaceFile(tmp, DIR.resolve(k + ".properties"));
  } catch (Throwable t) { warn("could not save account " + k + ": " + t); }
}""", bs))
# UUID-level API (commands, interest message): the player's ACTIVE profile account.
bs.addMethod(CtNewMethod.make("""
public static synchronized long get(java.util.UUID u) {
  return getKey(pkey(u));
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized void set(java.util.UUID u, long v) {
  setKey(pkey(u), v);
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized boolean readable(java.util.UUID u) {
  return ready(pkey(u));
}""", bs))
# republish bank:<uuid> from the active profile (epoch change)
bs.addMethod(CtNewMethod.make("""
public static synchronized void publish(java.util.UUID u) {
  String k = pkey(u);
  if (!ready(k)) { bridge().remove("bank:" + u.toString()); return; }
  Long v = (Long) BAL.get(k);
  bridge().put("bank:" + u.toString(), v == null ? Long.valueOf(0L) : v);
}""", bs))
# ---- transfers vs profile switches (review fix, see docstring "Transfers vs profile switches")
# epoch(u): SkyyProfiles' switch counter for u (Long), null without SkyyProfiles.
bs.addMethod(CtNewMethod.make("""
public static Object epoch(java.util.UUID u) {
  try { return bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { return null; }
}""", bs))
# sameProfile(u, k, e): true when u is still on key k with the epoch e read before k (key first, then epoch: catches A->B->A).
bs.addMethod(CtNewMethod.make("""
public static boolean sameProfile(java.util.UUID u, String k, Object e) {
  if (!k.equals(pkey(u))) return false;
  Object e2 = epoch(u);
  return e == null ? e2 == null : e.equals(e2);
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static void straddle(String op, java.util.UUID u, String k, Object e, long n) {
  warn("profile switched during a " + op + " of " + n + " coins for " + u + ": bank side booked on " + k
      + " (the profile it started on; active now " + pkey(u) + ", epoch " + e + " -> " + epoch(u)
      + "). SkyyCoins resolved the purse side itself: if it had already switched, the new profile's purse moved instead of " + k + "'s.");
}""", bs))
# 1 = done, 0 = not enough / refused (nothing moved), 3 = switched before coins moved (nothing moved),
# 2 = switched during the purse call (bank side booked on the start profile k, logged), 4 = account file unreadable (nothing moved)
bs.addMethod(CtNewMethod.make("""
public static synchronized int deposit(java.util.UUID u, long n) {
  if (n <= 0L) return 0;
  Object e = epoch(u);
  String k = pkey(u);
  if (!ready(k)) return 4;
  if (!sameProfile(u, k, e)) return 3;
  if (!purseTake(u, n)) return 0;
  boolean same = sameProfile(u, k, e);
  setKey(k, getKey(k) + n);
  if (same) return 1;
  straddle("deposit", u, k, e, n);
  return 2;
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized int withdraw(java.util.UUID u, long n) {
  if (n <= 0L) return 0;
  Object e = epoch(u);
  String k = pkey(u);
  if (!ready(k)) return 4;
  long have = getKey(k);
  if (!sameProfile(u, k, e)) return 3;
  if (have < n) return 0;
  if (!purseAdd(u, n)) return 0;
  boolean same = sameProfile(u, k, e);
  setKey(k, have - n);
  if (same) return 1;
  straddle("withdraw", u, k, e, n);
  return 2;
}""", bs))
# integration check: interest for one account in ONE lock hold (the old read-then-write in two holds could overwrite a deposit or
# withdraw landing in between). Same compounding as 0.1.1 (each period on min(balance, max)), one file write. Returns the gain.
bs.addMethod(CtNewMethod.make("""
public static synchronized long payInterest(String k, long due, int pct, long max) {
  if (!ready(k)) return 0L;
  long b = getKey(k);
  long total = 0L;
  for (long i = 0L; i < due; i++) {
    long principal = b < max ? b : max;
    long gain = principal * (long) pct / 100L;
    if (gain <= 0L) break;
    b = b + gain;
    total = total + gain;
  }
  if (total > 0L) setKey(k, b);
  return total;
}""", bs))
# every account file (all profiles, online or not) -> list of storage keys
bs.addMethod(CtNewMethod.make("""
public static synchronized java.util.List allAccounts() {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    if (!java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) return out;
    java.util.stream.Stream s = java.nio.file.Files.list(DIR);
    try {
      java.util.Iterator it = s.iterator();
      while (it.hasNext()) {
        String n = ((java.nio.file.Path) it.next()).getFileName().toString();
        if (!n.endsWith(".properties")) continue;
        String k = keyOf(n.substring(0, n.length() - 11));
        if (k != null) out.add(k);
      }
    } finally { s.close(); }
  } catch (Throwable t) { warn("could not list accounts: " + t); }
  return out;
}""", bs))

# ================= BankConfig =================
cfg.addField(CtField.make("public static java.nio.file.Path FILE;", cfg))
cfg.addField(CtField.make("public static volatile int PERCENT = 2;", cfg))
cfg.addField(CtField.make("public static volatile int MINUTES = 60;", cfg))
cfg.addField(CtField.make("public static volatile long MAX_PRINCIPAL = 10000000L;", cfg))
cfg.addField(CtField.make("public static volatile long LAST = 0L;", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static synchronized void save() {{
  try {{
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("interestPercent", String.valueOf(PERCENT));
    p.setProperty("intervalMinutes", String.valueOf(MINUTES));
    p.setProperty("maxPrincipal", String.valueOf(MAX_PRINCIPAL));
    p.setProperty("lastInterestMillis", String.valueOf(LAST));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyyBank config"); }} finally {{ out.close(); }}
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("could not save config: " + t); }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static synchronized void load() {{
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{ LAST = System.currentTimeMillis(); save(); return; }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    int pc = Integer.parseInt(p.getProperty("interestPercent", "2").trim());
    int mn = Integer.parseInt(p.getProperty("intervalMinutes", "60").trim());
    long mp = Long.parseLong(p.getProperty("maxPrincipal", "10000000").trim());
    long last = Long.parseLong(p.getProperty("lastInterestMillis", "0").trim());
    if (pc < 0) pc = 0;
    if (pc > 100) pc = 100;
    if (mn < 1) mn = 1;
    if (mp < 0L) mp = 0L;
    if (mp > 1000000000000L) mp = 1000000000000L;
    if (last <= 0L) last = System.currentTimeMillis();
    PERCENT = pc; MINUTES = mn; MAX_PRINCIPAL = mp; LAST = last;
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("could not load config: " + t); }}
}}""", cfg))

# ================= BankTick (scheduler thread, every 1s; interest every 30th run = every 30s) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make("public int runs = 0;", tick))
tick.addConstructor(CtNewConstructor.make("public BankTick() { }", tick))
# 0.1.1 run() body, now over storage keys (every profile file earns; the online message covers the active profile)
tick.addMethod(CtNewMethod.make(f"""
public void interest() {{
  try {{
    long interval = (long) {PKG}.BankConfig.MINUTES * 60000L;
    long now = System.currentTimeMillis();
    long due = (now - {PKG}.BankConfig.LAST) / interval;
    if (due <= 0L) return;
    if (due > 24L) due = 24L;
    int pct = {PKG}.BankConfig.PERCENT;
    java.util.List accounts = {PKG}.BankStore.allAccounts();
    java.util.HashMap earned = new java.util.HashMap();
    for (int i = 0; i < accounts.size(); i++) {{
      String key = (String) accounts.get(i);
      long total = {PKG}.BankStore.payInterest(key, due, pct, {PKG}.BankConfig.MAX_PRINCIPAL);
      if (total > 0L) earned.put(key, Long.valueOf(total));
    }}
    {PKG}.BankConfig.LAST = {PKG}.BankConfig.LAST + due * interval;
    {PKG}.BankConfig.save();
    {PKG}.BankStore.info("interest paid to " + earned.size() + " account(s), " + due + " period(s) at " + pct + "%");
    {UNI} uni = {UNI}.get();
    if (uni == null) return;
    java.util.Iterator it = uni.getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      Long g = (Long) earned.get({PKG}.BankStore.pkey(pr.getUuid()));
      if (g == null) continue;
      pr.sendMessage({MSG}.raw("[Bank] You earned " + g + " coins interest. Bank balance: " + {PKG}.BankStore.get(pr.getUuid())));
    }}
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("interest tick failed: " + t); }}
}}""", tick))
# 0.1.2 contract rule 3: republish bank:<uuid> when profile:epoch:<uuid> changes (no epoch key = no SkyyProfiles = nothing to do)
tick.addMethod(CtNewMethod.make(f"""
public void epochs() {{
  try {{
    {UNI} uni = {UNI}.get();
    if (uni == null) return;
    java.util.Map b = {PKG}.BankStore.bridge();
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = uni.getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      Object e = b.get("profile:epoch:" + u.toString());
      if (e == null) continue;
      Object seen = {PKG}.BankStore.EPOCH.get(u);
      if (seen != null && seen.equals(e)) continue;
      {PKG}.BankStore.EPOCH.put(u, e);
      try {{ {PKG}.BankStore.publish(u); }} catch (Throwable t) {{ {PKG}.BankStore.warn("could not republish bank:" + u + ": " + t); }}
    }}
    java.util.Iterator ks = {PKG}.BankStore.EPOCH.keySet().iterator();
    while (ks.hasNext()) {{
      if (!online.contains(ks.next())) ks.remove();
    }}
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("profile epoch check failed: " + t); }}
}}""", tick))
tick.addMethod(CtNewMethod.make("""
public void run() {
  epochs();
  this.runs = this.runs + 1;
  if (this.runs >= 30) {
    this.runs = 0;
    interest();
  }
}""", tick))

# ================= /bank =================
# 0.1.1: shared body (was BankCmd.execute in 0.1). actionText == null -> status; amountText == null -> "how much?".
# Order matters for javassist: statics first, then each variant's constructor + execute, then the parent constructor.
cmd.addMethod(CtNewMethod.make("""
public static long parseAmount(String s, long all) {
  s = s.trim().toLowerCase().replace(",", "");
  if (s.equals("all") || s.equals("max")) return all;
  long mult = 1L;
  if (s.endsWith("k")) { mult = 1000L; s = s.substring(0, s.length() - 1); }
  else if (s.endsWith("m")) { mult = 1000000L; s = s.substring(0, s.length() - 1); }
  double d = Double.parseDouble(s);
  return (long) (d * (double) mult);
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
public static void run({PR} pr, String actionText, String amountText) {{
  java.util.UUID u = pr.getUuid();
  try {{
    if (!{PKG}.BankStore.coinsReady()) {{ pr.sendMessage({MSG}.raw("[Bank] SkyyCoins is not loaded, the bank cannot move coins.")); return; }}
    if (!{PKG}.BankStore.readable(u)) {{ pr.sendMessage({MSG}.raw("[Bank] Your bank account file cannot be read right now, so nothing can move. Try again; if it keeps happening tell an admin (server log).")); return; }}
    if (actionText == null) {{
      pr.sendMessage({MSG}.raw("[Bank] Bank: " + {PKG}.BankStore.get(u) + " coins  |  Purse: " + {PKG}.BankStore.purse(u) + " coins"));
      pr.sendMessage({MSG}.raw("[Bank] Interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min (on up to " + {PKG}.BankConfig.MAX_PRINCIPAL + "). Bank coins are safe on death. /bank deposit|withdraw <amount|all>"));
      return;
    }}
    String action = actionText.trim().toLowerCase();
    if (action.equals("balance") || action.equals("bal")) {{
      pr.sendMessage({MSG}.raw("[Bank] Bank: " + {PKG}.BankStore.get(u) + " coins  |  Purse: " + {PKG}.BankStore.purse(u) + " coins"));
      return;
    }}
    boolean dep = action.startsWith("dep") || action.equals("d") || action.equals("put");
    boolean wd = action.startsWith("with") || action.equals("w") || action.equals("take");
    if (!dep && !wd) {{ pr.sendMessage({MSG}.raw("[Bank] Usage: /bank deposit <amount|all>  or  /bank withdraw <amount|all>")); return; }}
    if (amountText == null) {{ pr.sendMessage({MSG}.raw("[Bank] How much? e.g. /bank " + (dep ? "deposit" : "withdraw") + " 500  (or all, 2k, 1.5m)")); return; }}
    long all = dep ? {PKG}.BankStore.purse(u) : {PKG}.BankStore.get(u);
    long n;
    try {{ n = parseAmount(amountText, all); }}
    catch (Throwable t) {{ pr.sendMessage({MSG}.raw("[Bank] That is not a number. Use e.g. 500, 2k, 1.5m or all.")); return; }}
    if (n <= 0L) {{ pr.sendMessage({MSG}.raw("[Bank] Nothing to " + (dep ? "deposit" : "withdraw") + ".")); return; }}
    int r = dep ? {PKG}.BankStore.deposit(u, n) : {PKG}.BankStore.withdraw(u, n);
    if (r == 3) {{ pr.sendMessage({MSG}.raw("[Bank] Your profile changed, nothing was moved. Try again.")); return; }}
    if (r == 4) {{ pr.sendMessage({MSG}.raw("[Bank] Your bank account file cannot be read right now, nothing was moved. Try again; if it keeps happening tell an admin (server log).")); return; }}
    if (r == 2) {{ pr.sendMessage({MSG}.raw("[Bank] Your profile changed during this " + (dep ? "deposit: the " + n + " coins went into" : "withdrawal: the " + n + " coins came out of") + " the bank of the profile you started it on.")); return; }}
    if (dep) {{
      if (r != 1) {{ pr.sendMessage({MSG}.raw("[Bank] Not enough coins in your purse (" + {PKG}.BankStore.purse(u) + ").")); return; }}
      pr.sendMessage({MSG}.raw("[Bank] Deposited " + n + " coins. Bank: " + {PKG}.BankStore.get(u) + "  |  Purse: " + {PKG}.BankStore.purse(u)));
    }} else {{
      if (r != 1) {{ pr.sendMessage({MSG}.raw("[Bank] Not enough coins in the bank (" + {PKG}.BankStore.get(u) + ").")); return; }}
      pr.sendMessage({MSG}.raw("[Bank] Withdrew " + n + " coins. Bank: " + {PKG}.BankStore.get(u) + "  |  Purse: " + {PKG}.BankStore.purse(u)));
    }}
  }} catch (Throwable t) {{
    {PKG}.BankStore.warn("/bank failed: " + t);
    pr.sendMessage({MSG}.raw("[Bank] Something went wrong. Usage: /bank deposit|withdraw <amount|all>"));
  }}
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
public static void failed({PR} pr, Throwable t) {{
  {PKG}.BankStore.warn("/bank failed: " + t);
  pr.sendMessage({MSG}.raw("[Bank] Something went wrong. Usage: /bank deposit|withdraw <amount|all>"));
}}""", cmd))

# ---- usage variant /bank <action>   (description-only constructor, like vanilla WhereAmIOtherCommand / SkyyEssentials TpAcceptNamedCmd)
cmdA.addField(CtField.make(f"public {RA} actionArg;", cmdA))
cmdA.addConstructor(CtNewConstructor.make(f"""
public BankActionCmd() {{
  super("Show your bank and purse: /bank balance");
  this.actionArg = withRequiredArg("action", "balance (deposit and withdraw also need an amount)", {ATY}.STRING);
  {ADV}
}}""", cmdA))
cmdA.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String a = null;
  try {{ a = String.valueOf(ctx.get(this.actionArg)); }}
  catch (Throwable t) {{ {PKG}.BankCmd.failed(pr, t); return; }}
  {PKG}.BankCmd.run(pr, a, (String) null);
}}""", cmdA))

# ---- usage variant /bank <action> <amount>
cmdN.addField(CtField.make(f"public {RA} actionArg;", cmdN))
cmdN.addField(CtField.make(f"public {RA} amountArg;", cmdN))
cmdN.addConstructor(CtNewConstructor.make(f"""
public BankAmountCmd() {{
  super("Move coins: /bank deposit <amount|all> or /bank withdraw <amount|all>");
  this.actionArg = withRequiredArg("action", "deposit | withdraw", {ATY}.STRING);
  this.amountArg = withRequiredArg("amount", "number, 2k, 1.5m or all", {ATY}.STRING);
  {ADV}
}}""", cmdN))
cmdN.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String a = null;
  String n = null;
  try {{ a = String.valueOf(ctx.get(this.actionArg)); n = String.valueOf(ctx.get(this.amountArg)); }}
  catch (Throwable t) {{ {PKG}.BankCmd.failed(pr, t); return; }}
  {PKG}.BankCmd.run(pr, a, n);
}}""", cmdN))

# ---- parent /bank  (0 positional tokens: status, or the 0.1 flag form --action/--amount)
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addField(CtField.make(f"public {OA} amountArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public BankCmd() {{
  super("bank", "Bank: /bank | /bank balance | /bank deposit <amount|all> | /bank withdraw <amount|all>");
  this.actionArg = withOptionalArg("action", "deposit | withdraw (omit to see balances)", {ATY}.STRING);
  this.amountArg = withOptionalArg("amount", "number or all", {ATY}.STRING);
  {ADV}
  addUsageVariant(new {PKG}.BankActionCmd());
  addUsageVariant(new {PKG}.BankAmountCmd());
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String a = null;
  String n = null;
  try {{
    if (ctx.provided(this.actionArg)) a = String.valueOf(ctx.get(this.actionArg));
    if (ctx.provided(this.amountArg)) n = String.valueOf(ctx.get(this.amountArg));
  }} catch (Throwable t) {{ {PKG}.BankCmd.failed(pr, t); return; }}
  {PKG}.BankCmd.run(pr, a, n);
}}""", cmd))

# ================= /bankconfig (admin) =================
# 0.1.1: shared body (was BankConfigCmd.execute in 0.1). pctText == null -> show; minText/maxText == null -> keep current.
adm.addMethod(CtNewMethod.make(f"""
public static void apply({PR} pr, String pctText, String minText, String maxText) {{
  try {{
    if (pctText == null) {{
      long nextIn = ({PKG}.BankConfig.LAST + (long) {PKG}.BankConfig.MINUTES * 60000L - System.currentTimeMillis()) / 60000L;
      pr.sendMessage({MSG}.raw("[Bank] interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min, max principal " + {PKG}.BankConfig.MAX_PRINCIPAL + ", next payout in ~" + nextIn + " min. /bankconfig <percent> <minutes> [maxPrincipal]"));
      return;
    }}
    int pc = Integer.parseInt(pctText.replace("%", "").trim());
    int mn = minText != null ? Integer.parseInt(minText.trim()) : {PKG}.BankConfig.MINUTES;
    long mp = maxText != null ? {PKG}.BankCmd.parseAmount(maxText, {PKG}.BankConfig.MAX_PRINCIPAL) : {PKG}.BankConfig.MAX_PRINCIPAL;
    if (pc < 0 || pc > 100 || mn < 1 || mp < 0L || mp > 1000000000000L) {{ pr.sendMessage({MSG}.raw("[Bank] percent 0-100, minutes >= 1, maxPrincipal 0..1,000,000,000,000")); return; }}
    {PKG}.BankConfig.PERCENT = pc; {PKG}.BankConfig.MINUTES = mn; {PKG}.BankConfig.MAX_PRINCIPAL = mp;
    {PKG}.BankConfig.save();
    pr.sendMessage({MSG}.raw("[Bank] set: " + pc + "% every " + mn + " min, max principal " + mp));
  }} catch (Throwable t) {{ pr.sendMessage({MSG}.raw("[Bank] Usage: /bankconfig <percent> <minutes> [maxPrincipal]")); }}
}}""", adm))
# review fix: argument-read failures are logged server-side (mirrors BankCmd.failed); the player still sees the usage line.
adm.addMethod(CtNewMethod.make(f"""
public static void failed({PR} pr, Throwable t) {{
  {PKG}.BankStore.warn("/bankconfig failed: " + t);
  pr.sendMessage({MSG}.raw("[Bank] Usage: /bankconfig <percent> <minutes> [maxPrincipal]"));
}}""", adm))

# ---- usage variant /bankconfig <percent> <minutes>   (admin: requirePermission, no permission groups)
admS.addField(CtField.make(f"public {RA} pctArg;", admS))
admS.addField(CtField.make(f"public {RA} minArg;", admS))
admS.addConstructor(CtNewConstructor.make(f"""
public BankConfigSetCmd() {{
  super("(admin) Set bank interest: /bankconfig <percent> <minutes>");
  requirePermission("skyybank.admin");
  this.pctArg = withRequiredArg("percent", "interest percent per period", {ATY}.STRING);
  this.minArg = withRequiredArg("minutes", "real minutes per period", {ATY}.STRING);
}}""", admS))
admS.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String p = null;
  String m = null;
  try {{ p = String.valueOf(ctx.get(this.pctArg)); m = String.valueOf(ctx.get(this.minArg)); }}
  catch (Throwable t) {{ {PKG}.BankConfigCmd.failed(pr, t); return; }}
  {PKG}.BankConfigCmd.apply(pr, p, m, (String) null);
}}""", admS))

# ---- usage variant /bankconfig <percent> <minutes> <maxPrincipal>
admM.addField(CtField.make(f"public {RA} pctArg;", admM))
admM.addField(CtField.make(f"public {RA} minArg;", admM))
admM.addField(CtField.make(f"public {RA} maxArg;", admM))
admM.addConstructor(CtNewConstructor.make(f"""
public BankConfigSetMaxCmd() {{
  super("(admin) Set bank interest and cap: /bankconfig <percent> <minutes> <maxPrincipal>");
  requirePermission("skyybank.admin");
  this.pctArg = withRequiredArg("percent", "interest percent per period", {ATY}.STRING);
  this.minArg = withRequiredArg("minutes", "real minutes per period", {ATY}.STRING);
  this.maxArg = withRequiredArg("maxPrincipal", "interest is paid on at most this much", {ATY}.STRING);
}}""", admM))
admM.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String p = null;
  String m = null;
  String x = null;
  try {{ p = String.valueOf(ctx.get(this.pctArg)); m = String.valueOf(ctx.get(this.minArg)); x = String.valueOf(ctx.get(this.maxArg)); }}
  catch (Throwable t) {{ {PKG}.BankConfigCmd.failed(pr, t); return; }}
  {PKG}.BankConfigCmd.apply(pr, p, m, x);
}}""", admM))

# ---- parent /bankconfig  (0 positional tokens: show, or the 0.1 flag form --percent/--minutes/--maxPrincipal)
adm.addField(CtField.make(f"public {OA} pctArg;", adm))
adm.addField(CtField.make(f"public {OA} minArg;", adm))
adm.addField(CtField.make(f"public {OA} maxArg;", adm))
adm.addConstructor(CtNewConstructor.make(f"""
public BankConfigCmd() {{
  super("bankconfig", "(admin) /bankconfig <interest%> <minutes> [maxPrincipal]; no args shows the current setting");
  requirePermission("skyybank.admin");
  this.pctArg = withOptionalArg("percent", "interest percent per period", {ATY}.STRING);
  this.minArg = withOptionalArg("minutes", "real minutes per period", {ATY}.STRING);
  this.maxArg = withOptionalArg("maxPrincipal", "interest is paid on at most this much", {ATY}.STRING);
  addUsageVariant(new {PKG}.BankConfigSetCmd());
  addUsageVariant(new {PKG}.BankConfigSetMaxCmd());
}}""", adm))
adm.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String p = null;
  String m = null;
  String x = null;
  try {{
    if (ctx.provided(this.pctArg)) p = String.valueOf(ctx.get(this.pctArg));
    if (ctx.provided(this.minArg)) m = String.valueOf(ctx.get(this.minArg));
    if (ctx.provided(this.maxArg)) x = String.valueOf(ctx.get(this.maxArg));
  }} catch (Throwable t) {{ {PKG}.BankConfigCmd.failed(pr, t); return; }}
  {PKG}.BankConfigCmd.apply(pr, p, m, x);
}}""", adm))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyBankPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.BankStore.LOG = getLogger();
  {PKG}.BankStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyBank").resolve("accounts");
  {PKG}.BankConfig.FILE = getDataDirectory().resolveSibling("Skyy_SkyyBank").resolve("config.properties");
  {PKG}.BankConfig.load();
  getCommandRegistry().registerCommand(new {PKG}.BankCmd());
  getCommandRegistry().registerCommand(new {PKG}.BankConfigCmd());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.BankTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyBank] {VERSION} ready - /bank, interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min (coins bridge " + ({PKG}.BankStore.coinsReady() ? "found" : "NOT found yet") + ", profiles bridge " + ({PKG}.BankStore.bridge().get("profile:fn:key") instanceof java.util.function.Function ? "found" : "not found yet: one account per player") + ")");
}}""", pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (bs, cfg, tick, cmd, cmdA, cmdN, adm, admS, admM, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)
m = B.manifest("SkyyBank", VERSION, "SkyWynn bank: /bank deposit/withdraw, death-safe savings with periodic interest. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyBankPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyBank.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyBank" % VERSION, disable_prefix="Skyy:")
