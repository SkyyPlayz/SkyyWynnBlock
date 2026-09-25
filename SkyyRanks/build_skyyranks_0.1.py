"""SkyyRanks 0.1 - build script (javassist via jpype). NEW mod, research/Server-Setup-Spec.md section 5.1 (+ 4.19, 6, 8.4.5, 9 defaults).
Run:   python build_skyyranks_0.1.py          -> SkyyRanks/SkyyRanks-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the whole set)

WHAT IT IS: ranks for a server owner, made IN GAME. A rank = an engine permission group named skyy:<id> plus a block in
Skyy_SkyyRanks/ranks.properties (order, display name, chat prefix, prefix colour, staff flag, own grants). No second permission provider
is ever added (PermissionsModule.addProvider would make areProvidersTampered() true and break vanilla /op self): SkyyRanks only calls the
built-in provider through PermissionsModule, like vanilla /perm does. permissions.json is never edited by this mod directly.

RULES (spec 5.1, all enforced in code):
  - Seeded with ONE rank only: member ("Member", no prefix) = the default rank (ranks.default). Owners make the rest in game.
  - The default rank is implicit: nobody is added to it and it has no engine group; it is the rank shown for every player without a
    skyy:* group. So it holds no grants and no members (ranks.default refuses a rank that has either; grants on it are refused).
    It is the FLOOR of the ladder: it has no Up / Down (page and /rank up|down refuse it, and no rank moves below it); a new
    ranks.default, a hand edit or /rankadmin reload moves it to the bottom (RankStore.floorDefault - no rank's permissions change,
    effectiveIn skips the default rank). So "new ranks go just above the default" always means the bottom of the ladder.
  - Grants only on ranks + per-player denies. A rank group's node set = its marker skyyranks.rank.<id> + its own grants + every LOWER
    rank's marker and grants (the engine has no API to set a group parent, so the lower grants are copied in). At start and after every
    edit each skyy:<rank> group is made exactly that set (add missing, remove extra). A deny on a group is unreliable (groups are walked
    in set order, first yes/no wins) so there are none; a deny on the USER is checked first by PermissionsModule.hasPermission, so
    per-player denies (-node on the user) are reliable, even against op's "*".
  - hytale:Adventurer SAFETY (the first in-game test, spec 8.4.5). VERIFIED this session (HytalePermissionsProvider bytecode):
    addUserToGroup starts from userGroups.getOrDefault(uuid, Set.of()), NOT from DEFAULT_GROUP_LIST {hytale:Adventurer}, so adding a
    player with no stored entry to skyy:vip would leave them ONLY in skyy:vip and take every player command away. So every assign /
    remove / join clean-up: (1) addUserToGroup(hytale:Adventurer) explicitly first, (2) add the new skyy group, (3) remove every other
    skyy:* group, (4) add hytale:Adventurer explicitly again, (5) read getGroupsForUser back and verify it holds hytale:Adventurer and
    exactly the wanted skyy group (a missing Adventurer is re-added once more, then reported red + SEVERE in the log). The page status,
    /rank set and /rank who print the player's groups so the test can be read off the screen.
  - A player has at most one skyy:* group. Never touches a group that does not start with skyy:, never touches hytale:Admin membership
    (op stays vanilla /op), never adds or removes hytale:Adventurer from anyone except to ADD it for players in a SkyyRanks rank.
  - Unknown skyy:* groups that still hold nodes (hand-made, or a rank dropped from ranks.properties by hand) are left as they are and
    logged once; recreating a rank with that id manages them again. Empty (non-existent) skyy:* groups are removed from a player at join.
  - Nothing is changed in the engine before PermissionsModule is ENABLED (its start() loads permissions.json; a write before that would
    save an empty state over the file). RankStartTask polls every 2 s, then syncs the groups and reconciles the stored members.
  - Confirm steps (page: a Confirm view; chat: type the same command again within 10 s): granting * / any wildcard / *.admin /
    skyymenu.modconfig / skyyranks.admin; giving someone a staff rank or a rank that carries such a node; moving a rank so it (or the
    rank passed) gains such a node; deleting a rank; a personal deny on an op or a staff-rank member; taking a staff rank from another
    player; any change that takes skyyranks.admin (the editor) from players: a rank change of another player (not an op), a grant
    removal or a move - the question names you first (self-lockout) and counts the other members who lose it. Editor access is decided
    exactly as the engine does (RankPerm.grants: skyyranks.admin, *, skyyranks.*, skyyranks.admin.*), never a hand-kept list.
    Refused outright: a deny of *, a deny on yourself that covers skyyranks.admin, grants that start with - (grants only), grants on the
    default rank, deleting the default rank, moving the default rank.
  - ranks.properties unreadable (or no valid rank in it) -> nothing is synced, every rank change is refused, the page says so in red.
    It is never overwritten; a change made on disk while the server runs refuses in-game rank edits until /rankadmin reload.

CHAT: [Rank] [Title] Name: text. RankChatHook is registered with registerAsyncGlobal((short) chat.priority 31000, PlayerChatEvent) - after
  SkyyExploration 0.1 / 0.2's title hook at 30000 (read from both build scripts: it wraps the previous formatter in its TitleFormatter).
  Ours wraps whatever formatter is there by then (normally TitleFormatter(default)) in a RankFormatter that calls prev.format() first and
  puts Message.raw(prefix + " ").color(colour) in front - so the title and the name stay exactly as Exploration made them. No prefix (the
  seeded Member) or chat.prefix=false = the message is passed through untouched. The formatter only reads an in-memory map.

COMMANDS (every one: requirePermission("skyyranks.admin") on the root AND on each subcommand; ops pass through hytale:Admin's "*"):
  /rankadmin                      the ranks editor page (also the "Ranks editor" link row in SkyyMenu 0.3 Server Setup)
  /rankadmin player <player>      the editor on that player (rank + personal denies)
  /rankadmin reload               re-read ranks.properties, players.properties and config.properties, then sync
  /rankadmin sync                 make every skyy:* group match the ladder again and reconcile the stored members
  /rank                           help          /rank list | /rank info <rank>
  /rank create <id> <name...>     a new rank just ABOVE the default rank (id a-z 0-9, 2-16 characters; name 1-24 characters)
  /rank delete <rank>             members go back to the default rank (repeat to confirm)
  /rank name <rank> <name...>  |  /rank prefix <rank> <text...|none>  |  /rank colour <rank> <#rrggbb|red|none> (alias color)
  /rank staff <rank> <on|off>  |  /rank up <rank>  |  /rank down <rank>
  /rank grant <rank> <node>    |  /rank ungrant <rank> <node>
  /rank set <player> <rank>    |  /rank clear <player>      (hytale:Adventurer is always kept; the reply lists the player's groups)
  /rank who <player>              rank, engine groups, denies, personal grants
  /rank deny <player> <node>   |  /rank undeny <player> <node>
  /rank default <rank>            the same as the ranks.default setting (through the config kit: validated, logged, versioned)
  <rank> = id or display name. <player> = online name, a seen player's name, or a UUID. All arguments required (no optional args).

THE EDITOR PAGE (RankPage; inline only, ids SkyyRk..., root Group anchor Width/Height only, 1120 x 930 so it fits 1080 high, TextButton +
  EventData, TextFields read back with "@Key" "#Id.Value" and kept as drafts through every rebuild, no periodic updates, no hover
  bindings, never closes itself before opening another page; guard() re-checks skyyranks.admin FIRST in build() and handleDataEvent()):
  Tabs: Ranks | Players (+ Settings | Grants | Members inside a rank).
  Ranks: 7 rows per page, highest first: position, name, DEFAULT/STAFF tags, members / grants / inherited count, coloured prefix preview,
         Up / Down / Edit / Delete; a New rank row (id + name + Create rank).
  Rank > Settings: display name, chat prefix (preview), prefix colour (#rrggbb or a colour word), staff ON/OFF, position Up/Down,
         Make default (through the kit's ranks.default), Delete.
  Rank > Grants: own grants (Remove) then the ones copied from lower ranks (grey, "from <rank>"); Grant by typing a node; Search the
         server's registered permission nodes (PermissionsModule.getRegisteredPermissions, 20 hits at most) and Grant from the hits.
  Rank > Members: members (Remove), Add member by name or UUID, Online players list with Add.
  Players: online players first, then seen players (filter box); Open -> the player view.
  Player: rank picker (< name >, Set rank), their engine groups (read-only - shows hytale:Adventurer), personal denies (Remove), Deny by
         typing a node, or Search the registered nodes and Deny from the hits (how an auto command node like /pay's is found).
  Confirm: the question, Confirm / Cancel. Footer: Prev / Next, Refresh, < Server Setup (only when /modconfig exists), Close.

CONFIG (tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md; shows in SkyyMenu 0.3 Server Setup as "Ranks"):
  config:def:SkyyRanks / config:fn:SkyyRanks / config:epoch:SkyyRanks. File Skyy_SkyyRanks/config.properties. Node skyyranks.admin.
  ranks.editor   link   rankadmin
  ranks.default  text   member   (field RankCfg.DEFAULT_RANK; check= refuses an unknown rank or one with members or grants; after= moves it
                                  to the bottom of the ladder and re-syncs. text, not the spec's choice: rank ids are made in game, a kit
                                  choice list is fixed at build time)
  chat.prefix    bool   true     live
  chat.priority  int    31000    restart, adv (-32768..32767; check= asks first at 30000 or below: the title would come first)
  The kit's own permission re-check is routed through RankPerm.has (PERM_FN): the same PermissionsModule.hasPermission(who, node)
  call the kit makes by default, false on any error; it keeps RankPerm the one class that touches the permission system.
  Rank edits are not kit rows (the ranks file is the mod's own); they are logged in the same Skyy_SkyyRanks/config-changes.log with the
  kit's line format and status "done" (key rank[<id>], rank[<id>].name|prefix|colour|staff|position, rank[<id>].grant[<node>],
  member[<player>], deny[<player>]), so SkyyMenu's Changes view lists them without offering an Undo it cannot do. The Ranks editor row's
  help and the kit NOTE say so on the Server Setup page (rank edits are reversed in the editor).

BRIDGE (System.getProperties().get("skyy.bridge"), java.lang types only): rank:<uuid> = display name, rank:prefix:<uuid>, rank:colour:<uuid>
  ("" = plain), rank:id:<uuid> (published at join and after every change for members + online players; the default rank for players
  without one), rank:fn:of = Function (UUID or uuid String) -> String[] {id, name, prefix, colour, "true"/"false" staff}, rank:version.
  The marker node skyyranks.rank.<id> is on its own group and every higher one, so hasPermission("skyyranks.rank.vip") = "VIP or higher".

FILES (<world>/mods/Skyy_SkyyRanks/): config.properties (kit rows), ranks.properties (the mod's own writer: atomic tmp + fsync + move,
  \\uXXXX for non-ASCII), players.properties (uuid=rank|last name, rank empty = default; membership written at once, name-only updates
  5 s later), config-changes.log + config-history/ (kit). Ranks are per ACCOUNT, not per profile (PROFILES-CONTRACT: nothing to key).

THREADS: commands and page clicks on the admin's world thread; single-player engine changes run inline (a handful of calls; the engine
  saves permissions.json itself, synchronously, like vanilla /perm); a deleted rank's members are cleaned up by RankBulkTask on the
  scheduler; joins are handled 3 s after the first PlayerReadyEvent of a connection on the scheduler (PlayerReadyEvent fires on every
  world switch; RankReady keys on the connection's PlayerRef object, so a reconnect re-arms even before the old disconnect is handled). Locks: RankEngine.class (engine changes) may take RankStore.class inside it, never the other way round; the kit's monitors
  are never held while our code runs. No ECS systems, no components.

VERIFIED this session (HytaleServer.jar bytecode / reflection, tools/dev/bc.py, reflect.py, clinit.py): the provider methods above and
  their save = syncSave; removeGroupPermissions deletes a non-built-in group whose set becomes empty (hence the marker node);
  PermissionsModule mutators act on getFirstPermissionProvider() and fire PlayerGroupEvent / GroupPermissionChangeEvent +
  resendCommandTreeForPlayer; hasPermission order = user nodes, then each group (nodes, virtual grants, parent chain); inside one set
  "-*", then "-node", then "node", then deny wildcards, then "*"; PermissionsModule.start() = syncLoad; PluginBase.start0 sets ENABLED
  after start(); DEFAULT_GROUP_LIST = {hytale:Adventurer}; getRegisteredPermissions() = node -> groups; no vanilla /rank or /rankadmin root
  command (only the "rank" subcommand of /reputation); the provider's read() validates group names only, not nodes, and
  isValidPermissionNode("*") is false (so * is allowed explicitly); the vanilla listeners of the permission events (FlyCameraModule,
  WorldMapTracker, BuilderToolsPlugin) only read permissions and send packets (WorldMapTracker hops with world.execute), so engine calls
  from the scheduler thread are safe; resendCommandTreeForPlayer only writes a packet. Review pass (same day): hasPermission(Set,
  PermissionQuery) + the PermissionQuery constructor (wildcards = every dot-prefix of the node + ".*", the node itself included; no
  mid-part globbing, so skyyranks.a* grants nothing); PlayerRef.clone() returns this (one PlayerRef per connection across worlds).

CHECKED in a bare JVM (2026-09-25, scratch harness under tools/dev/scratch, deleted afterwards; 284 checks, 0 fails): all 50 classes load
  under -Xverify:all; a fake engine with the provider's real semantics (incl. the addUserToGroup trap, empty-group deletion, user denies
  first, the Admin parent chain) proved: no engine write before ENABLED; seeded only Member (no group); new ranks above the default;
  inheritance sets exact after grant / move (both directions); dangerous grant, move, assign, delete, deny-on-op/staff and self-lockout
  confirms; assign / re-assign / clear always end with hytale:Adventurer and exactly one skyy group, op keeps hytale:Admin; user denies
  beat rank grants and op; delete empties the group and the background clean-up keeps Adventurer; join clean-up (two ranks, dangling
  and default groups out, hand-made groups with nodes kept, store adopts the engine); reconcile; hand-edit guard + reload; unreadable
  ranks.properties = no sync, no edits; \\uXXXX round trip; the kit rows (ranks.default check with members / grants / display name,
  default switch re-syncs, chat.priority asks at <= 30000 and is RESTART, chat.prefix live, non-admin denied, export -> import preview
  "nothing to change", config line rewritten with comments kept); the change log lines; rank:fn:of never throws; chat confirm memory;
  the page in every view and mode (balanced markup, unique ids, no underscores, every event and set on an existing id, drafts kept,
  paging, confirm / cancel, guard locks a non-admin and an admin who lost the node); every command and subcommand (23) requires
  skyyranks.admin and has no permission groups.
  NOT re-run in the harness after the review fixes (default rank pinned at the floor + floorDefault, editor-loss confirms for other
  players / grant removal / moves, RankPerm.grants, the per-connection join guard, clean() dropping format characters, the unknown-group
  hint): compiled and linted only - they are in the in-game steps.
"""
import sys, os, re, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.ranks"
T = {
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PGE":  "com.hypixel.hytale.protocol.packets.interface_.Page",
    "PM":   "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    "PP":   "com.hypixel.hytale.server.core.permissions.provider.PermissionProvider",
    "PV":   "com.hypixel.hytale.server.core.permissions.PermissionValidation",
    "PST":  "com.hypixel.hytale.server.core.plugin.PluginState",
    "PCE":  "com.hypixel.hytale.server.core.event.events.player.PlayerChatEvent",
    "PCF":  "com.hypixel.hytale.server.core.event.events.player.PlayerChatEvent$Formatter",
    "PRE":  "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE":  "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "CMGR": "com.hypixel.hytale.server.core.command.system.CommandManager",
    "ACM":  "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "PKG":  PKG,
    "VERSION": VERSION,
    "ADMIN": 'requirePermission("skyyranks.admin");',
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
ER = "com.hypixel.hytale.event.EventRegistry"
for c, m in ((T["PM"], "get"), (T["PM"], "getGroupsForUser"), (T["PM"], "addUserToGroup"), (T["PM"], "removeUserFromGroup"),
             (T["PM"], "addGroupPermission"), (T["PM"], "removeGroupPermission"), (T["PM"], "addUserPermission"),
             (T["PM"], "removeUserPermission"), (T["PM"], "getAllRegisteredGroups"), (T["PM"], "getRegisteredPermissions"),
             (T["PM"], "getFirstPermissionProvider"), (T["PM"], "hasPermission"), (T["PP"], "getGroupPermissions"),
             (T["PP"], "getUserPermissions"), (T["PV"], "isValidPermissionNode"), (T["PV"], "isValidGroupName"), (PB, "getState"),
             (T["PST"], "ENABLED"), (T["UNI"], "get"), (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"), (T["PR"], "getUuid"),
             (T["PR"], "getUsername"), (T["PR"], "sendMessage"), (T["PR"], "isValid"), (T["HSV"], "SCHEDULED_EXECUTOR"),
             (PB, "shutdown"), (PB, "getDataDirectory"), (PB, "getCommandRegistry"), (PB, "getEventRegistry"), (PB, "getLogger"),
             (ER, "registerGlobal"), (ER, "registerAsyncGlobal"), (T["ACM"], "requirePermission"), (T["ACM"], "addSubCommand"),
             (T["ACM"], "withRequiredArg"), (T["ACM"], "addAliases"), (T["ATY"], "STRING"), (T["ATY"], "GREEDY_STRING"),
             (T["CTX"], "get"), (T["CTX"], "getInputString"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["MSG"], "join"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["EVD"], "append"),
             (T["BT"], "Activating"), (T["BT"], "Validating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"),
             (T["PAGE"], "build"), (PGM, "openCustomPage"), (PGM, "setPage"), (T["PLA"], "getPageManager"), (T["PGE"], "None"),
             (T["LIFE"], "CanDismiss"), (T["PCE"], "getFormatter"), (T["PCE"], "setFormatter"), (T["PCE"], "DEFAULT_FORMATTER"),
             (T["PCF"], "format"), (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"), (T["CMGR"], "get"),
             (T["CMGR"], "resolveCommand"), (T["CMGR"], "handleCommand")):
    B.probe(pool, c, m)

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def jlit(s):
    return json.dumps(s)          # a valid Java string literal for plain text (no surrogate tricks needed here)


def mk(name, sup=None, ifaces=()):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    for i in ifaces:
        c.addInterface(pool.get(i))
    return c


# ================= config text (the kit's DEFAULTS and the mod's own first-run file are the same text) =================
CONFIG_TEXT = "\n".join([
    "# SkyyRanks settings. Change them in game: SkyWynn Menu -> Server Setup -> Ranks (SkyyMenu 0.3), or edit here and use /rankadmin reload.",
    "# The ranks themselves (names, prefixes, colours, grants) are made with /rankadmin and live in ranks.properties.",
    "#",
    "# ranks.default = the rank shown for every player without a rank (a rank id). It has no members and no grants.",
    "ranks.default=member",
    "# chat.prefix = put the rank prefix in front of chat messages: [Rank] [Title] Name: text",
    "chat.prefix=true",
    "# chat.priority = when the prefix is added (read at server start only). SkyyExploration's title uses 30000; keep the rank above it.",
    "chat.priority=31000",
    "",
])

# ================= RankCfg fields (the kit binds them, so they exist before CFG.emit) =================
cfg = mk("RankCfg")
for f in ("public static volatile String DEFAULT_RANK = \"member\";", "public static volatile boolean CHAT_PREFIX = true;",
          "public static volatile int CHAT_PRIORITY = 31000;", "public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;",
          "public static @LOG@ LOG;", "public static volatile boolean INLINE;", "public static volatile java.util.ArrayList TEST_ONLINE;",
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT)):
    F(cfg, f)

# ================= RankPerm (first part): the ONLY class that talks to the engine's permission system =================
# FAKE = the bare-JVM test engine (null in game). has() is also the config kit's permission check (PERM_FN below): the same
# PermissionsModule.get().hasPermission(who, node) call the kit makes by default, false on any error - one engine door for the mod.
perm = mk("RankPerm")
F(perm, "public static volatile java.util.function.Function FAKE;")
M(perm, r"""
public static Object fake(String op, Object a, Object b) {
  return FAKE.apply(new Object[] { op, a, b });
}""")
M(perm, r"""
public static boolean has(java.util.UUID u, String node) {
  if (u == null || node == null) return false;
  try {
    if (FAKE != null) return Boolean.TRUE.equals(fake("has", u, node));
    return @PM@.get().hasPermission(u, node);
  } catch (Throwable t) { return false; }
}""")

# ================= the admin config kit (research/Server-Setup-Spec.md 4.19; tools/CONFIG-CONTRACT.md) =================
CATS = [("ranks", "Ranks"), ("chat", "Chat")]
ROWS = [
    ("ranks.editor", "Ranks editor", "ranks", "link", "", "", "", "rankadmin", "", "",
     "Ranks, prefixes, grants, members, denies. No Undo in Changes for these: change them back here.", ""),
    ("ranks.default", "Default rank", "ranks", "text", "member", "2", "16", "", "", "live",
     "Rank id for players without a rank: no members, no grants. It moves to the bottom of the ladder.",
     "field:RankCfg.DEFAULT_RANK@config.properties:ranks.default;check=RankHooks.checkDefault;after=RankHooks.afterDefault"),
    ("chat.prefix", "Rank prefix in chat", "chat", "bool", "true", "", "", "", "", "live",
     "Puts the rank prefix in front of chat messages: [Rank] [Title] Name.",
     "field:RankCfg.CHAT_PREFIX@config.properties:chat.prefix"),
    ("chat.priority", "Chat prefix order", "chat", "int", "31000", "-32768", "32767", "", "", "restart,adv",
     "Keep it above SkyyExploration's 30000 so the rank comes before the title.",
     "field:RankCfg.CHAT_PRIORITY@config.properties:chat.priority;check=RankHooks.checkPriority"),
]
kit = CFG.emit(pool, PKG, MOD="SkyyRanks", TITLE="Ranks", VERSION=VERSION, NODE="skyyranks.admin", CATS=CATS, ROWS=ROWS,
               FILES=["Skyy_SkyyRanks/config.properties"], NOTE="Ranks, grants, members, denies: Ranks editor (/rankadmin). Undo rank edits there, not in Changes.",
               RELOAD="RankHooks.reloadCfg", KEEP=20, DEFAULTS={"config.properties": CONFIG_TEXT}, PERM_FN="RankPerm.has")

# ================= RankCfg methods: logging, bridge, scheduler, online players, config.properties loader =================
M(cfg, r"""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyRanks] " + m); else System.out.println("[SkyyRanks] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyRanks] " + m); else System.out.println("[SkyyRanks] WARNING " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void severe(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.SEVERE).log("[SkyyRanks] " + m); else System.out.println("[SkyyRanks] SEVERE " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warnOnce(String key, String m) {
  if (key != null && WARNED.putIfAbsent(key, Boolean.TRUE) == null) warn(m);
}""")
M(cfg, r"""
public static Object makeBridge() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return o;
}""")
# the pack-wide bridge map; created under the System.class monitor (the same lock every Skyy mod uses), one call inside the block
M(cfg, r"""
public static java.util.Map bridge() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o instanceof java.util.Map) return (java.util.Map) o;
  synchronized (java.lang.System.class) { o = makeBridge(); }
  return (java.util.Map) o;
}""")
# a one-shot task on the server scheduler; bare JVM (tests) or INLINE: run it now on this thread
M(cfg, r"""
public static void later(Runnable r, long ms) {
  if (r == null) return;
  if (!INLINE) {
    try { @HSV@.SCHEDULED_EXECUTOR.schedule(r, ms, java.util.concurrent.TimeUnit.MILLISECONDS); return; } catch (Throwable t) { }
  }
  try { r.run(); } catch (Throwable t2) { warn("task failed: " + t2); }
}""")
# online players as String[] { uuid, name } (Universe.getPlayers is a concurrent collection, safe from any thread)
M(cfg, r"""
public static java.util.ArrayList online() {
  if (TEST_ONLINE != null) return new java.util.ArrayList(TEST_ONLINE);
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null) continue;
      out.add(new String[] { p.getUuid().toString(), p.getUsername() });
    }
  } catch (Throwable t) { }
  return out;
}""")
M(cfg, r"""
public static boolean isOnline(String us) {
  java.util.ArrayList l = online();
  for (int i = 0; i < l.size(); i++) if (((String[]) l.get(i))[0].equals(us)) return true;
  return false;
}""")
M(cfg, r"""
public static String colourOf(String r) {
  if (r == null || r.length() == 0) return "#ffd27f";
  char c = r.charAt(0);
  if (c == '+') return "#8fe08f";
  if (c == '-') return "#ff8f8f";
  return "#ffd27f";
}""")
M(cfg, r"""
public static String textOf(String r) {
  if (r == null || r.length() == 0) return "";
  char c = r.charAt(0);
  if (c == '+' || c == '-' || c == '=' || c == '?') return r.substring(1);
  return r;
}""")
M(cfg, r"""
public static void tellPr(@PR@ pr, String r) {
  try { if (pr != null && r != null) pr.sendMessage(@MSG@.raw("[Ranks] " + textOf(r)).color(colourOf(r))); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void tell(java.util.UUID u, String r) {
  if (u == null) return;
  try { @PR@ p = @UNI@.get().getPlayer(u); if (p != null && p.isValid()) tellPr(p, r); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static boolean bool(String v, boolean d) {
  if (v == null) return d;
  String s = v.trim().toLowerCase();
  if (s.equals("true") || s.equals("on") || s.equals("yes") || s.equals("1")) return true;
  if (s.equals("false") || s.equals("off") || s.equals("no") || s.equals("0")) return false;
  return d;
}""")
M(cfg, r"""
public static int intOf(String v, int d) {
  if (v == null) return d;
  try { return Integer.parseInt(v.trim()); } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static void writeDefaults() {
  try {
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
  } catch (Throwable t) { warn("could not write the default config.properties: " + t); }
}""")
# the mod's own loader (the kit reads the same file for its rows). chat.priority is only read at the first load: the hook is
# registered once in setup(), so a later value waits for a restart (the kit shows it as RESTART)
M(cfg, r"""
public static String loadCfg(boolean first) {
  java.util.Properties p = new java.util.Properties();
  if (first) writeDefaults();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) { warn("config.properties could not be read - defaults are used: " + t); }
  String d = p.getProperty("ranks.default", "member").trim().toLowerCase();
  if (!d.matches("[a-z][a-z0-9]{1,15}")) { warn("config.properties: ranks.default=" + d + " is not a rank id - member is used"); d = "member"; }
  DEFAULT_RANK = d;
  CHAT_PREFIX = bool(p.getProperty("chat.prefix"), true);
  if (first) {
    int pr = intOf(p.getProperty("chat.priority"), 31000);
    if (pr < -32768) pr = -32768;
    if (pr > 32767) pr = 32767;
    CHAT_PRIORITY = pr;
  }
  return "default rank " + d + ", chat prefix " + (CHAT_PREFIX ? "on" : "off") + ", chat priority " + CHAT_PRIORITY;
}""")

# ================= RankUI: every inline markup string (validated below: balanced, no underscore ids, ids start with SkyyRk) =================
def tbs(bg, fg, hov, pre, fs=18):
    lab = "LabelStyle: (FontSize: %d, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)" % (fs, fg)
    return ("Style: TextButtonStyle(Default: (Background: " + bg + ", " + lab + "), Hovered: (Background: " + hov + ", " + lab + "), "
            "Pressed: (Background: " + pre + ", " + lab + "));")


SBS = tbs("#5a4420", "#ffe9c9", "#8a6a30", "#3a2a10")        # the SkyWynn Menu brown buttons
ON_SEL = tbs("#7fe07f", "#062a06", "#a0f0a0", "#5fb05f")
OFF_SEL = tbs("#e07070", "#2a0606", "#f09090", "#b05050")
TAB_SEL = tbs("#e0b060", "#2a1a00", "#f0c880", "#b08840")
RED = tbs("#a03030", "#ffffff", "#c04040", "#801818")
GRN = tbs("#1f5a34", "#e6ffe8", "#2c7a48", "#133a22")
PW, PH, NROWS = 1120, 930, 7
TABS = ["Ranks", "Players", "Settings", "Grants", "Members"]


def btn(ident, w, text, style, h=52):
    return 'TextButton #%s { Anchor: (Width: %d, Height: %d); Text: "%s"; %s }' % (ident, w, h, text, style)


UI = {
    "ROOT":   "Group #SkyyRk { Anchor: (Width: %d, Height: %d); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 14); LayoutMode: Top; }" % (PW, PH),
    "ACCENT": "Group { Anchor: (Height: 3); Background: #e0b060; }",
    "TITLE":  'Label #SkyyRkTitle { Anchor: (Height: 48); Text: ""; Style: (FontSize: 28, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "HINT":   'Label #SkyyRkHint { Anchor: (Height: 26); Text: ""; Style: (FontSize: 16, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "TABS":   "Group #SkyyRkTabs { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 5); }",
    "SP12":   'Label { Anchor: (Width: 12, Height: 48); Text: ""; }',
    "SP48":   'Label { Anchor: (Width: 48, Height: 48); Text: ""; }',
    "GAP8":   "Group { Anchor: (Height: 8); }",
    "GAP6":   "Group { Anchor: (Height: 6); }",
    "HEAD":   'Label #SkyyRkHead { Anchor: (Height: 40); Text: ""; Style: (FontSize: 24, RenderBold: true, TextColor: #e0b060, VerticalAlignment: Center); }',
    "ROWS":   "Group #SkyyRkRows { Anchor: (Height: %d); LayoutMode: Top; }" % (NROWS * 76),
    "ROW":    "Group #SkyyRkRow%R { Anchor: (Height: 70); Background: #142030(0.92); LayoutMode: Left; Padding: (Top: 9); }",
    "LEAD":   'Label { Anchor: (Width: 14, Height: 52); Text: ""; }',
    "SP10":   'Label { Anchor: (Width: 10, Height: 52); Text: ""; }',
    "GAPUD":  'Label { Anchor: (Width: 180, Height: 52); Text: ""; }',
    "TXTA":   "Group #SkyyRkTxt%R { Anchor: (Width: 470, Height: 52); LayoutMode: Top; }",
    "TXTB":   "Group #SkyyRkTxt%R { Anchor: (Width: 440, Height: 52); LayoutMode: Top; }",
    "TXTC":   "Group #SkyyRkTxt%R { Anchor: (Width: 880, Height: 52); LayoutMode: Top; }",
    "TXTD":   "Group #SkyyRkTxt%R { Anchor: (Width: 700, Height: 52); LayoutMode: Top; }",
    "TXTE":   "Group #SkyyRkTxt%R { Anchor: (Width: 270, Height: 52); LayoutMode: Top; }",
    "TXTF":   "Group #SkyyRkTxt%R { Anchor: (Width: 500, Height: 52); LayoutMode: Top; }",
    "NAME":   'Label #SkyyRkName%R { Anchor: (Height: 28); Text: ""; Style: (FontSize: 21, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }',
    "NAMEDIM": 'Label #SkyyRkName%R { Anchor: (Height: 28); Text: ""; Style: (FontSize: 21, RenderBold: true, TextColor: #8fa0b0, VerticalAlignment: Center); }',
    "DESC":   'Label #SkyyRkDesc%R { Anchor: (Height: 24); Text: ""; Style: (FontSize: 16, TextColor: #b8c8d8, VerticalAlignment: Center); }',
    "PRE":    'Label #SkyyRkPre%R { Anchor: (Width: 150, Height: 52); Text: ""; Style: (FontSize: 20, RenderBold: true, TextColor: %C, VerticalAlignment: Center); }',
    "PICK":   'Label #SkyyRkPick { Anchor: (Width: 220, Height: 52); Text: ""; Style: (FontSize: 19, RenderBold: true, TextColor: #ffe9a0, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "BOX":    "Group #SkyyRkBox%R { Anchor: (Width: 300, Height: 52); Background: #16263a; }",
    "IN":     "TextField #SkyyRkIn%R { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 40; Style: (TextColor: #ffffff, FontSize: 18); }",
    "UP":     btn("SkyyRkUp%R", 80, "Up", SBS),
    "DOWN":   btn("SkyyRkDown%R", 80, "Down", SBS),
    "EDIT":   btn("SkyyRkEdit%R", 110, "Edit", SBS),
    "DEL":    btn("SkyyRkDel%R", 110, "Delete", RED),
    "REM":    btn("SkyyRkRem%R", 150, "Remove", RED),
    "OPEN":   btn("SkyyRkOpen%R", 150, "Open", SBS),
    "ADDR":   btn("SkyyRkAddr%R", 150, "Add", GRN),
    "GR":     btn("SkyyRkGr%R", 150, "Grant", GRN),
    "DENYB":  btn("SkyyRkDn%R", 150, "Deny", RED),
    "SET":    btn("SkyyRkSet%R", 110, "Set", GRN),
    "CLR":    btn("SkyyRkClr%R", 110, "Clear", SBS),
    "ON":     btn("SkyyRkOn%R", 120, "ON", SBS),
    "ONSEL":  btn("SkyyRkOn%R", 120, "ON", ON_SEL),
    "OFF":    btn("SkyyRkOff%R", 120, "OFF", SBS),
    "OFFSEL": btn("SkyyRkOff%R", 120, "OFF", OFF_SEL),
    "UP2":    btn("SkyyRkUp%R", 120, "Up", SBS),
    "DOWN2":  btn("SkyyRkDown%R", 120, "Down", SBS),
    "MK":     btn("SkyyRkMk%R", 200, "Make default", GRN),
    "DEL2":   btn("SkyyRkDel%R", 120, "Delete", RED),
    "CYP":    btn("SkyyRkCyp", 60, "<", SBS),
    "CYN":    btn("SkyyRkCyn", 60, ">", SBS),
    "SETRANK": btn("SkyyRkSetRank", 150, "Set rank", GRN),
    "EMPTY":  'Label #SkyyRkEmpty { Anchor: (Height: 90); Text: ""; Style: (FontSize: 19, TextColor: #c9dff0, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "ADD":    "Group #SkyyRkAdd { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 8); }",
    "ADDLBL": 'Label #SkyyRkAddLbl { Anchor: (Width: 130, Height: 46); Text: ""; Style: (FontSize: 19, RenderBold: true, TextColor: #e0b060, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "ADDSP":  'Label { Anchor: (Width: 10, Height: 46); Text: ""; }',
    "FB0":    "Group #SkyyRkFB0 { Anchor: (Width: %W, Height: 46); Background: #16263a; }",
    "FB1":    "Group #SkyyRkFB1 { Anchor: (Width: %W, Height: 46); Background: #16263a; }",
    "F0":     'TextField #SkyyRkF0 { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 80; PlaceholderText: "%P"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17); Style: (TextColor: #ffffff, FontSize: 18); }',
    "F1":     'TextField #SkyyRkF1 { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 80; PlaceholderText: "%P"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17); Style: (TextColor: #ffffff, FontSize: 18); }',
    "ACT0":   'TextButton #SkyyRkAct0 { Anchor: (Width: %W, Height: 46); Text: "%T"; ' + GRN + " }",
    "ACT1":   'TextButton #SkyyRkAct1 { Anchor: (Width: %W, Height: 46); Text: "%T"; ' + SBS + " }",
    "STOK":   'Label #SkyyRkStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #8fe08f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "STBAD":  'Label #SkyyRkStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #ff8f8f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "STINFO": 'Label #SkyyRkStatus { Anchor: (Height: 30); Text: ""; Style: (FontSize: 17, RenderBold: true, TextColor: #ffd27f, HorizontalAlignment: Center, VerticalAlignment: Center); }',
    "FOOT":   "Group #SkyyRkFoot { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 6); }",
    "FLEAD":  'Label { Anchor: (Width: 40, Height: 50); Text: ""; }',
    "FSP":    'Label { Anchor: (Width: 10, Height: 50); Text: ""; }',
    "PREV":   btn("SkyyRkPrev", 150, "< Prev", SBS, 50),
    "NEXT":   btn("SkyyRkNext", 150, "Next >", SBS, 50),
    "REFRESH": btn("SkyyRkRefresh", 170, "Refresh", SBS, 50),
    "SETUP":  btn("SkyyRkSetup", 240, "< Server Setup", SBS, 50),
    "CLOSE":  btn("SkyyRkClose", 170, "Close", SBS, 50),
    "MSGBOX": "Group #SkyyRkMsgBox { Anchor: (Height: 300); Background: #142030(0.92); Padding: (Horizontal: 40, Vertical: 30); LayoutMode: Top; }",
    "MSG":    'Label #SkyyRkMsg { Anchor: (Height: 240); Text: ""; Style: (FontSize: 21, TextColor: #ffe9c9, Wrap: true); }',
    "CROW":   "Group #SkyyRkCRow { Anchor: (Height: 80); LayoutMode: Left; Padding: (Top: 14); }",
    "CLEAD":  'Label { Anchor: (Width: 270, Height: 56); Text: ""; }',
    "CSP":    'Label { Anchor: (Width: 40, Height: 56); Text: ""; }',
    "YES":    btn("SkyyRkYes", 250, "Confirm", RED, 56),
    "NO":     btn("SkyyRkNo", 250, "Cancel", SBS, 56),
}
UI_TAB = ['TextButton #SkyyRkTab%d { Anchor: (Width: 190, Height: 48); Text: "%s"; %s }' % (i, t, SBS) for i, t in enumerate(TABS)]
UI_TABSEL = ['TextButton #SkyyRkTab%d { Anchor: (Width: 190, Height: 48); Text: "%s"; %s }' % (i, t, TAB_SEL) for i, t in enumerate(TABS)]
# placeholder and button texts that are substituted into F0/F1 (%P) and ACT0/ACT1 (%T) at runtime - validated like fixed inline text
TXT = {
    "P_ID": "id like vip", "P_NAME": "Display name like VIP", "P_NODE": "permission node or search words", "P_PLAYER": "player name or UUID",
    "P_FIND": "player name", "P_DENY": "permission node to deny",
    "A_CREATE": "Create rank", "A_GRANT": "Grant", "A_SEARCH": "Search", "A_BACKG": "Back to grants", "A_ADDM": "Add member",
    "A_ONLINE": "Online players", "A_BACKM": "Back to members", "A_FIND": "Search", "A_ALL": "Show all", "A_DENY": "Deny",
    "A_BACKD": "Back to denies",
}


def _check_ui(s, name):
    t = s.replace("%R", "0").replace("%C", "#ffffff").replace("%W", "100").replace("%P", "x").replace("%T", "x")
    assert t.count("{") == t.count("}") and t.count("(") == t.count(")"), "unbalanced inline UI %s: %s" % (name, s)
    for eid in re.findall(r"#([A-Za-z0-9_]+)\s*\{", t):
        assert "_" not in eid, "underscore in element id #" + eid
        assert eid.startswith("SkyyRk"), "ranks page ids start with SkyyRk: #" + eid
    assert "Anchow" not in t and ";;" not in t, name
    for txt_ in re.findall(r'(?:Text|PlaceholderText): "([^"]*)"', t):
        assert re.match(r"^[A-Za-z0-9 <>/-]*$", txt_), "inline text with unproven characters (use b.set): " + txt_


for k_, v_ in UI.items():
    _check_ui(v_, k_)
for v_ in UI_TAB + UI_TABSEL:
    _check_ui(v_, "TAB")
for k_, v_ in TXT.items():
    assert re.match(r"^[A-Za-z0-9 <>/-]+$", v_), "text constant with unproven characters: " + k_
assert "Top:" not in UI["ROOT"].split("Anchor: (")[1].split(")")[0] and "Width" in UI["ROOT"], "page root anchor must be Width/Height only"
# height budget: padding 2 x 14 + accent 3 + title 48 + hint 26 + tabs 58 + gap 8 + head 40 + rows 7 x 76 + add row 62 + status 30 + footer 62
_tall = 2 * 14 + 3 + 48 + 26 + 58 + 8 + 40 + NROWS * 76 + 62 + 30 + 62
assert _tall <= PH, "ranks page parts are %d px tall, page is %d" % (_tall, PH)
assert PH <= 1080 - 100, "the ranks page must fit a 1080 px high screen"
_confirm = 2 * 14 + 3 + 48 + 26 + 8 + 300 + 80 + 30 + 62
assert _confirm <= PH
INNER = PW - 40
for w_, what in ((14 + 470 + 150 + 10 + 80 + 10 + 80 + 10 + 110 + 10 + 110, "ranks row"), (14 + 440 + 300 + 10 + 110, "name row"),
                 (14 + 270 + 150 + 300 + 10 + 110 + 10 + 110, "prefix row"), (14 + 700 + 120 + 10 + 120, "on/off row"),
                 (14 + 700 + 200, "default row"), (14 + 880 + 150, "list row"), (14 + 500 + 60 + 10 + 220 + 10 + 60 + 10 + 150, "rank picker"),
                 (190 * 2 + 12 + 48 + 190 * 3 + 12 * 2, "tabs"), (130 + 10 + 220 + 10 + 340 + 10 + 220, "new rank row"),
                 (130 + 10 + 480 + 10 + 180 + 10 + 200, "add row"), (40 + 150 + 10 + 150 + 10 + 170 + 10 + 240 + 10 + 170, "footer"),
                 (270 + 250 + 40 + 250, "confirm row")):
    assert w_ <= INNER, "%s is %d px wide, the page has %d" % (what, w_, INNER)

ui = mk("RankUI")
for k_, v_ in UI.items():
    F(ui, "public static final String %s = %s;" % (k_, jlit(v_)))
for k_, v_ in TXT.items():
    F(ui, "public static final String %s = %s;" % (k_, jlit(v_)))
F(ui, "public static final String[] TAB = new String[] { %s };" % ", ".join(jlit(x) for x in UI_TAB))
F(ui, "public static final String[] TABSEL = new String[] { %s };" % ", ".join(jlit(x) for x in UI_TABSEL))
M(ui, r"""public static String r(String t, int r) { return t.replace("%R", String.valueOf(r)); }""")
M(ui, r"""public static String w(String t, int w) { return t.replace("%W", String.valueOf(w)); }""")

# ================= Rank (plain data; RankStore replaces whole lists, a published Rank is never changed again) =================
rk = mk("Rank")
for f in ("public String id;", "public String name;", "public String prefix;", "public String colour;", "public boolean staff;",
          "public java.util.TreeSet grants;"):
    F(rk, f)
C(rk, 'public Rank() { this.id = ""; this.name = ""; this.prefix = ""; this.colour = ""; this.staff = false; this.grants = new java.util.TreeSet(); }')
M(rk, r"""
public @PKG@.Rank copy() {
  @PKG@.Rank r = new @PKG@.Rank();
  r.id = this.id; r.name = this.name; r.prefix = this.prefix; r.colour = this.colour; r.staff = this.staff;
  r.grants = new java.util.TreeSet(this.grants);
  return r;
}""")

# ================= RankPerm (rest): every mutator refuses until PermissionsModule is ENABLED =================
# (its start() loads permissions.json; an earlier write would save an empty state over the file)
M(perm, r"""
public static boolean ready() {
  if (FAKE != null) return Boolean.TRUE.equals(fake("ready", null, null));
  try {
    @PM@ m = @PM@.get();
    if (m == null) return false;
    return m.getState() == @PST@.ENABLED;
  } catch (Throwable t) { return false; }
}""")
M(perm, r"""
public static java.util.Set groupsOf(java.util.UUID u) {
  if (u == null) return null;
  try {
    if (FAKE != null) return (java.util.Set) fake("groupsOf", u, null);
    return @PM@.get().getGroupsForUser(u);
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not read the permission groups of " + u + ": " + t); return null; }
}""")
M(perm, r"""
public static boolean addToGroup(java.util.UUID u, String g) {
  if (u == null || g == null || !ready()) return false;
  try {
    if (FAKE != null) { fake("addToGroup", u, g); return true; }
    @PM@.get().addUserToGroup(u, g);
    return true;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not add " + u + " to " + g + ": " + t); return false; }
}""")
M(perm, r"""
public static boolean removeFromGroup(java.util.UUID u, String g) {
  if (u == null || g == null || !ready()) return false;
  try {
    if (FAKE != null) { fake("removeFromGroup", u, g); return true; }
    @PM@.get().removeUserFromGroup(u, g);
    return true;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not remove " + u + " from " + g + ": " + t); return false; }
}""")
M(perm, r"""
public static java.util.Set groupNodes(String g) {
  try {
    if (FAKE != null) return (java.util.Set) fake("groupNodes", g, null);
    java.util.Set s = @PM@.get().getFirstPermissionProvider().getGroupPermissions(g);
    return s == null ? new java.util.HashSet() : s;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not read the nodes of " + g + ": " + t); return null; }
}""")
M(perm, r"""
public static boolean addGroupNodes(String g, java.util.Set nodes) {
  if (g == null || nodes == null || nodes.isEmpty() || !ready()) return false;
  try {
    if (FAKE != null) { fake("addGroupNodes", g, new java.util.HashSet(nodes)); return true; }
    @PM@.get().addGroupPermission(g, new java.util.HashSet(nodes));
    return true;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not add " + nodes + " to " + g + ": " + t); return false; }
}""")
M(perm, r"""
public static boolean removeGroupNodes(String g, java.util.Set nodes) {
  if (g == null || nodes == null || nodes.isEmpty() || !ready()) return false;
  try {
    if (FAKE != null) { fake("removeGroupNodes", g, new java.util.HashSet(nodes)); return true; }
    @PM@.get().removeGroupPermission(g, new java.util.HashSet(nodes));
    return true;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not remove " + nodes + " from " + g + ": " + t); return false; }
}""")
M(perm, r"""
public static java.util.Set userNodes(java.util.UUID u) {
  if (u == null) return null;
  try {
    if (FAKE != null) return (java.util.Set) fake("userNodes", u, null);
    java.util.Set s = @PM@.get().getFirstPermissionProvider().getUserPermissions(u);
    return s == null ? new java.util.HashSet() : s;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not read the personal nodes of " + u + ": " + t); return null; }
}""")
M(perm, r"""
public static boolean addUserNode(java.util.UUID u, String node) {
  if (u == null || node == null || !ready()) return false;
  java.util.HashSet s = new java.util.HashSet();
  s.add(node);
  try {
    if (FAKE != null) { fake("addUserNodes", u, s); return true; }
    @PM@.get().addUserPermission(u, s);
    return true;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not add " + node + " to " + u + ": " + t); return false; }
}""")
M(perm, r"""
public static boolean removeUserNode(java.util.UUID u, String node) {
  if (u == null || node == null || !ready()) return false;
  java.util.HashSet s = new java.util.HashSet();
  s.add(node);
  try {
    if (FAKE != null) { fake("removeUserNodes", u, s); return true; }
    @PM@.get().removeUserPermission(u, s);
    return true;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not remove " + node + " from " + u + ": " + t); return false; }
}""")
M(perm, r"""
public static java.util.Set allGroups() {
  try {
    if (FAKE != null) return (java.util.Set) fake("allGroups", null, null);
    return @PM@.get().getAllRegisteredGroups();
  } catch (Throwable t) { return new java.util.HashSet(); }
}""")
M(perm, r"""
public static java.util.Set registered() {
  try {
    if (FAKE != null) return (java.util.Set) fake("registered", null, null);
    return new java.util.TreeSet(@PM@.getRegisteredPermissions().keySet());
  } catch (Throwable t) { return new java.util.TreeSet(); }
}""")
# the engine's own node rule (PermissionValidation, VERIFIED regex ^-?\w[\w-]*(\.[\w*][\w*-]*)*$), with the same regex as a fallback.
# A bare * fails that rule (it is only used by registerPermission) but is what hytale:Admin holds; the provider validates only group
# names when it reads permissions.json (VERIFIED read() bytecode), so * is accepted here explicitly (a grant of * always asks first).
M(perm, r"""
public static boolean validNode(String n) {
  if (n == null || n.length() == 0 || n.length() > 120) return false;
  if (n.equals("*")) return true;
  try { return @PV@.isValidPermissionNode(n); } catch (Throwable t) { }
  return n.matches("-?\\w[\\w-]*(\\.[\\w*][\\w*-]*)*") || n.equals("*");
}""")
# does a node SET answer yes for one node, exactly as the engine decides it? PermissionsModule.hasPermission(Set, String) (a static
# pure function) first; the copy below is its VERIFIED bytecode (hasPermission(Set, PermissionQuery) + the PermissionQuery constructor):
# "-*", "-node", "node", deny wildcards "-a.*" / "-a.b.*" (longest first), "*", then wildcards "a.*", "a.b.*". A wildcard matches whole
# dot parts only (no mid-part globbing), and the node itself + ".*" counts: skyyranks.admin is granted by exactly skyyranks.admin, *,
# skyyranks.* and skyyranks.admin.* (the self-lockout checks and denies use this, never a hand-kept list)
M(perm, r"""
public static boolean grants(java.util.Set s, String node) {
  if (s == null || node == null || s.isEmpty()) return false;
  if (FAKE == null) {
    try { return Boolean.TRUE.equals(@PM@.hasPermission(s, node)); } catch (Throwable t) { }
  }
  if (s.contains("-*") || s.contains("-" + node)) return false;
  if (s.contains(node)) return true;
  String[] parts = node.split("\\.");
  String[] wc = new String[parts.length];
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < parts.length; i++) { if (i > 0) b.append('.'); b.append(parts[i]); wc[i] = b.toString() + ".*"; }
  for (int i = wc.length - 1; i >= 0; i--) if (s.contains("-" + wc[i])) return false;
  if (s.contains("*")) return true;
  for (int i = 0; i < wc.length; i++) if (s.contains(wc[i])) return true;
  return false;
}""")

# ================= RankStore: ranks.properties + players.properties, the ladder, the chat map, bridge publishing =================
st = mk("RankStore")
sav = mk("RankSaveTask", ifaces=("java.lang.Runnable",))
C(sav, "public RankSaveTask() { }")
HEAD_R = "".join(l + "\n" for l in [
    "# SkyyRanks ranks. Change them in game: /rankadmin (or SkyWynn Menu -> Server Setup -> Ranks -> Ranks editor).",
    "# Hand edits: best with the server stopped; while it runs, save the file and use /rankadmin reload right away.",
    "# One block per rank. order 1 = the lowest rank. A rank also gets every grant of the ranks below it.",
    "# The id is the part after rank. (a-z and 0-9, 2-16 characters, starting with a letter); its engine group is skyy:<id>.",
    "# prefix + colour are shown in chat as [Rank] [Title] Name (colour #rrggbb, empty = plain). grants = permission nodes, comma separated.",
    "# Members are given a rank in game (/rank set <player> <rank>); the default rank (config.properties ranks.default) has none.",
])
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path RFILE;", "public static java.nio.file.Path PFILE;",
          "public static volatile java.util.ArrayList RANKS = new java.util.ArrayList();",
          "public static final java.util.HashMap PLAYERS = new java.util.HashMap();",
          "public static volatile boolean BROKEN;", "public static volatile String WHY = \"\";",
          "public static volatile boolean PBROKEN;", "public static volatile String PWHY = \"\";",
          "public static long RMT = -1L;", "public static long RSZ = -1L;", "public static volatile int SKIPPED;",
          "public static boolean PDIRTY;", "public static boolean PSCHED;",
          "public static volatile java.util.Map CHAT = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile String[] DEFCHAT = new String[] { \"\", \"\" };",
          "public static final String HEAD_R = %s;" % jlit(HEAD_R)):
    F(st, f)
M(st, r"""
public static boolean validId(String id) {
  return id != null && id.matches("[a-z][a-z0-9]{1,15}");
}""")
M(st, r"""
public static String clip(String s, int max) {
  if (s == null) return "";
  return s.length() > max ? s.substring(0, max) : s;
}""")
# printable text for names and prefixes (a prefix is shown in front of every chat line of the rank's members): control characters
# (C0, DEL, C1), Unicode format characters (bidi overrides and isolates, zero-width characters) and line / paragraph separators are
# dropped, then trimmed and clipped
M(st, r"""
public static String clean(String s, int max) {
  if (s == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    int ty = Character.getType(c);
    if (ty == Character.CONTROL || ty == Character.FORMAT || ty == Character.LINE_SEPARATOR || ty == Character.PARAGRAPH_SEPARATOR) continue;
    b.append(c);
  }
  String t = b.toString().trim();
  return t.length() > max ? t.substring(0, max).trim() : t;
}""")
# "" = plain (none / clear / off / empty), "#rrggbb" lowercase, null = not a colour. A few colour words for convenience.
M(st, r"""
public static String normColour(String t) {
  if (t == null) return null;
  String s = t.trim().toLowerCase();
  if (s.length() == 0 || s.equals("none") || s.equals("clear") || s.equals("off") || s.equals("plain")) return "";
  String[] names = new String[] { "red", "#ff5555", "darkred", "#aa0000", "gold", "#ffaa00", "orange", "#ff8800", "yellow", "#ffff55",
    "green", "#55ff55", "darkgreen", "#00aa00", "aqua", "#55ffff", "cyan", "#55ffff", "blue", "#5555ff", "darkblue", "#0000aa",
    "purple", "#aa00aa", "pink", "#ff55ff", "white", "#ffffff", "gray", "#aaaaaa", "grey", "#aaaaaa", "black", "#000000" };
  for (int i = 0; i + 1 < names.length; i += 2) if (s.equals(names[i])) return names[i + 1];
  if (!s.startsWith("#")) s = "#" + s;
  if (s.length() != 7) return null;
  for (int i = 1; i < 7; i++) {
    char c = s.charAt(i);
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return null;
  }
  return s;
}""")
M(st, r"""
public static boolean validNode(String n) {
  return n != null && !n.startsWith("-") && @PKG@.RankPerm.validNode(n);
}""")
M(st, r"""
public static boolean dangerous(String n) {
  if (n == null) return false;
  return n.indexOf('*') >= 0 || n.endsWith(".admin") || n.equals("skyymenu.modconfig") || n.equals("skyyranks.admin");
}""")
M(st, r"""
public static String dangerText(String n) {
  if (n.equals("*")) return "* is every permission on the server, like op.";
  if (n.equals("skyyranks.admin")) return "It opens this ranks editor - its members could give themselves any permission.";
  if (n.equals("skyymenu.modconfig")) return "It opens Server Setup (every mod's settings, view only without the mod's own admin node).";
  if (n.indexOf('*') >= 0) return "A wildcard grants every node under it.";
  return "It opens an admin command or editor.";
}""")
# java.util.Properties escaping for values we write (non-ASCII as \uXXXX: ISO-8859-1 and UTF-8 readers see the same text)
M(st, r"""
public static String esc(String s) {
  if (s == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c == '\\') b.append("\\\\");
    else if (c == '\n') b.append("\\n");
    else if (c == '\r') b.append("\\r");
    else if (c == '\t') b.append("\\t");
    else if (c == ' ' && i == 0) b.append("\\ ");
    else if (c < 32 || c > 126) {
      String h = Integer.toHexString(c);
      b.append("\\u");
      for (int k = h.length(); k < 4; k++) b.append('0');
      b.append(h);
    } else b.append(c);
  }
  return b.toString();
}""")
# ---- the ladder (RANKS is copy-on-write: a published list is never changed, so reads need no lock)
M(st, r"""
public static int idx(java.util.ArrayList l, String id) {
  if (id == null) return -1;
  for (int i = 0; i < l.size(); i++) if (((@PKG@.Rank) l.get(i)).id.equals(id)) return i;
  return -1;
}""")
M(st, r"""
public static @PKG@.Rank find(String id) {
  java.util.ArrayList l = RANKS;
  int i = idx(l, id);
  return i < 0 ? null : (@PKG@.Rank) l.get(i);
}""")
M(st, r"""public static boolean isRank(String id) { return find(id) != null; }""")
M(st, r"""
public static String defaultId() {
  String d = @PKG@.RankCfg.DEFAULT_RANK;
  if (find(d) != null) return d;
  java.util.ArrayList l = RANKS;
  if (l.size() > 0) return ((@PKG@.Rank) l.get(0)).id;
  return "member";
}""")
M(st, r"""
public static String label(String id) {
  @PKG@.Rank r = find(id);
  return r == null ? String.valueOf(id) : r.name;
}""")
M(st, r"""
public static String resolveRank(String text) {
  if (text == null) return null;
  String t = text.trim();
  if (t.length() == 0) return null;
  java.util.ArrayList l = RANKS;
  String lo = t.toLowerCase();
  if (idx(l, lo) >= 0) return lo;
  for (int i = 0; i < l.size(); i++) { @PKG@.Rank r = (@PKG@.Rank) l.get(i); if (r.name.equalsIgnoreCase(t)) return r.id; }
  return null;
}""")
M(st, r"""
public static String idList() {
  java.util.ArrayList l = RANKS;
  StringBuilder b = new StringBuilder();
  for (int i = l.size() - 1; i >= 0; i--) { if (b.length() > 0) b.append(", "); b.append(((@PKG@.Rank) l.get(i)).id); }
  return b.toString();
}""")
M(st, r"""public static int position(String id) { return idx(RANKS, id); }""")
M(st, r"""
public static int grantCount(String id) {
  @PKG@.Rank r = find(id);
  return r == null ? 0 : r.grants.size();
}""")
M(st, r"""
public static String[] ownGrants(String id) {
  @PKG@.Rank r = find(id);
  if (r == null) return new String[0];
  return (String[]) r.grants.toArray(new String[0]);
}""")
# everything the rank's engine group holds: its marker + own grants + every LOWER non-default rank's marker and grants
M(st, r"""
public static java.util.TreeSet effectiveIn(java.util.ArrayList l, String id) {
  java.util.TreeSet s = new java.util.TreeSet();
  int at = idx(l, id);
  if (at < 0) return s;
  String def = defaultId();
  for (int i = 0; i <= at; i++) {
    @PKG@.Rank r = (@PKG@.Rank) l.get(i);
    if (r.id.equals(def)) continue;
    s.add("skyyranks.rank." + r.id);
    s.addAll(r.grants);
  }
  return s;
}""")
M(st, r"""public static java.util.TreeSet effective(String id) { return effectiveIn(RANKS, id); }""")
M(st, r"""
public static java.util.ArrayList inherited(String id) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList l = RANKS;
  int at = idx(l, id);
  if (at < 0) return out;
  @PKG@.Rank me = (@PKG@.Rank) l.get(at);
  String def = defaultId();
  java.util.HashSet seen = new java.util.HashSet(me.grants);
  for (int i = 0; i < at; i++) {
    @PKG@.Rank r = (@PKG@.Rank) l.get(i);
    if (r.id.equals(def)) continue;
    java.util.Iterator it = r.grants.iterator();
    while (it.hasNext()) { String n = (String) it.next(); if (seen.add(n)) out.add(new String[] { n, r.name }); }
  }
  return out;
}""")
M(st, r"""
public static String describeR(@PKG@.Rank r) {
  if (r == null) return "(none)";
  return r.name + "|" + r.prefix + "|" + r.colour + "|" + (r.staff ? "staff" : "-") + "|" + String.join(",", r.grants);
}""")
M(st, r"""public static String describe(String id) { return describeR(find(id)); }""")
# ---- the change log (the config kit's file and line format; status done = SkyyMenu offers no Undo for these)
M(st, r"""
public static void log(java.util.UUID who, String wn, String via, String key, String old, String nw) {
  try { @PKG@.CfgLog.add(who, wn, via, key, old, nw, "done"); @PKG@.CfgFile.logSoon(); } catch (Throwable t) { }
}""")
# ---- files
M(st, r"""
public static void replaceFile(java.nio.file.Path tmp, java.nio.file.Path f) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      try {
        java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
      } catch (java.nio.file.AtomicMoveNotSupportedException a) {
        java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      }
      return;
    } catch (java.nio.file.NoSuchFileException e) {
      throw e;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(st, r"""
public static void writeBytes(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(data);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  replaceFile(tmp, f);
}""")
M(st, r"""
public static String rankText(java.util.ArrayList l) {
  StringBuilder sb = new StringBuilder();
  sb.append(HEAD_R);
  sb.append("format=1\n");
  for (int i = 0; i < l.size(); i++) {
    @PKG@.Rank r = (@PKG@.Rank) l.get(i);
    String k = "rank." + r.id + ".";
    sb.append('\n');
    sb.append(k).append("order=").append(i + 1).append('\n');
    sb.append(k).append("name=").append(esc(r.name)).append('\n');
    sb.append(k).append("prefix=").append(esc(r.prefix)).append('\n');
    sb.append(k).append("colour=").append(esc(r.colour)).append('\n');
    sb.append(k).append("staff=").append(r.staff ? "true" : "false").append('\n');
    sb.append(k).append("grants=").append(esc(String.join(",", r.grants))).append('\n');
  }
  return sb.toString();
}""")
M(st, r"""
public static void stampRanks() {
  try {
    RMT = java.nio.file.Files.getLastModifiedTime(RFILE, new java.nio.file.LinkOption[0]).toMillis();
    RSZ = java.nio.file.Files.size(RFILE);
  } catch (Throwable t) { RMT = -1L; RSZ = -1L; }
}""")
# a hand edit made while the server runs is never overwritten: in-game rank edits wait for /rankadmin reload
M(st, r"""
public static String checkDisk() {
  try {
    if (RFILE == null || !java.nio.file.Files.exists(RFILE, new java.nio.file.LinkOption[0])) return null;
    long mt = java.nio.file.Files.getLastModifiedTime(RFILE, new java.nio.file.LinkOption[0]).toMillis();
    long sz = java.nio.file.Files.size(RFILE);
    if (RMT >= 0L && (mt != RMT || sz != RSZ)) return "-ranks.properties was edited on disk - use /rankadmin reload first (it keeps your edits), then try again.";
  } catch (Throwable t) { }
  return null;
}""")
M(st, r"""
public static String writeRanks(java.util.ArrayList l) {
  if (RFILE == null) return "no data folder";
  try {
    writeBytes(RFILE, rankText(l).getBytes("UTF-8"));
    stampRanks();
    return null;
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not save ranks.properties: " + t); return clip(String.valueOf(t), 160); }
}""")
M(st, r"""
public static synchronized String loadRanks() {
  SKIPPED = 0;
  if (!java.nio.file.Files.exists(RFILE, new java.nio.file.LinkOption[0])) {
    java.util.ArrayList l0 = new java.util.ArrayList();
    @PKG@.Rank m = new @PKG@.Rank();
    m.id = "member";
    m.name = "Member";
    l0.add(m);
    RANKS = l0;
    BROKEN = false;
    WHY = "";
    String e = writeRanks(l0);
    return e == null ? "ranks.properties created with the default rank Member" : "ranks.properties could not be created (" + e + ") - the rank Member is used from memory";
  }
  java.util.Properties p = new java.util.Properties();
  try {
    byte[] data = java.nio.file.Files.readAllBytes(RFILE);
    p.load(new java.io.ByteArrayInputStream(data));
    stampRanks();
  } catch (Throwable t) {
    BROKEN = true;
    WHY = clip(String.valueOf(t), 120);
    return "ranks.properties could not be read (" + WHY + ") - nothing is synced and every rank change is refused until it can be read (fix or delete it, then /rankadmin reload)";
  }
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {
    String k = String.valueOf(en.nextElement());
    if (!k.startsWith("rank.")) continue;
    int d2 = k.indexOf('.', 5);
    if (d2 > 5) ids.add(k.substring(5, d2));
  }
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.ArrayList ord = new java.util.ArrayList();
  java.util.Iterator it = ids.iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    if (!validId(id)) {
      SKIPPED++;
      @PKG@.RankCfg.warn("ranks.properties: " + id + " is not a valid rank id (a-z and 0-9, 2-16 characters, starting with a letter) - skipped; the next rank change in game rewrites the file without it");
      continue;
    }
    @PKG@.Rank r = new @PKG@.Rank();
    r.id = id;
    String nm = clean(p.getProperty("rank." + id + ".name", id), 24);
    r.name = nm.length() == 0 ? id : nm;
    r.prefix = clean(p.getProperty("rank." + id + ".prefix", ""), 32);
    String c = normColour(p.getProperty("rank." + id + ".colour", ""));
    if (c == null) { SKIPPED++; @PKG@.RankCfg.warn("ranks.properties: rank " + id + " colour is not #rrggbb - plain is used"); c = ""; }
    r.colour = c;
    r.staff = @PKG@.RankCfg.bool(p.getProperty("rank." + id + ".staff"), false);
    String[] parts = p.getProperty("rank." + id + ".grants", "").split(",");
    for (int k = 0; k < parts.length; k++) {
      String g = parts[k].trim();
      if (g.length() == 0) continue;
      if (!validNode(g)) { SKIPPED++; @PKG@.RankCfg.warn("ranks.properties: grant " + g + " of rank " + id + " is not a valid permission node - skipped"); continue; }
      r.grants.add(g);
    }
    int o = @PKG@.RankCfg.intOf(p.getProperty("rank." + id + ".order"), 1000);
    int pos = l.size();
    for (int q = 0; q < l.size(); q++) { if (((Integer) ord.get(q)).intValue() > o) { pos = q; break; } }
    l.add(pos, r);
    ord.add(pos, Integer.valueOf(o));
  }
  if (l.size() == 0) {
    BROKEN = true;
    WHY = "it has no valid rank";
    return "ranks.properties has no valid rank - nothing is synced and every rank change is refused until it has one (fix or delete it, then /rankadmin reload)";
  }
  RANKS = l;
  BROKEN = false;
  WHY = "";
  return l.size() + (l.size() == 1 ? " rank" : " ranks") + (SKIPPED > 0 ? " (" + SKIPPED + " bad entries skipped - see the warnings above)" : "");
}""")
M(st, r"""
public static String playersText() {
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyRanks players: uuid=rank|last known name (rank empty = the default rank). Written by the mod - give ranks in game (/rank set).\n");
  java.util.TreeMap m = new java.util.TreeMap(PLAYERS);
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String[] v = (String[]) e.getValue();
    sb.append((String) e.getKey()).append('=').append(esc(v[0] + "|" + v[1])).append('\n');
  }
  return sb.toString();
}""")
M(st, r"""
public static String writePlayers() {
  if (PFILE == null) return "no data folder";
  try { writeBytes(PFILE, playersText().getBytes("UTF-8")); return null; }
  catch (Throwable t) { @PKG@.RankCfg.warn("could not save players.properties: " + t); return clip(String.valueOf(t), 160); }
}""")
M(st, r"""
public static synchronized String loadPlayers() {
  if (!java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) { PBROKEN = false; PWHY = ""; PLAYERS.clear(); return "no players file yet"; }
  java.util.Properties p = new java.util.Properties();
  try {
    byte[] data = java.nio.file.Files.readAllBytes(PFILE);
    p.load(new java.io.ByteArrayInputStream(data));
  } catch (Throwable t) {
    PBROKEN = true;
    PWHY = clip(String.valueOf(t), 120);
    return "players.properties could not be read (" + PWHY + ") - membership changes are refused until it can be read";
  }
  PLAYERS.clear();
  int bad = 0;
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {
    String k = String.valueOf(en.nextElement());
    String us = null;
    try { us = java.util.UUID.fromString(k.trim()).toString(); } catch (Throwable t) { bad++; continue; }
    String v = p.getProperty(k, "");
    int bar = v.indexOf('|');
    String rid = (bar < 0 ? v : v.substring(0, bar)).trim().toLowerCase();
    String nm = bar < 0 ? "" : clean(v.substring(bar + 1), 32);
    if (rid.length() > 0 && !validId(rid)) { bad++; rid = ""; }
    PLAYERS.put(us, new String[] { rid, nm.length() == 0 ? us : nm });
  }
  PBROKEN = false;
  PWHY = "";
  return PLAYERS.size() + " players known" + (bad > 0 ? " (" + bad + " bad lines ignored)" : "");
}""")
M(st, r"""
public static synchronized void rebuildChat() {
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  String def = defaultId();
  java.util.Iterator it = PLAYERS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String[] v = (String[]) e.getValue();
    if (v[0].length() == 0 || v[0].equals(def)) continue;
    @PKG@.Rank r = find(v[0]);
    if (r == null) continue;
    m.put(e.getKey(), new String[] { r.prefix, r.colour });
  }
  CHAT = m;
  @PKG@.Rank d = find(def);
  DEFCHAT = d == null ? new String[] { "", "" } : new String[] { d.prefix, d.colour };
}""")
M(st, r"""
public static void rebuildChatSafe() {
  try { rebuildChat(); } catch (Throwable t) { @PKG@.RankCfg.warn("could not rebuild the chat prefixes: " + t); }
}""")
M(st, r"""
public static synchronized String reload() {
  String a = loadRanks();
  String b = loadPlayers();
  rebuildChat();
  return a + "; " + b;
}""")
M(st, r"""
public static synchronized String load(java.nio.file.Path dir) {
  DIR = dir;
  RFILE = dir.resolve("ranks.properties");
  PFILE = dir.resolve("players.properties");
  return reload();
}""")
M(st, r"""
public static java.util.ArrayList copyList() {
  java.util.ArrayList src = RANKS;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < src.size(); i++) l.add(((@PKG@.Rank) src.get(i)).copy());
  return l;
}""")
# write first, publish the new list only when the file says the same (memory == file)
M(st, r"""
public static synchronized String commit(java.util.ArrayList l) {
  if (BROKEN) return "-ranks.properties cannot be read (" + WHY + ") - fix or delete it, then /rankadmin reload. Nothing was changed.";
  String e = checkDisk();
  if (e != null) return e;
  String w = writeRanks(l);
  if (w != null) return "-ranks.properties could not be saved (" + w + ") - nothing was changed.";
  RANKS = l;
  rebuildChat();
  return null;
}""")
M(st, r"""
public static synchronized String create(String id0, String name0) {
  String id = id0 == null ? "" : id0.trim().toLowerCase();
  if (!validId(id)) return "-The rank id must be 2-16 characters: a-z and 0-9, starting with a letter (like vip or mod2).";
  if (find(id) != null) return "-There is already a rank with the id " + id + ".";
  String name = clean(name0, 24);
  if (name.length() == 0) return "-Give the rank a display name (1-24 characters), like VIP.";
  if (RANKS.size() >= 60) return "-60 ranks is the most this version keeps.";
  java.util.ArrayList l = copyList();
  int di = idx(l, defaultId());
  @PKG@.Rank r = new @PKG@.Rank();
  r.id = id;
  r.name = name;
  l.add(di + 1, r);
  return commit(l);
}""")
# Object[] { error or null, String[] member uuids, String[] their names, description before }
M(st, r"""
public static synchronized Object[] delete(String id) {
  java.util.ArrayList l = copyList();
  int at = idx(l, id);
  if (at < 0) return new Object[] { "-No rank called " + id + ".", new String[0], new String[0], "" };
  String before = describeR((@PKG@.Rank) l.get(at));
  l.remove(at);
  String e = commit(l);
  if (e != null) return new Object[] { e, new String[0], new String[0], before };
  java.util.ArrayList us = new java.util.ArrayList();
  java.util.ArrayList ns = new java.util.ArrayList();
  java.util.Iterator it = PLAYERS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    String[] v = (String[]) en.getValue();
    if (!v[0].equals(id)) continue;
    us.add(en.getKey());
    ns.add(v[1]);
    en.setValue(new String[] { "", v[1] });
  }
  if (us.size() > 0 && !PBROKEN) { String w = writePlayers(); if (w != null) @PKG@.RankCfg.warn("players.properties not saved after deleting " + id + " (members are shown as the default rank anyway): " + w); }
  rebuildChat();
  return new Object[] { null, (String[]) us.toArray(new String[0]), (String[]) ns.toArray(new String[0]), before };
}""")
# field: 0 name, 1 prefix, 2 colour, 3 staff ("true"/"false"); the value is already cleaned by the caller
M(st, r"""
public static synchronized String setField(String id, int field, String v) {
  java.util.ArrayList l = copyList();
  int at = idx(l, id);
  if (at < 0) return "-No rank called " + id + ".";
  @PKG@.Rank r = (@PKG@.Rank) l.get(at);
  if (field == 0) r.name = v;
  else if (field == 1) r.prefix = v;
  else if (field == 2) r.colour = v;
  else r.staff = "true".equals(v);
  return commit(l);
}""")
M(st, r"""
public static synchronized String move(String id, boolean up) {
  java.util.ArrayList l = copyList();
  int at = idx(l, id);
  if (at < 0) return "-No rank called " + id + ".";
  int to = up ? at + 1 : at - 1;
  if (to < 0 || to >= l.size()) return "=" + ((@PKG@.Rank) l.get(at)).name + " is already the " + (up ? "highest" : "lowest") + " rank.";
  String def = defaultId();
  if (id.equals(def) || ((@PKG@.Rank) l.get(to)).id.equals(def)) return "=The default rank " + label(def) + " always stays at the bottom of the ladder.";
  Object a = l.get(at);
  l.set(at, l.get(to));
  l.set(to, a);
  return commit(l);
}""")
# the default rank is the floor of the ladder (everyone without a rank; create() puts a new rank just above it). A hand edit or a new
# ranks.default can leave it higher: move it to the bottom. This changes no rank's permissions (effectiveIn skips the default rank, and
# the order of the other ranks stays the same). Returns the refusal, or null (moved or already there).
M(st, r"""
public static synchronized String floorDefault() {
  if (BROKEN) return null;
  String def = defaultId();
  int at = idx(RANKS, def);
  if (at <= 0) return null;
  java.util.ArrayList l = copyList();
  int i = idx(l, def);
  if (i <= 0) return null;
  Object d = l.remove(i);
  l.add(0, d);
  String e = commit(l);
  if (e != null) { @PKG@.RankCfg.warn("the default rank " + def + " is not at the bottom of the ladder and could not be moved there: " + @PKG@.RankCfg.textOf(e)); return e; }
  @PKG@.RankCfg.info("the default rank " + label(def) + " moved to the bottom of the ladder (it is everyone without a rank; no rank's permissions change)");
  return null;
}""")
M(st, r"""
public static synchronized String setGrant(String id, String node, boolean add) {
  java.util.ArrayList l = copyList();
  int at = idx(l, id);
  if (at < 0) return "-No rank called " + id + ".";
  @PKG@.Rank r = (@PKG@.Rank) l.get(at);
  if (add) { if (r.grants.size() >= 400) return "-400 grants per rank is the most this version keeps."; r.grants.add(node); }
  else r.grants.remove(node);
  return commit(l);
}""")
# ---- players (the membership list; the engine is the enforcement, see RankEngine)
M(st, r"""
public static synchronized String rankOf(String us) {
  String[] v = (String[]) PLAYERS.get(us);
  if (v == null || v[0].length() == 0) return "";
  if (find(v[0]) == null || v[0].equals(defaultId())) return "";
  return v[0];
}""")
M(st, r"""
public static String effectiveRank(String us) {
  String r = rankOf(us);
  return r.length() == 0 ? defaultId() : r;
}""")
M(st, r"""
public static synchronized String nameOf(String us, String dflt) {
  String[] v = (String[]) PLAYERS.get(us);
  return v == null ? dflt : v[1];
}""")
M(st, r"""
public static synchronized String setMember(String us, String name, String rid) {
  if (PBROKEN) return "-players.properties cannot be read (" + PWHY + ") - fix or delete it, then /rankadmin reload.";
  String[] old = (String[]) PLAYERS.get(us);
  String nm = name != null && name.length() > 0 ? clean(name, 32) : (old != null ? old[1] : us);
  PLAYERS.put(us, new String[] { rid == null ? "" : rid, nm });
  String e = writePlayers();
  if (e != null) {
    if (old == null) PLAYERS.remove(us); else PLAYERS.put(us, old);
    rebuildChat();
    return "-players.properties could not be saved (" + e + ")";
  }
  PDIRTY = false;
  rebuildChat();
  return null;
}""")
M(st, r"""
public static synchronized void flushPlayers() {
  PSCHED = false;
  if (!PDIRTY || PBROKEN) return;
  String e = writePlayers();
  if (e == null) { PDIRTY = false; return; }
  PSCHED = true;
  @PKG@.RankCfg.later(new @PKG@.RankSaveTask(), 30000L);
}""")
M(st, r"""
public static synchronized void seen(String us, String name) {
  if (us == null || name == null) return;
  String nm = clean(name, 32);
  if (nm.length() == 0) return;
  String[] old = (String[]) PLAYERS.get(us);
  if (old != null && old[1].equals(nm)) return;
  PLAYERS.put(us, new String[] { old == null ? "" : old[0], nm });
  PDIRTY = true;
  if (!PSCHED) { PSCHED = true; @PKG@.RankCfg.later(new @PKG@.RankSaveTask(), 5000L); }
}""")
M(st, r"""
public static synchronized int memberCount(String id) {
  int n = 0;
  java.util.Iterator it = PLAYERS.values().iterator();
  while (it.hasNext()) { String[] v = (String[]) it.next(); if (v[0].equals(id)) n++; }
  return n;
}""")
# members sorted by name (TreeMap on lower-case name + uuid: no Comparator class needed)
M(st, r"""
public static synchronized java.util.ArrayList membersOf(String id) {
  java.util.TreeMap m = new java.util.TreeMap();
  java.util.Iterator it = PLAYERS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String[] v = (String[]) e.getValue();
    if (v[0].equals(id)) m.put(v[1].toLowerCase() + "\t" + e.getKey(), new String[] { (String) e.getKey(), v[1] });
  }
  return new java.util.ArrayList(m.values());
}""")
M(st, r"""
public static synchronized String[] memberUuids() {
  java.util.ArrayList out = new java.util.ArrayList();
  String def = defaultId();
  java.util.Iterator it = PLAYERS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String[] v = (String[]) e.getValue();
    if (v[0].length() > 0 && !v[0].equals(def)) out.add(e.getKey());
  }
  return (String[]) out.toArray(new String[0]);
}""")
M(st, r"""
public static synchronized String[] findStored(String name) {
  java.util.Iterator it = PLAYERS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String[] v = (String[]) e.getValue();
    if (v[1].equalsIgnoreCase(name)) return new String[] { (String) e.getKey(), v[1] };
  }
  return null;
}""")
M(st, r"""
public static synchronized java.util.ArrayList searchStored(String filter, int max) {
  String f = filter == null ? "" : filter.trim().toLowerCase();
  java.util.TreeMap m = new java.util.TreeMap();
  java.util.Iterator it = PLAYERS.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String[] v = (String[]) e.getValue();
    if (f.length() > 0 && v[1].toLowerCase().indexOf(f) < 0) continue;
    m.put(v[1].toLowerCase() + "\t" + e.getKey(), new String[] { (String) e.getKey(), v[1] });
  }
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator mi = m.values().iterator();
  while (mi.hasNext() && out.size() < max) out.add(mi.next());
  return out;
}""")
# a player by UUID, online name or seen name -> String[] { uuid, name } or null
M(st, r"""
public static String[] findPlayer(String text) {
  if (text == null) return null;
  String t = text.trim();
  if (t.length() == 0) return null;
  if (t.length() >= 32 && t.indexOf('-') > 0) {
    try { java.util.UUID u = java.util.UUID.fromString(t); return new String[] { u.toString(), nameOf(u.toString(), u.toString()) }; } catch (Throwable x) { }
  }
  java.util.ArrayList on = @PKG@.RankCfg.online();
  for (int i = 0; i < on.size(); i++) { String[] p = (String[]) on.get(i); if (p[1] != null && p[1].equalsIgnoreCase(t)) return p; }
  return findStored(t);
}""")
# { id, name, prefix, colour, staff } of the rank a player shows as (the default rank without one)
M(st, r"""
public static String[] infoFor(String us) {
  String id = effectiveRank(us);
  @PKG@.Rank r = find(id);
  if (r == null) return new String[] { id, id, "", "", "false" };
  return new String[] { r.id, r.name, r.prefix, r.colour, r.staff ? "true" : "false" };
}""")
# rows for the Ranks view, highest first: { id, name, prefix, colour, staff, position, members, own, inherited, isDefault }
M(st, r"""
public static java.util.ArrayList rankRows() {
  java.util.ArrayList l = RANKS;
  String def = defaultId();
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.HashSet acc = new java.util.HashSet();
  for (int i = 0; i < l.size(); i++) {
    @PKG@.Rank r = (@PKG@.Rank) l.get(i);
    boolean isDef = r.id.equals(def);
    java.util.HashSet inh = new java.util.HashSet(acc);
    inh.removeAll(r.grants);
    out.add(0, new String[] { r.id, r.name, r.prefix, r.colour, r.staff ? "true" : "false", String.valueOf(i + 1),
      String.valueOf(isDef ? 0 : memberCount(r.id)), String.valueOf(r.grants.size()), String.valueOf(isDef ? 0 : inh.size()), isDef ? "1" : "" });
    if (!isDef) acc.addAll(r.grants);
  }
  return out;
}""")
M(st, r"""
public static Object[] ladder() {
  java.util.ArrayList l = RANKS;
  String[] ids = new String[l.size()];
  java.util.ArrayList g = new java.util.ArrayList();
  for (int i = 0; i < l.size(); i++) {
    @PKG@.Rank r = (@PKG@.Rank) l.get(i);
    ids[i] = r.id;
    g.add(r.grants.toArray(new String[0]));
  }
  return new Object[] { ids, g, defaultId() };
}""")
M(st, r"""
public static String[] chatOf(java.util.UUID u) {
  if (u == null) return null;
  Object o = CHAT.get(u.toString());
  if (o instanceof String[]) return (String[]) o;
  return DEFCHAT;
}""")
M(st, r"""
public static void publish(String us) {
  try {
    String[] r = infoFor(us);
    java.util.Map b = @PKG@.RankCfg.bridge();
    b.put("rank:" + us, r[1]);
    b.put("rank:id:" + us, r[0]);
    b.put("rank:prefix:" + us, r[2]);
    b.put("rank:colour:" + us, r[3]);
  } catch (Throwable t) { }
}""")
M(st, r"""
public static void publishAll() {
  try {
    String[] m = memberUuids();
    for (int i = 0; i < m.length; i++) publish(m[i]);
    java.util.ArrayList on = @PKG@.RankCfg.online();
    for (int i = 0; i < on.size(); i++) publish(((String[]) on.get(i))[0]);
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not publish ranks on the bridge: " + t); }
}""")
M(sav, r"""
public void run() {
  try { @PKG@.RankStore.flushPlayers(); } catch (Throwable t) { @PKG@.RankCfg.warn("players.properties save failed: " + t); }
}""")

# ================= RankEngine: every engine change (lock order: RankEngine.class, then RankStore.class inside it - never the reverse) =================
eng = mk("RankEngine")
for f in ("public static volatile boolean STARTED;", 'public static final String ADV = "hytale:Adventurer";',
          'public static final String ADMIN = "hytale:Admin";'):
    F(eng, f)
M(eng, r"""
public static String text(java.util.Set g) {
  if (g == null) return "(could not be read)";
  if (g.isEmpty()) return "(none)";
  return String.join(", ", new java.util.TreeSet(g));
}""")
M(eng, r"""
public static int skyyCount(java.util.Set g) {
  if (g == null) return 0;
  int n = 0;
  java.util.Iterator it = g.iterator();
  while (it.hasNext()) if (String.valueOf(it.next()).startsWith("skyy:")) n++;
  return n;
}""")
M(eng, r"""
public static boolean groupHas(String id, String node) {
  java.util.Set s = @PKG@.RankPerm.groupNodes("skyy:" + id);
  return s != null && s.contains(node);
}""")
M(eng, r"""
public static boolean isOp(java.util.UUID u) {
  java.util.Set g = @PKG@.RankPerm.groupsOf(u);
  return g != null && g.contains(ADMIN);
}""")
M(eng, r"""
public static synchronized int[] syncOne(String group, java.util.Set want0) {
  java.util.HashSet want = new java.util.HashSet(want0);
  java.util.Set have0 = @PKG@.RankPerm.groupNodes(group);
  if (have0 == null) return new int[] { 0, 0, 1 };
  java.util.HashSet have = new java.util.HashSet(have0);
  java.util.HashSet add = new java.util.HashSet(want);
  add.removeAll(have);
  java.util.HashSet rem = new java.util.HashSet(have);
  rem.removeAll(want);
  int bad = 0;
  if (!add.isEmpty() && !@PKG@.RankPerm.addGroupNodes(group, add)) bad = 1;
  if (!rem.isEmpty() && !@PKG@.RankPerm.removeGroupNodes(group, rem)) bad = 1;
  return new int[] { add.size(), rem.size(), bad };
}""")
# empties a group (the engine then deletes it: removeGroupPermissions drops a non-built-in group whose set is empty)
M(eng, r"""
public static synchronized boolean dropGroup(String id) {
  if (!@PKG@.RankStore.validId(id)) return false;
  java.util.Set have = @PKG@.RankPerm.groupNodes("skyy:" + id);
  if (have == null) return false;
  if (have.isEmpty()) return true;
  return @PKG@.RankPerm.removeGroupNodes("skyy:" + id, new java.util.HashSet(have));
}""")
M(eng, r"""
public static synchronized String syncGroups() {
  if (!@PKG@.RankPerm.ready()) return "the permission system is not loaded yet";
  if (@PKG@.RankStore.BROKEN) return "ranks.properties cannot be read - the groups are left as they are";
  Object[] lad = @PKG@.RankStore.ladder();
  String[] ids = (String[]) lad[0];
  java.util.ArrayList grants = (java.util.ArrayList) lad[1];
  String def = (String) lad[2];
  java.util.HashSet acc = new java.util.HashSet();
  java.util.HashSet known = new java.util.HashSet();
  int added = 0;
  int removed = 0;
  int groups = 0;
  int bad = 0;
  for (int i = 0; i < ids.length; i++) {
    known.add("skyy:" + ids[i]);
    if (ids[i].equals(def)) continue;
    acc.add("skyyranks.rank." + ids[i]);
    String[] g = (String[]) grants.get(i);
    for (int k = 0; k < g.length; k++) acc.add(g[k]);
    int[] d = syncOne("skyy:" + ids[i], acc);
    added += d[0];
    removed += d[1];
    bad += d[2];
    groups++;
  }
  java.util.Set dh = @PKG@.RankPerm.groupNodes("skyy:" + def);
  if (dh != null && !dh.isEmpty()) { int n = dh.size(); if (dropGroup(def)) removed += n; else bad++; }
  java.util.Iterator it = @PKG@.RankPerm.allGroups().iterator();
  while (it.hasNext()) {
    String g = String.valueOf(it.next());
    if (g.startsWith("skyy:") && !known.contains(g)) {
      java.util.Set n = @PKG@.RankPerm.groupNodes(g);
      String sfx = g.substring(5);
      String how = @PKG@.RankStore.validId(sfx) ? "Make a rank with the id " + sfx + " in /rankadmin to manage it, or remove it with /perm."
        : sfx + " cannot be a SkyyRanks rank id (a-z and 0-9, 2-16 characters, starting with a letter; group names are case-sensitive) - move its players to a rank and remove it with /perm.";
      if (n != null && !n.isEmpty()) @PKG@.RankCfg.warnOnce("unknown:" + g, "permissions.json has the group " + g + ", which is not a SkyyRanks rank - it is left as it is. " + how);
    }
  }
  return groups + (groups == 1 ? " rank group" : " rank groups") + " in sync (" + added + " nodes added, " + removed + " removed" + (bad > 0 ? ", " + bad + " engine calls FAILED - see the log" : "") + ")";
}""")
# THE ADVENTURER GUARD (spec 5.1 / 8.4.5). rid null = the default rank (no skyy group). Returns { Boolean adventurerKept, Boolean rankOk, groups text }.
M(eng, r"""
public static synchronized Object[] assign(java.util.UUID u, String rid) {
  String target = rid == null ? null : "skyy:" + rid;
  @PKG@.RankPerm.addToGroup(u, ADV);
  if (target != null) @PKG@.RankPerm.addToGroup(u, target);
  java.util.Set g = @PKG@.RankPerm.groupsOf(u);
  if (g != null) {
    Object[] arr = g.toArray();
    for (int i = 0; i < arr.length; i++) {
      String s = String.valueOf(arr[i]);
      if (s.startsWith("skyy:") && (target == null || !s.equals(target))) @PKG@.RankPerm.removeFromGroup(u, s);
    }
  }
  @PKG@.RankPerm.addToGroup(u, ADV);
  java.util.Set after = @PKG@.RankPerm.groupsOf(u);
  boolean adv = after != null && after.contains(ADV);
  if (!adv && after != null) {
    @PKG@.RankPerm.addToGroup(u, ADV);
    after = @PKG@.RankPerm.groupsOf(u);
    adv = after != null && after.contains(ADV);
  }
  int sk = skyyCount(after);
  boolean ok = after != null && (target == null ? sk == 0 : (after.contains(target) && sk == 1));
  if (!adv) @PKG@.RankCfg.severe("could NOT keep hytale:Adventurer for " + u + " - groups now " + text(after) + " - their normal commands may be gone; add it with /perm or permissions.json");
  return new Object[] { Boolean.valueOf(adv), Boolean.valueOf(ok), text(after) };
}""")
M(eng, r"""
public static synchronized Object[] assignAndStore(java.util.UUID u, String name, String rid) {
  Object[] r = assign(u, rid);
  String err = null;
  if (Boolean.TRUE.equals(r[1])) err = @PKG@.RankStore.setMember(u.toString(), name, rid == null ? "" : rid);
  return new Object[] { r[0], r[1], r[2], err };
}""")
# a former member of a deleted rank: Adventurer explicitly first, then the dangling group out, then verify Adventurer
M(eng, r"""
public static synchronized boolean clearGroup(java.util.UUID u, String group) {
  @PKG@.RankPerm.addToGroup(u, ADV);
  @PKG@.RankPerm.removeFromGroup(u, group);
  @PKG@.RankPerm.addToGroup(u, ADV);
  java.util.Set after = @PKG@.RankPerm.groupsOf(u);
  boolean adv = after != null && after.contains(ADV);
  if (!adv) @PKG@.RankCfg.severe("could NOT keep hytale:Adventurer for " + u + " while removing " + group + " - groups now " + text(after));
  return adv;
}""")
# the highest known non-default rank among a player's engine groups ("" = none)
M(eng, r"""
public static String bestRank(java.util.Set g) {
  if (g == null) return "";
  String def = @PKG@.RankStore.defaultId();
  String best = "";
  int bp = -1;
  java.util.Iterator it = g.iterator();
  while (it.hasNext()) {
    String s = String.valueOf(it.next());
    if (!s.startsWith("skyy:")) continue;
    String id = s.substring(5);
    if (id.equals(def)) continue;
    int p = @PKG@.RankStore.position(id);
    if (p > bp) { bp = p; best = id; }
  }
  return best;
}""")
# start and /rankadmin sync: the stored member list follows the engine (vanilla /perm or a restored permissions.json win); engine read-only
M(eng, r"""
public static synchronized int reconcileStored() {
  if (@PKG@.RankStore.BROKEN || @PKG@.RankStore.PBROKEN) return 0;
  String[] us = @PKG@.RankStore.memberUuids();
  int changed = 0;
  for (int i = 0; i < us.length; i++) {
    java.util.UUID u = null;
    try { u = java.util.UUID.fromString(us[i]); } catch (Throwable t) { continue; }
    java.util.Set g = @PKG@.RankPerm.groupsOf(u);
    if (g == null) continue;
    String stored = @PKG@.RankStore.rankOf(us[i]);
    String found = bestRank(g);
    if (found.equals(stored)) continue;
    String nm = @PKG@.RankStore.nameOf(us[i], us[i]);
    if (@PKG@.RankStore.setMember(us[i], null, found) == null) {
      changed++;
      @PKG@.RankStore.log(null, "engine", "file", "member[" + nm + "]", stored, found.length() == 0 ? @PKG@.RankStore.defaultId() : found);
    }
  }
  return changed;
}""")
# first PlayerReady of a session (scheduler thread): the invariants for players in SkyyRanks ranks, and the stored list follows the engine
M(eng, r"""
public static synchronized String onJoin(java.util.UUID u, String name) {
  String us = u.toString();
  @PKG@.RankStore.seen(us, name);
  if (@PKG@.RankStore.BROKEN || !@PKG@.RankPerm.ready()) return "skipped";
  java.util.Set g0 = @PKG@.RankPerm.groupsOf(u);
  if (g0 == null) return "groups unreadable";
  String def = @PKG@.RankStore.defaultId();
  String keep = bestRank(g0);
  int fixed = 0;
  Object[] arr = g0.toArray();
  for (int i = 0; i < arr.length; i++) {
    String s = String.valueOf(arr[i]);
    if (!s.startsWith("skyy:")) continue;
    String id = s.substring(5);
    boolean drop = false;
    if (@PKG@.RankStore.isRank(id)) drop = id.equals(def) || !id.equals(keep);
    else { java.util.Set n = @PKG@.RankPerm.groupNodes(s); drop = n != null && n.isEmpty(); }
    if (drop) {
      if (fixed == 0) @PKG@.RankPerm.addToGroup(u, ADV);
      if (@PKG@.RankPerm.removeFromGroup(u, s)) { fixed++; @PKG@.RankCfg.info("join clean-up: removed " + name + " from " + s + " (a player has at most one rank group; the default rank and deleted ranks have none)"); }
    }
  }
  if (keep.length() > 0 || fixed > 0) {
    java.util.Set g1 = @PKG@.RankPerm.groupsOf(u);
    if (g1 != null && !g1.contains(ADV)) {
      @PKG@.RankPerm.addToGroup(u, ADV);
      java.util.Set g2 = @PKG@.RankPerm.groupsOf(u);
      if (g2 != null && g2.contains(ADV)) @PKG@.RankCfg.warn("join: " + name + " was in " + keep + " without hytale:Adventurer - added it back (their normal commands work again)");
      else @PKG@.RankCfg.severe("join: " + name + " is in " + keep + " without hytale:Adventurer and it could not be added - groups " + text(g2));
    }
  }
  if (!@PKG@.RankStore.PBROKEN) {
    String stored = @PKG@.RankStore.rankOf(us);
    if (!keep.equals(stored) && @PKG@.RankStore.setMember(us, name, keep) == null)
      @PKG@.RankStore.log(null, "engine", "file", "member[" + name + "]", stored.length() == 0 ? def : stored, keep.length() == 0 ? def : keep);
  }
  @PKG@.RankStore.publish(us);
  return "ok";
}""")
M(eng, r"""
public static synchronized boolean deny(java.util.UUID u, String node) {
  @PKG@.RankPerm.addUserNode(u, "-" + node);
  java.util.Set n = @PKG@.RankPerm.userNodes(u);
  return n != null && n.contains("-" + node);
}""")
M(eng, r"""
public static synchronized boolean undeny(java.util.UUID u, String node) {
  @PKG@.RankPerm.removeUserNode(u, "-" + node);
  java.util.Set n = @PKG@.RankPerm.userNodes(u);
  return n != null && !n.contains("-" + node);
}""")
M(eng, r"""
public static String[] userList(java.util.UUID u, boolean denies) {
  java.util.Set n = @PKG@.RankPerm.userNodes(u);
  java.util.TreeSet out = new java.util.TreeSet();
  if (n != null) {
    java.util.Iterator it = n.iterator();
    while (it.hasNext()) {
      String s = String.valueOf(it.next());
      if (denies && s.startsWith("-")) out.add(s.substring(1));
      if (!denies && !s.startsWith("-")) out.add(s);
    }
  }
  return (String[]) out.toArray(new String[0]);
}""")
M(eng, r"""
public static synchronized String start() {
  String s = syncGroups();
  int c = reconcileStored();
  STARTED = true;
  @PKG@.RankStore.publishAll();
  return "ranks synced with the permission system: " + s + (c > 0 ? "; " + c + " stored members updated from permissions.json" : "");
}""")

# ================= RankBulkTask: the members of a deleted rank leave its (now empty) group on the scheduler =================
bulk = mk("RankBulkTask", ifaces=("java.lang.Runnable",))
for f in ("public String[] us;", "public String group;", "public java.util.UUID admin;", "public String label;"):
    F(bulk, f)
C(bulk, "public RankBulkTask(String[] us, String group, java.util.UUID admin, String label) { this.us = us; this.group = group; this.admin = admin; this.label = label; }")
M(bulk, r"""
public void run() {
  int ok = 0;
  int bad = 0;
  for (int i = 0; i < this.us.length; i++) {
    try {
      if (@PKG@.RankEngine.clearGroup(java.util.UUID.fromString(this.us[i]), this.group)) ok++; else bad++;
    } catch (Throwable t) { bad++; }
    try { @PKG@.RankStore.publish(this.us[i]); } catch (Throwable t) { }
  }
  String m = (bad == 0 ? "+" : "-") + ok + " former member" + (ok == 1 ? "" : "s") + " of " + this.label + " cleaned up" + (bad == 0 ? " - hytale:Adventurer kept for all." : ", " + bad + " FAILED (see the server log).");
  @PKG@.RankCfg.info(@PKG@.RankCfg.textOf(m));
  @PKG@.RankCfg.tell(this.admin, m);
}""")

# ================= RankHooks: the config kit's check / after / reload hooks =================
hk = mk("RankHooks")
M(hk, r"""
public static String checkDefault(String key, String value) {
  String v = value == null ? "" : value.trim();
  if (!@PKG@.RankStore.isRank(v)) {
    String id = @PKG@.RankStore.resolveRank(v);
    if (id != null) return "Type the rank id " + id + " (lower case), not the display name.";
    return "No rank with the id " + v + ". Ranks: " + @PKG@.RankStore.idList() + ".";
  }
  if (@PKG@.RankStore.grantCount(v) > 0) return @PKG@.RankStore.label(v) + " has grants - the default rank holds none (it is everyone without a rank). Remove them first.";
  int m = @PKG@.RankStore.memberCount(v);
  if (m > 0) return @PKG@.RankStore.label(v) + " has " + m + (m == 1 ? " member" : " members") + " - give them another rank first. The default rank has no members.";
  return null;
}""")
M(hk, r"""
public static void afterDefault(String key) {
  try {
    @PKG@.RankStore.floorDefault();
    @PKG@.RankStore.rebuildChatSafe();
    if (@PKG@.RankEngine.STARTED) @PKG@.RankCfg.info("default rank is now " + @PKG@.RankStore.defaultId() + ": " + @PKG@.RankEngine.syncGroups());
    @PKG@.RankStore.publishAll();
  } catch (Throwable t) { @PKG@.RankCfg.warn("default rank change follow-up failed: " + t); }
}""")
M(hk, r"""
public static String checkPriority(String key, String value) {
  int p = @PKG@.RankCfg.intOf(value, 31000);
  if (p <= 30000) return "?At " + p + " the rank prefix may be added before SkyyExploration's title (priority 30000), so chat could read [Title] [Rank] Name. Use " + p + " anyway?";
  return null;
}""")
# a hand-edited ranks.default that breaks the rule is used anyway (never refuse a start), but said once per load
M(hk, r"""
public static void warnDefault() {
  try {
    String d = @PKG@.RankStore.defaultId();
    if (!d.equals(@PKG@.RankCfg.DEFAULT_RANK)) @PKG@.RankCfg.warn("config.properties: ranks.default=" + @PKG@.RankCfg.DEFAULT_RANK + " is not a rank - " + d + " (the lowest rank) is the default instead");
    String why = checkDefault("ranks.default", d);
    if (why != null) @PKG@.RankCfg.warn("the default rank " + d + ": " + why + " It stays the default: its members show as the default rank and its grants go to nobody.");
  } catch (Throwable t) { }
}""")
M(hk, r"""
public static void reloadCfg() {
  try {
    @PKG@.RankCfg.loadCfg(false);
    @PKG@.RankStore.floorDefault();
    warnDefault();
    @PKG@.RankStore.rebuildChatSafe();
    if (@PKG@.RankEngine.STARTED) @PKG@.RankEngine.syncGroups();
    @PKG@.RankStore.publishAll();
  } catch (Throwable t) { @PKG@.RankCfg.warn("config reload failed: " + t); }
}""")

# ================= RankOps: every rank operation (commands and the page call these; replies start with + ok, - refused, = info, ? confirm) =================
ops = mk("RankOps")
F(ops, "public static final java.util.concurrent.ConcurrentHashMap CONFIRMS = new java.util.concurrent.ConcurrentHashMap();")
M(ops, r"""
public static String gate(boolean engine) {
  if (@PKG@.RankStore.BROKEN) return "-ranks.properties cannot be read (" + @PKG@.RankStore.WHY + ") - fix or delete it, then use /rankadmin reload. Nothing was changed.";
  if (engine && !@PKG@.RankEngine.STARTED) return "-The permission system is still loading - try again in a few seconds.";
  return null;
}""")
M(ops, r"""
public static String noRank(String t) {
  return "-No rank called " + t + ". Ranks: " + @PKG@.RankStore.idList() + ".";
}""")
M(ops, r"""
public static String noPlayer(String t) {
  return "-No player called " + t + " has been seen on this server. Use their exact name (online or seen before) or their UUID.";
}""")
# chat confirm: the same command again within 10 s
M(ops, r"""
public static boolean repeat(java.util.UUID u, String key) {
  if (u == null || key == null) return false;
  Object v = CONFIRMS.get(u);
  if (!(v instanceof String[])) return false;
  String[] a = (String[]) v;
  if (!a[0].equals(key)) return false;
  CONFIRMS.remove(u);
  long until = 0L;
  try { until = Long.parseLong(a[1]); } catch (Throwable t) { }
  return System.currentTimeMillis() <= until;
}""")
M(ops, r"""
public static void reply(@PR@ pr, String key, String r) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (r != null && r.startsWith("?")) {
    CONFIRMS.put(u, new String[] { key, String.valueOf(System.currentTimeMillis() + 10000L) });
    @PKG@.RankCfg.tellPr(pr, r + " Type the same command again within 10 seconds to confirm.");
    return;
  }
  CONFIRMS.remove(u);
  @PKG@.RankCfg.tellPr(pr, r == null ? "+Done." : r);
}""")
M(ops, r"""
public static String create(java.util.UUID who, String wn, String via, String id, String name) {
  String g = gate(true);
  if (g != null) return g;
  String e = @PKG@.RankStore.create(id, name);
  if (e != null) return e;
  String nid = id.trim().toLowerCase();
  @PKG@.RankStore.log(who, wn, via, "rank[" + nid + "]", "(none)", @PKG@.RankStore.describe(nid));
  String s = @PKG@.RankEngine.syncGroups();
  boolean ok = @PKG@.RankEngine.groupHas(nid, "skyyranks.rank." + nid);
  return "+Rank " + @PKG@.RankStore.label(nid) + " (" + nid + ") created just above " + @PKG@.RankStore.label(@PKG@.RankStore.defaultId()) + (ok ? " - group skyy:" + nid + " is ready." : " - but its engine group could not be made yet (" + s + ").");
}""")
M(ops, r"""
public static String delete(java.util.UUID who, String wn, String via, String text, boolean conf) {
  String g = gate(true);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  String lab = @PKG@.RankStore.label(rid);
  String def = @PKG@.RankStore.defaultId();
  if (rid.equals(def)) return "-" + lab + " is the default rank and cannot be deleted. Make another rank the default first.";
  int n = @PKG@.RankStore.memberCount(rid);
  boolean mine = who != null && rid.equals(@PKG@.RankStore.rankOf(who.toString())) && !@PKG@.RankEngine.isOp(who);
  if (!conf) return "?Delete the rank " + lab + "? " + (n == 0 ? "It has no members." : "Its " + n + (n == 1 ? " member goes" : " members go") + " back to " + @PKG@.RankStore.label(def) + " and lose" + (n == 1 ? "s" : "") + " its grants.") + (mine ? " You are in this rank yourself." : "");
  Object[] r = @PKG@.RankStore.delete(rid);
  if (r[0] != null) return (String) r[0];
  String[] us = (String[]) r[1];
  String[] ns = (String[]) r[2];
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "]", (String) r[3], "(none)");
  for (int i = 0; i < ns.length; i++) @PKG@.RankStore.log(who, wn, via, "member[" + ns[i] + "]", rid, def);
  boolean dropped = @PKG@.RankEngine.dropGroup(rid);
  @PKG@.RankEngine.syncGroups();
  @PKG@.RankStore.publishAll();
  if (us.length > 0) @PKG@.RankCfg.later(new @PKG@.RankBulkTask(us, "skyy:" + rid, who, lab), 50L);
  return (dropped ? "+" : "-") + "Rank " + lab + " deleted" + (dropped ? "" : " but its engine group could NOT be emptied (see the log)") + "." + (us.length > 0 ? " " + us.length + (us.length == 1 ? " member is" : " members are") + " back to " + @PKG@.RankStore.label(def) + " (groups cleaned up in the background)." : "");
}""")
M(ops, r"""
public static String rename(java.util.UUID who, String wn, String via, String text, String name0) {
  String g = gate(false);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  String name = @PKG@.RankStore.clean(name0, 24);
  if (name.length() == 0) return "-A display name needs 1-24 characters.";
  String old = @PKG@.RankStore.label(rid);
  if (old.equals(name)) return "=" + old + " is already called that.";
  String e = @PKG@.RankStore.setField(rid, 0, name);
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].name", old, name);
  @PKG@.RankStore.publishAll();
  return "+Rank " + rid + " is now called " + name + ".";
}""")
M(ops, r"""
public static String prefix(java.util.UUID who, String wn, String via, String text, String p0) {
  String g = gate(false);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  String p = @PKG@.RankStore.clean(p0, 32);
  if (p.equalsIgnoreCase("none") || p.equalsIgnoreCase("clear")) p = "";
  @PKG@.Rank r = @PKG@.RankStore.find(rid);
  if (r.prefix.equals(p)) return "=" + r.name + " already has " + (p.length() == 0 ? "no prefix." : "the prefix " + p + ".");
  String e = @PKG@.RankStore.setField(rid, 1, p);
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].prefix", r.prefix, p);
  @PKG@.RankStore.publishAll();
  return p.length() == 0 ? "+" + r.name + " has no chat prefix now." : "+" + r.name + " chat prefix: " + p + " (chat reads " + p + " [Title] Name).";
}""")
M(ops, r"""
public static String colour(java.util.UUID who, String wn, String via, String text, String c0) {
  String g = gate(false);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  String c = @PKG@.RankStore.normColour(c0);
  if (c == null) return "-" + c0 + " is not a colour. Use #rrggbb (like #ff5555), a word (red, gold, yellow, green, aqua, blue, purple, pink, white, gray) or none.";
  @PKG@.Rank r = @PKG@.RankStore.find(rid);
  if (r.colour.equals(c)) return "=" + r.name + " already uses " + (c.length() == 0 ? "no colour." : c + ".");
  String e = @PKG@.RankStore.setField(rid, 2, c);
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].colour", r.colour, c);
  @PKG@.RankStore.publishAll();
  return "+" + r.name + " prefix colour: " + (c.length() == 0 ? "plain." : c + ".");
}""")
M(ops, r"""
public static String staff(java.util.UUID who, String wn, String via, String text, boolean on) {
  String g = gate(false);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  @PKG@.Rank r = @PKG@.RankStore.find(rid);
  if (r.staff == on) return "=" + r.name + " is already " + (on ? "a staff rank." : "not a staff rank.");
  String e = @PKG@.RankStore.setField(rid, 3, on ? "true" : "false");
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].staff", r.staff ? "true" : "false", on ? "true" : "false");
  @PKG@.RankStore.publishAll();
  return "+" + r.name + (on ? " is a staff rank now (other mods see it in rank:fn:of; denies on its members ask first)." : " is no longer a staff rank.");
}""")
# editor access (skyyranks.admin) in a rank's node set, decided exactly as the engine does (RankPerm.grants)
M(ops, r"""
public static boolean adminIn(java.util.Set s) {
  return @PKG@.RankPerm.grants(s, "skyyranks.admin");
}""")
# the ranks (ids) that give skyyranks.admin in ladder a but no longer in ladder b (b = a after a grant removal or a move)
M(ops, r"""
public static java.util.ArrayList adminLost(java.util.ArrayList a, java.util.ArrayList b) {
  java.util.ArrayList out = new java.util.ArrayList();
  String def = @PKG@.RankStore.defaultId();
  for (int i = 0; i < b.size(); i++) {
    String id = ((@PKG@.Rank) b.get(i)).id;
    if (id.equals(def) || @PKG@.RankStore.idx(a, id) < 0) continue;
    if (adminIn(@PKG@.RankStore.effectiveIn(a, id)) && !adminIn(@PKG@.RankStore.effectiveIn(b, id))) out.add(id);
  }
  return out;
}""")
# the confirm text for who loses the editor ("" = nobody): the acting admin first (not an op: ops keep it through *), then the others
M(ops, r"""
public static String lossText(java.util.UUID who, java.util.ArrayList lost) {
  if (lost == null || lost.isEmpty()) return "";
  String mine = "";
  if (who != null && !@PKG@.RankEngine.isOp(who)) mine = @PKG@.RankStore.rankOf(who.toString());
  boolean self = mine.length() > 0 && lost.contains(mine);
  int n = 0;
  StringBuilder names = new StringBuilder();
  for (int i = 0; i < lost.size(); i++) {
    String id = (String) lost.get(i);
    n += @PKG@.RankStore.memberCount(id);
    if (i < 3) { if (names.length() > 0) names.append(", "); names.append(@PKG@.RankStore.label(id)); }
  }
  if (lost.size() > 3) names.append(" and ").append(lost.size() - 3).append(" more");
  if (self) n--;
  StringBuilder b = new StringBuilder();
  if (self) b.append(" You are in ").append(@PKG@.RankStore.label(mine)).append(" and would lose skyyranks.admin: this can lock you out of this editor.");
  if (n > 0) b.append(" ").append(n).append(self ? " other" : "").append(n == 1 ? " player" : " players").append(" in ").append(names.toString()).append(n == 1 ? " loses" : " lose").append(" skyyranks.admin (this editor; ops keep it).");
  return b.toString();
}""")
# nodes a rank starts to get / loses from a move, reported when they are dangerous
M(ops, r"""
public static String dangerList(java.util.Set s) {
  StringBuilder b = new StringBuilder();
  int n = 0;
  java.util.Iterator it = s.iterator();
  while (it.hasNext()) {
    String x = String.valueOf(it.next());
    if (!@PKG@.RankStore.dangerous(x)) continue;
    if (n < 4) { if (b.length() > 0) b.append(", "); b.append(x); }
    n++;
  }
  if (n > 4) b.append(" and ").append(n - 4).append(" more");
  return b.toString();
}""")
M(ops, r"""
public static String move(java.util.UUID who, String wn, String via, String text, boolean up, boolean conf) {
  String g = gate(true);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  java.util.ArrayList l = @PKG@.RankStore.RANKS;
  int at = @PKG@.RankStore.idx(l, rid);
  int to = up ? at + 1 : at - 1;
  String lab = @PKG@.RankStore.label(rid);
  String def = @PKG@.RankStore.defaultId();
  if (rid.equals(def)) return "=" + lab + " is the default rank: it always stays at the bottom of the ladder (it is everyone without a rank).";
  if (at < 0 || to < 0 || to >= l.size()) return "=" + lab + " is already the " + (up ? "highest" : "lowest") + " rank.";
  @PKG@.Rank other = (@PKG@.Rank) l.get(to);
  if (other.id.equals(def)) return "=" + lab + " is already the lowest rank above the default rank " + other.name + ", which always stays at the bottom.";
  if (!conf) {
    java.util.TreeSet before = @PKG@.RankStore.effectiveIn(l, up ? rid : other.id);
    java.util.ArrayList l2 = new java.util.ArrayList(l);
    l2.set(at, other);
    l2.set(to, l.get(at));
    java.util.TreeSet after = @PKG@.RankStore.effectiveIn(l2, up ? rid : other.id);
    after.removeAll(before);
    String d = dangerList(after);
    String loss = lossText(who, adminLost(l, l2));
    if (d.length() > 0 || loss.length() > 0) return "?Move " + lab + " " + (up ? "above " : "below ") + other.name + "?" + (d.length() > 0 ? " " + (up ? lab : other.name) + " (and every rank above it) then also gets " + d + "." : "") + loss;
  }
  String e = @PKG@.RankStore.move(rid, up);
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].position", String.valueOf(at + 1), String.valueOf(to + 1));
  String s = @PKG@.RankEngine.syncGroups();
  boolean bad = s.indexOf("FAILED") >= 0 || s.indexOf(" in sync") < 0;
  return (bad ? "-" : "+") + lab + " is now " + (up ? "above " : "below ") + other.name + " (position " + (to + 1) + " of " + l.size() + ")" + (bad ? " - engine: " + s : "") + ".";
}""")
M(ops, r"""
public static String grant(java.util.UUID who, String wn, String via, String text, String node0, boolean conf) {
  String g = gate(true);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  String lab = @PKG@.RankStore.label(rid);
  if (rid.equals(@PKG@.RankStore.defaultId())) return "-" + lab + " is the default rank: it holds no grants (it is everyone without a rank). Grant it to a rank, or change the owning mod's settings.";
  String node = node0 == null ? "" : node0.trim();
  if (node.startsWith("-")) return "-Grants only: a rank cannot deny. To take a permission from one player use a personal deny (Players tab or /rank deny).";
  if (!@PKG@.RankStore.validNode(node)) return "-" + node + " is not a valid permission node (letters, digits, - and _, parts joined by dots, * as a wildcard).";
  @PKG@.Rank r = @PKG@.RankStore.find(rid);
  if (r.grants.contains(node)) return "=" + lab + " already has " + node + ".";
  int above = @PKG@.RankStore.RANKS.size() - 1 - @PKG@.RankStore.position(rid);
  if (!conf && @PKG@.RankStore.dangerous(node)) return "?Grant " + node + " to " + lab + "? " + @PKG@.RankStore.dangerText(node) + (above > 0 ? " The " + above + (above == 1 ? " rank" : " ranks") + " above it get it too." : "");
  String e = @PKG@.RankStore.setGrant(rid, node, true);
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].grant[" + node + "]", "(none)", "granted");
  String s = @PKG@.RankEngine.syncGroups();
  boolean ok = @PKG@.RankEngine.groupHas(rid, node);
  return (ok ? "+" : "-") + lab + (ok ? " now has " : " should have ") + node + (above > 0 ? " (and the " + above + (above == 1 ? " rank" : " ranks") + " above it)" : "") + (ok ? "." : " but the engine group does not show it yet: " + s + ".");
}""")
M(ops, r"""
public static String ungrant(java.util.UUID who, String wn, String via, String text, String node0, boolean conf) {
  String g = gate(true);
  if (g != null) return g;
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  String lab = @PKG@.RankStore.label(rid);
  String node = node0 == null ? "" : node0.trim();
  @PKG@.Rank r = @PKG@.RankStore.find(rid);
  if (!r.grants.contains(node)) {
    java.util.ArrayList inh = @PKG@.RankStore.inherited(rid);
    for (int i = 0; i < inh.size(); i++) { String[] x = (String[]) inh.get(i); if (x[0].equals(node)) return "=" + node + " comes from " + x[1] + " (a lower rank) - remove it there."; }
    return "=" + lab + " does not have " + node + ".";
  }
  if (!conf) {
    java.util.ArrayList l = @PKG@.RankStore.RANKS;
    java.util.ArrayList l2 = new java.util.ArrayList();
    for (int i = 0; i < l.size(); i++) l2.add(((@PKG@.Rank) l.get(i)).copy());
    int at2 = @PKG@.RankStore.idx(l2, rid);
    if (at2 >= 0) ((@PKG@.Rank) l2.get(at2)).grants.remove(node);
    String loss = lossText(who, adminLost(l, l2));
    if (loss.length() > 0) return "?Remove " + node + " from " + lab + " (and every rank above it that gets it from there)?" + loss;
  }
  String e = @PKG@.RankStore.setGrant(rid, node, false);
  if (e != null) return e;
  @PKG@.RankStore.log(who, wn, via, "rank[" + rid + "].grant[" + node + "]", "granted", "(none)");
  String s = @PKG@.RankEngine.syncGroups();
  boolean bad = s.indexOf("FAILED") >= 0 || s.indexOf(" in sync") < 0;
  return (bad ? "-" : "+") + lab + " no longer has " + node + (bad ? " - engine: " + s : "") + ".";
}""")
# a real rank change asks ONE question when needed: what the new rank gives (staff flag, admin nodes) and what the player loses (a
# staff rank, the editor; for yourself the self-lockout). Ops keep the editor through hytale:Admin's *, so their loss is not asked about.
M(ops, r"""
public static String setRank(java.util.UUID who, String wn, String via, String ptext, String rtext, boolean conf) {
  String g = gate(true);
  if (g != null) return g;
  if (@PKG@.RankStore.PBROKEN) return "-players.properties cannot be read (" + @PKG@.RankStore.PWHY + ") - fix or delete it, then /rankadmin reload. Nothing was changed.";
  String[] p = @PKG@.RankStore.findPlayer(ptext);
  if (p == null) return noPlayer(ptext);
  String rid = @PKG@.RankStore.resolveRank(rtext);
  if (rid == null) return noRank(rtext);
  String def = @PKG@.RankStore.defaultId();
  boolean toDef = rid.equals(def);
  java.util.UUID u = java.util.UUID.fromString(p[0]);
  String cur = @PKG@.RankStore.rankOf(p[0]);
  String lab = @PKG@.RankStore.label(rid);
  if (!conf && !cur.equals(toDef ? "" : rid)) {
    boolean self = who != null && u.equals(who);
    java.util.TreeSet next = toDef ? new java.util.TreeSet() : @PKG@.RankStore.effective(rid);
    @PKG@.Rank r = toDef ? null : @PKG@.RankStore.find(rid);
    @PKG@.Rank old = cur.length() == 0 ? null : @PKG@.RankStore.find(cur);
    StringBuilder q = new StringBuilder();
    if (r != null) {
      String d = dangerList(next);
      if (r.staff) q.append(" It is a staff rank.");
      if (d.length() > 0) q.append(" It carries ").append(d).append(".");
    }
    if (old != null) {
      if (!self && old.staff && (r == null || !r.staff)) q.append(" ").append(p[1]).append(" leaves the staff rank ").append(old.name).append(".");
      if (adminIn(@PKG@.RankStore.effective(cur)) && !adminIn(next) && !@PKG@.RankEngine.isOp(u))
        q.append(self ? " You would lose skyyranks.admin (this editor) and could not change it back yourself." : " " + p[1] + " loses skyyranks.admin (this editor).");
    }
    if (q.length() > 0) return "?" + (self ? "Change your own rank to " + lab + "?" : (toDef ? "Take the rank " + @PKG@.RankStore.label(cur) + " from " + p[1] + "?" : "Give " + p[1] + " the rank " + lab + "?")) + q.toString();
  }
  Object[] r = @PKG@.RankEngine.assignAndStore(u, p[1], toDef ? null : rid);
  boolean adv = Boolean.TRUE.equals(r[0]);
  boolean ok = Boolean.TRUE.equals(r[1]);
  String groups = (String) r[2];
  String err = (String) r[3];
  if (ok && !cur.equals(toDef ? "" : rid)) @PKG@.RankStore.log(who, wn, via, "member[" + p[1] + "]", cur.length() == 0 ? def : cur, rid);
  @PKG@.RankStore.publish(p[0]);
  if (ok && !cur.equals(toDef ? "" : rid)) @PKG@.RankCfg.tell(u, toDef ? "=Your rank is now " + lab + "." : "+Your rank is now " + lab + ".");
  if (!adv) return "-" + p[1] + ": hytale:Adventurer could NOT be kept - their normal commands may be gone. Groups: " + groups + ". See the server log.";
  if (!ok) return "-" + p[1] + "'s groups did not end up as expected. Groups: " + groups + ".";
  if (err != null) return "-" + p[1] + " is " + lab + " in the permission system, but " + @PKG@.RankCfg.textOf(err) + ". Groups: " + groups + ".";
  if (cur.equals(toDef ? "" : rid)) return "=" + p[1] + " is already " + lab + ". Groups checked: " + groups + " - hytale:Adventurer kept.";
  return "+" + p[1] + " is now " + lab + ". Groups: " + groups + " - hytale:Adventurer kept.";
}""")
M(ops, r"""
public static String deny(java.util.UUID who, String wn, String via, String ptext, String node0, boolean conf) {
  String g = gate(true);
  if (g != null) return g;
  String[] p = @PKG@.RankStore.findPlayer(ptext);
  if (p == null) return noPlayer(ptext);
  String node = node0 == null ? "" : node0.trim();
  if (node.startsWith("-")) node = node.substring(1);
  if (node.equals("*")) return "-A deny of * blocks every command. Use /kick or /ban instead.";
  if (!@PKG@.RankStore.validNode(node)) return "-" + node + " is not a valid permission node.";
  java.util.UUID u = java.util.UUID.fromString(p[0]);
  java.util.HashSet one = new java.util.HashSet();
  one.add(node);
  if (who != null && u.equals(who) && adminIn(one)) return "-You cannot take skyyranks.admin away from yourself (" + node + " covers it).";
  String[] have = @PKG@.RankEngine.userList(u, true);
  for (int i = 0; i < have.length; i++) if (have[i].equals(node)) return "=" + p[1] + " already has a deny on " + node + ".";
  if (!conf) {
    boolean op = @PKG@.RankEngine.isOp(u);
    @PKG@.Rank r = @PKG@.RankStore.find(@PKG@.RankStore.effectiveRank(p[0]));
    boolean staff = r != null && r.staff;
    if (op || staff) return "?Deny " + node + " for " + p[1] + "? They are " + (op ? "an op" : "staff (" + r.name + ")") + " - a personal deny beats their op and rank permissions.";
  }
  boolean ok = @PKG@.RankEngine.deny(u, node);
  if (ok) @PKG@.RankStore.log(who, wn, via, "deny[" + p[1] + "]", "(none)", "-" + node);
  return ok ? "+" + p[1] + " can no longer use " + node + " (a personal deny, checked before any rank or op)." : "-The deny on " + node + " for " + p[1] + " did not show up in the permission system - see the server log.";
}""")
M(ops, r"""
public static String undeny(java.util.UUID who, String wn, String via, String ptext, String node0) {
  String g = gate(true);
  if (g != null) return g;
  String[] p = @PKG@.RankStore.findPlayer(ptext);
  if (p == null) return noPlayer(ptext);
  String node = node0 == null ? "" : node0.trim();
  if (node.startsWith("-")) node = node.substring(1);
  java.util.UUID u = java.util.UUID.fromString(p[0]);
  String[] have = @PKG@.RankEngine.userList(u, true);
  boolean found = false;
  for (int i = 0; i < have.length; i++) if (have[i].equals(node)) found = true;
  if (!found) return "=" + p[1] + " has no deny on " + node + ".";
  boolean ok = @PKG@.RankEngine.undeny(u, node);
  if (ok) @PKG@.RankStore.log(who, wn, via, "deny[" + p[1] + "]", "-" + node, "(none)");
  return ok ? "+" + p[1] + "'s deny on " + node + " is gone." : "-The deny on " + node + " is still there - see the server log.";
}""")
# through the config kit (validated by RankHooks.checkDefault, logged, versioned) - the same path as SkyyMenu's Server Setup
M(ops, r"""
public static String makeDefault(java.util.UUID who, String wn, String via, String text) {
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  int was = @PKG@.RankStore.position(rid);
  Object[] r = @PKG@.CfgFn.set("ranks.default", rid, who, wn, "yes", via);
  String stt = r == null || r.length < 3 ? "error" : String.valueOf(r[0]);
  String msg = r == null || r.length < 3 ? "could not change it" : String.valueOf(r[2]);
  if (was > 0 && @PKG@.RankStore.position(rid) == 0) msg = msg + " " + @PKG@.RankStore.label(rid) + " moved to the bottom of the ladder, where the default rank always is.";
  if (stt.equals("ok") || stt.equals("restart")) return (msg.indexOf("already") >= 0 ? "=" : "+") + msg;
  return "-" + msg;
}""")
M(ops, r"""
public static String who(String ptext) {
  String[] p = @PKG@.RankStore.findPlayer(ptext);
  if (p == null) return noPlayer(ptext);
  java.util.UUID u = java.util.UUID.fromString(p[0]);
  String rid = @PKG@.RankStore.effectiveRank(p[0]);
  java.util.Set g = @PKG@.RankPerm.groupsOf(u);
  String[] d = @PKG@.RankEngine.userList(u, true);
  String[] pg = @PKG@.RankEngine.userList(u, false);
  boolean adv = g != null && g.contains(@PKG@.RankEngine.ADV);
  return (adv || g == null ? "=" : "-") + p[1] + ": rank " + @PKG@.RankStore.label(rid) + (rid.equals(@PKG@.RankStore.defaultId()) ? " (default)" : "")
    + " - groups " + @PKG@.RankEngine.text(g) + (g != null && !adv && !g.contains(@PKG@.RankEngine.ADMIN) ? " - hytale:Adventurer MISSING" : "")
    + " - denies " + (d.length == 0 ? "none" : String.join(", ", java.util.Arrays.asList(d)))
    + (pg.length > 0 ? " - personal grants " + String.join(", ", java.util.Arrays.asList(pg)) : "") + ".";
}""")
M(ops, r"""
public static String info(String text) {
  String rid = @PKG@.RankStore.resolveRank(text);
  if (rid == null) return noRank(text);
  @PKG@.Rank r = @PKG@.RankStore.find(rid);
  boolean def = rid.equals(@PKG@.RankStore.defaultId());
  java.util.ArrayList ms = @PKG@.RankStore.membersOf(rid);
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < ms.size() && i < 12; i++) { if (b.length() > 0) b.append(", "); b.append(((String[]) ms.get(i))[1]); }
  if (ms.size() > 12) b.append(" and ").append(ms.size() - 12).append(" more");
  return "=" + r.name + " (" + rid + ", position " + (@PKG@.RankStore.position(rid) + 1) + " of " + @PKG@.RankStore.RANKS.size() + (def ? ", DEFAULT" : "") + (r.staff ? ", STAFF" : "") + ")"
    + " - prefix " + (r.prefix.length() == 0 ? "none" : r.prefix) + (r.colour.length() == 0 ? "" : " " + r.colour)
    + " - grants " + (r.grants.isEmpty() ? "none" : String.join(", ", r.grants)) + " (+" + @PKG@.RankStore.inherited(rid).size() + " from lower ranks)"
    + " - members " + (def ? "everyone without a rank" : (ms.isEmpty() ? "none" : b.toString())) + ".";
}""")
M(ops, r"""
public static String[] listLines() {
  java.util.ArrayList rows = @PKG@.RankStore.rankRows();
  String[] out = new String[rows.size() + 1];
  out[0] = "=Ranks, highest first (each rank also gets every grant of the ranks below it):";
  for (int i = 0; i < rows.size(); i++) {
    String[] r = (String[]) rows.get(i);
    out[i + 1] = "=" + r[5] + ". " + r[1] + " (" + r[0] + ")" + ("1".equals(r[9]) ? " DEFAULT - everyone without a rank" : " - " + r[6] + " members, " + r[7] + " grants (+" + r[8] + " from below)")
      + ("true".equals(r[4]) ? " - STAFF" : "") + (r[2].length() > 0 ? " - prefix " + r[2] : "");
  }
  return out;
}""")
# config.properties is re-read by the kit's reload op, which runs RankHooks.reloadCfg AFTER its pending writes (never read it here directly:
# a value set a moment ago may still be waiting for the kit's 500 ms save)
M(ops, r"""
public static String reload(java.util.UUID who, String wn) {
  String a = @PKG@.RankStore.reload();
  @PKG@.RankStore.floorDefault();
  @PKG@.RankHooks.warnDefault();
  String k = "";
  try {
    Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", who, wn, "command" });
    if (o instanceof Object[] && ((Object[]) o).length > 2) k = String.valueOf(((Object[]) o)[2]);
  } catch (Throwable t) { k = "config.properties not re-read: " + t; }
  @PKG@.RankStore.rebuildChatSafe();
  String s = "the permission system is still loading";
  if (@PKG@.RankEngine.STARTED) { s = @PKG@.RankEngine.syncGroups(); int c = @PKG@.RankEngine.reconcileStored(); if (c > 0) s = s + "; " + c + " stored members updated from permissions.json"; }
  @PKG@.RankStore.publishAll();
  return (@PKG@.RankStore.BROKEN ? "-" : "+") + "Re-read: " + a + ". Config: " + k + " Engine: " + s + ".";
}""")
M(ops, r"""
public static String sync() {
  if (!@PKG@.RankEngine.STARTED) return "-The permission system is still loading - try again in a few seconds.";
  String s = @PKG@.RankEngine.syncGroups();
  int c = @PKG@.RankEngine.reconcileStored();
  @PKG@.RankStore.publishAll();
  return "+" + s + (c > 0 ? "; " + c + " stored members updated from permissions.json." : "; the member list matches permissions.json.");
}""")

# ================= chat: RankFormatter / RankChatWrap / RankChatHook (the SkyyExploration TitleFormatter shape, one level further out) =================
fmt = mk("RankFormatter", ifaces=(T["PCF"],))
F(fmt, "public @PCF@ prev;")
C(fmt, "public RankFormatter(@PCF@ p) { this.prev = p; }")
M(fmt, r"""
public @MSG@ format(@PR@ sender, String content) {
  @MSG@ m = this.prev.format(sender, content);
  try {
    if (!@PKG@.RankCfg.CHAT_PREFIX || sender == null || m == null) return m;
    String[] c = @PKG@.RankStore.chatOf(sender.getUuid());
    if (c == null || c[0] == null || c[0].length() == 0) return m;
    @MSG@ p = @MSG@.raw(c[0] + " ");
    if (c[1] != null && c[1].length() == 7) p = p.color(c[1]);
    return @MSG@.join(new @MSG@[] { p, m });
  } catch (Throwable e) { return m; }
}""")
cwr = mk("RankChatWrap", ifaces=("java.util.function.Function",))
C(cwr, "public RankChatWrap() { }")
M(cwr, r"""
public Object apply(Object e) {
  try {
    if (!(e instanceof @PCE@)) return e;
    @PCE@ ev = (@PCE@) e;
    @PCF@ prev = ev.getFormatter();
    if (prev instanceof @PKG@.RankFormatter) return ev;
    ev.setFormatter(new @PKG@.RankFormatter(prev == null ? @PCE@.DEFAULT_FORMATTER : prev));
  } catch (Throwable t) { }
  return e;
}""")
chk = mk("RankChatHook", ifaces=("java.util.function.Function",))
F(chk, "public java.util.function.Function wrap;")
C(chk, "public RankChatHook() { this.wrap = new @PKG@.RankChatWrap(); }")
M(chk, r"""
public Object apply(Object f) {
  try {
    if (f instanceof java.util.concurrent.CompletableFuture) return ((java.util.concurrent.CompletableFuture) f).thenApply(this.wrap);
  } catch (Throwable t) { }
  return f;
}""")

# ================= rank:fn:of =================
ofn = mk("RankOfFn", ifaces=("java.util.function.Function",))
C(ofn, "public RankOfFn() { }")
M(ofn, r"""
public Object apply(Object a) {
  try {
    Object x = a;
    if (x instanceof Object[] && ((Object[]) x).length > 0) x = ((Object[]) x)[0];
    String us = null;
    if (x instanceof java.util.UUID) us = x.toString();
    else if (x instanceof String) us = java.util.UUID.fromString(((String) x).trim()).toString();
    if (us == null) return null;
    return @PKG@.RankStore.infoFor(us);
  } catch (Throwable t) { return null; }
}""")

# ================= tasks + events =================
stt = mk("RankStartTask", ifaces=("java.lang.Runnable",))
F(stt, "public int tries;")
C(stt, "public RankStartTask() { this.tries = 0; }")
M(stt, r"""
public void run() {
  try {
    if (!@PKG@.RankPerm.ready()) {
      this.tries++;
      if (this.tries <= 150) @PKG@.RankCfg.later(this, 2000L);
      else @PKG@.RankCfg.warn("the permission system did not finish loading within 5 minutes - ranks are not synced (rank changes stay refused); try /rankadmin sync");
      return;
    }
    @PKG@.RankCfg.info(@PKG@.RankEngine.start());
  } catch (Throwable t) { @PKG@.RankCfg.warn("start sync failed: " + t); }
}""")
join = mk("RankJoinTask", ifaces=("java.lang.Runnable",))
for f in ("public java.util.UUID u;", "public String name;", "public int tries;", "public static volatile boolean CHECKED;"):
    F(join, f)
C(join, "public RankJoinTask(java.util.UUID u, String name) { this.u = u; this.name = name; this.tries = 0; }")
# once per server run: /rank and /rankadmin must answer with OUR commands (duplicate names are silently last-wins)
M(join, r"""
public static void checkCommands() {
  if (CHECKED) return;
  CHECKED = true;
  try {
    @ACM@ a = @CMGR@.get().resolveCommand("rank");
    @ACM@ b = @CMGR@.get().resolveCommand("rankadmin");
    boolean okA = a != null && "@PKG@.RankCmd".equals(a.getClass().getName());
    boolean okB = b != null && "@PKG@.RankAdminCmd".equals(b.getClass().getName());
    if (!okA) @PKG@.RankCfg.warn("/rank does not belong to SkyyRanks (" + (a == null ? "not registered" : a.getClass().getName()) + ") - the ranks editor still opens with /rankadmin");
    if (!okB) @PKG@.RankCfg.warn("/rankadmin does not belong to SkyyRanks (" + (b == null ? "not registered" : b.getClass().getName()) + ")");
    if (okA && okB) @PKG@.RankCfg.info("command check: /rank /rankadmin belong to SkyyRanks");
  } catch (Throwable t) { @PKG@.RankCfg.warn("command check failed: " + t); }
}""")
M(join, r"""
public void run() {
  try {
    checkCommands();
    if (!@PKG@.RankEngine.STARTED) {
      this.tries++;
      if (this.tries <= 40) @PKG@.RankCfg.later(this, 3000L);
      return;
    }
    @PKG@.RankEngine.onJoin(this.u, this.name);
  } catch (Throwable t) { @PKG@.RankCfg.warn("join handling failed: " + t); }
}""")
rdy = mk("RankReady", ifaces=("java.util.function.Consumer",))
F(rdy, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")
C(rdy, "public RankReady() { }")
# PlayerReadyEvent fires on EVERY world switch -> once per CONNECTION. SESSION maps uuid -> WeakReference(PlayerRef): the PlayerRef is
# one object per connection that moves between worlds (PlayerRef.clone() returns this, removeFromStore/addToStore keep it; VERIFIED
# bytecode), so a world switch finds the same object and is skipped, while a reconnect is a new object and always re-arms - even when the
# old connection's PlayerDisconnectEvent has not been handled yet. Weak, so a missed disconnect never keeps a connection alive.
M(rdy, r"""
public void accept(Object ev) {
  try {
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    Object old = SESSION.get(u);
    if (old instanceof java.lang.ref.WeakReference && ((java.lang.ref.WeakReference) old).get() == pr) return;
    SESSION.put(u, new java.lang.ref.WeakReference(pr));
    @PKG@.RankCfg.later(new @PKG@.RankJoinTask(u, pr.getUsername()), 3000L);
  } catch (Throwable t) { @PKG@.RankCfg.warn("ready handler failed: " + t); }
}""")
quit_ = mk("RankQuit", ifaces=("java.util.function.Consumer",))
C(quit_, "public RankQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    Object o = @PKG@.RankReady.SESSION.get(u);
    Object x = o instanceof java.lang.ref.WeakReference ? ((java.lang.ref.WeakReference) o).get() : null;
    if (o != null && (x == null || x == pr)) @PKG@.RankReady.SESSION.remove(u, o);
    @PKG@.RankOps.CONFIRMS.remove(u);
  } catch (Throwable t) { }
}""")

