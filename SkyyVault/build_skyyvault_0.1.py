"""SkyyVault 0.1 - build script (javassist via jpype).
Run:   python build_skyyvault_0.1.py            -> SkyyVault/SkyyVault-0.1.jar
       (no --deploy in this script on purpose: tools/deploy_set.py installs the whole set once Skyy says deploy)

NEW MOD (HANDOFF 2026-09-24 20:10 BETA BACKLOG item 5). Skyy: "a /vault that works like the ender chests in the bank in Wynncraft -
a chest you can open from ANY profile for saving and transferring items between profiles."
The vault is per PLAYER (keyed by the player UUID, never by the profile key pkey(uuid)): every profile of a player opens the same
vault, so it is how items move between profiles (tools/PROFILES-CONTRACT.md rule 6: per-player data unless noted). Zero hard
dependencies: coins come from SkyyCoins only through the JVM bridge (coins:fn:take / coins:fn:add); without SkyyCoins the free pages
work and buying says coins are missing. SkyyProfiles is read only through profile:busy:<uuid> and profile:epoch:<uuid>.

WHAT THE PLAYER SEES
  /vault            openMode=page (default): OUR vault page (inline, rebuilt only after a click) opened TOGETHER with a container
                    window of vault page 1 (PageManager.openCustomPageWithWindows + a ContainerWindow subclass - the SkyySacks /pd
                    pattern). The page: title, "Page 2 of 4", < Prev / Next >, a row of page-number buttons (current green, owned
                    blue, locked grey), "Page 2 - 14 of 36 slots used", Open as chest, Buy page N - <price> coins (second click
                    confirms within 10 s), Close, three help lines and a result line. Prev / Next / a number swap the vault slots
                    in place (no window churn). "Open as chest" opens the same vault page in the VANILLA chest window (Page.Bench +
                    ContainerWindow - the proven vanilla /invsee, chest and TerrariaAddons pattern) - the fallback in case the
                    client does not draw window slots next to a custom page (UNVERIFIED, see below).
                    openMode=chest: /vault opens the vanilla chest window at once; /vault pages opens the page with the buttons,
                    whose Open button opens the selected page as a chest.
  /vault <page>     the same, on that page (usage variant, one required arg; the engine picks subcommands by name first).
  /vault next | prev    the next / previous page (swaps in place when the vault is already showing, else opens it).
  /vault pages      the page with the buttons (openMode=chest) - in page mode it is the same as /vault.
  /vault buy        buy the next page (type it twice within 10 s). /vault info  pages, slots used per page, next price.
                    The page's Buy button and /vault buy share ONE confirmation (VStore.CONFIRM, key buy:<uuid>:<page number>): a
                    click then a typed /vault buy (or the reverse) is the two-step confirm; arming by command refreshes an open vault
                    page so its button shows "Sure?". The key names the page, so a confirm armed for page 3 never buys page 4.
  Vault pages: freePages (2) free, more bought with coins up to maxPages (10): page N costs
  pagePrice + pagePriceStep x (N - freePages - 1) = 50k, 75k, 100k, ... (config). 36 slots per page (a large chest; config).
  PROPOSED NUMBERS, NOT SIGNED OFF BY SKYY: the backlog asks for "Wynncraft bank-style" storage (Wynncraft bank pages are bought, and
  its bank is shared by every character) but names no prices. Every number is in config.properties, so a decision needs no rebuild.
  Coins come from the ACTIVE profile's purse (coins:fn:take acts on the active profile) while the page belongs to the vault every
  profile shares - the Wynncraft pattern (one character's emeralds buy an account-wide bank page). Not yet written into
  tools/PROFILES-CONTRACT.md as a sanctioned pattern; Skyy decides.
  ADMIN  /vaultadmin open <player> [page]   READ-ONLY snapshot of that vault page in a vanilla chest window: a COPY of the page in
                    a SimpleItemContainer with FilterType.DENY_ALL (vanilla /invsee read-only pattern: nothing can be taken or put
                    in, and it is a copy, so nothing can change the real vault).  /vaultadmin info <player>  /vaultadmin setpages
                    <player> <n> (never below the highest page that holds items)  /vaultadmin reload (config.properties).
                    <player> = online name, a name seen before (names.properties) or a UUID. requirePermission("skyyvault.admin")
                    on the root, on every subcommand and on the open <player> <page> variant.
  Every player command, subcommand and the /vault <page> variant call setPermissionGroups(new String[] { "hytale:Adventurer" }).

NO DUPES, NO LOSS (the design)
  * At rest a vault lives in memory as one ItemStack[] per page (VData) and on disk as vaults/<uuid>.json. While it is open, ONE
    session (VSession) per vault owner shows one page in its own SimpleItemContainer (the "view"); every change event of the view
    copies the view into that page's array at once (VSessions.syncView) and schedules a save. So the arrays always equal what the
    player sees, and the file follows within saveDelayMillis (1 s). Every close (Esc, window close, world change, disconnect - the
    engine's PlayerAddedSystem closes all windows when the entity leaves a world) syncs once more and writes at once.
  * ONE editable view per vault: SESSIONS is keyed by the owner UUID. A second /vault reuses the live session (same page type and
    still on screen: the slots are swapped in place); otherwise the old view is released BEFORE the new one exists: a window that is
    part of the page on screen is RETIRED (DENY_ALL, synced, marked closed - the new page replaces it, so a page is never closed
    right before another opens), a window that is not on screen is closed (its close syncs + saves), a session whose window is gone
    is finalized. The admin view never creates a session: it is a read-only copy (two viewers can never both edit one vault).
  * A closed session's view is made inert: marked closed (its change listener stops), unregistered, FilterType.DENY_ALL (a late
    client move into it is refused, so nothing can be put into a dead view and vanish) and emptied.
  * Page swap: sync the old page first, then clear + fill the view from the target page and read every slot back; if the view does
    not match exactly, the session closes WITHOUT syncing (noSync) - the arrays keep both pages untouched, nothing is lost.
  * Opening (and a page swap) is refused while profile:busy:<uuid> is set (SkyyProfiles crash recovery / switch transaction) and for
    afterSwitchSeconds (30) after profile:epoch:<uuid> changed or profile:busy went away. Why 30: SkyyProfiles keeps its switch marker
    (switching/<uuid>.properties) 30 s after EVERY switch and after every clean crash recovery (ClearLater), whatever islandOnSwitch
    says. A server crash while that marker exists rolls the player forward at the next join: inventory cleared and the snapshot taken
    at the switch loaded - every inventory change since the switch is undone. A vault move in that time would then exist twice (put
    in) or be gone (taken out), because the vault file keeps it. The vault notices a switch no earlier than it happened and the
    marker is armed before the epoch is published, so 30 s after the vault noticed is never earlier than the marker's deletion.
    Lowering afterSwitchSeconds shortens the wait but widens the crash window to (30 - afterSwitchSeconds) s after a switch. An open vault
    closes (world-thread task from the 1 s ticker) when profile:busy appears or the epoch changes; the window's
    ValidatedWindow.validate() (called by the engine on player movement) also closes it on busy, or when our page / the chest page is no
    longer on screen.
  * Buying: coins:fn:take FIRST (must return TRUE), then the page count goes up and the file is written synchronously and read back;
    if that write fails the page count goes back and the exact coins are refunded (coins:fn:add); every buy / failure / refund is in
    vault.log.
  * Files: tmp + fsync + ATOMIC_MOVE (5 x 20 ms retries on a Windows FileSystemException - SkyyProfiles 0.1 pattern), then read back
    and the slot count compared. Writes are ordered by a revision number under a per-vault IO lock, so an older snapshot can never
    overwrite a newer file. A vault file that exists but cannot be read keeps that vault SHUT (never overwritten, re-read on every
    try, warned once a minute). A stack that cannot be decoded (item removed from the game) is kept byte-for-byte in "orphans" and
    retried at every load - never dropped.
  * Lossless stacks: the SkyyProfiles 0.1 slot format - explicit id / qty / durability / max durability / quality / overrideAnim /
    metadata BsonDocument PLUS the engine's own ItemStack.CODEC encoding (decoded first, the explicit fields are the fallback), as
    EXTENDED JSON. SkyyRolls rolls (metadata "SkyyRolls") and graded dishes (Skyy_Cook_* ids + metadata) survive exactly.
  * Shutdown: every open view is made inert and synced (the container read lock makes that safe off the world thread), then every
    changed vault is written synchronously before the saver thread stops.

THREADS: /vault commands, page clicks, window close (GamePacketHandler.handleCloseWindow / PlayerAddedSystem) and the view change
  events run on the player's world thread. The ticker (1 s, shared scheduler) only reads the bridge and the session table and
  hands closes to the player's world thread (VCloseTask). That includes the last-resort finalize of a session whose viewer has been
  gone 10 s (normally the engine closed its window long before): it runs as a VCloseTask (offline=true) on the world the view was
  shown in, so it is serialized with any late engine close there. Only when that world no longer exists or refuses the task, or the
  task still has not run 10 s later (a dead world thread), does the ticker retire the view itself - then no thread can still reach
  the view (its player and world are gone). The other off-thread retire is plugin shutdown (below). File writes run on one daemon
  saver thread (VSaveJob); a buy / setpages writes on the calling world thread (it must know the result). No ECS systems, no events
  registered.
COMMAND PERMISSIONS are checked by THIS SCRIPT at build time: tools/ci/lint.py only recognizes literal super("name" text, and every
  command here is generated by cmd(), so lint cannot see them. cmd() refuses a perm that is not @ADV@ / @ADMIN@, the generated
  constructor must contain setPermissionGroups / requirePermission, ADMIN_CMDS must match exactly the classes built with @ADMIN@
  (an admin command that forgot perm= fails the build instead of opening to players), and after compiling every command class file
  must reference setPermissionGroups + "hytale:Adventurer" or requirePermission + "skyyvault.admin".

DATA (<world>/mods/Skyy_SkyyVault/, stable across versions): vaults/<uuid>.json (EXTENDED JSON: format, mod, version, uuid, name,
  pages, capacity, savedAt, rev, count, content:[{page, slots:[{slot, id, qty, durability, maxDurability, quality, overrideAnim,
  meta, stack}]}], orphans:[{page, slot, ...}]); names.properties (lower-case name = uuid, for /vaultadmin with offline players);
  vault.log (BUY, BUY-FAIL, REFUND, SETPAGES, ADMIN-VIEW, WRITE-FAIL, FINALIZE-OFFLINE); config.properties (defaults written on first
  start; /vaultadmin reload re-reads it - slotsPerPage applies to vaults loaded afterwards).

UNVERIFIED (needs Skyy in game): (1) whether the client draws the ContainerWindow's slots next to a CUSTOM page
  (openCustomPageWithWindows) - never confirmed for SkyySacks' /pd either; if not, the page's Open as chest button (and openMode=chest)
  is the working path; (2) the page layout on a real client; (3) that FilterType.DENY_ALL blocks the vanilla chest panel's Take all /
  Put all buttons for the admin copy (it does for vanilla /invsee, and the copy never touches the real vault anyway); (4) the client
  closing the window by itself when the custom page is closed (if it does not, onDismiss closes it 1.5 s later).
KNOWN LIMIT: a SERVER CRASH (not a normal stop) within ~10 s after moving items between the inventory and the vault can duplicate or
  lose those stacks - the vault file is written within 1 s but the engine saves player inventories only every 10 s (the same window
  every Skyy storage mod has; tools/PROFILES-CONTRACT.md section 5). A normal stop / logout saves both sides. Right after a profile
  switch the window would be SkyyProfiles' 30 s marker instead (see the afterSwitchSeconds bullet); the default 30 s gate keeps the
  vault shut for exactly that time, so the ~10 s window stays the limit unless afterSwitchSeconds is lowered.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.vault"
T = {
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "CA":   "com.hypixel.hytale.component.ComponentAccessor",
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
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC":  "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "FT":   "com.hypixel.hytale.server.core.inventory.container.filter.FilterType",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "CW":   "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow",
    "VWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.ValidatedWindow",
    "WIN":  "com.hypixel.hytale.server.core.entity.entities.player.windows.Window",
    "EREG": "com.hypixel.hytale.event.EventRegistration",
    "PKG":  PKG,
    "VERSION": VERSION,
    "ADV":  'setPermissionGroups(new String[] { "hytale:Adventurer" });',
    "ADMIN": 'requirePermission("skyyvault.admin");',
}
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
WM  = "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager"
PB  = "com.hypixel.hytale.server.core.plugin.PluginBase"

# API probes: every engine member this mod calls (catches API drift at build time)
for c, m in ((T["UNI"], "get"), (T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"), (T["UNI"], "getWorld"), (T["PR"], "getWorldUuid"),
             (T["PR"], "getUsername"), (T["PR"], "getUuid"), (T["PR"], "isValid"), (T["PR"], "sendMessage"), (T["PR"], "getReference"),
             (T["WLD"], "execute"), (T["HSV"], "SCHEDULED_EXECUTOR"), (PB, "shutdown"), (PB, "getDataDirectory"), (PB, "getCommandRegistry"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "addUsageVariant"), (AC, "withRequiredArg"),
             (T["ATY"], "STRING"), (T["CTX"], "get"), (T["MSG"], "raw"), (T["MSG"], "color"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["BT"], "Activating"), (T["PAGE"], "rebuild"), (T["PAGE"], "handleDataEvent"), (T["PAGE"], "onDismiss"), (T["PAGE"], "close"),
             (T["LIFE"], "CanDismiss"), (T["PLA"], "getPageManager"), (T["PLA"], "getWindowManager"), (T["PLA"], "getComponentType"),
             (PGM, "openCustomPage"), (PGM, "openCustomPageWithWindows"), (PGM, "setPageWithWindows"), (PGM, "getCustomPage"), (PGM, "setPage"),
             (WM, "getWindow"), (WM, "closeWindow"), (T["WIN"], "getId"), (T["CW"], "onClose0"), (T["CW"], "getItemContainer"),
             (T["VWIN"], "validate"), (T["PGE"], "Bench"), (T["PGE"], "None"), (T["FT"], "DENY_ALL"), (T["EREG"], "unregister"),
             (T["SIC"], "getItemStack"), (T["SIC"], "getCapacity"), (T["IC"], "setItemStackForSlot"), (T["IC"], "clear"),
             (T["IC"], "registerChangeEvent"), (T["SIC"], "setGlobalFilter"), (T["CA"], "getComponent"),
             (T["IS"], "CODEC"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "getDurability"), (T["IS"], "getMaxDurability"),
             (T["IS"], "getQualityIndex"), (T["IS"], "getMetadata"), (T["IS"], "getOverrideDroppedItemAnimation"),
             (T["IS"], "setOverrideDroppedItemAnimation"), (T["IS"], "isEmpty"), (T["CODEC"], "encode"), (T["CODEC"], "decode"),
             ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson"), ("org.bson.json.JsonWriterSettings", "builder"),
             ("org.bson.json.JsonMode", "EXTENDED")):
    B.probe(pool, c, m)

TOKEN = re.compile(r"@([A-Z]{2,7})@")


def jv(src):
    def rep(m):
        k = m.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }"


def F(cls, src):
    cls.addField(CtField.make(jv(src), cls))


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


# ---- config defaults (edit here, rebuild; Skyy can also edit config.properties and /vaultadmin reload)
DEF_FREE, DEF_MAX, DEF_SLOTS = 2, 10, 36
DEF_PRICE, DEF_STEP = 50000, 25000
DEF_AFTER_SWITCH_S, DEF_SAVE_DELAY_MS = 30, 1000   # 30 = SkyyProfiles 0.1 keeps its switch marker 30 s (ClearLater)
MAX_CAP = 1024          # hard cap on slots per page (a hand-edited file cannot make a huge container)
MAX_PAGE = 1000         # hard cap on page numbers

cfg  = pool.makeClass(PKG + ".VCfg")
dat  = pool.makeClass(PKG + ".VData")
cod  = pool.makeClass(PKG + ".VCodec")
sto  = pool.makeClass(PKG + ".VStore")
sjob = pool.makeClass(PKG + ".VSaveJob")
thf  = pool.makeClass(PKG + ".VThreads")
ses  = pool.makeClass(PKG + ".VSession")
chg  = pool.makeClass(PKG + ".VChange")
win  = pool.makeClass(PKG + ".VWindow", pool.get(T["CW"]))
page = pool.makeClass(PKG + ".VaultPage", pool.get(T["PAGE"]))
clt  = pool.makeClass(PKG + ".VCloseTask")
vs   = pool.makeClass(PKG + ".VSessions")
tick = pool.makeClass(PKG + ".VTick")
pl   = pool.makeClass(PKG + ".SkyyVaultPlugin", pool.get(T["JP"]))
ALL = [cfg, dat, cod, sto, sjob, thf, ses, chg, win, page, clt, vs, tick]

# ================= VCfg: logger, bridge, config, atomic files =================
CFG_LINES = [
    "# SkyyVault config - edit, then /vaultadmin reload (or restart the server)",
    "# freePages = vault pages every player owns for free (the vault is shared by all profiles of a player)",
    "freePages=%d" % DEF_FREE,
    "# maxPages = the most vault pages a player can own (free + bought)",
    "maxPages=%d" % DEF_MAX,
    "# slotsPerPage = slots on one vault page (36 = a large chest). Applies to vaults loaded after a reload / restart.",
    "# Lowering it never hides items: a vault that already uses a higher slot keeps its bigger pages.",
    "slotsPerPage=%d" % DEF_SLOTS,
    "# pagePrice = coins for the first bought page; each later page costs pagePriceStep more",
    "# (with freePages=2: page 3 = pagePrice, page 4 = pagePrice + pagePriceStep, ...)",
    "pagePrice=%d" % DEF_PRICE,
    "pagePriceStep=%d" % DEF_STEP,
    "# openMode = page: /vault opens the vault page (buttons) together with the vault slots; its Open as chest button opens the plain chest",
    "#            chest: /vault opens the plain chest window at once; /vault pages opens the page with the buttons",
    "openMode=page",
    "# afterSwitchSeconds = the vault stays shut this many seconds after a profile switch (or a crash recovery at join).",
    "# SkyyProfiles keeps its switch marker 30 s: a server crash in that time undoes every inventory change since the switch,",
    "# so a vault move then would duplicate or lose items. Lower = less waiting but that crash window comes back.",
    "afterSwitchSeconds=%d" % DEF_AFTER_SWITCH_S,
    "# saveDelayMillis = how soon after a change the vault file is written (closing the vault writes it at once)",
    "saveDelayMillis=%d" % DEF_SAVE_DELAY_MS,
]
for f in ("public static java.nio.file.Path DIR;", "public static java.nio.file.Path VDIR;", "public static java.nio.file.Path FILE;",
          "public static java.nio.file.Path LOGF;", "public static java.nio.file.Path NAMESF;", "public static @LOG@ LOG;",
          "public static volatile int FREE_PAGES = %d;" % DEF_FREE, "public static volatile int MAX_PAGES = %d;" % DEF_MAX,
          "public static volatile int SLOTS = %d;" % DEF_SLOTS, "public static volatile long PRICE = %dL;" % DEF_PRICE,
          "public static volatile long STEP = %dL;" % DEF_STEP, "public static volatile long AFTER_SWITCH_MS = %dL;" % (DEF_AFTER_SWITCH_S * 1000),
          "public static volatile long SAVE_DELAY_MS = %dL;" % DEF_SAVE_DELAY_MS, "public static volatile boolean PAGE_MODE = true;",
          "public static final long CONFIRM_MS = 10000L;", "public static final int MAX_CAP = %d;" % MAX_CAP,
          "public static final int MAX_PAGE = %d;" % MAX_PAGE,
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();"):
    F(cfg, f)
F(cfg, "public static final String[] DEFAULT_LINES = %s;" % jarr(CFG_LINES))
M(cfg, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(cfg, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyVault] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyVault] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warnOnce(String key, String msg) {
  long now = System.currentTimeMillis();
  Object last = WARNED.get(key);
  if (last instanceof Long && now - ((Long) last).longValue() < 60000L) return;
  WARNED.put(key, Long.valueOf(now));
  warn(msg);
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d, long lo, long hi) {
  long v = d;
  try { String s = p.getProperty(k); if (s != null) v = Long.parseLong(s.trim()); } catch (Throwable t) { v = d; }
  if (v < lo) v = lo;
  if (v > hi) v = hi;
  return v;
}""")
# tmp file + fsync + atomic rename, 5 x 20 ms retries on a Windows FileSystemException (SkyyProfiles 0.1 ProfCfg.atomicWrite)
M(cfg, r"""
public static void atomicWrite(java.nio.file.Path f, byte[] data) throws java.io.IOException {
  java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
  try {
    out.write(data);
    out.flush();
    out.getFD().sync();
  } finally { out.close(); }
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(cfg, r"""
public static String readText(java.nio.file.Path f) throws java.io.IOException {
  return new String(java.nio.file.Files.readAllBytes(f), "UTF-8");
}""")
M(cfg, r"""
public static void appendLine(java.nio.file.Path f, String line) {
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(f, (line + "\n").getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { warn("could not append to " + f + ": " + t); }
}""")
M(cfg, r"""
public static synchronized String load() {
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < DEFAULT_LINES.length; i++) sb.append(DEFAULT_LINES[i]).append("\n");
      atomicWrite(FILE, sb.toString().getBytes("UTF-8"));
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    int fp = (int) lng(p, "freePages", (long) FREE_PAGES, 1L, 100L);
    int mp = (int) lng(p, "maxPages", (long) MAX_PAGES, 1L, (long) MAX_PAGE);
    if (mp < fp) mp = fp;
    FREE_PAGES = fp;
    MAX_PAGES = mp;
    SLOTS = (int) lng(p, "slotsPerPage", (long) SLOTS, 9L, 90L);
    PRICE = lng(p, "pagePrice", PRICE, 0L, 1000000000000L);
    STEP = lng(p, "pagePriceStep", STEP, 0L, 1000000000000L);
    AFTER_SWITCH_MS = lng(p, "afterSwitchSeconds", AFTER_SWITCH_MS / 1000L, 0L, 120L) * 1000L;
    SAVE_DELAY_MS = lng(p, "saveDelayMillis", SAVE_DELAY_MS, 100L, 30000L);
    String om = p.getProperty("openMode");
    if (om != null) {
      om = om.trim().toLowerCase();
      if (om.equals("chest")) PAGE_MODE = false;
      else if (om.equals("page")) PAGE_MODE = true;
    }
  } catch (Throwable t) { warn("config.properties could not be read (defaults / previous values kept): " + t); }
  return "free pages " + FREE_PAGES + ", max " + MAX_PAGES + ", " + SLOTS + " slots per page, price " + PRICE + " +" + STEP + " per page, openMode " + (PAGE_MODE ? "page" : "chest");
}""")

# ================= VData: one player's vault in memory (arrays = what the player sees) =================
for f in ("public java.util.UUID owner;", "public String name;", "public int unlocked;", "public int cap;",
          "public java.util.ArrayList pages;", "public org.bson.BsonArray orphans;", "public volatile long rev;",
          "public volatile long writtenRev;", "public Object ioLock;"):
    F(dat, f)
C(dat, r"""
public VData(java.util.UUID o, int cap) {
  this.owner = o; this.name = ""; this.unlocked = 0; this.cap = cap;
  this.pages = new java.util.ArrayList(); this.orphans = new org.bson.BsonArray();
  this.rev = 0L; this.writtenRev = 0L; this.ioLock = new Object();
}""")
M(dat, r"""
public synchronized @IS@[] page(int n) {
  while (this.pages.size() < n) this.pages.add(new @IS@[this.cap]);
  return (@IS@[]) this.pages.get(n - 1);
}""")
M(dat, r"""
public synchronized int used(int n) {
  if (n < 1 || n > this.pages.size()) return 0;
  @IS@[] a = (@IS@[]) this.pages.get(n - 1);
  int c = 0;
  for (int i = 0; i < a.length; i++) if (a[i] != null && !a[i].isEmpty()) c++;
  return c;
}""")
M(dat, r"""
public synchronized int highestUsed() {
  for (int p = this.pages.size(); p >= 1; p--) if (used(p) > 0) return p;
  return 0;
}""")
M(dat, r"""
public synchronized int total() {
  int c = 0;
  for (int p = 1; p <= this.pages.size(); p++) c = c + used(p);
  return c;
}""")
M(dat, r"""
public synchronized @IS@[] pageCopy(int n) {
  @IS@[] a = page(n);
  @IS@[] c = new @IS@[a.length];
  System.arraycopy(a, 0, c, 0, a.length);
  return c;
}""")
# the view -> page array copy (every change event); true when anything changed (then rev + 1)
M(dat, r"""
public synchronized boolean copyIn(int n, @IS@[] now) {
  @IS@[] a = page(n);
  boolean ch = false;
  for (int i = 0; i < a.length && i < now.length; i++) {
    if (a[i] != now[i]) { a[i] = now[i]; ch = true; }
  }
  if (ch) this.rev = this.rev + 1L;
  return ch;
}""")

# ================= VCodec: the SkyyProfiles 0.1 lossless slot format =================
M(cod, r"""
public static int intOf(org.bson.BsonDocument d, String k, int def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(cod, r"""
public static double dblOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().doubleValue(); } catch (Throwable t) { }
  return 0.0;
}""")
M(cod, r"""
public static String strOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return null;
}""")
M(cod, r"""
public static org.bson.BsonDocument slotDoc(int slot, @IS@ s) {
  org.bson.BsonDocument d = new org.bson.BsonDocument();
  d.put("slot", new org.bson.BsonInt32(slot));
  d.put("id", new org.bson.BsonString(s.getItemId()));
  d.put("qty", new org.bson.BsonInt32(s.getQuantity()));
  d.put("durability", new org.bson.BsonDouble(s.getDurability()));
  d.put("maxDurability", new org.bson.BsonDouble(s.getMaxDurability()));
  d.put("quality", new org.bson.BsonInt32(s.getQualityIndex()));
  d.put("overrideAnim", new org.bson.BsonBoolean(s.getOverrideDroppedItemAnimation()));
  org.bson.BsonDocument m = s.getMetadata();
  if (m != null) d.put("meta", (org.bson.BsonDocument) m.clone());
  try {
    org.bson.BsonValue enc = ((@CODEC@) @IS@.CODEC).encode(s);
    if (enc != null) d.put("stack", enc);
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("enc-" + s.getItemId(), "ItemStack.CODEC could not encode " + s.getItemId() + " (explicit fields kept): " + t); }
  return d;
}""")
# engine codec first (exact engine persistence semantics), explicit fields as the fallback; null = cannot be rebuilt (kept as orphan)
M(cod, r"""
public static @IS@ stackOf(org.bson.BsonDocument d) {
  String id = strOf(d, "id");
  int qty = intOf(d, "qty", 0);
  if (id == null || id.length() == 0 || qty <= 0) return null;
  try {
    org.bson.BsonValue enc = (org.bson.BsonValue) d.get("stack");
    if (enc != null && enc.isDocument()) {
      Object o = ((@CODEC@) @IS@.CODEC).decode(enc);
      if (o instanceof @IS@) {
        @IS@ s = (@IS@) o;
        if (!s.isEmpty() && id.equals(s.getItemId()) && s.getQuantity() == qty) return s;
      }
    }
  } catch (Throwable t) { }
  org.bson.BsonDocument meta = null;
  try { org.bson.BsonValue mv = (org.bson.BsonValue) d.get("meta"); if (mv != null && mv.isDocument()) meta = mv.asDocument(); } catch (Throwable t) { }
  @IS@ s2 = null;
  try { s2 = new @IS@(id, qty, dblOf(d, "durability"), dblOf(d, "maxDurability"), intOf(d, "quality", 0), meta); }
  catch (Throwable t) { return null; }
  try {
    org.bson.BsonValue a = (org.bson.BsonValue) d.get("overrideAnim");
    if (a != null && a.isBoolean() && a.asBoolean().getValue()) s2.setOverrideDroppedItemAnimation(true);
  } catch (Throwable t) { }
  return s2;
}""")
M(cod, r"""
public static String toJson(org.bson.BsonDocument d) {
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).indent(true).build();
  return d.toJson(s);
}""")
M(cod, r"""
public static int countSlots(org.bson.BsonDocument doc) {
  if (doc == null) return -1;
  int n = 0;
  org.bson.BsonArray c = doc.getArray("content", new org.bson.BsonArray());
  for (int i = 0; i < c.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) c.get(i);
    if (v != null && v.isDocument()) n = n + v.asDocument().getArray("slots", new org.bson.BsonArray()).size();
  }
  return n + doc.getArray("orphans", new org.bson.BsonArray()).size();
}""")

# ================= VStore: cache, load, files, saver, buy =================
for f in ("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap CONFIRM = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();",
          "public static volatile boolean NAMES_DIRTY = false;",
          "public static volatile java.util.concurrent.ScheduledExecutorService SAVER = null;",
          "public static volatile boolean STOPPING = false;"):
    F(sto, f)
M(sto, r"""
public static java.nio.file.Path fileOf(java.util.UUID u) {
  return @PKG@.VCfg.VDIR.resolve(u.toString() + ".json");
}""")
M(sto, r"""
public static void log(String line) {
  @PKG@.VCfg.appendLine(@PKG@.VCfg.LOGF, java.time.Instant.now().toString() + " " + line);
}""")
M(sto, r"""
public static String grp(long n) {
  String s = Long.toString(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (n < 0L) sb.append('-');
  return sb.reverse().toString();
}""")
# compact amount for button text (inline Text avoids commas): 50000 -> 50k, 1500000 -> 1.5m
M(sto, r"""
public static String shortAmt(long n) {
  if (n >= 1000000L) {
    long t = n / 100000L;
    return (t % 10L == 0L) ? (t / 10L) + "m" : (t / 10L) + "." + (t % 10L) + "m";
  }
  if (n >= 1000L) {
    long t = n / 100L;
    return (t % 10L == 0L) ? (t / 10L) + "k" : (t / 10L) + "." + (t % 10L) + "k";
  }
  return String.valueOf(n);
}""")
M(sto, r"""
public static long price(int page) {
  if (page <= @PKG@.VCfg.FREE_PAGES) return 0L;
  long p = @PKG@.VCfg.PRICE + @PKG@.VCfg.STEP * (long) (page - @PKG@.VCfg.FREE_PAGES - 1);
  return p < 0L ? 0L : p;
}""")
M(sto, r"""
public static String nameOf(@PKG@.VData d) {
  if (d == null) return "?";
  if (d.name != null && d.name.length() > 0) return d.name;
  return d.owner.toString();
}""")
# the whole vault as one BsonDocument; the caller holds the VData monitor (VData.snap)
M(sto, r"""
public static org.bson.BsonDocument toDoc(@PKG@.VData d) {
  org.bson.BsonDocument doc = new org.bson.BsonDocument();
  doc.put("format", new org.bson.BsonInt32(1));
  doc.put("mod", new org.bson.BsonString("SkyyVault"));
  doc.put("version", new org.bson.BsonString("@VERSION@"));
  doc.put("uuid", new org.bson.BsonString(d.owner.toString()));
  doc.put("name", new org.bson.BsonString(d.name == null ? "" : d.name));
  doc.put("pages", new org.bson.BsonInt32(d.unlocked));
  doc.put("capacity", new org.bson.BsonInt32(d.cap));
  doc.put("savedAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  doc.put("rev", new org.bson.BsonInt64(d.rev));
  org.bson.BsonArray content = new org.bson.BsonArray();
  int count = 0;
  for (int p = 0; p < d.pages.size(); p++) {
    @IS@[] a = (@IS@[]) d.pages.get(p);
    org.bson.BsonArray slots = new org.bson.BsonArray();
    for (int i = 0; i < a.length; i++) {
      if (a[i] == null || a[i].isEmpty()) continue;
      slots.add(@PKG@.VCodec.slotDoc(i, a[i]));
      count++;
    }
    if (slots.size() > 0) {
      org.bson.BsonDocument pd = new org.bson.BsonDocument();
      pd.put("page", new org.bson.BsonInt32(p + 1));
      pd.put("slots", slots);
      content.add(pd);
    }
  }
  doc.put("content", content);
  doc.put("count", new org.bson.BsonInt32(count));
  doc.put("orphans", d.orphans);
  return doc;
}""")
# one saved slot into the arrays; anything that cannot be placed (unknown item, bad page/slot, slot taken) is kept as an orphan
M(sto, r"""
public static void place(@PKG@.VData d, int pg, org.bson.BsonDocument sd) {
  int s = @PKG@.VCodec.intOf(sd, "slot", -1);
  @IS@ st = null;
  if (pg >= 1 && pg <= @PKG@.VCfg.MAX_PAGE && s >= 0 && s < d.cap) st = @PKG@.VCodec.stackOf(sd);
  if (st != null) {
    @IS@[] a = d.page(pg);
    if (a[s] == null) { a[s] = st; return; }
  }
  org.bson.BsonDocument o = (org.bson.BsonDocument) sd.clone();
  o.put("page", new org.bson.BsonInt32(pg));
  d.orphans.add(o);
  @PKG@.VCfg.warn("kept a vault stack that cannot be placed for " + d.owner + " (page " + pg + " slot " + s + ", " + @PKG@.VCodec.strOf(sd, "id") + ") - saved unchanged, retried at every load");
}""")
M(sto, r"""
public static @PKG@.VData fromDoc(java.util.UUID u, org.bson.BsonDocument doc) {
  org.bson.BsonArray content = doc.getArray("content", new org.bson.BsonArray());
  org.bson.BsonArray orph = doc.getArray("orphans", new org.bson.BsonArray());
  int maxSlot = -1;
  int maxPage = 0;
  for (int i = 0; i < content.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) content.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument pd = v.asDocument();
    int pg = @PKG@.VCodec.intOf(pd, "page", 0);
    org.bson.BsonArray sl = pd.getArray("slots", new org.bson.BsonArray());
    if (sl.size() > 0 && pg > maxPage && pg <= @PKG@.VCfg.MAX_PAGE) maxPage = pg;
    for (int k = 0; k < sl.size(); k++) {
      org.bson.BsonValue sv = (org.bson.BsonValue) sl.get(k);
      if (sv == null || !sv.isDocument()) continue;
      int s = @PKG@.VCodec.intOf(sv.asDocument(), "slot", -1);
      if (s > maxSlot && s < @PKG@.VCfg.MAX_CAP) maxSlot = s;
    }
  }
  for (int i = 0; i < orph.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) orph.get(i);
    if (v == null || !v.isDocument()) continue;
    int pg = @PKG@.VCodec.intOf(v.asDocument(), "page", 0);
    int s = @PKG@.VCodec.intOf(v.asDocument(), "slot", -1);
    if (pg > maxPage && pg <= @PKG@.VCfg.MAX_PAGE) maxPage = pg;
    if (s > maxSlot && s < @PKG@.VCfg.MAX_CAP) maxSlot = s;
  }
  int cap = @PKG@.VCfg.SLOTS;
  if (maxSlot + 1 > cap) cap = maxSlot + 1;
  @PKG@.VData d = new @PKG@.VData(u, cap);
  String nm = @PKG@.VCodec.strOf(doc, "name");
  d.name = nm == null ? "" : nm;
  int pages = @PKG@.VCodec.intOf(doc, "pages", @PKG@.VCfg.FREE_PAGES);
  if (pages < @PKG@.VCfg.FREE_PAGES) pages = @PKG@.VCfg.FREE_PAGES;
  if (pages < maxPage) pages = maxPage;
  if (pages > @PKG@.VCfg.MAX_PAGE) pages = @PKG@.VCfg.MAX_PAGE;
  d.unlocked = pages;
  d.page(pages);
  for (int i = 0; i < content.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) content.get(i);
    if (v == null || !v.isDocument()) continue;
    org.bson.BsonDocument pd = v.asDocument();
    int pg = @PKG@.VCodec.intOf(pd, "page", 0);
    org.bson.BsonArray sl = pd.getArray("slots", new org.bson.BsonArray());
    for (int k = 0; k < sl.size(); k++) {
      org.bson.BsonValue sv = (org.bson.BsonValue) sl.get(k);
      if (sv != null && sv.isDocument()) place(d, pg, sv.asDocument());
    }
  }
  for (int i = 0; i < orph.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) orph.get(i);
    if (v != null && v.isDocument()) place(d, @PKG@.VCodec.intOf(v.asDocument(), "page", 0), v.asDocument());
  }
  return d;
}""")
# first use: missing file = a fresh vault (no file is written until something changes); unreadable file = null (vault stays shut,
# never cached, re-read on the next try, never overwritten)
M(sto, r"""
public static synchronized @PKG@.VData loadLocked(java.util.UUID u) {
  Object c = CACHE.get(u);
  if (c != null) return (@PKG@.VData) c;
  java.nio.file.Path f = fileOf(u);
  @PKG@.VData d = null;
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      d = new @PKG@.VData(u, @PKG@.VCfg.SLOTS);
      d.unlocked = @PKG@.VCfg.FREE_PAGES;
      d.page(d.unlocked);
    } else {
      d = fromDoc(u, org.bson.BsonDocument.parse(@PKG@.VCfg.readText(f)));
    }
  } catch (Throwable t) {
    @PKG@.VCfg.warnOnce("read-" + u, "vault file " + f + " cannot be read - that vault stays shut and the file is not touched until it reads again: " + t);
    return null;
  }
  if (d == null) return null;
  CACHE.put(u, d);
  return d;
}""")
M(sto, r"""
public static @PKG@.VData load(java.util.UUID u) {
  if (u == null) return null;
  Object c = CACHE.get(u);
  if (c != null) return (@PKG@.VData) c;
  return loadLocked(u);
}""")

# ---- VData methods that need VStore.toDoc (synchronized instance methods: no synchronized blocks)
M(dat, r"""
public synchronized Object[] snap() {
  return new Object[] { @PKG@.VStore.toDoc(this), Long.valueOf(this.rev) };
}""")
M(dat, r"""
public synchronized Object[] unlockTo(int next) {
  if (this.unlocked != next - 1) return null;
  this.unlocked = next;
  page(next);
  this.rev = this.rev + 1L;
  return snap();
}""")
M(dat, r"""
public synchronized boolean relock(int next) {
  if (this.unlocked != next || used(next) > 0) return false;
  this.unlocked = next - 1;
  this.rev = this.rev + 1L;
  return true;
}""")
M(dat, r"""
public synchronized Object[] setUnlocked(int n) {
  this.unlocked = n;
  page(n);
  this.rev = this.rev + 1L;
  return snap();
}""")

# ---- file writes: ordered by revision under the per-vault IO lock (an older snapshot never overwrites a newer file)
M(sto, r"""
public static boolean write0(@PKG@.VData d, org.bson.BsonDocument doc, long r) {
  if (r <= d.writtenRev) return true;
  java.nio.file.Path f = fileOf(d.owner);
  try {
    int want = @PKG@.VCodec.countSlots(doc);
    @PKG@.VCfg.atomicWrite(f, @PKG@.VCodec.toJson(doc).getBytes("UTF-8"));
    org.bson.BsonDocument back = org.bson.BsonDocument.parse(@PKG@.VCfg.readText(f));
    if (@PKG@.VCodec.countSlots(back) != want) { @PKG@.VCfg.warn("vault file " + f + " did not read back correctly (kept in memory, retrying)"); return false; }
    d.writtenRev = r;
    return true;
  } catch (Throwable t) {
    @PKG@.VCfg.warnOnce("write-" + d.owner, "could not write vault file " + f + " (kept in memory, retrying): " + t);
    return false;
  }
}""")
M(sto, r"""
public static boolean writeDoc(@PKG@.VData d, org.bson.BsonDocument doc, long r) {
  synchronized (d.ioLock) {
    return write0(d, doc, r);
  }
}""")
F(sjob, "public java.util.UUID owner;")
C(sjob, "public VSaveJob(java.util.UUID o) { this.owner = o; }")
sjob.addInterface(pool.get("java.lang.Runnable"))
M(sto, r"""
public static void retryLater(java.util.UUID u) {
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) return;
  if (PENDING.putIfAbsent(u, Boolean.TRUE) != null) return;
  try { ex.schedule(new @PKG@.VSaveJob(u), 5000L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { PENDING.remove(u); }
}""")
M(sto, r"""
public static void saveJob(java.util.UUID u) {
  PENDING.remove(u);
  @PKG@.VData d = (@PKG@.VData) CACHE.get(u);
  if (d == null) return;
  if (d.rev == d.writtenRev) return;
  Object[] sn = d.snap();
  boolean ok = writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) { log("WRITE-FAIL " + u + " rev " + sn[1] + " (kept in memory, retrying in 5 s)"); retryLater(u); }
}""")
M(sto, r"""
public static void saveSoon(java.util.UUID u, long delay) {
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { saveJob(u); return; }
  try {
    if (delay <= 0L) { ex.execute(new @PKG@.VSaveJob(u)); return; }
    if (PENDING.putIfAbsent(u, Boolean.TRUE) != null) return;
    ex.schedule(new @PKG@.VSaveJob(u), delay, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { PENDING.remove(u); saveJob(u); }
}""")
M(sto, r"""
public static void saveNames() {
  try {
    NAMES_DIRTY = false;
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = NAMES.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      p.setProperty((String) e.getKey(), (String) e.getValue());
    }
    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
    p.store(bo, "SkyyVault: lower-case player name = uuid (for /vaultadmin with offline players)");
    @PKG@.VCfg.atomicWrite(@PKG@.VCfg.NAMESF, bo.toByteArray());
  } catch (Throwable t) { NAMES_DIRTY = true; @PKG@.VCfg.warnOnce("names", "could not write names.properties: " + t); }
}""")
M(sjob, r"""
public void run() {
  try {
    if (this.owner == null) @PKG@.VStore.saveNames();
    else @PKG@.VStore.saveJob(this.owner);
  } catch (Throwable t) { @PKG@.VCfg.warn("vault save job failed: " + t); }
}""")
M(sto, r"""
public static void flushAll() {
  java.util.Iterator it = CACHE.values().iterator();
  while (it.hasNext()) {
    @PKG@.VData d = (@PKG@.VData) it.next();
    try {
      if (d.rev != d.writtenRev) {
        Object[] sn = d.snap();
        if (!writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue())) log("SHUTDOWN-WRITE-FAIL " + d.owner + " rev " + sn[1]);
      }
    } catch (Throwable t) { @PKG@.VCfg.warn("vault flush failed for " + d.owner + ": " + t); }
  }
  if (NAMES_DIRTY) saveNames();
}""")
M(sto, r"""
public static void loadNames() {
  try {
    if (!java.nio.file.Files.exists(@PKG@.VCfg.NAMESF, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(@PKG@.VCfg.NAMESF, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Iterator it = p.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); NAMES.put(k, p.getProperty(k)); }
  } catch (Throwable t) { @PKG@.VCfg.warn("names.properties could not be read: " + t); }
}""")
M(sto, r"""
public static void noteName(@PKG@.VData d, String name) {
  if (d == null || name == null || name.length() == 0 || name.equals(d.name)) return;
  d.name = name;
  NAMES.put(name.toLowerCase(), d.owner.toString());
  NAMES_DIRTY = true;
  java.util.concurrent.ScheduledExecutorService ex = SAVER;
  if (STOPPING || ex == null) { saveNames(); return; }
  try { ex.execute(new @PKG@.VSaveJob((java.util.UUID) null)); } catch (Throwable t) { }
}""")
M(sto, r"""
public static java.util.UUID resolve(String who) {
  if (who == null) return null;
  String w = who.trim();
  if (w.length() == 0) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.getUsername() != null && p.getUsername().equalsIgnoreCase(w)) return p.getUuid();
    }
  } catch (Throwable t) { }
  try { return java.util.UUID.fromString(w); } catch (Throwable t) { }
  Object s = NAMES.get(w.toLowerCase());
  if (s instanceof String) { try { return java.util.UUID.fromString((String) s); } catch (Throwable t) { } }
  return null;
}""")
# arm on the first call, true on a second call within CONFIRM_MS. ONE key for the page's Buy button AND /vault buy, naming the page
# number, so a click and a typed command combine and a confirm armed for page N never buys page N + 1.
M(sto, r"""
public static String buyKey(java.util.UUID u, int page) {
  return "buy:" + u + ":" + page;
}""")
M(sto, r"""
public static boolean confirm(String key) {
  long now = System.currentTimeMillis();
  Object o = CONFIRM.get(key);
  if (o instanceof Long && ((Long) o).longValue() >= now) { CONFIRM.remove(key); return true; }
  CONFIRM.put(key, Long.valueOf(now + @PKG@.VCfg.CONFIRM_MS));
  return false;
}""")
M(sto, r"""
public static boolean armed(String key) {
  Object o = CONFIRM.get(key);
  return o instanceof Long && ((Long) o).longValue() >= System.currentTimeMillis();
}""")
M(sto, r"""
public static void disarm(String key) {
  CONFIRM.remove(key);
}""")
M(sto, r"""
public static void pruneConfirms(long now) {
  java.util.Iterator it = CONFIRM.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object v = e.getValue();
    if (!(v instanceof Long) || ((Long) v).longValue() < now) it.remove();
  }
}""")
M(sto, r"""
public static String refund(java.util.UUID u, long cost) {
  if (cost <= 0L) return "";
  Object add = @PKG@.VCfg.bridge().get("coins:fn:add");
  Object r = null;
  try { if (add instanceof java.util.function.Function) r = ((java.util.function.Function) add).apply(new Object[] { u, Long.valueOf(cost) }); } catch (Throwable t) { r = null; }
  if (r instanceof Long) { log("REFUND " + u + " " + cost); return " Your " + grp(cost) + " coins were refunded."; }
  log("REFUND-ERROR " + u + " " + cost + " coins could not be refunded - give them back by hand");
  @PKG@.VCfg.warn("REFUND-ERROR: " + cost + " coins for " + u + " could not be refunded (see vault.log)");
  return " The refund failed - an admin has been told (vault.log).";
}""")
# buy the next page: coins first (must be TRUE), then the page, written and read back; a failed write reverts + refunds
M(sto, r"""
public static String buy(java.util.UUID u, String name) {
  @PKG@.VData d = load(u);
  if (d == null) return "-Your vault file cannot be read - nothing was charged. Please tell an admin.";
  int next = d.unlocked + 1;
  if (next > @PKG@.VCfg.MAX_PAGES) return "-You already own every vault page (" + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + ").";
  long cost = price(next);
  if (cost > 0L) {
    Object take = @PKG@.VCfg.bridge().get("coins:fn:take");
    if (!(take instanceof java.util.function.Function)) return "-Coins are not available on this server (SkyyCoins is missing) - nothing changed.";
    Object r = null;
    try { r = ((java.util.function.Function) take).apply(new Object[] { u, Long.valueOf(cost) }); } catch (Throwable t) { r = null; }
    if (r == null) return "-Your purse could not be read right now - nothing was charged.";
    if (!Boolean.TRUE.equals(r)) return "-Vault page " + next + " costs " + grp(cost) + " coins - you do not have enough.";
  }
  Object[] sn = d.unlockTo(next);
  if (sn == null) return "-Your vault changed while buying - nothing bought." + refund(u, cost);
  boolean ok = writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) {
    boolean back = d.relock(next);
    saveSoon(u, 0L);
    log("BUY-FAIL " + u + " " + name + " page " + next + " cost " + cost + (back ? " (page taken back)" : " (page kept - it already held items)"));
    if (!back) return "+Bought vault page " + next + " - the file will be saved on the next try.";
    return "-The vault file could not be saved - page " + next + " was not bought." + refund(u, cost);
  }
  log("BUY " + u + " " + name + " page " + next + " cost " + cost);
  return "+Bought vault page " + next + " for " + grp(cost) + " coins - you now own " + next + " of " + @PKG@.VCfg.MAX_PAGES + " pages.";
}""")
M(sto, r"""
public static String setPages(String admin, java.util.UUID u, int n, int viewing) {
  @PKG@.VData d = load(u);
  if (d == null) return "-That vault file cannot be read (it was not touched).";
  if (n < 1 || n > @PKG@.VCfg.MAX_PAGE) return "-Pages must be 1 to " + @PKG@.VCfg.MAX_PAGE + ".";
  int hi = d.highestUsed();
  if (n < hi) return "-Page " + hi + " still holds items - it cannot be removed (items are never hidden).";
  if (viewing > n) return "-" + nameOf(d) + " is looking at vault page " + viewing + " right now - try again when they close it.";
  int old = d.unlocked;
  Object[] sn = d.setUnlocked(n);
  boolean ok = writeDoc(d, (org.bson.BsonDocument) sn[0], ((Long) sn[1]).longValue());
  if (!ok) retryLater(u);
  log("SETPAGES " + admin + " " + u + " " + old + " -> " + n + (ok ? "" : " (write failed - retrying)"));
  return "+" + nameOf(d) + " now owns " + n + " vault pages (was " + old + ").";
}""")
M(sto, r"""
public static String[] infoLines(java.util.UUID u, int viewing, boolean admin) {
  @PKG@.VData d = load(u);
  if (d == null) return new String[] { "-That vault file cannot be read - nothing in it was changed. " + (admin ? "Check the server log." : "Please tell an admin.") };
  java.util.ArrayList out = new java.util.ArrayList();
  int max = d.unlocked > @PKG@.VCfg.MAX_PAGES ? d.unlocked : @PKG@.VCfg.MAX_PAGES;
  out.add("=" + (admin ? "Vault of " + nameOf(d) + " (" + d.owner + ")" : "Your vault") + ": " + d.unlocked + " of " + max + " pages, " + d.cap + " slots each, " + d.total() + " stacks - shared by all profiles.");
  StringBuilder sb = new StringBuilder();
  for (int p = 1; p <= d.unlocked; p++) {
    if (sb.length() > 0) sb.append("  |  ");
    sb.append("Page ").append(p).append(": ").append(d.used(p)).append("/").append(d.cap);
    if (p == viewing) sb.append(" (open)");
    if (p % 5 == 0 || p == d.unlocked) { out.add("=" + sb.toString()); sb = new StringBuilder(); }
  }
  if (d.orphans.size() > 0) out.add("-" + d.orphans.size() + " stack(s) belong to items this server does not have right now - kept safe in the file" + (admin ? " (orphans)." : ", tell an admin."));
  if (d.unlocked < @PKG@.VCfg.MAX_PAGES) out.add("=Next page (" + (d.unlocked + 1) + ") costs " + grp(price(d.unlocked + 1)) + " coins" + (admin ? "." : " - /vault buy"));
  if (!admin) out.add("=/vault opens it, /vault 2 opens page 2, /vault next | prev switch pages, /vault pages shows the page buttons.");
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")

# ================= VThreads: daemon saver thread =================
thf.addInterface(pool.get("java.util.concurrent.ThreadFactory"))
C(thf, "public VThreads() { }")
M(thf, r"""
public Thread newThread(Runnable r) {
  Thread t = new Thread(r, "SkyyVault-saver");
  t.setDaemon(true);
  return t;
}""")

# ================= VSession: one open (editable) view of a vault =================
for f in ("public java.util.UUID owner;", "public java.util.UUID viewer;", "public @PR@ pr;", "public int page;", "public int mode;",
          "public @SIC@ view;", "public @PKG@.VWindow window;", "public @EREG@ reg;", "public volatile boolean closed;",
          "public volatile boolean swapping;", "public volatile boolean noSync;", "public Object epoch;", "public Object pageObj;",
          "public long askedClose;", "public int offline;"):
    F(ses, f)
C(ses, r"""
public VSession() {
  this.page = 1; this.mode = 1; this.closed = false; this.swapping = false; this.noSync = false;
  this.epoch = null; this.pageObj = null; this.askedClose = 0L; this.offline = 0;
}""")
M(ses, r"""
public synchronized boolean close1() {
  if (this.closed) return false;
  this.closed = true;
  return true;
}""")

# ================= VChange / VWindow constructors (bodies that call VSessions come later) =================
chg.addInterface(pool.get("java.util.function.Consumer"))
F(chg, "public @PKG@.VSession sess;")
C(chg, "public VChange(@PKG@.VSession s) { this.sess = s; }")
win.addInterface(pool.get(T["VWIN"]))
F(win, "public @PKG@.VSession sess;")
C(win, "public VWindow(@IC@ c, @PKG@.VSession s) { super(c); this.sess = s; }")

# ================= VaultPage part 1 (inline, rebuilt only after a click; never periodic updates) =================
for f in ("public @PKG@.VSession sess;", "public int sel;", "public String info;"):
    F(page, f)
C(page, r"""
public VaultPage(@PR@ pr, @PKG@.VSession s, int sel) {
  super(pr, @LIFE@.CanDismiss);
  this.sess = s; this.sel = sel < 1 ? 1 : sel; this.info = "";
}""")
M(page, r"""
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
}""")
M(page, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 / SkyyGuilds 0.1 jsonStr)
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
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(page, r"""
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#cfe3ff";
}""")
M(page, r"""
public static String textOf(String res) {
  if (res == null || res.length() == 0) return "";
  char c = res.charAt(0);
  if (c == '+' || c == '-' || c == '=') return res.substring(1);
  return res;
}""")
M(page, r"""
public void refreshWith(String res) {
  if (this.sess != null && !this.sess.closed) this.sel = this.sess.page;
  this.info = res == null ? "" : res;
  rebuild();
}""")
M(page, r"""
public void refresh() {
  refreshWith((String) null);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ store) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  boolean live = this.sess != null && !this.sess.closed;
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 19);
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 19);
  String ys = style("#6a4a12", "#8a641a", "#3e2a08", "#fff2d6", 19);
  String ds = style("#262f3d", "#303b4c", "#1a212c", "#7f8ea6", 19);
  b.appendInline((String) null, "Group #SkyyVault { Anchor: (Width: 1040, Height: 640); Background: #0b1524(0.96); Padding: (Horizontal: 26, Vertical: 16); LayoutMode: Top; }");
  b.appendInline("#SkyyVault", "Group { Anchor: (Height: 3); Background: #b48cff; }");
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 58); Text: \"Vault\"; Style: (FontSize: 34, RenderBold: true, TextColor: #dccaff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyVault", "Label #SkyyVSub { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 18, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyVSub.Text", "One chest shared by ALL your profiles - put items in on one profile and take them out on another.");
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 12); Text: \"\"; }");
  if (d == null) {
    b.appendInline("#SkyyVault", "Label #SkyyVErr { Anchor: (Height: 80); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ff9d6b, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyVErr.Text", "Your vault file cannot be read right now. Nothing in it was changed - please tell an admin.");
    b.appendInline("#SkyyVault", "Group #SkyyVErrRow { Anchor: (Height: 60); LayoutMode: Left; }");
    b.appendInline("#SkyyVErrRow", "Label { Anchor: (Width: 419, Height: 52); Text: \"\"; }");
    b.appendInline("#SkyyVErrRow", "TextButton #SkyyVClose { Anchor: (Width: 150, Height: 52); Text: \"Close\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyVClose", @EVD@.of("a", "close"));
    return;
  }
  int unlocked = d.unlocked;
  int max = unlocked > @PKG@.VCfg.MAX_PAGES ? unlocked : @PKG@.VCfg.MAX_PAGES;
  if (this.sel < 1) this.sel = 1;
  if (this.sel > max) this.sel = max;
  boolean showing = live && this.sess.page == this.sel;
  b.appendInline("#SkyyVault", "Group #SkyyVNav { Anchor: (Height: 60); LayoutMode: Left; }");
  b.appendInline("#SkyyVNav", "Label { Anchor: (Width: 65, Height: 52); Text: \"\"; }");
  b.appendInline("#SkyyVNav", "TextButton #SkyyVPrev { Anchor: (Width: 190, Height: 52); Text: \"< Prev\"; " + (this.sel > 1 ? bs : ds) + " }");
  b.appendInline("#SkyyVNav", "Label #SkyyVPageLbl { Anchor: (Width: 478, Height: 52); Text: \"\"; Style: (FontSize: 26, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyVPageLbl.Text", "Page " + this.sel + " of " + unlocked + (this.sel > unlocked ? "  (locked)" : ""));
  b.appendInline("#SkyyVNav", "TextButton #SkyyVNext { Anchor: (Width: 190, Height: 52); Text: \"Next >\"; " + (this.sel < max ? bs : ds) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVPrev", @EVD@.of("a", "prev"));
  ev.addEventBinding(@BT@.Activating, "#SkyyVNext", @EVD@.of("a", "next"));
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 10); Text: \"\"; }");
  int shown = max < 10 ? max : 10;
  int start = 1;
  if (max > 10) {
    start = this.sel - 4;
    if (start < 1) start = 1;
    if (start + 9 > max) start = max - 9;
  }
  int rowW = shown * 84 - 8;
  int pad = (988 - rowW) / 2;
  b.appendInline("#SkyyVault", "Group #SkyyVNums { Anchor: (Height: 58); LayoutMode: Left; }");
  if (pad > 0) b.appendInline("#SkyyVNums", "Label { Anchor: (Width: " + pad + ", Height: 52); Text: \"\"; }");
  for (int i = 0; i < shown; i++) {
    int n = start + i;
    String st = n == this.sel ? gs : (n <= unlocked ? bs : ds);
    if (i > 0) b.appendInline("#SkyyVNums", "Label { Anchor: (Width: 8, Height: 52); Text: \"\"; }");
    b.appendInline("#SkyyVNums", "TextButton #SkyyVNum" + n + " { Anchor: (Width: 76, Height: 52); Text: \"" + n + "\"; " + st + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyVNum" + n, @EVD@.of("a", "num:" + n));
  }
  b.appendInline("#SkyyVault", "Label #SkyyVUsed { Anchor: (Height: 44); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #e6f2ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  String used = "";
  if (this.sel <= unlocked) {
    used = "Page " + this.sel + " - " + d.used(this.sel) + " of " + d.cap + " slots used" + (showing ? " - showing now" : "");
    if (live && !showing) used = used + " (the slots still show page " + this.sess.page + ")";
  } else if (this.sel == unlocked + 1) {
    used = "Page " + this.sel + " is locked - it costs " + @PKG@.VStore.grp(@PKG@.VStore.price(this.sel)) + " coins";
  } else {
    used = "Page " + this.sel + " is locked - buy page " + (unlocked + 1) + " first";
  }
  b.set("#SkyyVUsed.Text", used);
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 6); Text: \"\"; }");
  b.appendInline("#SkyyVault", "Group #SkyyVAct { Anchor: (Height: 66); LayoutMode: Left; }");
  b.appendInline("#SkyyVAct", "Label { Anchor: (Width: 44, Height: 58); Text: \"\"; }");
  String openTxt = live ? "Open as chest" : ("Open page " + this.sel);
  b.appendInline("#SkyyVAct", "TextButton #SkyyVOpen { Anchor: (Width: 330, Height: 58); Text: \"" + openTxt + "\"; " + (this.sel <= unlocked ? gs : ds) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVOpen", @EVD@.of("a", "open"));
  b.appendInline("#SkyyVAct", "Label { Anchor: (Width: 20, Height: 58); Text: \"\"; }");
  int next = unlocked + 1;
  String buyTxt = "";
  String buySt = ds;
  if (next <= @PKG@.VCfg.MAX_PAGES) {
    long c = @PKG@.VStore.price(next);
    buyTxt = @PKG@.VStore.armed(@PKG@.VStore.buyKey(u, next)) ? ("Sure? Buy page " + next) : ("Buy page " + next + " - " + @PKG@.VStore.shortAmt(c) + " coins");
    buySt = ys;
  } else {
    buyTxt = "All pages bought";
    buySt = ds;
  }
  b.appendInline("#SkyyVAct", "TextButton #SkyyVBuy { Anchor: (Width: 380, Height: 58); Text: \"" + safe(buyTxt) + "\"; " + buySt + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVBuy", @EVD@.of("a", "buy"));
  b.appendInline("#SkyyVAct", "Label { Anchor: (Width: 20, Height: 58); Text: \"\"; }");
  b.appendInline("#SkyyVAct", "TextButton #SkyyVClose { Anchor: (Width: 150, Height: 58); Text: \"Close\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyVClose", @EVD@.of("a", "close"));
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 12); Text: \"\"; }");
  String[] help = null;
  if (live) {
    help = new String[] { "Drag items between your inventory and the vault slots. Close or Esc saves your vault.",
                          "Vault slots not showing next to this page? Click Open as chest.",
                          "Commands: /vault 2 opens page 2, /vault next and /vault prev switch pages, /vault info" };
  } else {
    help = new String[] { "Pick a page, then click Open to see its items as a chest.",
                          "In the chest: drag items in and out - Esc saves. /vault 2 or /vault next switches pages.",
                          "Every profile opens this same vault. Commands: /vault buy, /vault info" };
  }
  for (int i = 0; i < help.length; i++) {
    b.appendInline("#SkyyVault", "Label #SkyyVHelp" + i + " { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 17, TextColor: #b8c8d8, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyVHelp" + i + ".Text", help[i]);
  }
  b.appendInline("#SkyyVault", "Label { Anchor: (Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyVault", "Label #SkyyVInfo { Anchor: (Height: 36); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: " + colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyVInfo.Text", textOf(this.info));
}""")

# ================= VCloseTask constructor (run() comes after VSessions) =================
clt.addInterface(pool.get("java.lang.Runnable"))
# offline = true: the last-resort finalize of a session whose viewer is gone (VSessions.dispatchOffline), run on that world's thread
for f in ("public @PKG@.VSession sess;", "public String reason;", "public java.util.UUID wu;", "public boolean onlyIfPageGone;",
          "public boolean hop;", "public int tries;", "public boolean offline;"):
    F(clt, f)
C(clt, r"""
public VCloseTask(@PKG@.VSession s, String reason, java.util.UUID wu, boolean onlyIfPageGone, boolean hop) {
  this.sess = s; this.reason = reason; this.wu = wu; this.onlyIfPageGone = onlyIfPageGone; this.hop = hop; this.tries = 0;
  this.offline = false;
}""")

# ================= VSessions: the one-editable-view-per-vault logic =================
for f in ("public static final java.util.concurrent.ConcurrentHashMap SESSIONS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap EPOCHS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SWITCHED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BUSYSEEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static final int PAGE = 1;", "public static final int CHEST = 2;"):
    F(vs, f)
M(vs, r"""
public static void tell(@PR@ pr, String res) {
  if (pr == null || res == null || res.length() == 0) return;
  String col = "#cfe3ff";
  String txt = res;
  char c = res.charAt(0);
  if (c == '+') { col = "#8fe39a"; txt = res.substring(1); }
  else if (c == '-') { col = "#ff9d6b"; txt = res.substring(1); }
  else if (c == '=') { txt = res.substring(1); }
  try { pr.sendMessage(@MSG@.raw("[Vault] " + txt).color(col)); } catch (Throwable t) { }
}""")
M(vs, r"""
public static void tellAll(@PR@ pr, String[] lines) {
  if (lines == null) return;
  for (int i = 0; i < lines.length; i++) tell(pr, lines[i]);
}""")
# first sight of an epoch = baseline (contract section 4 rule 2); a later different value = a switch
M(vs, r"""
public static boolean noteEpoch(java.util.UUID u) {
  Object cur = @PKG@.VCfg.bridge().get("profile:epoch:" + u);
  if (cur == null) return false;
  Object prev = EPOCHS.put(u, cur);
  if (prev != null && !prev.equals(cur)) { SWITCHED.put(u, Long.valueOf(System.currentTimeMillis())); return true; }
  return false;
}""")
# profile:busy seen, then gone = a switch or a crash recovery at join finished: SkyyProfiles keeps its marker 30 s after both, so the
# settle window starts again (a recovery keeps the epoch, so noteEpoch alone would not see it)
M(vs, r"""
public static boolean noteBusy(java.util.UUID u) {
  if (@PKG@.VCfg.bridge().get("profile:busy:" + u) != null) { BUSYSEEN.put(u, Boolean.TRUE); return true; }
  if (BUSYSEEN.remove(u) != null) SWITCHED.put(u, Long.valueOf(System.currentTimeMillis()));
  return false;
}""")
# seconds the vault still stays shut after a switch / recovery (0 = open)
M(vs, r"""
public static long settleLeft(java.util.UUID u) {
  Object at = SWITCHED.get(u);
  if (!(at instanceof Long)) return 0L;
  long left = @PKG@.VCfg.AFTER_SWITCH_MS - (System.currentTimeMillis() - ((Long) at).longValue());
  if (left <= 0L) return 0L;
  return (left + 999L) / 1000L;
}""")
M(vs, r"""
public static String gate(java.util.UUID u) {
  if (noteBusy(u)) return "-Your profile is still loading - try /vault again in a moment.";
  noteEpoch(u);
  long left = settleLeft(u);
  if (left > 0L) return "-Your profile just changed - your vault opens in " + left + " s (your switch is still being saved).";
  return null;
}""")
M(vs, r"""
public static @PKG@.VSession current(java.util.UUID u) {
  Object o = SESSIONS.get(u);
  if (o == null) return null;
  @PKG@.VSession s = (@PKG@.VSession) o;
  if (s.closed) return null;
  return s;
}""")
M(vs, r"""
public static boolean registered(@PLA@ p, @PKG@.VSession s) {
  try {
    if (p == null || s == null || s.window == null) return false;
    int id = s.window.getId();
    if (id <= 0) return false;
    return p.getWindowManager().getWindow(id) == s.window;
  } catch (Throwable t) { return false; }
}""")
# the view -> the page array (explicit; the change listener calls it too); schedules the save when anything changed
M(vs, r"""
public static boolean syncView(@PKG@.VSession s) {
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d == null || s.view == null) return false;
  int cap = s.view.getCapacity();
  @IS@[] now = new @IS@[cap];
  for (int i = 0; i < cap; i++) {
    @IS@ x = s.view.getItemStack((short) i);
    if (x != null && !x.isEmpty()) now[i] = x;
  }
  boolean ch = d.copyIn(s.page, now);
  if (ch) @PKG@.VStore.saveSoon(s.owner, @PKG@.VCfg.SAVE_DELAY_MS);
  return ch;
}""")
M(vs, r"""
public static void onChange(@PKG@.VSession s) {
  if (s == null || s.closed || s.swapping) return;
  syncView(s);
}""")
# world thread: last sync (unless the view is known bad), then the view is made inert: listener off, DENY_ALL, emptied
M(vs, r"""
public static void finalizeWorld(@PKG@.VSession s) {
  if (s == null || !s.close1()) return;
  if (!s.noSync) { try { syncView(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault final sync failed for " + s.owner + ": " + t); } }
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  try { s.view.setGlobalFilter(@FT@.DENY_ALL); } catch (Throwable t) { }
  try { s.view.clear(); } catch (Throwable t) { }
  SESSIONS.remove(s.owner, s);
  LAST.put(s.owner, Integer.valueOf(s.page));
  @PKG@.VStore.saveSoon(s.owner, 0L);
}""")
# retire a view WITHOUT closing its window (any thread: viewer gone, plugin shutdown, or a view that is on screen and about to be
# replaced by a new page): DENY_ALL FIRST (no client move can land after the last sync), then sync, then marked closed. The view is not
# emptied (the client may still show it until the new page replaces it); its window is closed by the client, by validate() on the next
# movement (closed session = false) or by the engine on a world change.
M(vs, r"""
public static void retire(@PKG@.VSession s) {
  if (s == null) return;
  try { s.view.setGlobalFilter(@FT@.DENY_ALL); } catch (Throwable t) { }
  if (!s.close1()) return;
  if (!s.noSync) { try { syncView(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault final sync failed for " + s.owner + ": " + t); } }
  try { if (s.reg != null) s.reg.unregister(); } catch (Throwable t) { }
  SESSIONS.remove(s.owner, s);
  LAST.put(s.owner, Integer.valueOf(s.page));
  @PKG@.VStore.saveSoon(s.owner, 0L);
}""")
M(vs, r"""
public static void closeRegistered(@PLA@ p, @REF@ ref, @ST@ st, @PKG@.VSession s) {
  try { p.getWindowManager().closeWindow(ref, s.window.getId(), st); } catch (Throwable t) { @PKG@.VCfg.warn("vault window close failed for " + s.owner + ": " + t); }
  finalizeWorld(s);
}""")
M(vs, r"""
public static void closeAny(@PLA@ p, @REF@ ref, @ST@ st, @PKG@.VSession s) {
  if (s == null || s.closed) return;
  if (registered(p, s)) closeRegistered(p, ref, st, s);
  else finalizeWorld(s);
}""")
# clear + fill the view from a page and read every slot back; false = the view does not match (caller must not sync it)
M(vs, r"""
public static boolean fill(@PKG@.VSession s, @IS@[] src) {
  s.view.clear();
  int cap = s.view.getCapacity();
  for (int i = 0; i < cap && i < src.length; i++) {
    if (src[i] != null) s.view.setItemStackForSlot((short) i, src[i], false);
  }
  for (int i = 0; i < cap; i++) {
    @IS@ v = s.view.getItemStack((short) i);
    @IS@ w = null;
    if (i < src.length) w = src[i];
    boolean ve = v == null || v.isEmpty();
    boolean we = w == null || w.isEmpty();
    if (ve != we) return false;
    if (!ve && (!v.getItemId().equals(w.getItemId()) || v.getQuantity() != w.getQuantity())) return false;
  }
  return true;
}""")
M(vs, r"""
public static @PKG@.VSession newSession(@PR@ pr, java.util.UUID u, @PKG@.VData d, int page, int mode) {
  @PKG@.VSession s = new @PKG@.VSession();
  s.owner = u; s.viewer = u; s.pr = pr; s.page = page; s.mode = mode;
  s.view = new @SIC@((short) d.cap);
  s.epoch = @PKG@.VCfg.bridge().get("profile:epoch:" + u);
  s.swapping = true;
  boolean ok = false;
  try { ok = fill(s, d.pageCopy(page)); } catch (Throwable t) { @PKG@.VCfg.warn("vault view fill failed for " + u + ": " + t); ok = false; }
  s.swapping = false;
  if (!ok) return null;
  s.window = new @PKG@.VWindow(s.view, s);
  s.reg = s.view.registerChangeEvent(new @PKG@.VChange(s));
  return s;
}""")
# show another page in the SAME view: old page synced first; a view that does not read back exactly closes without syncing
M(vs, r"""
public static String swap(@PKG@.VSession s, int page) {
  if (s == null || s.closed) return "-Your vault is not open.";
  if (page == s.page) return null;
  @PKG@.VData d = (@PKG@.VData) @PKG@.VStore.CACHE.get(s.owner);
  if (d == null) return "-Your vault is not loaded.";
  if (page < 1 || page > d.unlocked) return "-Vault page " + page + " is locked.";
  s.swapping = true;
  try { syncView(s); }
  catch (Throwable t) { s.swapping = false; @PKG@.VCfg.warn("vault sync before swap failed for " + s.owner + ": " + t); return "-Could not switch pages right now - try again."; }
  String r = null;
  try {
    if (fill(s, d.pageCopy(page))) s.page = page;
    else { s.noSync = true; r = "-Could not show page " + page + " - your vault closed to keep your items safe (nothing was lost)."; }
  } catch (Throwable t) {
    s.noSync = true;
    r = "-Could not show page " + page + " - your vault closed to keep your items safe (nothing was lost).";
    @PKG@.VCfg.warn("vault swap failed for " + s.owner + ": " + t);
  }
  s.swapping = false;
  if (r == null) LAST.put(s.owner, Integer.valueOf(page));
  return r;
}""")
M(vs, r"""
public static boolean visible(@PLA@ p, @PKG@.VSession s) {
  try {
    Object cp = p.getPageManager().getCustomPage();
    if (s.mode == 1) return cp != null && cp == s.pageObj;
    return cp == null;
  } catch (Throwable t) { return false; }
}""")
M(vs, r"""
public static void refreshPage(@PLA@ p, @PKG@.VSession s) {
  try {
    Object cp = p.getPageManager().getCustomPage();
    if (cp != null && cp == s.pageObj && cp instanceof @PKG@.VaultPage) ((@PKG@.VaultPage) cp).refresh();
  } catch (Throwable t) { }
}""")
# make room for a new view: a window that is part of the page on screen is RETIRED (the new page replaces it - never close a page right
# before opening another), a window that is not on screen is closed now, a session without a window is finalized
M(vs, r"""
public static void release(@PLA@ p, @REF@ ref, @ST@ st, @PKG@.VSession s) {
  if (s == null || s.closed) return;
  if (!registered(p, s)) { finalizeWorld(s); return; }
  if (visible(p, s)) { retire(s); return; }
  closeRegistered(p, ref, st, s);
}""")
# open (or re-show) the vault. Returns null (page opened, nothing to say) or a "+/-/=" line for chat.
M(vs, r"""
public static String open(@PR@ pr, @REF@ ref, @ST@ st, int page, int mode) {
  java.util.UUID u = pr.getUuid();
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  String g = gate(u);
  if (g != null) return g;
  @PKG@.VData d = @PKG@.VStore.load(u);
  if (d == null) return "-Your vault file cannot be read right now. Nothing was changed - please tell an admin.";
  @PKG@.VStore.noteName(d, pr.getUsername());
  if (page < 1) page = 1;
  if (page > d.unlocked) {
    if (d.unlocked < @PKG@.VCfg.MAX_PAGES) return "-Vault page " + page + " is locked - you own " + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + " pages. Page " + (d.unlocked + 1) + " costs " + @PKG@.VStore.grp(@PKG@.VStore.price(d.unlocked + 1)) + " coins - /vault buy";
    return "-You own " + d.unlocked + " vault pages - there is no page " + page + ".";
  }
  @PKG@.VSession ex = current(u);
  if (ex != null) {
    boolean reg = registered(p, ex);
    if (reg && ex.mode == mode && visible(p, ex)) {
      String r = swap(ex, page);
      if (r != null) { closeAny(p, ref, st, ex); return r; }
      if (mode == 1) refreshPage(p, ex);
      return "=Showing vault page " + page + " of " + d.unlocked + ".";
    }
    release(p, ref, st, ex);
  }
  @PKG@.VSession s = newSession(pr, u, d, page, mode);
  if (s == null) return "-Could not show vault page " + page + " - nothing was changed.";
  SESSIONS.put(u, s);
  LAST.put(u, Integer.valueOf(page));
  boolean ok = false;
  try {
    if (mode == 1) {
      @PKG@.VaultPage vp = new @PKG@.VaultPage(pr, s, page);
      s.pageObj = vp;
      ok = p.getPageManager().openCustomPageWithWindows(ref, st, vp, new @WIN@[] { s.window });
    } else {
      ok = p.getPageManager().setPageWithWindows(ref, st, @PGE@.Bench, true, new @WIN@[] { s.window });
    }
  } catch (Throwable t) { @PKG@.VCfg.warn("vault open failed for " + u + ": " + t); ok = false; }
  if (!ok) {
    closeAny(p, ref, st, s);
    return "-The vault window could not open - nothing was changed.";
  }
  if (mode == 2) return "=Vault page " + page + " of " + d.unlocked + " (shared by all your profiles): drag items in and out, Esc saves. /vault next or /vault <page> switches pages.";
  return null;
}""")
M(vs, r"""
public static String openDefault(@PR@ pr, @REF@ ref, @ST@ st, int page) {
  return open(pr, ref, st, page, @PKG@.VCfg.PAGE_MODE ? 1 : 2);
}""")
M(vs, r"""
public static int lastPage(java.util.UUID u) {
  Object l = LAST.get(u);
  if (l instanceof Integer) return ((Integer) l).intValue();
  return 1;
}""")
# /vault pages: page mode = the normal page; chest mode = the page with the buttons and no slots (its Open button opens a chest)
M(vs, r"""
public static String openNav(@PR@ pr, @REF@ ref, @ST@ st) {
  java.util.UUID u = pr.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  if (d == null) return "-Your vault file cannot be read right now. Nothing was changed - please tell an admin.";
  int pg = lastPage(u);
  if (pg < 1 || pg > d.unlocked) pg = 1;
  if (@PKG@.VCfg.PAGE_MODE) return open(pr, ref, st, pg, 1);
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  @PKG@.VSession s = current(u);
  if (s != null) { pg = s.page; release(p, ref, st, s); }
  p.getPageManager().openCustomPage(ref, st, new @PKG@.VaultPage(pr, (@PKG@.VSession) null, pg));
  return null;
}""")
M(vs, r"""
public static String step(@PR@ pr, @REF@ ref, @ST@ st, int delta) {
  java.util.UUID u = pr.getUuid();
  @PKG@.VData d = @PKG@.VStore.load(u);
  if (d == null) return "-Your vault file cannot be read right now. Nothing was changed - please tell an admin.";
  @PKG@.VSession s = current(u);
  int base = s != null ? s.page : lastPage(u);
  int t = base + delta;
  if (t < 1) return "-You are on the first vault page.";
  if (t > d.unlocked) {
    if (t <= @PKG@.VCfg.MAX_PAGES) return "-Vault page " + t + " is locked - /vault buy unlocks it for " + @PKG@.VStore.grp(@PKG@.VStore.price(t)) + " coins.";
    return "-That is your last vault page.";
  }
  int mode = s != null ? s.mode : (@PKG@.VCfg.PAGE_MODE ? 1 : 2);
  return open(pr, ref, st, t, mode);
}""")
# a page click on a live page-mode session; a failed swap closes the session (without syncing a bad view)
M(vs, r"""
public static String pageSwap(@PKG@.VaultPage vp, @REF@ ref, @ST@ st, int t) {
  @PKG@.VSession s = vp.sess;
  if (s == null || s.closed) return "-Your vault slots closed - click a page to open them again.";
  String g = gate(s.owner);
  if (g != null) return g;
  String r = swap(s, t);
  if (r != null) {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) closeAny(p, ref, st, s); else finalizeWorld(s);
  }
  return r;
}""")
# after /vault buy (armed or bought): the player's own vault page on screen (with or without slots) shows the new state + the result
M(vs, r"""
public static void afterBuy(@PR@ pr, @REF@ ref, @ST@ st, String res) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    Object cp = p.getPageManager().getCustomPage();
    if (cp instanceof @PKG@.VaultPage) ((@PKG@.VaultPage) cp).refreshWith(res);
  } catch (Throwable t) { }
}""")
M(vs, r"""
public static void windowClosed(@PKG@.VSession s) {
  finalizeWorld(s);
}""")
# ValidatedWindow.validate (engine calls it on player movement): false closes the window
M(vs, r"""
public static boolean stillValid(@PKG@.VSession s, @REF@ ref, @CA@ a) {
  if (s == null || s.closed) return false;
  try { if (@PKG@.VCfg.bridge().get("profile:busy:" + s.owner) != null) return false; } catch (Throwable t) { }
  try {
    @PLA@ p = (@PLA@) a.getComponent(ref, @PLA@.getComponentType());
    if (p != null) {
      Object cp = p.getPageManager().getCustomPage();
      if (s.mode == 1 && cp != s.pageObj) return false;
      if (s.mode == 2 && cp != null) return false;
    }
  } catch (Throwable t) { }
  return true;
}""")
M(vs, r"""
public static void dispatchClose(@PKG@.VSession s, String why, boolean onlyIfPageGone) {
  try {
    java.util.UUID wu = s.pr.getWorldUuid();
    @WLD@ w = null;
    if (wu != null) w = @UNI@.get().getWorld(wu);
    if (w == null) return;
    w.execute(new @PKG@.VCloseTask(s, why, wu, onlyIfPageGone, false));
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("close-" + s.owner, "could not schedule the vault close for " + s.owner + ": " + t); }
}""")
# a session whose viewer has been gone 10 s: retire the view (its window died with the entity; the view is only synced + made inert)
M(vs, r"""
public static void offlineFinalize(@PKG@.VSession s) {
  if (s == null || s.closed) return;
  retire(s);
  @PKG@.VStore.log("FINALIZE-OFFLINE " + s.owner + " page " + s.page);
}""")
# ... on the world thread the view was shown in (serialized with a late engine close there). No such world any more, or it refuses the
# task = nothing can still reach the view: retire it here. tickOne retires it itself if the task has not run 10 s later.
M(vs, r"""
public static void dispatchOffline(@PKG@.VSession s) {
  @WLD@ w = null;
  java.util.UUID wu = null;
  try {
    wu = s.pr.getWorldUuid();
    if (wu != null) w = @UNI@.get().getWorld(wu);
  } catch (Throwable t) { w = null; }
  if (w != null) {
    try {
      @PKG@.VCloseTask ct = new @PKG@.VCloseTask(s, (String) null, wu, false, false);
      ct.offline = true;
      w.execute(ct);
      return;
    } catch (Throwable t) { @PKG@.VCfg.warnOnce("offline-" + s.owner, "world " + wu + " refused the vault finalize for " + s.owner + " (finalized here): " + t); }
  }
  offlineFinalize(s);
}""")
# world thread (or a scheduler hop first): close the session's window and our page; tell the player why
M(vs, r"""
public static void closeTask(@PKG@.VCloseTask t) {
  @PKG@.VSession s = t.sess;
  if (s == null || s.closed) return;
  if (t.offline) { offlineFinalize(s); return; }
  if (t.hop) { dispatchClose(s, t.reason, t.onlyIfPageGone); return; }
  @PR@ pr = s.pr;
  java.util.UUID wu = pr.getWorldUuid();
  if (wu == null || !wu.equals(t.wu)) {
    if (t.tries < 3) { t.tries = t.tries + 1; dispatchClose(s, t.reason, t.onlyIfPageGone); }
    return;
  }
  @REF@ ref = pr.getReference();
  if (ref == null) return;
  @ST@ st = ref.getStore();
  if (st == null) return;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  Object cp = p.getPageManager().getCustomPage();
  boolean ours = s.pageObj != null && cp == s.pageObj;
  if (t.onlyIfPageGone && ours) return;
  closeAny(p, ref, st, s);
  if (ours) { try { p.getPageManager().setPage(ref, st, @PGE@.None); } catch (Throwable e) { } }
  if (t.reason != null) tell(pr, t.reason);
}""")
# our page was dismissed (Esc / replaced): if the client did not close the slots with it, close them 1.5 s later
M(vs, r"""
public static void dismissed(@PKG@.VSession s) {
  if (s == null || s.closed) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.VCloseTask(s, (String) null, (java.util.UUID) null, true, true), 1500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { dispatchClose(s, (String) null, true); }
}""")
M(vs, r"""
public static void tickOne(@UNI@ un, @PKG@.VSession s, long now) {
  if (s.closed) { SESSIONS.remove(s.owner, s); return; }
  @PR@ pr = un.getPlayer(s.viewer);
  if (pr == null || !pr.isValid()) {
    s.offline = s.offline + 1;
    if (s.offline == 10) dispatchOffline(s);
    else if (s.offline >= 20) offlineFinalize(s);
    return;
  }
  s.offline = 0;
  java.util.Map b = @PKG@.VCfg.bridge();
  String why = null;
  if (b.get("profile:busy:" + s.owner) != null) why = "=Your vault closed while your profile loads. Your items are safe.";
  else {
    Object ep = b.get("profile:epoch:" + s.owner);
    if (ep != null && s.epoch == null) s.epoch = ep;
    else if (ep != null && !ep.equals(s.epoch)) why = "=Your vault closed because your profile changed. Your items are safe - /vault opens it again in " + (@PKG@.VCfg.AFTER_SWITCH_MS / 1000L) + " s.";
  }
  if (why != null && now - s.askedClose > 5000L) { s.askedClose = now; dispatchClose(s, why, false); }
}""")
M(vs, r"""
public static void tick() {
  @UNI@ un = null;
  try { un = @UNI@.get(); } catch (Throwable t) { un = null; }
  if (un == null) return;
  long now = System.currentTimeMillis();
  try {
    java.util.Iterator it = un.getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.isValid()) { noteBusy(p.getUuid()); noteEpoch(p.getUuid()); }
    }
  } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick-players", "vault tick (players) failed: " + t); }
  try {
    java.util.Iterator w = SWITCHED.entrySet().iterator();
    while (w.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) w.next();
      if (now - ((Long) e.getValue()).longValue() > 130000L) w.remove();
    }
  } catch (Throwable t) { }
  try { @PKG@.VStore.pruneConfirms(now); } catch (Throwable t) { }
  java.util.Iterator si = SESSIONS.values().iterator();
  while (si.hasNext()) {
    @PKG@.VSession s = (@PKG@.VSession) si.next();
    try { tickOne(un, s, now); } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick-" + s.owner, "vault tick failed for " + s.owner + ": " + t); }
  }
}""")
# /vaultadmin open: a READ-ONLY COPY of one page (DENY_ALL, vanilla /invsee pattern); never a session, never saved
M(vs, r"""
public static String adminView(@PR@ admin, @REF@ ref, @ST@ st, String who, int page) {
  java.util.UUID tu = @PKG@.VStore.resolve(who);
  if (tu == null) return "-No player or vault found for " + who + " - use an online name, a name seen before or a UUID.";
  @PKG@.VData d = @PKG@.VStore.load(tu);
  if (d == null) return "-That vault file cannot be read (it was not touched) - see the server log.";
  if (page < 1 || page > d.unlocked) return "-" + @PKG@.VStore.nameOf(d) + " owns vault pages 1 to " + d.unlocked + ".";
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return "-You are not in a world right now.";
  @PKG@.VSession own = current(admin.getUuid());
  if (own != null) release(p, ref, st, own);
  @IS@[] src = d.pageCopy(page);
  @SIC@ c = new @SIC@((short) d.cap);
  for (int i = 0; i < src.length && i < d.cap; i++) {
    if (src[i] != null) c.setItemStackForSlot((short) i, src[i], false);
  }
  c.setGlobalFilter(@FT@.DENY_ALL);
  boolean ok = false;
  try { ok = p.getPageManager().setPageWithWindows(ref, st, @PGE@.Bench, true, new @WIN@[] { new @CW@(c) }); } catch (Throwable t) { ok = false; }
  if (!ok) return "-The read-only window could not open.";
  @PKG@.VStore.log("ADMIN-VIEW " + admin.getUsername() + " viewed " + tu + " (" + @PKG@.VStore.nameOf(d) + ") page " + page);
  @PKG@.VSession live = current(tu);
  return "=READ-ONLY view of " + @PKG@.VStore.nameOf(d) + "'s vault page " + page + " of " + d.unlocked + " (" + d.used(page) + " of " + d.cap + " slots used)" + (live != null ? " - they have their vault open on page " + live.page + " right now, this is a snapshot." : ".");
}""")
M(vs, r"""
public static void shutdownSync() {
  java.util.Iterator it = SESSIONS.values().iterator();
  while (it.hasNext()) {
    @PKG@.VSession s = (@PKG@.VSession) it.next();
    try { retire(s); } catch (Throwable t) { @PKG@.VCfg.warn("vault shutdown sync failed for " + s.owner + ": " + t); }
  }
}""")

# ================= bodies that call VSessions =================
M(clt, r"""
public void run() {
  try { @PKG@.VSessions.closeTask(this); } catch (Throwable t) { @PKG@.VCfg.warn("vault close task failed: " + t); }
}""")
M(chg, r"""
public void accept(Object ev) {
  try { @PKG@.VSessions.onChange(this.sess); } catch (Throwable t) { @PKG@.VCfg.warnOnce("chg", "vault change sync failed: " + t); }
}""")
M(win, r"""
public void onClose0(@REF@ ref, @CA@ a) {
  try { super.onClose0(ref, a); } catch (Throwable t) { }
  try { @PKG@.VSessions.windowClosed(this.sess); } catch (Throwable t) { @PKG@.VCfg.warn("vault window close handling failed: " + t); }
}""")
M(win, r"""
public boolean validate(@REF@ ref, @CA@ a) {
  try { return @PKG@.VSessions.stillValid(this.sess, ref, a); } catch (Throwable t) { return true; }
}""")
tick.addInterface(pool.get("java.lang.Runnable"))
C(tick, "public VTick() { }")
M(tick, r"""
public void run() {
  try { @PKG@.VSessions.tick(); } catch (Throwable t) { @PKG@.VCfg.warnOnce("tick", "vault tick failed: " + t); }
}""")

# ================= VaultPage part 2: clicks + dismiss =================
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ store, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (a.equals("close")) { close(); return; }
    @PKG@.VData d = @PKG@.VStore.load(u);
    if (d == null) { this.info = "-Your vault file cannot be read - please tell an admin."; rebuild(); return; }
    boolean live = this.sess != null && !this.sess.closed;
    int max = d.unlocked > @PKG@.VCfg.MAX_PAGES ? d.unlocked : @PKG@.VCfg.MAX_PAGES;
    int tp = 0;
    if (a.equals("prev")) tp = this.sel - 1;
    else if (a.equals("next")) tp = this.sel + 1;
    else if (a.startsWith("num:")) { try { tp = Integer.parseInt(a.substring(4)); } catch (Throwable e) { tp = 0; } }
    String bkey = @PKG@.VStore.buyKey(u, d.unlocked + 1);
    if (a.equals("prev") || a.equals("next") || a.startsWith("num:")) {
      if (tp < 1 || tp > max) return;
      @PKG@.VStore.disarm(bkey);
      if (tp > d.unlocked) {
        this.sel = tp;
        if (tp == d.unlocked + 1) this.info = "=Page " + tp + " is locked. Click Buy to unlock it for " + @PKG@.VStore.grp(@PKG@.VStore.price(tp)) + " coins.";
        else this.info = "=Page " + tp + " is locked. Buy page " + (d.unlocked + 1) + " first.";
        rebuild();
        return;
      }
      if (live && this.sess.mode == 1) {
        String r = @PKG@.VSessions.pageSwap(this, ref, store, tp);
        this.sel = tp;
        this.info = r == null ? "+Showing page " + tp + "." : r;
        rebuild();
        return;
      }
      if (this.sess != null && @PKG@.VCfg.PAGE_MODE) {
        String r = @PKG@.VSessions.open(this.playerRef, ref, store, tp, 1);
        if (r != null) { this.sel = tp; this.info = r; rebuild(); }
        return;
      }
      this.sel = tp;
      this.info = "";
      rebuild();
      return;
    }
    if (a.equals("open")) {
      @PKG@.VStore.disarm(bkey);
      if (this.sel > d.unlocked) { this.info = "-Page " + this.sel + " is locked - buy it first."; rebuild(); return; }
      String r = @PKG@.VSessions.open(this.playerRef, ref, store, this.sel, 2);
      if (r != null && r.startsWith("=")) @PKG@.VSessions.tell(this.playerRef, r);
      else if (r != null) { this.info = r; rebuild(); }
      return;
    }
    if (a.equals("buy")) {
      int next = d.unlocked + 1;
      if (next > @PKG@.VCfg.MAX_PAGES) { this.info = "-You already own every vault page."; rebuild(); return; }
      if (!@PKG@.VStore.confirm(@PKG@.VStore.buyKey(u, next))) {
        this.info = "=Page " + next + " costs " + @PKG@.VStore.grp(@PKG@.VStore.price(next)) + " coins - click Sure? or type /vault buy within 10 s.";
        rebuild();
        return;
      }
      String r = @PKG@.VStore.buy(u, this.playerRef.getUsername());
      this.info = r;
      if (r.startsWith("+")) {
        this.sel = next;
        if (live && this.sess.mode == 1) {
          String r2 = @PKG@.VSessions.pageSwap(this, ref, store, next);
          if (r2 != null) this.info = r2;
        }
      }
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.VCfg.warn("vault page click failed: " + t); }
}""")
M(page, r"""
public void onDismiss(@REF@ ref, @ST@ store) {
  try { if (this.sess != null && !this.sess.closed && this.sess.mode == 1) @PKG@.VSessions.dismissed(this.sess); } catch (Throwable t) { }
}""")

