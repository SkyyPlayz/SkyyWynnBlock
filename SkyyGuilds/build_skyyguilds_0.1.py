"""SkyyGuilds 0.1 - build script (javassist via jpype).
Run:   python build_skyyguilds_0.1.py            -> SkyyGuilds/SkyyGuilds-0.1.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)

NEW MOD (SkyyGuilds-Plan.md core scope, HANDOFF design lock "Guilds in the core loop with parties"): membership, guild bank,
guild XP, seasons. Zero hard dependencies: coins come from SkyyCoins and XP from SkyySkills only through the JVM bridge
(System.getProperties().get("skyy.bridge")); without them the guild still works (no bank moves / no XP).
Guilds are per PLAYER (UUID), not per profile (tools/PROFILES-CONTRACT.md rule 6): switching profile keeps your guild. Only the
coins of the bank move to / from the player's ACTIVE profile purse (SkyyCoins resolves the profile itself).

COMMANDS (every player command, subcommand and argument form calls setPermissionGroups(new String[] { "hytale:Adventurer" });
optional arguments are never used - names with spaces are GREEDY_STRING, which the engine accepts inside subcommands:
AbstractCommand.acceptCall -> ParserContext.convertToSubCommand once per command level, extractGreedyRawTail skips
subCommandIndex + earlier required parameters words of the raw input; registerRequiredArg sets allowsExtraArguments for a greedy arg,
acceptCall0 then only needs tokens >= required - HytaleServer.jar bytecode, 2026-09-24):
  /guild                          opens the guild page (not in a guild: a Create page with a name box, plus your pending invite)
  /guild help                     every command in chat
  /guild create <name>            3-24 letters / digits / spaces, unique (case-insensitive); you become the Leader
  /guild tag <tag>                Leader: 2-4 letters/digits, unique; /guild tag clear removes it
  /guild invite <player>          Leader / Officer; the player must be online; invites last inviteSeconds (300)
  /guild accept | /guild decline  answer your newest invite
  /guild leave                    Members leave at once; the Leader confirms (repeat within 10 s): the best Officer (then the oldest
                                  member) becomes Leader; the LAST member leaving disbands the guild (bank paid to their purse)
  /guild kick <player>            Leader / Officer, only members ranked BELOW you (Officers kick Members, the Leader anyone)
  /guild promote <player>         Leader: Member -> Officer
  /guild demote <player>          Leader: Officer -> Member
  /guild transfer <player>        Leader hands the guild over (repeat within 10 s); the old Leader becomes an Officer
  /guild disband                  Leader, repeat within 10 s; the bank is paid into the Leader's purse FIRST (refused if that fails)
  /guild info | /guild list       your guild in chat | the top 10 guilds by level
  /guild bank                     balance + the last 5 bank log lines
  /guild bank deposit <amount>    anyone in the guild; amount 500, 2k, 1.5m, all
  /guild bank withdraw <amount>   Leader / Officer
  /gc <message>                   guild chat (GREEDY_STRING like SkyyParty's /pc)
  /guildadmin ...                 requirePermission("skyyguilds.admin") on the root and on every subcommand:
       info <guild>  |  delete <guild> (repeat within 10 s; bank paid to the Leader, works offline)  |  season  |  season next
       (repeat within 10 s)  |  xp <amount> <guild> (test helper: adds guild XP)  |  reload (config.properties)
  <guild> = name (case-insensitive), tag or id.

THE /guild PAGE (inline only, HANDOFF section 2: no .ui files, no underscores in ids, root Group anchor Width/Height only, TextButton +
EventData, rebuilt only after a click - never a periodic page update, never closes itself before opening another page):
  1120 x 900: name + [TAG], level, season XP, your rank, a green XP bar with "x / y XP to level L+1", bank + online count;
  member rows (8 per page, Prev/Next) with an online dot, name, rank, guild XP they added, online/offline and the buttons your rank
  allows: Promote / Demote / Kick / Make leader (Kick and Make leader need a second click); an Invite TextField + button
  (Leader/Officer), an Amount TextField + Deposit (+ Withdraw for Leader/Officer), the last 3 bank log lines, Refresh, Leave guild
  (second click confirms), Disband (Leader, second click). Text fields use the SkyySacks 0.7.3 search pattern (verified in game):
  EventData.of("a", action).append("@GInvite", "#SkyyGInvite.Value"), read back with jsonStr. Not in a guild: 1120 x 660 with the
  pending invite (Accept / Decline), a guild name TextField + Create guild, the rules and the commands.

GUILD XP: every GuildTick (5 s, scheduler) the online guild members get an XpTask on THEIR world thread every xpPollSeconds (10 s).
  It sums skill:fn:xp (SkyySkills 0.4+: apply(Object[]{UUID, skill}) -> Long total XP of the ACTIVE profile) over xpSkills
  (Mining, Foraging, Farming, Acrobatics, Archery, Swordsmanship, Assassination, Shaman, Sorcery, Alchemy, Smithing, Cooking,
  Exploration - "Combat" is left out on purpose: it is an alias of the current class skill). The positive change since the last check
  x xpSharePercent (10) / 100 goes to the guild (fractions carry over), capped at xpMaxPerCheck skill XP per check. The baseline is
  keyed by profile key + guild id, so a profile switch or joining a guild is a new baseline (no credit for XP earned elsewhere); the
  first check after a join / restart only records the baseline (up to one check of XP is not counted after a server restart).
  Fallback without skill:fn:xp: the sum of the levels in skill:<uuid> ("Mining:12,..."), xpPerLevelFallback (25) guild XP per level
  gained. SkyySkills is never touched or called for anything else.
  Level curve: level L -> L+1 needs levelBase + levelStep x (L - 1) guild XP (defaults 100 / 150: level 2 at 100, level 5 at 1,300,
  level 10 at 6,300 guild XP). A level-up is announced to the online members.
SEASONS: meta.properties holds the season number (starts at 1). Guild XP also counts into season.<n> of that guild; /guildadmin season
  shows the season top 10, /guildadmin season next starts the next season (levels and total XP stay; no rewards yet).

GUILD BANK: coins move only through SkyyCoins' coins:fn:get / coins:fn:take / coins:fn:add (SkyyCoins 0.1.5: act on the ACTIVE
  profile; null = purse unreadable, nothing changed). All under the one GuildStore lock (the SkyyBank 0.1.2 pattern: SkyyCoins never
  calls back, so no lock cycle). Rule: the guild file never shows coins that already left the bank. Deposit = take from the purse
  FIRST (coins:fn:take must say TRUE), then add to the bank and write. Withdraw = write the lower bank FIRST (a failed write = nothing
  moved), then coins:fn:add; if that does not return a number the exact amount goes back and is written again. Disband / admin
  delete = rewrite the guild file as disbanded with bank 0 FIRST (a failed write refuses), then pay the bank to the Leader (a failed
  payout restores the live file and refuses), then move the file to guilds/deleted/. Every move is logged: guild file log.0..9 (the
  page) + banklog.log (all time, one line per move).
  maxBank (1e12) caps a bank. No coins are created: nothing in this mod adds coins except a withdraw / payout of coins the bank held.

BRIDGE (FIXED CONTRACT shared with SkyyParty 0.1.3 and SkyyHud 0.3.8; per PLAYER):
  "guild:<uuid>"      = guild name (String) while the player is in a guild, removed when they leave / are kicked / it is disbanded
  "guild:info:<uuid>" = "name|tag|level|xp|xpForNext|onlineCount|memberCount|rank"  (tag "" when none; xp = XP INTO the current level,
                        xpForNext = the XP that level needs in total, so a bar is xp / xpForNext; rank = Leader / Officer / Member).
                        Republished on every change (join, leave, rank, tag, XP) for every member, and every 5 s for online members.
  "guild:fn:online"   = java.util.function.Function apply(UUID viewer) -> String[] display names of the ONLINE members of the viewer's
                        guild (the viewer included, in stored member order), empty array when not in a guild. Any thread.
  Read: coins:fn:get/take/add (SkyyCoins), skill:fn:xp / skill:<uuid> (SkyySkills), profile:fn:key (SkyyProfiles, baseline key only).

DATA (<world>/mods/Skyy_SkyyGuilds/, stable across versions): guilds/<id>.properties (id g1, g2, ...: name, tag, created, xp, bank,
  member.<uuid>=rank|joinedMillis|guildXpAdded|name, season.<n>=xp, log.0..9) = the truth; players.properties (uuid=guildId|name|guild,
  rewritten after every membership change, rebuilt from the guild files at every start - a player listed in two guild files keeps
  the first and is removed from the other, logged); meta.properties (nextId, season, seasonStart); banklog.log (append-only);
  config.properties (defaults written on first start; /guildadmin reload). Every file write = tmp file + fsync + atomic rename
  (ATOMIC_MOVE + REPLACE_EXISTING, 5 x 20 ms retries on a Windows FileSystemException - SkyyProfiles 0.1 pattern). A disbanded guild
  file is marked disbanded=<millis> and moved to guilds/deleted/ (never loaded again, never hard-deleted). XP-only changes are
  written by the 5 s tick (dirty flag) and on shutdown; membership, tag and bank changes are written at once.

THREADS: commands and page clicks run on the player's world thread (AbstractPlayerCommand / page events); the tick on the shared
  scheduler (no component, stat or inventory access at all; Universe.getPlayers / getPlayer + sendMessage only, the SkyyBank tick
  pattern); XP reads on the member's own world thread. One registered command set, no ECS systems, no events (join / leave notices
  come from the tick's online set, so PlayerReadyEvent re-fires on world switches do not matter).

UNVERIFIED (static + bare-JVM checks only; needs the 2-player test): the /guild page layout and the two TextFields on one page
  (inline markup copied from verified SkyySacks / SkyySkills pages, but this exact page never ran on a client), Message.color on guild
  chat lines (SkyyClasses uses it), the 8-row member list with per-row buttons, GREEDY names inside subcommands in game (bytecode only),
  guild XP from real SkyySkills XP (the bare-JVM test used a fake skill:fn:xp), the online / offline notices.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.guilds"
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
    "PKG":  PKG,
    "VERSION": VERSION,
    # every player command: grant its auto permission node to the default player group (vanilla /help /who pattern)
    "ADV":  'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    "ADMIN": 'requirePermission("skyyguilds.admin");',
}
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
PB  = "com.hypixel.hytale.server.core.plugin.PluginBase"

for c, m in ((T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"), (T["UNI"], "getWorld"), (T["PR"], "getWorldUuid"),
             (T["PR"], "getUsername"), (T["PR"], "getUuid"), (T["PR"], "isValid"), (T["PR"], "sendMessage"), (T["WLD"], "execute"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (PB, "shutdown"), (PB, "getDataDirectory"), (PB, "getCommandRegistry"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "withRequiredArg"),
             (T["ATY"], "GREEDY_STRING"), (T["ATY"], "STRING"), (T["CTX"], "get"), (T["MSG"], "raw"), (T["MSG"], "color"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["EVD"], "append"),
             (T["BT"], "Activating"), (T["BT"], "Validating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"),
             (PGM, "openCustomPage"), (T["PLA"], "getPageManager"), (T["LIFE"], "CanDismiss")):
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
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


mem  = pool.makeClass(PKG + ".GMember")
gld  = pool.makeClass(PKG + ".Guild")
cfg  = pool.makeClass(PKG + ".GCfg")
gs   = pool.makeClass(PKG + ".GuildStore")
xpt  = pool.makeClass(PKG + ".XpTask")
tick = pool.makeClass(PKG + ".GuildTick")
ofn  = pool.makeClass(PKG + ".GuildOnlineFn")
page = pool.makeClass(PKG + ".GuildPage", pool.get(T["PAGE"]))
pl   = pool.makeClass(PKG + ".SkyyGuildsPlugin", pool.get(T["JP"]))
ALL = [mem, gld, cfg, gs, xpt, tick, ofn, page]

# ================= GMember / Guild (plain data; every access holds the GuildStore lock) =================
for f in ("public String uuid;", "public java.util.UUID uid;", "public String name;", "public int rank;", "public long joined;",
          "public long contrib;"):
    F(mem, f)
C(mem, "public GMember() { }")

for f in ("public String id;", "public String name;", "public String tag;", "public long created;", "public long xp;",
          "public long bank;", "public java.util.LinkedHashMap members;", "public java.util.HashMap season;",
          "public java.util.ArrayList log;", "public boolean dirty;"):
    F(gld, f)
C(gld, r"""
public Guild() {
  this.members = new java.util.LinkedHashMap();
  this.season = new java.util.HashMap();
  this.log = new java.util.ArrayList();
  this.tag = "";
  this.name = "";
}""")
M(gld, r"""
public long seasonXp(int s) {
  Object v = this.season.get(String.valueOf(s));
  return v instanceof Long ? ((Long) v).longValue() : 0L;
}""")
M(gld, r"""
public void addSeason(int s, long n) {
  this.season.put(String.valueOf(s), Long.valueOf(seasonXp(s) + n));
}""")
M(gld, r"""
public @PKG@.GMember member(String u) {
  if (u == null) return null;
  return (@PKG@.GMember) this.members.get(u);
}""")
M(gld, r"""
public @PKG@.GMember leader() {
  java.util.Iterator it = this.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    if (m.rank == 2) return m;
  }
  return null;
}""")

# ================= GCfg fields (load() is added after GuildStore.warn exists) =================
SKILLS = "Mining,Foraging,Farming,Acrobatics,Archery,Swordsmanship,Assassination,Shaman,Sorcery,Alchemy,Smithing,Cooking,Exploration"
for f in ("public static java.nio.file.Path FILE;",
          "public static volatile int SHARE = 10;",
          "public static volatile int POLL = 10;",
          'public static volatile String[] SKILLS = "%s".split(",");' % SKILLS,
          "public static volatile long LEVEL_FALLBACK = 25L;",
          "public static volatile long MAX_DELTA = 10000000L;",
          "public static volatile long BASE = 100L;",
          "public static volatile long STEP = 150L;",
          "public static volatile int MAX_MEMBERS = 25;",
          "public static volatile int INVITE_SECONDS = 300;",
          "public static volatile long MAX_BANK = 1000000000000L;",
          "public static volatile boolean ONLINE_MSG = true;"):
    F(cfg, f)

CFG_LINES = [
    "# SkyyGuilds %s settings. /guildadmin reload re-reads this file (no restart needed)." % VERSION,
    "# Guild XP: the skill XP every guild member earns (SkyySkills) adds this percent to the guild's XP (fractions carry over).",
    "xpSharePercent=10",
    "# How often the members' skill XP is checked, in seconds (5 to 300, in 5 second steps).",
    "xpPollSeconds=10",
    "# The skills (SkyySkills skill:fn:xp names) whose XP counts. Unknown names count 0. Combat is left out on purpose (it is the class skill).",
    "xpSkills=" + SKILLS,
    "# Only when SkyySkills has no skill:fn:xp (older than 0.4): guild XP per skill LEVEL a member gains.",
    "xpPerLevelFallback=25",
    "# Most skill XP one member can add in one check (guards against admin XP commands); the rest of that jump is ignored.",
    "xpMaxPerCheck=10000000",
    "# Guild level curve: level L -> L+1 needs levelBase + levelStep x (L - 1) guild XP.",
    "levelBase=100",
    "levelStep=150",
    "# Largest guild.",
    "maxMembers=25",
    "# How long a guild invite lasts, in seconds.",
    "inviteSeconds=300",
    "# Largest guild bank balance, in coins.",
    "maxBank=1000000000000",
    "# Chat notice to the guild when a member comes online or goes offline.",
    "onlineMessages=true",
]
CFG_TEXT = "\\n".join(l.replace("\\", "\\\\").replace('"', '\\"') for l in CFG_LINES) + "\\n"

# ================= GuildStore (the ONE lock: every guild state change is a static synchronized method here) =================
for f in ("public static java.nio.file.Path DIR;",
          "public static java.nio.file.Path GDIR;",
          "public static @LOG@ LOG;",
          "public static final java.util.HashMap GUILDS = new java.util.HashMap();",
          "public static final java.util.HashMap BYNAME = new java.util.HashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BYPLAYER = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap INVITES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap CONFIRM = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile int SEASON = 1;",
          "public static volatile long SEASON_START = 0L;",
          "public static volatile long NEXT_ID = 1L;"):
    F(gs, f)
# GUILDS: id -> Guild, BYNAME: lower-case name -> id (both under the lock). BYPLAYER: uuid string -> id (written under the lock, read
# lock-free). INVITES: invitee uuid string -> Object[]{guildId, inviterName, Long expiryMillis}. CONFIRM: "action:uuid..." -> Long expiry.

M(gs, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# profile contract helper (tools/PROFILES-CONTRACT.md), verbatim - only used for the XP baseline key (guilds are per player)
M(gs, r"""
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(gs, r"""
public static void warn(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyGuilds] " + msg);
    else System.out.println("[SkyyGuilds] WARN " + msg);
  } catch (Throwable t) { }
}""")
M(gs, r"""
public static void info(String msg) {
  try {
    if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyGuilds] " + msg);
    else System.out.println("[SkyyGuilds] " + msg);
  } catch (Throwable t) { }
}""")
M(gs, r"""
public static long parseLong(String s, long d) {
  if (s == null) return d;
  try { return Long.parseLong(s.trim()); } catch (Throwable t) { return d; }
}""")

