"""Derive SkyyParty/build_skyyparty_0.1.2.py from 0.1.1 (0.1.1 stays untouched; CRLF line endings kept).
0.1.2: every command gets setPermissionGroups(new String[] { "hytale:Adventurer" }) - /party (alias /p), /party invite,
/party accept, /party leave, /party list and /pc - so ordinary players can use them (vanilla /help /who /ping pattern, same as
SkyyEssentials 0.1). Before, AbstractCommand.setOwner() gave each of them an auto node
"skyy.0.1.1_skyyparty.command.party[.invite|.accept|...]" / "...command.pc" that only "*" admins held.
Argument parsing was checked and needs no change: invite is a real subcommand with one withRequiredArg, and /pc uses
ArgTypes.GREEDY_STRING (registerRequiredArg sets allowsExtraArguments + hasGreedyStringArg, extractGreedyRawTail joins the raw tail).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyParty", "build_skyyparty_0.1.1.py")
dst = os.path.join(ROOT, "SkyyParty", "build_skyyparty_0.1.2.py")
raw = open(src, "rb").read()
assert b"\r\n" in raw, "expected CRLF source"
s = raw.decode("utf8").replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:70])
    s = s.replace(old, new)

# ---------- docstring + version ----------
rep('"""SkyyParty 0.1.1 - build script (javassist via jpype).\n'
    'Run:   python build_skyyparty_0.1.1.py            -> SkyyParty/SkyyParty-0.1.1.jar\n'
    '       python build_skyyparty_0.1.1.py --deploy   -> also copies to Mods/SkyyParty.jar and enables it in the HUD mod world\n',
    '"""SkyyParty 0.1.2 - build script (javassist via jpype).\n'
    'Run:   python build_skyyparty_0.1.2.py            -> SkyyParty/SkyyParty-0.1.2.jar\n'
    '       python build_skyyparty_0.1.2.py --deploy   -> also copies to Mods/SkyyParty.jar and enables it in the HUD mod world\n'
    '0.1.2: ordinary players can use the party commands. Every command (/party alias /p, /party invite|accept|leave|list, /pc)\n'
    '  calls setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as SkyyEssentials 0.1).\n'
    '  Engine (HytaleServer.jar bytecode, 2026-09-23): AbstractCommand.setOwner() gives every command without requirePermission() an\n'
    '  auto node "<plugin base permission>.command.party" (subcommands: that id + ".invite" etc., version included), which default\n'
    '  "hytale:Adventurer" players never held, so only "*" admins could run them. putRecursivePermissionGroups() walks subcommands,\n'
    '  CommandManager.createVirtualPermissionGroups() collects it, PermissionsModule.start() -> refreshVirtualGroups() runs after\n'
    '  every plugin setup(). Subcommand hasPermission(): own node, then (only when it has no groups of its own) the parent node.\n'
    '  Positional arguments already work and are unchanged: "/party invite <player>" = subcommand dispatch on the first token\n'
    '  (checkForExecutingSubcommands -> convertToSubCommand) then 1 token == 1 required arg; "/party" alone runs PartyCmd.execute\n'
    '  (not an AbstractCommandCollection, 0 tokens == 0 required); "/pc <message with spaces>" = GREEDY_STRING, which sets\n'
    '  allowsExtraArguments and passes the raw tail (extractGreedyRawTail) as one value.\n')
rep('VERSION = "0.1.1"', 'VERSION = "0.1.2"')

# ---------- ADV constant + API probe ----------
rep('LOG = "com.hypixel.hytale.logger.HytaleLogger"\n',
    'LOG = "com.hypixel.hytale.logger.HytaleLogger"\n'
    '# every party command is player-facing: grant its (auto-generated) permission node to the default player group\n'
    'ADV = \'setPermissionGroups(new String[] { "hytale:Adventurer" });\'\n')
rep('             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):\n',
    '             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"), (APC, "setPermissionGroups")):\n')

# ---------- constructors ----------
rep('  super("invite", "Invite a player to your party");\n',
    '  super("invite", "Invite a player to your party");\n  {ADV}\n')
rep('''acc.addConstructor(CtNewConstructor.make('public AcceptCmd() { super("accept", "Accept a party invite"); }', acc))''',
    '''acc.addConstructor(CtNewConstructor.make(f'public AcceptCmd() {{ super("accept", "Accept a party invite"); {ADV} }}', acc))''')
rep('''lev.addConstructor(CtNewConstructor.make('public LeaveCmd() { super("leave", "Leave your party"); }', lev))''',
    '''lev.addConstructor(CtNewConstructor.make(f'public LeaveCmd() {{ super("leave", "Leave your party"); {ADV} }}', lev))''')
rep('''lst.addConstructor(CtNewConstructor.make('public ListCmd() { super("list", "List party members"); }', lst))''',
    '''lst.addConstructor(CtNewConstructor.make(f'public ListCmd() {{ super("list", "List party members"); {ADV} }}', lst))''')
rep('  super("pc", "Party chat");\n',
    '  super("pc", "Party chat");\n  {ADV}\n')
rep('  super("party", "Party commands");\n',
    '  super("party", "Party commands");\n  {ADV}\n')

assert s.count("{ADV}") == 6, s.count("{ADV}")
open(dst, "wb").write(s.replace("\n", "\r\n").encode("utf8"))
print("wrote", dst)
