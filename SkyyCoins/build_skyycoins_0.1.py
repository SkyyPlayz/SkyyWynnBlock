import jpype, sys, os, zipfile, json
from jdk4py import JAVA_HOME
jpype.startJVM(str(JAVA_HOME/"lib"/"server"/"libjvm.so"), "--add-opens=java.base/java.lang=ALL-UNNAMED", classpath=["/tmp/javassist/javassist.jar"])
J = jpype.JClass
ClassPool, CtField, CtNewMethod, CtNewConstructor = J("javassist.ClassPool"), J("javassist.CtField"), J("javassist.CtNewMethod"), J("javassist.CtNewConstructor")
REL = sys.argv[1]
pool = ClassPool(False); pool.appendSystemPath(); pool.appendClassPath(REL)
OUT = "/tmp/skyycoins_classes"; os.system(f"rm -rf {OUT}"); os.makedirs(OUT)

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
DC  = "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent"

dc = pool.get(DC)
assert any(str(m.getName()) == "getComponentType" for m in dc.getMethods()), "DeathComponent.getComponentType missing"
print("DeathComponent OK")

PKG = "com.skyy.coins"
cs   = pool.makeClass(PKG + ".CoinStore")
cfg  = pool.makeClass(PKG + ".CoinConfig")
task = pool.makeClass(PKG + ".CoinTask")
tick = pool.makeClass(PKG + ".CoinTick")
bal  = pool.makeClass(PKG + ".BalanceCmd", pool.get(APC))
pay  = pool.makeClass(PKG + ".PayCmd", pool.get(APC))
give = pool.makeClass(PKG + ".GiveCmd", pool.get(APC))
dp   = pool.makeClass(PKG + ".DeathPenaltyCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyCoinsPlugin", pool.get(JP))

# ================= CoinStore =================
cs.addField(CtField.make("public static java.nio.file.Path DIR;", cs))
cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAL = new java.util.concurrent.ConcurrentHashMap();", cs))
cs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOADED = new java.util.concurrent.ConcurrentHashMap();", cs))
cs.addMethod(CtNewMethod.make("""
public static void load(java.util.UUID u) {
  if (LOADED.putIfAbsent(u, Boolean.TRUE) != null) return;
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      p.load(in); in.close();
      String v = p.getProperty("balance");
      if (v != null) BAL.put(u, Long.valueOf(Long.parseLong(v)));
    }
  } catch (Throwable t) { }
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static boolean known(java.util.UUID u) {
  load(u);
  return LOADED.get(u) == Boolean.TRUE && BAL.containsKey(u);
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static long get(java.util.UUID u) {
  load(u);
  Long v = (Long) BAL.get(u);
  return v == null ? 0L : v.longValue();
}""", cs))
cs.addMethod(CtNewMethod.make("""
public static void set(java.util.UUID u, long v) {
  if (v < 0L) v = 0L;
  BAL.put(u, Long.valueOf(v));
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("balance", String.valueOf(v));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(DIR.resolve(u.toString() + ".properties"), new java.nio.file.OpenOption[0]);
    p.store(out, "SkyyCoins");
    out.close();
  } catch (Throwable t) { }
}""", cs))
cs.addMethod(CtNewMethod.make("public static void add(java.util.UUID u, long d) { set(u, get(u) + d); }", cs))

# ================= CoinConfig =================
cfg.addField(CtField.make("public static java.nio.file.Path FILE;", cfg))
cfg.addField(CtField.make("public static volatile int MIN = 10;", cfg))
cfg.addField(CtField.make("public static volatile int MAX = 25;", cfg))
cfg.addMethod(CtNewMethod.make("""
public static void load() {
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    p.load(in); in.close();
    MIN = Integer.parseInt(p.getProperty("penaltyMin", "10"));
    MAX = Integer.parseInt(p.getProperty("penaltyMax", "25"));
  } catch (Throwable t) { }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static void save() {
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("penaltyMin", String.valueOf(MIN));
    p.setProperty("penaltyMax", String.valueOf(MAX));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(FILE, new java.nio.file.OpenOption[0]);
    p.store(out, "SkyyCoins config");
    out.close();
  } catch (Throwable t) { }
}""", cfg))