# ---- GCfg.load (needs GuildStore.warn / parseLong)
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d, long min, long max) {
  long v = @PKG@.GuildStore.parseLong(p.getProperty(k), d);
  if (v < min) v = min;
  if (v > max) v = max;
  return v;
}""")
M(cfg, r"""
public static void load() {
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, "@CFGTEXT@".getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    SHARE = (int) lng(p, "xpSharePercent", 10L, 0L, 1000L);
    long poll = lng(p, "xpPollSeconds", 10L, 5L, 300L);
    POLL = (int) ((poll + 4L) / 5L * 5L);
    String sk = p.getProperty("xpSkills");
    if (sk != null && sk.trim().length() > 0) {
      String[] a = sk.split(",");
      java.util.ArrayList l = new java.util.ArrayList();
      for (int i = 0; i < a.length; i++) {
        String x = a[i].trim();
        if (x.length() > 0 && !x.equalsIgnoreCase("combat")) l.add(x);
      }
      String[] r = new String[l.size()];
      for (int i = 0; i < r.length; i++) r[i] = (String) l.get(i);
      SKILLS = r;
    }
    LEVEL_FALLBACK = lng(p, "xpPerLevelFallback", 25L, 0L, 1000000L);
    MAX_DELTA = lng(p, "xpMaxPerCheck", 10000000L, 1L, 1000000000000L);
    BASE = lng(p, "levelBase", 100L, 1L, 1000000000000L);
    STEP = lng(p, "levelStep", 150L, 0L, 1000000000000L);
    MAX_MEMBERS = (int) lng(p, "maxMembers", 25L, 1L, 500L);
    INVITE_SECONDS = (int) lng(p, "inviteSeconds", 300L, 10L, 86400L);
    MAX_BANK = lng(p, "maxBank", 1000000000000L, 0L, 1000000000000000L);
    ONLINE_MSG = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("onlineMessages", "true")).trim());
  } catch (Throwable t) { @PKG@.GuildStore.warn("could not read " + FILE + " (defaults used): " + t); }
}""".replace("@CFGTEXT@", CFG_TEXT))

M(gs, r"""
public static @UNI@ uni() {
  try { return @UNI@.get(); } catch (Throwable t) { return null; }
}""")
M(gs, r"""
public static @PR@ online(java.util.UUID u) {
  if (u == null) return null;
  try {
    @UNI@ un = uni();
    if (un == null) return null;
    @PR@ p = un.getPlayer(u);
    return (p != null && p.isValid()) ? p : null;
  } catch (Throwable t) { return null; }
}""")
M(gs, r"""
public static @PR@ onlineByName(String n) {
  if (n == null) return null;
  String want = n.trim();
  if (want.length() == 0) return null;
  try {
    @UNI@ un = uni();
    if (un == null) return null;
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.isValid() && p.getUsername() != null && p.getUsername().equalsIgnoreCase(want)) return p;
    }
  } catch (Throwable t) { }
  return null;
}""")
M(gs, r"""
public static void say(@PR@ p, String text, String color) {
  if (p == null || text == null) return;
  try { p.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")
M(gs, r"""
public static void sayU(java.util.UUID u, String text, String color) {
  say(online(u), text, color);
}""")
# results: "+..." success (green), "-..." refused (orange), "=..." info / confirm prompt (blue)
M(gs, r"""
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#cfe3ff";
}""")
M(gs, r"""
public static String textOf(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")
M(gs, r"""
public static void tell(@PR@ p, String res) {
  if (res == null || res.length() == 0) return;
  say(p, "[Guild] " + textOf(res), colorOf(res));
}""")
M(gs, r"""
public static void tellAll(@PR@ p, String[] lines) {
  for (int i = 0; lines != null && i < lines.length; i++) tell(p, lines[i]);
}""")
# ---- files: tmp + fsync + atomic rename, 5 x 20 ms retries on a Windows FileSystemException (SkyyProfiles 0.1 / SkyyBank 0.1.2)
M(gs, r"""
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
M(gs, r"""
public static void writeProps(java.nio.file.Path f, java.util.Properties p, String header) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    p.store(out, header);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  replaceFile(tmp, f);
}""")
M(gs, r"""
public static String rankName(int r) {
  if (r >= 2) return "Leader";
  if (r == 1) return "Officer";
  return "Member";
}""")
M(gs, r"""
public static String norm(String s) {
  if (s == null) return "";
  String t = s.trim();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (Character.isWhitespace(c)) {
      if (sb.length() > 0 && sb.charAt(sb.length() - 1) != ' ') sb.append(' ');
    } else sb.append(c);
  }
  return sb.toString().trim();
}""")
M(gs, r"""
public static boolean alnum(char c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9');
}""")
M(gs, r"""
public static String nameError(String n) {
  if (n.length() < 3 || n.length() > 24) return "A guild name needs 3 to 24 characters (letters, digits and spaces).";
  boolean letter = false;
  for (int i = 0; i < n.length(); i++) {
    char c = n.charAt(i);
    if (!alnum(c) && c != ' ') return "A guild name may only use letters, digits and spaces.";
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) letter = true;
  }
  if (!letter) return "A guild name needs at least one letter.";
  return null;
}""")
M(gs, r"""
public static String tagError(String t) {
  if (t.length() < 2 || t.length() > 4) return "A guild tag needs 2 to 4 letters or digits.";
  for (int i = 0; i < t.length(); i++) if (!alnum(t.charAt(i))) return "A guild tag may only use letters and digits.";
  return null;
}""")
# typed text echoed in chat: letters, digits, _ and spaces only, max 32
M(gs, r"""
public static String clean(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 32; i++) {
    char c = s.charAt(i);
    if (alnum(c) || c == '_' || c == ' ' || c == '-') sb.append(c);
  }
  return sb.toString().trim();
}""")
M(gs, r"""
public static long need(long lv) {
  long n = @PKG@.GCfg.BASE + @PKG@.GCfg.STEP * (lv - 1L);
  return n < 1L ? 1L : n;
}""")
# {level, xp into that level, xp that level needs}
M(gs, r"""
public static long[] levelInfo(long xp) {
  long left = xp < 0L ? 0L : xp;
  long lv = 1L;
  while (lv < 100000L) {
    long n = need(lv);
    if (left < n) break;
    left = left - n;
    lv++;
  }
  return new long[] { lv, left, need(lv) };
}""")
M(gs, r"""
public static String fmt(long n) {
  if (n < 0L) return "-" + fmt(n == Long.MIN_VALUE ? Long.MAX_VALUE : -n);
  if (n < 10000L) return String.valueOf(n);
  if (n < 1000000L) { long t = n / 100L; return (t / 10L) + "." + (t % 10L) + "k"; }
  if (n < 1000000000L) { long h = n / 10000L; return (h / 100L) + "." + ((h % 100L) < 10L ? "0" : "") + (h % 100L) + "m"; }
  long g = n / 10000000L;
  return (g / 100L) + "." + ((g % 100L) < 10L ? "0" : "") + (g % 100L) + "b";
}""")
M(gs, r"""
public static String tagText(@PKG@.Guild g) {
  return (g.tag == null || g.tag.length() == 0) ? "" : " [" + g.tag + "]";
}""")
M(gs, r"""
public static String mins() {
  int s = @PKG@.GCfg.INVITE_SECONDS;
  if (s % 60 == 0) return (s / 60) + (s == 60 ? " minute" : " minutes");
  return s + " seconds";
}""")
# FIXED CONTRACT value: "name|tag|level|xp|xpForNext|onlineCount|memberCount|rank"
M(gs, r"""
public static String infoString(@PKG@.Guild g, @PKG@.GMember m, int onl) {
  long[] li = levelInfo(g.xp);
  return g.name + "|" + (g.tag == null ? "" : g.tag) + "|" + li[0] + "|" + li[1] + "|" + li[2] + "|" + onl + "|" + g.members.size() + "|" + rankName(m.rank);
}""")
M(gs, r"""
public static synchronized int onlineCount(@PKG@.Guild g) {
  int n = 0;
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    if (online(m.uid) != null) n++;
  }
  return n;
}""")
M(gs, r"""
public static synchronized void publishGuild(@PKG@.Guild g) {
  if (g == null) return;
  int onl = onlineCount(g);
  java.util.Map b = bridge();
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    b.put("guild:" + m.uuid, g.name);
    b.put("guild:info:" + m.uuid, infoString(g, m, onl));
  }
}""")
M(gs, r"""
public static void unpublish(String u) {
  java.util.Map b = bridge();
  b.remove("guild:" + u);
  b.remove("guild:info:" + u);
}""")
# except = comma-joined uuid strings that do not get the line (they got their own message), or null
M(gs, r"""
public static synchronized void broadcast(@PKG@.Guild g, String text, String color, String except) {
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    if (except != null && except.indexOf(m.uuid) >= 0) continue;
    say(online(m.uid), text, color);
  }
}""")
M(gs, r"""
public static synchronized java.util.Properties propsOf(@PKG@.Guild g) {
  java.util.Properties p = new java.util.Properties();
  p.setProperty("id", g.id);
  p.setProperty("name", g.name);
  p.setProperty("tag", g.tag == null ? "" : g.tag);
  p.setProperty("created", String.valueOf(g.created));
  p.setProperty("xp", String.valueOf(g.xp));
  p.setProperty("bank", String.valueOf(g.bank));
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    p.setProperty("member." + m.uuid, m.rank + "|" + m.joined + "|" + m.contrib + "|" + (m.name == null ? "" : m.name));
  }
  java.util.Iterator si = g.season.keySet().iterator();
  while (si.hasNext()) {
    String k = (String) si.next();
    p.setProperty("season." + k, String.valueOf(g.season.get(k)));
  }
  for (int i = 0; i < g.log.size(); i++) p.setProperty("log." + i, (String) g.log.get(i));
  return p;
}""")
M(gs, r"""
public static synchronized boolean saveGuild(@PKG@.Guild g) {
  try {
    writeProps(GDIR.resolve(g.id + ".properties"), propsOf(g), "SkyyGuilds guild file - edit only while the server is stopped");
    g.dirty = false;
    return true;
  } catch (Throwable t) {
    g.dirty = true;
    warn("could not save guild " + g.id + " (kept in memory, retried every 5 s): " + t);
    return false;
  }
}""")
M(gs, r"""
public static synchronized void saveIndex() {
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = GUILDS.values().iterator();
    while (it.hasNext()) {
      @PKG@.Guild g = (@PKG@.Guild) it.next();
      java.util.Iterator mi = g.members.values().iterator();
      while (mi.hasNext()) {
        @PKG@.GMember m = (@PKG@.GMember) mi.next();
        p.setProperty(m.uuid, g.id + "|" + m.name + "|" + g.name);
      }
    }
    writeProps(DIR.resolve("players.properties"), p, "SkyyGuilds players index (uuid=guildId|name|guild) - rebuilt from guilds/*.properties at every start; the guild files are the truth");
  } catch (Throwable t) { warn("could not save the players index: " + t); }
}""")
M(gs, r"""
public static synchronized void saveMeta() {
  try {
    java.util.Properties p = new java.util.Properties();
    p.setProperty("nextId", String.valueOf(NEXT_ID));
    p.setProperty("season", String.valueOf(SEASON));
    p.setProperty("seasonStart", String.valueOf(SEASON_START));
    writeProps(DIR.resolve("meta.properties"), p, "SkyyGuilds meta - season number and the next guild id");
  } catch (Throwable t) { warn("could not save meta.properties: " + t); }
}""")
# bank log: last 10 in the guild file (page) + banklog.log (all time)
M(gs, r"""
public static synchronized void addLog(@PKG@.Guild g, String who, String action, long amount) {
  long now = System.currentTimeMillis();
  String w = who == null ? "?" : who.replace('|', ' ');
  g.log.add(now + "|" + w + "|" + action + "|" + amount + "|" + g.bank);
  while (g.log.size() > 10) g.log.remove(0);
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    String line = java.time.Instant.ofEpochMilli(now).toString() + " guild=" + g.id + " (" + g.name + ") player=" + w + " " + action + " " + amount + " bank=" + g.bank + System.lineSeparator();
    java.nio.file.Files.write(DIR.resolve("banklog.log"), line.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { warn("could not write banklog.log: " + t); }
}""")
# exactly one Leader: none -> the best Officer / oldest member; several -> the oldest stays, the rest become Officers
M(gs, r"""
public static boolean fixLeader(@PKG@.Guild g) {
  @PKG@.GMember lead = null;
  int leaders = 0;
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    if (m.rank == 2) { leaders++; if (lead == null || m.joined < lead.joined) lead = m; }
  }
  if (leaders == 1) return false;
  if (g.members.size() == 0) return false;
  if (leaders == 0) {
    java.util.Iterator it2 = g.members.values().iterator();
    while (it2.hasNext()) {
      @PKG@.GMember m = (@PKG@.GMember) it2.next();
      if (lead == null || m.rank > lead.rank || (m.rank == lead.rank && m.joined < lead.joined)) lead = m;
    }
    lead.rank = 2;
    warn("guild " + g.id + " had no Leader - " + lead.name + " is the Leader now");
    return true;
  }
  java.util.Iterator it3 = g.members.values().iterator();
  while (it3.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it3.next();
    if (m.rank == 2 && m != lead) m.rank = 1;
  }
  warn("guild " + g.id + " had " + leaders + " Leaders - kept " + lead.name + ", the others are Officers");
  return true;
}""")
M(gs, r"""
public static java.util.Properties readProps(java.nio.file.Path f) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 3; i++) {
    try {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      return p;
    } catch (java.nio.file.NoSuchFileException e) {
      throw e;
    } catch (java.io.IOException e) {
      last = e;
    }
    try { Thread.sleep(50L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(gs, r"""
public static @PKG@.Guild loadGuildFile(java.nio.file.Path f) {
  String fn = f.getFileName().toString();
  try {
    java.util.Properties p = readProps(f);
    if (p.getProperty("disbanded") != null) return null;
    String base = fn.substring(0, fn.length() - 11);
    @PKG@.Guild g = new @PKG@.Guild();
    g.id = p.getProperty("id", base).trim();
    if (!g.id.equals(base)) { warn("guild file " + fn + " says id=" + g.id + " - using " + base); g.id = base; }
    g.name = norm(p.getProperty("name", ""));
    if (g.name.length() == 0) { warn("guild file " + fn + " has no name - not loaded"); return null; }
    g.tag = p.getProperty("tag", "").trim();
    g.created = parseLong(p.getProperty("created"), 0L);
    g.xp = Math.max(0L, parseLong(p.getProperty("xp"), 0L));
    g.bank = Math.max(0L, parseLong(p.getProperty("bank"), 0L));
    java.util.ArrayList mems = new java.util.ArrayList();
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      if (k.startsWith("member.")) {
        java.util.UUID uid = null;
        try { uid = java.util.UUID.fromString(k.substring(7).trim()); } catch (Throwable t) { uid = null; }
        if (uid == null) { warn("guild file " + fn + ": bad member key " + k + " - skipped"); continue; }
        String[] v = p.getProperty(k).split("\\|", 4);
        @PKG@.GMember m = new @PKG@.GMember();
        m.uid = uid;
        m.uuid = uid.toString();
        m.rank = (int) parseLong(v.length > 0 ? v[0] : "0", 0L);
        if (m.rank < 0 || m.rank > 2) m.rank = 0;
        m.joined = v.length > 1 ? parseLong(v[1], 0L) : 0L;
        m.contrib = v.length > 2 ? Math.max(0L, parseLong(v[2], 0L)) : 0L;
        m.name = (v.length > 3 && v[3].trim().length() > 0) ? v[3].trim() : m.uuid.substring(0, 8);
        mems.add(m);
      } else if (k.startsWith("season.")) {
        g.season.put(k.substring(7).trim(), Long.valueOf(Math.max(0L, parseLong(p.getProperty(k), 0L))));
      }
    }
    // members in join order (the file itself is unordered)
    for (int i = 1; i < mems.size(); i++) {
      @PKG@.GMember x = (@PKG@.GMember) mems.get(i);
      int j = i - 1;
      while (j >= 0 && ((@PKG@.GMember) mems.get(j)).joined > x.joined) { mems.set(j + 1, mems.get(j)); j--; }
      mems.set(j + 1, x);
    }
    for (int i = 0; i < mems.size(); i++) {
      @PKG@.GMember m = (@PKG@.GMember) mems.get(i);
      g.members.put(m.uuid, m);
    }
    for (int i = 0; i < 10; i++) {
      String l = p.getProperty("log." + i);
      if (l != null) g.log.add(l);
    }
    return g;
  } catch (Throwable t) {
    warn("could not read guild file " + fn + " (NOT loaded, left untouched on disk): " + t);
    return null;
  }
}""")
M(gs, r"""
public static synchronized void loadAll() {
  GUILDS.clear();
  BYNAME.clear();
  BYPLAYER.clear();
  long now = System.currentTimeMillis();
  try {
    java.nio.file.Files.createDirectories(GDIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path mf = DIR.resolve("meta.properties");
    if (java.nio.file.Files.exists(mf, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = readProps(mf);
      NEXT_ID = Math.max(1L, parseLong(p.getProperty("nextId"), 1L));
      SEASON = (int) Math.max(1L, parseLong(p.getProperty("season"), 1L));
      SEASON_START = parseLong(p.getProperty("seasonStart"), now);
    } else {
      NEXT_ID = 1L; SEASON = 1; SEASON_START = now;
      saveMeta();
    }
  } catch (Throwable t) { warn("could not read meta.properties (season 1): " + t); }
  java.util.ArrayList files = new java.util.ArrayList();
  try {
    java.util.stream.Stream s = java.nio.file.Files.list(GDIR);
    try {
      java.util.Iterator it = s.iterator();
      while (it.hasNext()) {
        java.nio.file.Path f = (java.nio.file.Path) it.next();
        String n = f.getFileName().toString();
        if (n.endsWith(".properties") && java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) files.add(f);
      }
    } finally { s.close(); }
  } catch (Throwable t) { warn("could not list " + GDIR + ": " + t); }
  int members = 0;
  for (int i = 0; i < files.size(); i++) {
    @PKG@.Guild g = loadGuildFile((java.nio.file.Path) files.get(i));
    if (g == null) continue;
    String low = g.name.toLowerCase();
    if (BYNAME.containsKey(low)) warn("two guild files use the name '" + g.name + "' (" + BYNAME.get(low) + " and " + g.id + ") - name lookups find " + BYNAME.get(low));
    else BYNAME.put(low, g.id);
    GUILDS.put(g.id, g);
    if (g.id.startsWith("g")) {
      long n = parseLong(g.id.substring(1), 0L);
      if (n >= NEXT_ID) NEXT_ID = n + 1L;
    }
    java.util.ArrayList dup = new java.util.ArrayList();
    java.util.Iterator mi = g.members.values().iterator();
    while (mi.hasNext()) {
      @PKG@.GMember m = (@PKG@.GMember) mi.next();
      Object other = BYPLAYER.get(m.uuid);
      if (other != null) { dup.add(m.uuid); warn(m.name + " (" + m.uuid + ") is listed in guild " + other + " AND " + g.id + " - kept in " + other + ", removed from " + g.id); }
      else { BYPLAYER.put(m.uuid, g.id); members++; }
    }
    for (int d = 0; d < dup.size(); d++) g.members.remove(dup.get(d));
    if (fixLeader(g) || dup.size() > 0) g.dirty = true;
  }
  saveMeta();
  saveIndex();
  java.util.Iterator gi = GUILDS.values().iterator();
  while (gi.hasNext()) {
    @PKG@.Guild g = (@PKG@.Guild) gi.next();
    if (g.dirty) saveGuild(g);
    publishGuild(g);
  }
  info("loaded " + GUILDS.size() + " guild(s) with " + members + " member(s), season " + SEASON + " (" + DIR + ")");
}""")
# confirm-by-repeating: true when the same key was asked within the last 10 s (then it is consumed)
M(gs, r"""
public static boolean confirm(String key) {
  long now = System.currentTimeMillis();
  Object t = CONFIRM.get(key);
  if (t instanceof Long && ((Long) t).longValue() >= now) { CONFIRM.remove(key); return true; }
  CONFIRM.put(key, Long.valueOf(now + 10000L));
  return false;
}""")
M(gs, r"""
public static String gidOf(String u) {
  Object id = BYPLAYER.get(u);
  return id == null ? null : (String) id;
}""")
M(gs, r"""
public static synchronized @PKG@.Guild guildOf(String u) {
  Object id = BYPLAYER.get(u);
  return id == null ? null : (@PKG@.Guild) GUILDS.get(id);
}""")
# member by uuid string, stored name (any case), or an online player's name
M(gs, r"""
public static synchronized @PKG@.GMember findMember(@PKG@.Guild g, String who) {
  if (who == null) return null;
  String w = who.trim();
  if (w.length() == 0) return null;
  @PKG@.GMember byId = g.member(w);
  if (byId != null) return byId;
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    if (m.name != null && m.name.equalsIgnoreCase(w)) return m;
  }
  @PR@ p = onlineByName(w);
  if (p != null) return g.member(p.getUuid().toString());
  return null;
}""")
# ---- SkyyCoins bridge (coins:fn:* act on the ACTIVE profile; null = purse unreadable / SkyyCoins refused, nothing changed)
M(gs, r"""
public static boolean coinsReady() {
  java.util.Map b = bridge();
  return b.get("coins:fn:get") instanceof java.util.function.Function
      && b.get("coins:fn:add") instanceof java.util.function.Function
      && b.get("coins:fn:take") instanceof java.util.function.Function;
}""")
M(gs, r"""
public static Long coinsGet(java.util.UUID u) {
  try {
    Object f = bridge().get("coins:fn:get");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(u);
    return r instanceof Number ? Long.valueOf(((Number) r).longValue()) : null;
  } catch (Throwable t) { return null; }
}""")
M(gs, r"""
public static Object coinsTake(java.util.UUID u, long n) {
  try {
    Object f = bridge().get("coins:fn:take");
    if (!(f instanceof java.util.function.Function)) return null;
    return ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
  } catch (Throwable t) { warn("coins:fn:take failed: " + t); return null; }
}""")
M(gs, r"""
public static boolean coinsAdd(java.util.UUID u, long n) {
  try {
    Object f = bridge().get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(n) });
    return r instanceof Number;
  } catch (Throwable t) { warn("coins:fn:add failed: " + t); return false; }
}""")
# 500, 2k, 1.5m, 2b, 1,000, all / max, half; throws on text that is not a number
M(gs, r"""
public static long parseAmount(String s, long all) {
  String t = s == null ? "" : s.trim().toLowerCase().replace(",", "").replace("_", "");
  if (t.equals("all") || t.equals("max") || t.equals("everything")) return all;
  if (t.equals("half")) return all / 2L;
  double mult = 1.0;
  if (t.endsWith("k")) { mult = 1000.0; t = t.substring(0, t.length() - 1); }
  else if (t.endsWith("m")) { mult = 1000000.0; t = t.substring(0, t.length() - 1); }
  else if (t.endsWith("b")) { mult = 1000000000.0; t = t.substring(0, t.length() - 1); }
  if (t.length() == 0) throw new IllegalArgumentException("empty amount");
  double d = Double.parseDouble(t);
  if (Double.isNaN(d) || Double.isInfinite(d)) throw new IllegalArgumentException("not a number");
  double v = d * mult;
  if (v < 1.0) return 0L;
  if (v > 9.0E15) return Long.MAX_VALUE;
  return (long) Math.floor(v);
}""")

# ================= operations (commands and the page call these; u + username so they also run in a bare-JVM test) =================
M(gs, r"""
public static synchronized String create(java.util.UUID u, String uname, String raw) {
  String us = u.toString();
  if (BYPLAYER.containsKey(us)) return "-You are already in a guild. Leave it first with /guild leave.";
  String name = norm(raw);
  String err = nameError(name);
  if (err != null) return "-" + err;
  String low = name.toLowerCase();
  if (BYNAME.containsKey(low)) return "-A guild called " + name + " already exists. Pick another name.";
  long now = System.currentTimeMillis();
  @PKG@.Guild g = new @PKG@.Guild();
  g.id = "g" + NEXT_ID;
  while (GUILDS.containsKey(g.id)) { NEXT_ID = NEXT_ID + 1L; g.id = "g" + NEXT_ID; }
  NEXT_ID = NEXT_ID + 1L;
  saveMeta();
  g.name = name;
  g.created = now;
  @PKG@.GMember m = new @PKG@.GMember();
  m.uuid = us; m.uid = u; m.name = uname; m.rank = 2; m.joined = now;
  g.members.put(us, m);
  GUILDS.put(g.id, g);
  BYNAME.put(low, g.id);
  BYPLAYER.put(us, g.id);
  INVITES.remove(us);
  saveGuild(g);
  saveIndex();
  publishGuild(g);
  info(uname + " (" + us + ") founded guild " + g.id + " '" + name + "'");
  return "+You founded " + name + "! You are its Leader. Invite players with /guild invite <player> - /guild opens the guild page.";
}""")
M(gs, r"""
public static synchronized String setTag(java.util.UUID u, String uname, String raw) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.member(us).rank < 2) return "-Only the Leader can change the guild tag.";
  String t = raw == null ? "" : raw.trim();
  String lt = t.toLowerCase();
  if (lt.equals("clear") || lt.equals("none") || lt.equals("remove") || lt.equals("off")) {
    g.tag = "";
    saveGuild(g);
    publishGuild(g);
    broadcast(g, "[Guild] " + uname + " removed the guild tag.", "#cfe3ff", us);
    return "+The guild tag is removed.";
  }
  String err = tagError(t);
  if (err != null) return "-" + err + " (/guild tag clear removes it)";
  t = t.toUpperCase();
  java.util.Iterator it = GUILDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.Guild o = (@PKG@.Guild) it.next();
    if (o != g && o.tag != null && o.tag.equalsIgnoreCase(t)) return "-Another guild already uses the tag [" + t + "].";
  }
  g.tag = t;
  saveGuild(g);
  publishGuild(g);
  broadcast(g, "[Guild] " + uname + " set the guild tag to [" + t + "].", "#8fe39a", us);
  return "+The guild tag is now [" + t + "].";
}""")
M(gs, r"""
public static synchronized String invite(java.util.UUID u, String uname, String who) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild. Create one with /guild create <name>.";
  if (g.member(us).rank < 1) return "-Only the Leader and Officers can invite players.";
  if (g.members.size() >= @PKG@.GCfg.MAX_MEMBERS) return "-Your guild is full (" + @PKG@.GCfg.MAX_MEMBERS + " members).";
  String w = who == null ? "" : who.trim();
  if (w.length() == 0) return "-Type the name of the player to invite.";
  @PR@ t = onlineByName(w);
  if (t == null) return "-No online player called " + clean(w) + ". They must be online to get an invite.";
  String tu = t.getUuid().toString();
  if (tu.equals(us)) return "-You can't invite yourself.";
  if (g.member(tu) != null) return "-" + t.getUsername() + " is already in your guild.";
  if (BYPLAYER.containsKey(tu)) return "-" + t.getUsername() + " is already in another guild.";
  long exp = System.currentTimeMillis() + (long) @PKG@.GCfg.INVITE_SECONDS * 1000L;
  INVITES.put(tu, new Object[] { g.id, uname, Long.valueOf(exp) });
  say(t, "[Guild] " + uname + " invited you to join " + g.name + tagText(g) + "! Type /guild accept (or open /guild) within " + mins() + " - /guild decline says no.", "#ffd070");
  broadcast(g, "[Guild] " + uname + " invited " + t.getUsername() + " to the guild.", "#cfe3ff", us);
  return "+Invited " + t.getUsername() + " to " + g.name + ". The invite lasts " + mins() + ".";
}""")
M(gs, r"""
public static synchronized String accept(java.util.UUID u, String uname) {
  String us = u.toString();
  if (BYPLAYER.containsKey(us)) return "-You are already in a guild. Leave it first with /guild leave.";
  Object[] inv = (Object[]) INVITES.remove(us);
  if (inv == null || ((Long) inv[2]).longValue() < System.currentTimeMillis()) return "-You have no guild invite right now (invites last " + mins() + ").";
  @PKG@.Guild g = (@PKG@.Guild) GUILDS.get(inv[0]);
  if (g == null) return "-That guild no longer exists.";
  if (g.members.size() >= @PKG@.GCfg.MAX_MEMBERS) return "-" + g.name + " is full.";
  @PKG@.GMember m = new @PKG@.GMember();
  m.uuid = us; m.uid = u; m.name = uname; m.rank = 0; m.joined = System.currentTimeMillis();
  g.members.put(us, m);
  BYPLAYER.put(us, g.id);
  saveGuild(g);
  saveIndex();
  publishGuild(g);
  broadcast(g, "[Guild] " + uname + " joined the guild!", "#8fe39a", us);
  info(uname + " (" + us + ") joined guild " + g.id + " '" + g.name + "'");
  return "+Welcome to " + g.name + tagText(g) + "! /gc <message> talks to your guild - /guild opens the guild page.";
}""")
M(gs, r"""
public static synchronized String decline(java.util.UUID u, String uname) {
  Object[] inv = (Object[]) INVITES.remove(u.toString());
  if (inv == null) return "-You have no guild invite right now.";
  @PKG@.Guild g = (@PKG@.Guild) GUILDS.get(inv[0]);
  if (g == null) return "=That guild no longer exists.";
  broadcast(g, "[Guild] " + uname + " declined the guild invite.", "#cfe3ff", null);
  return "=You declined the invite to " + g.name + ".";
}""")
M(gs, r"""
public static synchronized void removeMember(@PKG@.Guild g, String us) {
  g.members.remove(us);
  BYPLAYER.remove(us);
  unpublish(us);
}""")
M(gs, r"""
public static synchronized @PKG@.GMember successor(@PKG@.Guild g, String exceptU) {
  @PKG@.GMember best = null;
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    if (m.uuid.equals(exceptU)) continue;
    if (best == null || m.rank > best.rank || (m.rank == best.rank && m.joined < best.joined)) best = m;
  }
  return best;
}""")
# a removed guild's file: final state marked disbanded=<millis>, then moved to guilds/deleted/ (never loaded again, never hard-deleted)
M(gs, r"""
public static synchronized boolean archive(@PKG@.Guild g) {
  long now = System.currentTimeMillis();
  java.nio.file.Path f = GDIR.resolve(g.id + ".properties");
  try {
    java.util.Properties p = propsOf(g);
    p.setProperty("disbanded", String.valueOf(now));
    writeProps(f, p, "SkyyGuilds guild file - DISBANDED, kept for the record only");
    java.nio.file.Path dd = GDIR.resolve("deleted");
    java.nio.file.Files.createDirectories(dd, new java.nio.file.attribute.FileAttribute[0]);
    replaceFile(f, dd.resolve(g.id + "-" + now + ".properties"));
    return true;
  } catch (Throwable t) {
    warn("could not archive guild file " + g.id + " (if it still exists it is marked disbanded and will not load): " + t);
    return false;
  }
}""")
# Disband: (1) the guild file is rewritten as disbanded with bank 0 BEFORE any coin moves (a failed write refuses the disband, nothing
# changed), (2) the bank is paid to payTo (the Leader) - a failed payout restores the live file and refuses, (3) the file moves to
# guilds/deleted/. The file on disk never shows more coins than exist, so a crash can never pay the same bank twice.
M(gs, r"""
public static synchronized String disbandNow(@PKG@.Guild g, java.util.UUID payTo, String payName, String actorU, String by) {
  long amt = g.bank;
  if (amt > 0L && (payTo == null || !coinsReady())) return "-The guild bank still holds " + amt + " coins and SkyyCoins is not available to pay them out, so " + g.name + " was NOT disbanded.";
  try {
    java.util.Properties p = propsOf(g);
    p.setProperty("bank", "0");
    p.setProperty("disbanded", String.valueOf(System.currentTimeMillis()));
    writeProps(GDIR.resolve(g.id + ".properties"), p, "SkyyGuilds guild file - DISBANDED (" + amt + " bank coins paid to " + payName + "), kept for the record only");
  } catch (Throwable t) {
    warn("disband of " + g.id + " refused: the guild file could not be written: " + t);
    return "-The guild file could not be written, so " + g.name + " was NOT disbanded (nothing changed). Try again.";
  }
  long paid = 0L;
  if (amt > 0L) {
    if (!coinsAdd(payTo, amt)) {
      g.dirty = true;
      saveGuild(g);
      return "-SkyyCoins could not pay the guild bank's " + amt + " coins out, so " + g.name + " was NOT disbanded. Try again.";
    }
    g.bank = 0L;
    paid = amt;
    addLog(g, payName, "disband-payout", amt);
  }
  archive(g);
  GUILDS.remove(g.id);
  if (g.id.equals(BYNAME.get(g.name.toLowerCase()))) BYNAME.remove(g.name.toLowerCase());
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    BYPLAYER.remove(m.uuid);
    unpublish(m.uuid);
    if (actorU == null || !actorU.equals(m.uuid)) sayU(m.uid, "[Guild] " + g.name + " was disbanded by " + by + ".", "#ffd070");
  }
  java.util.Iterator ii = INVITES.entrySet().iterator();
  while (ii.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) ii.next();
    Object[] v = (Object[]) e.getValue();
    if (v != null && g.id.equals(v[0])) ii.remove();
  }
  saveIndex();
  info(g.name + " (" + g.id + ") disbanded by " + by + (paid > 0L ? ", bank " + paid + " coins paid to " + payName : ""));
  boolean self = actorU != null && payTo != null && actorU.equals(payTo.toString());
  return "+" + g.name + " is disbanded." + (paid > 0L ? " The guild bank's " + paid + " coins went to " + (self ? "your purse." : payName + "'s purse.") : "");
}""")
M(gs, r"""
public static synchronized String leaveWarning(java.util.UUID u) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  @PKG@.GMember me = g.member(us);
  if (me.rank == 2 && g.members.size() <= 1) return "=You are the last member: leaving DISBANDS " + g.name + (g.bank > 0L ? " and pays the bank's " + g.bank + " coins to your purse" : "") + ". Click Leave again within 10 s.";
  if (me.rank == 2) return "=Leaving makes " + successor(g, us).name + " the new Leader. Click Leave again within 10 s.";
  return "=Click Leave again within 10 s to leave " + g.name + ".";
}""")
M(gs, r"""
public static synchronized String disbandWarning(java.util.UUID u) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.member(us).rank < 2) return "-Only the Leader can disband the guild.";
  return "=Disbanding deletes " + g.name + " for all " + g.members.size() + " members" + (g.bank > 0L ? " and pays the bank's " + g.bank + " coins to your purse" : "") + ". Click Disband again within 10 s.";
}""")
M(gs, r"""
public static synchronized String leave(java.util.UUID u, String uname, boolean confirmed) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  @PKG@.GMember me = g.member(us);
  if (me.rank == 2 && g.members.size() <= 1) {
    if (!confirmed && !confirm("leave:" + us)) return "=You are the last member, so leaving DISBANDS " + g.name + (g.bank > 0L ? " and pays the guild bank's " + g.bank + " coins into your purse" : "") + ". Type /guild leave again within 10 s to confirm.";
    return disbandNow(g, u, uname, us, uname);
  }
  if (me.rank == 2) {
    @PKG@.GMember s = successor(g, us);
    if (!confirmed && !confirm("leave:" + us)) return "=You are the Leader: leaving makes " + s.name + " the new Leader. Type /guild leave again within 10 s to confirm.";
    s.rank = 2;
    removeMember(g, us);
    saveGuild(g);
    saveIndex();
    publishGuild(g);
    sayU(s.uid, "[Guild] " + uname + " left - you are the Leader of " + g.name + " now!", "#ffe08a");
    broadcast(g, "[Guild] " + uname + " left the guild. " + s.name + " is the new Leader.", "#ffd070", s.uuid);
    return "+You left " + g.name + ". " + s.name + " is its new Leader.";
  }
  removeMember(g, us);
  saveGuild(g);
  saveIndex();
  publishGuild(g);
  broadcast(g, "[Guild] " + uname + " left the guild.", "#cfe3ff", null);
  return "+You left " + g.name + ".";
}""")
M(gs, r"""
public static synchronized String kick(java.util.UUID u, String uname, String who) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  @PKG@.GMember me = g.member(us);
  if (me.rank < 1) return "-Only the Leader and Officers can kick members.";
  @PKG@.GMember t = findMember(g, who);
  if (t == null) return "-Nobody called " + clean(who) + " is in your guild.";
  if (t.uuid.equals(us)) return "-You can't kick yourself - use /guild leave.";
  if (t.rank >= me.rank) return "-You can only kick members ranked below you (" + t.name + " is " + rankName(t.rank) + ").";
  removeMember(g, t.uuid);
  saveGuild(g);
  saveIndex();
  publishGuild(g);
  sayU(t.uid, "[Guild] You were removed from " + g.name + " by " + uname + ".", "#ff9d6b");
  broadcast(g, "[Guild] " + t.name + " was removed from the guild by " + uname + ".", "#ffd070", us);
  info(uname + " kicked " + t.name + " from " + g.id);
  return "+Removed " + t.name + " from the guild.";
}""")
M(gs, r"""
public static synchronized String promote(java.util.UUID u, String uname, String who) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.member(us).rank < 2) return "-Only the Leader can promote members.";
  @PKG@.GMember t = findMember(g, who);
  if (t == null) return "-Nobody called " + clean(who) + " is in your guild.";
  if (t.uuid.equals(us)) return "-You are the Leader already.";
  if (t.rank >= 1) return "-" + t.name + " is already an Officer. /guild transfer " + t.name + " makes them the Leader.";
  t.rank = 1;
  saveGuild(g);
  publishGuild(g);
  sayU(t.uid, "[Guild] " + uname + " promoted you to Officer: you can invite, kick Members and withdraw from the guild bank.", "#8fe39a");
  broadcast(g, "[Guild] " + t.name + " is now an Officer.", "#cfe3ff", us + "," + t.uuid);
  return "+" + t.name + " is now an Officer.";
}""")
M(gs, r"""
public static synchronized String demote(java.util.UUID u, String uname, String who) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.member(us).rank < 2) return "-Only the Leader can demote Officers.";
  @PKG@.GMember t = findMember(g, who);
  if (t == null) return "-Nobody called " + clean(who) + " is in your guild.";
  if (t.rank == 2) return "-The Leader can't be demoted - /guild transfer <player> hands the guild over.";
  if (t.rank == 0) return "-" + t.name + " is already a Member.";
  t.rank = 0;
  saveGuild(g);
  publishGuild(g);
  sayU(t.uid, "[Guild] " + uname + " made you a Member again.", "#ffd070");
  broadcast(g, "[Guild] " + t.name + " is now a Member.", "#cfe3ff", us + "," + t.uuid);
  return "+" + t.name + " is now a Member.";
}""")
M(gs, r"""
public static synchronized String transfer(java.util.UUID u, String uname, String who, boolean confirmed) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  @PKG@.GMember me = g.member(us);
  if (me.rank < 2) return "-Only the Leader can hand the guild over.";
  @PKG@.GMember t = findMember(g, who);
  if (t == null) return "-Nobody called " + clean(who) + " is in your guild.";
  if (t.uuid.equals(us)) return "-You are the Leader already.";
  if (!confirmed && !confirm("transfer:" + us + ":" + t.uuid)) return "=This makes " + t.name + " the Leader of " + g.name + " (you become an Officer). Type the same command again within 10 s to confirm.";
  t.rank = 2;
  me.rank = 1;
  saveGuild(g);
  publishGuild(g);
  sayU(t.uid, "[Guild] " + uname + " made you the Leader of " + g.name + "!", "#ffe08a");
  broadcast(g, "[Guild] " + t.name + " is the new Leader (" + uname + " is now an Officer).", "#ffd070", us + "," + t.uuid);
  info(uname + " handed " + g.id + " to " + t.name);
  return "+" + t.name + " is now the Leader of " + g.name + ". You are an Officer.";
}""")
M(gs, r"""
public static synchronized String disband(java.util.UUID u, String uname, boolean confirmed) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.member(us).rank < 2) return "-Only the Leader can disband the guild.";
  if (!confirmed && !confirm("disband:" + us)) return "=This deletes " + g.name + " for every member" + (g.bank > 0L ? " and pays the guild bank's " + g.bank + " coins into your purse" : "") + ". Type /guild disband again within 10 s to confirm.";
  return disbandNow(g, u, uname, us, uname);
}""")
# deposit: take from the purse FIRST (coins:fn:take must say TRUE), then add to the bank
M(gs, r"""
public static synchronized String deposit(java.util.UUID u, String uname, String amountText) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (!coinsReady()) return "-SkyyCoins is not loaded, so the guild bank cannot move coins.";
  Long purse = coinsGet(u);
  if (purse == null) return "-Your purse cannot be read right now - nothing moved. Try again.";
  long n;
  try { n = parseAmount(amountText, purse.longValue()); }
  catch (Throwable t) { return "-That is not an amount. Use e.g. 500, 2k, 1.5m or all."; }
  if (n <= 0L) return "-Nothing to deposit (your purse has " + purse + " coins).";
  if (n > purse.longValue()) return "-Not enough coins in your purse (" + purse + ").";
  if (g.bank > @PKG@.GCfg.MAX_BANK - n) return "-The guild bank can hold at most " + @PKG@.GCfg.MAX_BANK + " coins (it has " + g.bank + ").";
  Object r = coinsTake(u, n);
  if (!(r instanceof Boolean)) return "-SkyyCoins could not take the coins (purse unreadable?) - nothing moved.";
  if (!((Boolean) r).booleanValue()) return "-Not enough coins in your purse.";
  g.bank = g.bank + n;
  addLog(g, uname, "deposit", n);
  saveGuild(g);
  broadcast(g, "[Guild] " + uname + " deposited " + n + " coins. Guild bank: " + g.bank + ".", "#ffd070", us);
  Long after = coinsGet(u);
  return "+Deposited " + n + " coins. Guild bank: " + g.bank + " - your purse: " + (after == null ? "?" : String.valueOf(after)) + ".";
}""")
# withdraw: the lower bank is WRITTEN first (a failed write = nothing moved), then coins:fn:add; if SkyyCoins did not add, the exact
# amount goes back and is written again. The file never shows coins that already left the bank.
M(gs, r"""
public static synchronized String withdraw(java.util.UUID u, String uname, String amountText) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild.";
  if (g.member(us).rank < 1) return "-Only the Leader and Officers can withdraw from the guild bank.";
  if (!coinsReady()) return "-SkyyCoins is not loaded, so the guild bank cannot move coins.";
  long n;
  try { n = parseAmount(amountText, g.bank); }
  catch (Throwable t) { return "-That is not an amount. Use e.g. 500, 2k, 1.5m or all."; }
  if (n <= 0L) return "-Nothing to withdraw (the guild bank has " + g.bank + " coins).";
  if (n > g.bank) return "-The guild bank only has " + g.bank + " coins.";
  g.bank = g.bank - n;
  if (!saveGuild(g)) {
    g.bank = g.bank + n;
    return "-The guild file could not be written - nothing moved (guild bank: " + g.bank + "). Try again.";
  }
  if (!coinsAdd(u, n)) {
    g.bank = g.bank + n;
    saveGuild(g);
    warn("withdraw of " + n + " for " + uname + " (" + us + ") from " + g.id + " refused by SkyyCoins - bank restored to " + g.bank);
    return "-SkyyCoins could not put the coins in your purse - nothing moved (guild bank: " + g.bank + ").";
  }
  addLog(g, uname, "withdraw", n);
  saveGuild(g);
  broadcast(g, "[Guild] " + uname + " withdrew " + n + " coins. Guild bank: " + g.bank + ".", "#ffd070", us);
  Long after = coinsGet(u);
  return "+Withdrew " + n + " coins. Guild bank: " + g.bank + " - your purse: " + (after == null ? "?" : String.valueOf(after)) + ".";
}""")
M(gs, r"""
public static synchronized String chat(java.util.UUID u, String uname, String msg) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return "-You are not in a guild. /guild create <name> or ask for an invite.";
  String m = msg == null ? "" : msg.trim();
  if (m.length() == 0) return "-Usage: /gc <message>";
  if (m.length() > 256) m = m.substring(0, 256);
  int r = g.member(us).rank;
  String rk = r == 2 ? "[Leader] " : (r == 1 ? "[Officer] " : "");
  broadcast(g, "[Guild] " + rk + uname + ": " + m, "#7fe0a0", null);
  return null;
}""")
M(gs, r"""
public static String logText(String line) {
  try {
    String[] v = line.split("\\|", 5);
    long ms = parseLong(v[0], 0L);
    String when = new java.text.SimpleDateFormat("MM-dd HH:mm").format(new java.util.Date(ms));
    String act = v[2];
    String verb = act.equals("deposit") ? "deposited" : (act.equals("withdraw") ? "withdrew" : (act.equals("disband-payout") ? "was paid out" : act));
    return when + "   " + v[1] + " " + verb + " " + v[3] + " coins   (bank " + v[4] + ")";
  } catch (Throwable t) { return line; }
}""")
M(gs, r"""
public static synchronized String[] infoLines(java.util.UUID u) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return new String[] { "=You are not in a guild. /guild create <name> starts one, or ask a Leader or Officer for an invite." };
  long[] li = levelInfo(g.xp);
  StringBuilder lead = new StringBuilder();
  StringBuilder offs = new StringBuilder();
  StringBuilder mems = new StringBuilder();
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    String n = m.name + (online(m.uid) != null ? "*" : "");
    StringBuilder sb = m.rank == 2 ? lead : (m.rank == 1 ? offs : mems);
    if (sb.length() > 0) sb.append(", ");
    sb.append(n);
  }
  return new String[] {
    "=" + g.name + tagText(g) + " - level " + li[0] + " (" + li[1] + " / " + li[2] + " XP to level " + (li[0] + 1L) + ") - season " + SEASON + ": " + g.seasonXp(SEASON) + " XP",
    "=Guild bank: " + g.bank + " coins - " + g.members.size() + " / " + @PKG@.GCfg.MAX_MEMBERS + " members, " + onlineCount(g) + " online (*)",
    "=Leader: " + lead + (offs.length() > 0 ? " - Officers: " + offs : "") + (mems.length() > 0 ? " - Members: " + mems : ""),
    "=You are " + rankName(g.member(us).rank) + ". /guild opens the guild page, /gc <message> is guild chat."
  };
}""")
M(gs, r"""
public static synchronized String[] bankLines(java.util.UUID u) {
  @PKG@.Guild g = guildOf(u.toString());
  if (g == null) return new String[] { "-You are not in a guild." };
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("=Guild bank of " + g.name + ": " + g.bank + " coins. /guild bank deposit <amount> - /guild bank withdraw <amount> (Leader / Officer).");
  int from = g.log.size() - 5;
  if (from < 0) from = 0;
  for (int i = g.log.size() - 1; i >= from; i--) out.add("=  " + logText((String) g.log.get(i)));
  if (g.log.size() == 0) out.add("=  No deposits or withdrawals yet.");
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
M(gs, r"""
public static synchronized String[] listLines() {
  java.util.ArrayList all = new java.util.ArrayList(GUILDS.values());
  for (int i = 1; i < all.size(); i++) {
    @PKG@.Guild x = (@PKG@.Guild) all.get(i);
    int j = i - 1;
    while (j >= 0 && ((@PKG@.Guild) all.get(j)).xp < x.xp) { all.set(j + 1, all.get(j)); j--; }
    all.set(j + 1, x);
  }
  if (all.size() == 0) return new String[] { "=There are no guilds yet. /guild create <name> founds the first one." };
  int n = all.size() < 10 ? all.size() : 10;
  String[] r = new String[n + 1];
  r[0] = "=Top guilds (" + all.size() + " in total):";
  for (int i = 0; i < n; i++) {
    @PKG@.Guild g = (@PKG@.Guild) all.get(i);
    r[i + 1] = "=  " + (i + 1) + ". " + g.name + tagText(g) + " - level " + levelInfo(g.xp)[0] + " - " + g.members.size() + " members";
  }
  return r;
}""")
M(gs, r"""
public static String[] helpLines() {
  return new String[] {
    "=/guild - the guild page.  /guild create <name>  /guild accept  /guild decline  /guild list  /guild info",
    "=/gc <message> - guild chat.  /guild bank  /guild bank deposit <amount>  /guild bank withdraw <amount> (Leader/Officer)",
    "=Leader/Officer: /guild invite|kick <player>.  Leader: /guild promote|demote|transfer <player>  /guild tag <tag>  /guild disband",
    "=/guild leave. Amounts: 500, 2k, 1.5m or all. Guild XP = " + @PKG@.GCfg.SHARE + "% of the skill XP every member earns."
  };
}""")
M(gs, r"""
public static synchronized long addXp(String gid, String us, long n) {
  if (n <= 0L) return 0L;
  @PKG@.Guild g = (@PKG@.Guild) GUILDS.get(gid);
  if (g == null) return 0L;
  @PKG@.GMember m = us == null ? null : g.member(us);
  if (us != null && m == null) return 0L;
  long before = levelInfo(g.xp)[0];
  long nx = g.xp + n;
  if (nx < g.xp) nx = Long.MAX_VALUE / 4L;
  g.xp = nx;
  g.addSeason(SEASON, n);
  if (m != null) m.contrib = m.contrib + n;
  g.dirty = true;
  publishGuild(g);
  long after = levelInfo(g.xp)[0];
  if (after > before) {
    broadcast(g, "[Guild] " + g.name + " reached guild level " + after + "!", "#ffe08a", null);
    info(g.id + " '" + g.name + "' reached level " + after);
  }
  return n;
}""")
# tick (every 5 s) for each online player: stored name refresh + republish; true = in a guild
M(gs, r"""
public static synchronized boolean touch(java.util.UUID u, String uname) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) { unpublish(us); return false; }
  @PKG@.GMember m = g.member(us);
  if (uname != null && uname.length() > 0 && !uname.equals(m.name)) { m.name = uname; g.dirty = true; }
  java.util.Map b = bridge();
  b.put("guild:" + us, g.name);
  b.put("guild:info:" + us, infoString(g, m, onlineCount(g)));
  return true;
}""")
M(gs, r"""
public static synchronized void welcome(@PR@ pr) {
  String us = pr.getUuid().toString();
  @PKG@.Guild g = guildOf(us);
  if (g != null) {
    say(pr, "[Guild] " + g.name + tagText(g) + " - level " + levelInfo(g.xp)[0] + " - " + onlineCount(g) + " of " + g.members.size() + " members online. /gc <message> talks to them, /guild opens the guild page.", "#8fe39a");
    if (@PKG@.GCfg.ONLINE_MSG) broadcast(g, "[Guild] " + pr.getUsername() + " is online.", "#9fb8d0", us);
    return;
  }
  Object[] inv = (Object[]) INVITES.get(us);
  if (inv != null) {
    @PKG@.Guild ig = (@PKG@.Guild) GUILDS.get(inv[0]);
    if (ig != null) say(pr, "[Guild] You have an invite to " + ig.name + tagText(ig) + " from " + inv[1] + ": /guild accept or /guild decline.", "#ffd070");
  }
}""")
M(gs, r"""
public static synchronized void wentOffline(java.util.UUID u) {
  if (!@PKG@.GCfg.ONLINE_MSG) return;
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return;
  broadcast(g, "[Guild] " + g.member(us).name + " went offline.", "#9fb8d0", us);
  publishGuild(g);
}""")
M(gs, r"""
public static synchronized void flushDirty() {
  java.util.Iterator it = GUILDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.Guild g = (@PKG@.Guild) it.next();
    if (g.dirty) saveGuild(g);
  }
}""")
M(gs, r"""
public static int cmpRow(String[] a, String[] b) {
  int ra = Integer.parseInt(a[2]);
  int rb = Integer.parseInt(b[2]);
  if (ra != rb) return rb - ra;
  if (!a[4].equals(b[4])) return a[4].equals("1") ? -1 : 1;
  return a[1].compareToIgnoreCase(b[1]);
}""")
M(gs, r"""
public static void sortRows(java.util.ArrayList rows) {
  for (int i = 1; i < rows.size(); i++) {
    String[] x = (String[]) rows.get(i);
    int j = i - 1;
    while (j >= 0 && cmpRow((String[]) rows.get(j), x) > 0) { rows.set(j + 1, rows.get(j)); j--; }
    rows.set(j + 1, x);
  }
}""")
# page data: {name, tag, Long xp, Long bank, Integer myRank, rows String[]{uuid, name, rank, contrib, online 1/0}, log, Long seasonXp,
# Integer season, Integer online, id}
M(gs, r"""
public static synchronized Object[] snapshot(java.util.UUID u) {
  String us = u.toString();
  @PKG@.Guild g = guildOf(us);
  if (g == null) return null;
  java.util.ArrayList rows = new java.util.ArrayList();
  int onl = 0;
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    boolean on = online(m.uid) != null;
    if (on) onl++;
    rows.add(new String[] { m.uuid, m.name == null ? "?" : m.name, String.valueOf(m.rank), String.valueOf(m.contrib), on ? "1" : "0" });
  }
  sortRows(rows);
  return new Object[] { g.name, g.tag == null ? "" : g.tag, Long.valueOf(g.xp), Long.valueOf(g.bank), Integer.valueOf(g.member(us).rank), rows,
                        new java.util.ArrayList(g.log), Long.valueOf(g.seasonXp(SEASON)), Integer.valueOf(SEASON), Integer.valueOf(onl), g.id };
}""")
M(gs, r"""
public static synchronized Object[] inviteFor(java.util.UUID u) {
  Object[] inv = (Object[]) INVITES.get(u.toString());
  if (inv == null) return null;
  long left = ((Long) inv[2]).longValue() - System.currentTimeMillis();
  if (left <= 0L) { INVITES.remove(u.toString()); return null; }
  @PKG@.Guild g = (@PKG@.Guild) GUILDS.get(inv[0]);
  if (g == null) return null;
  return new Object[] { g.name, g.tag == null ? "" : g.tag, Long.valueOf(levelInfo(g.xp)[0]), Integer.valueOf(g.members.size()), inv[1], Long.valueOf(left) };
}""")
M(gs, r"""
public static synchronized String nameOfMember(java.util.UUID u, String target) {
  @PKG@.Guild g = guildOf(u.toString());
  if (g == null) return "?";
  @PKG@.GMember m = g.member(target);
  return m == null ? "?" : m.name;
}""")
M(gs, r"""
public static synchronized java.util.ArrayList memberList(String us) {
  @PKG@.Guild g = guildOf(us);
  if (g == null) return null;
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    out.add(new Object[] { m.uid, m.name });
  }
  return out;
}""")
# guild:fn:online - the membership copy is taken under the lock, the online checks run outside it
M(gs, r"""
public static String[] onlineNames(java.util.UUID u) {
  java.util.ArrayList ms = memberList(u.toString());
  if (ms == null) return new String[0];
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < ms.size(); i++) {
    Object[] e = (Object[]) ms.get(i);
    @PR@ p = online((java.util.UUID) e[0]);
    if (p != null) out.add(p.getUsername() != null ? p.getUsername() : (String) e[1]);
  }
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
# ---- admin
M(gs, r"""
public static synchronized @PKG@.Guild findGuild(String raw) {
  if (raw == null) return null;
  String t = norm(raw);
  if (t.length() == 0) return null;
  Object id = BYNAME.get(t.toLowerCase());
  if (id != null) return (@PKG@.Guild) GUILDS.get(id);
  @PKG@.Guild byId = (@PKG@.Guild) GUILDS.get(t);
  if (byId != null) return byId;
  java.util.Iterator it = GUILDS.values().iterator();
  while (it.hasNext()) {
    @PKG@.Guild g = (@PKG@.Guild) it.next();
    if (g.tag != null && g.tag.length() > 0 && g.tag.equalsIgnoreCase(t)) return g;
  }
  return null;
}""")
M(gs, r"""
public static synchronized String[] adminInfo(String raw) {
  @PKG@.Guild g = findGuild(raw);
  if (g == null) return new String[] { "-No guild called " + clean(raw) + ". /guild list shows the top guilds." };
  long[] li = levelInfo(g.xp);
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("=" + g.name + tagText(g) + " (id " + g.id + ", file guilds/" + g.id + ".properties, created " + java.time.Instant.ofEpochMilli(g.created) + ")");
  out.add("=Level " + li[0] + " (" + li[1] + "/" + li[2] + "), total XP " + g.xp + ", season " + SEASON + " XP " + g.seasonXp(SEASON) + ", bank " + g.bank + " coins");
  java.util.Iterator it = g.members.values().iterator();
  while (it.hasNext()) {
    @PKG@.GMember m = (@PKG@.GMember) it.next();
    out.add("=  " + rankName(m.rank) + " " + m.name + (online(m.uid) != null ? " (online)" : "") + " - " + m.contrib + " guild XP added - " + m.uuid);
  }
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
M(gs, r"""
public static synchronized String adminDelete(java.util.UUID admin, String adminName, String raw) {
  @PKG@.Guild g = findGuild(raw);
  if (g == null) return "-No guild called " + clean(raw) + ".";
  @PKG@.GMember l = g.leader();
  if (!confirm("adel:" + admin + ":" + g.id)) return "=This deletes " + g.name + " (" + g.members.size() + " members" + (g.bank > 0L ? ", its bank's " + g.bank + " coins are paid to its Leader " + (l == null ? "?" : l.name) : "") + "). Type the same command again within 10 s to confirm.";
  return disbandNow(g, l == null ? null : l.uid, l == null ? "?" : l.name, admin.toString(), adminName + " (admin)");
}""")
M(gs, r"""
public static synchronized String[] seasonLines() {
  java.util.ArrayList all = new java.util.ArrayList(GUILDS.values());
  int s = SEASON;
  for (int i = 1; i < all.size(); i++) {
    @PKG@.Guild x = (@PKG@.Guild) all.get(i);
    int j = i - 1;
    while (j >= 0 && ((@PKG@.Guild) all.get(j)).seasonXp(s) < x.seasonXp(s)) { all.set(j + 1, all.get(j)); j--; }
    all.set(j + 1, x);
  }
  int n = all.size() < 10 ? all.size() : 10;
  String[] r = new String[n + 1];
  r[0] = "=Season " + s + " (started " + java.time.Instant.ofEpochMilli(SEASON_START) + "). /guildadmin season next starts season " + (s + 1) + ".";
  for (int i = 0; i < n; i++) {
    @PKG@.Guild g = (@PKG@.Guild) all.get(i);
    r[i + 1] = "=  " + (i + 1) + ". " + g.name + tagText(g) + " - " + g.seasonXp(s) + " season XP (level " + levelInfo(g.xp)[0] + ")";
  }
  return r;
}""")
M(gs, r"""
public static synchronized String seasonNext(java.util.UUID admin, String adminName) {
  if (!confirm("season:" + admin)) return "=This ends season " + SEASON + " and starts season " + (SEASON + 1) + ": every guild's season XP starts at 0 (levels and total XP stay). Type /guildadmin season next again within 10 s to confirm.";
  SEASON = SEASON + 1;
  SEASON_START = System.currentTimeMillis();
  saveMeta();
  info(adminName + " started guild season " + SEASON);
  try {
    @UNI@ un = uni();
    if (un != null) {
      java.util.Iterator it = un.getPlayers().iterator();
      while (it.hasNext()) say((@PR@) it.next(), "[Guilds] Season " + SEASON + " has begun! Every guild's season XP starts again at 0.", "#ffe08a");
    }
  } catch (Throwable t) { }
  return "+Season " + SEASON + " started.";
}""")
M(gs, r"""
public static synchronized String adminXp(String amountText, String raw) {
  long n;
  try { n = parseAmount(amountText, 0L); } catch (Throwable t) { return "-That is not an amount: " + clean(amountText); }
  if (n <= 0L || n > 1000000000000L) return "-Give between 1 and 1000000000000 guild XP.";
  @PKG@.Guild g = findGuild(raw);
  if (g == null) return "-No guild called " + clean(raw) + ".";
  addXp(g.id, null, n);
  return "+Gave " + n + " guild XP to " + g.name + " (now level " + levelInfo(g.xp)[0] + ").";
}""")
M(gs, r"""
public static String[] adminHelp() {
  return new String[] {
    "=/guildadmin info <guild>  -  /guildadmin delete <guild> (repeat to confirm; bank paid to the Leader)",
    "=/guildadmin season  -  /guildadmin season next (repeat to confirm)  -  /guildadmin xp <amount> <guild>  -  /guildadmin reload",
    "=<guild> = name, tag or id (g1). Data: mods/Skyy_SkyyGuilds (guilds/, players.properties, meta.properties, banklog.log, config.properties)."
  };
}""")

# ================= XpTask (the member's own world thread): skill XP delta -> guild XP =================
xpt.addInterface(pool.get("java.lang.Runnable"))
F(xpt, "public @PR@ pr;")
F(xpt, "public static final java.util.concurrent.ConcurrentHashMap BASE = new java.util.concurrent.ConcurrentHashMap();")
F(xpt, "public static final java.util.concurrent.ConcurrentHashMap FRAC = new java.util.concurrent.ConcurrentHashMap();")
F(xpt, "public static volatile boolean WARNED = false;")
C(xpt, "public XpTask(@PR@ pr) { this.pr = pr; }")
# total XP over GCfg.SKILLS through skill:fn:xp; -1 = SkyySkills has no skill:fn:xp
M(xpt, r"""
public static long total(java.util.UUID u) {
  Object f = @PKG@.GuildStore.bridge().get("skill:fn:xp");
  if (!(f instanceof java.util.function.Function)) return -1L;
  long sum = 0L;
  String[] sk = @PKG@.GCfg.SKILLS;
  for (int i = 0; i < sk.length; i++) {
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, sk[i] });
    if (r instanceof Number) {
      long v = ((Number) r).longValue();
      if (v > 0L) sum = sum + v;
    }
  }
  return sum;
}""")
# fallback: the sum of the levels in skill:<uuid> = "Mining:12,Foraging:3,..."; -1 = nothing published
M(xpt, r"""
public static long levels(java.util.UUID u) {
  Object s = @PKG@.GuildStore.bridge().get("skill:" + u.toString());
  if (!(s instanceof String)) return -1L;
  long sum = 0L;
  String[] parts = ((String) s).split(",");
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i];
    int c = p.lastIndexOf(':');
    if (c > 0) sum = sum + Math.max(0L, @PKG@.GuildStore.parseLong(p.substring(c + 1), 0L));
  }
  return sum;
}""")
# delta since the last check for this key; -1 = first sight (baseline only)
M(xpt, r"""
public static synchronized long step(String key, long now) {
  Object last = BASE.get(key);
  BASE.put(key, Long.valueOf(now));
  if (!(last instanceof Long)) return -1L;
  return now - ((Long) last).longValue();
}""")
M(xpt, r"""
public static synchronized long share(String key, long delta, double pct) {
  Object fo = FRAC.get(key);
  double fr = fo instanceof Double ? ((Double) fo).doubleValue() : 0.0;
  double c = (double) delta * pct / 100.0 + fr;
  long whole = (long) Math.floor(c);
  FRAC.put(key, Double.valueOf(c - (double) whole));
  return whole;
}""")
# one check for one player (also used by the bare-JVM test with a null PlayerRef): returns the guild XP added
M(xpt, r"""
public static long check(java.util.UUID u) {
  String gid = @PKG@.GuildStore.gidOf(u.toString());
  if (gid == null) return 0L;
  long t = total(u);
  String mode = "x";
  if (t < 0L) { t = levels(u); mode = "l"; }
  if (t < 0L) return 0L;
  String key = @PKG@.GuildStore.pkey(u) + "|" + gid + "|" + mode;
  long d = step(key, t);
  if (d <= 0L) return 0L;
  if (d > @PKG@.GCfg.MAX_DELTA) d = @PKG@.GCfg.MAX_DELTA;
  long gain = mode.equals("x") ? share(key, d, (double) @PKG@.GCfg.SHARE) : d * @PKG@.GCfg.LEVEL_FALLBACK;
  if (gain <= 0L) return 0L;
  return @PKG@.GuildStore.addXp(gid, u.toString(), gain);
}""")
M(xpt, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    check(this.pr.getUuid());
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; @PKG@.GuildStore.warn("guild XP check failed (logged once): " + t); }
  }
}""")

# ================= GuildTick (scheduler, every 5 s) =================
tick.addInterface(pool.get("java.lang.Runnable"))
F(tick, "public int runs = 0;")
F(tick, "public static final java.util.HashSet SEEN = new java.util.HashSet();")
F(tick, "public static final java.util.HashMap MISS = new java.util.HashMap();")
F(tick, "public static volatile long WARNED = 0L;")
C(tick, "public GuildTick() { }")
M(tick, r"""
public static void prune(java.util.concurrent.ConcurrentHashMap m, boolean invites, long now) {
  java.util.Iterator it = m.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    long exp = 0L;
    if (invites && v instanceof Object[]) exp = ((Long) ((Object[]) v)[2]).longValue();
    else if (v instanceof Long) exp = ((Long) v).longValue();
    if (exp < now) it.remove();
  }
}""")
# World.execute throws IllegalThreadStateException once a world stops accepting tasks: each player in its own try (SkyyCoins 0.1.5)
M(tick, r"""
public static void dispatch(@PR@ pr) {
  try {
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @UNI@ un = @PKG@.GuildStore.uni();
    if (un == null) return;
    @WLD@ w = un.getWorld(wu);
    if (w == null) return;
    w.execute(new @PKG@.XpTask(pr));
  } catch (Throwable t) {
    long now = System.currentTimeMillis();
    if (now - WARNED > 60000L) { WARNED = now; @PKG@.GuildStore.warn("guild XP check not dispatched (retried): " + t); }
  }
}""")
# presence: this tick's online set -> {newly online (welcome), gone for two ticks in a row (went offline)}; a relog or a one-tick
# hiccup inside 10 s says nothing. Static + synchronized so the bare-JVM test can drive it without a Universe.
M(tick, r"""
public static synchronized java.util.ArrayList[] presence(java.util.HashSet online) {
  java.util.ArrayList fresh = new java.util.ArrayList();
  java.util.ArrayList gone = new java.util.ArrayList();
  java.util.Iterator oi = online.iterator();
  while (oi.hasNext()) {
    Object u = oi.next();
    if (!SEEN.contains(u)) fresh.add(u);
    MISS.remove(u);
  }
  java.util.HashSet keep = new java.util.HashSet(online);
  java.util.Iterator si = SEEN.iterator();
  while (si.hasNext()) {
    Object o = si.next();
    if (online.contains(o)) continue;
    Object mc = MISS.get(o);
    int miss = (mc instanceof Integer ? ((Integer) mc).intValue() : 0) + 1;
    if (miss >= 2) { MISS.remove(o); gone.add(o); }
    else { MISS.put(o, Integer.valueOf(miss)); keep.add(o); }
  }
  SEEN.clear();
  SEEN.addAll(keep);
  return new java.util.ArrayList[] { fresh, gone };
}""")
M(tick, r"""
public void run() {
  try {
    this.runs = this.runs + 1;
    long now = System.currentTimeMillis();
    prune(@PKG@.GuildStore.INVITES, true, now);
    prune(@PKG@.GuildStore.CONFIRM, false, now);
    @UNI@ un = @PKG@.GuildStore.uni();
    if (un == null) return;
    int every = @PKG@.GCfg.POLL / 5;
    if (every < 1) every = 1;
    boolean poll = this.runs % every == 0;
    java.util.HashSet online = new java.util.HashSet();
    java.util.HashMap refs = new java.util.HashMap();
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      refs.put(u, pr);
      boolean member = false;
      try { member = @PKG@.GuildStore.touch(u, pr.getUsername()); } catch (Throwable t) { }
      if (member && poll) dispatch(pr);
    }
    java.util.ArrayList[] pres = presence(online);
    for (int i = 0; i < pres[0].size(); i++) {
      try { @PKG@.GuildStore.welcome((@PR@) refs.get(pres[0].get(i))); } catch (Throwable t) { }
    }
    for (int i = 0; i < pres[1].size(); i++) {
      try { @PKG@.GuildStore.wentOffline((java.util.UUID) pres[1].get(i)); } catch (Throwable t) { }
    }
    @PKG@.GuildStore.flushDirty();
    if (@PKG@.XpTask.BASE.size() > 20000) { @PKG@.XpTask.BASE.clear(); @PKG@.XpTask.FRAC.clear(); }
  } catch (Throwable t) { @PKG@.GuildStore.warn("guild tick failed: " + t); }
}""")

# ================= guild:fn:online =================
ofn.addInterface(pool.get("java.util.function.Function"))
C(ofn, "public GuildOnlineFn() { }")
M(ofn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof java.util.UUID)) return new String[0];
    return @PKG@.GuildStore.onlineNames((java.util.UUID) arg);
  } catch (Throwable t) { return new String[0]; }
}""")

