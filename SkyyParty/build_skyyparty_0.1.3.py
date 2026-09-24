"""SkyyParty 0.1.3 - build script (javassist via jpype).
Run:   python build_skyyparty_0.1.3.py            -> SkyyParty/SkyyParty-0.1.3.jar
       (--deploy exists like every Skyy build script, but only deploy with Skyy's OK; tools/deploy_set.py is the normal path)
Derived by COPY + EDIT from build_skyyparty_0.1.2.py (no patch script): same package, same class names for the 0.1.2 commands,
Java source now uses @TOKEN@ substitution (the SkyyMenu 0.1.2 style) instead of f-strings, so braces are plain Java.

0.1.3 (2026-09-24, for Skyy's first 2-player party + guild test; the friend joins as an ordinary hytale:Adventurer player):
  Commands (every command and subcommand calls setPermissionGroups(new String[] { "hytale:Adventurer" }); required args only):
    /party (alias /p)            opens the party PAGE (0.1.2 printed a help line); falls back to the help line in chat
    /party invite <player>       unchanged syntax; the invitee now gets the exact command: "Type /party accept to join (or
                                 /party decline). The invite runs out in 60 s." Expired invites are pruned every 5 s and both
                                 sides are told. A full party (maxSize) refuses the invite and the accept.
    /party accept | leave | list unchanged (list now shows n/max and [leader])
    /party decline               NEW - refuse the pending invite (the inviter is told)
    /party kick <player>         NEW - leader only
    /party promote <player>      NEW - leader only, hands the lead over
    /party disband               NEW - leader only
    /pc <message>                unchanged (GREEDY_STRING)
  /party page (inline, 1240 x 840, root anchor Width/Height only, no underscores in ids, TextButton + EventData, no periodic
    updates - it has a Refresh button): title with n / max, a status line, a pending-invite box with Accept / Decline (when you
    are not in a party and have an open invite), one big row per member (name, "(you)", Party leader / Member, Health, Stamina
    and Mana as "cur / max" text + a bar, from the party:stats bridge value, Online / Offline + where they are: Hub / Your island
    / <name>'s island (their own or anyone else's) / world name, "(with you)" when in your world), leader-only Promote + Kick buttons on the
    other members' rows (not built at all for members), an Invite row (TextField + Invite button, the SkyySacks 0.7.3/0.7.4
    craft search pattern verified in game 2026-09-24: Validating (Enter, no lock) or Activating on the button, EventData
    "a"="invite" + "@InviteName" = "#SkyyPInvName.Value"; the name is matched exactly (ignoring case) first, then by prefix),
    Leave party (members) / Disband (leader only) / Refresh / Close. Every click re-checks everything (leader, membership) at
    click time through the same PartyStore functions the commands use.
  Party store: a party is one Party object (volatile ArrayList, leader at index 0, then join order) that is REPLACED, never
    mutated, under the PartyStore lock, so readers on any thread (bridge Function, pages, ticking system) always see one
    consistent snapshot. Leader leaving or disconnecting still promotes the next member (join order); a party that drops to one
    player is disbanded (0.1.2 rule). Still in memory only, per PLAYER (not per profile - tools/PROFILES-CONTRACT.md rule 6).
  Config: <world>/mods/Skyy_SkyyParty/config.properties (written on first start, tmp + atomic rename): maxSize=5 (2-10),
    inviteSeconds=60 (15-600). Read once at server start (MAX / INVITE_MS are volatile: set in setup(), read on every thread).
  Review fixes (2026-09-24, same version - 0.1.3 was never deployed): the page reads party:stats with split(",", -1) and needs only
    the 6 numbers, so an empty world name no longer hides a member's Health / Stamina / Mana; a member standing on their own island
    shows "<name>'s island" (was the literal "Their island"); "(with you)" needs a non-empty world name; config written atomically.
  FIXED BRIDGE CONTRACT (System.getProperties().get("skyy.bridge") ConcurrentHashMap, per PLAYER):
    "party:fn:members"  java.util.function.Function, apply(java.util.UUID viewer) -> String[] of member UUID strings, leader
                        first, then join order; an empty String[0] when not in a party (also for a null / bad argument).
    "party:leader:<uuid>" leader UUID string, for every member; removed when the player is not in a party.
    "party:name:<uuid>" the player's username; published for every online player about once a second (ticking system) and at
                        every party action; kept after they leave (offline members' names stay readable).
    "party:stats:<uuid>" "hp,maxHp,stamina,maxStamina,mana,maxMana,worldName" (ints, Math.round), refreshed about every 1 s
                        (wall clock) on THAT member's own world thread by PartyStats (an EntityTickingSystem on Player
                        entities, one registerSystem for the class; EntityTickingSystem.isParallel() returns false in
                        HytaleServer.jar, so ticks run on the world thread), only while they are in a party. Commas in the
                        world name are replaced by spaces. Removed on leave / kick / disband / disconnect (the store removes
                        it after updating membership and the ticker re-checks membership after every put, so a tick racing
                        a leave can never leave a stale value behind).
    All party:* keys are removed in shutdown().
  Engine facts used (HytaleServer.jar, tools/dev reflect.py / bcfull.py, 2026-09-24):
    PlayerRef.isValid() = entity ref != null || holder != null, so a player in a cross-world transfer still counts as online.
    Universe.getPlayerByUsername(String, NameMatching) with NameMatching EXACT_IGNORE_CASE / STARTS_WITH_IGNORE_CASE.
    Store.getExternalData() -> EntityStore.getWorld().getName() inside the ticking system.
    PageManager.setPage(ref, store, Page.None) closes the page (SkyyMenu 0.1.2 close path, verified in game).
  Threads: commands and page clicks run on the clicking player's world thread and only touch PartyStore (synchronized static
    methods, no calls out while locked), the bridge map and PlayerRef.sendMessage (the 0.1.2 cross-player broadcast path).
    The 5 s invite pruner runs on HytaleServer.SCHEDULED_EXECUTOR and only touches INVITES + chat. Nothing reads another
    player's components: other members' stats come from the bridge value their own world thread wrote.

0.1.2: ordinary players can use the party commands. Every command (/party alias /p, /party invite|accept|leave|list, /pc)
  calls setPermissionGroups(new String[] { "hytale:Adventurer" }) (vanilla /help /who /ping pattern, same as SkyyEssentials 0.1).
  Engine (HytaleServer.jar bytecode, 2026-09-23): AbstractCommand.setOwner() gives every command without requirePermission() an
  auto node "<plugin base permission>.command.party" (subcommands: that id + ".invite" etc., version included), which default
  "hytale:Adventurer" players never held, so only "*" admins could run them. putRecursivePermissionGroups() walks subcommands,
  CommandManager.createVirtualPermissionGroups() collects it, PermissionsModule.start() -> refreshVirtualGroups() runs after
  every plugin setup(). Subcommand hasPermission(): own node, then (only when it has no groups of its own) the parent node.
  Positional arguments already work and are unchanged: "/party invite <player>" = subcommand dispatch on the first token
  (checkForExecutingSubcommands -> convertToSubCommand) then 1 token == 1 required arg; "/party" alone runs PartyCmd.execute
  (not an AbstractCommandCollection, 0 tokens == 0 required); "/pc <message with spaces>" = GREEDY_STRING, which sets
  allowsExtraArguments and passes the raw tail (extractGreedyRawTail) as one value.
Fixes vs 0.1 (code review 2026-09-22): synchronized party store (no lost members on concurrent accept),
accept refuses when already in a party, leader leaving promotes the next member instead of disbanding,
players are removed from their party on disconnect, expired invites are pruned, direct Universe.getPlayer
lookup, no exception text leaked to chat.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.3"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.party"
T = {
    "PKG": PKG,
    "JP":  "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":  "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST":  "com.hypixel.hytale.component.Store",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":  "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":  "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PGM": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "PGE": "com.hypixel.hytale.protocol.packets.interface_.Page",
    "NMT": "com.hypixel.hytale.server.core.NameMatching",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":  "com.hypixel.hytale.component.CommandBuffer",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "CRP": "com.hypixel.hytale.component.ComponentRegistryProxy",
    "ES":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "PBS": "com.hypixel.hytale.server.core.plugin.PluginBase",
    # every party command is player-facing: grant its (auto-generated) permission node to the default player group
    "ADV": 'setPermissionGroups(new String[] { "hytale:Adventurer" });',
}
TOK = re.compile(r"@([A-Z]+)@")


def sub(src):
    out = TOK.sub(lambda m: T[m.group(1)] if m.group(1) in T else m.group(0), src)
    left = TOK.findall(out)
    if left:
        raise SystemExit("unknown @TOKEN@ in Java source: %s" % left)
    return out


def M(cls, src):
    cls.addMethod(CtNewMethod.make(sub(src), cls))


def C(cls, src):
    cls.addConstructor(CtNewConstructor.make(sub(src), cls))


def F(cls, src):
    cls.addField(CtField.make(sub(src), cls))


for c, m in ((T["UNI"], "getPlayer"), (T["UNI"], "getPlayerByUsername"), (T["UNI"], "getDefaultWorld"), (T["PDE"], "getPlayerRef"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (T["PBS"], "shutdown"), (T["PBS"], "getEntityStoreRegistry"), (T["PBS"], "getDataDirectory"),
             (T["APC"], "setPermissionGroups"), (T["ATY"], "PLAYER_REF"), (T["ATY"], "GREEDY_STRING"), (T["PR"], "isValid"),
             (T["PR"], "getUsername"), (T["NMT"], "EXACT_IGNORE_CASE"), (T["NMT"], "STARTS_WITH_IGNORE_CASE"),
             (T["PAGE"], "rebuild"), (T["PGM"], "openCustomPage"), (T["PGM"], "setPage"), (T["PGE"], "None"), (T["PLA"], "getPageManager"),
             (T["PLA"], "isWaitingForClientReady"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"),
             (T["EVD"], "of"), (T["EVD"], "append"), (T["BT"], "Activating"), (T["BT"], "Validating"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESV"], "get"), (T["ESV"], "getMax"), (T["DST"], "getHealth"),
             (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["ETS"], "tick"), (T["ACH"], "getReferenceTo"), (T["CB"], "getComponent"),
             (T["CRP"], "registerSystem"), (T["ST"], "getExternalData"), (T["ES"], "getWorld"), (T["WLD"], "getName")):
    B.probe(pool, c, m)

pty  = pool.makeClass(PKG + ".Party")
ps   = pool.makeClass(PKG + ".PartyStore")
fn   = pool.makeClass(PKG + ".PartyFn")
sts  = pool.makeClass(PKG + ".PartyStats", pool.get(T["ETS"]))
page = pool.makeClass(PKG + ".PartyPage", pool.get(T["PAGE"]))
inv  = pool.makeClass(PKG + ".InviteCmd", pool.get(T["APC"]))
acc  = pool.makeClass(PKG + ".AcceptCmd", pool.get(T["APC"]))
dec  = pool.makeClass(PKG + ".DeclineCmd", pool.get(T["APC"]))
lev  = pool.makeClass(PKG + ".LeaveCmd", pool.get(T["APC"]))
lst  = pool.makeClass(PKG + ".ListCmd", pool.get(T["APC"]))
kck  = pool.makeClass(PKG + ".KickCmd", pool.get(T["APC"]))
pro  = pool.makeClass(PKG + ".PromoteCmd", pool.get(T["APC"]))
dis  = pool.makeClass(PKG + ".DisbandCmd", pool.get(T["APC"]))
pc   = pool.makeClass(PKG + ".PartyChatCmd", pool.get(T["APC"]))
root = pool.makeClass(PKG + ".PartyCmd", pool.get(T["APC"]))
quit_ = pool.makeClass(PKG + ".PartyQuit")
prune = pool.makeClass(PKG + ".PartyPrune")
pl   = pool.makeClass(PKG + ".SkyyPartyPlugin", pool.get(T["JP"]))

# ================= Party: one party = one immutable-by-convention member list (leader first), swapped under the store lock =================
F(pty, "public volatile java.util.ArrayList list;")
C(pty, "public Party(java.util.ArrayList l) { this.list = l; }")

# ================= PartyStore (in-memory, per player; THE data feed for the HUD party widget + future map) =================
F(ps, "public static @LOG@ LOG;")
F(ps, "public static final java.util.concurrent.ConcurrentHashMap PARTY_OF = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> Party
F(ps, "public static final java.util.concurrent.ConcurrentHashMap INVITES = new java.util.concurrent.ConcurrentHashMap();")   # invitee uuid -> Object[]{inviter uuid, Long expiryMs, String inviterName}
F(ps, "public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();")     # uuid -> long[]{last stats publish ms}
F(ps, "public static volatile int MAX = 5;")          # written once in setup() (loadConfig), read from every thread
F(ps, "public static volatile long INVITE_MS = 60000L;")
M(ps, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyParty] " + msg); } catch (Throwable t) { }
}""")
# the SkyyCoins / SkyyProfiles bridge helper, verbatim (same monitor, so no mod can create a second map)
M(ps, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(ps, r"""
public static java.util.ArrayList listOf(java.util.UUID u) {
  if (u == null) return null;
  Object o = PARTY_OF.get(u);
  if (o == null) return null;
  java.util.ArrayList l = ((@PKG@.Party) o).list;
  if (l == null || l.isEmpty() || !l.contains(u)) return null;
  return l;
}""")
M(ps, r"""
public static java.util.UUID leaderOf(java.util.UUID u) {
  java.util.ArrayList l = listOf(u);
  return l == null ? null : (java.util.UUID) l.get(0);
}""")
M(ps, r"""
public static @PR@ online(java.util.UUID u) {
  if (u == null) return null;
  try {
    @PR@ p = @UNI@.get().getPlayer(u);
    return (p != null && p.isValid()) ? p : null;
  } catch (Throwable t) { return null; }
}""")
M(ps, r"""
public static void pubName(@PR@ p) {
  try {
    if (p == null) return;
    String n = p.getUsername();
    if (n == null || n.length() == 0) return;
    java.util.Map b = bridge();
    String k = "party:name:" + p.getUuid().toString();
    if (!n.equals(b.get(k))) b.put(k, n);
  } catch (Throwable t) { }
}""")
M(ps, r"""
public static String nameOf(java.util.UUID u) {
  if (u == null) return "someone";
  @PR@ p = online(u);
  if (p != null && p.getUsername() != null) return p.getUsername();
  try {
    Object n = bridge().get("party:name:" + u.toString());
    if (n != null) return n.toString();
  } catch (Throwable t) { }
  return "someone";
}""")
M(ps, r"""
public static String cut(String s, int max) {
  if (s == null) return "";
  if (s.length() <= max) return s;
  return s.substring(0, max) + "...";
}""")
M(ps, r"""
public static void publishParty(java.util.ArrayList l) {
  if (l == null || l.isEmpty()) return;
  java.util.Map b = bridge();
  String lead = l.get(0).toString();
  for (int i = 0; i < l.size(); i++) b.put("party:leader:" + l.get(i).toString(), lead);
}""")
M(ps, r"""
public static void unpublish(java.util.UUID u) {
  if (u == null) return;
  java.util.Map b = bridge();
  b.remove("party:leader:" + u.toString());
  b.remove("party:stats:" + u.toString());
}""")
# ---- the only methods that change parties (synchronized, never call out except the bridge map) ----
# 0 = joined, 1 = member already in a party, 2 = party full
M(ps, r"""
public static synchronized int join(java.util.UUID inviter, java.util.UUID member) {
  if (listOf(member) != null) return 1;
  java.util.ArrayList cur = listOf(inviter);
  @PKG@.Party pt;
  java.util.ArrayList nl;
  if (cur == null) {
    nl = new java.util.ArrayList();
    nl.add(inviter);
    pt = new @PKG@.Party(nl);
  } else {
    pt = (@PKG@.Party) PARTY_OF.get(inviter);
    nl = new java.util.ArrayList(cur);
  }
  if (nl.size() >= MAX) return 2;
  nl.add(member);
  pt.list = nl;
  PARTY_OF.put(inviter, pt);
  PARTY_OF.put(member, pt);
  publishParty(nl);
  return 0;
}""")
# null = was not in a party; else { ArrayList before, ArrayList after (the others, new leader first), Boolean disbanded }
M(ps, r"""
public static synchronized Object[] removeMember(java.util.UUID m) {
  java.util.ArrayList before = listOf(m);
  if (before == null) {
    PARTY_OF.remove(m);
    unpublish(m);
    return null;
  }
  @PKG@.Party pt = (@PKG@.Party) PARTY_OF.get(m);
  java.util.ArrayList after = new java.util.ArrayList(before);
  after.remove(m);
  PARTY_OF.remove(m);
  unpublish(m);
  if (after.size() <= 1) {
    for (int i = 0; i < after.size(); i++) {
      java.util.UUID o = (java.util.UUID) after.get(i);
      PARTY_OF.remove(o);
      unpublish(o);
    }
    pt.list = new java.util.ArrayList();
    return new Object[] { before, after, Boolean.TRUE };
  }
  pt.list = after;
  publishParty(after);
  return new Object[] { before, after, Boolean.FALSE };
}""")
M(ps, r"""
public static synchronized Object[] kickM(java.util.UUID leader, java.util.UUID target) {
  java.util.ArrayList l = listOf(leader);
  if (l == null) return new Object[] { "none" };
  if (!leader.equals(l.get(0))) return new Object[] { "notleader" };
  if (leader.equals(target)) return new Object[] { "self" };
  if (!l.contains(target)) return new Object[] { "notmember" };
  Object[] r = removeMember(target);
  if (r == null) return new Object[] { "notmember" };
  return new Object[] { "ok", r[0], r[1], r[2] };
}""")
M(ps, r"""
public static synchronized String promoteM(java.util.UUID leader, java.util.UUID target) {
  java.util.ArrayList l = listOf(leader);
  if (l == null) return "none";
  if (!leader.equals(l.get(0))) return "notleader";
  if (leader.equals(target)) return "self";
  if (!l.contains(target)) return "notmember";
  java.util.ArrayList nl = new java.util.ArrayList();
  nl.add(target);
  for (int i = 0; i < l.size(); i++) if (!target.equals(l.get(i))) nl.add(l.get(i));
  ((@PKG@.Party) PARTY_OF.get(leader)).list = nl;
  publishParty(nl);
  return "ok";
}""")
M(ps, r"""
public static synchronized Object[] disbandM(java.util.UUID leader) {
  java.util.ArrayList l = listOf(leader);
  if (l == null) return new Object[] { "none", null };
  if (!leader.equals(l.get(0))) return new Object[] { "notleader", null };
  @PKG@.Party pt = (@PKG@.Party) PARTY_OF.get(leader);
  for (int i = 0; i < l.size(); i++) {
    java.util.UUID o = (java.util.UUID) l.get(i);
    PARTY_OF.remove(o);
    unpublish(o);
  }
  pt.list = new java.util.ArrayList();
  return new Object[] { "ok", l };
}""")
# ---- chat helpers ----
M(ps, r"""
public static void send(@PR@ p, String msg) {
  try { if (p != null) p.sendMessage(@MSG@.raw(msg)); } catch (Throwable t) { }
}""")
M(ps, r"""
public static void tell(java.util.UUID u, String msg) {
  send(online(u), msg);
}""")
M(ps, r"""
public static void broadcastTo(java.util.List l, String msg, java.util.UUID skip1, java.util.UUID skip2) {
  if (l == null) return;
  for (int i = 0; i < l.size(); i++) {
    java.util.UUID u = (java.util.UUID) l.get(i);
    if (u.equals(skip1) || u.equals(skip2)) continue;
    tell(u, msg);
  }
}""")
M(ps, r"""
public static int inviteSecs() {
  return (int) (INVITE_MS / 1000L);
}""")
M(ps, r"""
public static String helpText() {
  return "Party: /party (opens the party page) - /party invite <player> - /party accept - /party decline - /party leave - /party list - /party kick <player> - /party promote <player> - /party disband - /pc <message>";
}""")
# a typed player name from the page TextField: letters, digits and underscores only (Hytale usernames), max 32
M(ps, r"""
public static String cleanName(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 32; i++) {
    char c = s.charAt(i);
    if (Character.isLetterOrDigit(c) || c == '_') sb.append(c);
  }
  return sb.toString();
}""")
M(ps, r"""
public static @PR@ findOnline(String name) {
  if (name == null || name.length() == 0) return null;
  @PR@ p = null;
  try { p = @UNI@.get().getPlayerByUsername(name, @NMT@.EXACT_IGNORE_CASE); } catch (Throwable t) { p = null; }
  if (p == null) {
    try { p = @UNI@.get().getPlayerByUsername(name, @NMT@.STARTS_WITH_IGNORE_CASE); } catch (Throwable t) { p = null; }
  }
  return (p != null && p.isValid()) ? p : null;
}""")
# ---- actions (commands AND page buttons): each returns the line for the acting player; others get [Party] chat lines ----
M(ps, r"""
public static String invite(@PR@ me, @PR@ target) {
  if (target == null || !target.isValid()) return "That player is not online.";
  java.util.UUID mu = me.getUuid();
  java.util.UUID tu = target.getUuid();
  if (tu.equals(mu)) return "You can't invite yourself.";
  pubName(me);
  pubName(target);
  String tn = target.getUsername();
  if (listOf(tu) != null) return tn + " is already in a party.";
  java.util.ArrayList mine = listOf(mu);
  int n = mine == null ? 1 : mine.size();
  if (n >= MAX) return "Your party is full (" + n + "/" + MAX + ").";
  long now = System.currentTimeMillis();
  Object[] old = (Object[]) INVITES.get(tu);
  if (old != null && mu.equals(old[0]) && ((Long) old[1]).longValue() > now) {
    long left = (((Long) old[1]).longValue() - now + 999L) / 1000L;
    return "You already invited " + tn + " - that invite runs out in " + left + " s.";
  }
  INVITES.put(tu, new Object[] { mu, Long.valueOf(now + INVITE_MS), me.getUsername() });
  int s = inviteSecs();
  send(target, "[Party] " + me.getUsername() + " invited you to their party! Type /party accept to join (or /party decline). The invite runs out in " + s + " s.");
  if (mine != null) broadcastTo(mine, "[Party] " + me.getUsername() + " invited " + tn + " to the party.", mu, null);
  return "Invited " + tn + " to your party. They have " + s + " s to type /party accept.";
}""")
M(ps, r"""
public static String accept(@PR@ me) {
  java.util.UUID mu = me.getUuid();
  pubName(me);
  if (listOf(mu) != null) return "You're already in a party. Leave it first with /party leave.";
  Object[] inv = (Object[]) INVITES.remove(mu);
  if (inv == null || ((Long) inv[1]).longValue() < System.currentTimeMillis()) return "You have no party invite right now (invites run out after " + inviteSecs() + " s).";
  java.util.UUID inviter = (java.util.UUID) inv[0];
  if (online(inviter) == null) return "The player who invited you is no longer online.";
  int r = join(inviter, mu);
  if (r == 1) return "You're already in a party.";
  if (r == 2) return "That party is full (" + MAX + " players).";
  java.util.ArrayList l = listOf(mu);
  if (l == null) return "Could not join the party.";
  broadcastTo(l, "[Party] " + me.getUsername() + " joined the party! (" + l.size() + "/" + MAX + ")", mu, null);
  return "You joined " + nameOf((java.util.UUID) l.get(0)) + "'s party! Open /party to see it. Party chat: /pc <message>";
}""")
M(ps, r"""
public static String decline(@PR@ me) {
  Object[] inv = (Object[]) INVITES.remove(me.getUuid());
  if (inv == null || ((Long) inv[1]).longValue() < System.currentTimeMillis()) return "You have no party invite right now.";
  tell((java.util.UUID) inv[0], "[Party] " + me.getUsername() + " declined your party invite.");
  return "Declined the party invite from " + String.valueOf(inv[2]) + ".";
}""")
# r = removeMember() result; stayMsg / goneMsg go to the remaining members (never to the one who left)
M(ps, r"""
public static void announceLeave(Object[] r, java.util.UUID mu, String stayMsg, String goneMsg) {
  java.util.ArrayList before = (java.util.ArrayList) r[0];
  java.util.ArrayList after = (java.util.ArrayList) r[1];
  boolean gone = ((Boolean) r[2]).booleanValue();
  if (gone) { broadcastTo(after, goneMsg, mu, null); return; }
  broadcastTo(after, stayMsg, mu, null);
  java.util.UUID oldLead = (java.util.UUID) before.get(0);
  java.util.UUID newLead = (java.util.UUID) after.get(0);
  if (!newLead.equals(oldLead)) broadcastTo(after, "[Party] " + nameOf(newLead) + " is now the party leader.", null, null);
}""")
M(ps, r"""
public static String leave(@PR@ me) {
  java.util.UUID mu = me.getUuid();
  Object[] r = removeMember(mu);
  if (r == null) return "You're not in a party.";
  String n = me.getUsername();
  announceLeave(r, mu, "[Party] " + n + " left the party.", "[Party] " + n + " left. The party has been disbanded.");
  return "You left the party.";
}""")
M(ps, r"""
public static String kick(@PR@ me, java.util.UUID target) {
  if (target == null) return "That player is not in your party.";
  java.util.UUID mu = me.getUuid();
  String tn = nameOf(target);
  Object[] r = kickM(mu, target);
  String code = (String) r[0];
  if ("none".equals(code)) return "You're not in a party.";
  if ("notleader".equals(code)) return "Only the party leader can kick members.";
  if ("self".equals(code)) return "You can't kick yourself - use /party leave or /party disband.";
  if (!"ok".equals(code)) return tn + " is not in your party.";
  java.util.ArrayList after = (java.util.ArrayList) r[2];
  boolean gone = ((Boolean) r[3]).booleanValue();
  tell(target, "[Party] You were kicked from the party by " + me.getUsername() + ".");
  if (gone) return "Kicked " + tn + ". Nobody else is left, so the party is disbanded.";
  broadcastTo(after, "[Party] " + me.getUsername() + " kicked " + tn + " from the party.", mu, null);
  return "Kicked " + tn + " from the party.";
}""")
M(ps, r"""
public static String promote(@PR@ me, java.util.UUID target) {
  if (target == null) return "That player is not in your party.";
  java.util.UUID mu = me.getUuid();
  String tn = nameOf(target);
  String code = promoteM(mu, target);
  if ("none".equals(code)) return "You're not in a party.";
  if ("notleader".equals(code)) return "Only the party leader can promote members.";
  if ("self".equals(code)) return "You are already the party leader.";
  if (!"ok".equals(code)) return tn + " is not in your party.";
  tell(target, "[Party] " + me.getUsername() + " made you the party leader.");
  broadcastTo(listOf(target), "[Party] " + tn + " is now the party leader (promoted by " + me.getUsername() + ").", mu, target);
  return tn + " is now the party leader.";
}""")
M(ps, r"""
public static String disband(@PR@ me) {
  java.util.UUID mu = me.getUuid();
  Object[] r = disbandM(mu);
  String code = (String) r[0];
  if ("none".equals(code)) return "You're not in a party.";
  if (!"ok".equals(code)) return "Only the party leader can disband the party. Use /party leave to leave it.";
  broadcastTo((java.util.List) r[1], "[Party] " + me.getUsername() + " disbanded the party.", mu, null);
  return "You disbanded the party.";
}""")
M(ps, r"""
public static String listText(@PR@ me) {
  java.util.ArrayList l = listOf(me.getUuid());
  if (l == null) return "You're not in a party. /party invite <player> to start one, or /party to open the party page.";
  StringBuilder sb = new StringBuilder("Party (" + l.size() + "/" + MAX + "): ");
  for (int i = 0; i < l.size(); i++) {
    java.util.UUID u = (java.util.UUID) l.get(i);
    if (i > 0) sb.append(", ");
    sb.append(nameOf(u));
    if (online(u) == null) sb.append(" (offline)");
    if (i == 0) sb.append(" [leader]");
  }
  return sb.toString();
}""")
M(ps, r"""
public static void pruneInvites() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = INVITES.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (v == null || ((Long) v[1]).longValue() >= now) continue;
    if (!INVITES.remove(e.getKey(), v)) continue;
    java.util.UUID invitee = (java.util.UUID) e.getKey();
    tell((java.util.UUID) v[0], "[Party] Your party invite to " + nameOf(invitee) + " ran out.");
    tell(invitee, "[Party] The party invite from " + String.valueOf(v[2]) + " ran out.");
  }
}""")
M(ps, r"""
public static void onQuit(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String name = pr.getUsername();
  CLOCK.remove(u);
  Object[] mine = (Object[]) INVITES.remove(u);
  if (mine != null) tell((java.util.UUID) mine[0], "[Party] " + name + " left the game - your party invite was cancelled.");
  java.util.Iterator it = INVITES.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] v = (Object[]) e.getValue();
    if (v == null || !u.equals(v[0])) continue;
    if (INVITES.remove(e.getKey(), v)) tell((java.util.UUID) e.getKey(), "[Party] " + name + " left the game - their party invite was cancelled.");
  }
  Object[] r = removeMember(u);
  if (r != null) announceLeave(r, u, "[Party] " + name + " disconnected and left the party.", "[Party] " + name + " disconnected. The party has been disbanded.");
}""")
M(ps, r"""
public static int intProp(java.util.Properties p, String key, int def, int lo, int hi) {
  int v = def;
  try { v = Integer.parseInt(p.getProperty(key, String.valueOf(def)).trim()); } catch (Throwable t) { warn("config.properties: bad " + key + " - using " + def); v = def; }
  if (v < lo) v = lo;
  if (v > hi) v = hi;
  return v;
}""")
M(ps, r"""
public static void loadConfig(java.nio.file.Path dir) {
  try {
    java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path f = dir.resolve("config.properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      String nl = System.lineSeparator();
      String txt = "# SkyyParty settings - read when the server starts" + nl
        + "# maxSize = most players in one party (2-10)" + nl + "maxSize=5" + nl
        + "# inviteSeconds = how long a party invite stays open (15-600)" + nl + "inviteSeconds=60" + nl;
      // tmp + atomic rename (SkyyProfiles / SkyySacks pattern): a crash mid-write never leaves a half-written config behind
      java.nio.file.Path tmp = dir.resolve("config.properties.tmp");
      java.nio.file.Files.write(tmp, txt.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    MAX = intProp(p, "maxSize", 5, 2, 10);
    INVITE_MS = (long) intProp(p, "inviteSeconds", 60, 15, 600) * 1000L;
  } catch (Throwable t) {
    warn("could not read config.properties - using maxSize=" + MAX + " inviteSeconds=" + (INVITE_MS / 1000L) + ": " + t);
  }
}""")

# ================= PartyFn: bridge "party:fn:members" =================
fn.addInterface(pool.get("java.util.function.Function"))
C(fn, "public PartyFn() { }")
M(fn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = null;
    if (o instanceof java.util.UUID) u = (java.util.UUID) o;
    else if (o != null) u = java.util.UUID.fromString(o.toString());
    java.util.ArrayList l = @PKG@.PartyStore.listOf(u);
    if (l == null) return new String[0];
    String[] out = new String[l.size()];
    for (int i = 0; i < out.length; i++) out[i] = l.get(i).toString();
    return out;
  } catch (Throwable t) { return new String[0]; }
}""")

# ================= PartyStats: party:stats:<uuid> on the member's OWN world thread (EntityTickingSystem on Player) =================
# AccEffects (SkyyAccessories 0.2+) pattern: store.getComponent for Player / PlayerRef, cb.getComponent for EntityStatMap.
# Throttled by wall clock (1 s per player), so the dt unit does not matter.
F(sts, "public static boolean FAILED_ONCE = false;")
C(sts, "public PartyStats() { super(); }")
M(sts, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(sts, r"""
public static int val(@ESM@ m, int idx, boolean max) {
  if (m == null || idx < 0) return 0;
  @ESV@ v = m.get(idx);
  if (v == null) return 0;
  return max ? Math.round(v.getMax()) : Math.round(v.get());
}""")
M(sts, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    long now = System.currentTimeMillis();
    long[] c = (long[]) @PKG@.PartyStore.CLOCK.get(u);
    if (c == null) { c = new long[] { 0L }; @PKG@.PartyStore.CLOCK.put(u, c); }
    if (now - c[0] < 1000L) return;
    c[0] = now;
    @PKG@.PartyStore.pubName(pr);
    if (@PKG@.PartyStore.listOf(u) == null) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
    int hi = @DST@.getHealth();
    int si = @DST@.getStamina();
    int mi = @DST@.getMana();
    String w = "";
    try {
      Object ex = store.getExternalData();
      if (ex instanceof @ES@) {
        @WLD@ wd = ((@ES@) ex).getWorld();
        if (wd != null && wd.getName() != null) w = wd.getName().replace(',', ' ');
      }
    } catch (Throwable t) { w = ""; }
    String s = "" + val(m, hi, false) + "," + val(m, hi, true) + "," + val(m, si, false) + "," + val(m, si, true) + "," + val(m, mi, false) + "," + val(m, mi, true) + "," + w;
    java.util.Map b = @PKG@.PartyStore.bridge();
    String key = "party:stats:" + u.toString();
    b.put(key, s);
    // a leave / kick / disband / disconnect may have run on another thread since the check above: never leave a stale value
    if (@PKG@.PartyStore.listOf(u) == null) b.remove(key);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.PartyStore.warn("party stats tick failed (logged once): " + t); }
  }
}""")

