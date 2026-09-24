"""SkyyBank 0.1 - build script (javassist via jpype).
Run:   python build_skyybank_0.1.py            -> SkyyBank/SkyyBank-0.1.jar
       python build_skyybank_0.1.py --deploy   -> also copies to Mods/SkyyBank.jar and enables it in the HUD mod world
SkyBlock-style bank: /bank (status), /bank deposit <n|all>, /bank withdraw <n|all>.
Bank coins are death-safe by construction (SkyyCoins' death penalty only touches the purse).
Interest: every intervalMinutes (default 60 real minutes, counted from the last payout even across restarts)
every account earns interestPercent (default 2%) on min(balance, maxPrincipal 10,000,000). Offline players earn too.
Coins move through the SkyyCoins bridge functions (System property "skyy.bridge": coins:fn:get/add/take) -> zero deps;
if SkyyCoins is not loaded the commands say so. Publishes "bank:<uuid>" -> Long for a future HUD widget.
Admin: /bankconfig <percent> <minutes> [maxPrincipal]  (permission skyybank.admin).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
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
LOG = "com.hypixel.hytale.logger.HytaleLogger"

for c, m in ((HSV, "SCHEDULED_EXECUTOR"), (CTX, "provided"), (UNI, "getPlayers"), (PR, "getUuid"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

PKG = "com.skyy.bank"
bs   = pool.makeClass(PKG + ".BankStore")
cfg  = pool.makeClass(PKG + ".BankConfig")
tick = pool.makeClass(PKG + ".BankTick")
cmd  = pool.makeClass(PKG + ".BankCmd", pool.get(APC))
adm  = pool.makeClass(PKG + ".BankConfigCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyBankPlugin", pool.get(JP))

# ================= BankStore =================
bs.addField(CtField.make("public static java.nio.file.Path DIR;", bs))
bs.addField(CtField.make(f"public static {LOG} LOG;", bs))
bs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAL = new java.util.concurrent.ConcurrentHashMap();", bs))
bs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOADED = new java.util.concurrent.ConcurrentHashMap();", bs))
bs.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
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
# ---- ledger
bs.addMethod(CtNewMethod.make("""
public static synchronized void load(java.util.UUID u) {
  if (LOADED.containsKey(u)) return;
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      String v = p.getProperty("balance");
      if (v != null) BAL.put(u, Long.valueOf(Long.parseLong(v.trim())));
    }
    LOADED.put(u, Boolean.TRUE);
    Long cur = (Long) BAL.get(u);
    bridge().put("bank:" + u.toString(), cur == null ? Long.valueOf(0L) : cur);
  } catch (Throwable t) { warn("could not load account " + u + ": " + t); }
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized long get(java.util.UUID u) {
  load(u);
  Long v = (Long) BAL.get(u);
  return v == null ? 0L : v.longValue();
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized void set(java.util.UUID u, long v) {
  if (v < 0L) v = 0L;
  load(u);
  BAL.put(u, Long.valueOf(v));
  bridge().put("bank:" + u.toString(), Long.valueOf(v));
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("balance", String.valueOf(v));
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyBank"); } finally { out.close(); }
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (Throwable t) { warn("could not save account " + u + ": " + t); }
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized boolean deposit(java.util.UUID u, long n) {
  if (n <= 0L) return false;
  if (!purseTake(u, n)) return false;
  set(u, get(u) + n);
  return true;
}""", bs))
bs.addMethod(CtNewMethod.make("""
public static synchronized boolean withdraw(java.util.UUID u, long n) {
  if (n <= 0L) return false;
  long have = get(u);
  if (have < n) return false;
  if (!purseAdd(u, n)) return false;
  set(u, have - n);
  return true;
}""", bs))
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
        try { out.add(java.util.UUID.fromString(n.substring(0, n.length() - 11))); } catch (Throwable t) { }
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

# ================= BankTick (scheduler thread, every 30s) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public BankTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
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
      java.util.UUID u = (java.util.UUID) accounts.get(i);
      long total = 0L;
      for (long k = 0L; k < due; k++) {{
        long b = {PKG}.BankStore.get(u);
        long principal = b < {PKG}.BankConfig.MAX_PRINCIPAL ? b : {PKG}.BankConfig.MAX_PRINCIPAL;
        long gain = principal * (long) pct / 100L;
        if (gain <= 0L) break;
        {PKG}.BankStore.set(u, b + gain);
        total += gain;
      }}
      if (total > 0L) earned.put(u, Long.valueOf(total));
    }}
    {PKG}.BankConfig.LAST = {PKG}.BankConfig.LAST + due * interval;
    {PKG}.BankConfig.save();
    {PKG}.BankStore.info("interest paid to " + earned.size() + " account(s), " + due + " period(s) at " + pct + "%");
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      Long g = (Long) earned.get(pr.getUuid());
      if (g == null) continue;
      pr.sendMessage({MSG}.raw("[Bank] You earned " + g + " coins interest. Bank balance: " + {PKG}.BankStore.get(pr.getUuid())));
    }}
  }} catch (Throwable t) {{ {PKG}.BankStore.warn("interest tick failed: " + t); }}
}}""", tick))

