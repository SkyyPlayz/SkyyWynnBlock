"""SkyyCoins 0.1.5 - build script (javassist via jpype).
Run:   python build_skyycoins_0.1.5.py            -> SkyyCoins/SkyyCoins-0.1.5.jar
       python build_skyycoins_0.1.5.py --deploy   -> also copies to Mods/SkyyCoins.jar and enables it in the HUD mod world
Fixes vs 0.1 (code review 2026-09-22): atomic /pay transfer (synchronized ledger), permission gates on
/coinsgive and /deathpenalty, config range validation, world-thread re-check in the death task,
atomic file writes, logged I/O failures, ticker cancelled on shutdown, DEAD/GRANTED maps pruned,
/deathpenalty with no argument shows the current setting.
0.1.5: per-profile storage (tools/PROFILES-CONTRACT.md). Balance files are balances/<pkey>.properties where pkey(uuid) is the
  contract helper (bridge "profile:fn:key"); without SkyyProfiles pkey = uuid.toString() = profile 1, so the existing files ARE
  profile 1 (no migration) and everything behaves exactly like 0.1.4. BAL / LOADED and the starter-coin guard GRANTED are keyed by
  the pkey String (rule 2). Every ledger op resolves pkey ONCE, outside the ledger lock (SkyyProfiles' function is never called while
  the lock is held), then runs ONE synchronized *K method on that key (transfer = both sides under one lock), so an op never
  straddles a profile switch. Starter coins per profile: a profile with no balance file gets 10,000 on its first tick (a new
  profile starts fresh; profile N >= 2 gets a "New profile" message). coins:fn:get/add/take act on the ACTIVE profile.
  coins:<uuid> stays keyed by UUID and always shows the ACTIVE profile (rule 3): CoinTick (1 s) remembers the last
  profile:epoch:<uuid> per UUID and on a change flags that player's CoinTask (republish = true), which republishes on the player's
  world thread - CoinTick itself never touches the balance files (review fix: no disk I/O or ledger lock on the shared scheduler
  thread, same as 0.1.4); the epoch is only recorded once the flagged task is handed to a world, so a player without a world
  yet is retried next tick. Each op also re-resolves pkey afterwards and republishes if the profile switched mid-op. /balance
  names the active profile (profile:name:<uuid>) when SkyyProfiles publishes one. Death state (DEAD) stays per player. Nothing
  touches the inventory (rule 5).
0.1.4: (1) /balance (bal, coins, purse) and /pay <player> <amount> are open to ordinary players: their constructors call
  setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as SkyyEssentials 0.1).
  Before, CommandRegistry.registerCommand -> AbstractCommand.setOwner() gave them an auto node like
  "skyy.0.1.3_skyycoins.command.balance" that only "*" admins had. /coinsgive and /deathpenalty keep requirePermission("skyycoins.admin").
  (2) /deathpenalty 5% and /deathpenalty 5%-10% work positionally. The spec used to be an OPTIONAL arg, which the parser only
  accepts as "--percent 5%" (acceptCall0 needs positional token count == required arg count, so "/deathpenalty 5%" failed with
  wrongNumberRequiredParameters). Now DeathPenaltySetCmd is a usage variant (description-only constructor, one withRequiredArg
  "percent") with its OWN requirePermission("skyycoins.admin"). /deathpenalty alone still shows the current setting, and
  /deathpenalty --percent 5% still works (the parent keeps its optional arg). Parse/apply logic is DeathPenaltyCmd.applySpec().
  Engine checks (HytaleServer.jar bytecode, 2026-09-23): acceptCall0 calls checkForExecutingSubcommands FIRST, which picks
  variantCommands.get(<positional token count>) when that count differs from the parent's own required count (0 here), and
  runs the variant's acceptCall0 -> the variant's own hasPermission(); the parent's hasPermission() is never reached, hence
  the variant's own requirePermission. A variant (with a parent, no permission groups) also re-checks parent.hasPermission().
  addUsageVariant keys by the variant's required count and completeRegistration rejects a variant whose count equals the
  parent's (1 vs 0 is fine). Tokenizer only treats quotes, backslash and [ , ] specially, so "5%-10%" is one token.
  Plugin setup() (registerCommand) runs in PluginManager.setup() before PermissionsModule.start() -> refreshVirtualGroups()
  -> CommandManager.createVirtualPermissionGroups() reads getPermissionGroupsRecursive(), so the Adventurer grant is picked up.
0.1.3: publishes bridge FUNCTIONS (java.util.function.Function objects) so other Skyy mods can get/add/take coins with zero deps:
  "coins:fn:get"  apply(UUID) -> Long balance
  "coins:fn:add"  apply(Object[]{UUID, Long delta}) -> Long new balance (delta may be negative, clamps at 0)
  "coins:fn:take" apply(Object[]{UUID, Long amount}) -> Boolean (false = not enough, nothing taken)
0.1.2: publishes balances to the JVM bridge (System property "skyy.bridge", key "coins:<uuid>") so SkyyHud can show a Coins widget without a dependency.
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
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
DC  = "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent"
LOG = "com.hypixel.hytale.logger.HytaleLogger"

for c, m in ((DC, "getComponentType"), (HSV, "SCHEDULED_EXECUTOR"), (CTX, "provided"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "setPermissionGroups"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addUsageVariant"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

PKG = "com.skyy.coins"
# vanilla player permission group (like /help /who /ping): every player without an explicit group is in it
ADV = 'setPermissionGroups(new String[] { "hytale:Adventurer" });'
cs   = pool.makeClass(PKG + ".CoinStore")
cfg  = pool.makeClass(PKG + ".CoinConfig")
task = pool.makeClass(PKG + ".CoinTask")
tick = pool.makeClass(PKG + ".CoinTick")
bal  = pool.makeClass(PKG + ".BalanceCmd", pool.get(APC))
pay  = pool.makeClass(PKG + ".PayCmd", pool.get(APC))
give = pool.makeClass(PKG + ".GiveCmd", pool.get(APC))
dp   = pool.makeClass(PKG + ".DeathPenaltyCmd", pool.get(APC))
dps  = pool.makeClass(PKG + ".DeathPenaltySetCmd", pool.get(APC))
fn   = pool.makeClass(PKG + ".CoinFn")
pl   = pool.makeClass(PKG + ".SkyyCoinsPlugin", pool.get(JP))

# ================= CoinStore (synchronized ledger, atomic file writes, per profile) =================
# PROFILES-CONTRACT rule 2: BAL / LOADED are keyed by the profile storage key String from pkey(uuid), not by the UUID.
# Public ops (known/get/set/add/take/transfer) are NOT synchronized: they resolve pkey once, outside the ledger lock, then call ONE
# synchronized *K method on that key, then recheck() the active key and republish coins:<uuid> if the profile switched meanwhile.
# The synchronized *K methods never call pkey (so SkyyProfiles' function is never called while the ledger lock is held).
cs.addField(CtField.make("public static java.nio.file.Path DIR;", cs))
cs.addField(CtField.make(f"public static {LOG} LOG;", cs))
cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAL = new java.util.concurrent.ConcurrentHashMap();", cs))
cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOADED = new java.util.concurrent.ConcurrentHashMap();", cs))
cs.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCoins] " + msg); } catch (Throwable t) { }
}""", cs))
# tools/PROFILES-CONTRACT.md helper, verbatim: storage key of the player's ACTIVE profile ("<uuid>" = profile 1, "<uuid>-pN" = N).
# Without SkyyProfiles it is always uuid.toString(), i.e. exactly the 0.1.4 file names.
cs.addMethod(CtNewMethod.make("""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""", cs))
# balances/<k>.properties is read once per key; the first successful load publishes coins:<uuid> (as 0.1.4 load() did)
cs.addMethod(CtNewMethod.make("""
public static synchronized void loadK(java.util.UUID u, String k) {
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
    Long cur = (Long) BAL.get(k);
    bridge().put("coins:" + u.toString(), cur == null ? Long.valueOf(0L) : cur);
  } catch (Throwable t) { warn("could not load balance for " + k + ": " + t); }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized boolean knownK(java.util.UUID u, String k) {
  loadK(u, k);
  return BAL.containsKey(k);
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized long getK(java.util.UUID u, String k) {
  loadK(u, k);
  Long v = (Long) BAL.get(k);
  return v == null ? 0L : v.longValue();
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized void setK(java.util.UUID u, String k, long v) {
  if (v < 0L) v = 0L;
  loadK(u, k);
  BAL.put(k, Long.valueOf(v));
  bridge().put("coins:" + u.toString(), Long.valueOf(v));
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("balance", String.valueOf(v));
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyCoins"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(k + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save balance for " + k + ": " + t); }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized long addK(java.util.UUID u, String k, long d) {
  long v = getK(u, k) + d;
  if (v < 0L) v = 0L;
  setK(u, k, v);
  return v;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized boolean takeK(java.util.UUID u, String k, long amount) {
  if (amount <= 0L) return false;
  long have = getK(u, k);
  if (have < amount) return false;
  setK(u, k, have - amount);
  return true;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized boolean transferK(java.util.UUID from, String kf, java.util.UUID to, String kt, long amount) {
  if (amount <= 0L) return false;
  long have = getK(from, kf);
  if (have < amount) return false;
  setK(from, kf, have - amount);
  addK(to, kt, amount);
  return true;
}""", cs))
# starter coins, once per profile key: only a key with no balance yet (no file) is granted - atomic check + set
cs.addMethod(CtNewMethod.make("""
public static synchronized boolean starterK(java.util.UUID u, String k, long amount) {
  loadK(u, k);
  if (BAL.containsKey(k)) return false;
  setK(u, k, amount);
  return true;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static synchronized void publishK(java.util.UUID u, String k) {
  bridge().put("coins:" + u.toString(), Long.valueOf(getK(u, k)));
}""", cs))
# coins:<uuid> = balance of the ACTIVE profile (PROFILES-CONTRACT rule 3); called by CoinTask (world thread, never the scheduler
# thread: it may read the balance file and takes the ledger lock) when CoinTick flagged a profile:epoch:<uuid> change
cs.addMethod(CtNewMethod.make("""
public static void publish(java.util.UUID u) {
  try { publishK(u, pkey(u)); } catch (Throwable t) { warn("could not publish balance for " + u + ": " + t); }
}""", cs))
# after an op on key k: if the active profile changed meanwhile, coins:<uuid> must show the new active profile, not k
cs.addMethod(CtNewMethod.make("""
public static void recheck(java.util.UUID u, String k) {
  try {
    String now = pkey(u);
    if (!now.equals(k)) publishK(u, now);
  } catch (Throwable t) { }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static boolean known(java.util.UUID u) {
  String k = pkey(u);
  boolean r = knownK(u, k);
  recheck(u, k);
  return r;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static long get(java.util.UUID u) {
  String k = pkey(u);
  long r = getK(u, k);
  recheck(u, k);
  return r;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static void set(java.util.UUID u, long v) {
  String k = pkey(u);
  setK(u, k, v);
  recheck(u, k);
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static long add(java.util.UUID u, long d) {
  String k = pkey(u);
  long r = addK(u, k, d);
  recheck(u, k);
  return r;
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static boolean transfer(java.util.UUID from, java.util.UUID to, long amount) {
  String kf = pkey(from);
  String kt = pkey(to);
  boolean ok = transferK(from, kf, to, kt, amount);
  recheck(from, kf);
  recheck(to, kt);
  return ok;
}""", cs))