# ================= RankPage: the big ranks editor (inline; guard() first in build() and handleDataEvent()) =================
page = mk("RankPage", T["PAGE"])
for f in ("public java.util.UUID me;", "public String meName;", "public String view;", "public String rankId;", "public int sub;",
          "public int mode;", "public int pageNo;", "public int pages;", "public String target;", "public String targetName;",
          "public int pick;", "public String status;", "public String d0;", "public String d1;", "public String i0;", "public String i1;",
          "public String i2;", "public String pfilter;", "public java.util.ArrayList rowKeys;", "public String[] pending;",
          "public String backView;", "public String confirmMsg;", "public boolean locked;", "public boolean testMode;",
          "public boolean setupCmd;", "public java.util.ArrayList hits;", "public String[] fkeys;", "public String[] fids;"):
    F(page, f)
M(page, r"""
public void init(String v, String arg) {
  this.view = "ranks"; this.rankId = ""; this.sub = 0; this.mode = 0; this.pageNo = 0; this.pages = 1;
  this.target = ""; this.targetName = ""; this.pick = -1; this.status = "";
  this.d0 = ""; this.d1 = ""; this.i0 = ""; this.i1 = ""; this.i2 = ""; this.pfilter = "";
  this.rowKeys = new java.util.ArrayList(); this.pending = null; this.backView = "ranks"; this.confirmMsg = "";
  this.locked = false; this.hits = null; this.fkeys = new String[0]; this.fids = new String[0];
  this.setupCmd = false;
  try { this.setupCmd = @CMGR@.get().resolveCommand("modconfig") != null; } catch (Throwable t) { this.setupCmd = false; }
  if ("player".equals(v) && arg != null) {
    String[] p = @PKG@.RankStore.findPlayer(arg);
    if (p != null) { this.view = "player"; this.target = p[0]; this.targetName = p[1]; }
    else this.status = @PKG@.RankOps.noPlayer(arg);
  } else if ("rank".equals(v) && arg != null && @PKG@.RankStore.resolveRank(arg) != null) {
    this.view = "rank"; this.rankId = @PKG@.RankStore.resolveRank(arg);
  }
}""")
C(page, r"""
public RankPage(@PR@ pr, String v, String arg) {
  super(pr, @LIFE@.CanDismiss);
  this.me = pr == null ? null : pr.getUuid();
  this.meName = pr == null ? "" : pr.getUsername();
  this.testMode = false;
  init(v, arg);
}""")
# test harness only (no PlayerRef in a bare JVM): the same page with a given admin UUID/name, never rebuilds on the wire
C(page, r"""
public RankPage(java.util.UUID u, String name, String v, String arg) {
  super((@PR@) null, @LIFE@.CanDismiss);
  this.me = u;
  this.meName = name;
  this.testMode = true;
  init(v, arg);
}""")
M(page, r"""
public boolean guard() {
  boolean ok = false;
  try { ok = @PKG@.RankPerm.has(this.me, "skyyranks.admin"); } catch (Throwable t) { ok = false; }
  if (!ok) {
    this.locked = true;
    this.pending = null;
    this.d0 = ""; this.d1 = ""; this.i0 = ""; this.i1 = ""; this.i2 = "";
    this.status = "-You no longer have access to the ranks editor (skyyranks.admin).";
  }
  return ok;
}""")
M(page, r"""
public void redraw() { if (!this.testMode) rebuild(); }""")
# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr, verified in game with a TextField)
M(page, r"""
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
M(page, r"""
public static boolean has(String data, String key) {
  return data != null && data.indexOf(String.valueOf((char) 34) + key + String.valueOf((char) 34)) >= 0;
}""")
M(page, r"""
public @EVD@ evd(String act) {
  @EVD@ e = @EVD@.of("a", act);
  for (int k = 0; k < this.fkeys.length; k++) e = e.append(this.fkeys[k], "#" + this.fids[k] + ".Value");
  return e;
}""")
M(page, r"""
public void bind(@UEB@ ev, String id, String act) { ev.addEventBinding(@BT@.Activating, "#" + id, evd(act)); }""")
M(page, r"""
public void bindEnter(@UEB@ ev, String id, String act) { ev.addEventBinding(@BT@.Validating, "#" + id, evd(act), false); }""")
M(page, r"""
public void clearDrafts() { this.d0 = ""; this.d1 = ""; this.i0 = ""; this.i1 = ""; this.i2 = ""; }""")
M(page, r"""
public void setPages(int n) {
  this.pages = n <= 7 ? 1 : (n + 6) / 7;
  if (this.pageNo >= this.pages) this.pageNo = this.pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
}""")
M(page, r"""
public String pageText() { return this.pages > 1 ? "   -   page " + (this.pageNo + 1) + " of " + this.pages : ""; }""")
# ---- building blocks
M(page, r"""
public void rowStart(@UCB@ b, int r, String txt) {
  b.appendInline("#SkyyRkRows", @PKG@.RankUI.r(@PKG@.RankUI.ROW, r));
  b.appendInline("#SkyyRkRow" + r, @PKG@.RankUI.LEAD);
  b.appendInline("#SkyyRkRow" + r, @PKG@.RankUI.r(txt, r));
}""")
M(page, r"""
public void texts(@UCB@ b, int r, String name, String desc, boolean dim) {
  b.appendInline("#SkyyRkTxt" + r, @PKG@.RankUI.r(dim ? @PKG@.RankUI.NAMEDIM : @PKG@.RankUI.NAME, r));
  b.appendInline("#SkyyRkTxt" + r, @PKG@.RankUI.r(@PKG@.RankUI.DESC, r));
  b.set("#SkyyRkName" + r + ".Text", name == null ? "" : name);
  b.set("#SkyyRkDesc" + r + ".Text", desc == null ? "" : desc);
}""")
M(page, r"""
public void rowEnd(@UCB@ b) { b.appendInline("#SkyyRkRows", @PKG@.RankUI.GAP6); }""")
M(page, r"""
public void sp(@UCB@ b, int r) { b.appendInline("#SkyyRkRow" + r, @PKG@.RankUI.SP10); }""")
M(page, r"""
public void button(@UCB@ b, @UEB@ ev, int r, String tpl, String idBase, String act) {
  b.appendInline("#SkyyRkRow" + r, @PKG@.RankUI.r(tpl, r));
  bind(ev, idBase + r, act);
}""")
# the prefix preview in the rank's own colour (colours are validated #rrggbb, so they are safe inside the markup)
M(page, r"""
public void pre(@UCB@ b, int r, String prefix, String colour) {
  String c = colour != null && colour.length() == 7 ? colour : "#ffffff";
  boolean none = prefix == null || prefix.length() == 0;
  b.appendInline("#SkyyRkRow" + r, @PKG@.RankUI.r(@PKG@.RankUI.PRE, r).replace("%C", none ? "#6e7da1" : c));
  b.set("#SkyyRkPre" + r + ".Text", none ? "(no prefix)" : prefix);
}""")
M(page, r"""
public void empty(@UCB@ b, String text) {
  b.appendInline("#SkyyRkRows", @PKG@.RankUI.EMPTY);
  b.set("#SkyyRkEmpty.Text", text);
}""")
M(page, r"""
public void addRow(@UCB@ b, String label) {
  b.appendInline("#SkyyRk", @PKG@.RankUI.ADD);
  b.appendInline("#SkyyRkAdd", @PKG@.RankUI.ADDLBL);
  b.set("#SkyyRkAddLbl.Text", label);
  b.appendInline("#SkyyRkAdd", @PKG@.RankUI.ADDSP);
}""")
M(page, r"""
public void field(@UCB@ b, @UEB@ ev, int n, int w, String placeholder, String value, String enterAct) {
  String box = n == 0 ? @PKG@.RankUI.FB0 : @PKG@.RankUI.FB1;
  String tf = n == 0 ? @PKG@.RankUI.F0 : @PKG@.RankUI.F1;
  b.appendInline("#SkyyRkAdd", @PKG@.RankUI.w(box, w));
  b.appendInline("#SkyyRkFB" + n, tf.replace("%P", placeholder));
  if (value != null && value.length() > 0) b.set("#SkyyRkF" + n + ".Value", value);
  bindEnter(ev, "SkyyRkF" + n, enterAct);
  b.appendInline("#SkyyRkAdd", @PKG@.RankUI.ADDSP);
}""")
M(page, r"""
public void act(@UCB@ b, @UEB@ ev, int n, int w, String text, String action) {
  String t = n == 0 ? @PKG@.RankUI.ACT0 : @PKG@.RankUI.ACT1;
  b.appendInline("#SkyyRkAdd", @PKG@.RankUI.w(t, w).replace("%T", text));
  bind(ev, "SkyyRkAct" + n, action);
  b.appendInline("#SkyyRkAdd", @PKG@.RankUI.ADDSP);
}""")
M(page, r"""
public void tab(@UCB@ b, @UEB@ ev, int i, boolean sel) {
  b.appendInline("#SkyyRkTabs", sel ? @PKG@.RankUI.TABSEL[i] : @PKG@.RankUI.TAB[i]);
  bind(ev, "SkyyRkTab" + i, "tab" + i);
}""")
M(page, r"""
public void buildTabs(@UCB@ b, @UEB@ ev) {
  b.appendInline("#SkyyRk", @PKG@.RankUI.TABS);
  boolean rk = this.view.equals("rank");
  boolean pl = this.view.equals("players") || this.view.equals("player");
  tab(b, ev, 0, !pl);
  b.appendInline("#SkyyRkTabs", @PKG@.RankUI.SP12);
  tab(b, ev, 1, pl);
  if (rk) {
    b.appendInline("#SkyyRkTabs", @PKG@.RankUI.SP48);
    tab(b, ev, 2, this.sub == 0);
    b.appendInline("#SkyyRkTabs", @PKG@.RankUI.SP12);
    tab(b, ev, 3, this.sub == 1);
    b.appendInline("#SkyyRkTabs", @PKG@.RankUI.SP12);
    tab(b, ev, 4, this.sub == 2);
  }
}""")
M(page, r"""
public void buildStatus(@UCB@ b) {
  String s = this.status == null ? "" : this.status;
  char c = s.length() == 0 ? '=' : s.charAt(0);
  String t = c == '+' ? @PKG@.RankUI.STOK : (c == '-' ? @PKG@.RankUI.STBAD : @PKG@.RankUI.STINFO);
  b.appendInline("#SkyyRk", t);
  b.set("#SkyyRkStatus.Text", @PKG@.RankCfg.textOf(s));
}""")
M(page, r"""
public void buildFoot(@UCB@ b, @UEB@ ev, boolean paging) {
  b.appendInline("#SkyyRk", @PKG@.RankUI.FOOT);
  b.appendInline("#SkyyRkFoot", @PKG@.RankUI.FLEAD);
  if (paging && this.pages > 1) {
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.PREV); bind(ev, "SkyyRkPrev", "prev");
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.FSP);
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.NEXT); bind(ev, "SkyyRkNext", "next");
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.FSP);
  }
  if (!this.locked) {
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.REFRESH); bind(ev, "SkyyRkRefresh", "refresh");
    b.appendInline("#SkyyRkFoot", @PKG@.RankUI.FSP);
    if (this.setupCmd) { b.appendInline("#SkyyRkFoot", @PKG@.RankUI.SETUP); bind(ev, "SkyyRkSetup", "setup"); b.appendInline("#SkyyRkFoot", @PKG@.RankUI.FSP); }
  }
  b.appendInline("#SkyyRkFoot", @PKG@.RankUI.CLOSE); bind(ev, "SkyyRkClose", "close");
}""")
# ---- view: Ranks (highest first)
M(page, r"""
public void buildRanks(@UCB@ b, @UEB@ ev) {
  java.util.ArrayList l = @PKG@.RankStore.rankRows();
  String def = @PKG@.RankStore.defaultId();
  b.set("#SkyyRkTitle.Text", "Ranks");
  b.set("#SkyyRkHint.Text", "Each rank also gets every grant of the ranks below it. Players without a rank show as " + @PKG@.RankStore.label(def) + ".");
  int n = l.size();
  setPages(n);
  b.set("#SkyyRkHead.Text", "Ranks   -   " + n + "   -   highest first" + pageText());
  b.appendInline("#SkyyRk", @PKG@.RankUI.ROWS);
  int from = this.pageNo * 7;
  int to = Math.min(n, from + 7);
  for (int i = from; i < to; i++) {
    String[] r = (String[]) l.get(i);
    int ri = i - from;
    boolean isDef = "1".equals(r[9]);
    this.rowKeys.add(r[0]);
    rowStart(b, ri, @PKG@.RankUI.TXTA);
    String tags = (isDef ? "   DEFAULT" : "") + ("true".equals(r[4]) ? "   STAFF" : "");
    String desc = isDef ? "everyone without a rank - no group, no grants" : r[6] + ("1".equals(r[6]) ? " member" : " members") + " - " + r[7] + " grants" + ("0".equals(r[8]) ? "" : " (+" + r[8] + " below)") + " - skyy:" + r[0];
    texts(b, ri, r[5] + ".  " + r[1] + tags, desc, false);
    pre(b, ri, r[2], r[3]);
    sp(b, ri);
    if (isDef) b.appendInline("#SkyyRkRow" + ri, @PKG@.RankUI.GAPUD);
    else {
      button(b, ev, ri, @PKG@.RankUI.UP, "SkyyRkUp", "up:" + ri);
      sp(b, ri);
      button(b, ev, ri, @PKG@.RankUI.DOWN, "SkyyRkDown", "down:" + ri);
      sp(b, ri);
    }
    button(b, ev, ri, @PKG@.RankUI.EDIT, "SkyyRkEdit", "edit:" + ri);
    sp(b, ri);
    if (!isDef) button(b, ev, ri, @PKG@.RankUI.DEL, "SkyyRkDel", "del:" + ri);
    rowEnd(b);
  }
  if (n == 0) empty(b, "No ranks - ranks.properties could not be read.");
  addRow(b, "New rank");
  field(b, ev, 0, 220, @PKG@.RankUI.P_ID, this.d0, "create");
  field(b, ev, 1, 340, @PKG@.RankUI.P_NAME, this.d1, "create");
  act(b, ev, 0, 220, @PKG@.RankUI.A_CREATE, "create");
}""")
# ---- view: one rank, tab Settings (7 fixed rows)
M(page, r"""
public void setRow(@UCB@ b, @UEB@ ev, int r, String draft, String current, boolean clear) {
  b.appendInline("#SkyyRkRow" + r, @PKG@.RankUI.r(@PKG@.RankUI.BOX, r));
  b.appendInline("#SkyyRkBox" + r, @PKG@.RankUI.r(@PKG@.RankUI.IN, r));
  String v = draft != null && draft.length() > 0 ? draft : current;
  if (v != null && v.length() > 0) b.set("#SkyyRkIn" + r + ".Value", v);
  bindEnter(ev, "SkyyRkIn" + r, "set" + r);
  sp(b, r);
  button(b, ev, r, @PKG@.RankUI.SET, "SkyyRkSet", "set" + r);
  if (clear) { sp(b, r); button(b, ev, r, @PKG@.RankUI.CLR, "SkyyRkClr", "clr" + r); }
}""")
M(page, r"""
public void buildSettings(@UCB@ b, @UEB@ ev, @PKG@.Rank rk) {
  String def = @PKG@.RankStore.defaultId();
  boolean isDef = rk.id.equals(def);
  java.util.ArrayList l = @PKG@.RankStore.RANKS;
  int pos = @PKG@.RankStore.idx(l, rk.id);
  b.set("#SkyyRkHead.Text", rk.name + "   -   settings");
  b.appendInline("#SkyyRk", @PKG@.RankUI.ROWS);
  rowStart(b, 0, @PKG@.RankUI.TXTB);
  texts(b, 0, "Display name", "Now: " + rk.name + "   (1-24 characters)", false);
  setRow(b, ev, 0, this.i0, rk.name, false);
  rowEnd(b);
  rowStart(b, 1, @PKG@.RankUI.TXTE);
  texts(b, 1, "Chat prefix", rk.prefix.length() == 0 ? "none - chat shows no rank" : "[Rank] [Title] Name: text", false);
  pre(b, 1, rk.prefix, rk.colour);
  setRow(b, ev, 1, this.i1, rk.prefix, true);
  rowEnd(b);
  rowStart(b, 2, @PKG@.RankUI.TXTE);
  texts(b, 2, "Prefix colour", "like #ff5555, red or gold", false);
  pre(b, 2, rk.colour.length() == 0 ? "plain" : rk.colour, rk.colour);
  setRow(b, ev, 2, this.i2, rk.colour, true);
  rowEnd(b);
  rowStart(b, 3, @PKG@.RankUI.TXTD);
  texts(b, 3, "Staff rank", "Marks staff for other mods. A personal deny on a staff member asks first.", false);
  button(b, ev, 3, rk.staff ? @PKG@.RankUI.ONSEL : @PKG@.RankUI.ON, "SkyyRkOn", "staffon");
  sp(b, 3);
  button(b, ev, 3, rk.staff ? @PKG@.RankUI.OFF : @PKG@.RankUI.OFFSEL, "SkyyRkOff", "staffoff");
  rowEnd(b);
  rowStart(b, 4, @PKG@.RankUI.TXTD);
  int below = 0;
  for (int i = 0; i < pos; i++) if (!((@PKG@.Rank) l.get(i)).id.equals(def)) below++;
  if (isDef) texts(b, 4, "Position " + (pos + 1) + " of " + l.size(), "The default rank always stays at the bottom: it is everyone without a rank.", false);
  else {
    texts(b, 4, "Position " + (pos + 1) + " of " + l.size(), below == 0 ? "The lowest rank above the default - it gets no other rank's grants." : "It also gets every grant of the " + below + (below == 1 ? " rank" : " ranks") + " below it.", false);
    button(b, ev, 4, @PKG@.RankUI.UP2, "SkyyRkUp", "mvup");
    sp(b, 4);
    button(b, ev, 4, @PKG@.RankUI.DOWN2, "SkyyRkDown", "mvdown");
  }
  rowEnd(b);
  rowStart(b, 5, @PKG@.RankUI.TXTD);
  texts(b, 5, isDef ? "The default rank" : "Default rank", isDef ? "Everyone without a rank shows as " + rk.name + ". It has no group, members or grants." : "Needs no members or grants. It then moves to the bottom of the ladder.", false);
  if (!isDef) button(b, ev, 5, @PKG@.RankUI.MK, "SkyyRkMk", "mkdef");
  rowEnd(b);
  rowStart(b, 6, @PKG@.RankUI.TXTD);
  texts(b, 6, "Delete rank", isDef ? "The default rank cannot be deleted - make another rank the default first." : "Its members go back to " + @PKG@.RankStore.label(def) + " and lose its grants (asks first).", false);
  if (!isDef) button(b, ev, 6, @PKG@.RankUI.DEL2, "SkyyRkDel", "delrank");
  rowEnd(b);
}""")
# ---- view: one rank, tab Grants (own grants, then the ones copied from lower ranks; or the search hits)
M(page, r"""
public void buildGrants(@UCB@ b, @UEB@ ev, @PKG@.Rank rk) {
  boolean isDef = rk.id.equals(@PKG@.RankStore.defaultId());
  java.util.ArrayList inh = @PKG@.RankStore.inherited(rk.id);
  b.appendInline("#SkyyRk", @PKG@.RankUI.ROWS);
  if (isDef) {
    setPages(0);
    b.set("#SkyyRkHead.Text", rk.name + "   -   grants");
    empty(b, "The default rank holds no grants: it is everyone without a rank. Give permissions to a rank, or use the mod's own settings.");
    return;
  }
  java.util.ArrayList items = new java.util.ArrayList();
  if (this.mode == 1 && this.hits != null) {
    for (int i = 0; i < this.hits.size(); i++) items.add(new String[] { (String) this.hits.get(i), "hit" });
  } else {
    java.util.Iterator it = rk.grants.iterator();
    while (it.hasNext()) items.add(new String[] { (String) it.next(), "own" });
    for (int i = 0; i < inh.size(); i++) { String[] x = (String[]) inh.get(i); items.add(new String[] { x[0], "from " + x[1] }); }
  }
  int n = items.size();
  setPages(n);
  if (this.mode == 1) b.set("#SkyyRkHead.Text", "Search   -   " + n + (n == 1 ? " node" : " nodes") + " found (20 at most)" + pageText());
  else b.set("#SkyyRkHead.Text", rk.name + "   -   " + rk.grants.size() + " own grants, " + inh.size() + " from lower ranks" + pageText());
  int from = this.pageNo * 7;
  int to = Math.min(n, from + 7);
  for (int i = from; i < to; i++) {
    String[] x = (String[]) items.get(i);
    int ri = i - from;
    this.rowKeys.add(x[0]);
    rowStart(b, ri, @PKG@.RankUI.TXTC);
    if (x[1].equals("hit")) {
      boolean hasIt = rk.grants.contains(x[0]);
      texts(b, ri, x[0], hasIt ? rk.name + " already has it" : (@PKG@.RankStore.dangerous(x[0]) ? "admin node - asks before granting" : "registered by the server or a mod"), hasIt);
      sp(b, ri);
      if (!hasIt) button(b, ev, ri, @PKG@.RankUI.GR, "SkyyRkGr", "hit:" + ri);
    } else if (x[1].equals("own")) {
      texts(b, ri, x[0], "own grant" + (@PKG@.RankStore.dangerous(x[0]) ? " - admin node" : "") + " - every higher rank gets it too", false);
      sp(b, ri);
      button(b, ev, ri, @PKG@.RankUI.REM, "SkyyRkRem", "ungrant:" + ri);
    } else {
      texts(b, ri, x[0], x[1] + " (a lower rank) - remove it there", true);
    }
    rowEnd(b);
  }
  if (n == 0) empty(b, this.mode == 1 ? "No registered node matches. Type the exact node and click Grant to grant it anyway." : rk.name + " has no grants yet. Type a node below (like skyyessentials.fly) or search.");
  addRow(b, "Grant");
  field(b, ev, 0, 480, @PKG@.RankUI.P_NODE, this.d0, "grant");
  act(b, ev, 0, 150, @PKG@.RankUI.A_GRANT, "grant");
  if (this.mode == 1) act(b, ev, 1, 200, @PKG@.RankUI.A_BACKG, "hitsback");
  else act(b, ev, 1, 150, @PKG@.RankUI.A_SEARCH, "search");
}""")
# ---- view: one rank, tab Members (members, or the online players to add)
M(page, r"""
public void buildMembers(@UCB@ b, @UEB@ ev, @PKG@.Rank rk) {
  boolean isDef = rk.id.equals(@PKG@.RankStore.defaultId());
  b.appendInline("#SkyyRk", @PKG@.RankUI.ROWS);
  if (isDef) {
    setPages(0);
    b.set("#SkyyRkHead.Text", rk.name + "   -   members");
    empty(b, "Everyone without a rank shows as " + rk.name + ". To take a rank away, remove the player from that rank.");
    return;
  }
  java.util.ArrayList items = new java.util.ArrayList();
  if (this.mode == 1) {
    java.util.ArrayList on = @PKG@.RankCfg.online();
    for (int i = 0; i < on.size(); i++) { String[] p = (String[]) on.get(i); items.add(new String[] { p[0], p[1], "on" }); }
  } else {
    java.util.ArrayList ms = @PKG@.RankStore.membersOf(rk.id);
    for (int i = 0; i < ms.size(); i++) { String[] p = (String[]) ms.get(i); items.add(new String[] { p[0], p[1], "m" }); }
  }
  int n = items.size();
  setPages(n);
  b.set("#SkyyRkHead.Text", this.mode == 1 ? "Online players   -   " + n + pageText() : rk.name + "   -   " + n + (n == 1 ? " member" : " members") + pageText());
  int from = this.pageNo * 7;
  int to = Math.min(n, from + 7);
  for (int i = from; i < to; i++) {
    String[] x = (String[]) items.get(i);
    int ri = i - from;
    this.rowKeys.add(x[0]);
    rowStart(b, ri, @PKG@.RankUI.TXTC);
    boolean online = x[2].equals("on") || @PKG@.RankCfg.isOnline(x[0]);
    if (x[2].equals("on")) {
      String cur = @PKG@.RankStore.effectiveRank(x[0]);
      boolean already = cur.equals(rk.id);
      texts(b, ri, x[1] + "   (online)", "Rank now: " + @PKG@.RankStore.label(cur) + (already ? " - already in " + rk.name : ""), already);
      sp(b, ri);
      if (!already) button(b, ev, ri, @PKG@.RankUI.ADDR, "SkyyRkAddr", "addon:" + ri);
    } else {
      texts(b, ri, x[1] + (online ? "   (online)" : ""), x[0], false);
      sp(b, ri);
      button(b, ev, ri, @PKG@.RankUI.REM, "SkyyRkRem", "unmember:" + ri);
    }
    rowEnd(b);
  }
  if (n == 0) empty(b, this.mode == 1 ? "Nobody is online." : rk.name + " has no members yet. Add one by name below, or pick from the online players.");
  addRow(b, "Add");
  field(b, ev, 0, 480, @PKG@.RankUI.P_PLAYER, this.d0, "addmember");
  act(b, ev, 0, 180, @PKG@.RankUI.A_ADDM, "addmember");
  if (this.mode == 1) act(b, ev, 1, 200, @PKG@.RankUI.A_BACKM, "onlineback");
  else act(b, ev, 1, 200, @PKG@.RankUI.A_ONLINE, "online");
}""")
# ---- view: Players (online first, then seen players)
M(page, r"""
public void buildPlayers(@UCB@ b, @UEB@ ev) {
  b.set("#SkyyRkTitle.Text", "Ranks - Players");
  b.set("#SkyyRkHint.Text", "Open a player to change their rank or their personal denies. Online players come first.");
  String f = this.pfilter == null ? "" : this.pfilter.trim().toLowerCase();
  java.util.ArrayList items = new java.util.ArrayList();
  java.util.HashSet seenU = new java.util.HashSet();
  java.util.ArrayList on = @PKG@.RankCfg.online();
  for (int i = 0; i < on.size(); i++) {
    String[] p = (String[]) on.get(i);
    if (f.length() > 0 && p[1].toLowerCase().indexOf(f) < 0) continue;
    items.add(new String[] { p[0], p[1], "on" });
    seenU.add(p[0]);
  }
  java.util.ArrayList st = @PKG@.RankStore.searchStored(f, 200);
  for (int i = 0; i < st.size(); i++) { String[] p = (String[]) st.get(i); if (seenU.add(p[0])) items.add(new String[] { p[0], p[1], "" }); }
  int n = items.size();
  setPages(n);
  b.set("#SkyyRkHead.Text", "Players   -   " + n + (f.length() > 0 ? " matching " + this.pfilter : "") + pageText());
  b.appendInline("#SkyyRk", @PKG@.RankUI.ROWS);
  int from = this.pageNo * 7;
  int to = Math.min(n, from + 7);
  for (int i = from; i < to; i++) {
    String[] x = (String[]) items.get(i);
    int ri = i - from;
    this.rowKeys.add(x[0]);
    rowStart(b, ri, @PKG@.RankUI.TXTC);
    String rid = @PKG@.RankStore.effectiveRank(x[0]);
    texts(b, ri, x[1] + (x[2].equals("on") ? "   (online)" : ""), "Rank: " + @PKG@.RankStore.label(rid) + (rid.equals(@PKG@.RankStore.defaultId()) ? " (default)" : ""), false);
    sp(b, ri);
    button(b, ev, ri, @PKG@.RankUI.OPEN, "SkyyRkOpen", "popen:" + ri);
    rowEnd(b);
  }
  if (n == 0) empty(b, f.length() > 0 ? "No player matches " + this.pfilter + "." : "No players seen yet.");
  addRow(b, "Find");
  field(b, ev, 0, 480, @PKG@.RankUI.P_FIND, this.d0, "psearch");
  act(b, ev, 0, 150, @PKG@.RankUI.A_FIND, "psearch");
  act(b, ev, 1, 150, @PKG@.RankUI.A_ALL, "pall");
}""")
# ---- view: one player (rank picker, engine groups, personal denies)
M(page, r"""
public void buildPlayer(@UCB@ b, @UEB@ ev) {
  java.util.UUID u = java.util.UUID.fromString(this.target);
  java.util.ArrayList l = @PKG@.RankStore.RANKS;
  String cur = @PKG@.RankStore.effectiveRank(this.target);
  if (this.pick < 0 || this.pick >= l.size()) this.pick = Math.max(0, @PKG@.RankStore.idx(l, cur));
  @PKG@.Rank pk = (@PKG@.Rank) l.get(this.pick);
  b.set("#SkyyRkTitle.Text", "Player - " + this.targetName);
  b.set("#SkyyRkHint.Text", "A personal deny is checked before every rank and before op. Changing the rank always keeps hytale:Adventurer.");
  String[] den = @PKG@.RankEngine.userList(u, true);
  boolean hitMode = this.mode == 1 && this.hits != null;
  String[] d = hitMode ? (String[]) this.hits.toArray(new String[0]) : den;
  int n = d.length;
  this.pages = n <= 5 ? 1 : (n + 4) / 5;
  if (this.pageNo >= this.pages) this.pageNo = this.pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  if (hitMode) b.set("#SkyyRkHead.Text", "Search   -   " + n + (n == 1 ? " node" : " nodes") + " found (20 at most)" + pageText());
  else b.set("#SkyyRkHead.Text", this.targetName + "   -   rank " + @PKG@.RankStore.label(cur) + "   -   " + n + (n == 1 ? " deny" : " denies") + pageText());
  b.appendInline("#SkyyRk", @PKG@.RankUI.ROWS);
  rowStart(b, 0, @PKG@.RankUI.TXTF);
  texts(b, 0, "Rank: " + @PKG@.RankStore.label(cur) + (cur.equals(@PKG@.RankStore.defaultId()) ? " (default)" : ""), "Pick a rank with < and >, then click Set rank.", false);
  b.appendInline("#SkyyRkRow0", @PKG@.RankUI.CYP); bind(ev, "SkyyRkCyp", "cprev");
  sp(b, 0);
  b.appendInline("#SkyyRkRow0", @PKG@.RankUI.PICK);
  b.set("#SkyyRkPick.Text", pk.name + (pk.id.equals(@PKG@.RankStore.defaultId()) ? " (default)" : ""));
  sp(b, 0);
  b.appendInline("#SkyyRkRow0", @PKG@.RankUI.CYN); bind(ev, "SkyyRkCyn", "cnext");
  sp(b, 0);
  b.appendInline("#SkyyRkRow0", @PKG@.RankUI.SETRANK); bind(ev, "SkyyRkSetRank", "setrank");
  rowEnd(b);
  java.util.Set g = @PKG@.RankPerm.groupsOf(u);
  boolean adv = g != null && g.contains(@PKG@.RankEngine.ADV);
  rowStart(b, 1, @PKG@.RankUI.TXTC);
  texts(b, 1, "Permission groups" + (g != null && g.contains(@PKG@.RankEngine.ADMIN) ? " - op" : ""), @PKG@.RankEngine.text(g) + (g != null && !adv ? "   - hytale:Adventurer MISSING" : ""), false);
  rowEnd(b);
  int from = this.pageNo * 5;
  int to = Math.min(n, from + 5);
  for (int i = from; i < to; i++) {
    int ri = i - from + 2;
    this.rowKeys.add(d[i]);
    rowStart(b, ri, @PKG@.RankUI.TXTC);
    if (hitMode) {
      boolean already = false;
      for (int k = 0; k < den.length; k++) if (den[k].equals(d[i])) already = true;
      texts(b, ri, d[i], already ? this.targetName + " already has a deny on it" : "registered by the server or a mod - Deny takes it from " + this.targetName + " only", already);
      sp(b, ri);
      if (!already) button(b, ev, ri, @PKG@.RankUI.DENYB, "SkyyRkDn", "dhit:" + (i - from));
    } else {
      texts(b, ri, "-" + d[i], "Denied for " + this.targetName + " - checked before any rank or op", false);
      sp(b, ri);
      button(b, ev, ri, @PKG@.RankUI.REM, "SkyyRkRem", "undeny:" + (i - from));
    }
    rowEnd(b);
  }
  if (n == 0) {
    rowStart(b, 2, @PKG@.RankUI.TXTC);
    if (hitMode) texts(b, 2, "No registered node matches", "Type the exact node and click Deny to deny it anyway.", true);
    else texts(b, 2, "No personal denies", "Type a node below to take it from " + this.targetName + " only (like skyyessentials.fly), or search.", true);
    rowEnd(b);
  }
  addRow(b, "Deny");
  field(b, ev, 0, 480, @PKG@.RankUI.P_DENY, this.d0, "deny");
  act(b, ev, 0, 150, @PKG@.RankUI.A_DENY, "deny");
  if (hitMode) act(b, ev, 1, 200, @PKG@.RankUI.A_BACKD, "dhitsback");
  else act(b, ev, 1, 150, @PKG@.RankUI.A_SEARCH, "dsearch");
}""")
M(page, r"""
public void buildConfirm(@UCB@ b, @UEB@ ev) {
  b.set("#SkyyRkTitle.Text", "Please confirm");
  b.set("#SkyyRkHint.Text", "Nothing has changed yet.");
  b.appendInline("#SkyyRk", @PKG@.RankUI.GAP8);
  b.appendInline("#SkyyRk", @PKG@.RankUI.MSGBOX);
  b.appendInline("#SkyyRkMsgBox", @PKG@.RankUI.MSG);
  b.set("#SkyyRkMsg.Text", this.confirmMsg == null ? "" : this.confirmMsg);
  b.appendInline("#SkyyRk", @PKG@.RankUI.CROW);
  b.appendInline("#SkyyRkCRow", @PKG@.RankUI.CLEAD);
  b.appendInline("#SkyyRkCRow", @PKG@.RankUI.YES); bind(ev, "SkyyRkYes", "yes");
  b.appendInline("#SkyyRkCRow", @PKG@.RankUI.CSP);
  b.appendInline("#SkyyRkCRow", @PKG@.RankUI.NO); bind(ev, "SkyyRkNo", "no");
  buildStatus(b);
  buildFoot(b, ev, false);
}""")
M(page, r"""
public void fieldsFor() {
  if (this.view.equals("confirm") || this.locked) { this.fkeys = new String[0]; this.fids = new String[0]; return; }
  if (this.view.equals("ranks")) { this.fkeys = new String[] { "@F0", "@F1" }; this.fids = new String[] { "SkyyRkF0", "SkyyRkF1" }; return; }
  if (this.view.equals("rank") && this.sub == 0) { this.fkeys = new String[] { "@I0", "@I1", "@I2" }; this.fids = new String[] { "SkyyRkIn0", "SkyyRkIn1", "SkyyRkIn2" }; return; }
  if (this.view.equals("rank") && this.rankId.equals(@PKG@.RankStore.defaultId())) { this.fkeys = new String[0]; this.fids = new String[0]; return; }
  this.fkeys = new String[] { "@F0" };
  this.fids = new String[] { "SkyyRkF0" };
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  boolean ok = guard();
  this.rowKeys = new java.util.ArrayList();
  if (ok && this.view.equals("rank") && @PKG@.RankStore.find(this.rankId) == null) { this.view = "ranks"; this.pageNo = 0; }
  if (ok && this.view.equals("player") && this.target.length() == 0) this.view = "players";
  fieldsFor();
  b.appendInline((String) null, @PKG@.RankUI.ROOT);
  b.appendInline("#SkyyRk", @PKG@.RankUI.ACCENT);
  b.appendInline("#SkyyRk", @PKG@.RankUI.TITLE);
  b.appendInline("#SkyyRk", @PKG@.RankUI.HINT);
  if (!ok) {
    b.set("#SkyyRkTitle.Text", "Ranks");
    b.set("#SkyyRkHint.Text", "");
    buildStatus(b);
    buildFoot(b, ev, false);
    return;
  }
  if (this.view.equals("confirm")) { buildConfirm(b, ev); return; }
  if (@PKG@.RankStore.BROKEN && (this.status == null || this.status.length() == 0)) this.status = "-ranks.properties cannot be read (" + @PKG@.RankStore.WHY + ") - rank changes are refused until it is fixed (then /rankadmin reload).";
  else if (!@PKG@.RankEngine.STARTED && (this.status == null || this.status.length() == 0)) this.status = "=The permission system is still loading - rank changes wait a few seconds.";
  buildTabs(b, ev);
  b.appendInline("#SkyyRk", @PKG@.RankUI.GAP8);
  b.appendInline("#SkyyRk", @PKG@.RankUI.HEAD);
  if (this.view.equals("rank")) {
    @PKG@.Rank rk = @PKG@.RankStore.find(this.rankId);
    b.set("#SkyyRkTitle.Text", "Rank - " + rk.name);
    b.set("#SkyyRkHint.Text", "Engine group skyy:" + rk.id + ". It also gets every grant of the ranks below it.");
    if (this.sub == 1) buildGrants(b, ev, rk);
    else if (this.sub == 2) buildMembers(b, ev, rk);
    else { this.pages = 1; buildSettings(b, ev, rk); }
  } else if (this.view.equals("players")) buildPlayers(b, ev);
  else if (this.view.equals("player")) buildPlayer(b, ev);
  else buildRanks(b, ev);
  buildStatus(b);
  buildFoot(b, ev, true);
}""")
# ---- clicks
M(page, r"""
public int idx(String a, String prefix) {
  if (!a.startsWith(prefix)) return -1;
  try {
    int i = Integer.parseInt(a.substring(prefix.length()));
    if (i < 0 || this.rowKeys == null || i >= this.rowKeys.size()) return -1;
    return i;
  } catch (Throwable t) { return -1; }
}""")
M(page, r"""
public String key(int i) { return (String) this.rowKeys.get(i); }""")
M(page, r"""
public void capture(String data) {
  if (has(data, "@F0")) this.d0 = jsonStr(data, "@F0");
  if (has(data, "@F1")) this.d1 = jsonStr(data, "@F1");
  if (has(data, "@I0")) this.i0 = jsonStr(data, "@I0");
  if (has(data, "@I1")) this.i1 = jsonStr(data, "@I1");
  if (has(data, "@I2")) this.i2 = jsonStr(data, "@I2");
}""")
M(page, r"""
public String runOp(String[] op, boolean conf) {
  String o = op[0];
  java.util.UUID u = this.me;
  String n = this.meName;
  if (o.equals("create")) return @PKG@.RankOps.create(u, n, "menu", op[1], op[2]);
  if (o.equals("delete")) return @PKG@.RankOps.delete(u, n, "menu", op[1], conf);
  if (o.equals("name")) return @PKG@.RankOps.rename(u, n, "menu", op[1], op[2]);
  if (o.equals("prefix")) return @PKG@.RankOps.prefix(u, n, "menu", op[1], op[2]);
  if (o.equals("colour")) return @PKG@.RankOps.colour(u, n, "menu", op[1], op[2]);
  if (o.equals("staff")) return @PKG@.RankOps.staff(u, n, "menu", op[1], "on".equals(op[2]));
  if (o.equals("move")) return @PKG@.RankOps.move(u, n, "menu", op[1], "up".equals(op[2]), conf);
  if (o.equals("grant")) return @PKG@.RankOps.grant(u, n, "menu", op[1], op[2], conf);
  if (o.equals("ungrant")) return @PKG@.RankOps.ungrant(u, n, "menu", op[1], op[2], conf);
  if (o.equals("setrank")) return @PKG@.RankOps.setRank(u, n, "menu", op[1], op[2], conf);
  if (o.equals("deny")) return @PKG@.RankOps.deny(u, n, "menu", op[1], op[2], conf);
  if (o.equals("undeny")) return @PKG@.RankOps.undeny(u, n, "menu", op[1], op[2]);
  if (o.equals("default")) return @PKG@.RankOps.makeDefault(u, n, "menu", op[1]);
  return "-Unknown action.";
}""")
# every change goes through here: a '?' answer parks the op and shows the Confirm view
M(page, r"""
public String run(String[] op) {
  String r = runOp(op, false);
  if (r == null) r = "+Done.";
  if (r.startsWith("?")) {
    this.pending = op;
    this.backView = this.view;
    this.confirmMsg = r.substring(1);
    this.view = "confirm";
    this.status = "";
    return r;
  }
  this.status = r;
  return r;
}""")
M(page, r"""
public boolean clickNav(String a) {
  if (a.equals("refresh")) { this.status = ""; return true; }
  if (a.equals("prev")) { this.pageNo--; return true; }
  if (a.equals("next")) { this.pageNo++; return true; }
  if (a.equals("tab0")) { this.view = "ranks"; this.pageNo = 0; this.mode = 0; this.hits = null; clearDrafts(); this.status = ""; return true; }
  if (a.equals("tab1")) { this.view = "players"; this.pageNo = 0; this.mode = 0; clearDrafts(); this.status = ""; return true; }
  if (a.equals("tab2") || a.equals("tab3") || a.equals("tab4")) {
    if (!this.view.equals("rank")) return true;
    this.sub = a.equals("tab2") ? 0 : (a.equals("tab3") ? 1 : 2);
    this.pageNo = 0; this.mode = 0; this.hits = null; clearDrafts(); this.status = "";
    return true;
  }
  return false;
}""")
M(page, r"""
public void clickRanks(String a) {
  if (a.equals("create")) {
    String r = run(new String[] { "create", this.d0, this.d1 });
    if (r.startsWith("+")) { String id = this.d0.trim().toLowerCase(); this.d0 = ""; this.d1 = ""; this.view = "rank"; this.rankId = id; this.sub = 0; this.pageNo = 0; clearDrafts(); }
    return;
  }
  int i = idx(a, "up:");
  if (i >= 0) { run(new String[] { "move", key(i), "up" }); return; }
  i = idx(a, "down:");
  if (i >= 0) { run(new String[] { "move", key(i), "down" }); return; }
  i = idx(a, "edit:");
  if (i >= 0) { this.view = "rank"; this.rankId = key(i); this.sub = 0; this.pageNo = 0; this.mode = 0; clearDrafts(); this.status = ""; return; }
  i = idx(a, "del:");
  if (i >= 0) { run(new String[] { "delete", key(i) }); return; }
}""")
# the server's registered permission nodes (every command registers its node) matching every typed word, 20 at most
M(page, r"""
public void search(String verb) {
  String q = this.d0 == null ? "" : this.d0.trim().toLowerCase();
  if (q.length() < 2) { this.status = "=Type at least 2 letters of a node (like fly or admin), then click Search."; return; }
  String[] words = q.split("\\s+");
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.RankPerm.registered().iterator();
  while (it.hasNext() && out.size() < 20) {
    String nd = String.valueOf(it.next());
    String lo = nd.toLowerCase();
    boolean all = true;
    for (int k = 0; k < words.length; k++) if (lo.indexOf(words[k]) < 0) all = false;
    if (all) out.add(nd);
  }
  this.hits = out; this.mode = 1; this.pageNo = 0;
  this.status = out.size() == 0 ? "=No registered node matches " + q + "." : "=" + out.size() + (out.size() == 1 ? " node matches. " : " nodes match. ") + "Click " + verb + " on the one you want.";
}""")
M(page, r"""
public void clickRank(String a) {
  String id = this.rankId;
  if (this.sub == 0) {
    if (a.equals("set0")) { if (run(new String[] { "name", id, this.i0 }).startsWith("+")) this.i0 = ""; return; }
    if (a.equals("set1")) { if (run(new String[] { "prefix", id, this.i1 }).startsWith("+")) this.i1 = ""; return; }
    if (a.equals("clr1")) { this.i1 = ""; run(new String[] { "prefix", id, "none" }); return; }
    if (a.equals("set2")) { if (run(new String[] { "colour", id, this.i2 }).startsWith("+")) this.i2 = ""; return; }
    if (a.equals("clr2")) { this.i2 = ""; run(new String[] { "colour", id, "none" }); return; }
    if (a.equals("staffon")) { run(new String[] { "staff", id, "on" }); return; }
    if (a.equals("staffoff")) { run(new String[] { "staff", id, "off" }); return; }
    if (a.equals("mvup")) { run(new String[] { "move", id, "up" }); return; }
    if (a.equals("mvdown")) { run(new String[] { "move", id, "down" }); return; }
    if (a.equals("mkdef")) { run(new String[] { "default", id }); return; }
    if (a.equals("delrank")) { run(new String[] { "delete", id }); return; }
    return;
  }
  if (this.sub == 1) {
    if (a.equals("grant")) { if (run(new String[] { "grant", id, this.d0 }).startsWith("+")) { this.d0 = ""; this.mode = 0; this.hits = null; } return; }
    if (a.equals("search")) { search("Grant"); return; }
    if (a.equals("hitsback")) { this.mode = 0; this.hits = null; this.pageNo = 0; this.status = ""; return; }
    int i = idx(a, "hit:");
    if (i >= 0) { run(new String[] { "grant", id, key(i) }); return; }
    i = idx(a, "ungrant:");
    if (i >= 0) { run(new String[] { "ungrant", id, key(i) }); return; }
    return;
  }
  if (a.equals("addmember")) { if (run(new String[] { "setrank", this.d0, id }).startsWith("+")) this.d0 = ""; return; }
  if (a.equals("online")) { this.mode = 1; this.pageNo = 0; this.status = ""; return; }
  if (a.equals("onlineback")) { this.mode = 0; this.pageNo = 0; this.status = ""; return; }
  int j = idx(a, "addon:");
  if (j >= 0) { run(new String[] { "setrank", key(j), id }); return; }
  j = idx(a, "unmember:");
  if (j >= 0) { run(new String[] { "setrank", key(j), @PKG@.RankStore.defaultId() }); return; }
}""")
M(page, r"""
public void clickPlayers(String a) {
  if (a.equals("psearch")) { this.pfilter = this.d0 == null ? "" : this.d0.trim(); this.pageNo = 0; this.status = ""; return; }
  if (a.equals("pall")) { this.pfilter = ""; this.d0 = ""; this.pageNo = 0; this.status = ""; return; }
  int i = idx(a, "popen:");
  if (i >= 0) {
    String us = key(i);
    this.target = us;
    this.targetName = @PKG@.RankStore.nameOf(us, us);
    java.util.ArrayList on = @PKG@.RankCfg.online();
    for (int k = 0; k < on.size(); k++) { String[] p = (String[]) on.get(k); if (p[0].equals(us)) this.targetName = p[1]; }
    this.view = "player"; this.pick = -1; this.pageNo = 0; this.mode = 0; this.hits = null; clearDrafts(); this.status = "";
  }
}""")
M(page, r"""
public void clickPlayer(String a) {
  java.util.ArrayList l = @PKG@.RankStore.RANKS;
  if (a.equals("cprev")) { this.pick = this.pick <= 0 ? l.size() - 1 : this.pick - 1; return; }
  if (a.equals("cnext")) { this.pick = this.pick >= l.size() - 1 ? 0 : this.pick + 1; return; }
  if (a.equals("setrank")) {
    if (this.pick < 0 || this.pick >= l.size()) return;
    run(new String[] { "setrank", this.target, ((@PKG@.Rank) l.get(this.pick)).id });
    return;
  }
  if (a.equals("deny")) { if (run(new String[] { "deny", this.target, this.d0 }).startsWith("+")) { this.d0 = ""; this.mode = 0; this.hits = null; } return; }
  if (a.equals("dsearch")) { search("Deny"); return; }
  if (a.equals("dhitsback")) { this.mode = 0; this.hits = null; this.pageNo = 0; this.status = ""; return; }
  int i = idx(a, "dhit:");
  if (i >= 0) { run(new String[] { "deny", this.target, key(i) }); return; }
  i = idx(a, "undeny:");
  if (i >= 0) run(new String[] { "undeny", this.target, key(i) });
}""")
M(page, r"""
public void clickConfirm(String a) {
  if (a.equals("yes") && this.pending != null) {
    String[] op = this.pending;
    this.pending = null;
    this.view = this.backView == null ? "ranks" : this.backView;
    String r = runOp(op, true);
    if (r == null) r = "+Done.";
    if (r.startsWith("?")) r = "-Still needs a confirm - nothing changed.";
    this.status = r;
    if (r.startsWith("+") && op[0].equals("delete")) { this.view = "ranks"; this.pageNo = 0; }
    return;
  }
  this.pending = null;
  this.view = this.backView == null ? "ranks" : this.backView;
  this.status = "=Cancelled - nothing changed.";
}""")
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.RankCfg.warn("could not close the ranks page: " + t); }
}""")
# the Server Setup page (SkyyMenu 0.3) replaces this page directly - no close first
M(page, r"""
public void openSetup() {
  try { @CMGR@.get().handleCommand(this.playerRef, "modconfig ranks"); }
  catch (Throwable t) { this.status = "-Server Setup could not be opened (SkyyMenu 0.3 needed)."; redraw(); }
}""")
M(page, r"""
public void click(String a) {
  if (clickNav(a)) return;
  if (this.view.equals("confirm")) { clickConfirm(a); return; }
  if (this.view.equals("ranks")) { clickRanks(a); return; }
  if (this.view.equals("rank")) { clickRank(a); return; }
  if (this.view.equals("players")) { clickPlayers(a); return; }
  if (this.view.equals("player")) { clickPlayer(a); return; }
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("close")) { closePage(ref, st); return; }
    if (!guard()) { redraw(); return; }
    this.locked = false;
    capture(data);
    if (a.equals("setup")) { openSetup(); return; }
    if (!this.view.equals("confirm")) { this.pending = null; }
    click(a);
    redraw();
  } catch (Throwable t) {
    @PKG@.RankCfg.warn("ranks page click failed: " + t);
    this.status = "-Something went wrong - see the server log.";
    try { redraw(); } catch (Throwable t2) { }
  }
}""")