# ================= commands =================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []
CMD_PERM = {}   # class name -> "@ADV@" | "@ADMIN@" (checked against ADMIN_CMDS and the compiled class files at the end)
# EVERY admin command class (root, subcommands, usage variants). A cmd(...) that is not listed here must be a player command (@ADV@)
# and every listed one must be built with perm=A - so an admin command that forgets perm= fails the build instead of opening to players.
ADMIN_CMDS = {"VAOpenPageCmd", "VAOpenCmd", "VAInfoCmd", "VASetPagesCmd", "VAReloadCmd", "VaultAdminCmd"}


def cmd(clsname, name, desc, args, body, perm="@ADV@", subs=(), variant=None):
    """One AbstractPlayerCommand. name=None -> usage variant (description-only constructor). args = [(field, argName, argDesc)] STRING,
    read into a0, a1, ...
    Permission self-check (tools/ci/lint.py cannot see these templated constructors): perm must be @ADV@ or @ADMIN@ and the generated
    constructor must contain the permission call."""
    if perm not in ("@ADV@", "@ADMIN@"):
        raise SystemExit("command %s: perm must be @ADV@ or @ADMIN@ (COMMAND RULES), got %r" % (clsname, perm))
    if clsname in CMD_PERM:
        raise SystemExit("command class %s defined twice" % clsname)
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    for (fld, _an, _ad) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = [('super("%s", "%s");' % (name, desc)) if name else ('super("%s");' % desc), perm]
    for (fld, an, ad) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.STRING);' % (fld, an, ad))
    if variant:
        lines.append("addUsageVariant(new @PKG@.%s());" % variant)
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    ctor = "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines))
    want = 'setPermissionGroups(new String[] { "hytale:Adventurer" });' if perm == "@ADV@" else 'requirePermission("skyyvault.admin");'
    if want not in jv(ctor):
        raise SystemExit("command %s: generated constructor lacks %s:\n%s" % (clsname, want, jv(ctor)))
    CMD_PERM[clsname] = perm
    C(c, ctor)
    reads = "".join('    String a%d = String.valueOf(ctx.get(this.%s)).trim();\n' % (i, a[0]) for i, a in enumerate(args))
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.VCfg.warn(\"" + clsname + " failed: \" + t);\n"
      "    @PKG@.VSessions.tell(pr, \"-Something went wrong - the server log has the details.\");\n  }\n}")
    CMDS.append(c)
    return c


