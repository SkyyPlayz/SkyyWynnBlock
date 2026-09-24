# one-off (2026-09-23): SkyyCoins 0.1.3 -> 0.1.4 (player permissions + positional /deathpenalty).
# Reads SkyyCoins/build_skyycoins_0.1.3.py (left untouched) and writes SkyyCoins/build_skyycoins_0.1.4.py (CRLF kept).
#  1) /balance and /pay get setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern,
#     same ADV constant as SkyyEssentials 0.1). /coinsgive and /deathpenalty keep requirePermission("skyycoins.admin").
#  2) /deathpenalty <spec> becomes a usage variant (DeathPenaltySetCmd, one required arg) so "/deathpenalty 5%" works;
#     the variant has its own requirePermission("skyycoins.admin") because the engine dispatches to a variant before the
#     parent's permission check. The parse/apply logic moves to a static DeathPenaltyCmd.applySpec(pr, spec) shared by both.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.3.py")
dst = os.path.join(ROOT, "SkyyCoins", "build_skyycoins_0.1.4.py")
assert not os.path.exists(dst), dst + " already exists"
raw = open(src, "rb").read()
assert raw.count(b"\r\n") == raw.count(b"\n"), "expected pure CRLF source"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "expected %d occurrence(s), found %d of:\n%s" % (count, n, old)
    s = s.replace(old, new)


# ---------- docstring ----------
rep('"""SkyyCoins 0.1.3 - build script (javassist via jpype).\n'
    'Run:   python build_skyycoins_0.1.2.py            -> SkyyCoins/SkyyCoins-0.1.1.jar\n'
    '       python build_skyycoins_0.1.2.py --deploy   -> also copies',
    '"""SkyyCoins 0.1.4 - build script (javassist via jpype).\n'
    'Run:   python build_skyycoins_0.1.4.py            -> SkyyCoins/SkyyCoins-0.1.4.jar\n'
    '       python build_skyycoins_0.1.4.py --deploy   -> also copies')
rep('/deathpenalty with no argument shows the current setting.\n0.1.3:',
    '/deathpenalty with no argument shows the current setting.\n'
    '0.1.4: (1) /balance (bal, coins, purse) and /pay <player> <amount> are open to ordinary players: their constructors call\n'
    '  setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as SkyyEssentials 0.1).\n'
    '  Before, CommandRegistry.registerCommand -> AbstractCommand.setOwner() gave them an auto node like\n'
    '  "skyy.0.1.3_skyycoins.command.balance" that only "*" admins had. /coinsgive and /deathpenalty keep requirePermission("skyycoins.admin").\n'
    '  (2) /deathpenalty 5% and /deathpenalty 5%-10% work positionally. The spec used to be an OPTIONAL arg, which the parser only\n'
    '  accepts as "--percent 5%" (acceptCall0 needs positional token count == required arg count, so "/deathpenalty 5%" failed with\n'
    '  wrongNumberRequiredParameters). Now DeathPenaltySetCmd is a usage variant (description-only constructor, one withRequiredArg\n'
    '  "percent") with its OWN requirePermission("skyycoins.admin"). /deathpenalty alone still shows the current setting, and\n'
    '  /deathpenalty --percent 5% still works (the parent keeps its optional arg). Parse/apply logic is DeathPenaltyCmd.applySpec().\n'
    '  Engine checks (HytaleServer.jar bytecode, 2026-09-23): acceptCall0 calls checkForExecutingSubcommands FIRST, which picks\n'
    '  variantCommands.get(<positional token count>) when that count differs from the parent\'s own required count (0 here), and\n'
    '  runs the variant\'s acceptCall0 -> the variant\'s own hasPermission(); the parent\'s hasPermission() is never reached, hence\n'
    '  the variant\'s own requirePermission. A variant (with a parent, no permission groups) also re-checks parent.hasPermission().\n'
    '  addUsageVariant keys by the variant\'s required count and completeRegistration rejects a variant whose count equals the\n'
    '  parent\'s (1 vs 0 is fine). Tokenizer only treats quotes, backslash and [ , ] specially, so "5%-10%" is one token.\n'
    '  Plugin setup() (registerCommand) runs in PluginManager.setup() before PermissionsModule.start() -> refreshVirtualGroups()\n'
    '  -> CommandManager.createVirtualPermissionGroups() reads getPermissionGroupsRecursive(), so the Adventurer grant is picked up.\n'
    '0.1.3:')

# ---------- version ----------
rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')

# ---------- API probes ----------
rep('             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),\n',
    '             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),\n'
    '             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "setPermissionGroups"),\n'
    '             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addUsageVariant"),\n')
rep('PKG = "com.skyy.coins"\n',
    'PKG = "com.skyy.coins"\n'
    '# vanilla player permission group (like /help /who /ping): every player without an explicit group is in it\n'
    'ADV = \'setPermissionGroups(new String[] { "hytale:Adventurer" });\'\n')

# ---------- new class ----------
rep('dp   = pool.makeClass(PKG + ".DeathPenaltyCmd", pool.get(APC))\n',
    'dp   = pool.makeClass(PKG + ".DeathPenaltyCmd", pool.get(APC))\n'
    'dps  = pool.makeClass(PKG + ".DeathPenaltySetCmd", pool.get(APC))\n')

# ---------- /balance, /pay: Adventurer group ----------
rep('''bal.addConstructor(CtNewConstructor.make("""
public BalanceCmd() {
  super("balance", "Check your coin balance");
  addAliases(new String[] { "bal", "coins", "purse" });
}""", bal))''',
    '''bal.addConstructor(CtNewConstructor.make(f"""
public BalanceCmd() {{
  super("balance", "Check your coin balance");
  addAliases(new String[] {{ "bal", "coins", "purse" }});
  {ADV}
}}""", bal))''')
rep('''  this.amountArg = withRequiredArg("amount", "Coins to send", {ATY}.INTEGER);
}}""", pay))''',
    '''  this.amountArg = withRequiredArg("amount", "Coins to send", {ATY}.INTEGER);
  {ADV}
}}""", pay))''')

# ---------- /deathpenalty: shared logic + usage variant ----------
OLD_DP = s[s.index('dp.addField(CtField.make(f"public {OA} specArg;", dp))\n'):s.index('# ================= plugin =================')]
assert OLD_DP.count('}}""", dp))') == 2, OLD_DP
NEW_DP = '''dp.addField(CtField.make(f"public {OA} specArg;", dp))
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

'''
s = s.replace(OLD_DP, NEW_DP, 1)

# ---------- write class files ----------
rep('for c in (cs, cfg, fn, task, tick, bal, pay, give, dp, pl):',
    'for c in (cs, cfg, fn, task, tick, bal, pay, give, dp, dps, pl):')

open(dst, "w", encoding="utf8", newline="\r\n").write(s)
print("wrote", dst)
