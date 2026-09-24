"""Derive SkyyIslands/build_skyyislands_0.4.3.py from 0.4.2 (0.4.2 stays untouched).
0.4.3: /island + /hub usable by ordinary players (setPermissionGroups hytale:Adventurer) and real positional subcommands
/island info | home | visit <player> | invite <player> (optional args are flags only, never positional). Full note in the new
script's docstring.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.4.2.py")
dst = os.path.join(ROOT, "SkyyIslands", "build_skyyislands_0.4.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) == 1, "anchor missing or not unique: " + old[:90]
    s = s.replace(old, new, count)


def block(start_marker, end_marker, new):
    """Replace s[start_marker .. end_marker) (end marker kept)."""
    global s
    assert s.count(start_marker) == 1, "block start missing or not unique: " + start_marker[:90]
    a = s.index(start_marker)
    b = s.index(end_marker, a)
    s = s[:a] + new + s[b:]


# ---- docstring + version
NOTE = r'''"""SkyyIslands 0.4.3 - build script
0.4.3: COMMANDS FOR EVERYONE + POSITIONAL FORMS (engine facts re-verified against HytaleServer.jar bytecode 2026-09-23).
  Permissions: AbstractCommand.setOwner() gave /island and /hub the auto node "<plugin base>.command.<cmd>" (the version is part of
  it), which default players (group hytale:Adventurer) do not have, so only "*" admins could use them. /island, its 4 subcommands
  and /hub now call setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, as SkyyEssentials 0.1):
  CommandManager.createVirtualPermissionGroups -> AbstractCommand.getPermissionGroupsRecursive (walks subcommands) and
  PermissionsModule.hasPermission checks the virtual group of every group the player is in. /sethub keeps requirePermission("skyyislands.admin").
  Arguments: optional args are flags only - AbstractCommand.acceptCall0 needs #positional tokens == #required args, so
  "/island visit Steve" failed with wrongNumberRequiredParameters. /island now has real subcommands (addSubCommand, SkyyParty pattern):
  info, home (alias go), visit <player> (alias warp), invite <player> (alias add); visit/invite use withRequiredArg(PLAYER_REF).
  checkForExecutingSubcommands matches the first positional token against subcommand names/aliases (lower-cased) BEFORE the root's
  own permission and argument-count checks; with no positional token the root (an AbstractPlayerCommand, not an
  AbstractCommandCollection) runs its own execute() = go home. The old flag form (/island --action visit --player X, used by
  SkyyMenu 0.1) still works: flags are not positional tokens, so it reaches the root execute unchanged.
  The action code moved into static IslandCmd.info / invite / visit, shared by the subcommands and the flag form.