VS = "@PKG@.VSessions."
PARSE = ("int n = 0; try { n = Integer.parseInt(a%d); } catch (Throwable e) { n = 0; } "
         "if (n < 1) { " + VS + "tell(pr, \"-%s\"); return; } ")
cmd("VaultPageCmd", None, "Open one vault page: /vault <page>", [("pageArg", "page", "Vault page number")],
    PARSE % (0, "Use /vault <page number> - for example /vault 2") + VS + "tell(pr, " + VS + "openDefault(pr, ref, store, n));")
cmd("VaultBuyCmd", "buy", "Buy the next vault page with coins (type it twice to confirm)", [],
    r"""@PKG@.VData d = @PKG@.VStore.load(pr.getUuid());
    if (d == null) { @PKG@.VSessions.tell(pr, "-Your vault file cannot be read - nothing was charged. Please tell an admin."); return; }
    int next = d.unlocked + 1;
    if (next > @PKG@.VCfg.MAX_PAGES) { @PKG@.VSessions.tell(pr, "-You already own every vault page (" + d.unlocked + " of " + @PKG@.VCfg.MAX_PAGES + ")."); return; }
    if (!@PKG@.VStore.confirm(@PKG@.VStore.buyKey(pr.getUuid(), next))) {
      String arm = "=Page " + next + " costs " + @PKG@.VStore.grp(@PKG@.VStore.price(next)) + " coins - type /vault buy again or click Sure? within 10 s.";
      @PKG@.VSessions.tell(pr, arm);
      @PKG@.VSessions.afterBuy(pr, ref, store, arm);
      return;
    }
    String res = @PKG@.VStore.buy(pr.getUuid(), pr.getUsername());
    @PKG@.VSessions.tell(pr, res);
    @PKG@.VSessions.afterBuy(pr, ref, store, res);""")