# ================= PartyPage: /party (inline; no periodic updates - Refresh button) =================
F(page, "public String info;")
C(page, r"""
public PartyPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.info = "";
}""")
# SkyySacks 0.7.3 jsonStr, verbatim: one string value out of the page event JSON ("@InviteName": "..."), escapes handled
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
public static java.util.UUID parseUuid(String s) {
  try { return java.util.UUID.fromString(s.trim()); } catch (Throwable t) { return null; }
}""")
M(page, r"""
public static String style(String bg, String hov, String prs, String txt, int fs) {
  String l = "LabelStyle: (FontSize: " + fs + ", TextColor: " + txt + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + l + "), Hovered: (Background: " + hov + ", " + l + "), Pressed: (Background: " + prs + ", " + l + "));";
}""")
# "hp,maxHp,stamina,maxStamina,mana,maxMana,worldName" -> the 6 numbers (null when missing / malformed)
M(page, r"""
public static int[] nums(String s) {
  if (s == null) return null;
  String[] p = s.split(",", -1);
  if (p.length < 6) return null;
  int[] out = new int[6];
  try {
    for (int i = 0; i < 6; i++) out[i] = Integer.parseInt(p[i].trim());
  } catch (Throwable t) { return null; }
  return out;
}""")
M(page, r"""
public static String worldPart(String s) {
  if (s == null) return null;
  int c = 0;
  for (int i = 0; i < s.length(); i++) {
    if (s.charAt(i) == ',') {
      c++;
      if (c == 6) return s.substring(i + 1);
    }
  }
  return null;
}""")
M(page, r"""
public static String stats(java.util.UUID u) {
  try {
    Object o = @PKG@.PartyStore.bridge().get("party:stats:" + u.toString());
    return o == null ? null : o.toString();
  } catch (Throwable t) { return null; }
}""")
# friendly place name: SkyyIslands worlds are skyy-island-<uuid> or skyy-island-<uuid>-pN (tools/PROFILES-CONTRACT.md)
M(page, r"""
public static String where(String w, java.util.UUID member, java.util.UUID viewer) {
  if (w == null || w.length() == 0) return "somewhere";
  if (w.startsWith("skyy-island-")) {
    String k = w.substring(12);
    String owner = k.length() >= 36 ? k.substring(0, 36) : k;
    if (owner.equals(viewer.toString())) return "Your island";
    if (owner.equals(member.toString())) return @PKG@.PartyStore.cut(@PKG@.PartyStore.nameOf(member), 14) + "'s island";
    try {
      Object n = @PKG@.PartyStore.bridge().get("party:name:" + owner);
      if (n != null) return @PKG@.PartyStore.cut(n.toString(), 14) + "'s island";
    } catch (Throwable t) { }
    return "An island";
  }
  try {
    @WLD@ d = @UNI@.get().getDefaultWorld();
    if (d != null && w.equals(d.getName())) return "Hub";
  } catch (Throwable t) { }
  return @PKG@.PartyStore.cut(w, 20);
}""")
# one stat column: "Health  18 / 20" + a two-part bar (fill + rest Groups in a Left layout; both proven patterns)
M(page, r"""
public static void statCol(@UCB@ b, String parent, String id, String text, int cur, int max, String fill, String rest, int ch, boolean compact) {
  b.appendInline(parent, "Group #" + id + "C { Anchor: (Width: 190, Height: " + ch + "); LayoutMode: Top; }");
  int th = compact ? ch - 12 : 38;
  int bh = compact ? 8 : 14;
  b.appendInline("#" + id + "C", "Label #" + id + "T { Anchor: (Height: " + th + "); Text: \"\"; Style: (FontSize: " + (compact ? 14 : 18) + ", RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.set("#" + id + "T.Text", text);
  b.appendInline("#" + id + "C", "Group #" + id + "B { Anchor: (Height: " + bh + "); LayoutMode: Left; }");
  int w = 170;
  int f = 0;
  if (max > 0) {
    int c = cur < 0 ? 0 : (cur > max ? max : cur);
    f = (int) (((long) w * (long) c) / (long) max);
  }
  if (f > 0) b.appendInline("#" + id + "B", "Group { Anchor: (Width: " + f + ", Height: " + bh + "); Background: " + fill + "; }");
  if (w - f > 0) b.appendInline("#" + id + "B", "Group { Anchor: (Width: " + (w - f) + ", Height: " + bh + "); Background: " + rest + "; }");
}""")
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.PartyStore.warn("could not close the party page: " + t); }
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID me = this.playerRef.getUuid();
  @PKG@.PartyStore.pubName(this.playerRef);
  java.util.ArrayList l = @PKG@.PartyStore.listOf(me);
  boolean in = l != null;
  boolean lead = in && me.equals(l.get(0));
  int max = @PKG@.PartyStore.MAX;
  String blue = style("#1d3a5f", "#2f5a8f", "#0f2038", "#dceeff", 18);
  String red = style("#6a2020", "#8f3030", "#401010", "#ffe0e0", 18);
  String green = style("#1f5a2a", "#2f8040", "#10381a", "#e0ffe0", 18);
  String small = style("#1d3a5f", "#2f5a8f", "#0f2038", "#dceeff", 15);
  String smallRed = style("#6a2020", "#8f3030", "#401010", "#ffe0e0", 15);
  b.appendInline((String) null, "Group #SkyyParty { Anchor: (Width: 1240, Height: 840); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 12); LayoutMode: Top; }");
  b.appendInline("#SkyyParty", "Group { Anchor: (Height: 2); Background: #7fb0e0; }");
  b.appendInline("#SkyyParty", "Label #SkyyPTitle { Anchor: (Height: 46); Text: \"\"; Style: (FontSize: 28, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyPTitle.Text", in ? ("Party   " + l.size() + " / " + max + " players") : "Party");
  b.appendInline("#SkyyParty", "Label #SkyyPInfo { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: #f0d890, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  String inf = this.info;
  if (inf == null || inf.length() == 0) {
    if (!in) inf = "You're not in a party yet.";
    else if (lead) inf = "You lead this party. Promote or Kick a member on their row.";
    else inf = "Party leader: " + @PKG@.PartyStore.nameOf((java.util.UUID) l.get(0)) + ". Party chat: /pc <message>";
  }
  b.set("#SkyyPInfo.Text", inf);

  // ---- pending invite (only when not in a party)
  Object[] inv = (Object[]) @PKG@.PartyStore.INVITES.get(me);
  long left = 0L;
  if (inv != null) left = (((Long) inv[1]).longValue() - System.currentTimeMillis() + 999L) / 1000L;
  if (!in && inv != null && left > 0L) {
    b.appendInline("#SkyyParty", "Group #SkyyPPending { Anchor: (Height: 66); LayoutMode: Left; Background: #1f3a24; Padding: (Horizontal: 12, Top: 10); }");
    b.appendInline("#SkyyPPending", "Label #SkyyPPendTxt { Anchor: (Width: 760, Height: 46); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #d8ffd8, VerticalAlignment: Center); }");
    b.set("#SkyyPPendTxt.Text", String.valueOf(inv[2]) + " invited you to their party  (" + left + " s left)");
    b.appendInline("#SkyyPPending", "TextButton #SkyyPAccept { Anchor: (Width: 180, Height: 46); Text: \"Accept\"; " + green + " }");
    b.appendInline("#SkyyPPending", "Label { Anchor: (Width: 12, Height: 46); Text: \"\"; }");
    b.appendInline("#SkyyPPending", "TextButton #SkyyPDecline { Anchor: (Width: 180, Height: 46); Text: \"Decline\"; " + red + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyPAccept", @EVD@.of("a", "accept"));
    ev.addEventBinding(@BT@.Activating, "#SkyyPDecline", @EVD@.of("a", "decline"));
    b.appendInline("#SkyyParty", "Group { Anchor: (Height: 10); }");
  }

  // ---- members
  if (in) {
    int n = l.size();
    boolean compact = n > 5;
    int rh = compact ? Math.max(44, 460 / n - 6) : 86;
    int ch = rh - 8;
    b.appendInline("#SkyyParty", "Group #SkyyPHead { Anchor: (Height: 30); LayoutMode: Left; Padding: (Horizontal: 10); }");
    b.appendInline("#SkyyPHead", "Label { Anchor: (Width: 270, Height: 30); Text: \"Member\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
    b.appendInline("#SkyyPHead", "Label { Anchor: (Width: 190, Height: 30); Text: \"Health\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
    b.appendInline("#SkyyPHead", "Label { Anchor: (Width: 190, Height: 30); Text: \"Stamina\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
    b.appendInline("#SkyyPHead", "Label { Anchor: (Width: 190, Height: 30); Text: \"Mana\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
    b.appendInline("#SkyyPHead", "Label { Anchor: (Width: 190, Height: 30); Text: \"Where\"; Style: (FontSize: 15, RenderBold: true, TextColor: #8fa4b8, VerticalAlignment: Center); }");
    String myWorld = worldPart(stats(me));
    for (int i = 0; i < n; i++) {
      java.util.UUID u = (java.util.UUID) l.get(i);
      boolean self = u.equals(me);
      boolean isLead = i == 0;
      String rid = "#SkyyPRow" + i;
      b.appendInline("#SkyyParty", "Group #SkyyPRow" + i + " { Anchor: (Height: " + rh + "); LayoutMode: Left; Background: " + (self ? "#1b3354" : "#13243a") + "; Padding: (Horizontal: 10, Top: 6); }");
      // name + role
      b.appendInline(rid, "Group #SkyyPNC" + i + " { Anchor: (Width: 270, Height: " + ch + "); LayoutMode: Top; }");
      String nm = @PKG@.PartyStore.cut(@PKG@.PartyStore.nameOf(u), 18) + (self ? "  (you)" : "");
      if (compact) {
        b.appendInline("#SkyyPNC" + i, "Label #SkyyPName" + i + " { Anchor: (Height: " + ch + "); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + (isLead ? "#f0c850" : "#ffffff") + ", VerticalAlignment: Center); }");
        b.set("#SkyyPName" + i + ".Text", (isLead ? "* " : "") + nm);
      } else {
        b.appendInline("#SkyyPNC" + i, "Label #SkyyPName" + i + " { Anchor: (Height: 42); Text: \"\"; Style: (FontSize: 22, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
        b.set("#SkyyPName" + i + ".Text", nm);
        b.appendInline("#SkyyPNC" + i, "Label #SkyyPRole" + i + " { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + (isLead ? "#f0c850" : "#9fb8d0") + ", VerticalAlignment: Center); }");
        b.set("#SkyyPRole" + i + ".Text", isLead ? "* Party leader" : "Member");
      }
      // health / stamina / mana from the member's own world thread (party:stats)
      String s = stats(u);
      int[] v = nums(s);
      if (v == null) {
        statCol(b, rid, "SkyyPHp" + i, "Health  ...", 0, 0, "#d04848", "#3a1a1a", ch, compact);
        statCol(b, rid, "SkyyPSt" + i, "Stamina  ...", 0, 0, "#e0b040", "#3a3014", ch, compact);
        statCol(b, rid, "SkyyPMp" + i, "Mana  ...", 0, 0, "#4a8ae0", "#142440", ch, compact);
      } else {
        statCol(b, rid, "SkyyPHp" + i, "Health  " + v[0] + " / " + v[1], v[0], v[1], "#d04848", "#3a1a1a", ch, compact);
        statCol(b, rid, "SkyyPSt" + i, "Stamina  " + v[2] + " / " + v[3], v[2], v[3], "#e0b040", "#3a3014", ch, compact);
        statCol(b, rid, "SkyyPMp" + i, v[5] > 0 ? ("Mana  " + v[4] + " / " + v[5]) : "Mana  none", v[4], v[5], "#4a8ae0", "#142440", ch, compact);
      }
      // online + where
      boolean on = @PKG@.PartyStore.online(u) != null;
      String w = worldPart(s);
      String wh = on ? where(w, u, me) : "";
      if (on && !self && w != null && w.length() > 0 && w.equals(myWorld)) wh = wh + " (with you)";
      b.appendInline(rid, "Group #SkyyPWC" + i + " { Anchor: (Width: 190, Height: " + ch + "); LayoutMode: Top; }");
      if (compact) {
        b.appendInline("#SkyyPWC" + i, "Label #SkyyPWh" + i + " { Anchor: (Height: " + ch + "); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + (on ? "#8fe08f" : "#e08f8f") + ", VerticalAlignment: Center); }");
        b.set("#SkyyPWh" + i + ".Text", on ? wh : "Offline");
      } else {
        b.appendInline("#SkyyPWC" + i, "Label #SkyyPOn" + i + " { Anchor: (Height: 38); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + (on ? "#8fe08f" : "#e08f8f") + ", VerticalAlignment: Center); }");
        b.set("#SkyyPOn" + i + ".Text", on ? "Online" : "Offline");
        b.appendInline("#SkyyPWC" + i, "Label #SkyyPWh" + i + " { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #c9d6e6, VerticalAlignment: Center); }");
        b.set("#SkyyPWh" + i + ".Text", wh);
      }
      // leader-only buttons on the OTHER members' rows (not built at all for members)
      if (lead && !self) {
        int bh = compact ? ch - 4 : 40;
        int pt = compact ? 0 : 16;
        b.appendInline(rid, "Group #SkyyPAC" + i + " { Anchor: (Width: 158, Height: " + ch + "); LayoutMode: Left; Padding: (Top: " + pt + "); }");
        b.appendInline("#SkyyPAC" + i, "TextButton #SkyyPPro" + i + " { Anchor: (Width: 88, Height: " + bh + "); Text: \"Promote\"; " + small + " }");
        b.appendInline("#SkyyPAC" + i, "Label { Anchor: (Width: 6, Height: " + bh + "); Text: \"\"; }");
        b.appendInline("#SkyyPAC" + i, "TextButton #SkyyPKick" + i + " { Anchor: (Width: 64, Height: " + bh + "); Text: \"Kick\"; " + smallRed + " }");
        ev.addEventBinding(@BT@.Activating, "#SkyyPPro" + i, @EVD@.of("a", "promote:" + u.toString()));
        ev.addEventBinding(@BT@.Activating, "#SkyyPKick" + i, @EVD@.of("a", "kick:" + u.toString()));
      }
      b.appendInline("#SkyyParty", "Group { Anchor: (Height: 6); }");
    }
  } else {
    b.appendInline("#SkyyParty", "Group #SkyyPEmpty { Anchor: (Height: 150); LayoutMode: Top; Background: #13243a; Padding: (Horizontal: 18, Top: 14); }");
    b.appendInline("#SkyyPEmpty", "Label #SkyyPEmptyA { Anchor: (Height: 44); Text: \"\"; Style: (FontSize: 22, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyPEmptyA.Text", "Play together - start a party");
    b.appendInline("#SkyyPEmpty", "Label #SkyyPEmptyB { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 17, TextColor: #c9d6e6, VerticalAlignment: Center); }");
    b.set("#SkyyPEmptyB.Text", "1. Type your friend's name in the box below and press Enter or Invite.");
    b.appendInline("#SkyyPEmpty", "Label #SkyyPEmptyC { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 17, TextColor: #c9d6e6, VerticalAlignment: Center); }");
    b.set("#SkyyPEmptyC.Text", "2. They type /party accept in chat, or open /party and click Accept.");
  }

  // ---- invite row: SkyySacks 0.7.3 search TextField pattern (Enter = Validating without lock, or the button)
  b.appendInline("#SkyyParty", "Group { Anchor: (Height: 10); }");
  b.appendInline("#SkyyParty", "Group #SkyyPInvRow { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyPInvRow", "Label #SkyyPInvLbl { Anchor: (Width: 190, Height: 40); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: #dceeff, VerticalAlignment: Center); }");
  b.set("#SkyyPInvLbl.Text", "Invite a player");
  b.appendInline("#SkyyPInvRow", "Group #SkyyPInvBox { Anchor: (Width: 380, Height: 40); Background: #16263a; }");
  b.appendInline("#SkyyPInvBox", "TextField #SkyyPInvName { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 32; PlaceholderText: \"Player name - press Enter\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
  b.appendInline("#SkyyPInvRow", "Label { Anchor: (Width: 10, Height: 40); Text: \"\"; }");
  b.appendInline("#SkyyPInvRow", "TextButton #SkyyPInvGo { Anchor: (Width: 150, Height: 40); Text: \"Invite\"; " + blue + " }");
  ev.addEventBinding(@BT@.Validating, "#SkyyPInvName", @EVD@.of("a", "invite").append("@InviteName", "#SkyyPInvName.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyPInvGo", @EVD@.of("a", "invite").append("@InviteName", "#SkyyPInvName.Value"));
  b.appendInline("#SkyyPInvRow", "Label #SkyyPInvHint { Anchor: (Width: 460, Height: 40); Text: \"\"; Style: (FontSize: 15, TextColor: #8fa4b8, VerticalAlignment: Center); }");
  b.set("#SkyyPInvHint.Text", "   they must be online - the invite lasts " + @PKG@.PartyStore.inviteSecs() + " s");

  // ---- actions
  b.appendInline("#SkyyParty", "Group #SkyyPActs { Anchor: (Height: 62); LayoutMode: Left; Padding: (Top: 12); }");
  if (in) {
    b.appendInline("#SkyyPActs", "TextButton #SkyyPLeave { Anchor: (Width: 200, Height: 46); Text: \"Leave party\"; " + red + " }");
    b.appendInline("#SkyyPActs", "Label { Anchor: (Width: 12, Height: 46); Text: \"\"; }");
    ev.addEventBinding(@BT@.Activating, "#SkyyPLeave", @EVD@.of("a", "leave"));
  }
  if (lead) {
    b.appendInline("#SkyyPActs", "TextButton #SkyyPDisband { Anchor: (Width: 200, Height: 46); Text: \"Disband party\"; " + red + " }");
    b.appendInline("#SkyyPActs", "Label { Anchor: (Width: 12, Height: 46); Text: \"\"; }");
    ev.addEventBinding(@BT@.Activating, "#SkyyPDisband", @EVD@.of("a", "disband"));
  }
  b.appendInline("#SkyyPActs", "TextButton #SkyyPRefresh { Anchor: (Width: 160, Height: 46); Text: \"Refresh\"; " + blue + " }");
  b.appendInline("#SkyyPActs", "Label { Anchor: (Width: 12, Height: 46); Text: \"\"; }");
  b.appendInline("#SkyyPActs", "TextButton #SkyyPClose { Anchor: (Width: 160, Height: 46); Text: \"Close\"; " + blue + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyPRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyPClose", @EVD@.of("a", "close"));

  // ---- footer
  b.appendInline("#SkyyParty", "Label #SkyyPFootA { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyPFootA.Text", "Party chat: /pc <message>   -   Health, Stamina and Mana update when you press Refresh");
  b.appendInline("#SkyyParty", "Label #SkyyPFootB { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyPFootB.Text", "/party invite <player>  accept  decline  leave  list  kick <player>  promote <player>  disband");
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    @PR@ me = this.playerRef;
    // only the invite bindings carry "@InviteName" (the typed text) - handled before any action match, so a typed word can
    // never be mistaken for a button payload
    if (data.indexOf("\"@InviteName\"") >= 0) {
      String nm = @PKG@.PartyStore.cleanName(jsonStr(data, "@InviteName"));
      if (nm.length() == 0) this.info = "Type a player's name in the box first, then press Enter or Invite.";
      else {
        @PR@ t = @PKG@.PartyStore.findOnline(nm);
        this.info = t == null ? ("Nobody called " + nm + " is online right now.") : @PKG@.PartyStore.invite(me, t);
      }
      rebuild();
      return;
    }
    String a = jsonStr(data, "a");
    if (a.equals("close")) { closePage(ref, st); return; }
    if (a.equals("accept")) this.info = @PKG@.PartyStore.accept(me);
    else if (a.equals("decline")) this.info = @PKG@.PartyStore.decline(me);
    else if (a.equals("leave")) this.info = @PKG@.PartyStore.leave(me);
    else if (a.equals("disband")) this.info = @PKG@.PartyStore.disband(me);
    else if (a.equals("refresh")) this.info = "";
    else if (a.startsWith("kick:")) this.info = @PKG@.PartyStore.kick(me, parseUuid(a.substring(5)));
    else if (a.startsWith("promote:")) this.info = @PKG@.PartyStore.promote(me, parseUuid(a.substring(8)));
    else return;
    rebuild();
  } catch (Throwable t) { @PKG@.PartyStore.warn("party page event failed: " + t); }
}""")