cs.addMethod(CtNewMethod.make("""
public static boolean take(java.util.UUID u, long amount) {
  String k = pkey(u);
  boolean ok = takeK(u, k, amount);
  recheck(u, k);
  return ok;
}""", cs))

# ================= CoinFn (bridge functions) =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addField(CtField.make("public String mode;", fn))
fn.addConstructor(CtNewConstructor.make("public CoinFn(String mode) { this.mode = mode; }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    if ("get".equals(mode)) {{
      if (!(arg instanceof java.util.UUID)) return Long.valueOf(0L);
      return Long.valueOf({PKG}.CoinStore.get((java.util.UUID) arg));
    }}
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];
    long n = ((Number) a[1]).longValue();
    if ("add".equals(mode)) return Long.valueOf({PKG}.CoinStore.add(u, n));
    if ("take".equals(mode)) return Boolean.valueOf({PKG}.CoinStore.take(u, n));
    return null;
  }} catch (Throwable t) {{ {PKG}.CoinStore.warn("bridge fn " + mode + " failed: " + t); return null; }}
}}""", fn))

# ================= CoinConfig =================
cfg.addField(CtField.make("public static java.nio.file.Path FILE;", cfg))
cfg.addField(CtField.make("public static volatile int MIN = 10;", cfg))
cfg.addField(CtField.make("public static volatile int MAX = 25;", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static void save() {{
  try {{
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("penaltyMin", String.valueOf(MIN));
    p.setProperty("penaltyMax", String.valueOf(MAX));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyyCoins config - death penalty percent range"); }} finally {{ out.close(); }}
  }} catch (Throwable t) {{ {PKG}.CoinStore.warn("could not save config: " + t); }}
}}""", cfg))