cmd("VaultInfoCmd", "info", "Your vault pages, slots used and the next page price", [],
    r"""@PKG@.VSession s = @PKG@.VSessions.current(pr.getUuid());
    @PKG@.VSessions.tellAll(pr, @PKG@.VStore.infoLines(pr.getUuid(), s == null ? 0 : s.page, false));""")
cmd("VaultPagesCmd", "pages", "Open the vault page with the page buttons", [], VS + "tell(pr, " + VS + "openNav(pr, ref, store));")
cmd("VaultNextCmd", "next", "Show the next vault page", [], VS + "tell(pr, " + VS + "step(pr, ref, store, 1));")
cmd("VaultPrevCmd", "prev", "Show the previous vault page", [], VS + "tell(pr, " + VS + "step(pr, ref, store, -1));")
cmd("VaultCmd", "vault", "Your vault - one chest shared by all your profiles (/vault 2 opens page 2)", [],
    VS + "tell(pr, " + VS + "openDefault(pr, ref, store, 1));", variant="VaultPageCmd",
    subs=("VaultBuyCmd", "VaultInfoCmd", "VaultPagesCmd", "VaultNextCmd", "VaultPrevCmd"))

# ---- admin (requirePermission on the root, on every subcommand and on the open variant)
A = "@ADMIN@"
cmd("VAOpenPageCmd", None, "Admin: read-only view of one vault page: /vaultadmin open <player> <page>",
    [("playerArg", "player", "Online name, known name or UUID"), ("pageArg", "page", "Vault page number")],
    PARSE % (1, "Use /vaultadmin open <player> <page number>") + VS + "tell(pr, " + VS + "adminView(pr, ref, store, a0, n));", perm=A)