# ================= /bank =================
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addField(CtField.make(f"public {OA} amountArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public BankCmd() {{
  super("bank", "Bank: /bank | /bank deposit <amount|all> | /bank withdraw <amount|all>");
  this.actionArg = withOptionalArg("action", "deposit | withdraw (omit to see balances)", {ATY}.STRING);
  this.amountArg = withOptionalArg("amount", "number or all", {ATY}.STRING);
}}""", cmd))
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
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  try {{
    if (!{PKG}.BankStore.coinsReady()) {{ pr.sendMessage({MSG}.raw("[Bank] SkyyCoins is not loaded, the bank cannot move coins.")); return; }}
    if (!ctx.provided(this.actionArg)) {{
      pr.sendMessage({MSG}.raw("[Bank] Bank: " + {PKG}.BankStore.get(u) + " coins  |  Purse: " + {PKG}.BankStore.purse(u) + " coins"));
      pr.sendMessage({MSG}.raw("[Bank] Interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min (on up to " + {PKG}.BankConfig.MAX_PRINCIPAL + "). Bank coins are safe on death. /bank deposit|withdraw <amount|all>"));
      return;
    }}
    String action = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
    if (action.equals("balance") || action.equals("bal")) {{
      pr.sendMessage({MSG}.raw("[Bank] Bank: " + {PKG}.BankStore.get(u) + " coins  |  Purse: " + {PKG}.BankStore.purse(u) + " coins"));
      return;
    }}
    boolean dep = action.startsWith("dep") || action.equals("d") || action.equals("put");
    boolean wd = action.startsWith("with") || action.equals("w") || action.equals("take");
    if (!dep && !wd) {{ pr.sendMessage({MSG}.raw("[Bank] Usage: /bank deposit <amount|all>  or  /bank withdraw <amount|all>")); return; }}
    if (!ctx.provided(this.amountArg)) {{ pr.sendMessage({MSG}.raw("[Bank] How much? e.g. /bank " + (dep ? "deposit" : "withdraw") + " 500  (or all, 2k, 1.5m)")); return; }}
    long all = dep ? {PKG}.BankStore.purse(u) : {PKG}.BankStore.get(u);
    long n;
    try {{ n = parseAmount(String.valueOf(ctx.get(this.amountArg)), all); }}
    catch (Throwable t) {{ pr.sendMessage({MSG}.raw("[Bank] That is not a number. Use e.g. 500, 2k, 1.5m or all.")); return; }}
    if (n <= 0L) {{ pr.sendMessage({MSG}.raw("[Bank] Nothing to " + (dep ? "deposit" : "withdraw") + ".")); return; }}
    if (dep) {{
      if (!{PKG}.BankStore.deposit(u, n)) {{ pr.sendMessage({MSG}.raw("[Bank] Not enough coins in your purse (" + {PKG}.BankStore.purse(u) + ").")); return; }}
      pr.sendMessage({MSG}.raw("[Bank] Deposited " + n + " coins. Bank: " + {PKG}.BankStore.get(u) + "  |  Purse: " + {PKG}.BankStore.purse(u)));
    }} else {{
      if (!{PKG}.BankStore.withdraw(u, n)) {{ pr.sendMessage({MSG}.raw("[Bank] Not enough coins in the bank (" + {PKG}.BankStore.get(u) + ").")); return; }}
      pr.sendMessage({MSG}.raw("[Bank] Withdrew " + n + " coins. Bank: " + {PKG}.BankStore.get(u) + "  |  Purse: " + {PKG}.BankStore.purse(u)));
    }}
  }} catch (Throwable t) {{
    {PKG}.BankStore.warn("/bank failed: " + t);
    pr.sendMessage({MSG}.raw("[Bank] Something went wrong. Usage: /bank deposit|withdraw <amount|all>"));
  }}
}}""", cmd))