'''
rep('"""SkyyIslands 0.4.2 - build script' + LF, NOTE)
rep('VERSION = "0.4.2"', 'VERSION = "0.4.3"')

# ---- constants + probes
rep('OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"' + LF,
    'OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"' + LF
    + 'RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"' + LF
    + 'AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"' + LF)
rep('             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),' + LF,
    '             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),' + LF
    + '             (AC, "setPermissionGroups"), (AC, "addSubCommand"), (AC, "withRequiredArg"), (AC, "addAliases"),' + LF)

# ---- classes
rep('PKG = "com.skyy.islands"' + LF,
    'PKG = "com.skyy.islands"' + LF
    + '# vanilla /help /who /ping permission-group line: every player in the default group may run the command' + LF
    + 'ADV = \'setPermissionGroups(new String[] { "hytale:Adventurer" });\'' + LF)
rep('icmd = pool.makeClass(PKG + ".IslandCmd", pool.get(APC))' + LF,
    'icmd = pool.makeClass(PKG + ".IslandCmd", pool.get(APC))' + LF
    + 'iinf = pool.makeClass(PKG + ".IslandInfoCmd", pool.get(APC))' + LF
    + 'ihom = pool.makeClass(PKG + ".IslandHomeCmd", pool.get(APC))' + LF
    + 'ivis = pool.makeClass(PKG + ".IslandVisitCmd", pool.get(APC))' + LF
    + 'iinv = pool.makeClass(PKG + ".IslandInviteCmd", pool.get(APC))' + LF)

# ---- /island: the root constructor moves below the subcommand classes (it constructs them)
block('icmd.addConstructor(CtNewConstructor.make(f"""' + LF + 'public IslandCmd() {{',
      'icmd.addMethod(CtNewMethod.make(f"""' + LF + 'public static {TRF} here(',
      '# IslandCmd constructor is added after the subcommand classes below (javassist: a class must have its constructor before' + LF
      + '# another class\'s code constructs it).' + LF)

ISLAND_TAIL = r'''icmd.addMethod(CtNewMethod.make(f"""
public static void info({PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  String name = {PKG}.IslandStore.worldName(u);
  String members = {PKG}.IslandStore.read(u).getProperty("members", "");
  pr.sendMessage({MSG}.raw("[Island] " + (name == null ? "No island yet, /island to create one." : "world " + name + (({UNI}.get().getWorld(name) != null) ? " (loaded)" : " (unloaded)")) + "  members: " + (members.isEmpty() ? "none" : String.valueOf(members.split(",").length))));
  pr.sendMessage({MSG}.raw("[Island] You are in world: " + world.getName()));
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
public static void invite({PR} pr, {PR} target) {{
  java.util.UUID u = pr.getUuid();
  if (target == null || !target.isValid()) {{ pr.sendMessage({MSG}.raw("[Island] That player is not online.")); return; }}
  if (target.getUuid().equals(u)) {{ pr.sendMessage({MSG}.raw("[Island] That is you.")); return; }}
  if ({PKG}.IslandStore.addMember(u, target.getUuid())) {{
    pr.sendMessage({MSG}.raw("[Island] " + target.getUsername() + " can now BUILD on your island (anyone can visit)."));
    target.sendMessage({MSG}.raw("[Island] " + pr.getUsername() + " gave you build rights on their island! /island visit " + pr.getUsername()));
  }} else pr.sendMessage({MSG}.raw("[Island] " + target.getUsername() + " is already a member."));
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
public static void visit({ST} store, {REF} ref, {PR} pr, {WLD} world, {PR} target) {{
  if (target == null || !target.isValid()) {{ pr.sendMessage({MSG}.raw("[Island] That player is not online.")); return; }}
  go(store, ref, pr, world, target.getUuid(), false);
  if (!{PKG}.IslandStore.isMember(target.getUuid(), pr.getUuid())) pr.sendMessage({MSG}.raw("[Island] Visiting " + target.getUsername() + "'s island - look, don't touch (they can /island invite you to build)."));
}}""", icmd))