cfg.addMethod(CtNewMethod.make(f"""
public static void load() {{
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{ save(); return; }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    int mn = Integer.parseInt(p.getProperty("penaltyMin", "10").trim());
    int mx = Integer.parseInt(p.getProperty("penaltyMax", "25").trim());
    if (mn < 0) mn = 0;
    if (mx > 100) mx = 100;
    if (mn > mx) {{ {PKG}.CoinStore.warn("config penaltyMin > penaltyMax, using defaults 10-25"); mn = 10; mx = 25; }}
    MIN = mn; MAX = mx;
  }} catch (Throwable t) {{ {PKG}.CoinStore.warn("could not load config: " + t); }}
}}""", cfg))
# ================= CoinTask (world thread) =================
# The epoch republish runs right after the validity check and BEFORE the world check: it touches no components (pkey + balance
# file + bridge only), so a task that lands on the old world's thread after a world switch still delivers it instead of dropping it.
task.addInterface(pool.get("java.lang.Runnable"))
task.addField(CtField.make(f"public {PR} pr;", task))
task.addField(CtField.make("public java.util.UUID expectedWorld;", task))
# set by CoinTick when profile:epoch:<uuid> changed: run() republishes coins:<uuid> for the active profile (off the scheduler thread)
task.addField(CtField.make("public boolean republish;", task))
task.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DEAD = new java.util.concurrent.ConcurrentHashMap();", task))
# DEAD is keyed by UUID (live player state); GRANTED by the profile key String (starter coins once per profile, rule 2)
task.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap GRANTED = new java.util.concurrent.ConcurrentHashMap();", task))
task.addConstructor(CtNewConstructor.make(f"public CoinTask({PR} pr, java.util.UUID w) {{ this.pr = pr; this.expectedWorld = w; }}", task))
task.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    if (this.republish) {PKG}.CoinStore.publish(pr.getUuid());
    java.util.UUID nowWorld = pr.getWorldUuid();
    if (nowWorld == null || !nowWorld.equals(this.expectedWorld)) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    java.util.UUID u = pr.getUuid();
    String k = {PKG}.CoinStore.pkey(u);
    if (GRANTED.putIfAbsent(k, Boolean.TRUE) == null && {PKG}.CoinStore.starterK(u, k, 10000L)) {{
      {PKG}.CoinStore.recheck(u, k);
      if (k.equals(u.toString())) pr.sendMessage({MSG}.raw("[SkyyCoins] Welcome! You received 10,000 starter coins. /balance to check."));
      else pr.sendMessage({MSG}.raw("[SkyyCoins] New profile: you received 10,000 starter coins. /balance to check."));
    }}
    Object death = st.getComponent(r, {DC}.getComponentType());
    boolean wasDead = DEAD.containsKey(u);
    if (death != null && !wasDead) {{
      DEAD.put(u, Boolean.TRUE);
      long balNow = {PKG}.CoinStore.getK(u, k);
      if (balNow > 0L) {{
        int min = {PKG}.CoinConfig.MIN; int max = {PKG}.CoinConfig.MAX;
        int pct = min >= max ? min : min + java.util.concurrent.ThreadLocalRandom.current().nextInt(max - min + 1);
        long loss = balNow * (long) pct / 100L;
        if (loss > 0L) {{
          long after = {PKG}.CoinStore.addK(u, k, -loss);
          {PKG}.CoinStore.recheck(u, k);
          pr.sendMessage({MSG}.raw("You died and lost " + loss + " coins (" + pct + "%). Balance: " + after));
        }}
      }}
    }} else if (death == null && wasDead) {{
      DEAD.remove(u);
    }}
  }} catch (Throwable t) {{ {PKG}.CoinStore.warn("death task failed: " + t); }}
}}""", task))

# ================= CoinTick (scheduler thread -> dispatch per world) =================
tick.addInterface(pool.get("java.lang.Runnable"))
# last profile:epoch:<uuid> seen per UUID (PROFILES-CONTRACT rule 3): a change republishes coins:<uuid> for the new active profile.
# Without SkyyProfiles the epoch key never exists and nothing happens. This runs on the SHARED scheduler thread, so it only DETECTS
# the change and sets CoinTask.republish; the publish itself (file read + ledger lock) runs in CoinTask on the world thread.
# EPOCH is updated only after w.execute() accepted the flagged task, so no world / a failed hand-off retries next tick.
tick.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();", tick))
tick.addConstructor(CtNewConstructor.make("public CoinTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.HashSet onlineKeys = new java.util.HashSet();
    java.util.Map br = {PKG}.CoinStore.bridge();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      onlineKeys.add({PKG}.CoinStore.pkey(u));
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      Object ep = null;
      boolean changed = false;
      try {{
        ep = br.get("profile:epoch:" + u.toString());
        Object last = EPOCH.get(u);
        if (ep != null) changed = !ep.equals(last); else changed = last != null;
      }} catch (Throwable te) {{ changed = false; {PKG}.CoinStore.warn("profile epoch check failed for " + u + ": " + te); }}
      {PKG}.CoinTask ct = new {PKG}.CoinTask(pr, wu);
      ct.republish = changed;
      w.execute(ct);
      if (changed) {{
        if (ep != null) EPOCH.put(u, ep); else EPOCH.remove(u);
      }}
    }}
    {PKG}.CoinTask.DEAD.keySet().retainAll(online);
    {PKG}.CoinTask.GRANTED.keySet().retainAll(onlineKeys);
    EPOCH.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", tick))

# ================= commands =================
bal.addConstructor(CtNewConstructor.make(f"""
public BalanceCmd() {{
  super("balance", "Check your coin balance");
  addAliases(new String[] {{ "bal", "coins", "purse" }});
  {ADV}
}}""", bal))
bal.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  String line = "Balance: " + {PKG}.CoinStore.get(u) + " coins";
  Object pn = {PKG}.CoinStore.bridge().get("profile:name:" + u.toString());
  if (pn instanceof String && ((String) pn).length() > 0) line = line + " (profile: " + pn + ")";
  pr.sendMessage({MSG}.raw(line));
}}""", bal))

