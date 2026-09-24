"""SkyyProfiles 0.1 - build script (javassist via jpype). SkyBlock-style profiles for SkyWynn = the class selector.
Run:   python build_skyyprofiles_0.1.py            -> SkyyProfiles/SkyyProfiles-0.1.jar
       python build_skyyprofiles_0.1.py --deploy   -> also copies to Mods/SkyyProfiles.jar and enables it in the HUD mod world
       (Skyy 2026-09-23: build WITHOUT --deploy; the whole mod set is deployed together once Skyy OKs.)

Skyy (2026-09-23): "start profiles, and make class selection part of creating the profile like Minecraft so you are locked into your class."
Contract implemented: tools/PROFILES-CONTRACT.md (v1). One profile = one class (chosen at creation, never changeable) + its own island,
coins, bank, bags, skills, collections, accessories (the other mods key their files by pkey) + its own VANILLA INVENTORY (this mod).

PROFILES: ids "1".."N" per player (config maxProfiles, default 4, 1-6). Each has a name, a class (locked at creation), created, lastPlayed.
  Names: SkyBlock-style fruit names (FRUITS below), picked at random among the unused ones; "Other name" rerolls. No typed names in 0.1:
  a TextField exists in vanilla .ui templates (NameRespawnPointPage) but inline TextField syntax is unproven on Skyy's client (a parse
  error disconnects the client on the join path) - fruit names are the safe choice (task rule).
  Storage key (contract): profile "1" = uuid.toString() (= every existing data file, no migration), profile N = uuid + "-p" + N.
CREATE PROFILE page (Minecraft create-world style): class cards from the SkyyClasses bridge (class:list = the ENABLED classes, "Name:Skill")
  merged with a built-in fallback roster (Archer, Warrior, Mage selectable; Assassin, Shaman "coming later"); pick one, "Create profile".
  First join with no profile: the page opens ~openDelayMillis (2 s) after the first PlayerReadyEvent of the session (SkyyHud/SkyyClasses
  OpenTask pattern: world-thread hop + WorldMap channel gate) and creates profile "1" (legacy key = everything the player already has).
  A class the player already had in SkyyClasses 0.1.x (bridge class:<uuid>, else class:fn:get) is pre-selected. "Later" / Esc closes it;
  it re-opens on every login until profile 1 exists (promptEveryLogin=true) - /profiles or /profiles create opens it any time.
PROFILES page (/profiles, alias /profile): a card per profile (class icon, name, class + combat skill, created, last played, ACTIVE),
  Switch -> Confirm/Cancel, "Create new" while slots are free. Positional forms: /profiles create (alias new), /profiles switch <n|name>,
  /profiles list. Everyone may use them (setPermissionGroups hytale:Adventurer on the root and every subcommand, HANDOFF COMMAND RULES).
SWITCH (world thread, one uninterrupted task, per-player BUSY guard):
  0. refuse while dead (DeathComponent), in combat (DamageDataComponent lastDamageTime / lastCombatAction within combatSeconds=10,
     measured with the world's TimeResource like DamageSystems$RecordLastCombat) or while a custom page other than ours is open.
  1. read + parse the TARGET profile's inventories/<toKey>.json first (a profile never switched away from = brand new = empty);
     a missing/unreadable file for a profile that should have one refuses the switch with nothing changed.
  2. capture EVERY vanilla inventory section - InventoryComponent Hotbar, Storage, Backpack, Armor, Utility, Tool (verified: these six
     components are all Inventory.getSectionById serves, InventoryUtils.clear clears InventoryComponent.EVERYTHING) - each slot's full
     ItemStack: id, quantity, durability, max durability, quality index, overrideDroppedItemAnimation, metadata BsonDocument, plus the
     engine's own ItemStack.CODEC encoding (restored first; the explicit fields are the fallback + human-readable). Written to
     inventories/<fromKey>.json as EXTENDED JSON (lossless BSON types) atomically (tmp + fsync + ATOMIC_MOVE) and read back + counted
     BEFORE anything is cleared.
  3. write the marker switching/<uuid>.properties (from, to, fromKey, toKey, toHadFile, stage=saved) - atomic + fsync.
  4. clear all sections (ItemContainer.clear / removeItemStackFromSlot, verified empty afterwards).
  5. load the target snapshot (backpack SIZE is per profile too when perProfileBackpack=true: vanilla Backpack.resize, as the vanilla
     /inventory backpack command; a new profile starts at newProfileBackpack=0 like a new vanilla player). Each stack goes back to its
     slot with setItemStackForSlot(slot, stack, false) (verified by reading the slot); anything that cannot -> addOrDropItemStack into
     storage-hotbar-backpack (storage first).
  6. players/<uuid>.properties: active=to, epoch+1, from.inv=1 (atomic). 7. delete the marker. 8. republish the bridge, close our page,
     dispatch the player's own "/island" (CommandManager.get().handleCommand(playerRef, "island") - SkyyIslands 0.4.4 sends them to the
     ACTIVE profile's island, created on first use); without SkyyIslands -> the default world spawn (SkyyIslands HubCmd fallback calls).
  Failure inside 4-6 -> immediate rollback (clear + reload the step-2 snapshot, marker removed). If even that fails the marker becomes
  stage=failed (never auto-applied; the snapshots stay on disk for an admin) and the player is told.
  keepItems (config, default Skyy_Menu = the SkyyMenu item): never saved, never cleared - it stays on every profile (SkyyMenu gives its
  item once per PLAYER, so a new profile would otherwise have no menu item).
CRASH SAFETY: a leftover marker at join (first PlayerReadyEvent of the session, files read off the world thread, applied on it):
  stage=saved + players file active == from -> ROLL BACK: clear, load inventories/<fromKey>.json (the snapshot the marker was written
  after). active == to -> ROLL FORWARD: clear, load the target snapshot (or empty for a new profile). Either way the live inventory becomes
  exactly the snapshot of the ACTIVE profile and the other profile's items stay in their file: no loss, no duplication.
  stage=done -> just deleted. stage=failed -> reported (log + player), left for an admin.
ADMIN (perm skyyprofiles.admin): /profileadmin info <player|uuid>, /profileadmin setclass <player|uuid> <n> <class> (fix mistakes; bumps
  the epoch when it is the active profile), /profileadmin reload (config + re-read player files).
BRIDGE (System.getProperties().get("skyy.bridge")), all per-player keys published on join and on every change, epoch LAST:
  profile:fn:key          Function apply(UUID) -> storage key of the ACTIVE profile (loads offline players from disk, cached)
  profile:key:<uuid>      same String            profile:<uuid>        active id "1", "2", ... (absent = no profile yet)
  profile:class:<uuid>    locked class of the active profile (absent = none)   profile:name:<uuid>  its name
  profile:epoch:<uuid>    Long, +1 on every creation and switch (and admin setclass of the active profile); 0 = no profile yet
  profile:list:<uuid>     extra (not in contract v1): "1:Apple:Archer,2:Banana:Mage"
SCHEMA (Skyy_SkyyProfiles/, everything keyed by player UUID; this mod owns the profile list):
  config.properties        maxProfiles, openDelayMillis, promptEveryLogin, combatSeconds, islandOnSwitch, perProfileBackpack,
                           newProfileBackpack, keepItems
  players/<uuid>.properties  username, active, epoch, switches, prompted, p.<id>.name, p.<id>.class, p.<id>.created,
                           p.<id>.lastPlayed (epoch millis), p.<id>.inv=1 (only while that profile is NOT active: its items are on disk)
  inventories/<key>.json   {format:1, mod, uuid, profile, key, savedAt, backpackCapacity, count, sections:[{name, capacity,
                           slots:[{slot, id, qty, durability, maxDurability, quality, overrideAnim, meta, stack}]}]}  (EXTENDED JSON)
  switching/<uuid>.properties  marker {from, to, fromKey, toKey, toHadFile, stage=saved|done|failed, at}
  switches.log             one line per CREATE / SWITCH / ROLLBACK / RECOVER (admin audit trail)
"""
import sys, os, re, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))

# =====================================================================================================================
# DATA (edit here, rebuild). UI text: no , : ; { } " ' _ \ (the inline UI parser is picky; the build asserts it).
# Fallback roster = SkyyClasses 0.1.3 (used when SkyyClasses is not loaded; class:list decides which are selectable when it is).
# =====================================================================================================================
CLASSES = [
    {"name": "Archer", "skill": "Archery", "color": "#8fd67a", "enabled": True,
     "desc": "Fights from range. Charge a shortbow or load a crossbow and strike before the enemy gets close.",
     "icons": ["Weapon_Shortbow_Iron", "Weapon_Crossbow_Iron", "Weapon_Arrow_Crude"], "weapon_text": "Shortbows / Crossbows"},
    {"name": "Warrior", "skill": "Swordsmanship", "color": "#e0b060", "enabled": True,
     "desc": "Front line blade fighter. Swords and longswords up close and spears for reach.",
     "icons": ["Weapon_Sword_Iron", "Weapon_Longsword_Iron", "Weapon_Spear_Iron"], "weapon_text": "Swords / Longswords / Spears"},
    {"name": "Mage", "skill": "Sorcery", "color": "#7fb0e0", "enabled": True,
     "desc": "Spellcaster. Staves strike up close and cast magic at range.",
     "icons": ["Weapon_Staff_Iron", "Weapon_Staff_Wizard", "Weapon_Staff_Crystal_Ice"], "weapon_text": "Staves"},
    {"name": "Assassin", "skill": "Assassination", "color": "#b58cff", "enabled": False,
     "desc": "Coming later. Fast and deadly with twin daggers and kunai throwing knives.",
     "icons": ["Weapon_Daggers_Iron", "Weapon_Kunai"], "weapon_text": "Daggers / Kunai"},
    {"name": "Shaman", "skill": "Shaman skill", "color": "#ff7a5c", "enabled": False,
     "desc": "Coming later. The fifth Wynncraft class - its weapons and skill are designed when that phase starts.",
     "icons": ["Weapon_Wand_Wood"], "weapon_text": "Designed later"},
]
FRUITS = ["Apple", "Banana", "Blueberry", "Coconut", "Cucumber", "Grapes", "Kiwi", "Lemon", "Lime", "Mango", "Orange",
          "Papaya", "Pear", "Pineapple", "Pomegranate", "Raspberry", "Strawberry", "Tomato", "Watermelon", "Zucchini"]
NEW_ICON = "Ingredient_Voidheart"      # "Create new" card + profiles without a class
EXTRA_ICON = "Weapon_Sword_Iron"       # a class published by SkyyClasses that this build does not know
DEF_MAX_PROFILES = 4
DEF_OPEN_DELAY_MS = 2000
DEF_COMBAT_S = 10
DEF_KEEP = "Skyy_Menu"
MAX_ID = 64                            # highest profile id ever scanned in a player file
PAGE_W, PAGE_H = 780, 600

BAD_UI = set(',:;{}"\'_\\')
for _c in CLASSES:
    for _k in ("name", "skill", "desc", "weapon_text"):
        _bad = BAD_UI & set(_c[_k])
        assert not _bad, "UI text %s.%s contains %r" % (_c["name"], _k, "".join(sorted(_bad)))
    assert re.match(r"^#[0-9a-fA-F]{6}$", _c["color"]), _c["color"]
    assert 1 <= len(_c["icons"]) <= 3, "1-3 icons per class"
for _f in FRUITS:
    assert re.match(r"^[A-Za-z]+$", _f), _f
assert len(set(FRUITS)) == len(FRUITS) >= 6
_ASSETS = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
_ITEMS = set(os.path.basename(n)[:-5] for n in _ASSETS.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
for _ic in [i for c in CLASSES for i in c["icons"]] + [NEW_ICON, EXTRA_ICON, DEF_KEEP]:
    assert _ic in _ITEMS or _ic == DEF_KEEP, "icon item %s not in Assets.zip" % _ic
print("roster fallback:", ", ".join("%s(%s)" % (c["name"], "on" if c["enabled"] else "later") for c in CLASSES), "| fruits:", len(FRUITS))

# =====================================================================================================================
# JVM + engine classes
# =====================================================================================================================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.profiles"
T = {
    "PKG": PKG,
    "JP":    "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":   "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":    "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":   "com.hypixel.hytale.component.Ref",
    "ST":    "com.hypixel.hytale.component.Store",
    "CA":    "com.hypixel.hytale.component.ComponentAccessor",
    "CT":    "com.hypixel.hytale.component.ComponentType",
    "UNI":   "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":   "com.hypixel.hytale.server.core.universe.world.World",
    "APC":   "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":   "com.hypixel.hytale.server.core.command.system.CommandContext",
    "CMGR":  "com.hypixel.hytale.server.core.command.system.CommandManager",
    "MSG":   "com.hypixel.hytale.server.core.Message",
    "HSV":   "com.hypixel.hytale.server.core.HytaleServer",
    "ATY":   "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":    "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG":   "com.hypixel.hytale.logger.HytaleLogger",
    "PLA":   "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE":  "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGE":   "com.hypixel.hytale.protocol.packets.interface_.Page",
    "LIFE":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":   "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":   "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":   "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":    "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PRE":   "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "PDE":   "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "INVC":  "com.hypixel.hytale.server.core.inventory.InventoryComponent",
    "HOT":   "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
    "STO":   "com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage",
    "BAK":   "com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack",
    "ARM":   "com.hypixel.hytale.server.core.inventory.InventoryComponent$Armor",
    "UTI":   "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility",
    "TOO":   "com.hypixel.hytale.server.core.inventory.InventoryComponent$Tool",
    "IC":    "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "SIC":   "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "IS":    "com.hypixel.hytale.server.core.inventory.ItemStack",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "TRF":   "com.hypixel.hytale.math.vector.Transform",
    "TP":    "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "DDC":   "com.hypixel.hytale.server.core.entity.damage.DamageDataComponent",
    "DEATH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "TR":    "com.hypixel.hytale.server.core.modules.time.TimeResource",
}
def jv(src):
    """Java source with @TOKEN@ placeholders (raw strings: no brace doubling, \\" stays a Java escape)."""
    out = src
    for k, v in T.items():
        out = out.replace("@" + k + "@", v)
    left = re.findall(r"@[A-Z]+@", out)
    assert not left, "unreplaced tokens: %s" % left
    return out
def jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }"

AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((T["PLA"], "getPageManager"), (T["PLA"], "getPlayerConnection"), (T["PLA"], "getInventory"), (T["PLA"], "getComponentType"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "getCustomPage"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "setPage"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (T["PAGE"], "rebuild"), (T["PAGE"], "onDismiss"), (T["PGE"], "None"), (T["HSV"], "SCHEDULED_EXECUTOR"),
             (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"), (T["UNI"], "getWorld"), (T["UNI"], "getDefaultWorld"),
             (T["PR"], "hasPermission"), (T["PR"], "getWorldUuid"), (T["PR"], "getReference"), (T["PR"], "getUsername"), (T["PR"], "isValid"),
             (T["MSG"], "color"), (T["MSG"], "raw"), (T["PRE"], "getPlayerRef"), (T["PDE"], "getPlayerRef"),
             (AC, "addSubCommand"), (AC, "addAliases"), (AC, "requirePermission"), (AC, "setPermissionGroups"), (AC, "withRequiredArg"),
             (T["CMGR"], "get"), (T["CMGR"], "resolveCommand"), (T["CMGR"], "handleCommand"),
             (T["INVC"], "getInventory"), (T["HOT"], "getComponentType"), (T["STO"], "getComponentType"), (T["BAK"], "getComponentType"),
             (T["BAK"], "resize"), (T["ARM"], "getComponentType"), (T["UTI"], "getComponentType"), (T["TOO"], "getComponentType"),
             (T["IC"], "getCapacity"), (T["IC"], "getItemStack"), (T["IC"], "setItemStackForSlot"), (T["IC"], "clear"),
             (T["IC"], "removeItemStackFromSlot"), (T["SIC"], "addOrDropItemStack"),
             ("com.hypixel.hytale.server.core.inventory.Inventory", "getCombinedStorageHotbarBackpack"),
             (T["IS"], "CODEC"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "getDurability"), (T["IS"], "getMaxDurability"),
             (T["IS"], "getQualityIndex"), (T["IS"], "getMetadata"), (T["IS"], "getOverrideDroppedItemAnimation"),
             (T["IS"], "setOverrideDroppedItemAnimation"), (T["IS"], "withQuantity"), (T["IS"], "isEmpty"),
             (T["CODEC"], "encode"), (T["CODEC"], "decode"),
             (T["TP"], "createForPlayer"), (T["TP"], "getComponentType"), (T["WLD"], "getWorldConfig"), (T["WLD"], "execute"),
             (T["DDC"], "getComponentType"), (T["DDC"], "getLastDamageTime"), (T["DDC"], "getLastCombatAction"),
             (T["DEATH"], "getComponentType"), (T["TR"], "getResourceType"), (T["TR"], "getNow"), (T["ST"], "getResource"),
             ("org.bson.BsonDocument", "parse"), ("org.bson.BsonDocument", "toJson"), ("org.bson.json.JsonWriterSettings", "builder"),
             ("org.bson.json.JsonMode", "EXTENDED"), ("org.bson.BsonValue", "asNumber"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

cfg  = pool.makeClass(PKG + ".ProfCfg")
ros  = pool.makeClass(PKG + ".ProfRoster")
nam  = pool.makeClass(PKG + ".ProfNames")
sto  = pool.makeClass(PKG + ".ProfStore")
kfn  = pool.makeClass(PKG + ".KeyFn")
inv  = pool.makeClass(PKG + ".ProfInv")
sw   = pool.makeClass(PKG + ".ProfSwitch")
page = pool.makeClass(PKG + ".ProfilePage", pool.get(T["PAGE"]))
opn  = pool.makeClass(PKG + ".OpenTask")
rec  = pool.makeClass(PKG + ".RecoverTask")
rtk  = pool.makeClass(PKG + ".ReadyTask")
svt  = pool.makeClass(PKG + ".SaveTask")
rdy  = pool.makeClass(PKG + ".ProfReady")
quit_ = pool.makeClass(PKG + ".ProfQuit")
pcre = pool.makeClass(PKG + ".ProfCreateCmd", pool.get(T["APC"]))
psw  = pool.makeClass(PKG + ".ProfSwitchCmd", pool.get(T["APC"]))
plst = pool.makeClass(PKG + ".ProfListCmd", pool.get(T["APC"]))
pcmd = pool.makeClass(PKG + ".ProfilesCmd", pool.get(T["APC"]))
ainf = pool.makeClass(PKG + ".AdmInfoCmd", pool.get(T["APC"]))
acls = pool.makeClass(PKG + ".AdmSetClassCmd", pool.get(T["APC"]))
arel = pool.makeClass(PKG + ".AdmReloadCmd", pool.get(T["APC"]))
adm  = pool.makeClass(PKG + ".ProfileAdminCmd", pool.get(T["APC"]))
pl   = pool.makeClass(PKG + ".SkyyProfilesPlugin", pool.get(T["JP"]))

def F(cls, src): cls.addField(CtField.make(jv(src), cls))
def M(cls, src): cls.addMethod(CtNewMethod.make(jv(src), cls))
def C(cls, src): cls.addConstructor(CtNewConstructor.make(jv(src), cls))

# ================= ProfCfg: logger, bridge, config, atomic file writes =================
CFG_LINES = [
    "# SkyyProfiles config - edit, then /profileadmin reload (or restart the server)",
    "# maxProfiles = profile slots per player (1-6). Each profile = its own class, island, coins, skills, bags and vanilla inventory.",
    "maxProfiles=%d" % DEF_MAX_PROFILES,
    "# openDelayMillis = how long after joining the Create Profile page opens for a player without a profile",
    "openDelayMillis=%d" % DEF_OPEN_DELAY_MS,
    "# promptEveryLogin = true: open the Create Profile page on every login until the first profile exists. false: only the very first join",
    "promptEveryLogin=true",
    "# combatSeconds = no profile switch within this many seconds after taking or dealing damage",
    "combatSeconds=%d" % DEF_COMBAT_S,
    "# islandOnSwitch = true: after a switch the player runs /island (the new profile's island; the world spawn if SkyyIslands is missing)",
    "islandOnSwitch=true",
    "# perProfileBackpack = true: the backpack SIZE (vanilla backpack upgrades) is saved per profile too",
    "perProfileBackpack=true",
    "# newProfileBackpack = backpack size of a brand-new profile (vanilla players start at 0; -1 = keep the current size)",
    "newProfileBackpack=0",
    "# keepItems = item ids that are NOT swapped: they stay in the inventory on every profile (comma list). Skyy_Menu = the SkyyMenu item",
    "keepItems=%s" % DEF_KEEP,
]
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static @LOG@ LOG;")
F(cfg, "public static final int MAX_ID = %d;" % MAX_ID)
F(cfg, "public static volatile int MAX_PROFILES = %d;" % DEF_MAX_PROFILES)
F(cfg, "public static volatile long OPEN_DELAY_MS = %dL;" % DEF_OPEN_DELAY_MS)
F(cfg, "public static volatile boolean PROMPT_EVERY_LOGIN = true;")
F(cfg, "public static volatile long COMBAT_MS = %dL;" % (DEF_COMBAT_S * 1000))
F(cfg, "public static volatile boolean ISLAND_ON_SWITCH = true;")
F(cfg, "public static volatile boolean PER_PROFILE_BACKPACK = true;")
F(cfg, "public static volatile int NEW_BACKPACK = 0;")
F(cfg, "public static volatile String KEEP = %s;" % jstr("," + DEF_KEEP + ","))
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
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyProfiles] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyProfiles] " + msg); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("yes") || v.equals("on") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("no") || v.equals("off") || v.equals("0")) return false;
  return d;
}""")
M(cfg, r"""
public static boolean keep(String id) {
  if (id == null || id.length() == 0) return false;
  return KEEP.indexOf("," + id + ",") >= 0;
}""")
# tmp file + fsync + atomic rename (falls back to a plain replace only where the file system cannot rename atomically)
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
  try {
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (java.nio.file.AtomicMoveNotSupportedException e) {
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  }
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
    long mp = lng(p, "maxProfiles", (long) MAX_PROFILES);
    if (mp < 1L) mp = 1L;
    if (mp > 6L) mp = 6L;
    long d = lng(p, "openDelayMillis", OPEN_DELAY_MS);
    if (d < 250L) d = 250L;
    if (d > 60000L) d = 60000L;
    long cs = lng(p, "combatSeconds", COMBAT_MS / 1000L);
    if (cs < 0L) cs = 0L;
    if (cs > 600L) cs = 600L;
    long nb = lng(p, "newProfileBackpack", (long) NEW_BACKPACK);
    if (nb < -1L) nb = -1L;
    if (nb > 256L) nb = 256L;
    String k = p.getProperty("keepItems", "");
    StringBuilder ks = new StringBuilder(",");
    String[] parts = k.split(",");
    for (int i = 0; i < parts.length; i++) {
      String s = parts[i].trim();
      if (s.length() > 0) ks.append(s).append(",");
    }
    MAX_PROFILES = (int) mp;
    OPEN_DELAY_MS = d;
    COMBAT_MS = cs * 1000L;
    NEW_BACKPACK = (int) nb;
    KEEP = ks.toString();
    PROMPT_EVERY_LOGIN = bool(p, "promptEveryLogin", PROMPT_EVERY_LOGIN);
    ISLAND_ON_SWITCH = bool(p, "islandOnSwitch", ISLAND_ON_SWITCH);
    PER_PROFILE_BACKPACK = bool(p, "perProfileBackpack", PER_PROFILE_BACKPACK);
    return "maxProfiles=" + MAX_PROFILES + " combatSeconds=" + (COMBAT_MS / 1000L) + " islandOnSwitch=" + ISLAND_ON_SWITCH
      + " perProfileBackpack=" + PER_PROFILE_BACKPACK + " newProfileBackpack=" + NEW_BACKPACK + " keepItems=" + KEEP
      + " promptEveryLogin=" + PROMPT_EVERY_LOGIN + " openDelayMillis=" + OPEN_DELAY_MS;
  } catch (Throwable t) { warn("could not load config: " + t); return "config load failed: " + t; }
}""")

# ================= ProfRoster: class cards = SkyyClasses bridge class:list merged with the fallback table =================
F(ros, "public static final String[] NAMES = %s;" % jarr([c["name"] for c in CLASSES]))
F(ros, "public static final String[] SKILLS = %s;" % jarr([c["skill"] for c in CLASSES]))
F(ros, "public static final String[] DESCS = %s;" % jarr([c["desc"] for c in CLASSES]))
F(ros, "public static final String[] COLORS = %s;" % jarr([c["color"] for c in CLASSES]))
F(ros, "public static final String[] WTEXT = %s;" % jarr([c["weapon_text"] for c in CLASSES]))
F(ros, "public static final String[] ICONS = %s;" % jarr([",".join(c["icons"]) for c in CLASSES]))
F(ros, "public static final boolean[] ENABLED = new boolean[] { %s };" % ", ".join("true" if c["enabled"] else "false" for c in CLASSES))
F(ros, "public static final String NEW_ICON = %s;" % jstr(NEW_ICON))
F(ros, "public static final String EXTRA_ICON = %s;" % jstr(EXTRA_ICON))
M(ros, r"""
public static int indexOf(String s) {
  if (s == null) return -1;
  s = s.trim();
  for (int i = 0; i < NAMES.length; i++) if (NAMES[i].equalsIgnoreCase(s)) return i;
  return -1;
}""")
# one entry = String[] { name, skill, desc, color, weapons text, icons (comma list), "1" selectable / "0" coming later }
M(ros, r"""
public static java.util.ArrayList roster() {
  java.util.ArrayList out = new java.util.ArrayList();
  String list = null;
  try { Object o = @PKG@.ProfCfg.bridge().get("class:list"); if (o instanceof String) list = ((String) o).trim(); } catch (Throwable t) { }
  boolean have = list != null && list.length() > 0;
  String[] parts = have ? list.split(",") : new String[0];
  for (int i = 0; i < NAMES.length; i++) {
    String skill = SKILLS[i];
    boolean on = ENABLED[i];
    if (have) {
      on = false;
      for (int k = 0; k < parts.length; k++) {
        String[] nv = parts[k].split(":");
        if (nv.length > 0 && nv[0].trim().equalsIgnoreCase(NAMES[i])) {
          on = true;
          if (nv.length > 1 && nv[1].trim().length() > 0) skill = nv[1].trim();
        }
      }
    }
    out.add(new String[] { NAMES[i], skill, DESCS[i], COLORS[i], WTEXT[i], ICONS[i], on ? "1" : "0" });
  }
  if (have) {
    for (int k = 0; k < parts.length; k++) {
      String[] nv = parts[k].split(":");
      String n = nv.length > 0 ? nv[0].trim() : "";
      if (n.length() == 0 || indexOf(n) >= 0) continue;
      String sk = nv.length > 1 ? nv[1].trim() : "";
      out.add(new String[] { n, sk, "A class from SkyyClasses.", "#c9d6e2", "See /class", EXTRA_ICON, "1" });
    }
  }
  return out;
}""")
M(ros, r"""
public static String[] entry(String name) {
  if (name == null) return null;
  String s = name.trim();
  if (s.length() == 0) return null;
  java.util.ArrayList r = roster();
  for (int i = 0; i < r.size(); i++) {
    String[] c = (String[]) r.get(i);
    if (c[0].equalsIgnoreCase(s) || (c[0] + "s").equalsIgnoreCase(s)) return c;
  }
  return null;
}""")
M(ros, r"""
public static String iconOf(String cls) {
  String[] c = entry(cls);
  if (c == null) return cls == null || cls.trim().length() == 0 ? NEW_ICON : EXTRA_ICON;
  String[] ic = c[5].split(",");
  return ic.length > 0 && ic[0].length() > 0 ? ic[0] : EXTRA_ICON;
}""")
M(ros, r"""
public static String skillOf(String cls) {
  String[] c = entry(cls);
  return c == null ? "" : c[1];
}""")
M(ros, r"""
public static String article(String name) {
  if (name == null || name.length() == 0) return "";
  char c = Character.toUpperCase(name.charAt(0));
  return ("AEIOU".indexOf(c) >= 0 ? "an " : "a ") + name;
}""")
M(ros, r"""
public static String choiceText() {
  java.util.ArrayList r = roster();
  java.util.ArrayList on = new java.util.ArrayList();
  for (int i = 0; i < r.size(); i++) { String[] c = (String[]) r.get(i); if ("1".equals(c[6])) on.add(c[0]); }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < on.size(); i++) {
    if (i > 0) sb.append(i == on.size() - 1 ? " or " : ", ");
    sb.append((String) on.get(i));
  }
  return sb.toString();
}""")