# ================= commands (every one: Adventurer group; required args only) =================
F(inv, "public @RA@ targetArg;")
C(inv, r"""
public InviteCmd() {
  super("invite", "Invite a player to your party");
  @ADV@
  this.targetArg = withRequiredArg("player", "Player to invite", @ATY@.PLAYER_REF);
}""")
M(inv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object t = ctx.get(this.targetArg);
    if (t == null) { pr.sendMessage(@MSG@.raw("Usage: /party invite <player>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.invite(pr, (@PR@) t)));
  } catch (Throwable t2) { @PKG@.PartyStore.warn("invite failed: " + t2); pr.sendMessage(@MSG@.raw("Invite failed.")); }
}""")

C(acc, 'public AcceptCmd() { super("accept", "Accept a party invite"); @ADV@ }')
M(acc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.accept(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("accept failed: " + t2); pr.sendMessage(@MSG@.raw("Accept failed.")); }
}""")

C(dec, 'public DeclineCmd() { super("decline", "Decline a party invite"); @ADV@ }')
M(dec, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.decline(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("decline failed: " + t2); }
}""")

C(lev, 'public LeaveCmd() { super("leave", "Leave your party"); @ADV@ }')
M(lev, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.leave(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("leave failed: " + t2); }
}""")

C(lst, 'public ListCmd() { super("list", "List party members"); @ADV@ }')
M(lst, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.listText(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("list failed: " + t2); }
}""")

F(kck, "public @RA@ targetArg;")
C(kck, r"""
public KickCmd() {
  super("kick", "Kick a member from your party (leader only)");
  @ADV@
  this.targetArg = withRequiredArg("player", "Party member to kick", @ATY@.PLAYER_REF);
}""")
M(kck, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object t = ctx.get(this.targetArg);
    if (t == null) { pr.sendMessage(@MSG@.raw("Usage: /party kick <player>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.kick(pr, ((@PR@) t).getUuid())));
  } catch (Throwable t2) { @PKG@.PartyStore.warn("kick failed: " + t2); pr.sendMessage(@MSG@.raw("Kick failed.")); }
}""")

