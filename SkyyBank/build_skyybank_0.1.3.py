"""SkyyBank 0.1.3 - build script (javassist via jpype).
Run:   python build_skyybank_0.1.3.py            -> SkyyBank/SkyyBank-0.1.3.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)
SkyBlock-style bank: /bank (opens the bank page, 0.1.3), /bank balance, /bank status, /bank deposit <n|all|2k|1.5m>,
/bank withdraw <n|all>.

0.1.3 (Skyy's beta backlog item 4, HANDOFF log 2026-09-24 20:10): /bank with no arguments opens the BANK PAGE.
  - Derived from the live 0.1.2 by copy + edit (SkyyBank has no tools/*_patch.py). Unchanged from 0.1.2: BankConfig, one account
    per profile (pkey), the transfer bracket (results 1/0/2/3/4, plus 5 from the review fixes below), interest (interestPercent
    every intervalMinutes on min(balance, maxPrincipal), every account file incl. offline profiles, catch-up capped at 24 periods,
    one lock hold per account), the epoch republish of bank:<uuid>, the data files. BankStore's transfers and BankTick's threading
    changed in the review fixes below (same results, same files).
  - Chat forms unchanged: /bank balance|bal, /bank deposit|withdraw <amount|all> (and the short verbs), /bank deposit alone asks
    "how much?", the 0.1 flag form /bank --action deposit --amount all. The messages are the same strings as 0.1.2 (except when the
    purse cannot be read, review fix 3): the deposit / withdraw body moved into BankCmd.move(uuid, dep, amountText), which returns
    the text with a status mark (+ done, - refused, = info) and is shared by the chat path and the page. New: /bank status (alias
    info) prints the old two-line /bank status in chat, for players who prefer chat. If the Player component cannot be read, /bank
    falls back to that status.
  - THE PAGE (inline only, HANDOFF section 2: no .ui files, no underscores in ids, root Group anchor Width/Height only, TextButton +
    EventData, rebuilt only after a click - never a periodic update, never closes itself before opening another page), 1100 x 680:
      title "Bank" + the active profile (profile:name:<uuid> / profile:class:<uuid> when SkyyProfiles publishes them);
      two big panels: PURSE (coins:fn:get) and BANK (this profile's account), 40 pt numbers with thousands separators;
      an interest panel: "Interest: P% every M minutes, paid on up to X coins", "Next interest: in N min S s" (from
      lastInterestMillis + intervalMinutes; the tick checks every 30 s, so a due payout reads "any moment now"), and
      "Your next payout: +G coins" (G = min(bank, maxPrincipal) x P / 100, the same integer maths as payInterest);
      the controls row: [Deposit all] on the LEFT (the whole purse), in the MIDDLE an Amount TextField + [Deposit] + [Withdraw],
      [Withdraw all] on the RIGHT (the whole bank), each with a caption under it;
      a result line (green done / red refused / blue info), [Refresh] and [Close] (CustomUIPage.close() = PageManager.setPage(None),
      the SkyyMenu closePage call).
    The amount box copies the /guild bank box (SkyyGuilds 0.1, itself the SkyySacks 0.7.3 search pattern verified in game):
    EventData.of("a", "deposit").append("@BAmount", "#SkyyBAmount.Value"), read back with jsonStr. Enter in the box never moves
    coins (the box has two coin actions): it keeps the amount and says to click Deposit or Withdraw (the SkyyGuilds review fix).
    The typed amount is kept in the box after a refused move and cleared after a done one. Amounts: 500, 2k, 1.5m, 1,000, all.
    Every button goes through BankCmd.move -> BankStore.deposit / withdraw exactly like the chat commands (same checks, same
    profile bracket, same texts). The balance panels show "unreadable" when the purse or the account file cannot be read.
  - The page runs on the player's world thread (command execute + page events), the same thread as the chat commands.
  - SkyyMenu: 0.1.3 (built the same evening) replaced the old Bank submenu with one "Bank" tile (cmdc:bank, "Click to open!") that
    opens this page, and its Mods list already shows this version's commands (/bank status included) - the old "Click to print your
    balance in chat" tooltip follow-up is RESOLVED there. With the live SkyyMenu 0.1.2 the "Bank Account" item (/bank, keep-open)
    would also open this page. Deploy SkyyBank 0.1.3 and SkyyMenu 0.1.3 TOGETHER: tools/deploy_set.py still pins both at 0.1.2.
  0.1.3 REVIEW FIXES (same version, never deployed):
  1. Lock scope: 0.1.2 deposit / withdraw were `static synchronized` and called coins:fn:take / add while holding BankStore.class,
     i.e. across SkyyCoins' own ledger lock and balance-file write - every other bank op and the interest sweep waited on another
     mod's lock and disk. (No deadlock was possible: SkyyCoins never calls the bank, SkyyProfiles never calls out.) Now the coins
     call runs with no bank lock held and the ledger side is one short synchronized step on the key: creditK(k, n) / debitK(k, n),
     the SkyyCoins CoinStore shape (resolve outside the lock, one *K call, no call-outs under it). Deposit takes the purse first,
     then credits k; withdraw reserves (debits) k first, then pays the purse, and puts the reservation back if the purse call fails
     - no coins can be created, and interest paid in between is never overwritten (every ledger write is an atomic
     read-modify-write). Same result codes.
  2. Threads: HytaleServer.SCHEDULED_EXECUTOR is ONE shared daemon thread (newSingleThreadScheduledExecutor "Scheduler" in
     HytaleServer.<clinit>). 0.1.2 ran the whole interest sweep (every account file read + written) and the epoch republish (pkey +
     possible file read) on it. BankTick now only detects there (volatile / bridge-map reads; no pkey, no file, no bank lock) and
     hands the work as a BankJob to BankTick.WORKER, SkyyBank's own single daemon thread (engine ThreadUtil.daemon("SkyyBank")),
     shut down in shutdown(). Not the world thread like SkyyCoins' CoinTask: interest also pays offline profiles, which have no
     world. SWEEPING stops a slow sweep from being queued twice; an epoch is recorded only once its job was accepted (retried next
     second otherwise). Each online player's "[Bank] You earned" message and epoch check has its own try (one failing player no
     longer silences the players after them that tick).
  3. Unreadable purse: SkyyCoins 0.1.5 coins:fn:get / add / take return null when the purse file cannot be read (nothing changed).
     0.1.2 folded that into 0 / false, so chat said "Nothing to deposit", "Not enough coins in your purse (0)" or - for a withdrawal
     - "Not enough coins in the bank (<real balance>)". purseTake / purseAdd now return 1 / 0 / -1, deposit / withdraw return
     5 = the purse cannot be read (nothing moved), and move() says "Your purse cannot be read right now, nothing was moved" in chat
     AND on the page; the chat balance / status / done lines say "unreadable" instead of a made-up 0. The purse is read only for
     "deposit all", so a withdrawal never depends on coins:fn:get; the page's own purse pre-check (which refused withdrawals when
     only coins:fn:get failed) is gone.
  Checked and NOT changed - PROFILES-CONTRACT section 4 rule 1 ("one key per operation ... Do not re-resolve halfway (the SkyyBank
    0.1.2 pattern)"): the bank side resolves its storage key k ONCE per transfer and every bank read and write uses k. sameProfile()
    calls pkey(u) again only to COMPARE (switch detection for results 2 / 3), never as a storage key. That parenthetical was written
    in the same integration commit (23ee19a) that marked this code "Already right: one key per transfer (the bank side never
    re-resolves)" - it names this code as the example of the rule, but it reads like the opposite; the contract wording is a doc
    follow-up (not this mod's file). Refunding on a straddle (result 2) instead of booking the start profile stays rejected for the
    reason in 0.1.2 "Transfers vs profile switches": the refund would land on the NEW profile's purse. OPEN, tracked: closing the
    last microsecond window needs a key-pinned coins bridge call (e.g. coins:fn:takeKey / addKey taking the storage key) in
    SkyyCoins + the contract; then deposit / withdraw pass k and results 2 / 3 go away.
  CHECKED in a bare JVM (2026-09-24, scratch harness under tools/dev/scratch, deleted afterwards; -Xverify:all on all 11 classes):
    BankCmd.move texts = 0.1.2's chat strings; the page built with a fake PlayerRef (55 commands: balanced inline markup, 25 ids,
    no underscores, unique, one root with Width/Height only, controls left-to-right Deposit all | Amount | Deposit | Withdraw |
    Withdraw all, 7 bindings); clicks with fake coins:fn:* (Deposit all, Withdraw all, typed 2k / 1,500 / too much / empty, Enter
    never moves coins, Refresh, Close = close() without a rebuild, unknown action ignored, coins conserved); texts for due interest,
    2 h / 1 min intervals, the principal cap, 0%, a tiny bank, an unreadable purse, no SkyyCoins, an unreadable account file;
    hytale:Adventurer on /bank and both variants, skyybank.admin on /bankconfig and both variants.
  REVIEW FIXES CHECKED in a bare JVM (2026-09-24, second scratch harness, deleted afterwards; -Xverify:all + init on all 12 classes):
    Thread.holdsLock(BankStore.class) is false inside coins:fn:take and coins:fn:add; 0.1.2 texts for done / not enough / deposit
    all / withdraw all / 1,500 / not a number / how much / no SkyyCoins; purse returning null: deposit 500, deposit all, withdraw
    500, withdraw all all say "cannot be read" and move nothing; only add failing -> the withdrawal is put back; only take failing
    -> nothing moved; unreadable account file -> 4, purse untouched; page clicks (deposit 2k, withdraw / deposit all / withdraw all
    with a failing purse, amount kept on refusal, Enter never moves) and page build with a readable and an unreadable purse;
    BankTick: 30 runs without a worker pay nothing and resolve no pkey on the tick thread, with the worker 3 due periods compound on
    thread "SkyyBank" only (pkey calls recorded per thread), LAST advances, SWEEPING clears, an epoch job republishes bank:<uuid> on
    the worker, submit after shutdown is refused.
  UNVERIFIED (needs the game): the page on a real client (layout, 40 pt numbers, the 22 pt TextField - markup copied from the
    /guild page and the SkyySacks search box, but this page never ran on a client); CustomUIPage.close() from a button (bytecode =
    the SkyyMenu closePage call); /bank from SkyyMenu's Bank tile opening this page over the menu; PlayerRef.sendMessage from the
    SkyyBank worker thread (0.1.2 sent the same interest message from the shared scheduler thread, also not a world thread).
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
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.3"
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
# 0.1.3 page types (same classes as the SkyyGuilds 0.1 /guild page)
PLA  = "com.hypixel.hytale.server.core.entity.entities.Player"
PAGE = "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
PGM  = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
LIFE = "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB  = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB  = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD  = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT   = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
TUT  = "com.hypixel.hytale.server.core.util.concurrent.ThreadUtil"   # 0.1.3 review fix: daemon factory for the bank worker thread

for c, m in ((HSV, "SCHEDULED_EXECUTOR"), (CTX, "provided"), (UNI, "getPlayers"), (PR, "getUuid"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             (AC, "setPermissionGroups"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "withOptionalArg"),
             (CTX, "get"), (ATY, "STRING"),
             (UCB, "appendInline"), (UCB, "set"), (UEB, "addEventBinding"), (EVD, "of"), (EVD, "append"),
             (BT, "Activating"), (BT, "Validating"), (PAGE, "rebuild"), (PAGE, "handleDataEvent"), (PAGE, "close"),
             (PAGE, "build"), (PGM, "openCustomPage"), (PLA, "getPageManager"), (PLA, "getComponentType"),
             (LIFE, "CanDismiss"), (TUT, "daemon")):
    B.probe(pool, c, m)

PKG = "com.skyy.bank"
bs   = pool.makeClass(PKG + ".BankStore")
cfg  = pool.makeClass(PKG + ".BankConfig")
tick = pool.makeClass(PKG + ".BankTick")
job  = pool.makeClass(PKG + ".BankJob")                           # 0.1.3 review fix: work handed from BankTick to its worker thread
cmd  = pool.makeClass(PKG + ".BankCmd", pool.get(APC))
cmdA = pool.makeClass(PKG + ".BankActionCmd", pool.get(APC))      # usage variant: /bank <action>
cmdN = pool.makeClass(PKG + ".BankAmountCmd", pool.get(APC))      # usage variant: /bank <action> <amount>
adm  = pool.makeClass(PKG + ".BankConfigCmd", pool.get(APC))
admS = pool.makeClass(PKG + ".BankConfigSetCmd", pool.get(APC))   # usage variant: /bankconfig <pct> <min>
admM = pool.makeClass(PKG + ".BankConfigSetMaxCmd", pool.get(APC))  # usage variant: /bankconfig <pct> <min> <max>
page = pool.makeClass(PKG + ".BankPage", pool.get(PAGE))           # 0.1.3: the /bank page

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
# 0.1.3 review fix: the purse helpers tell "refused / not enough" apart from "the coins bridge call failed". SkyyCoins 0.1.5's
# coins:fn:get/add/take return null for an unreadable balance file (and for any other failure inside the call); nothing changed
# then (CoinStore throws in need() before any write). 0.1.2 folded that null into 0 / false, so chat said "Not enough coins in
# your purse (0)" or "Not enough coins in the bank (<real balance>)" when the purse could not be read.
# purseOr(u): the purse, or -1 when SkyyCoins is missing or the purse cannot be read.
bs.addMethod(CtNewMethod.make("""
public static long purseOr(java.util.UUID u) {
  try {
    Object f = bridge().get("coins:fn:get");
    if (!(f instanceof java.util.function.Function)) return -1L;
    Object r = ((java.util.function.Function) f).apply(u);
    return r instanceof Number ? ((Number) r).longValue() : -1L;
  } catch (Throwable t) { return -1L; }
}""", bs))
# chat texts: "500" / "500 coins" as in 0.1.2, "unreadable" instead of a made-up 0
bs.addMethod(CtNewMethod.make("""
public static String purseNum(java.util.UUID u) {
  long p = purseOr(u);
  return p < 0L ? "unreadable" : String.valueOf(p);
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static String purseCoins(java.util.UUID u) {
  long p = purseOr(u);
  return p < 0L ? "unreadable" : p + " coins";
}""", bs))
# purseTake: 1 = taken, 0 = not enough (nothing taken), -1 = SkyyCoins missing / the call failed (nothing taken)
bs.addMethod(CtNewMethod.make("""
public static int purseTake(java.util.UUID u, long n) {
  Object f = bridge().get("coins:fn:take");
  if (!(f instanceof java.util.function.Function)) return -1;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) }); } catch (Throwable t) { return -1; }
  if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  return -1;
}""", bs))
# purseAdd: 1 = added, -1 = SkyyCoins missing / the call failed (nothing added)
bs.addMethod(CtNewMethod.make("""
public static int purseAdd(java.util.UUID u, long n) {
  Object f = bridge().get("coins:fn:add");
  if (!(f instanceof java.util.function.Function)) return -1;
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) }); } catch (Throwable t) { return -1; }
  return r instanceof Number ? 1 : -1;
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
# 0.1.3 review fix (lock scope): the ledger side of a transfer is ONE short locked read-modify-write on the key k, and the SkyyCoins
# call happens with NO bank lock held (0.1.2 held BankStore.class across coins:fn:take/add, i.e. across CoinStore's own lock and
# balance-file write, stalling every other bank op and the interest sweep meanwhile). Same shape as SkyyCoins' CoinStore: resolve
# the key outside the lock, one synchronized *K step, no call-outs to another mod under the lock.
# creditK: + n on k (false = the account file cannot be read; nothing written).
bs.addMethod(CtNewMethod.make("""
public static synchronized boolean creditK(String k, long n) {
  if (!ready(k)) return false;
  setKey(k, getKey(k) + n);
  return true;
}""", bs))
# debitK: - n on k if the balance covers it. 1 = done, 0 = not enough (nothing written), 4 = unreadable (nothing written).
bs.addMethod(CtNewMethod.make("""
public static synchronized int debitK(String k, long n) {
  if (!ready(k)) return 4;
  long have = getKey(k);
  if (have < n) return 0;
  setKey(k, have - n);
  return 1;
}""", bs))
# 1 = done, 0 = not enough / refused (nothing moved), 3 = switched before coins moved (nothing moved),
# 2 = switched during the purse call (bank side booked on the start profile k, logged), 4 = account file unreadable (nothing moved),
# 5 = the purse cannot be read / the coins bridge call failed (nothing moved; 0.1.3 review fix, was reported as 0 before).
# One storage key k per transfer (PROFILES-CONTRACT section 4 rule 1): every bank read and write uses k; sameProfile() only compares.
# Deposit: purse first (nothing to undo if it is refused), then credit k. Withdraw: debit k first (the coins are reserved, so no
# coins can be created), then the purse; if the purse call fails the reservation goes back to k.
bs.addMethod(CtNewMethod.make("""
public static int deposit(java.util.UUID u, long n) {
  if (n <= 0L) return 0;
  Object e = epoch(u);
  String k = pkey(u);
  if (!ready(k)) return 4;
  if (!sameProfile(u, k, e)) return 3;
  int t = purseTake(u, n);
  if (t < 0) return 5;
  if (t == 0) return 0;
  boolean same = sameProfile(u, k, e);
  if (!creditK(k, n)) {
    int back = purseAdd(u, n);
    warn("deposit of " + n + " coins for " + u + ": account " + k + " could not be read after the purse was charged - "
        + (back == 1 ? "the coins went back to the purse" : "REFUND FAILED, give the player " + n + " coins by hand"));
    return 4;
  }
  if (same) return 1;
  straddle("deposit", u, k, e, n);
  return 2;
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static int withdraw(java.util.UUID u, long n) {
  if (n <= 0L) return 0;
  Object e = epoch(u);
  String k = pkey(u);
  if (!ready(k)) return 4;
  if (!sameProfile(u, k, e)) return 3;
  int d = debitK(k, n);
  if (d != 1) return d;
  if (purseAdd(u, n) != 1) {
    if (!creditK(k, n)) warn("withdraw of " + n + " coins for " + u + ": the purse call failed and account " + k
        + " could not be credited back - REFUND FAILED, add " + n + " coins to that account by hand");
    return 5;
  }
  boolean same = sameProfile(u, k, e);
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

# ================= BankTick (scheduler thread, every 1s; interest check every 30th run = every 30s) =================
# 0.1.3 review fix: HytaleServer.SCHEDULED_EXECUTOR is ONE shared daemon thread ("Scheduler", newSingleThreadScheduledExecutor in
# HytaleServer.<clinit>) that the engine and every mod schedule on. 0.1.2 did the whole interest sweep there (list the accounts
# folder, read + write every account file under the bank lock, message every online player) and the epoch republish (pkey +
# possibly an account-file read). Now BankTick only DETECTS on that thread (interest due? epoch changed? - volatile fields and
# bridge map reads, no pkey, no file, no bank lock) and hands the work to WORKER, SkyyBank's own single daemon thread
# (ThreadUtil.daemon("SkyyBank"), the engine's factory), as a BankJob. Not the world thread like SkyyCoins' CoinTask: interest pays
# every account file, offline profiles included, which have no world. One worker thread = sweeps and republishes never overlap.
# SWEEPING (set on hand-off, cleared when the sweep ends) stops a slow sweep from being queued twice.
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make("public int runs = 0;", tick))
tick.addField(CtField.make("public static volatile java.util.concurrent.ExecutorService WORKER;", tick))
tick.addField(CtField.make("public static volatile boolean SWEEPING = false;", tick))
tick.addField(CtField.make("public static volatile long WARNED = 0L;", tick))
tick.addConstructor(CtNewConstructor.make("public BankTick() { }", tick))
# 0.1.1 run() body, now over storage keys (every profile file earns; the online message covers the active profile). Runs on WORKER.
# Review fix: each player's "[Bank] You earned" message has its own try (one failing player no longer silences everyone after them).
tick.addMethod(CtNewMethod.make(f"""
public static void sweep() {{
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
    try {{
      if (pr != null && pr.isValid()) {{
        Long g = (Long) earned.get({PKG}.BankStore.pkey(pr.getUuid()));
        if (g != null) pr.sendMessage({MSG}.raw("[Bank] You earned " + g + " coins interest. Bank balance: " + {PKG}.BankStore.get(pr.getUuid())));
      }}
    }} catch (Throwable t) {{ {PKG}.BankStore.warn("interest message failed for one player: " + t); }}
  }}
}}""", tick))
tick.addMethod(CtNewMethod.make(f"""
public static void interest() {{
  try {{ sweep(); }} catch (Throwable t) {{ {PKG}.BankStore.warn("interest tick failed: " + t); }}
  SWEEPING = false;
}}""", tick))
# cheap due check for the scheduler thread (volatile reads only)
tick.addMethod(CtNewMethod.make(f"""
public static boolean due() {{
  long interval = (long) {PKG}.BankConfig.MINUTES * 60000L;
  if (interval <= 0L) return false;
  return (System.currentTimeMillis() - {PKG}.BankConfig.LAST) / interval > 0L;
}}""", tick))
# hand a job to WORKER; false = not accepted (no worker yet / shut down): the caller retries on a later tick
tick.addMethod(CtNewMethod.make(f"""
public static boolean submit(java.lang.Runnable r) {{
  try {{
    java.util.concurrent.ExecutorService w = WORKER;
    if (w == null) return false;
    w.execute(r);
    return true;
  }} catch (Throwable t) {{
    long now = System.currentTimeMillis();
    if (now - WARNED >= 60000L) {{ WARNED = now; {PKG}.BankStore.warn("bank worker did not take a job (retried): " + t); }}
    return false;
  }}
}}""", tick))

# ================= BankJob (0.1.3 review fix: runs on BankTick.WORKER) =================
# u == null -> the interest sweep; u != null -> republish bank:<u> from the active profile (epoch change).
job.addInterface(pool.get("java.lang.Runnable"))
job.addField(CtField.make("public java.util.UUID u;", job))
job.addConstructor(CtNewConstructor.make("public BankJob(java.util.UUID u) { this.u = u; }", job))
job.addMethod(CtNewMethod.make(f"""
public void run() {{
  if (this.u == null) {{ {PKG}.BankTick.interest(); return; }}
  try {{ {PKG}.BankStore.publish(this.u); }} catch (Throwable t) {{ {PKG}.BankStore.warn("could not republish bank:" + this.u + ": " + t); }}
}}""", job))

# 0.1.2 contract rule 3: republish bank:<uuid> when profile:epoch:<uuid> changes (no epoch key = no SkyyProfiles = nothing to do).
# 0.1.3: detection only (bridge reads); the republish is a BankJob on WORKER. The epoch is recorded once the job was accepted, so a
# refused hand-off is retried next second. One player's failure never skips the rest.
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
      try {{
        if (pr != null && pr.isValid()) {{
          java.util.UUID u = pr.getUuid();
          online.add(u);
          Object e = b.get("profile:epoch:" + u.toString());
          Object seen = {PKG}.BankStore.EPOCH.get(u);
          if (e != null && (seen == null || !seen.equals(e))) {{
            if (submit(new {PKG}.BankJob(u))) {PKG}.BankStore.EPOCH.put(u, e);
          }}
        }}
      }} catch (Throwable t) {{ {PKG}.BankStore.warn("profile epoch check failed for one player: " + t); }}
    }}
    java.util.Iterator ks = {PKG}.BankStore.EPOCH.keySet().iterator();
    while (ks.hasNext()) {{
      if (!online.contains(ks.next())) ks.remove();
    }}
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("profile epoch check failed: " + t); }}
}}""", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  epochs();
  this.runs = this.runs + 1;
  if (this.runs >= 30) {{
    this.runs = 0;
    if (!SWEEPING && due()) {{
      SWEEPING = true;
      if (!submit(new {PKG}.BankJob((java.util.UUID) null))) SWEEPING = false;
    }}
  }}
}}""", tick))

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
# 0.1.3: the deposit / withdraw body of 0.1.2's run(), shared by the chat path and the page. Returns the SAME text 0.1.2 sent (without
# the "[Bank] " prefix) behind a status mark: '+' done, '-' refused / nothing moved, '=' info. The two guards at the top are 0.1.2's
# run() guards (run() still checks them first, so the chat order of messages is unchanged; the page relies on them here).
# "all" / "max" (parseAmount's spelling rules): only then does move() need the purse (deposit) or bank (withdraw) balance
cmd.addMethod(CtNewMethod.make("""
public static boolean isAll(String s) {
  if (s == null) return false;
  String t = s.trim().toLowerCase().replace(",", "");
  return t.equals("all") || t.equals("max");
}""", cmd))
# 0.1.3 review fix: an unreadable purse (SkyyCoins 0.1.5 coins:fn:* return null) now says so, in chat AND on the page, instead of
# "Nothing to deposit" / "Not enough coins in your purse (0)" / "Not enough coins in the bank (<real balance>)". Every other text
# is unchanged. The purse is read only for "deposit all", so a withdrawal never depends on coins:fn:get.
cmd.addMethod(CtNewMethod.make(f"""
public static String move(java.util.UUID u, boolean dep, String amountText) {{
  String purseBad = "-Your purse cannot be read right now, nothing was moved. Try again; if it keeps happening tell an admin (server log).";
  if (!{PKG}.BankStore.coinsReady()) return "-SkyyCoins is not loaded, the bank cannot move coins.";
  if (!{PKG}.BankStore.readable(u)) return "-Your bank account file cannot be read right now, so nothing can move. Try again; if it keeps happening tell an admin (server log).";
  if (amountText == null) return "=How much? e.g. /bank " + (dep ? "deposit" : "withdraw") + " 500  (or all, 2k, 1.5m)";
  long all = 0L;
  if (isAll(amountText)) {{
    all = dep ? {PKG}.BankStore.purseOr(u) : {PKG}.BankStore.get(u);
    if (all < 0L) return purseBad;
  }}
  long n;
  try {{ n = parseAmount(amountText, all); }}
  catch (Throwable t) {{ return "-That is not a number. Use e.g. 500, 2k, 1.5m or all."; }}
  if (n <= 0L) return "-Nothing to " + (dep ? "deposit" : "withdraw") + ".";
  int r = dep ? {PKG}.BankStore.deposit(u, n) : {PKG}.BankStore.withdraw(u, n);
  if (r == 5) return purseBad;
  if (r == 3) return "-Your profile changed, nothing was moved. Try again.";
  if (r == 4) return "-Your bank account file cannot be read right now, nothing was moved. Try again; if it keeps happening tell an admin (server log).";
  if (r == 2) return "=Your profile changed during this " + (dep ? "deposit: the " + n + " coins went into" : "withdrawal: the " + n + " coins came out of") + " the bank of the profile you started it on.";
  if (dep) {{
    if (r != 1) return "-Not enough coins in your purse (" + {PKG}.BankStore.purseNum(u) + ").";
    return "+Deposited " + n + " coins. Bank: " + {PKG}.BankStore.get(u) + "  |  Purse: " + {PKG}.BankStore.purseNum(u);
  }}
  if (r != 1) return "-Not enough coins in the bank (" + {PKG}.BankStore.get(u) + ").";
  return "+Withdrew " + n + " coins. Bank: " + {PKG}.BankStore.get(u) + "  |  Purse: " + {PKG}.BankStore.purseNum(u);
}}""", cmd))
# 0.1.3: 0.1.2's "/bank" chat status (two lines), now /bank status | /bank info, and the fallback when the page cannot open.
cmd.addMethod(CtNewMethod.make(f"""
public static void status({PR} pr, java.util.UUID u) {{
  pr.sendMessage({MSG}.raw("[Bank] Bank: " + {PKG}.BankStore.get(u) + " coins  |  Purse: " + {PKG}.BankStore.purseCoins(u)));
  pr.sendMessage({MSG}.raw("[Bank] Interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min (on up to " + {PKG}.BankConfig.MAX_PRINCIPAL + "). Bank coins are safe on death. /bank deposit|withdraw <amount|all>"));
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
public static void run({PR} pr, String actionText, String amountText) {{
  java.util.UUID u = pr.getUuid();
  try {{
    if (!{PKG}.BankStore.coinsReady()) {{ pr.sendMessage({MSG}.raw("[Bank] SkyyCoins is not loaded, the bank cannot move coins.")); return; }}
    if (!{PKG}.BankStore.readable(u)) {{ pr.sendMessage({MSG}.raw("[Bank] Your bank account file cannot be read right now, so nothing can move. Try again; if it keeps happening tell an admin (server log).")); return; }}
    if (actionText == null) {{ status(pr, u); return; }}
    String action = actionText.trim().toLowerCase();
    if (action.equals("balance") || action.equals("bal")) {{
      pr.sendMessage({MSG}.raw("[Bank] Bank: " + {PKG}.BankStore.get(u) + " coins  |  Purse: " + {PKG}.BankStore.purseCoins(u)));
      return;
    }}
    if (action.equals("status") || action.equals("info")) {{ status(pr, u); return; }}
    boolean dep = action.startsWith("dep") || action.equals("d") || action.equals("put");
    boolean wd = action.startsWith("with") || action.equals("w") || action.equals("take");
    if (!dep && !wd) {{ pr.sendMessage({MSG}.raw("[Bank] Usage: /bank deposit <amount|all>  or  /bank withdraw <amount|all>")); return; }}
    String res = move(u, dep, amountText);
    pr.sendMessage({MSG}.raw("[Bank] " + res.substring(1)));
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

# ================= BankPage (0.1.3; inline, rebuilt only after a click) =================
# Written with @TOKEN@ placeholders instead of f-strings (the markup is full of braces): jv() fills them in.
TOK = {"PKG": PKG, "PR": PR, "REF": REF, "ST": ST, "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT, "LIFE": LIFE}
TOKEN = re.compile(r"@([A-Z]{2,5})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in TOK:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return TOK[k]
    return TOKEN.sub(rep, src)


def PM(src):
    try:
        page.addMethod(CtNewMethod.make(jv(src), page))
    except Exception as e:
        raise SystemExit("compile failed in BankPage:\n%s\n---\n%s" % (e, jv(src)[:1500]))


page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String keepAmount;", page))
page.addConstructor(CtNewConstructor.make(jv(r"""
public BankPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.info = "";
  this.keepAmount = "";
}"""), page))
PM(r"""
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr / SkyyGuilds 0.1 GuildPage.jsonStr, verbatim)
PM(r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) {
      char n = data.charAt(i + 1);
      if (n == 'u' && i + 5 < data.length()) {
        try { sb.append((char) Integer.parseInt(data.substring(i + 2, i + 6), 16)); } catch (Throwable t) { }
        i += 6;
        continue;
      }
      if (n == 'n' || n == 'r' || n == 't' || n == 'b' || n == 'f') sb.append(' '); else sb.append(n);
      i += 2;
      continue;
    }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
# 12345678 -> "12,345,678" (no Locale: the same separator for every player)
PM(r"""
public static String fmt(long n) {
  boolean neg = n < 0L;
  String s = String.valueOf(neg ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (neg) sb.append('-');
  return sb.reverse().toString();
}""")
PM(r"""
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#7fe07f";
  if (c == '-') return "#ff8080";
  return "#8fc8ff";
}""")
PM(r"""
public static String textOf(String res) {
  if (res == null || res.length() == 0) return "";
  char c = res.charAt(0);
  if (c == '+' || c == '-' || c == '=') return res.substring(1);
  return res;
}""")
# 2475000 ms -> "41 min 15 s"; 7500000 -> "2 h 5 min"
PM(r"""
public static String dur(long ms) {
  long s = (ms + 999L) / 1000L;
  if (s < 1L) s = 1L;
  long h = s / 3600L;
  long m = (s % 3600L) / 60L;
  long sec = s % 60L;
  if (h > 0L) return h + " h " + m + " min";
  if (m > 0L) return m + " min " + sec + " s";
  return sec + " s";
}""")
PM(r"""
public static String every(int mins) {
  if (mins >= 60 && mins % 60 == 0) {
    int h = mins / 60;
    return h == 1 ? "hour" : h + " hours";
  }
  return mins == 1 ? "minute" : mins + " minutes";
}""")
PM(r"""
public static String subText(java.util.UUID u) {
  String s = "Coins in the bank earn interest and are never lost when you die.";
  try {
    java.util.Map br = @PKG@.BankStore.bridge();
    Object n = br.get("profile:name:" + u.toString());
    Object c = br.get("profile:class:" + u.toString());
    if (n instanceof String && ((String) n).length() > 0) {
      String cl = (c instanceof String && ((String) c).length() > 0) ? " (" + c + ")" : "";
      return "Profile " + n + cl + "  -  every profile has its own bank. " + s;
    }
  } catch (Throwable t) { }
  return s;
}""")
PM(r"""
public static String rateText(int pct, int mins, long max) {
  if (pct <= 0) return "Interest is switched off on this server.";
  return "Interest: " + pct + "% every " + every(mins) + ", paid on up to " + fmt(max) + " coins";
}""")
# lastInterestMillis + intervalMinutes = the next due time; BankTick checks every 30 s, so a due payout lands within ~30 s
PM(r"""
public static String nextText(int pct, long leftMs) {
  if (pct <= 0) return "No interest is paid while it is switched off.";
  if (leftMs <= 0L) return "Next interest: any moment now";
  return "Next interest: in " + dur(leftMs) + "   (Refresh to update)";
}""")
# one period of payInterest's maths: min(balance, max) * pct / 100 (integer), shown before it is paid
PM(r"""
public static String gainText(boolean readable, long bank, int pct, long max) {
  if (!readable) return "Your bank account cannot be read right now - nothing can move. Tell an admin if this stays.";
  if (pct <= 0) return "Bank coins are still safe when you die.";
  long principal = bank < max ? bank : max;
  long gain = principal * (long) pct / 100L;
  if (gain > 0L) return "Your next payout: +" + fmt(gain) + " coins" + (bank > max ? "   (interest is paid on the first " + fmt(max) + " coins)" : "");
  if (bank <= 0L) return "Deposit coins to start earning interest.";
  long need = (100L + (long) pct - 1L) / (long) pct;
  return "Deposit at least " + fmt(need) + " coins to earn interest.";
}""")
PM(r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  boolean coins = false;
  try { coins = @PKG@.BankStore.coinsReady(); } catch (Throwable t) { }
  boolean readable = false;
  try { readable = @PKG@.BankStore.readable(u); } catch (Throwable t) { }
  long purse = coins ? @PKG@.BankStore.purseOr(u) : -1L;
  long bank = 0L;
  if (readable) { try { bank = @PKG@.BankStore.get(u); } catch (Throwable t) { readable = false; } }
  int pct = @PKG@.BankConfig.PERCENT;
  int mins = @PKG@.BankConfig.MINUTES;
  long max = @PKG@.BankConfig.MAX_PRINCIPAL;
  long left = @PKG@.BankConfig.LAST + (long) mins * 60000L - System.currentTimeMillis();
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 20);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 20);
  String ns = style("#2a3444", "#3a475c", "#1a2230", "#e6f2ff", 18);
  String cap = "Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }";
  b.appendInline((String) null, "Group #SkyyBank { Anchor: (Width: 1100, Height: 680); Background: #0b1524(0.96); Padding: (Horizontal: 28, Vertical: 16); LayoutMode: Top; }");
  b.appendInline("#SkyyBank", "Group { Anchor: (Height: 3); Background: #ffd070; }");
  b.appendInline("#SkyyBank", "Label { Anchor: (Height: 58); Text: \"Bank\"; Style: (FontSize: 34, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyBank", "Label #SkyyBSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBSub.Text", subText(u));
  b.appendInline("#SkyyBank", "Label { Anchor: (Height: 12); Text: \"\"; }");
  b.appendInline("#SkyyBank", "Group #SkyyBBal { Anchor: (Height: 132); LayoutMode: Left; }");
  b.appendInline("#SkyyBBal", "Group #SkyyBPurseBox { Anchor: (Width: 510, Height: 132); Background: #142236; LayoutMode: Top; Padding: (Top: 10); }");
  b.appendInline("#SkyyBPurseBox", "Label { Anchor: (Height: 34); Text: \"Purse\"; Style: (FontSize: 21, RenderBold: true, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyBPurseBox", "Label #SkyyBPurse { Anchor: (Height: 60); Text: \"\"; Style: (FontSize: 40, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBPurse.Text", purse >= 0L ? fmt(purse) : (coins ? "unreadable" : "no SkyyCoins"));
  b.appendInline("#SkyyBPurseBox", "Label { Anchor: (Height: 24); Text: \"coins you carry - lost in part when you die\"; " + cap);
  b.appendInline("#SkyyBBal", "Label { Anchor: (Width: 24, Height: 132); Text: \"\"; }");
  b.appendInline("#SkyyBBal", "Group #SkyyBBankBox { Anchor: (Width: 510, Height: 132); Background: #2a2410; LayoutMode: Top; Padding: (Top: 10); }");
  b.appendInline("#SkyyBBankBox", "Label { Anchor: (Height: 34); Text: \"Bank\"; Style: (FontSize: 21, RenderBold: true, TextColor: #ffd070, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyBBankBox", "Label #SkyyBBalance { Anchor: (Height: 60); Text: \"\"; Style: (FontSize: 40, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBBalance.Text", readable ? fmt(bank) : "unreadable");
  b.appendInline("#SkyyBBankBox", "Label { Anchor: (Height: 24); Text: \"coins in the bank - safe when you die\"; " + cap);
  b.appendInline("#SkyyBank", "Label { Anchor: (Height: 16); Text: \"\"; }");
  b.appendInline("#SkyyBank", "Group #SkyyBInt { Anchor: (Height: 118); Background: #101c2c; LayoutMode: Top; Padding: (Top: 8); }");
  b.appendInline("#SkyyBInt", "Label #SkyyBRate { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 21, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBRate.Text", rateText(pct, mins, max));
  b.appendInline("#SkyyBInt", "Label #SkyyBNext { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 21, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBNext.Text", nextText(pct, left));
  b.appendInline("#SkyyBInt", "Label #SkyyBGain { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: #7fe07f, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBGain.Text", gainText(readable, bank, pct, max));
  b.appendInline("#SkyyBank", "Label { Anchor: (Height: 20); Text: \"\"; }");
  b.appendInline("#SkyyBank", "Group #SkyyBCtl { Anchor: (Height: 62); LayoutMode: Left; }");
  b.appendInline("#SkyyBCtl", "TextButton #SkyyBDepAll { Anchor: (Width: 200, Height: 60); Text: \"Deposit all\"; " + gs + " }");
  b.appendInline("#SkyyBCtl", "Label { Anchor: (Width: 42, Height: 60); Text: \"\"; }");
  b.appendInline("#SkyyBCtl", "Group #SkyyBAmtBox { Anchor: (Width: 240, Height: 60); Background: #16263a; }");
  b.appendInline("#SkyyBAmtBox", "TextField #SkyyBAmount { Anchor: (Full: 0); Padding: (Horizontal: 14); MaxLength: 16; PlaceholderText: \"Amount\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 22); Style: (TextColor: #ffffff, FontSize: 22); }");
  if (this.keepAmount != null && this.keepAmount.length() > 0) b.set("#SkyyBAmount.Value", this.keepAmount);
  b.appendInline("#SkyyBCtl", "Label { Anchor: (Width: 10, Height: 60); Text: \"\"; }");
  b.appendInline("#SkyyBCtl", "TextButton #SkyyBDep { Anchor: (Width: 150, Height: 60); Text: \"Deposit\"; " + gs + " }");
  b.appendInline("#SkyyBCtl", "Label { Anchor: (Width: 10, Height: 60); Text: \"\"; }");
  b.appendInline("#SkyyBCtl", "TextButton #SkyyBWd { Anchor: (Width: 150, Height: 60); Text: \"Withdraw\"; " + bs + " }");
  b.appendInline("#SkyyBCtl", "Label { Anchor: (Width: 42, Height: 60); Text: \"\"; }");
  b.appendInline("#SkyyBCtl", "TextButton #SkyyBWdAll { Anchor: (Width: 200, Height: 60); Text: \"Withdraw all\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyBDepAll", @EVD@.of("a", "depall").append("@BAmount", "#SkyyBAmount.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyBWdAll", @EVD@.of("a", "wdall").append("@BAmount", "#SkyyBAmount.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyBDep", @EVD@.of("a", "deposit").append("@BAmount", "#SkyyBAmount.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyBWd", @EVD@.of("a", "withdraw").append("@BAmount", "#SkyyBAmount.Value"));
  ev.addEventBinding(@BT@.Validating, "#SkyyBAmount", @EVD@.of("a", "amount").append("@BAmount", "#SkyyBAmount.Value"), false);
  b.appendInline("#SkyyBank", "Group #SkyyBCap { Anchor: (Height: 28); LayoutMode: Left; }");
  b.appendInline("#SkyyBCap", "Label { Anchor: (Width: 200, Height: 28); Text: \"your whole purse\"; " + cap);
  b.appendInline("#SkyyBCap", "Label { Anchor: (Width: 42, Height: 28); Text: \"\"; }");
  b.appendInline("#SkyyBCap", "Label #SkyyBCapMid { Anchor: (Width: 560, Height: 28); Text: \"\"; " + cap);
  b.set("#SkyyBCapMid.Text", "type 500, 2k, 1.5m or all - then click Deposit or Withdraw");
  b.appendInline("#SkyyBCap", "Label { Anchor: (Width: 42, Height: 28); Text: \"\"; }");
  b.appendInline("#SkyyBCap", "Label { Anchor: (Width: 200, Height: 28); Text: \"your whole bank\"; " + cap);
  b.appendInline("#SkyyBank", "Label { Anchor: (Height: 12); Text: \"\"; }");
  b.appendInline("#SkyyBank", "Label #SkyyBInfo { Anchor: (Height: 36); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBInfo.Text", textOf(this.info));
  b.appendInline("#SkyyBank", "Label #SkyyBChat { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyBChat.Text", "Chat works too: /bank deposit 500, /bank withdraw all, /bank balance");
  b.appendInline("#SkyyBank", "Group #SkyyBBottom { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyBBottom", "Label { Anchor: (Width: 342, Height: 46); Text: \"\"; }");
  b.appendInline("#SkyyBBottom", "TextButton #SkyyBRefresh { Anchor: (Width: 170, Height: 46); Text: \"Refresh\"; " + ns + " }");
  b.appendInline("#SkyyBBottom", "Label { Anchor: (Width: 20, Height: 46); Text: \"\"; }");
  b.appendInline("#SkyyBBottom", "TextButton #SkyyBClose { Anchor: (Width: 170, Height: 46); Text: \"Close\"; " + ns + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyBRefresh", @EVD@.of("a", "refresh").append("@BAmount", "#SkyyBAmount.Value"));
  ev.addEventBinding(@BT@.Activating, "#SkyyBClose", @EVD@.of("a", "close"));
}""")
# clicks run on the player's world thread (page events), like the /bank chat commands. Every coin move is BankCmd.move = the chat path.
PM(r"""
public String typed(String data) {
  String t = jsonStr(data, "@BAmount").trim();
  if (t.length() > 16) t = t.substring(0, 16);
  return t;
}""")
PM(r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { close(); return; }
    java.util.UUID u = this.playerRef.getUuid();
    String t = typed(data);
    String res = null;
    this.keepAmount = t;
    if (a.equals("refresh")) {
      res = "";
    } else if (a.equals("depall") || a.equals("wdall")) {
      boolean dep = a.equals("depall");
      try { res = @PKG@.BankCmd.move(u, dep, "all"); }
      catch (Throwable t1) { @PKG@.BankStore.warn("bank page " + a + " failed: " + t1); res = "-Something went wrong - the server log has the details."; }
    } else if (a.equals("deposit") || a.equals("withdraw")) {
      boolean dep = a.equals("deposit");
      if (t.length() == 0) {
        res = "=Type an amount in the box first (500, 2k, 1.5m or all), then click " + (dep ? "Deposit." : "Withdraw.");
      } else {
        try { res = @PKG@.BankCmd.move(u, dep, t); }
        catch (Throwable t2) { @PKG@.BankStore.warn("bank page " + a + " failed: " + t2); res = "-Something went wrong - the server log has the details."; }
        if (res != null && res.startsWith("+")) this.keepAmount = "";
      }
    } else if (a.equals("amount")) {
      if (t.length() == 0) res = "=Type an amount (500, 2k, 1.5m or all), then click Deposit or Withdraw.";
      else res = "=Click Deposit or Withdraw to move " + t + " coins. Enter alone never moves coins.";
    } else {
      return;
    }
    this.info = res == null ? "" : res;
    rebuild();
  } catch (Throwable ex) { @PKG@.BankStore.warn("bank page click failed: " + ex); }
}""")

# 0.1.3: /bank with no arguments opens the page (on the world thread, straight from the command: never close-then-open).
# No Player component (should not happen for a player command) -> 0.1.2's chat status instead.
cmd.addMethod(CtNewMethod.make(f"""
public static void openPage({REF} ref, {ST} store, {PR} pr) {{
  try {{
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p != null) {{ p.getPageManager().openCustomPage(ref, store, new {PKG}.BankPage(pr)); return; }}
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("could not open the bank page: " + t); }}
  run(pr, (String) null, (String) null);
}}""", cmd))

# ---- usage variant /bank <action>   (description-only constructor, like vanilla WhereAmIOtherCommand / SkyyEssentials TpAcceptNamedCmd)
cmdA.addField(CtField.make(f"public {RA} actionArg;", cmdA))
cmdA.addConstructor(CtNewConstructor.make(f"""
public BankActionCmd() {{
  super("Show your bank and purse in chat: /bank balance or /bank status");
  this.actionArg = withRequiredArg("action", "balance | status (deposit and withdraw also need an amount)", {ATY}.STRING);
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
  super("bank", "Bank: /bank opens the bank page | /bank balance | /bank status | /bank deposit <amount|all> | /bank withdraw <amount|all>");
  this.actionArg = withOptionalArg("action", "deposit | withdraw (omit to open the bank page)", {ATY}.STRING);
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
  if (a == null && n == null) {{ {PKG}.BankCmd.openPage(ref, store, pr); return; }}
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
  {PKG}.BankTick.WORKER = java.util.concurrent.Executors.newSingleThreadExecutor({TUT}.daemon("SkyyBank"));
  this.ticker ={HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.BankTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyBank] {VERSION} ready - /bank (page), interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min (coins bridge " + ({PKG}.BankStore.coinsReady() ? "found" : "NOT found yet") + ", profiles bridge " + ({PKG}.BankStore.bridge().get("profile:fn:key") instanceof java.util.function.Function ? "found" : "not found yet: one account per player") + ")");
}}""", pl))
# 0.1.3: the worker finishes what it already has (a sweep in progress writes its files atomically) and then ends; daemon thread.
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ if ({PKG}.BankTick.WORKER != null) {PKG}.BankTick.WORKER.shutdown(); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (bs, cfg, tick, job, cmd, cmdA, cmdN, adm, admS, admM, page, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)
m = B.manifest("SkyyBank", VERSION, "SkyWynn bank: /bank opens the bank page (deposit / withdraw, interest), death-safe savings with periodic interest, one account per profile. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyBankPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