# ================= ProfNames: SkyBlock-style fruit names =================
F(nam, "public static final String[] FRUITS = %s;" % jarr(FRUITS))
M(nam, r"""
public static boolean used(java.util.Properties p, String n) {
  if (p == null || n == null) return false;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String v = p.getProperty("p." + i + ".name");
    if (v != null && v.equalsIgnoreCase(n)) return true;
  }
  return false;
}""")
M(nam, r"""
public static String pick(java.util.Properties p, String avoid) {
  java.util.ArrayList free = new java.util.ArrayList();
  for (int i = 0; i < FRUITS.length; i++) {
    if (!used(p, FRUITS[i]) && !FRUITS[i].equals(avoid)) free.add(FRUITS[i]);
  }
  if (free.isEmpty()) {
    for (int i = 0; i < FRUITS.length; i++) if (!used(p, FRUITS[i])) free.add(FRUITS[i]);
  }
  if (free.isEmpty()) return "Profile";
  return (String) free.get(java.util.concurrent.ThreadLocalRandom.current().nextInt(free.size()));
}""")

# ================= ProfStore: the profile list per player (copy-on-write, atomic files), keys, bridge =================
F(sto, "public static java.nio.file.Path DIR;")
F(sto, "public static java.nio.file.Path SWDIR;")
F(sto, "public static java.nio.file.Path INVDIR;")
F(sto, "public static java.nio.file.Path LOGF;")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap SESSION = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap BUSY = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap BROKEN = new java.util.concurrent.ConcurrentHashMap();")
M(sto, r"""
public static synchronized java.util.Properties load(java.util.UUID u) {
  java.util.Properties p = (java.util.Properties) DATA.get(u);
  if (p != null) return p;
  p = new java.util.Properties();
  try {
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
    BROKEN.remove(u);
  } catch (Throwable t) {
    BROKEN.put(u, Boolean.TRUE);
    @PKG@.ProfCfg.warn("could not read players/" + u + ".properties - profile changes for this player are blocked until it is fixed: " + t);
  }
  DATA.put(u, p);
  return p;
}""")
M(sto, r"""
public static boolean saveProps(java.util.UUID u, java.util.Properties q) {
  try {
    java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
    q.store(bos, "SkyyProfiles player - profile list (edit only while the player is offline)");
    @PKG@.ProfCfg.atomicWrite(DIR.resolve(u.toString() + ".properties"), bos.toByteArray());
    return true;
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not save players/" + u + ".properties: " + t); return false; }
}""")
M(sto, r"""
public static synchronized boolean commit(java.util.UUID u, java.util.Properties q) {
  if (BROKEN.containsKey(u)) return false;
  if (!saveProps(u, q)) return false;
  DATA.put(u, q);
  return true;
}""")
M(sto, r"""
public static long num(java.util.Properties p, String k) {
  try { String v = p.getProperty(k); return v == null ? 0L : Long.parseLong(v.trim()); } catch (Throwable t) { return 0L; }
}""")
M(sto, r"""
public static boolean exists(java.util.Properties p, String id) {
  if (p == null || id == null) return false;
  return p.getProperty("p." + id + ".name") != null || p.getProperty("p." + id + ".class") != null;
}""")
M(sto, r"""
public static int count(java.util.Properties p) {
  int n = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (exists(p, String.valueOf(i))) n++;
  return n;
}""")
M(sto, r"""
public static String nextId(java.util.Properties p) {
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (!exists(p, String.valueOf(i))) return String.valueOf(i);
  return null;
}""")
M(sto, r"""
public static String lowestId(java.util.Properties p) {
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) if (exists(p, String.valueOf(i))) return String.valueOf(i);
  return null;
}""")
M(sto, r"""
public static String keyFor(java.util.UUID u, String id) {
  if (id == null || id.equals("1")) return u.toString();
  return u.toString() + "-p" + id;
}""")
M(sto, r"""
public static String activeOf(java.util.Properties p) {
  if (p == null) return null;
  String a = p.getProperty("active");
  if (a == null) return null;
  a = a.trim();
  return exists(p, a) ? a : null;
}""")
M(sto, r"""
public static String activeId(java.util.UUID u) {
  return activeOf(load(u));
}""")
# profile:fn:key - hot path for every Skyy mod: no lock on a cache hit
M(sto, r"""
public static String keyOf(java.util.UUID u) {
  java.util.Properties p = (java.util.Properties) DATA.get(u);
  if (p == null) p = load(u);
  return keyFor(u, activeOf(p));
}""")
M(sto, r"""
public static synchronized boolean create(java.util.UUID u, String id, String name, String cls, boolean makeActive) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (exists(q, id)) return false;
  String now = String.valueOf(System.currentTimeMillis());
  q.setProperty("p." + id + ".name", name);
  q.setProperty("p." + id + ".class", cls == null ? "" : cls);
  q.setProperty("p." + id + ".created", now);
  q.setProperty("p." + id + ".lastPlayed", now);
  if (makeActive) q.setProperty("active", id);
  q.setProperty("epoch", String.valueOf(num(q, "epoch") + 1L));
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized boolean setActive(java.util.UUID u, String from, String to) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!exists(q, to)) return false;
  String now = String.valueOf(System.currentTimeMillis());
  q.setProperty("active", to);
  if (from != null && exists(q, from) && !from.equals(to)) {
    q.setProperty("p." + from + ".lastPlayed", now);
    q.setProperty("p." + from + ".inv", "1");
  }
  q.remove("p." + to + ".inv");
  q.setProperty("p." + to + ".lastPlayed", now);
  q.setProperty("epoch", String.valueOf(num(q, "epoch") + 1L));
  q.setProperty("switches", String.valueOf(num(q, "switches") + 1L));
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized boolean setClass(java.util.UUID u, String id, String cls) {
  java.util.Properties q = (java.util.Properties) load(u).clone();
  if (!exists(q, id)) return false;
  q.setProperty("p." + id + ".class", cls);
  if (id.equals(activeOf(q))) q.setProperty("epoch", String.valueOf(num(q, "epoch") + 1L));
  return commit(u, q);
}""")
M(sto, r"""
public static synchronized void touch(java.util.UUID u) {
  java.util.Properties p = load(u);
  String a = activeOf(p);
  if (a == null) return;
  java.util.Properties q = (java.util.Properties) p.clone();
  q.setProperty("p." + a + ".lastPlayed", String.valueOf(System.currentTimeMillis()));
  commit(u, q);
}""")
M(sto, r"""
public static synchronized void noteLogin(java.util.UUID u, String username) {
  java.util.Properties p = load(u);
  if (username == null || username.equals(p.getProperty("username"))) return;
  java.util.Properties q = (java.util.Properties) p.clone();
  q.setProperty("username", username);
  commit(u, q);
}""")
M(sto, r"""
public static synchronized void markPrompted(java.util.UUID u) {
  java.util.Properties p = load(u);
  if ("1".equals(p.getProperty("prompted"))) return;
  java.util.Properties q = (java.util.Properties) p.clone();
  q.setProperty("prompted", "1");
  commit(u, q);
}""")
M(sto, r"""
public static String listText(java.util.Properties p) {
  StringBuilder sb = new StringBuilder();
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!exists(p, id)) continue;
    if (sb.length() > 0) sb.append(",");
    sb.append(id).append(":").append(p.getProperty("p." + id + ".name", "")).append(":").append(p.getProperty("p." + id + ".class", ""));
  }
  return sb.toString();
}""")
# contract bridge keys; epoch goes LAST so a consumer that sees the new epoch also sees the new key/class/name
M(sto, r"""
public static void publish(java.util.UUID u) {
  java.util.Map b = @PKG@.ProfCfg.bridge();
  String us = u.toString();
  java.util.Properties p = load(u);
  String a = activeOf(p);
  b.put("profile:key:" + us, keyFor(u, a));
  if (a == null) {
    b.remove("profile:" + us);
    b.remove("profile:class:" + us);
    b.remove("profile:name:" + us);
    b.remove("profile:list:" + us);
  } else {
    b.put("profile:" + us, a);
    String c = p.getProperty("p." + a + ".class", "");
    if (c.length() > 0) b.put("profile:class:" + us, c); else b.remove("profile:class:" + us);
    String n = p.getProperty("p." + a + ".name", "");
    if (n.length() > 0) b.put("profile:name:" + us, n); else b.remove("profile:name:" + us);
    b.put("profile:list:" + us, listText(p));
  }
  b.put("profile:epoch:" + us, Long.valueOf(num(p, "epoch")));
}""")
M(sto, r"""
public static String resolveId(java.util.UUID u, String arg) {
  if (arg == null) return null;
  String s = arg.trim();
  java.util.Properties p = load(u);
  if (exists(p, s)) return s;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (exists(p, id) && s.equalsIgnoreCase(p.getProperty("p." + id + ".name", ""))) return id;
  }
  return null;
}""")
M(sto, r"""
public static java.util.UUID resolve(String s) {
  if (s == null) return null;
  s = s.trim();
  if (s.length() == 0) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.getUsername() != null && p.getUsername().equalsIgnoreCase(s)) return p.getUuid();
    }
  } catch (Throwable t) { }
  try { return java.util.UUID.fromString(s); } catch (Throwable t) { }
  java.util.UUID found = null;
  try {
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(DIR, "*.properties");
    try {
      java.util.Iterator it2 = ds.iterator();
      while (found == null && it2.hasNext()) {
        java.nio.file.Path f = (java.nio.file.Path) it2.next();
        java.util.Properties q = new java.util.Properties();
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { q.load(in); } finally { in.close(); }
        if (s.equalsIgnoreCase(q.getProperty("username", ""))) {
          String fn = f.getFileName().toString();
          found = java.util.UUID.fromString(fn.substring(0, fn.length() - 11));
        }
      }
    } finally { ds.close(); }
  } catch (Throwable t) { }
  return found;
}""")
M(sto, r"""
public static String fmtAgo(long t) {
  if (t <= 0L) return "never";
  long s = (System.currentTimeMillis() - t) / 1000L;
  if (s < 60L) return "just now";
  long m = s / 60L;
  if (m < 60L) return m + " min ago";
  long h = m / 60L;
  if (h < 48L) return h + " h ago";
  return (h / 24L) + " days ago";
}""")
M(sto, r"""
public static String fmtDate(long t) {
  if (t <= 0L) return "unknown";
  try { return new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date(t)); } catch (Throwable x) { return "unknown"; }
}""")
M(sto, r"""
public static String describe(java.util.UUID u) {
  java.util.Properties p = load(u);
  String act = activeOf(p);
  StringBuilder sb = new StringBuilder();
  int n = 0;
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!exists(p, id)) continue;
    if (n > 0) sb.append(" | ");
    n++;
    String c = p.getProperty("p." + id + ".class", "");
    sb.append(id).append(" ").append(p.getProperty("p." + id + ".name", "?")).append(" - ").append(c.length() == 0 ? "no class" : c);
    if (id.equals(act)) sb.append(" - ACTIVE");
    else sb.append(" - last played ").append(fmtAgo(num(p, "p." + id + ".lastPlayed")));
  }
  if (n == 0) return "no profiles yet";
  return sb.toString() + " | slots " + n + "/" + @PKG@.ProfCfg.MAX_PROFILES;
}""")
M(sto, r"""
public static void log(String line) {
  @PKG@.ProfCfg.appendLine(LOGF, java.time.Instant.now().toString() + " " + line);
}""")

# ================= KeyFn: bridge profile:fn:key =================
kfn.addInterface(pool.get("java.util.function.Function"))
C(kfn, "public KeyFn() { }")
M(kfn, r"""
public Object apply(Object o) {
  try { if (o instanceof java.util.UUID) return @PKG@.ProfStore.keyOf((java.util.UUID) o); } catch (Throwable t) { }
  return o == null ? null : String.valueOf(o);
}""")