cmd("VAOpenCmd", "open", "Admin: read-only view of a player's vault (page 1; /vaultadmin open <player> <page>)",
    [("playerArg", "player", "Online name, known name or UUID")], VS + "tell(pr, " + VS + "adminView(pr, ref, store, a0, 1));",
    perm=A, variant="VAOpenPageCmd")
cmd("VAInfoCmd", "info", "Admin: a player's vault pages and slots used", [("playerArg", "player", "Online name, known name or UUID")],
    r"""java.util.UUID tu = @PKG@.VStore.resolve(a0);
    if (tu == null) { @PKG@.VSessions.tell(pr, "-No player or vault found for " + a0 + "."); return; }
    @PKG@.VSession s = @PKG@.VSessions.current(tu);
    @PKG@.VSessions.tellAll(pr, @PKG@.VStore.infoLines(tu, s == null ? 0 : s.page, true));
    if (s != null) @PKG@.VSessions.tell(pr, "=Their vault is open right now on page " + s.page + ".");""", perm=A)
cmd("VASetPagesCmd", "setpages", "Admin: set how many vault pages a player owns (never below a page that holds items)",
    [("playerArg", "player", "Online name, known name or UUID"), ("pagesArg", "pages", "Number of pages")],
    PARSE % (1, "Use /vaultadmin setpages <player> <number of pages>") +
    r"""java.util.UUID tu = @PKG@.VStore.resolve(a0);
    if (tu == null) { @PKG@.VSessions.tell(pr, "-No player or vault found for " + a0 + "."); return; }
    @PKG@.VSession s = @PKG@.VSessions.current(tu);
    @PKG@.VSessions.tell(pr, @PKG@.VStore.setPages(pr.getUsername(), tu, n, s == null ? 0 : s.page));""", perm=A)