pay.addField(CtField.make(f"public {RA} targetArg;", pay))
pay.addField(CtField.make(f"public {RA} amountArg;", pay))
pay.addConstructor(CtNewConstructor.make(f"""
public PayCmd() {{
  super("pay", "Send coins to another player");
  this.targetArg = withRequiredArg("player", "Player to pay", {ATY}.PLAYER_REF);
  this.amountArg = withRequiredArg("amount", "Coins to send", {ATY}.INTEGER);
  {ADV}
}}""", pay))
pay.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object t = ctx.get(this.targetArg);
    Object a = ctx.get(this.amountArg);
    if (t == null || a == null) {{ pr.sendMessage({MSG}.raw("Usage: /pay <player> <amount>")); return; }}
    {PR} target = ({PR}) t;
    long amount = (long) ((Integer) a).intValue();
    if (amount <= 0L) {{ pr.sendMessage({MSG}.raw("Amount must be positive.")); return; }}
    if (target.getUuid().equals(pr.getUuid())) {{ pr.sendMessage({MSG}.raw("You can't pay yourself.")); return; }}
    if (!target.isValid()) {{ pr.sendMessage({MSG}.raw("That player is not online.")); return; }}
    if (!{PKG}.CoinStore.transfer(pr.getUuid(), target.getUuid(), amount)) {{
      pr.sendMessage({MSG}.raw("Not enough coins (balance: " + {PKG}.CoinStore.get(pr.getUuid()) + ")."));
      return;
    }}
    pr.sendMessage({MSG}.raw("Paid " + amount + " coins to " + target.getUsername() + ". Balance: " + {PKG}.CoinStore.get(pr.getUuid())));
    target.sendMessage({MSG}.raw(pr.getUsername() + " paid you " + amount + " coins. Balance: " + {PKG}.CoinStore.get(target.getUuid())));
  }} catch (Throwable t2) {{
    {PKG}.CoinStore.warn("/pay failed: " + t2);
    pr.sendMessage({MSG}.raw("Pay failed. Usage: /pay <player> <amount>"));
  }}
}}""", pay))

give.addField(CtField.make(f"public {RA} amountArg;", give))
give.addConstructor(CtNewConstructor.make(f"""
public GiveCmd() {{
  super("coinsgive", "(admin) grant yourself coins");
  requirePermission("skyycoins.admin");
  this.amountArg = withRequiredArg("amount", "Coins to grant", {ATY}.INTEGER);
}}""", give))
give.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object a = ctx.get(this.amountArg);
    if (a == null) return;
    long amount = (long) ((Integer) a).intValue();
    if (amount <= 0L) {{ pr.sendMessage({MSG}.raw("Amount must be positive.")); return; }}
    long after = {PKG}.CoinStore.add(pr.getUuid(), amount);
    pr.sendMessage({MSG}.raw("Granted " + amount + ". Balance: " + after));
  }} catch (Throwable t) {{ {PKG}.CoinStore.warn("/coinsgive failed: " + t); }}
}}""", give))