# ================= ProfInv: vanilla inventory snapshot / clear / restore (WORLD THREAD ONLY) =================
F(inv, "public static final String[] SECTIONS = new String[] { \"hotbar\", \"storage\", \"backpack\", \"armor\", \"utility\", \"tools\" };")
M(inv, r"""
public static @CT@ typeOf(int i) {
  if (i == 0) return @HOT@.getComponentType();
  if (i == 1) return @STO@.getComponentType();
  if (i == 2) return @BAK@.getComponentType();
  if (i == 3) return @ARM@.getComponentType();
  if (i == 4) return @UTI@.getComponentType();
  if (i == 5) return @TOO@.getComponentType();
  return null;
}""")
M(inv, r"""
public static @IC@ section(@ST@ st, @REF@ ref, int i) {
  @CT@ t = typeOf(i);
  if (t == null) return null;
  @INVC@ c = (@INVC@) st.getComponent(ref, t);
  return c == null ? null : c.getInventory();
}""")
M(inv, r"""
public static int secIndex(String name) {
  if (name == null) return -1;
  for (int i = 0; i < SECTIONS.length; i++) if (SECTIONS[i].equals(name)) return i;
  return -1;
}""")
M(inv, r"""
public static int intOf(org.bson.BsonDocument d, String k, int def) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(inv, r"""
public static double dblOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isNumber()) return v.asNumber().doubleValue(); } catch (Throwable t) { }
  return 0.0;
}""")
M(inv, r"""
public static String strOf(org.bson.BsonDocument d, String k) {
  try { org.bson.BsonValue v = (org.bson.BsonValue) d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return null;
}""")
M(inv, r"""
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
  } catch (Throwable t) { @PKG@.ProfCfg.warn("ItemStack.CODEC could not encode " + s.getItemId() + " (explicit fields kept): " + t); }
  return d;
}""")
M(inv, r"""
public static org.bson.BsonDocument header(java.util.UUID u, String id, String key) {
  org.bson.BsonDocument doc = new org.bson.BsonDocument();
  doc.put("format", new org.bson.BsonInt32(1));
  doc.put("mod", new org.bson.BsonString("SkyyProfiles"));
  doc.put("uuid", new org.bson.BsonString(u.toString()));
  doc.put("profile", new org.bson.BsonString(id == null ? "1" : id));
  doc.put("key", new org.bson.BsonString(key));
  doc.put("savedAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  return doc;
}""")
M(inv, r"""
public static org.bson.BsonDocument capture(@ST@ st, @REF@ ref, java.util.UUID u, String id, String key) {
  org.bson.BsonDocument doc = header(u, id, key);
  org.bson.BsonArray secs = new org.bson.BsonArray();
  int total = 0;
  for (int i = 0; i < SECTIONS.length; i++) {
    @IC@ c = section(st, ref, i);
    int cap = 0;
    if (c != null) cap = c.getCapacity();
    org.bson.BsonDocument sd = new org.bson.BsonDocument();
    sd.put("name", new org.bson.BsonString(SECTIONS[i]));
    sd.put("capacity", new org.bson.BsonInt32(cap));
    org.bson.BsonArray slots = new org.bson.BsonArray();
    for (int k = 0; k < cap; k++) {
      @IS@ s = c.getItemStack((short) k);
      if (s == null || s.isEmpty()) continue;
      if (@PKG@.ProfCfg.keep(s.getItemId())) continue;
      slots.add(slotDoc(k, s));
      total++;
    }
    sd.put("slots", slots);
    secs.add(sd);
    if (i == 2 && c != null) doc.put("backpackCapacity", new org.bson.BsonInt32(cap));
  }
  doc.put("sections", secs);
  doc.put("count", new org.bson.BsonInt32(total));
  return doc;
}""")
M(inv, r"""
public static int slotCount(org.bson.BsonDocument doc) {
  int n = 0;
  if (doc == null) return -1;
  org.bson.BsonArray secs = doc.getArray("sections", new org.bson.BsonArray());
  for (int i = 0; i < secs.size(); i++) {
    org.bson.BsonValue v = (org.bson.BsonValue) secs.get(i);
    if (v == null || !v.isDocument()) continue;
    n = n + v.asDocument().getArray("slots", new org.bson.BsonArray()).size();
  }
  return n;
}""")
M(inv, r"""
public static java.nio.file.Path fileOf(String key) {
  return @PKG@.ProfStore.INVDIR.resolve(key + ".json");
}""")
M(inv, r"""
public static String toJson(org.bson.BsonDocument d) {
  org.bson.json.JsonWriterSettings s = org.bson.json.JsonWriterSettings.builder().outputMode(org.bson.json.JsonMode.EXTENDED).indent(true).build();
  return d.toJson(s);
}""")
M(inv, r"""
public static org.bson.BsonDocument read(String key) {
  java.nio.file.Path f = fileOf(key);
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    return org.bson.BsonDocument.parse(@PKG@.ProfCfg.readText(f));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not read inventory file " + f + ": " + t); return null; }
}""")
M(inv, r"""
public static boolean write(String key, org.bson.BsonDocument doc) {
  java.nio.file.Path f = fileOf(key);
  try {
    @PKG@.ProfCfg.atomicWrite(f, toJson(doc).getBytes("UTF-8"));
    org.bson.BsonDocument back = read(key);
    if (back == null || slotCount(back) != slotCount(doc)) { @PKG@.ProfCfg.warn("inventory file " + f + " did not read back correctly"); return false; }
    return true;
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not write inventory file " + f + ": " + t); return false; }
}""")
M(inv, r"""
public static org.bson.BsonDocument empty(java.util.UUID u, String id, String key) {
  org.bson.BsonDocument doc = header(u, id, key);
  doc.put("sections", new org.bson.BsonArray());
  doc.put("count", new org.bson.BsonInt32(0));
  doc.put("fresh", new org.bson.BsonBoolean(true));
  if (@PKG@.ProfCfg.NEW_BACKPACK >= 0) doc.put("backpackCapacity", new org.bson.BsonInt32(@PKG@.ProfCfg.NEW_BACKPACK));
  return doc;
}""")
# engine codec first (exact engine persistence semantics), explicit fields as the fallback
M(inv, r"""
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
  @IS@ s2 = new @IS@(id, qty, dblOf(d, "durability"), dblOf(d, "maxDurability"), intOf(d, "quality", 0), meta);
  try {
    org.bson.BsonValue a = (org.bson.BsonValue) d.get("overrideAnim");
    if (a != null && a.isBoolean() && a.asBoolean().getValue()) s2.setOverrideDroppedItemAnimation(true);
  } catch (Throwable t) { }
  return s2;
}""")
M(inv, r"""
public static boolean hasItem(@ST@ st, @REF@ ref, String id) {
  for (int i = 0; i < SECTIONS.length; i++) {
    @IC@ c = section(st, ref, i);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int k = 0; k < cap; k++) {
      @IS@ s = c.getItemStack((short) k);
      if (s != null && !s.isEmpty() && id.equals(s.getItemId())) return true;
    }
  }
  return false;
}""")
# empties every section except keepItems; true only when every other slot is verified empty
M(inv, r"""
public static boolean clearAll(@ST@ st, @REF@ ref) {
  boolean ok = true;
  for (int i = 0; i < SECTIONS.length; i++) {
    @IC@ c = section(st, ref, i);
    if (c == null) continue;
    int cap = c.getCapacity();
    boolean kept = false;
    for (int k = 0; k < cap; k++) {
      @IS@ s = c.getItemStack((short) k);
      if (s != null && !s.isEmpty() && @PKG@.ProfCfg.keep(s.getItemId())) kept = true;
    }
    if (!kept) {
      try { c.clear(); } catch (Throwable t) { @PKG@.ProfCfg.warn("clear of " + SECTIONS[i] + " failed, clearing slot by slot: " + t); }
    }
    for (int k = 0; k < cap; k++) {
      @IS@ s = c.getItemStack((short) k);
      if (s == null || s.isEmpty() || @PKG@.ProfCfg.keep(s.getItemId())) continue;
      try { c.removeItemStackFromSlot((short) k, false); } catch (Throwable t) { }
      @IS@ s2 = c.getItemStack((short) k);
      if (s2 != null && !s2.isEmpty()) { ok = false; @PKG@.ProfCfg.warn("could not empty " + SECTIONS[i] + " slot " + k + " (" + s2.getItemId() + ")"); }
    }
  }
  return ok;
}""")
M(inv, r"""
public static void give(@ST@ st, @REF@ ref, @PLA@ player, @IS@ s, java.util.UUID u) {
  try {
    @SIC@.addOrDropItemStack(st, ref, player.getInventory().getCombinedStorageHotbarBackpack(), s);
  } catch (Throwable t) {
    @PKG@.ProfCfg.warn("could not give " + s.getItemId() + " x" + s.getQuantity() + " to " + u + ": " + t);
    try { @PKG@.ProfStore.log("LOST? " + u + " " + toJson(slotDoc(-1, s)).replace('\n', ' ')); } catch (Throwable t2) { }
  }
}""")
# returns { placed, moved (not in its old slot -> storage first, dropped if full), skipped }
# rollbackMode: a slot that still holds the identical stack (it could not be cleared) counts as placed - never duplicated
M(inv, r"""
public static int[] loadInto(@ST@ st, @REF@ ref, @PLA@ player, org.bson.BsonDocument doc, java.util.UUID u, boolean rollbackMode) {
  int placed = 0;
  int moved = 0;
  int skipped = 0;
  if (@PKG@.ProfCfg.PER_PROFILE_BACKPACK && doc.containsKey("backpackCapacity")) {
    int want = intOf(doc, "backpackCapacity", -1);
    @BAK@ bp = (@BAK@) st.getComponent(ref, @BAK@.getComponentType());
    if (bp != null && want >= 0 && want <= 32000 && want != bp.getInventory().getCapacity()) {
      java.util.ArrayList over = new java.util.ArrayList();
      bp.resize((short) want, over);
      for (int k = 0; k < over.size(); k++) {
        @IS@ os = (@IS@) over.get(k);
        if (os != null && !os.isEmpty()) { give(st, ref, player, os, u); moved++; }
      }
    }
  }
  org.bson.BsonArray secs = doc.getArray("sections", new org.bson.BsonArray());
  for (int i = 0; i < secs.size(); i++) {
    org.bson.BsonValue sv = (org.bson.BsonValue) secs.get(i);
    if (sv == null || !sv.isDocument()) continue;
    org.bson.BsonDocument sd = sv.asDocument();
    int si = secIndex(strOf(sd, "name"));
    @IC@ c = si < 0 ? null : section(st, ref, si);
    org.bson.BsonArray slots = sd.getArray("slots", new org.bson.BsonArray());
    for (int k = 0; k < slots.size(); k++) {
      org.bson.BsonValue v = (org.bson.BsonValue) slots.get(k);
      if (v == null || !v.isDocument()) { skipped++; continue; }
      org.bson.BsonDocument d = v.asDocument();
      @IS@ s = stackOf(d);
      if (s == null) { skipped++; @PKG@.ProfCfg.warn("unreadable saved slot for " + u + ": " + d.toJson()); continue; }
      if (@PKG@.ProfCfg.keep(s.getItemId()) && hasItem(st, ref, s.getItemId())) { skipped++; continue; }
      int slot = intOf(d, "slot", -1);
      boolean done = false;
      if (c != null && slot >= 0 && slot < c.getCapacity()) {
        @IS@ cur = c.getItemStack((short) slot);
        if (cur == null || cur.isEmpty()) {
          try { c.setItemStackForSlot((short) slot, s, false); } catch (Throwable t) { }
          @IS@ chk = c.getItemStack((short) slot);
          if (chk != null && !chk.isEmpty() && s.getItemId().equals(chk.getItemId())) {
            int rest = s.getQuantity() - chk.getQuantity();
            if (rest <= 0) done = true; else s = s.withQuantity(rest);
          }
        } else if (rollbackMode && s.getItemId().equals(cur.getItemId()) && cur.getQuantity() == s.getQuantity()) {
          done = true;
        }
      }
      if (done) placed++;
      else { give(st, ref, player, s, u); moved++; }
    }
  }
  return new int[] { placed, moved, skipped };
}""")

# ================= ProfSwitch: checks, the switch transaction, creation, crash recovery =================
M(sw, r"""
public static long ago(java.time.Instant then, java.time.Instant now) {
  if (then == null || now == null) return -1L;
  try {
    long ms = java.time.Duration.between(then, now).toMillis();
    return ms < 0L ? -1L : ms;
  } catch (Throwable t) { return -1L; }
}""")
M(sw, r"""
public static String refuse(@ST@ st, @REF@ ref, @PLA@ player) {
  try {
    if (st.getComponent(ref, @DEATH@.getComponentType()) != null) return "You cannot switch profiles while dead.";
  } catch (Throwable t) { }
  try {
    @DDC@ dc = (@DDC@) st.getComponent(ref, @DDC@.getComponentType());
    if (dc != null && @PKG@.ProfCfg.COMBAT_MS > 0L) {
      @TR@ tr = (@TR@) st.getResource(@TR@.getResourceType());
      java.time.Instant now = tr == null ? null : tr.getNow();
      long a = ago(dc.getLastDamageTime(), now);
      long b = ago(dc.getLastCombatAction(), now);
      long m = -1L;
      if (a >= 0L) m = a;
      if (b >= 0L && (m < 0L || b < m)) m = b;
      if (m >= 0L && m < @PKG@.ProfCfg.COMBAT_MS) {
        long left = (@PKG@.ProfCfg.COMBAT_MS - m + 999L) / 1000L;
        return "You are in combat - wait " + left + " s before switching profiles.";
      }
    }
  } catch (Throwable t) { }
  try {
    Object cp = player.getPageManager().getCustomPage();
    if (cp != null && !(cp instanceof @PKG@.ProfilePage)) return "Close the open menu first, then switch profiles.";
  } catch (Throwable t) { }
  return null;
}""")
M(sw, r"""
public static java.nio.file.Path markerFile(java.util.UUID u) {
  return @PKG@.ProfStore.SWDIR.resolve(u.toString() + ".properties");
}""")
M(sw, r"""
public static boolean storeMarker(java.util.UUID u, java.util.Properties m) {
  try {
    java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
    m.store(bos, "SkyyProfiles switch marker - saved = finish or roll back at join, done = delete, failed = an admin restores by hand");
    @PKG@.ProfCfg.atomicWrite(markerFile(u), bos.toByteArray());
    return true;
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not write the switch marker for " + u + ": " + t); return false; }
}""")
M(sw, r"""
public static java.util.Properties readMarker(java.util.UUID u) {
  java.nio.file.Path f = markerFile(u);
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    java.util.Properties m = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { m.load(in); } finally { in.close(); }
    return m;
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not read the switch marker " + f + ": " + t); return null; }
}""")
M(sw, r"""
public static boolean writeMarker(java.util.UUID u, String from, String to, String fromKey, String toKey, boolean toHad) {
  java.util.Properties m = new java.util.Properties();
  m.setProperty("from", from);
  m.setProperty("to", to);
  m.setProperty("fromKey", fromKey);
  m.setProperty("toKey", toKey);
  m.setProperty("toHadFile", toHad ? "1" : "0");
  m.setProperty("stage", "saved");
  m.setProperty("at", String.valueOf(System.currentTimeMillis()));
  return storeMarker(u, m);
}""")
M(sw, r"""
public static void clearMarker(java.util.UUID u) {
  java.nio.file.Path f = markerFile(u);
  try { java.nio.file.Files.deleteIfExists(f); return; } catch (Throwable t) { @PKG@.ProfCfg.warn("could not delete " + f + " - marking it done: " + t); }
  java.util.Properties m = new java.util.Properties();
  m.setProperty("stage", "done");
  storeMarker(u, m);
}""")
M(sw, r"""
public static void failMarker(java.util.UUID u) {
  java.util.Properties m = readMarker(u);
  if (m == null) m = new java.util.Properties();
  m.setProperty("stage", "failed");
  storeMarker(u, m);
}""")
M(sw, r"""
public static void closeOurPage(@REF@ ref, @ST@ st, @PLA@ player) {
  try {
    Object cp = player.getPageManager().getCustomPage();
    if (cp instanceof @PKG@.ProfilePage) player.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { }
}""")
# the player's own /island (SkyyIslands sends them to the ACTIVE profile's island); fallback = default world spawn (SkyyIslands HubCmd)
M(sw, r"""
public static void travel(@ST@ st, @REF@ ref, @PR@ pr) {
  if (!@PKG@.ProfCfg.ISLAND_ON_SWITCH) return;
  try {
    if (@CMGR@.get().resolveCommand("island") != null) {
      @CMGR@.get().handleCommand(pr, "island");
      return;
    }
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not run /island after a switch: " + t); }
  try {
    if (st.getComponent(ref, @TP@.getComponentType()) != null) return;
    @WLD@ target = @UNI@.get().getDefaultWorld();
    if (target == null) return;
    @TRF@ where = target.getWorldConfig().getSpawnProvider().getSpawnPoint(target, pr.getUuid());
    if (where == null) return;
    ((@CA@) st).addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(target, where));
    pr.sendMessage(@MSG@.raw("[Profiles] SkyyIslands is not installed - you were sent to the world spawn."));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("fallback teleport after a switch failed: " + t); }
}""")
M(sw, r"""
public static boolean rollback(@ST@ st, @REF@ ref, @PLA@ player, java.util.UUID u, org.bson.BsonDocument cur, String why) {
  try {
    @PKG@.ProfInv.clearAll(st, ref);
    int[] r = @PKG@.ProfInv.loadInto(st, ref, player, cur, u, true);
    clearMarker(u);
    @PKG@.ProfStore.log("ROLLBACK " + u + " (" + why + ") restored=" + r[0] + " moved=" + r[1] + " skipped=" + r[2]);
    return true;
  } catch (Throwable t) {
    @PKG@.ProfCfg.warn("ROLLBACK FAILED for " + u + " (" + why + "): " + t + " - snapshots stay in inventories/, marker set to failed");
    failMarker(u);
    @PKG@.ProfStore.log("ROLLBACK-FAILED " + u + " (" + why + ") " + t);
    return false;
  }
}""")
M(sw, r"""
public static String switchLocked(@ST@ st, @REF@ ref, @PR@ pr, @PLA@ player, java.util.UUID u, java.util.Properties p, String from, String to) {
  String fromKey = @PKG@.ProfStore.keyFor(u, from);
  String toKey = @PKG@.ProfStore.keyFor(u, to);
  String toName = p.getProperty("p." + to + ".name", "Profile " + to);
  String toCls = p.getProperty("p." + to + ".class", "");
  boolean toHad = "1".equals(p.getProperty("p." + to + ".inv"));
  org.bson.BsonDocument target = null;
  if (toHad) {
    target = @PKG@.ProfInv.read(toKey);
    if (target == null) return "The saved inventory of " + toName + " is missing or unreadable - nothing was changed. Ask an admin (inventories/" + toKey + ".json).";
  } else {
    target = @PKG@.ProfInv.empty(u, to, toKey);
  }
  org.bson.BsonDocument cur = @PKG@.ProfInv.capture(st, ref, u, from, fromKey);
  int saved = @PKG@.ProfInv.slotCount(cur);
  if (!@PKG@.ProfInv.write(fromKey, cur)) return "Could not save your current inventory - nothing was changed.";
  if (!writeMarker(u, from, to, fromKey, toKey, toHad)) return "Could not start the switch - nothing was changed.";
  int[] res = null;
  try {
    if (!@PKG@.ProfInv.clearAll(st, ref)) {
      boolean ok0 = rollback(st, ref, player, u, cur, "clear failed");
      return ok0 ? "Could not empty your inventory - the switch was cancelled and your items are back." : "The switch failed. Please relog - an admin may need to restore your items (server log).";
    }
    res = @PKG@.ProfInv.loadInto(st, ref, player, target, u, false);
  } catch (Throwable t) {
    @PKG@.ProfCfg.warn("switch " + u + " " + from + "->" + to + " failed while swapping items: " + t);
    boolean ok1 = rollback(st, ref, player, u, cur, "swap failed " + t);
    return ok1 ? "The switch failed and was cancelled - your items are back." : "The switch failed. Please relog - an admin may need to restore your items (server log).";
  }
  if (!@PKG@.ProfStore.setActive(u, from, to)) {
    boolean ok2 = rollback(st, ref, player, u, cur, "players file not saved");
    return ok2 ? "Could not save the profile change - the switch was cancelled and your items are back." : "The switch failed. Please relog - an admin may need to restore your items (server log).";
  }
  clearMarker(u);
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("SWITCH " + u + " " + pr.getUsername() + " " + from + "->" + to + " saved=" + saved + " loaded=" + res[0] + " moved=" + res[1] + " skipped=" + res[2]);
  closeOurPage(ref, st, player);
  pr.sendMessage(@MSG@.raw("[Profiles] Switched to " + toName + (toCls.length() > 0 ? " (" + toCls + ")" : "") + ". Your other inventory is saved with its profile.").color("#8fe39a"));
  if (res[1] > 0) pr.sendMessage(@MSG@.raw("[Profiles] " + res[1] + " stack(s) could not go back to their old slot and were added to your inventory (dropped at your feet if it was full).").color("#ffc800"));
  travel(st, ref, pr);
  return null;
}""")
M(sw, r"""
public static String switchTo(@ST@ st, @REF@ ref, @PR@ pr, @PLA@ player, String to) {
  java.util.UUID u = pr.getUuid();
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = @PKG@.ProfStore.load(u);
  String from = @PKG@.ProfStore.activeOf(p);
  if (from == null) return "Create your first profile first (/profiles create).";
  if (to == null || !@PKG@.ProfStore.exists(p, to)) return "You have no such profile. /profiles list shows yours.";
  if (to.equals(from)) return "You are already on that profile.";
  String why = refuse(st, ref, player);
  if (why != null) return why;
  if (@PKG@.ProfStore.BUSY.putIfAbsent(u, Boolean.TRUE) != null) return "A profile switch is already running.";
  String r = null;
  try { r = switchLocked(st, ref, pr, player, u, p, from, to); }
  catch (Throwable t) { @PKG@.ProfCfg.warn("switch failed for " + u + ": " + t); r = "The switch failed: " + t.getMessage(); }
  @PKG@.ProfStore.BUSY.remove(u);
  return r;
}""")
M(sw, r"""
public static String createFirst(@PR@ pr, String cls, String name) {
  java.util.UUID u = pr.getUuid();
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.activeOf(p) != null) return "You already have a profile.";
  if (name == null || name.length() == 0 || @PKG@.ProfNames.used(p, name)) name = @PKG@.ProfNames.pick(p, null);
  if (!@PKG@.ProfStore.create(u, "1", name, cls, true)) return "Could not save your profile - try again or ask an admin.";
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("CREATE " + u + " " + pr.getUsername() + " profile 1 " + name + " " + cls + " (first profile = existing data)");
  pr.sendMessage(@MSG@.raw("[Profiles] Profile " + name + " created - you are " + @PKG@.ProfRoster.article(cls) + " for good on this profile. Everything you already had belongs to it. /profiles manages your profiles.").color("#8fe39a"));
  return null;
}""")
M(sw, r"""
public static String createAndSwitch(@ST@ st, @REF@ ref, @PR@ pr, @PLA@ player, String cls, String name) {
  java.util.UUID u = pr.getUuid();
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.activeOf(p) == null) return createFirst(pr, cls, name);
  if (@PKG@.ProfStore.count(p) >= @PKG@.ProfCfg.MAX_PROFILES) return "All " + @PKG@.ProfCfg.MAX_PROFILES + " profile slots are used.";
  String why = refuse(st, ref, player);
  if (why != null) return why;
  if (@PKG@.ProfStore.BUSY.containsKey(u)) return "A profile switch is already running.";
  String id = @PKG@.ProfStore.nextId(p);
  if (id == null) return "No free profile id.";
  if (name == null || name.length() == 0 || @PKG@.ProfNames.used(p, name)) name = @PKG@.ProfNames.pick(p, null);
  if (!@PKG@.ProfStore.create(u, id, name, cls, false)) return "Could not save the new profile - nothing was changed.";
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("CREATE " + u + " " + pr.getUsername() + " profile " + id + " " + name + " " + cls);
  String err = switchTo(st, ref, pr, player, id);
  if (err != null) return "Profile " + name + " was created but the switch did not happen - " + err + " Use Switch when you are ready.";
  return null;
}""")
# off the world thread at join: which snapshot must become the live inventory? null = nothing to do (or left for an admin)
M(sw, r"""
public static Object[] recoverPlan(java.util.UUID u) {
  java.util.Properties m = readMarker(u);
  if (m == null) return null;
  String stage = m.getProperty("stage", "");
  if (stage.equals("done")) { clearMarker(u); return null; }
  String from = m.getProperty("from");
  String to = m.getProperty("to");
  if (stage.equals("failed")) {
    @PKG@.ProfCfg.warn("player " + u + " has a FAILED switch marker (" + from + "->" + to + ") - restore by hand from inventories/, then delete switching/" + u + ".properties");
    return new Object[] { null, null, "failed" };
  }
  String act = @PKG@.ProfStore.activeId(u);
  if (act == null || from == null || to == null) { @PKG@.ProfCfg.warn("switch marker for " + u + " cannot be matched (active " + act + ") - left alone"); return null; }
  if (act.equals(from)) {
    org.bson.BsonDocument d = @PKG@.ProfInv.read(m.getProperty("fromKey", ""));
    if (d == null) { @PKG@.ProfCfg.warn("switch marker for " + u + ": snapshot " + m.getProperty("fromKey") + " is missing - left alone"); return null; }
    return new Object[] { d, from, "rolled back" };
  }
  if (act.equals(to)) {
    org.bson.BsonDocument d2 = null;
    if ("1".equals(m.getProperty("toHadFile"))) {
      d2 = @PKG@.ProfInv.read(m.getProperty("toKey", ""));
      if (d2 == null) { @PKG@.ProfCfg.warn("switch marker for " + u + ": snapshot " + m.getProperty("toKey") + " is missing - left alone"); return null; }
    } else {
      d2 = @PKG@.ProfInv.empty(u, to, m.getProperty("toKey", ""));
    }
    return new Object[] { d2, to, "finished" };
  }
  @PKG@.ProfCfg.warn("switch marker for " + u + " names " + from + "->" + to + " but the active profile is " + act + " - left alone");
  return null;
}""")
M(sw, r"""
public static void recoverApply(@ST@ st, @REF@ ref, @PR@ pr, @PLA@ player, org.bson.BsonDocument doc, String which, String how) {
  java.util.UUID u = pr.getUuid();
  boolean ok = @PKG@.ProfInv.clearAll(st, ref);
  int[] r = @PKG@.ProfInv.loadInto(st, ref, player, doc, u, false);
  clearMarker(u);
  @PKG@.ProfStore.publish(u);
  @PKG@.ProfStore.log("RECOVER " + u + " " + pr.getUsername() + " profile " + which + " " + how + " loaded=" + r[0] + " moved=" + r[1] + " skipped=" + r[2] + (ok ? "" : " (some slots could not be emptied)"));
  java.util.Properties p = @PKG@.ProfStore.load(u);
  String name = p.getProperty("p." + which + ".name", "Profile " + which);
  pr.sendMessage(@MSG@.raw("[Profiles] Your last profile switch was interrupted by a server stop. It was " + how + " - you are on " + name + " with its saved inventory.").color("#ffc800"));
}""")

# ================= ProfilePage: Profiles list (view 0) + Create Profile (view 1) =================
BTN = ("Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
       "Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
       "Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
BTN_GO = ("Style: TextButtonStyle(Default: (Background: #2f6a3a, LabelStyle: (FontSize: 12, TextColor: #e9ffe9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
          "Hovered: (Background: #3f8a4a, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), "
          "Pressed: (Background: #1f4a2a, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));")
def ui(src):
    return (src.replace("__BTN__", BTN.replace('"', '\\"')).replace("__BTNGO__", BTN_GO.replace('"', '\\"'))
               .replace("__W__", str(PAGE_W)).replace("__H__", str(PAGE_H)))
F(page, "public int view;")
F(page, "public boolean first;")
F(page, "public String pending;")
F(page, "public String pickName;")
F(page, "public String pickClass;")
F(page, "public String info;")
F(page, "public boolean reminded;")
M(page, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\'', ' ').replace('\\', ' ');
}""")
# first profile: pre-select the class the player already has in SkyyClasses 0.1.x (bridge class:<uuid>, else class:fn:get)
M(page, r"""
public void prepareCreate() {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Properties p = @PKG@.ProfStore.load(u);
  this.pickName = @PKG@.ProfNames.pick(p, null);
  this.pickClass = null;
  if (!this.first) return;
  String had = null;
  try {
    Object o = @PKG@.ProfCfg.bridge().get("class:" + u.toString());
    if (o instanceof String) had = (String) o;
    if (had == null) {
      Object f = @PKG@.ProfCfg.bridge().get("class:fn:get");
      if (f instanceof java.util.function.Function) {
        Object r = ((java.util.function.Function) f).apply(u);
        if (r instanceof String) had = (String) r;
      }
    }
  } catch (Throwable t) { }
  String[] c = @PKG@.ProfRoster.entry(had);
  if (c != null && "1".equals(c[6])) {
    this.pickClass = c[0];
    this.info = "Your current class " + c[0] + " is pre-selected.";
  }
}""")
M(page, ui(r"""
public void buildList(@UCB@ b, @UEB@ ev, java.util.UUID u, java.util.Properties p) {
  String bs = "__BTN__";
  String go = "__BTNGO__";
  String act = @PKG@.ProfStore.activeOf(p);
  int n = @PKG@.ProfStore.count(p);
  int max = @PKG@.ProfCfg.MAX_PROFILES;
  b.appendInline((String) null, "Group #SkyyPf { Anchor: (Width: __W__, Height: __H__); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }");
  b.appendInline("#SkyyPf", "Group { Anchor: (Height: 2); Background: #d08a4a; }");
  b.appendInline("#SkyyPf", "Label { Anchor: (Height: 30); Text: \"Profiles\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyPf", "Label { Anchor: (Height: 20); Text: \"Each profile is its own save - class, island, coins, skills, bags and inventory.\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
    String id = String.valueOf(i);
    if (!@PKG@.ProfStore.exists(p, id)) continue;
    boolean on = id.equals(act);
    boolean pend = id.equals(this.pending);
    String name = p.getProperty("p." + id + ".name", "Profile " + id);
    String cls = p.getProperty("p." + id + ".class", "");
    String[] ce = @PKG@.ProfRoster.entry(cls);
    String color = ce == null ? "#c9d6e2" : ce[3];
    String bg = on ? "#173524(0.95)" : (pend ? "#3a2f1a(0.95)" : "#142030(0.9)");
    String cid = "#SkyyPfCard" + id;
    String tid = "#SkyyPfTxt" + id;
    String aid = "#SkyyPfAct" + id;
    b.appendInline("#SkyyPf", "Label { Anchor: (Height: 6); Text: \"\"; }");
    b.appendInline("#SkyyPf", "Group #SkyyPfCard" + id + " { Anchor: (Height: 64); LayoutMode: Left; Background: " + bg + "; }");
    b.appendInline(cid, "Label { Anchor: (Width: 10, Height: 64); Text: \"\"; }");
    b.appendInline(cid, "Group { Anchor: (Width: 60, Height: 64); ItemIcon { Anchor: (Width: 44, Height: 44, Left: 8, Top: 10); ItemId: \"" + safe(@PKG@.ProfRoster.iconOf(cls)) + "\"; } }");
    b.appendInline(cid, "Group #SkyyPfTxt" + id + " { Anchor: (Width: 500, Height: 64); LayoutMode: Top; Padding: (Top: 4); }");
    b.appendInline(tid, "Label { Anchor: (Height: 22); Text: \"" + safe(name + (on ? " - ACTIVE" : "")) + "\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (on ? "#8fe39a" : "#ffe9c9") + ", VerticalAlignment: Center); }");
    String line2 = cls.length() == 0 ? "No class - an admin can set it" : cls + " - combat skill " + @PKG@.ProfRoster.skillOf(cls);
    b.appendInline(tid, "Label { Anchor: (Height: 18); Text: \"" + safe(line2) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: " + color + ", VerticalAlignment: Center); }");
    String line3 = "Created " + @PKG@.ProfStore.fmtDate(@PKG@.ProfStore.num(p, "p." + id + ".created")) + " - "
      + (on ? "playing now" : "last played " + @PKG@.ProfStore.fmtAgo(@PKG@.ProfStore.num(p, "p." + id + ".lastPlayed")));
    b.appendInline(tid, "Label { Anchor: (Height: 16); Text: \"" + safe(line3) + "\"; Style: (FontSize: 11, TextColor: #9fb8cc, VerticalAlignment: Center); }");
    b.appendInline(cid, "Group #SkyyPfAct" + id + " { Anchor: (Width: 170, Height: 64); LayoutMode: Top; Padding: (Top: 17); }");
    if (on) {
      b.appendInline(aid, "Label { Anchor: (Width: 150, Height: 30); Text: \"Active\"; Style: (FontSize: 13, RenderBold: true, TextColor: #8fe39a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else {
      b.appendInline(aid, "TextButton #SkyyPfSw" + id + " { Anchor: (Width: 150, Height: 30); Text: \"Switch\"; " + (pend ? go : bs) + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyPfSw" + id, @EVD@.of("a", "pfsw" + id));
    }
  }
  if (n < max) {
    b.appendInline("#SkyyPf", "Label { Anchor: (Height: 6); Text: \"\"; }");
    b.appendInline("#SkyyPf", "Group #SkyyPfNewCard { Anchor: (Height: 56); LayoutMode: Left; Background: #0d1219(0.85); }");
    b.appendInline("#SkyyPfNewCard", "Label { Anchor: (Width: 10, Height: 56); Text: \"\"; }");
    b.appendInline("#SkyyPfNewCard", "Group { Anchor: (Width: 60, Height: 56); ItemIcon { Anchor: (Width: 36, Height: 36, Left: 12, Top: 10); ItemId: \"" + @PKG@.ProfRoster.NEW_ICON + "\"; } }");
    b.appendInline("#SkyyPfNewCard", "Label { Anchor: (Width: 500, Height: 56); Text: \"" + safe("Empty slot - a new profile starts from zero with the class you pick (" + (max - n) + " free)") + "\"; Style: (FontSize: 12, TextColor: #c9d6e2, VerticalAlignment: Center, Wrap: true); }");
    b.appendInline("#SkyyPfNewCard", "Group #SkyyPfNewAct { Anchor: (Width: 170, Height: 56); LayoutMode: Top; Padding: (Top: 13); }");
    b.appendInline("#SkyyPfNewAct", "TextButton #SkyyPfNew { Anchor: (Width: 150, Height: 30); Text: \"Create new\"; " + go + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyPfNew", @EVD@.of("a", "pfnew"));
  }
  b.appendInline("#SkyyPf", "Label { Anchor: (Height: 8); Text: \"\"; }");
  b.appendInline("#SkyyPf", "Label #SkyyPfInfo { Anchor: (Height: 22); Text: \"" + safe(this.info) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffd27a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  if (this.pending != null && @PKG@.ProfStore.exists(p, this.pending) && !this.pending.equals(act)) {
    String pn = p.getProperty("p." + this.pending + ".name", "Profile " + this.pending);
    String pc = p.getProperty("p." + this.pending + ".class", "");
    String q = "Switch to " + pn + (pc.length() > 0 ? " (" + pc + ")" : "") + "? Your inventory is saved and you go to the island of that profile.";
    b.appendInline("#SkyyPf", "Group #SkyyPfConfirm { Anchor: (Height: 34); LayoutMode: Left; Padding: (Top: 2); }");
    b.appendInline("#SkyyPfConfirm", "Label { Anchor: (Width: 470, Height: 30); Text: \"" + safe(q) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center, Wrap: true); }");
    b.appendInline("#SkyyPfConfirm", "TextButton #SkyyPfYes { Anchor: (Width: 120, Height: 28); Text: \"Confirm\"; " + go + " }");
    b.appendInline("#SkyyPfConfirm", "Label { Anchor: (Width: 10, Height: 28); Text: \"\"; }");
    b.appendInline("#SkyyPfConfirm", "TextButton #SkyyPfNo { Anchor: (Width: 120, Height: 28); Text: \"Cancel\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyPfYes", @EVD@.of("a", "pfyes"));
    ev.addEventBinding(@BT@.Activating, "#SkyyPfNo", @EVD@.of("a", "pfno"));
  } else {
    String foot = n + " of " + max + " profile slots used. Switching saves your inventory and takes you to the island of the other profile. Not while in combat.";
    b.appendInline("#SkyyPf", "Label #SkyyPfFoot { Anchor: (Height: 30); Text: \"" + safe(foot) + "\"; Style: (FontSize: 11, TextColor: #8fa4b8, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  }
}"""))
M(page, ui(r"""
public void buildCreate(@UCB@ b, @UEB@ ev, java.util.UUID u, java.util.Properties p) {
  String bs = "__BTN__";
  String go = "__BTNGO__";
  String newId = this.first ? "1" : @PKG@.ProfStore.nextId(p);
  if (newId == null) newId = "?";
  b.appendInline((String) null, "Group #SkyyPf { Anchor: (Width: __W__, Height: __H__); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }");
  b.appendInline("#SkyyPf", "Group { Anchor: (Height: 2); Background: #d08a4a; }");
  b.appendInline("#SkyyPf", "Label { Anchor: (Height: 30); Text: \"" + (this.first ? "Create your first profile" : "Create a new profile") + "\"; Style: (FontSize: 17, RenderBold: true, TextColor: #ffe9c9, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyPf", "Group #SkyyPfNameRow { Anchor: (Height: 30); LayoutMode: Left; }");
  b.appendInline("#SkyyPfNameRow", "Label { Anchor: (Width: 580, Height: 30); Text: \"" + safe("Profile " + newId + " will be called " + this.pickName) + "\"; Style: (FontSize: 13, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center); }");
  b.appendInline("#SkyyPfNameRow", "TextButton #SkyyPfName { Anchor: (Width: 150, Height: 28); Text: \"Other name\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyPfName", @EVD@.of("a", "pfname"));
  String sub = this.first
    ? "Pick your class. It is locked to this profile forever - like creating a world. Everything you already have stays on this first profile."
    : "Pick a class. It is locked to this profile forever. The new profile starts from zero - empty inventory and its own island, coins and skills.";
  b.appendInline("#SkyyPf", "Label { Anchor: (Height: 32); Text: \"" + safe(sub) + "\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  java.util.ArrayList r = @PKG@.ProfRoster.roster();
  int shown = r.size() < 6 ? r.size() : 6;
  for (int i = 0; i < shown; i++) {
    String[] c = (String[]) r.get(i);
    boolean on = "1".equals(c[6]);
    boolean sel = this.pickClass != null && c[0].equalsIgnoreCase(this.pickClass);
    String bg = sel ? "#173524(0.95)" : (on ? "#142030(0.9)" : "#0d1219(0.85)");
    String cid = "#SkyyPfCls" + i;
    String iid = "#SkyyPfIco" + i;
    String tid = "#SkyyPfCTx" + i;
    String aid = "#SkyyPfCAct" + i;
    b.appendInline("#SkyyPf", "Label { Anchor: (Height: 4); Text: \"\"; }");
    b.appendInline("#SkyyPf", "Group #SkyyPfCls" + i + " { Anchor: (Height: 68); LayoutMode: Left; Background: " + bg + "; }");
    b.appendInline(cid, "Label { Anchor: (Width: 8, Height: 68); Text: \"\"; }");
    b.appendInline(cid, "Group #SkyyPfIco" + i + " { Anchor: (Width: 150, Height: 68); LayoutMode: Left; }");
    String[] ic = c[5].split(",");
    for (int k = 0; k < ic.length && k < 3; k++) {
      b.appendInline(iid, "Group { Anchor: (Width: 48, Height: 68); ItemIcon { Anchor: (Width: 40, Height: 40, Left: 4, Top: 14); ItemId: \"" + safe(ic[k]) + "\"; } }");
    }
    b.appendInline(cid, "Group #SkyyPfCTx" + i + " { Anchor: (Width: 440, Height: 68); LayoutMode: Top; Padding: (Top: 3); }");
    String title = c[0] + (sel ? " - selected" : (on ? "" : " - coming later"));
    b.appendInline(tid, "Label { Anchor: (Height: 22); Text: \"" + safe(title) + "\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (on ? c[3] : "#5f6b78") + ", VerticalAlignment: Center); }");
    b.appendInline(tid, "Label { Anchor: (Height: 16); Text: \"" + safe("Combat skill " + c[1] + " - " + c[4]) + "\"; Style: (FontSize: 11, RenderBold: true, TextColor: " + (on ? "#9fd8a2" : "#5f6b78") + ", VerticalAlignment: Center); }");
    b.appendInline(tid, "Label { Anchor: (Height: 26); Text: \"" + safe(c[2]) + "\"; Style: (FontSize: 10, TextColor: " + (on ? "#c9d6e2" : "#5f6b78") + ", VerticalAlignment: Center, Wrap: true); }");
    b.appendInline(cid, "Group #SkyyPfCAct" + i + " { Anchor: (Width: 140, Height: 68); LayoutMode: Top; Padding: (Top: 19); }");
    if (!on) {
      b.appendInline(aid, "Label { Anchor: (Width: 130, Height: 30); Text: \"Coming later\"; Style: (FontSize: 12, RenderBold: true, TextColor: #5f6b78, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else if (sel) {
      b.appendInline(aid, "Label { Anchor: (Width: 130, Height: 30); Text: \"Selected\"; Style: (FontSize: 13, RenderBold: true, TextColor: #8fe39a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    } else {
      b.appendInline(aid, "TextButton #SkyyPfPick" + i + " { Anchor: (Width: 130, Height: 30); Text: \"Select\"; " + bs + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyPfPick" + i, @EVD@.of("a", "pfcls" + i));
    }
  }
  b.appendInline("#SkyyPf", "Label { Anchor: (Height: 8); Text: \"\"; }");
  String q = this.pickClass == null ? "Select a class to continue."
    : "Create " + this.pickName + " as " + @PKG@.ProfRoster.article(this.pickClass) + "? The class can never be changed.";
  b.appendInline("#SkyyPf", "Group #SkyyPfMakeRow { Anchor: (Height: 34); LayoutMode: Left; Padding: (Top: 2); }");
  b.appendInline("#SkyyPfMakeRow", "Label { Anchor: (Width: 470, Height: 30); Text: \"" + safe(q) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffe9c9, VerticalAlignment: Center, Wrap: true); }");
  if (this.pickClass != null) {
    b.appendInline("#SkyyPfMakeRow", "TextButton #SkyyPfMake { Anchor: (Width: 130, Height: 28); Text: \"Create profile\"; " + go + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyPfMake", @EVD@.of("a", "pfmake"));
  } else {
    b.appendInline("#SkyyPfMakeRow", "Label { Anchor: (Width: 130, Height: 28); Text: \"\"; }");
  }
  b.appendInline("#SkyyPfMakeRow", "Label { Anchor: (Width: 10, Height: 28); Text: \"\"; }");
  b.appendInline("#SkyyPfMakeRow", "TextButton #SkyyPfBack { Anchor: (Width: 120, Height: 28); Text: \"" + (this.first ? "Later" : "Back") + "\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyPfBack", @EVD@.of("a", "pfback"));
  b.appendInline("#SkyyPf", "Label #SkyyPfInfo { Anchor: (Height: 22); Text: \"" + safe(this.info) + "\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffd27a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
}"""))
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  java.util.Properties p = @PKG@.ProfStore.load(u);
  if (@PKG@.ProfStore.activeOf(p) == null) { this.first = true; this.view = 1; }
  if (this.view == 1 && (this.pickName == null || this.pickName.length() == 0)) prepareCreate();
  if (this.view == 1) buildCreate(b, ev, u, p); else buildList(b, ev, u, p);
}""")
M(page, r"""
public void closeSelf(@REF@ ref, @ST@ st) {
  try {
    @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (player != null) player.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not close the profiles page: " + t); }
}""")
M(page, r"""
public void remindFirst() {
  try {
    if (this.reminded || @PKG@.ProfStore.activeId(this.playerRef.getUuid()) != null) return;
    this.reminded = true;
    this.playerRef.sendMessage(@MSG@.raw("[Profiles] You have no profile yet. Type /profiles to create one - you pick your class (" + @PKG@.ProfRoster.choiceText() + ") and it is locked to that profile.").color("#ffc800"));
  } catch (Throwable t) { }
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    java.util.Properties p = @PKG@.ProfStore.load(u);
    for (int i = 1; i <= @PKG@.ProfCfg.MAX_ID; i++) {
      if (data.indexOf("pfsw" + i + "\"") < 0) continue;
      String id = String.valueOf(i);
      this.pending = @PKG@.ProfStore.exists(p, id) ? id : null;
      this.info = "";
      rebuild();
      return;
    }
    if (data.indexOf("pfyes\"") >= 0) {
      String to = this.pending;
      this.pending = null;
      if (to == null) { rebuild(); return; }
      @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (player == null) return;
      String err = @PKG@.ProfSwitch.switchTo(st, ref, this.playerRef, player, to);
      if (err != null) { this.info = err; rebuild(); }
      return;
    }
    if (data.indexOf("pfno\"") >= 0) { this.pending = null; this.info = ""; rebuild(); return; }
    if (data.indexOf("pfnew\"") >= 0) {
      if (@PKG@.ProfStore.count(p) >= @PKG@.ProfCfg.MAX_PROFILES) { this.info = "All " + @PKG@.ProfCfg.MAX_PROFILES + " profile slots are used."; rebuild(); return; }
      this.view = 1;
      this.pending = null;
      this.info = "";
      prepareCreate();
      rebuild();
      return;
    }
    java.util.ArrayList r = @PKG@.ProfRoster.roster();
    for (int i = 0; i < r.size() && i < 6; i++) {
      if (data.indexOf("pfcls" + i + "\"") < 0) continue;
      String[] c = (String[]) r.get(i);
      if ("1".equals(c[6])) { this.pickClass = c[0]; this.info = ""; }
      else this.info = c[0] + " is coming later.";
      rebuild();
      return;
    }
    if (data.indexOf("pfname\"") >= 0) { this.pickName = @PKG@.ProfNames.pick(p, this.pickName); rebuild(); return; }
    if (data.indexOf("pfmake\"") >= 0) {
      if (this.pickClass == null) { this.info = "Select a class first."; rebuild(); return; }
      String[] ce = @PKG@.ProfRoster.entry(this.pickClass);
      if (ce == null || !"1".equals(ce[6])) { this.info = this.pickClass + " is not available."; this.pickClass = null; rebuild(); return; }
      @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (player == null) return;
      if (@PKG@.ProfStore.activeOf(p) == null) {
        String e1 = @PKG@.ProfSwitch.createFirst(this.playerRef, ce[0], this.pickName);
        if (e1 == null) { closeSelf(ref, st); return; }
        this.info = e1;
        rebuild();
        return;
      }
      int before = @PKG@.ProfStore.count(p);
      String e2 = @PKG@.ProfSwitch.createAndSwitch(st, ref, this.playerRef, player, ce[0], this.pickName);
      if (e2 == null) return;
      this.info = e2;
      if (@PKG@.ProfStore.count(@PKG@.ProfStore.load(u)) > before) { this.view = 0; this.first = false; }
      rebuild();
      return;
    }
    if (data.indexOf("pfback\"") >= 0) {
      if (this.first || @PKG@.ProfStore.activeOf(p) == null) { closeSelf(ref, st); remindFirst(); return; }
      this.view = 0;
      this.info = "";
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.ProfCfg.warn("profiles page event failed: " + t); }
}""")
M(page, r"""
public void onDismiss(@REF@ ref, @ST@ st) {
  if (this.first) remindFirst();
}""")
C(page, r"""
public ProfilePage(@PR@ pr, int view, boolean first) {
  super(pr, @LIFE@.CanDismiss);
  this.view = view;
  this.first = first;
  this.pending = null;
  this.info = "";
  this.pickName = "";
  this.pickClass = null;
  this.reminded = false;
  if (view == 1) prepareCreate();
}""")
M(page, r"""
public static String open(@ST@ st, @REF@ ref, @PR@ pr, int view) {
  @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (player == null) return "Could not open the page.";
  java.util.UUID u = pr.getUuid();
  if (@PKG@.ProfStore.BROKEN.containsKey(u)) return "Your profile file could not be read - ask an admin (server log).";
  java.util.Properties p = @PKG@.ProfStore.load(u);
  boolean first = @PKG@.ProfStore.activeOf(p) == null;
  int v = first ? 1 : view;
  if (v == 1 && !first && @PKG@.ProfStore.count(p) >= @PKG@.ProfCfg.MAX_PROFILES) return "All " + @PKG@.ProfCfg.MAX_PROFILES + " profile slots are used.";
  player.getPageManager().openCustomPage(ref, st, new @PKG@.ProfilePage(pr, v, first));
  return null;
}""")

# ================= OpenTask: first-join Create Profile page (SkyyHud/SkyyClasses pattern: delay, world-thread hop, WorldMap channel gate) =================
opn.addInterface(pool.get("java.lang.Runnable"))
F(opn, "public @PR@ pr;")
F(opn, "public boolean onWorld;")
F(opn, "public int calm;")
F(opn, "public int tries;")
C(opn, "public OpenTask(@PR@ pr) { this.pr = pr; this.onWorld = false; this.calm = 0; this.tries = 0; }")
M(opn, r"""
public void later(long ms) {
  this.onWorld = false;
  @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(opn, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    if (!this.onWorld) {
      java.util.UUID wu = pr.getWorldUuid();
      if (wu == null) { if (++this.tries < 240) later(500L); return; }
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) { if (++this.tries < 240) later(500L); return; }
      this.onWorld = true;
      w.execute(this);
      return;
    }
    java.util.UUID u = pr.getUuid();
    if (@PKG@.ProfStore.activeId(u) != null) return;
    @REF@ r = pr.getReference();
    if (r == null) { if (++this.tries < 240) later(500L); return; }
    @ST@ st = r.getStore();
    if (st == null) return;
    @PLA@ player = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (player == null) { if (++this.tries < 240) later(500L); return; }
    boolean writable = true;
    try {
      com.hypixel.hytale.server.core.io.PacketHandler ph = player.getPlayerConnection();
      com.hypixel.hytale.protocol.io.ChannelConnection ch = ph == null ? null : ph.getChannel(com.hypixel.hytale.protocol.NetworkChannel.WorldMap);
      writable = ch == null || ch.isWritable();
    } catch (Throwable t) { writable = true; }
    if (writable) this.calm++; else this.calm = 0;
    if (this.calm < 2) { if (++this.tries < 240) later(500L); return; }
    player.getPageManager().openCustomPage(r, st, new @PKG@.ProfilePage(pr, 1, true));
    @PKG@.ProfStore.markPrompted(u);
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not open the Create Profile page on join: " + t); }
}""")

# ================= RecoverTask: apply a crash-recovery plan on the player's world thread (retries until the player is in a world) =================
rec.addInterface(pool.get("java.lang.Runnable"))
F(rec, "public @PR@ pr;")
F(rec, "public org.bson.BsonDocument doc;")
F(rec, "public String which;")
F(rec, "public String how;")
F(rec, "public boolean onWorld;")
F(rec, "public int tries;")
C(rec, r"""
public RecoverTask(@PR@ pr, org.bson.BsonDocument doc, String which, String how) {
  this.pr = pr; this.doc = doc; this.which = which; this.how = how; this.onWorld = false; this.tries = 0;
}""")
M(rec, r"""
public void later(long ms) {
  this.onWorld = false;
  @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(rec, r"""
public void giveUp() {
  if (pr != null) @PKG@.ProfStore.BUSY.remove(pr.getUuid());
  @PKG@.ProfCfg.warn("crash recovery postponed for " + (pr == null ? "?" : String.valueOf(pr.getUuid())) + " - the marker stays for the next login");
}""")
M(rec, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) { giveUp(); return; }
    if (!this.onWorld) {
      java.util.UUID wu = pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { if (++this.tries < 120) later(250L); else giveUp(); return; }
      this.onWorld = true;
      w.execute(this);
      return;
    }
    @REF@ r = pr.getReference();
    @ST@ st = r == null ? null : r.getStore();
    @PLA@ player = null;
    if (st != null) player = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (player == null) { if (++this.tries < 120) later(250L); else giveUp(); return; }
    @PKG@.ProfSwitch.recoverApply(st, r, pr, player, this.doc, this.which, this.how);
  } catch (Throwable t) { @PKG@.ProfCfg.warn("crash recovery failed for " + (pr == null ? "?" : String.valueOf(pr.getUuid())) + ": " + t); }
  if (pr != null) @PKG@.ProfStore.BUSY.remove(pr.getUuid());
}""")

# ================= ReadyTask: first ready of the session, OFF the world thread (disk I/O) =================
rtk.addInterface(pool.get("java.lang.Runnable"))
F(rtk, "public @PR@ pr;")
C(rtk, "public ReadyTask(@PR@ pr) { this.pr = pr; }")
M(rtk, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.ProfStore.DATA.remove(u);
    java.util.Properties p = @PKG@.ProfStore.load(u);
    if (@PKG@.ProfStore.BROKEN.containsKey(u)) {
      pr.sendMessage(@MSG@.raw("[Profiles] Your profile file could not be read - profile changes are blocked. Please tell an admin.").color("#ff9d6b"));
      return;
    }
    @PKG@.ProfStore.noteLogin(u, pr.getUsername());
    p = @PKG@.ProfStore.load(u);
    if (@PKG@.ProfStore.activeOf(p) == null && @PKG@.ProfStore.count(p) > 0) {
      String low = @PKG@.ProfStore.lowestId(p);
      @PKG@.ProfCfg.warn("player " + u + " has profiles but no valid active one - activating profile " + low);
      @PKG@.ProfStore.setActive(u, null, low);
      p = @PKG@.ProfStore.load(u);
    }
    Object[] plan = @PKG@.ProfSwitch.recoverPlan(u);
    if (plan != null && plan[0] != null) {
      @PKG@.ProfStore.BUSY.put(u, Boolean.TRUE);
      new @PKG@.RecoverTask(pr, (org.bson.BsonDocument) plan[0], (String) plan[1], (String) plan[2]).later(0L);
    } else if (plan != null) {
      pr.sendMessage(@MSG@.raw("[Profiles] A profile switch of yours failed earlier and needs an admin - your items are saved on the server. Please tell an admin.").color("#ff9d6b"));
    }
    @PKG@.ProfStore.publish(u);
    String act = @PKG@.ProfStore.activeOf(p);
    if (act == null) {
      pr.sendMessage(@MSG@.raw("[Profiles] Welcome! Create your profile: you pick your class (" + @PKG@.ProfRoster.choiceText() + ") and it is locked to that profile. /profiles").color("#ffc800"));
      if (@PKG@.ProfCfg.PROMPT_EVERY_LOGIN || !"1".equals(p.getProperty("prompted"))) new @PKG@.OpenTask(pr).later(@PKG@.ProfCfg.OPEN_DELAY_MS);
      return;
    }
    String cls = p.getProperty("p." + act + ".class", "");
    pr.sendMessage(@MSG@.raw("[Profiles] Playing profile " + p.getProperty("p." + act + ".name", act) + (cls.length() > 0 ? " (" + cls + ")" : "") + ". /profiles to switch or create one.").color("#9fd8a2"));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("ready task failed: " + t); }
}""")
svt.addInterface(pool.get("java.lang.Runnable"))
F(svt, "public java.util.UUID u;")
C(svt, "public SaveTask(java.util.UUID u) { this.u = u; }")
M(svt, r"""
public void run() {
  try { if (u != null) @PKG@.ProfStore.touch(u); } catch (Throwable t) { }
}""")