F(pro, "public @RA@ targetArg;")
C(pro, r"""
public PromoteCmd() {
  super("promote", "Make a member the party leader (leader only)");
  @ADV@
  this.targetArg = withRequiredArg("player", "Party member to promote", @ATY@.PLAYER_REF);
}""")
M(pro, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    Object t = ctx.get(this.targetArg);
    if (t == null) { pr.sendMessage(@MSG@.raw("Usage: /party promote <player>")); return; }
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.promote(pr, ((@PR@) t).getUuid())));
  } catch (Throwable t2) { @PKG@.PartyStore.warn("promote failed: " + t2); pr.sendMessage(@MSG@.raw("Promote failed.")); }
}""")

C(dis, 'public DisbandCmd() { super("disband", "Disband your party (leader only)"); @ADV@ }')
M(dis, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.disband(pr))); }
  catch (Throwable t2) { @PKG@.PartyStore.warn("disband failed: " + t2); }
}""")

# /pc - unchanged behaviour (GREEDY_STRING; everyone in the party incl. the sender sees "[Party] name: msg")
F(pc, "public @RA@ msgArg;")
C(pc, r"""
public PartyChatCmd() {
  super("pc", "Party chat");
  @ADV@
  this.msgArg = withRequiredArg("message", "Message to your party", @ATY@.GREEDY_STRING);
}""")
M(pc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  Object m = ctx.get(this.msgArg);
  if (m == null) return;
  java.util.ArrayList l = @PKG@.PartyStore.listOf(pr.getUuid());
  if (l == null) { pr.sendMessage(@MSG@.raw("You're not in a party.")); return; }
  @PKG@.PartyStore.broadcastTo(l, "[Party] " + pr.getUsername() + ": " + m.toString(), null, null);
}""")

C(root, r"""
public PartyCmd() {
  super("party", "Party: open the party page, or /party invite|accept|decline|leave|list|kick|promote|disband");
  @ADV@
  addAliases(new String[] { "p" });
  addSubCommand(new @PKG@.InviteCmd());
  addSubCommand(new @PKG@.AcceptCmd());
  addSubCommand(new @PKG@.DeclineCmd());
  addSubCommand(new @PKG@.LeaveCmd());
  addSubCommand(new @PKG@.ListCmd());
  addSubCommand(new @PKG@.KickCmd());
  addSubCommand(new @PKG@.PromoteCmd());
  addSubCommand(new @PKG@.DisbandCmd());
}""")
M(root, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.helpText())); return; }
    @PKG@.PartyStore.pubName(pr);
    p.getPageManager().openCustomPage(ref, store, new @PKG@.PartyPage(pr));
  } catch (Throwable t) {
    @PKG@.PartyStore.warn("/party page failed: " + t);
    pr.sendMessage(@MSG@.raw(@PKG@.PartyStore.helpText()));
  }
}""")