cmd("VAReloadCmd", "reload", "Admin: re-read config.properties", [],
    VS + "tell(pr, \"+config.properties re-read: \" + @PKG@.VCfg.load());", perm=A)
cmd("VaultAdminCmd", "vaultadmin", "Vault admin: open <player> [page] | info <player> | setpages <player> <n> | reload", [],
    VS + "tellAll(pr, new String[] { \"=/vaultadmin open <player> [page] - read-only view of a vault page\", "
    "\"=/vaultadmin info <player> - pages and slots used\", \"=/vaultadmin setpages <player> <pages> - set owned pages\", "
    "\"=/vaultadmin reload - re-read config.properties\" });",
    perm=A, subs=("VAOpenCmd", "VAInfoCmd", "VASetPagesCmd", "VAReloadCmd"))

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyVaultPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.VCfg.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyVault");
  @PKG@.VCfg.DIR = dir;
  @PKG@.VCfg.VDIR = dir.resolve("vaults");
  @PKG@.VCfg.FILE = dir.resolve("config.properties");
  @PKG@.VCfg.LOGF = dir.resolve("vault.log");
  @PKG@.VCfg.NAMESF = dir.resolve("names.properties");
  String cfg = @PKG@.VCfg.load();
  @PKG@.VStore.loadNames();
  @PKG@.VStore.STOPPING = false;
  @PKG@.VStore.SAVER = java.util.concurrent.Executors.newSingleThreadScheduledExecutor(new @PKG@.VThreads());
  getCommandRegistry().registerCommand(new @PKG@.VaultCmd());
  getCommandRegistry().registerCommand(new @PKG@.VaultAdminCmd());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.VTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyVault] @VERSION@ ready - /vault (shared by all profiles), /vaultadmin; " + cfg + "; data in " + dir);
}""")
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  @PKG@.VStore.STOPPING = true;
  try { @PKG@.VSessions.shutdownSync(); } catch (Throwable t) { }
  try { @PKG@.VStore.flushAll(); } catch (Throwable t) { }
  try {
    java.util.concurrent.ScheduledExecutorService ex = @PKG@.VStore.SAVER;
    if (ex != null) { ex.shutdown(); ex.awaitTermination(3L, java.util.concurrent.TimeUnit.SECONDS); }
  } catch (Throwable t) { }
  try { @PKG@.VStore.flushAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

# ---- command permission self-check, part 2 (part 1 is in cmd()): the admin set is exact, nothing else is a command, and the COMPILED
# constructors really reference the permission call + its argument
built_admin = set(k for k, v in CMD_PERM.items() if v == "@ADMIN@")
if built_admin != ADMIN_CMDS:
    raise SystemExit("ADMIN_CMDS mismatch - built with @ADMIN@: %s, listed: %s" % (sorted(built_admin), sorted(ADMIN_CMDS)))
for c in ALL + [pl]:
    if str(c.getSuperclass().getName()) == T["APC"]:
        raise SystemExit("%s is a command but was not built by cmd() (no permission self-check)" % c.getName())

for c in ALL + CMDS + [pl]:
    c.writeFile(OUT)
print("classes written:", len(ALL + CMDS) + 1)

for c in CMDS:
    short = str(c.getSimpleName())
    with open(os.path.join(OUT, *(PKG.split(".") + [short + ".class"])), "rb") as fh:
        raw = fh.read()
    need = (b"setPermissionGroups", b"hytale:Adventurer") if CMD_PERM[short] == "@ADV@" else (b"requirePermission", b"skyyvault.admin")
    if not all(n in raw for n in need):
        raise SystemExit("compiled command %s lacks %s" % (short, " + ".join(n.decode() for n in need)))
print("command permissions checked:", len(CMDS), "commands (%d player, %d admin)" % (len(CMDS) - len(built_admin), len(built_admin)))

jar = os.path.join(HERE, "SkyyVault-%s.jar" % VERSION)
man = B.manifest("SkyyVault", VERSION, "SkyWynn vault: /vault is one chest shared by all your profiles (Wynncraft bank style) - pages, buy more with coins (SkyyCoins bridge), lossless item storage. Per player. Zero dependencies.", PKG + ".SkyyVaultPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