# ================= PlayerReadyEvent (fires on EVERY world switch -> once per session) / disconnect =================
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public ProfReady() { }")
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
    if (@PKG@.ProfStore.SESSION.putIfAbsent(u, Boolean.TRUE) != null) return;
    @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.ReadyTask(pr));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("ready handler failed: " + t); }
}""")
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public ProfQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.ProfStore.SESSION.remove(u);
    @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.SaveTask(u));
  } catch (Throwable t) { }
}""")

# ================= /profiles create | switch <n> | list, /profiles (alias /profile) =================
C(pcre, r"""
public ProfCreateCmd() {
  super("create", "Create a new profile - pick its class, locked to that profile forever");
  addAliases(new String[] { "new" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(pcre, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String err = @PKG@.ProfilePage.open(store, ref, pr, 1);
    if (err != null) pr.sendMessage(@MSG@.raw("[Profiles] " + err));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("/profiles create failed: " + t); pr.sendMessage(@MSG@.raw("[Profiles] Could not open the page.")); }
}""")
F(psw, "public @RA@ profArg;")
C(psw, r"""
public ProfSwitchCmd() {
  super("switch", "Switch to another of your profiles: /profiles switch <number or name>");
  this.profArg = withRequiredArg("profile", "profile number (1, 2, ...) or name", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(psw, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.UUID u = pr.getUuid();
    String arg = String.valueOf(ctx.get(this.profArg));
    String id = @PKG@.ProfStore.resolveId(u, arg);
    if (id == null) { pr.sendMessage(@MSG@.raw("[Profiles] No profile '" + arg + "'. Yours: " + @PKG@.ProfStore.describe(u))); return; }
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    String err = @PKG@.ProfSwitch.switchTo(store, ref, pr, player, id);
    if (err != null) pr.sendMessage(@MSG@.raw("[Profiles] " + err).color("#ff9d6b"));
  } catch (Throwable t) { @PKG@.ProfCfg.warn("/profiles switch failed: " + t); pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profiles switch <number or name>")); }
}""")
C(plst, r"""
public ProfListCmd() {
  super("list", "List your profiles in chat");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(plst, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Profiles] " + @PKG@.ProfStore.describe(pr.getUuid())));
}""")
C(pcmd, r"""
public ProfilesCmd() {
  super("profiles", "Your profiles (each = its own class, island and inventory): /profiles | create | switch <n> | list");
  addAliases(new String[] { "profile" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.ProfCreateCmd());
  addSubCommand(new @PKG@.ProfSwitchCmd());
  addSubCommand(new @PKG@.ProfListCmd());
}""")
M(pcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String err = @PKG@.ProfilePage.open(store, ref, pr, 0);
    if (err != null) pr.sendMessage(@MSG@.raw("[Profiles] " + err));
  } catch (Throwable t) {
    @PKG@.ProfCfg.warn("/profiles failed: " + t);
    pr.sendMessage(@MSG@.raw("[Profiles] Could not open the page. Your profiles: " + @PKG@.ProfStore.describe(pr.getUuid())));
  }
}""")

# ================= /profileadmin info | setclass | reload (perm skyyprofiles.admin) =================
F(ainf, "public @RA@ playerArg;")
C(ainf, r"""
public AdmInfoCmd() {
  super("info", "(admin) A player's profiles: /profileadmin info <player|uuid>");
  requirePermission("skyyprofiles.admin");
  this.playerArg = withRequiredArg("player", "player name (online, or seen before) or uuid", @ATY@.STRING);
}""")
M(ainf, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyprofiles.admin")) { pr.sendMessage(@MSG@.raw("[Profiles] no permission (skyyprofiles.admin)")); return; }
    java.util.UUID t = @PKG@.ProfStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Profiles] Unknown player - use a name (online or seen before) or a uuid.")); return; }
    java.util.Properties p = @PKG@.ProfStore.load(t);
    String act = @PKG@.ProfStore.activeOf(p);
    pr.sendMessage(@MSG@.raw("[Profiles] " + p.getProperty("username", "?") + " (" + t + "): " + @PKG@.ProfStore.describe(t)));
    pr.sendMessage(@MSG@.raw("[Profiles] active key " + @PKG@.ProfStore.keyFor(t, act) + " | epoch " + @PKG@.ProfStore.num(p, "epoch") + " | switches " + @PKG@.ProfStore.num(p, "switches")
      + (@PKG@.ProfStore.BROKEN.containsKey(t) ? " | FILE UNREADABLE" : "") + (@PKG@.ProfSwitch.readMarker(t) != null ? " | switch marker present (switching/" + t + ".properties)" : "")));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profileadmin info <player|uuid>")); }
}""")
F(acls, "public @RA@ playerArg;")
F(acls, "public @RA@ profArg;")
F(acls, "public @RA@ classArg;")
C(acls, r"""
public AdmSetClassCmd() {
  super("setclass", "(admin) Fix the class of a profile: /profileadmin setclass <player|uuid> <profile number> <class>");
  requirePermission("skyyprofiles.admin");
  this.playerArg = withRequiredArg("player", "player name (online, or seen before) or uuid", @ATY@.STRING);
  this.profArg = withRequiredArg("profile", "profile number (1, 2, ...) or name", @ATY@.STRING);
  this.classArg = withRequiredArg("class", "archer | warrior | mage (assassin, shaman later)", @ATY@.STRING);
}""")
M(acls, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyyprofiles.admin")) { pr.sendMessage(@MSG@.raw("[Profiles] no permission (skyyprofiles.admin)")); return; }
    java.util.UUID t = @PKG@.ProfStore.resolve(String.valueOf(ctx.get(this.playerArg)));
    if (t == null) { pr.sendMessage(@MSG@.raw("[Profiles] Unknown player - use a name (online or seen before) or a uuid.")); return; }
    String id = @PKG@.ProfStore.resolveId(t, String.valueOf(ctx.get(this.profArg)));
    if (id == null) { pr.sendMessage(@MSG@.raw("[Profiles] That player has no such profile: " + @PKG@.ProfStore.describe(t))); return; }
    String[] c = @PKG@.ProfRoster.entry(String.valueOf(ctx.get(this.classArg)));
    if (c == null) { pr.sendMessage(@MSG@.raw("[Profiles] Unknown class. Classes: " + @PKG@.ProfRoster.choiceText())); return; }
    if (!@PKG@.ProfStore.setClass(t, id, c[0])) { pr.sendMessage(@MSG@.raw("[Profiles] Could not save the change (see the server log).")); return; }
    @PKG@.ProfStore.publish(t);
    @PKG@.ProfStore.log("SETCLASS " + t + " profile " + id + " -> " + c[0] + " by " + pr.getUsername());
    pr.sendMessage(@MSG@.raw("[Profiles] Profile " + id + " of " + t + " is now " + @PKG@.ProfRoster.article(c[0]) + ("1".equals(c[6]) ? "" : " (not selectable yet in SkyyClasses)") + ". " + @PKG@.ProfStore.describe(t)));
    @PR@ tp = @UNI@.get().getPlayer(t);
    if (tp != null && tp.isValid()) tp.sendMessage(@MSG@.raw("[Profiles] An admin set the class of your profile " + id + " to " + c[0] + ".").color("#ffc800"));
  } catch (Throwable x) { pr.sendMessage(@MSG@.raw("[Profiles] Usage: /profileadmin setclass <player|uuid> <profile number> <class>")); }
}""")
C(arel, r"""
public AdmReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyProfiles/config.properties and the player files");
  requirePermission("skyyprofiles.admin");
}""")
M(arel, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyyprofiles.admin")) { pr.sendMessage(@MSG@.raw("[Profiles] no permission (skyyprofiles.admin)")); return; }
  String c = @PKG@.ProfCfg.load();
  @PKG@.ProfStore.DATA.clear();
  @PKG@.ProfStore.BROKEN.clear();
  int n = 0;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) { @PR@ p = (@PR@) it.next(); if (p != null) { @PKG@.ProfStore.publish(p.getUuid()); n++; } }
  } catch (Throwable t) { }
  pr.sendMessage(@MSG@.raw("[Profiles] reloaded (" + n + " online players republished): " + c));
}""")
C(adm, r"""
public ProfileAdminCmd() {
  super("profileadmin", "(admin) /profileadmin info <player> | setclass <player> <n> <class> | reload");
  requirePermission("skyyprofiles.admin");
  addSubCommand(new @PKG@.AdmInfoCmd());
  addSubCommand(new @PKG@.AdmSetClassCmd());
  addSubCommand(new @PKG@.AdmReloadCmd());
}""")
M(adm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Profiles] /profileadmin info <player|uuid> | setclass <player|uuid> <profile> <class> | reload"));
  pr.sendMessage(@MSG@.raw("[Profiles] config: " + @PKG@.ProfCfg.load()));
}""")

# ================= plugin =================
C(pl, "public SkyyProfilesPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ProfCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyProfiles");
  @PKG@.ProfCfg.FILE = base.resolve("config.properties");
  @PKG@.ProfStore.DIR = base.resolve("players");
  @PKG@.ProfStore.SWDIR = base.resolve("switching");
  @PKG@.ProfStore.INVDIR = base.resolve("inventories");
  @PKG@.ProfStore.LOGF = base.resolve("switches.log");
  String cfgText = @PKG@.ProfCfg.load();
  try {
    java.nio.file.Files.createDirectories(@PKG@.ProfStore.DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.createDirectories(@PKG@.ProfStore.SWDIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.createDirectories(@PKG@.ProfStore.INVDIR, new java.nio.file.attribute.FileAttribute[0]);
  } catch (Throwable t) { @PKG@.ProfCfg.warn("could not create the data folders: " + t); }
  int markers = 0;
  try {
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(@PKG@.ProfStore.SWDIR, "*.properties");
    try { java.util.Iterator it = ds.iterator(); while (it.hasNext()) { it.next(); markers++; } } finally { ds.close(); }
  } catch (Throwable t) { }
  @PKG@.ProfCfg.bridge().put("profile:fn:key", new @PKG@.KeyFn());
  getCommandRegistry().registerCommand(new @PKG@.ProfilesCmd());
  getCommandRegistry().registerCommand(new @PKG@.ProfileAdminCmd());
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.ProfReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.ProfQuit());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyProfiles] __VER__ ready - /profiles, /profileadmin; " + cfgText
    + (markers > 0 ? "; " + markers + " interrupted switch(es) will be finished or rolled back when those players join" : ""));
}""".replace("__VER__", VERSION))
M(pl, r"""
protected void shutdown() {
  super.shutdown();
}""")

for c in (cfg, ros, nam, sto, kfn, inv, sw, page, opn, rec, rtk, svt, rdy, quit_, pcre, psw, plst, pcmd, ainf, acls, arel, adm, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)
m = B.manifest("SkyyProfiles", VERSION, "SkyWynn profiles (SkyBlock style): each profile is its own save - class (picked at creation, locked), island, coins, skills, bags and vanilla inventory. /profiles. Zero dependencies; SkyyClasses and SkyyIslands are used when present.", PKG + ".SkyyProfilesPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyProfiles.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyProfiles" % VERSION, disable_prefix="Skyy:")