# ================= CoinTask (world thread) =================
task.addInterface(pool.get("java.lang.Runnable"))
task.addField(CtField.make(f"public {PR} pr;", task))
task.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DEAD = new java.util.concurrent.ConcurrentHashMap();", task))
task.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap GRANTED = new java.util.concurrent.ConcurrentHashMap();", task))
task.addConstructor(CtNewConstructor.make(f"public CoinTask({PR} pr) {{ this.pr = pr; }}", task))
task.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (pr == null || !pr.isValid()) return;
    {REF} r = pr.getReference();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    java.util.UUID u = pr.getUuid();
    // test-grant starter coins once
    if (GRANTED.putIfAbsent(u, Boolean.TRUE) == null && !{PKG}.CoinStore.known(u)) {{
      {PKG}.CoinStore.set(u, 10000L);
      pr.sendMessage({MSG}.raw("[SkyyCoins test] granted 10,000 starter coins. /balance to check, /deathpenalty to tune."));
    }}
    Object death = st.getComponent(r, {DC}.getComponentType());
    boolean wasDead = DEAD.containsKey(u);
    if (death != null && !wasDead) {{
      DEAD.put(u, Boolean.TRUE);
      long balNow = {PKG}.CoinStore.get(u);
      if (balNow > 0L) {{
        int min = {PKG}.CoinConfig.MIN; int max = {PKG}.CoinConfig.MAX;
        int pct = min >= max ? min : min + new java.util.Random().nextInt(max - min + 1);
        long loss = balNow * (long) pct / 100L;
        if (loss > 0L) {{
          {PKG}.CoinStore.add(u, -loss);
          pr.sendMessage({MSG}.raw("You died and lost " + loss + " coins (" + pct + "%). Balance: " + {PKG}.CoinStore.get(u)));
        }}
      }}
    }} else if (death == null && wasDead) {{
      DEAD.remove(u);
    }}
  }} catch (Throwable t) {{ }}
}}""", task))

# ================= CoinTick =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public CoinTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) continue;
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) continue;
      w.execute(new {PKG}.CoinTask(pr));
    }}
  }} catch (Throwable t) {{ }}
}}""", tick))

# ================= commands =================
bal.addConstructor(CtNewConstructor.make("""
public BalanceCmd() {
  super("balance", "Check your coin balance");
  addAliases(new String[] { "bal", "coins", "purse" });
}""", bal))
bal.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  pr.sendMessage({MSG}.raw("Balance: " + {PKG}.CoinStore.get(pr.getUuid()) + " coins"));
}}""", bal))

pay.addField(CtField.make(f"public {RA} targetArg;", pay))
pay.addField(CtField.make(f"public {RA} amountArg;", pay))
pay.addConstructor(CtNewConstructor.make(f"""
public PayCmd() {{
  super("pay", "Send coins to another player");
  this.targetArg = withRequiredArg("player", "Player to pay", {ATY}.PLAYER_REF);
  this.amountArg = withRequiredArg("amount", "Coins to send", {ATY}.INTEGER);
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
    long have = {PKG}.CoinStore.get(pr.getUuid());
    if (have < amount) {{ pr.sendMessage({MSG}.raw("Not enough coins (balance: " + have + ").")); return; }}
    {PKG}.CoinStore.add(pr.getUuid(), -amount);
    {PKG}.CoinStore.add(target.getUuid(), amount);
    pr.sendMessage({MSG}.raw("Paid " + amount + " coins to " + target.getUsername() + ". Balance: " + {PKG}.CoinStore.get(pr.getUuid())));
    target.sendMessage({MSG}.raw(pr.getUsername() + " paid you " + amount + " coins. Balance: " + {PKG}.CoinStore.get(target.getUuid())));
  }} catch (Throwable t2) {{
    pr.sendMessage({MSG}.raw("Pay failed: " + t2));
  }}
}}""", pay))

give.addField(CtField.make(f"public {RA} amountArg;", give))
give.addConstructor(CtNewConstructor.make(f"""
public GiveCmd() {{
  super("coinsgive", "(testing) grant yourself coins");
  this.amountArg = withRequiredArg("amount", "Coins to grant", {ATY}.INTEGER);
}}""", give))
give.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object a = ctx.get(this.amountArg);
    if (a == null) return;
    long amount = (long) ((Integer) a).intValue();
    {PKG}.CoinStore.add(pr.getUuid(), amount);
    pr.sendMessage({MSG}.raw("Granted " + amount + ". Balance: " + {PKG}.CoinStore.get(pr.getUuid())));
  }} catch (Throwable t) {{ }}
}}""", give))