# ================= disconnect cleanup + invite pruning =================
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public PartyQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    @PKG@.PartyStore.onQuit(pr);
  } catch (Throwable t) { @PKG@.PartyStore.warn("disconnect cleanup failed: " + t); }
}""")

prune.addInterface(pool.get("java.lang.Runnable"))
C(prune, "public PartyPrune() { }")
M(prune, r"""
public void run() {
  try { @PKG@.PartyStore.pruneInvites(); } catch (Throwable t) { }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture pruner;")
C(pl, "public SkyyPartyPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.PartyStore.LOG = getLogger();
  @PKG@.PartyStore.loadConfig(getDataDirectory().resolveSibling("Skyy_SkyyParty"));
  @PKG@.PartyStore.bridge().put("party:fn:members", new @PKG@.PartyFn());
  getCommandRegistry().registerCommand(new @PKG@.PartyCmd());
  getCommandRegistry().registerCommand(new @PKG@.PartyChatCmd());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.PartyQuit());
  getEntityStoreRegistry().registerSystem(new @PKG@.PartyStats());
  this.pruner = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.PartyPrune(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyParty] """ + VERSION + r""" ready - /party page, invite|accept|decline|leave|list|kick|promote|disband, /pc; maxSize=" + @PKG@.PartyStore.MAX + " inviteSeconds=" + @PKG@.PartyStore.inviteSecs() + "; bridge party:fn:members, party:leader, party:name, party:stats");
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.pruner != null) this.pruner.cancel(false); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.PartyStore.bridge();
    java.util.Iterator it = b.keySet().iterator();
    while (it.hasNext()) {
      Object k = it.next();
      if (k instanceof String && ((String) k).startsWith("party:")) it.remove();
    }
  } catch (Throwable t) { }
  super.shutdown();
}""")

for c in (pty, ps, fn, sts, page, inv, acc, dec, lev, lst, kck, pro, dis, pc, root, quit_, prune, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyParty-%s.jar" % VERSION)
m = B.manifest("SkyyParty", VERSION, "SkyWynn parties: /party page (members with health, stamina, mana and where they are; invite box; leader kick / promote / disband), invites with a 60 s timeout, party chat /pc, leader handoff. Publishes party members + stats for the SkyyHud party widget. Zero dependencies.", PKG + ".SkyyPartyPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyParty.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyParty" % VERSION, disable_prefix="Skyy:")