# ================= /bankconfig (admin) =================
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
}}""", adm))
adm.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    if (!ctx.provided(this.pctArg)) {{
      long nextIn = ({PKG}.BankConfig.LAST + (long) {PKG}.BankConfig.MINUTES * 60000L - System.currentTimeMillis()) / 60000L;
      pr.sendMessage({MSG}.raw("[Bank] interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min, max principal " + {PKG}.BankConfig.MAX_PRINCIPAL + ", next payout in ~" + nextIn + " min. /bankconfig <percent> <minutes> [maxPrincipal]"));
      return;
    }}
    int pc = Integer.parseInt(String.valueOf(ctx.get(this.pctArg)).replace("%", "").trim());
    int mn = ctx.provided(this.minArg) ? Integer.parseInt(String.valueOf(ctx.get(this.minArg)).trim()) : {PKG}.BankConfig.MINUTES;
    long mp = ctx.provided(this.maxArg) ? {PKG}.BankCmd.parseAmount(String.valueOf(ctx.get(this.maxArg)), {PKG}.BankConfig.MAX_PRINCIPAL) : {PKG}.BankConfig.MAX_PRINCIPAL;
    if (pc < 0 || pc > 100 || mn < 1 || mp < 0L || mp > 1000000000000L) {{ pr.sendMessage({MSG}.raw("[Bank] percent 0-100, minutes >= 1, maxPrincipal 0..1,000,000,000,000")); return; }}
    {PKG}.BankConfig.PERCENT = pc; {PKG}.BankConfig.MINUTES = mn; {PKG}.BankConfig.MAX_PRINCIPAL = mp;
    {PKG}.BankConfig.save();
    pr.sendMessage({MSG}.raw("[Bank] set: " + pc + "% every " + mn + " min, max principal " + mp));
  }} catch (Throwable t) {{ pr.sendMessage({MSG}.raw("[Bank] Usage: /bankconfig <percent> <minutes> [maxPrincipal]")); }}
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
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.BankTick(), 30L, 30L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyBank] {VERSION} ready - /bank, interest " + {PKG}.BankConfig.PERCENT + "% every " + {PKG}.BankConfig.MINUTES + " min (coins bridge " + ({PKG}.BankStore.coinsReady() ? "found" : "NOT found yet") + ")");
}}""", pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (bs, cfg, tick, cmd, adm, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyBank-%s.jar" % VERSION)
m = B.manifest("SkyyBank", VERSION, "SkyWynn bank: /bank deposit/withdraw, death-safe savings with periodic interest. Uses the SkyyCoins bridge, zero dependencies.", PKG + ".SkyyBankPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyBank.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyBank" % VERSION, disable_prefix="Skyy:")