dp.addField(CtField.make(f"public {RA} specArg;", dp))
dp.addConstructor(CtNewConstructor.make(f"""
public DeathPenaltyCmd() {{
  super("deathpenalty", "Set death coin loss, e.g. 5% or 5%-10%");
  this.specArg = withRequiredArg("percent", "e.g. 5% or 5%-10%", {ATY}.STRING);
}}""", dp))
dp.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    Object o = ctx.get(this.specArg);
    if (o == null) {{ pr.sendMessage({MSG}.raw("Current: " + {PKG}.CoinConfig.MIN + "%-" + {PKG}.CoinConfig.MAX + "%")); return; }}
    String s = o.toString().trim().replace("%", "");
    int min; int max;
    int dash = s.indexOf('-');
    if (dash >= 0) {{
      min = Integer.parseInt(s.substring(0, dash).trim());
      max = Integer.parseInt(s.substring(dash + 1).trim());
    }} else {{
      min = Integer.parseInt(s); max = min;
    }}
    if (min < 0 || max > 100 || min > max) {{ pr.sendMessage({MSG}.raw("Invalid range. Use 0-100, min <= max.")); return; }}
    {PKG}.CoinConfig.MIN = min; {PKG}.CoinConfig.MAX = max;
    {PKG}.CoinConfig.save();
    pr.sendMessage({MSG}.raw("Death penalty set: " + (min == max ? (min + "%") : (min + "%-" + max + "%")) + " of carried coins."));
  }} catch (Throwable t) {{
    pr.sendMessage({MSG}.raw("Usage: /deathpenalty 5%  or  /deathpenalty 5%-10%"));
  }}
}}""", dp))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyCoinsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.CoinStore.DIR = getDataDirectory().resolve("balances");
  {PKG}.CoinConfig.FILE = getDataDirectory().resolve("config.properties");
  {PKG}.CoinConfig.load();
  getCommandRegistry().registerCommand(new {PKG}.BalanceCmd());
  getCommandRegistry().registerCommand(new {PKG}.PayCmd());
  getCommandRegistry().registerCommand(new {PKG}.GiveCmd());
  getCommandRegistry().registerCommand(new {PKG}.DeathPenaltyCmd());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.CoinTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.WARNING).log("[SkyyCoins] 0.1 ready - /balance /pay /deathpenalty (current " + {PKG}.CoinConfig.MIN + "%-" + {PKG}.CoinConfig.MAX + "%)");
}}""", pl))

for c in (cs, cfg, task, tick, bal, pay, give, dp, pl): c.writeFile(OUT)
print("classes written")

manifest = {
  "Group": "Skyy", "Name": "0.1 SkyyCoins", "Version": "0.1.0",
  "Description": "SkyWynn economy core: coin ledger, /balance, /pay, configurable death penalty (/deathpenalty 5% or 5%-10%). Zero dependencies.",
  "Authors": [{"Name": "Skyy"}], "ServerVersion": "*", "DisabledByDefault": False,
  "IncludesAssetPack": False, "Main": "com.skyy.coins.SkyyCoinsPlugin"
}
with zipfile.ZipFile("/tmp/SkyyCoins.jar", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("manifest.json", json.dumps(manifest, indent=2))
    for root, _, files in os.walk(OUT):
        for f in files:
            if f.endswith(".class"):
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
print("assembled /tmp/SkyyCoins.jar", os.path.getsize("/tmp/SkyyCoins.jar"))
