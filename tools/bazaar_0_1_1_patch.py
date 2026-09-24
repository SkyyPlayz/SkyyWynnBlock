"""Derive SkyyBazaar/build_skyybazaar_0.1.1.py from 0.1 (0.1 stays untouched).
0.1.1: /bazaar (/bz) usable by ordinary players (setPermissionGroups hytale:Adventurer, vanilla /help /who /ping pattern);
/bazaaradmin positional forms are real admin-gated subcommands (price <itemId> <base>, price <itemId>, reload, reset <itemId|all>,
info <itemId>) because optional args are not positional in the engine parser. Everything else identical.
Verification is split in the generated docstring: the offline parser harness covers /bazaaradmin parsing + admin gating only; the
/bazaar Adventurer grant is bytecode-verified plus an offline replay of setOwner/refreshVirtualGroups/PermissionsModule.hasPermission.
Run:  python tools/bazaar_0_1_1_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.1.py   (never --deploy without Skyy's OK)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.1.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


# ---------------- docstring ----------------
rep('"""SkyyBazaar 0.1 - build script (javassist via jpype).', '"""SkyyBazaar 0.1.1 - build script (javassist via jpype).')
rep('''Run:   python build_skyybazaar_0.1.py            -> SkyyBazaar/SkyyBazaar-0.1.jar   (build only; no --deploy was used for 0.1)
       python build_skyybazaar_0.1.py --deploy   -> also copies to Mods/SkyyBazaar.jar and enables it in the HUD mod world
''', '''Run:   python build_skyybazaar_0.1.1.py            -> SkyyBazaar/SkyyBazaar-0.1.1.jar   (build only; --deploy only with Skyy's OK)
       python build_skyybazaar_0.1.1.py --deploy   -> also copies to Mods/SkyyBazaar.jar and enables it in the HUD mod world
       (0.1.1 is generated from build_skyybazaar_0.1.py by tools/bazaar_0_1_1_patch.py; 0.1 is kept as it was)

0.1.1 (2026-09-23) - command access fixes only; pricing, trades, anti-dupe, files, log and bridge are byte-for-byte the 0.1 logic.
 - /bazaar (/bz) is usable by ordinary players. 0.1 never called requirePermission(), so CommandRegistry -> AbstractCommand.setOwner()
   generated the node "skyy.0.1_skyybazaar.command.bazaar" (PluginBase base permission "<group>.<name>" lower-cased, spaces -> "_",
   so it even changes with every version) and players in the default group hytale:Adventurer have no permissions -> only "*" admins
   could open it. Now BzCmd calls setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as
   SkyyEssentials 0.1): CommandManager.createVirtualPermissionGroups -> PermissionsModule virtual group grants that node to Adventurer.
 - /bazaaradmin positional forms work. In 0.1 all three arguments were withOptionalArg, and optional args are NOT positional:
   AbstractCommand.acceptCall0 requires (positional tokens) == totalNumRequiredParameters unless setAllowsExtraArguments(true), so
   "/bazaaradmin price Ore_Copper 5" failed with server.commands.parsing.error.wrongNumberRequiredParameters and only
   "--action price --item Ore_Copper --value 5" worked. 0.1.1 adds real subcommands with withRequiredArg:
       /bazaaradmin                      status line + usage (root execute, unchanged)
       /bazaaradmin price <itemId> <base>   set a base price           /bazaaradmin price <itemId>   show the current base (usage variant)
       /bazaaradmin reload                 /bazaaradmin reset <itemId|all>          /bazaaradmin info <itemId>
   Engine (bytecode, AbstractCommand.checkForExecutingSubcommands): the first positional token is looked up as a subcommand name
   (lower-cased, aliases too) and dispatched; otherwise a usage variant is picked from variantCommands by the positional-token count,
   only when that count differs from the command's own required count (addUsageVariant keys the variant by ITS required count at add
   time, so a variant declares its args in its own constructor). With no positional tokens and no match the root runs its own
   execute (0 == 0 required), so plain /bazaaradmin and the old --action/--item/--value flags still work on the root.
   The subcommand is dispatched BEFORE the root's hasPermission check, so every subcommand and the variant call
   requirePermission("skyybazaar.admin") themselves (hasPermission then also walks up to the parent, which needs the same node).
   All forms go through one static BzAdminCmd.run(pr, action, item, value) = the 0.1 execute body with ctx reads replaced by params.
 - What proved what (offline only; nothing here is a live-server test - Skyy's in-game test is the real check):
   (a) Offline parser harness (session scratchpad bz/bz011_parsetest.py, not shipped: real Tokenizer / ParserContext / acceptCall on
       the built classes, fake console sender holding an explicit node list). It covers ONLY /bazaaradmin: the positional forms parse
       (price <id> <base>, price <id>, reload, RELOAD, reset <id|all>, info <id>, old --action/--item/--value), wrong token counts give
       wrongNumberRequiredParameters, and without skyybazaar.admin every form gives noPermissionForCommand. It builds commands directly
       and never calls setOwner(), so BzCmd.permission stays null there and /bazaar runs for anyone on 0.1 AND 0.1.1: it is no
       evidence for the /bazaar fix. Its sender is not a player, so every "ran" stops at AbstractPlayerCommand's playerOrArg reply
       (the run() bodies are not exercised).
   (b) The /bazaar Adventurer grant rests on bytecode: setOwner() fills in permission only when it is null (and not openToEveryone)
       with generatePermission() = PluginBase.getBasePermission() + ".command.bazaar"; PluginManager.setup() runs every plugin's
       setup() (our registerCommand) before PluginManager.start() runs PermissionsModule.start() -> refreshVirtualGroups() ->
       CommandManager.createVirtualPermissionGroups() -> setVirtualGroups(); PlayerRef.hasPermission -> PermissionsModule.hasPermission
       checks the user's nodes, then for each group (default hytale:Adventurer) that group's nodes, then virtualGroups.get(group).
       Offline replay bz/bz011_advtest.py (scratchpad) runs those real engine methods with only object construction stubbed (plugin,
       CommandManager and PermissionsModule allocated without constructors, in-memory HytalePermissionsProvider): 0.1 Adventurer
       /bazaar -> noPermissionForCommand; 0.1.1 Adventurer /bazaar and /bz -> ran; hytale:None player -> denied; Adventurer
       /bazaaradmin (plain, reload, price, info) -> denied; a user granted skyybazaar.admin -> reload and price <id> <base> ran.
       Not covered offline: the real boot, and a hot /plugin load - virtual groups are rebuilt only by PermissionsModule.start() and
       reload(), so a version loaded after boot needs /perm reload or a restart before Adventurers can use /bazaar.
''')
rep(''' - Admin (permission skyybazaar.admin): /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>.''',
    ''' - Admin (permission skyybazaar.admin): /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>
   (positional subcommands since 0.1.1; 0.1 only accepted --action/--item/--value).''')

# ---------------- version + API probes ----------------
rep('VERSION = "0.1"' + LF, 'VERSION = "0.1.1"' + LF)
rep('OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"' + LF,
    'OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"' + LF +
    'RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"' + LF)
rep('(HSV, "SCHEDULED_EXECUTOR"), (ACM, "requirePermission"), (ACM, "addAliases"), (ACM, "withOptionalArg"),',
    '(HSV, "SCHEDULED_EXECUTOR"), (ACM, "requirePermission"), (ACM, "addAliases"), (ACM, "withOptionalArg"),' + LF +
    '             (ACM, "withRequiredArg"), (ACM, "setPermissionGroups"), (ACM, "addSubCommand"), (ACM, "addUsageVariant"),')

# ---------------- classes ----------------
rep('adm  = pool.makeClass(PKG + ".BzAdminCmd", pool.get(APC))' + LF,
    'adm  = pool.makeClass(PKG + ".BzAdminCmd", pool.get(APC))' + LF +
    'aprc = pool.makeClass(PKG + ".BzAdmPriceCmd", pool.get(APC))' + LF +
    'aprv = pool.makeClass(PKG + ".BzAdmPriceShowCmd", pool.get(APC))' + LF +
    'arlc = pool.makeClass(PKG + ".BzAdmReloadCmd", pool.get(APC))' + LF +
    'arsc = pool.makeClass(PKG + ".BzAdmResetCmd", pool.get(APC))' + LF +
    'ainc = pool.makeClass(PKG + ".BzAdmInfoCmd", pool.get(APC))' + LF)
rep('for c in (utl, coin, prod, cat_, mkt, inv_, res, trd, page, fac, cmd, adm, tick, pl):',
    'for c in (utl, coin, prod, cat_, mkt, inv_, res, trd, page, fac, cmd, aprv, aprc, arlc, arsc, ainc, adm, tick, pl):')

# ---------------- /bazaar: player-facing ----------------
rep('''  super("bazaar", "Open the Bazaar - instant buy and sell of commodities");
  addAliases(new String[] { "bz" });
}""", cmd))''', '''  super("bazaar", "Open the Bazaar - instant buy and sell of commodities");
  addAliases(new String[] { "bz" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""", cmd))''')

# ---------------- /bazaaradmin: subcommands ----------------
A0 = '# ================= /bazaaradmin =================' + LF
A1 = '# ================= BzTick'
a = s.index(A0)
b = s.index(A1, a)
old = s[a:b]
EX0 = 'adm.addMethod(CtNewMethod.make(f"""' + LF + 'protected void execute('
e = old.index(EX0)
head, body = old[:e], old[e:]
# head = fields + old constructor; body = old execute (kept as the shared static run, ctx reads -> parameters)
C0 = 'adm.addConstructor(CtNewConstructor.make(f"""'
fields = head[:head.index(C0)]
assert fields.count("adm.addField") == 3 and "OA" in fields, fields
old_ctor = head[head.index(C0):]
pairs = [
    ('protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{',
     'public static void run({PR} pr, String action, String itemRaw, String valueRaw) {{'),
    ('if (!ctx.provided(this.actionArg)) {{', 'if (action == null) {{'),
    ('String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();', 'String a = action.trim().toLowerCase();'),
    ('String item = ctx.provided(this.itemArg) ? String.valueOf(ctx.get(this.itemArg)).trim() : null;',
     'String item = itemRaw != null ? itemRaw.trim() : null;'),
    ('if (!ctx.provided(this.valueArg)) {{', 'if (valueRaw == null) {{'),
    ('v = Double.parseDouble(String.valueOf(ctx.get(this.valueArg)).trim());', 'v = Double.parseDouble(valueRaw.trim());'),
]
for o, n in pairs:
    assert body.count(o) == 1, "execute anchor: " + o
    body = body.replace(o, n)
assert "ctx." not in body and "this." not in body, "run() still reads ctx/this"
assert body.rstrip().endswith('}}""", adm))'), body[-80:]
run_method = body.rstrip() + LF

# the old constructor, plus the four subcommands (added last, after requirePermission / args; addSubCommand only marks the CHILD
# registered, so the root may still add its own args before it - order kept like SkyyParty 0.1.1)
C_OLD_END = '''  this.valueArg = withOptionalArg("value", "new base price (0.01 .. 1000000000)", {ATY}.STRING);
}}""", adm))'''
assert old_ctor.count(C_OLD_END) == 1, old_ctor
new_ctor = old_ctor.replace(C_OLD_END, '''  this.valueArg = withOptionalArg("value", "new base price (0.01 .. 1000000000)", {ATY}.STRING);
  addSubCommand(new {PKG}.BzAdmPriceCmd());
  addSubCommand(new {PKG}.BzAdmReloadCmd());
  addSubCommand(new {PKG}.BzAdmResetCmd());
  addSubCommand(new {PKG}.BzAdmInfoCmd());
}}""", adm))''').rstrip() + LF

SUBS = r'''
# --- subcommands / variant (javassist: each class gets its constructor + execute BEFORE the class that constructs it) ---
EXEC_SIG = f"protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world)"
def adm_exec(cls, call, what):
    cls.addMethod(CtNewMethod.make(f"""
{EXEC_SIG} {{
  try {{
    {call}
  }} catch (Throwable t) {{
    {PKG}.BzUtil.warn("/bazaaradmin {what} failed: " + t);
    pr.sendMessage({MSG}.raw("[Bazaar] Usage: /bazaaradmin price <itemId> <base> | reload | reset <itemId|all> | info <itemId>"));
  }}
}}""", cls))

# /bazaaradmin price <itemId>  (usage variant of price: 1 required arg -> shows the current base, like 0.1 without --value)
aprv.addField(CtField.make(f"public {RA} itemArg;", aprv))
aprv.addConstructor(CtNewConstructor.make(f"""
public BzAdmPriceShowCmd() {{
  super("(admin) show the current base price of a bazaar product");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id", {ATY}.STRING);
}}""", aprv))
adm_exec(aprv, f'{PKG}.BzAdminCmd.run(pr, "price", String.valueOf(ctx.get(this.itemArg)), (String) null);', "price")

# /bazaaradmin price <itemId> <base>
aprc.addField(CtField.make(f"public {RA} itemArg;", aprc))
aprc.addField(CtField.make(f"public {RA} valueArg;", aprc))
aprc.addConstructor(CtNewConstructor.make(f"""
public BzAdmPriceCmd() {{
  super("price", "(admin) set a product's base price: /bazaaradmin price <itemId> <base>");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id", {ATY}.STRING);
  this.valueArg = withRequiredArg("base", "new base price (0.01 .. 1000000000)", {ATY}.STRING);
  addUsageVariant(new {PKG}.BzAdmPriceShowCmd());
}}""", aprc))
adm_exec(aprc, f'{PKG}.BzAdminCmd.run(pr, "price", String.valueOf(ctx.get(this.itemArg)), String.valueOf(ctx.get(this.valueArg)));', "price")

# /bazaaradmin reload
arlc.addConstructor(CtNewConstructor.make("""
public BzAdmReloadCmd() {
  super("reload", "(admin) re-read products.properties and market.properties from disk");
  requirePermission("skyybazaar.admin");
}""", arlc))
adm_exec(arlc, f'{PKG}.BzAdminCmd.run(pr, "reload", (String) null, (String) null);', "reload")

# /bazaaradmin reset <itemId|all>
arsc.addField(CtField.make(f"public {RA} itemArg;", arsc))
arsc.addConstructor(CtNewConstructor.make(f"""
public BzAdmResetCmd() {{
  super("reset", "(admin) reset a product's demand factor to 1.0: /bazaaradmin reset <itemId|all>");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id, or all", {ATY}.STRING);
}}""", arsc))
adm_exec(arsc, f'{PKG}.BzAdminCmd.run(pr, "reset", String.valueOf(ctx.get(this.itemArg)), (String) null);', "reset")

# /bazaaradmin info <itemId>
ainc.addField(CtField.make(f"public {RA} itemArg;", ainc))
ainc.addConstructor(CtNewConstructor.make(f"""
public BzAdmInfoCmd() {{
  super("info", "(admin) prices, demand and lifetime volume of a product: /bazaaradmin info <itemId>");
  requirePermission("skyybazaar.admin");
  this.itemArg = withRequiredArg("itemId", "bazaar product item id", {ATY}.STRING);
}}""", ainc))
adm_exec(ainc, f'{PKG}.BzAdminCmd.run(pr, "info", String.valueOf(ctx.get(this.itemArg)), (String) null);', "info")

'''

ROOT_EXEC = r'''adm.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  // plain /bazaaradmin (status) and the 0.1 flag forms --action/--item/--value; positional forms are the subcommands above
  String a = ctx.provided(this.actionArg) ? String.valueOf(ctx.get(this.actionArg)) : (String) null;
  String item = ctx.provided(this.itemArg) ? String.valueOf(ctx.get(this.itemArg)) : (String) null;
  String v = ctx.provided(this.valueArg) ? String.valueOf(ctx.get(this.valueArg)) : (String) null;
  {PKG}.BzAdminCmd.run(pr, a, item, v);
}}""", adm))

'''

COMMENT = ('# 0.1.1: positional forms are real subcommands (price / reload / reset / info + a "price <itemId>" usage variant). The engine' + LF +
           '# dispatches a subcommand BEFORE it checks the root permission, so each one requires skyybazaar.admin itself. The root keeps' + LF +
           '# its optional --action/--item/--value args (0.1 forms) and every form runs the same static run() = the 0.1 execute body.' + LF)

assert fields.startswith(A0)
new = A0 + COMMENT + fields[len(A0):] + run_method + SUBS + new_ctor + ROOT_EXEC
s = s[:a] + new + s[b:]

assert 'VERSION = "0.1.1"' in s
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