dp.addField(CtField.make(f"public {OA} specArg;", dp))
# shared by /deathpenalty (show, or --percent <spec>) and the /deathpenalty <spec> variant; spec == null -> show current setting
dp.addMethod(CtNewMethod.make(f"""
public static void applySpec({PR} pr, String spec) {{
  int cmin = {PKG}.CoinConfig.MIN; int cmax = {PKG}.CoinConfig.MAX;
  String cur = cmin == cmax ? (cmin + "%") : (cmin + "%-" + cmax + "%");
  try {{
    if (spec == null) {{ pr.sendMessage({MSG}.raw("Death penalty is currently " + cur + " of carried coins. /deathpenalty 5% or /deathpenalty 5%-10% to change.")); return; }}
    String s = spec.trim().replace("%", "").replace(" ", "");
    int min; int max;
    int dash = s.indexOf('-');
    if (dash >= 0) {{
      min = Integer.parseInt(s.substring(0, dash));
      max = Integer.parseInt(s.substring(dash + 1));
    }} else {{
      min = Integer.parseInt(s); max = min;
    }}
    if (min < 0 || max > 100 || min > max) {{ pr.sendMessage({MSG}.raw("Invalid range. Use 0-100, min <= max.")); return; }}
    {PKG}.CoinConfig.MIN = min; {PKG}.CoinConfig.MAX = max;
    {PKG}.CoinConfig.save();
    pr.sendMessage({MSG}.raw("Death penalty set: " + (min == max ? (min + "%") : (min + "%-" + max + "%")) + " of carried coins."));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("Usage: /deathpenalty 5%  or  /deathpenalty 5%-10%   (currently " + cur + ")"));
  }}
}}""", dp))