# ================= GuildPage (inline, rebuilt only after a click) =================
for f in ("public int pageNo;", "public String info;", "public java.util.ArrayList rowIds;", "public String confirm;",
          "public long confirmUntil;", "public String keepInvite;", "public String keepAmount;", "public String keepName;"):
    F(page, f)
C(page, r"""
public GuildPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.pageNo = 0; this.info = ""; this.confirm = ""; this.confirmUntil = 0L;
  this.keepInvite = ""; this.keepAmount = ""; this.keepName = "";
  this.rowIds = new java.util.ArrayList();
}""")
M(page, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")
M(page, r"""
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr, verified in game with the search TextField)
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
public static String two(long n) {
  return n < 10L ? "0" + n : String.valueOf(n);
}""")
M(page, r"""
public void infoLabel(@UCB@ b) {
  String col = @PKG@.GuildStore.colorOf(this.info);
  b.appendInline("#SkyyGuild", "Label #SkyyGInfo { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + col + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGInfo.Text", @PKG@.GuildStore.textOf(this.info));
}""")
M(page, r"""
public void buildNone(@UCB@ b, @UEB@ ev, java.util.UUID u) {
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 17);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 17);
  b.appendInline((String) null, "Group #SkyyGuild { Anchor: (Width: 1120, Height: 660); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyGuild", "Group { Anchor: (Height: 3); Background: #ffd070; }");
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 54); Text: \"Guilds\"; Style: (FontSize: 30, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGuild", "Label #SkyyGNoneTxt { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGNoneTxt.Text", "You are not in a guild yet. A guild shares a bank, levels up from its members' skill XP and has its own chat.");
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 14); Text: \"\"; }");
  Object[] inv = @PKG@.GuildStore.inviteFor(u);
  if (inv != null) {
    long secs = ((Long) inv[5]).longValue() / 1000L;
    String tg = ((String) inv[1]).length() > 0 ? " [" + inv[1] + "]" : "";
    b.appendInline("#SkyyGuild", "Group #SkyyGInvRow { Anchor: (Height: 64); LayoutMode: Left; Padding: (Top: 8); Background: #1d3320(0.95); }");
    b.appendInline("#SkyyGInvRow", "Label { Anchor: (Width: 16, Height: 48); Text: \"\"; }");
    b.appendInline("#SkyyGInvRow", "Label #SkyyGInvTxt { Anchor: (Width: 740, Height: 48); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center); }");
    b.set("#SkyyGInvTxt.Text", "Invite to " + inv[0] + tg + " (level " + inv[2] + ", " + inv[3] + " members) from " + inv[4] + " - " + (secs / 60L) + ":" + two(secs % 60L) + " left");
    b.appendInline("#SkyyGInvRow", "TextButton #SkyyGAccept { Anchor: (Width: 140, Height: 44); Text: \"Accept\"; " + gs + " }");
    b.appendInline("#SkyyGInvRow", "Label { Anchor: (Width: 10, Height: 44); Text: \"\"; }");
    b.appendInline("#SkyyGInvRow", "TextButton #SkyyGDecline { Anchor: (Width: 140, Height: 44); Text: \"Decline\"; " + rs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGAccept", @EVD@.of("a", "accept"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGDecline", @EVD@.of("a", "decline"));
    b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 16); Text: \"\"; }");
  }
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 40); Text: \"Create a guild\"; Style: (FontSize: 21, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGuild", "Group #SkyyGCreateRow { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyGCreateRow", "Label { Anchor: (Width: 196, Height: 42); Text: \"\"; }");
  b.appendInline("#SkyyGCreateRow", "Group #SkyyGNameBox { Anchor: (Width: 460, Height: 42); Background: #16263a; }");
  b.appendInline("#SkyyGNameBox", "TextField #SkyyGName { Anchor: (Full: 0); Padding: (Horizontal: 12); MaxLength: 24; PlaceholderText: \"Guild name\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 17); Style: (TextColor: #ffffff, FontSize: 17); }");
  if (this.keepName != null && this.keepName.length() > 0) b.set("#SkyyGName.Value", this.keepName);
  b.appendInline("#SkyyGCreateRow", "Label { Anchor: (Width: 12, Height: 42); Text: \"\"; }");
  b.appendInline("#SkyyGCreateRow", "TextButton #SkyyGCreate { Anchor: (Width: 200, Height: 42); Text: \"Create guild\"; " + gs + " }");
  ev.addEventBinding(@BT@.Validating, "#SkyyGName", @EVD@.of("a", "create").append("@GName", "#SkyyGName.Value"), false);
  ev.addEventBinding(@BT@.Activating, "#SkyyGCreate", @EVD@.of("a", "create").append("@GName", "#SkyyGName.Value"));
  b.appendInline("#SkyyGuild", "Label #SkyyGRule { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGRule.Text", "3 to 24 letters, digits and spaces. Every guild name is unique. You become its Leader.");
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 22); Text: \"\"; }");
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 32); Text: \"Commands\"; Style: (FontSize: 19, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  String[] help = @PKG@.GuildStore.helpLines();
  for (int i = 0; i < help.length; i++) {
    b.appendInline("#SkyyGuild", "Label #SkyyGHelp" + i + " { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 14, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGHelp" + i + ".Text", @PKG@.GuildStore.textOf(help[i]));
  }
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 12); Text: \"\"; }");
  infoLabel(b);
  b.appendInline("#SkyyGuild", "Group #SkyyGBottom { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyGBottom", "Label { Anchor: (Width: 466, Height: 40); Text: \"\"; }");
  b.appendInline("#SkyyGBottom", "TextButton #SkyyGRefresh { Anchor: (Width: 140, Height: 40); Text: \"Refresh\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGRefresh", @EVD@.of("a", "refresh"));
}""")
M(page, r"""
public void buildGuild(@UCB@ b, @UEB@ ev, java.util.UUID u, Object[] s) {
  String name = (String) s[0];
  String tag = (String) s[1];
  long xp = ((Long) s[2]).longValue();
  long bank = ((Long) s[3]).longValue();
  int my = ((Integer) s[4]).intValue();
  java.util.ArrayList rows = (java.util.ArrayList) s[5];
  java.util.ArrayList log = (java.util.ArrayList) s[6];
  long sx = ((Long) s[7]).longValue();
  int season = ((Integer) s[8]).intValue();
  int onl = ((Integer) s[9]).intValue();
  String us = u.toString();
  long[] li = @PKG@.GuildStore.levelInfo(xp);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 15);
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 15);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 15);
  String ys = style("#7a3a10", "#9a4c18", "#4a2208", "#fff0dc", 15);
  b.appendInline((String) null, "Group #SkyyGuild { Anchor: (Width: 1120, Height: 900); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyGuild", "Group { Anchor: (Height: 3); Background: #ffd070; }");
  b.appendInline("#SkyyGuild", "Label #SkyyGTitle { Anchor: (Height: 46); Text: \"\"; Style: (FontSize: 28, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGTitle.Text", name + (tag.length() > 0 ? "  [" + tag + "]" : ""));
  b.appendInline("#SkyyGuild", "Label #SkyyGSub { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 17, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Guild level " + li[0] + "     Season " + season + ": " + @PKG@.GuildStore.fmt(sx) + " guild XP     You are the " + @PKG@.GuildStore.rankName(my));
  int bw = 1072;
  int fill = li[2] > 0L ? (int) ((long) bw * li[1] / li[2]) : 0;
  if (fill < 0) fill = 0;
  if (fill > bw) fill = bw;
  b.appendInline("#SkyyGuild", "Group #SkyyGBar { Anchor: (Width: " + bw + ", Height: 24); Background: #22324a; }");
  if (fill > 0) b.appendInline("#SkyyGBar", "Group { Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 24); Background: #58c070; }");
  b.appendInline("#SkyyGBar", "Label #SkyyGBarTxt { Anchor: (Full: 0); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGBarTxt.Text", @PKG@.GuildStore.fmt(li[1]) + " / " + @PKG@.GuildStore.fmt(li[2]) + " XP to level " + (li[0] + 1L));
  b.appendInline("#SkyyGuild", "Label #SkyyGXpTxt { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 14, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGXpTxt.Text", "Members add " + @PKG@.GCfg.SHARE + "% of the skill XP they earn to the guild. Total guild XP: " + @PKG@.GuildStore.fmt(xp));
  b.appendInline("#SkyyGuild", "Label #SkyyGStats { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffd070, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGStats.Text", "Guild bank: " + bank + " coins          Online: " + onl + " / " + rows.size() + " members");
  String hs = "Style: (FontSize: 15, RenderBold: true, TextColor: #9fb8d0, VerticalAlignment: Center); }";
  b.appendInline("#SkyyGuild", "Group #SkyyGMemHdr { Anchor: (Height: 26); LayoutMode: Left; }");
  b.appendInline("#SkyyGMemHdr", "Label { Anchor: (Width: 34, Height: 26); Text: \"\"; }");
  b.appendInline("#SkyyGMemHdr", "Label { Anchor: (Width: 270, Height: 26); Text: \"Member\"; " + hs);
  b.appendInline("#SkyyGMemHdr", "Label { Anchor: (Width: 130, Height: 26); Text: \"Rank\"; " + hs);
  b.appendInline("#SkyyGMemHdr", "Label { Anchor: (Width: 200, Height: 26); Text: \"Guild XP added\"; " + hs);
  b.appendInline("#SkyyGMemHdr", "Label { Anchor: (Width: 96, Height: 26); Text: \"Status\"; " + hs);
  b.appendInline("#SkyyGMemHdr", "Label #SkyyGMemAct { Anchor: (Width: 330, Height: 26); Text: \"\"; " + hs);
  b.set("#SkyyGMemAct.Text", my == 2 ? "Leader actions" : (my == 1 ? "Officer actions" : ""));
  int per = 8;
  int pages = (rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  this.rowIds = new java.util.ArrayList();
  for (int i = start; i < rows.size() && i < start + per; i++) {
    String[] r = (String[]) rows.get(i);
    int idx = i - start;
    this.rowIds.add(r[0]);
    int rr = Integer.parseInt(r[2]);
    boolean on = "1".equals(r[4]);
    boolean me = r[0].equals(us);
    String rid = "#SkyyGRow" + idx;
    b.appendInline("#SkyyGuild", "Group #SkyyGRow" + idx + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 3); Background: " + (me ? "#1c2c44(0.95)" : "#142030(0.9)") + "; }");
    b.appendInline(rid, "Group { Anchor: (Width: 34, Height: 38); Group { Anchor: (Left: 10, Top: 12, Width: 14, Height: 14); Background: " + (on ? "#50d060" : "#55606e") + "; } }");
    b.appendInline(rid, "Label #SkyyGRowName" + idx + " { Anchor: (Width: 270, Height: 38); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + (on ? "#ffffff" : "#9aa6b4") + ", VerticalAlignment: Center); }");
    b.set("#SkyyGRowName" + idx + ".Text", r[1] + (me ? "  (you)" : ""));
    String rc = rr == 2 ? "#ffd060" : (rr == 1 ? "#8fc8ff" : "#c8d4e0");
    b.appendInline(rid, "Label #SkyyGRowRank" + idx + " { Anchor: (Width: 130, Height: 38); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + rc + ", VerticalAlignment: Center); }");
    b.set("#SkyyGRowRank" + idx + ".Text", @PKG@.GuildStore.rankName(rr));
    b.appendInline(rid, "Label #SkyyGRowXp" + idx + " { Anchor: (Width: 200, Height: 38); Text: \"\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyGRowXp" + idx + ".Text", @PKG@.GuildStore.fmt(@PKG@.GuildStore.parseLong(r[3], 0L)) + " XP");
    b.appendInline(rid, "Label #SkyyGRowOn" + idx + " { Anchor: (Width: 96, Height: 38); Text: \"\"; Style: (FontSize: 14, TextColor: " + (on ? "#7fe07f" : "#7f8a98") + ", VerticalAlignment: Center); }");
    b.set("#SkyyGRowOn" + idx + ".Text", on ? "online" : "offline");
    boolean canKick = !me && rr < my && my >= 1;
    if (my == 2 && !me) {
      if (rr == 0) {
        b.appendInline(rid, "TextButton #SkyyGPro" + idx + " { Anchor: (Width: 110, Height: 36); Text: \"Promote\"; " + bs + " }");
        ev.addEventBinding(@BT@.Activating, "#SkyyGPro" + idx, @EVD@.of("a", "promote:" + idx));
      } else {
        b.appendInline(rid, "TextButton #SkyyGDem" + idx + " { Anchor: (Width: 110, Height: 36); Text: \"Demote\"; " + bs + " }");
        ev.addEventBinding(@BT@.Activating, "#SkyyGDem" + idx, @EVD@.of("a", "demote:" + idx));
      }
      b.appendInline(rid, "Label { Anchor: (Width: 6, Height: 36); Text: \"\"; }");
    }
    if (canKick) {
      boolean ck = this.confirm.equals("kick:" + r[0]);
      b.appendInline(rid, "TextButton #SkyyGKick" + idx + " { Anchor: (Width: 90, Height: 36); Text: \"" + (ck ? "Sure?" : "Kick") + "\"; " + rs + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyGKick" + idx, @EVD@.of("a", "kick:" + idx));
      b.appendInline(rid, "Label { Anchor: (Width: 6, Height: 36); Text: \"\"; }");
    }
    if (my == 2 && !me) {
      boolean cl = this.confirm.equals("lead:" + r[0]);
      b.appendInline(rid, "TextButton #SkyyGLead" + idx + " { Anchor: (Width: 116, Height: 36); Text: \"" + (cl ? "Confirm?" : "Make leader") + "\"; " + ys + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyGLead" + idx, @EVD@.of("a", "lead:" + idx));
    }
    b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 4); Text: \"\"; }");
  }
  if (pages > 1) {
    b.appendInline("#SkyyGuild", "Group #SkyyGNav { Anchor: (Height: 36); LayoutMode: Left; Padding: (Top: 2); }");
    b.appendInline("#SkyyGNav", "Label { Anchor: (Width: 340, Height: 32); Text: \"\"; }");
    b.appendInline("#SkyyGNav", "TextButton #SkyyGPrev { Anchor: (Width: 110, Height: 32); Text: \"< Prev\"; " + bs + " }");
    b.appendInline("#SkyyGNav", "Label #SkyyGPageTxt { Anchor: (Width: 170, Height: 32); Text: \"\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyGNav", "TextButton #SkyyGNext { Anchor: (Width: 110, Height: 32); Text: \"Next >\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGNext", @EVD@.of("a", "next"));
  } else {
    b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 12); Text: \"\"; }");
  }
  b.appendInline("#SkyyGuild", "Group #SkyyGAct { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 6); }");
  if (my >= 1) {
    b.appendInline("#SkyyGAct", "Group #SkyyGInvBox { Anchor: (Width: 270, Height: 40); Background: #16263a; }");
    b.appendInline("#SkyyGInvBox", "TextField #SkyyGInvite { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 32; PlaceholderText: \"Player name\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
    if (this.keepInvite != null && this.keepInvite.length() > 0) b.set("#SkyyGInvite.Value", this.keepInvite);
    b.appendInline("#SkyyGAct", "Label { Anchor: (Width: 8, Height: 40); Text: \"\"; }");
    b.appendInline("#SkyyGAct", "TextButton #SkyyGInviteBtn { Anchor: (Width: 120, Height: 40); Text: \"Invite\"; " + gs + " }");
    ev.addEventBinding(@BT@.Validating, "#SkyyGInvite", @EVD@.of("a", "invite").append("@GInvite", "#SkyyGInvite.Value"), false);
    ev.addEventBinding(@BT@.Activating, "#SkyyGInviteBtn", @EVD@.of("a", "invite").append("@GInvite", "#SkyyGInvite.Value"));
    b.appendInline("#SkyyGAct", "Label { Anchor: (Width: 60, Height: 40); Text: \"\"; }");
  } else {
    b.appendInline("#SkyyGAct", "Label { Anchor: (Width: 300, Height: 40); Text: \"\"; }");
  }
  b.appendInline("#SkyyGAct", "Group #SkyyGAmtBox { Anchor: (Width: 200, Height: 40); Background: #16263a; }");
  b.appendInline("#SkyyGAmtBox", "TextField #SkyyGAmount { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 16; PlaceholderText: \"Amount\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
  if (this.keepAmount != null && this.keepAmount.length() > 0) b.set("#SkyyGAmount.Value", this.keepAmount);
  b.appendInline("#SkyyGAct", "Label { Anchor: (Width: 8, Height: 40); Text: \"\"; }");
  b.appendInline("#SkyyGAct", "TextButton #SkyyGDep { Anchor: (Width: 136, Height: 40); Text: \"Deposit\"; " + gs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGDep", @EVD@.of("a", "deposit").append("@GAmount", "#SkyyGAmount.Value"));
  if (my >= 1) {
    b.appendInline("#SkyyGAct", "Label { Anchor: (Width: 8, Height: 40); Text: \"\"; }");
    b.appendInline("#SkyyGAct", "TextButton #SkyyGWd { Anchor: (Width: 136, Height: 40); Text: \"Withdraw\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGWd", @EVD@.of("a", "withdraw").append("@GAmount", "#SkyyGAmount.Value"));
  }
  b.appendInline("#SkyyGuild", "Label #SkyyGHint { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 13, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGHint.Text", (my >= 1 ? "Invite: an online player's name.   " : "") + "Amounts: 500, 2k, 1.5m or all - coins come from and go to your purse." + (my >= 1 ? "" : "  The Leader and Officers can withdraw."));
  b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 24); Text: \"Guild bank log\"; Style: (FontSize: 15, RenderBold: true, TextColor: #9fb8d0, VerticalAlignment: Center); }");
  int shown = 0;
  for (int i = log.size() - 1; i >= 0 && shown < 3; i--) {
    b.appendInline("#SkyyGuild", "Label #SkyyGLog" + shown + " { Anchor: (Height: 20); Text: \"\"; Style: (FontSize: 14, TextColor: #c8d4e0, VerticalAlignment: Center); }");
    b.set("#SkyyGLog" + shown + ".Text", "   " + @PKG@.GuildStore.logText((String) log.get(i)));
    shown++;
  }
  if (shown == 0) {
    b.appendInline("#SkyyGuild", "Label #SkyyGLog0 { Anchor: (Height: 20); Text: \"\"; Style: (FontSize: 14, TextColor: #8fa4b8, VerticalAlignment: Center); }");
    b.set("#SkyyGLog0.Text", "   No deposits or withdrawals yet.");
    shown = 1;
  }
  for (int i = shown; i < 3; i++) b.appendInline("#SkyyGuild", "Label { Anchor: (Height: 20); Text: \"\"; }");
  b.appendInline("#SkyyGuild", "Group #SkyyGBottom { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGBottom", "Label { Anchor: (Width: 230, Height: 40); Text: \"\"; }");
  b.appendInline("#SkyyGBottom", "TextButton #SkyyGRefresh { Anchor: (Width: 140, Height: 40); Text: \"Refresh\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGRefresh", @EVD@.of("a", "refresh"));
  b.appendInline("#SkyyGBottom", "Label { Anchor: (Width: 14, Height: 40); Text: \"\"; }");
  boolean cLeave = this.confirm.equals("leave");
  b.appendInline("#SkyyGBottom", "TextButton #SkyyGLeave { Anchor: (Width: 220, Height: 40); Text: \"" + (cLeave ? "Click again to leave" : "Leave guild") + "\"; " + rs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGLeave", @EVD@.of("a", "leave"));
  if (my == 2) {
    b.appendInline("#SkyyGBottom", "Label { Anchor: (Width: 14, Height: 40); Text: \"\"; }");
    boolean cDis = this.confirm.equals("disband");
    b.appendInline("#SkyyGBottom", "TextButton #SkyyGDisband { Anchor: (Width: 240, Height: 40); Text: \"" + (cDis ? "Click again to DISBAND" : "Disband guild") + "\"; " + rs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGDisband", @EVD@.of("a", "disband"));
  }
  infoLabel(b);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  if (this.confirmUntil < System.currentTimeMillis()) this.confirm = "";
  Object[] s = null;
  try { s = @PKG@.GuildStore.snapshot(u); } catch (Throwable t) { @PKG@.GuildStore.warn("guild page snapshot failed: " + t); }
  if (s == null) buildNone(b, ev, u);
  else buildGuild(b, ev, u, s);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    String un = this.playerRef.getUsername();
    long now = System.currentTimeMillis();
    if (this.confirmUntil < now) this.confirm = "";
    if (a.equals("refresh")) { this.info = ""; this.confirm = ""; rebuild(); return; }
    if (a.equals("prev")) { this.pageNo--; this.confirm = ""; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; this.confirm = ""; rebuild(); return; }
    String res = null;
    String keep = "";
    this.keepInvite = ""; this.keepAmount = ""; this.keepName = "";
    String was = this.confirm;
    this.confirm = "";
    if (a.equals("create")) {
      keep = jsonStr(data, "@GName");
      res = @PKG@.GuildStore.create(u, un, keep);
      if (res != null && res.startsWith("-")) this.keepName = keep;
    } else if (a.equals("accept")) {
      res = @PKG@.GuildStore.accept(u, un);
    } else if (a.equals("decline")) {
      res = @PKG@.GuildStore.decline(u, un);
    } else if (a.equals("invite")) {
      keep = jsonStr(data, "@GInvite");
      res = @PKG@.GuildStore.invite(u, un, keep);
      if (res != null && res.startsWith("-")) this.keepInvite = keep;
    } else if (a.equals("deposit") || a.equals("withdraw")) {
      keep = jsonStr(data, "@GAmount");
      res = a.equals("deposit") ? @PKG@.GuildStore.deposit(u, un, keep) : @PKG@.GuildStore.withdraw(u, un, keep);
      if (res != null && res.startsWith("-")) this.keepAmount = keep;
    } else if (a.equals("leave")) {
      if (was.equals("leave")) res = @PKG@.GuildStore.leave(u, un, true);
      else { res = @PKG@.GuildStore.leaveWarning(u); if (res.startsWith("=")) { this.confirm = "leave"; this.confirmUntil = now + 10000L; } }
    } else if (a.equals("disband")) {
      if (was.equals("disband")) res = @PKG@.GuildStore.disband(u, un, true);
      else { res = @PKG@.GuildStore.disbandWarning(u); if (res.startsWith("=")) { this.confirm = "disband"; this.confirmUntil = now + 10000L; } }
    } else {
      int c = a.indexOf(':');
      if (c <= 0 || this.rowIds == null) return;
      String act = a.substring(0, c);
      int idx = -1;
      try { idx = Integer.parseInt(a.substring(c + 1)); } catch (Throwable t) { idx = -1; }
      if (idx < 0 || idx >= this.rowIds.size()) return;
      String tu = (String) this.rowIds.get(idx);
      if (act.equals("promote")) res = @PKG@.GuildStore.promote(u, un, tu);
      else if (act.equals("demote")) res = @PKG@.GuildStore.demote(u, un, tu);
      else if (act.equals("kick")) {
        if (was.equals("kick:" + tu)) res = @PKG@.GuildStore.kick(u, un, tu);
        else { this.confirm = "kick:" + tu; this.confirmUntil = now + 10000L; res = "=Click Sure? within 10 s to remove " + @PKG@.GuildStore.nameOfMember(u, tu) + " from the guild."; }
      } else if (act.equals("lead")) {
        if (was.equals("lead:" + tu)) res = @PKG@.GuildStore.transfer(u, un, tu, true);
        else { this.confirm = "lead:" + tu; this.confirmUntil = now + 10000L; res = "=Click Confirm? within 10 s to make " + @PKG@.GuildStore.nameOfMember(u, tu) + " the Leader (you become an Officer)."; }
      } else return;
    }
    this.info = res == null ? "+Done." : res;
    rebuild();
  } catch (Throwable t) { @PKG@.GuildStore.warn("guild page click failed: " + t); }
}""")

# ================= commands =================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []


def cmd(clsname, name, desc, args, body, perm="@ADV@", subs=(), aliases=()):
    """One AbstractPlayerCommand. args = [(field, argName, argDesc, "STRING" | "GREEDY_STRING")], read into a0, a1, ..."""
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    for (fld, _an, _ad, _ty) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = ['super("%s", "%s");' % (name, desc), perm]
    if aliases:
        lines.append("addAliases(new String[] { %s });" % ", ".join('"%s"' % a for a in aliases))
    for (fld, an, ad, ty) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (fld, an, ad, ty))
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    reads = "".join('    String a%d = String.valueOf(ctx.get(this.%s));\n' % (i, a[0]) for i, a in enumerate(args))
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.GuildStore.warn(\"/" + name + " failed: \" + t);\n"
      "    @PKG@.GuildStore.tell(pr, \"-Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


U = "pr.getUuid(), pr.getUsername()"
S = "@PKG@.GuildStore."
cmd("GHelpCmd", "help", "Every guild command", [], S + "tellAll(pr, " + S + "helpLines());")
cmd("GCreateCmd", "create", "Found a guild: /guild create <name> (3-24 letters, digits, spaces)",
    [("nameArg", "name", "Guild name (spaces allowed)", "GREEDY_STRING")], S + "tell(pr, " + S + "create(" + U + ", a0));")
cmd("GTagCmd", "tag", "Leader: set the guild tag (2-4 letters/digits) or /guild tag clear",
    [("tagArg", "tag", "2-4 letters or digits, or clear", "STRING")], S + "tell(pr, " + S + "setTag(" + U + ", a0));")
cmd("GInviteCmd", "invite", "Leader/Officer: invite an online player",
    [("playerArg", "player", "Online player name", "STRING")], S + "tell(pr, " + S + "invite(" + U + ", a0));")
cmd("GAcceptCmd", "accept", "Accept your guild invite", [], S + "tell(pr, " + S + "accept(" + U + "));")
cmd("GDeclineCmd", "decline", "Decline your guild invite", [], S + "tell(pr, " + S + "decline(" + U + "));")
cmd("GLeaveCmd", "leave", "Leave your guild", [], S + "tell(pr, " + S + "leave(" + U + ", false));")
cmd("GKickCmd", "kick", "Leader/Officer: remove a lower-ranked member",
    [("playerArg", "player", "Member name", "STRING")], S + "tell(pr, " + S + "kick(" + U + ", a0));")
cmd("GPromoteCmd", "promote", "Leader: make a Member an Officer",
    [("playerArg", "player", "Member name", "STRING")], S + "tell(pr, " + S + "promote(" + U + ", a0));")
cmd("GDemoteCmd", "demote", "Leader: make an Officer a Member",
    [("playerArg", "player", "Member name", "STRING")], S + "tell(pr, " + S + "demote(" + U + ", a0));")
cmd("GTransferCmd", "transfer", "Leader: hand the guild to another member (repeat to confirm)",
    [("playerArg", "player", "Member name", "STRING")], S + "tell(pr, " + S + "transfer(" + U + ", a0, false));")
cmd("GDisbandCmd", "disband", "Leader: delete the guild (repeat within 10 s to confirm)", [], S + "tell(pr, " + S + "disband(" + U + ", false));")
cmd("GInfoCmd", "info", "Your guild in chat", [], S + "tellAll(pr, " + S + "infoLines(pr.getUuid()));")
cmd("GListCmd", "list", "The top 10 guilds", [], S + "tellAll(pr, " + S + "listLines());")
cmd("GDepositCmd", "deposit", "Put coins from your purse into the guild bank: 500, 2k, 1.5m, all",
    [("amountArg", "amount", "500, 2k, 1.5m or all", "STRING")], S + "tell(pr, " + S + "deposit(" + U + ", a0));")
cmd("GWithdrawCmd", "withdraw", "Leader/Officer: take coins from the guild bank into your purse",
    [("amountArg", "amount", "500, 2k, 1.5m or all", "STRING")], S + "tell(pr, " + S + "withdraw(" + U + ", a0));")
cmd("GBankCmd", "bank", "Guild bank balance + log; /guild bank deposit|withdraw <amount>", [],
    S + "tellAll(pr, " + S + "bankLines(pr.getUuid()));", subs=("GDepositCmd", "GWithdrawCmd"))
cmd("GuildChatCmd", "gc", "Guild chat: /gc <message>",
    [("msgArg", "message", "Message to your guild", "GREEDY_STRING")], S + "tell(pr, " + S + "chat(" + U + ", a0));")
root = cmd("GuildCmd", "guild", "Guilds: /guild opens the guild page - /guild help lists every command", [],
    r"""@PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { @PKG@.GuildStore.tellAll(pr, @PKG@.GuildStore.helpLines()); return; }
    p.getPageManager().openCustomPage(ref, store, new @PKG@.GuildPage(pr));""",
    subs=("GHelpCmd", "GCreateCmd", "GTagCmd", "GInviteCmd", "GAcceptCmd", "GDeclineCmd", "GLeaveCmd", "GKickCmd", "GPromoteCmd",
          "GDemoteCmd", "GTransferCmd", "GDisbandCmd", "GInfoCmd", "GListCmd", "GBankCmd"))

# ---- admin (requirePermission on the root AND on every subcommand: a subcommand with no permission groups checks its own node)
A = "@ADMIN@"
cmd("GAInfoCmd", "info", "Admin: a guild's details", [("guildArg", "guild", "Guild name, tag or id", "GREEDY_STRING")],
    S + "tellAll(pr, " + S + "adminInfo(a0));", perm=A)
cmd("GADeleteCmd", "delete", "Admin: delete a guild (repeat to confirm; bank paid to its Leader)",
    [("guildArg", "guild", "Guild name, tag or id", "GREEDY_STRING")], S + "tell(pr, " + S + "adminDelete(" + U + ", a0));", perm=A)
cmd("GASeasonNextCmd", "next", "Admin: start the next guild season (repeat to confirm)", [],
    S + "tell(pr, " + S + "seasonNext(" + U + "));", perm=A)
cmd("GASeasonCmd", "season", "Admin: the current guild season and its top 10", [], S + "tellAll(pr, " + S + "seasonLines());",
    perm=A, subs=("GASeasonNextCmd",))
cmd("GAXpCmd", "xp", "Admin: give a guild XP (testing)", [("amountArg", "amount", "Guild XP", "STRING"),
    ("guildArg", "guild", "Guild name, tag or id", "GREEDY_STRING")], S + "tell(pr, " + S + "adminXp(a0, a1));", perm=A)
cmd("GAReloadCmd", "reload", "Admin: re-read config.properties", [],
    "@PKG@.GCfg.load(); " + S + "tell(pr, \"+config.properties re-read: XP share \" + @PKG@.GCfg.SHARE + \"%, check every \" + @PKG@.GCfg.POLL + \" s, max \" + @PKG@.GCfg.MAX_MEMBERS + \" members.\");", perm=A)
cmd("GuildAdminCmd", "guildadmin", "Guild admin: info | delete | season | xp | reload", [], S + "tellAll(pr, " + S + "adminHelp());",
    perm=A, subs=("GAInfoCmd", "GADeleteCmd", "GASeasonCmd", "GAXpCmd", "GAReloadCmd"))

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyGuildsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.GuildStore.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyGuilds");
  @PKG@.GuildStore.DIR = dir;
  @PKG@.GuildStore.GDIR = dir.resolve("guilds");
  @PKG@.GCfg.FILE = dir.resolve("config.properties");
  @PKG@.GCfg.load();
  @PKG@.GuildStore.loadAll();
  getCommandRegistry().registerCommand(new @PKG@.GuildCmd());
  getCommandRegistry().registerCommand(new @PKG@.GuildChatCmd());
  getCommandRegistry().registerCommand(new @PKG@.GuildAdminCmd());
  @PKG@.GuildStore.bridge().put("guild:fn:online", new @PKG@.GuildOnlineFn());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.GuildTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyGuilds] @VERSION@ ready - /guild (page), /gc, /guildadmin; XP share " + @PKG@.GCfg.SHARE + "% of members' skill XP; data in " + dir);
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.GuildStore.flushDirty(); } catch (Throwable t) { }
  try { @PKG@.GuildStore.bridge().remove("guild:fn:online"); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL + CMDS + [pl]:
    c.writeFile(OUT)
print("classes written:", len(ALL + CMDS) + 1)

jar = os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION)
man = B.manifest("SkyyGuilds", VERSION, "SkyWynn guilds: create/invite/ranks, guild chat (/gc), guild bank (SkyyCoins bridge), guild XP from members' skill XP (SkyySkills bridge), seasons, /guild page. Per player. Zero dependencies.", PKG + ".SkyyGuildsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