# ---- /island subcommands (constructor + execute BEFORE the IslandCmd constructor that does addSubCommand(new ...))
def island_sub(cls, ctor_src, body):
    cls.addConstructor(CtNewConstructor.make(ctor_src, cls))
    cls.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
{body}
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/island error ({cls.getSimpleName()}): " + t);
    pr.sendMessage({MSG}.raw("[Island] Something went wrong: " + t.getMessage()));
  }}
}}""", cls))

# /island info
island_sub(iinf, f"""
public IslandInfoCmd() {{
  super("info", "About your island: its world, loaded or not, member count, and the world you are in");
  {ADV}
}}""", f"    {PKG}.IslandCmd.info(pr, world);")
# /island home (alias go) - same as plain /island
island_sub(ihom, f"""
public IslandHomeCmd() {{
  super("home", "Go to your island (same as /island)");
  addAliases(new String[] {{ "go" }});
  {ADV}
}}""", f"    {PKG}.IslandCmd.go(store, ref, pr, world, pr.getUuid(), true);")
# /island visit <player> (alias warp)
ivis.addField(CtField.make(f"public {RA} targetArg;", ivis))
island_sub(ivis, f"""
public IslandVisitCmd() {{
  super("visit", "Visit a player's island (anyone can visit, only members can build)");
  addAliases(new String[] {{ "warp" }});
  this.targetArg = withRequiredArg("player", "player whose island to visit", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"""    Object t = ctx.get(this.targetArg);
    {PR} target = null;
    if (t instanceof {PR}) target = ({PR}) t;
    {PKG}.IslandCmd.visit(store, ref, pr, world, target);""")
# /island invite <player> (alias add)
iinv.addField(CtField.make(f"public {RA} targetArg;", iinv))
island_sub(iinv, f"""
public IslandInviteCmd() {{
  super("invite", "Give a player build rights on your island");
  addAliases(new String[] {{ "add" }});
  this.targetArg = withRequiredArg("player", "player to give build rights", {ATY}.PLAYER_REF);
  {ADV}
}}""", f"""    Object t = ctx.get(this.targetArg);
    {PR} target = null;
    if (t instanceof {PR}) target = ({PR}) t;
    {PKG}.IslandCmd.invite(pr, target);""")

# ---- /island root: no positional token -> own execute (go home, or the old --action/--player flag form)
icmd.addConstructor(CtNewConstructor.make(f"""
public IslandCmd() {{
  super("island", "Go to your private island (creates it the first time). /island info | home | visit <player> | invite <player>");
  addAliases(new String[] {{ "is" }});
  this.actionArg = withOptionalArg("action", "old flag form: invite | visit | info | home (prefer /island visit <player>)", {ATY}.STRING);
  this.targetArg = withOptionalArg("player", "old flag form: player to invite / visit", {ATY}.PLAYER_REF);
  {ADV}
  addSubCommand(new {PKG}.IslandInfoCmd());
  addSubCommand(new {PKG}.IslandHomeCmd());
  addSubCommand(new {PKG}.IslandVisitCmd());
  addSubCommand(new {PKG}.IslandInviteCmd());
}}""", icmd))
icmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  java.util.UUID u = pr.getUuid();
  try {{
    if (!ctx.provided(this.actionArg)) {{ go(store, ref, pr, world, u, true); return; }}
    String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
    if (a.equals("info")) {{ info(pr, world); return; }}
    if (a.equals("home") || a.equals("go")) {{ go(store, ref, pr, world, u, true); return; }}
    if (!ctx.provided(this.targetArg)) {{ pr.sendMessage({MSG}.raw("[Island] Usage: /island | /island invite <player> | /island visit <player> | /island info")); return; }}
    {PR} target = ({PR}) ctx.get(this.targetArg);
    if (target == null || !target.isValid()) {{ pr.sendMessage({MSG}.raw("[Island] That player is not online.")); return; }}
    if (a.equals("invite") || a.equals("add")) {{ invite(pr, target); return; }}
    if (a.equals("visit") || a.equals("warp")) {{ visit(store, ref, pr, world, target); return; }}
    pr.sendMessage({MSG}.raw("[Island] Usage: /island | /island invite <player> | /island visit <player> | /island info"));
  }} catch (Throwable t) {{
    {PKG}.IslandStore.warn("/island error: " + t);
    pr.sendMessage({MSG}.raw("[Island] Something went wrong: " + t.getMessage()));
  }}
}}""", icmd))

'''
block('icmd.addMethod(CtNewMethod.make(f"""' + LF + 'protected void execute(',
      '# ================= /hub =================', ISLAND_TAIL)

# ---- /hub: players
rep('  addAliases(new String[] { "lobby" });' + LF + '}""", hcmd))',
    '  addAliases(new String[] { "lobby" });' + LF + '  setPermissionGroups(new String[] { "hytale:Adventurer" });' + LF + '}""", hcmd))')

# ---- startup log + class list
rep('ready - /island /hub /sethub, island protection on',
    'ready - /island [info|home|visit <player>|invite <player>] /hub /sethub (players: hytale:Adventurer), island protection on')
rep('for c in (st_, fill, cfl, reln, relt, bld, icmd, hcmd, shub,',
    'for c in (st_, fill, cfl, reln, relt, bld, icmd, iinf, ihom, ivis, iinv, hcmd, shub,')

assert not os.path.exists(dst), "refusing to overwrite " + dst
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "line endings", "CRLF" if NL == CR + LF else "LF")