# /deathpenalty <spec> - usage variant (description-only constructor). The engine dispatches to a variant BEFORE the
# parent's permission check, so the variant carries its own admin permission. Constructor + execute are added before
# DeathPenaltyCmd's constructor, which does addUsageVariant(new DeathPenaltySetCmd()).
dps.addField(CtField.make(f"public {RA} specArg;", dps))
dps.addConstructor(CtNewConstructor.make(f"""
public DeathPenaltySetCmd() {{
  super("(admin) Set death coin loss, e.g. 5% or 5%-10%");
  requirePermission("skyycoins.admin");
  this.specArg = withRequiredArg("percent", "e.g. 5% or 5%-10%", {ATY}.STRING);
}}""", dps))
dps.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String spec = "";
  try {{
    Object o = ctx.get(this.specArg);
    if (o != null) spec = o.toString();
  }} catch (Throwable t) {{ {PKG}.CoinStore.warn("/deathpenalty <spec> failed: " + t); }}
  {PKG}.DeathPenaltyCmd.applySpec(pr, spec);
}}""", dps))

dp.addConstructor(CtNewConstructor.make(f"""
public DeathPenaltyCmd() {{
  super("deathpenalty", "(admin) Set death coin loss, e.g. 5% or 5%-10%; no argument shows the current setting");
  requirePermission("skyycoins.admin");
  this.specArg = withOptionalArg("percent", "e.g. 5% or 5%-10%", {ATY}.STRING);
  addUsageVariant(new {PKG}.DeathPenaltySetCmd());
}}""", dp))
dp.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  String spec = null;
  try {{
    if (ctx.provided(this.specArg)) spec = String.valueOf(ctx.get(this.specArg));
  }} catch (Throwable t) {{ spec = ""; }}
  {PKG}.DeathPenaltyCmd.applySpec(pr, spec);
}}""", dp))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyCoinsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.CoinStore.LOG = getLogger();
  {PKG}.CoinStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyCoins").resolve("balances");
  {PKG}.CoinConfig.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCoins").resolve("config.properties");
  {PKG}.CoinConfig.load();
  getCommandRegistry().registerCommand(new {PKG}.BalanceCmd());
  getCommandRegistry().registerCommand(new {PKG}.PayCmd());
  getCommandRegistry().registerCommand(new {PKG}.GiveCmd());
  getCommandRegistry().registerCommand(new {PKG}.DeathPenaltyCmd());
  {PKG}.CoinStore.bridge().put("coins:fn:get", new {PKG}.CoinFn("get"));
  {PKG}.CoinStore.bridge().put("coins:fn:add", new {PKG}.CoinFn("add"));
  {PKG}.CoinStore.bridge().put("coins:fn:take", new {PKG}.CoinFn("take"));
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CoinTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCoins] {VERSION} ready - /balance /pay /deathpenalty (current " + {PKG}.CoinConfig.MIN + "%-" + {PKG}.CoinConfig.MAX + "%)");
}}""", pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.coins.CoinStore.bridge().remove("coins:fn:get"); com.skyy.coins.CoinStore.bridge().remove("coins:fn:add"); com.skyy.coins.CoinStore.bridge().remove("coins:fn:take"); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (cs, cfg, fn, task, tick, bal, pay, give, dp, dps, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyCoins-%s.jar" % VERSION)
m = B.manifest("SkyyCoins", VERSION, "SkyWynn economy core: coin ledger (per profile with SkyyProfiles), /balance, /pay, configurable death penalty (/deathpenalty 5% or 5%-10%), bridge functions for other Skyy mods. Zero dependencies.", PKG + ".SkyyCoinsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCoins.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCoins" % VERSION, disable_prefix="Skyy:")