# ================= commands (admin only: requirePermission on the root AND every subcommand) =================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []
REST = r"""
public static String rest(String input, String word, int skip) {
  if (input == null || word == null) return "";
  String[] t = input.trim().split("\\s+");
  int at = -1;
  for (int i = 0; i < t.length; i++) { if (t[i].equalsIgnoreCase(word) || t[i].equalsIgnoreCase("/" + word)) { at = i; break; } }
  if (at < 0) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = at + 1 + skip; i < t.length; i++) { if (sb.length() > 0) sb.append(' '); sb.append(t[i]); }
  return sb.toString();
}"""
M(ops, REST)


def cmd(clsname, name, desc, args, body, subs=(), aliases=()):
    """One admin AbstractPlayerCommand. args = [(field, argName, argDesc, "STRING" | "GREEDY_STRING")], read into a0, a1, ..."""
    c = mk(clsname, T["APC"])
    for (fld, _an, _ad, _ty) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = ['super("%s", "%s");' % (name, desc), "@ADMIN@"]
    if aliases:
        lines.append("addAliases(new String[] { %s });" % ", ".join('"%s"' % a for a in aliases))
    for (fld, an, ad, ty) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (fld, an, ad, ty))
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    reads = "".join('    String a%d = String.valueOf(ctx.get(this.%s)).trim();\n' % (i, a[0]) for i, a in enumerate(args))
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.RankCfg.warn(\"/" + name + " failed: \" + t);\n"
      "    @PKG@.RankCfg.tellPr(pr, \"-Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


U = "pr.getUuid(), pr.getUsername(), \"command\""
O = "@PKG@.RankOps."
OPEN = r"""@PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { @PKG@.RankCfg.tellPr(pr, "-The ranks editor could not be opened."); return; }
    p.getPageManager().openCustomPage(ref, store, new @PKG@.RankPage(pr, %s));"""
HELP = [
    "=/rank list - every rank, highest first   |   /rank info <rank> - prefix, grants, members",
    "=/rank create <id> <name> - a new rank just above the default (id: a-z and 0-9)   |   /rank delete <rank> - asks first",
    "=/rank name|prefix|colour <rank> <text> - display name, chat prefix like [VIP] (none clears), colour #ff5555 or red",
    "=/rank staff <rank> <on|off>   |   /rank up|down <rank> - move it on the ladder (a rank gets every grant below it)",
    "=/rank grant|ungrant <rank> <node> - permissions   |   /rank default <rank> - shown for players without a rank",
    "=/rank set <player> <rank>   |   /rank clear <player> - hytale:Adventurer is always kept",
    "=/rank who <player> - rank, permission groups, denies   |   /rank deny|undeny <player> <node> - a personal deny",
    "=/rankadmin - the ranks editor page   |   /rankadmin player <player>, /rankadmin reload, /rankadmin sync",
]
M(ops, "public static String[] helpLines() { return new String[] { %s }; }" % ", ".join(jlit(h) for h in HELP))
M(ops, r"""
public static void tellAll(@PR@ pr, String[] lines) {
  for (int i = 0; i < lines.length; i++) @PKG@.RankCfg.tellPr(pr, lines[i]);
}""")
RARG = ("rankArg", "rank", "Rank id or name", "STRING")
PARG = ("playerArg", "player", "Player name or UUID", "STRING")
NARG = ("nodeArg", "node", "Permission node", "STRING")
cmd("RkListCmd", "list", "(admin) every rank, highest first", [], O + "tellAll(pr, " + O + "listLines());")
cmd("RkInfoCmd", "info", "(admin) a rank's prefix, grants and members: /rank info <rank>", [RARG], "@PKG@.RankCfg.tellPr(pr, " + O + "info(a0));")
cmd("RkCreateCmd", "create", "(admin) a new rank just above the default: /rank create <id> <name>",
    [("idArg", "id", "a-z and 0-9, 2-16 characters, like vip", "STRING"), ("nameArg", "name", "Display name (spaces allowed)", "GREEDY_STRING")],
    'String nm = ' + O + 'rest(ctx.getInputString(), "create", 1); if (nm.length() == 0) nm = a1;\n    ' + O + 'reply(pr, "create", ' + O + 'create(' + U + ', a0, nm));')
cmd("RkDeleteCmd", "delete", "(admin) delete a rank - members go back to the default rank (repeat to confirm)", [RARG],
    'String k = "delete|" + a0.toLowerCase();\n    ' + O + 'reply(pr, k, ' + O + 'delete(' + U + ', a0, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkNameCmd", "name", "(admin) a rank's display name: /rank name <rank> <name>",
    [RARG, ("nameArg", "name", "Display name (spaces allowed)", "GREEDY_STRING")],
    'String nm = ' + O + 'rest(ctx.getInputString(), "name", 1); if (nm.length() == 0) nm = a1;\n    ' + O + 'reply(pr, "name", ' + O + 'rename(' + U + ', a0, nm));')
cmd("RkPrefixCmd", "prefix", "(admin) a rank's chat prefix: /rank prefix <rank> <text or none>",
    [RARG, ("textArg", "text", "Prefix like [VIP], or none", "GREEDY_STRING")],
    'String tx = ' + O + 'rest(ctx.getInputString(), "prefix", 1); if (tx.length() == 0) tx = a1;\n    ' + O + 'reply(pr, "prefix", ' + O + 'prefix(' + U + ', a0, tx));')
cmd("RkColourCmd", "colour", "(admin) a rank's prefix colour: /rank colour <rank> <#rrggbb, red, gold... or none>",
    [RARG, ("colourArg", "colour", "#rrggbb, a colour word, or none", "STRING")],
    O + 'reply(pr, "colour", ' + O + 'colour(' + U + ', a0, a1));', aliases=("color",))
cmd("RkStaffCmd", "staff", "(admin) mark a rank as staff: /rank staff <rank> <on|off>",
    [RARG, ("onArg", "on", "on or off", "STRING")],
    'boolean on = @PKG@.RankCfg.bool(a1, false);\n    ' + O + 'reply(pr, "staff", ' + O + 'staff(' + U + ', a0, on));')
cmd("RkUpCmd", "up", "(admin) move a rank one step up the ladder (it gets the grants of the rank it passes)", [RARG],
    'String k = "up|" + a0.toLowerCase();\n    ' + O + 'reply(pr, k, ' + O + 'move(' + U + ', a0, true, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkDownCmd", "down", "(admin) move a rank one step down the ladder", [RARG],
    'String k = "down|" + a0.toLowerCase();\n    ' + O + 'reply(pr, k, ' + O + 'move(' + U + ', a0, false, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkGrantCmd", "grant", "(admin) give a rank a permission node: /rank grant <rank> <node>", [RARG, NARG],
    'String k = "grant|" + a0.toLowerCase() + "|" + a1;\n    ' + O + 'reply(pr, k, ' + O + 'grant(' + U + ', a0, a1, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkUngrantCmd", "ungrant", "(admin) take a permission node from a rank: /rank ungrant <rank> <node>", [RARG, NARG],
    'String k = "ungrant|" + a0.toLowerCase() + "|" + a1;\n    ' + O + 'reply(pr, k, ' + O + 'ungrant(' + U + ', a0, a1, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkSetCmd", "set", "(admin) give a player a rank: /rank set <player> <rank> (hytale:Adventurer is always kept)", [PARG, RARG],
    'String k = "set|" + a0.toLowerCase() + "|" + a1.toLowerCase();\n    ' + O + 'reply(pr, k, ' + O + 'setRank(' + U + ', a0, a1, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkClearCmd", "clear", "(admin) take a player's rank away (back to the default rank)", [PARG],
    'String k = "clear|" + a0.toLowerCase();\n    ' + O + 'reply(pr, k, ' + O + 'setRank(' + U + ', a0, @PKG@.RankStore.defaultId(), ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkWhoCmd", "who", "(admin) a player's rank, permission groups and denies", [PARG], "@PKG@.RankCfg.tellPr(pr, " + O + "who(a0));")
cmd("RkDenyCmd", "deny", "(admin) a personal deny: /rank deny <player> <node> (beats ranks and op)", [PARG, NARG],
    'String k = "deny|" + a0.toLowerCase() + "|" + a1;\n    ' + O + 'reply(pr, k, ' + O + 'deny(' + U + ', a0, a1, ' + O + 'repeat(pr.getUuid(), k)));')
cmd("RkUndenyCmd", "undeny", "(admin) remove a personal deny: /rank undeny <player> <node>", [PARG, NARG],
    O + 'reply(pr, "undeny", ' + O + 'undeny(' + U + ', a0, a1));')
cmd("RkDefaultCmd", "default", "(admin) the rank shown for players without one: /rank default <rank>", [RARG],
    O + 'reply(pr, "default", ' + O + 'makeDefault(' + U + ', a0));')
cmd("RankCmd", "rank", "(admin) ranks: list, info, create, delete, name, prefix, colour, staff, up, down, grant, ungrant, set, clear, who, deny, undeny, default", [],
    O + "tellAll(pr, " + O + "helpLines());",
    subs=("RkListCmd", "RkInfoCmd", "RkCreateCmd", "RkDeleteCmd", "RkNameCmd", "RkPrefixCmd", "RkColourCmd", "RkStaffCmd", "RkUpCmd",
          "RkDownCmd", "RkGrantCmd", "RkUngrantCmd", "RkSetCmd", "RkClearCmd", "RkWhoCmd", "RkDenyCmd", "RkUndenyCmd", "RkDefaultCmd"))
cmd("RkaPlayerCmd", "player", "(admin) the ranks editor on one player: /rankadmin player <player>", [PARG], OPEN % '"player", a0')
cmd("RkaReloadCmd", "reload", "(admin) re-read ranks.properties, players.properties and config.properties, then sync", [],
    "@PKG@.RankCfg.tellPr(pr, " + O + "reload(pr.getUuid(), pr.getUsername()));")
cmd("RkaSyncCmd", "sync", "(admin) make every skyy rank group match the ladder again", [], "@PKG@.RankCfg.tellPr(pr, " + O + "sync());")
cmd("RankAdminCmd", "rankadmin", "(admin) the ranks editor page - /rankadmin player <player>, /rankadmin reload, /rankadmin sync", [],
    OPEN % '"ranks", (String) null', subs=("RkaPlayerCmd", "RkaReloadCmd", "RkaSyncCmd"))

# ================= plugin =================
pl = mk("SkyyRanksPlugin", T["JP"])
C(pl, "public SkyyRanksPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.RankCfg.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyRanks");
  @PKG@.RankCfg.DIR = dir;
  @PKG@.RankCfg.FILE = dir.resolve("config.properties");
  String c = @PKG@.RankCfg.loadCfg(true);
  String s = @PKG@.RankStore.load(dir);
  @PKG@.RankStore.floorDefault();
  @PKG@.RankHooks.warnDefault();
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  getCommandRegistry().registerCommand(new @PKG@.RankCmd());
  getCommandRegistry().registerCommand(new @PKG@.RankAdminCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.RankReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.RankQuit());
  getEventRegistry().registerAsyncGlobal((short) @PKG@.RankCfg.CHAT_PRIORITY, @PCE@.class, new @PKG@.RankChatHook());
  java.util.Map b = @PKG@.RankCfg.bridge();
  b.put("rank:fn:of", new @PKG@.RankOfFn());
  b.put("rank:version", "@VERSION@");
  @PKG@.RankCfg.later(new @PKG@.RankStartTask(), 2000L);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRanks] @VERSION@ ready - /rankadmin (editor page), /rank (chat commands), node skyyranks.admin; " + s + "; " + c + "; ranks are synced with the permission system as soon as it has loaded; data in " + dir);
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.RankStore.flushPlayers(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

ALL = [cfg, ui, rk, perm, st, sav, eng, bulk, hk, ops, fmt, cwr, chk, ofn, stt, join, rdy, quit_, page] + CMDS + [pl]
for c in ALL:
    c.writeFile(OUT)
kit.write(OUT)
print("classes written:", len(ALL) + len(kit.classes), "(%d kit)" % len(kit.classes))

jar = os.path.join(HERE, "SkyyRanks-%s.jar" % VERSION)
man = B.manifest("SkyyRanks", VERSION, "SkyWynn ranks made in game: ranks as permission groups (grants copied up the ladder), members, per-player denies, chat prefix and colour ([Rank] [Title] Name), /rankadmin editor page and /rank commands. Never adds a permission provider; always keeps hytale:Adventurer. Zero dependencies.", PKG + ".SkyyRanksPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
if "--deploy" in sys.argv:
    raise SystemExit("SkyyRanks: --deploy is not supported here - deploys go through tools/deploy_set.py")
