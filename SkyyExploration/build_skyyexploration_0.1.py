"""SkyyExploration 0.1 - build script (javassist via jpype, tools/skyybuild.py). NEW mod, never deployed: edit this file directly.
Owner: Skyy (they/them). Spec: research/Exploration-Build-Spec.md part 2 (Skyy's picks: SkyyExploration-Plan.md "Build now", HANDOFF
section 1 "Exploration call (Skyy, 2026-09-24)"). Pairs with SkyySkills 0.4.1 (Exploration row, no boosters) + SkyyTrees 0.2
(Exploration tree: Treasure Sense / Scavenger), but loads and works alone (zero dependencies, everything through the skyy bridge).

Run:   python build_skyyexploration_0.1.py            -> SkyyExploration/SkyyExploration-0.1.jar
       python build_skyyexploration_0.1.py --deploy   -> also Mods/SkyyExploration.jar + enabled in the HUD mod world (ONLY with Skyy's OK)

WHAT IT DOES (each source pays ONCE per profile, never while flying or in creative, XP boosters never apply)
  A4 LOOT CHESTS  World loot is rolled when the chest's block entity is ADDED to the chunk store (StashPlugin$StashSystem, then the
     drop list is cleared). ChestSpawnSys = our own ChunkStore RefSystem (query ItemContainerBlock + BlockModule$BlockStateInfo) ordered
     BEFORE StashPlugin$StashSystem (SystemDependency(Order.BEFORE, ...)) records every container that HAS a drop list at add time in a
     per-world registry (world-file journal chests/<worldFile>.log; lines "A x y z droplist placedBy" / "R x y z"). Players can never
     create a drop list (only spawner tables, prefabs or an admin /stash set). If the ordered registration throws
     IllegalArgumentException (Hytale:Stash is not loaded: turned off in the server config, or its setup failed), the unordered
     ChestSpawnLateSys is registered instead (one WARN). Load order is never the cause: Mod.calculateLoadOrder (HytaleServer.jar)
     makes every enabled core plugin of group "Hytale" (manifests.json in the server jar, inServerClassPath) a predecessor of every
     Mods-folder plugin, PluginManager.setup() runs setup() in that order, and a modLoadOrder that contradicts it stops the server
     (ModLoadOrderException) - so StashSystem is always registered before our setup() when Hytale:Stash is enabled.
     A REMOVE / BUILDER_TOOLS_UNDO of the block entity drops the record; a SPAWN without a drop list at a recorded spot drops it too
     (a fresh non-loot container replaced it); UNLOAD / a LOAD without a drop list keep it. The capture keeps running while
     chests.enabled=false (a chest generated then would otherwise be lost for good).
     OPEN: ChestOpenSys (UseBlockEvent$Post on the player) resolves the multi-block origin (BlockSection.getFiller, StashCommand math)
     and queues an OpenCheck on the world thread that polls ItemContainerBlock.getWindows() for the player's UUIDComponent uuid (next
     tick, then every chests.pollMs up to chests.pollMaxMs). Backup: ExpTick scans the player's open ContainerBlockWindows every
     second. Award (ExpAward.chestOpened, world task): refused while creative / flying / profile:busy / the profile key changed / the
     player left that world; PlacedByInteractionComponent guard (a different placer than recorded -> the record is dropped); then the
     opened set of the profile, XP = chests.base x zoneMult[Z] x tierMult[T] for Zone<Z>_<Faction>_Tier<T> (else chests.xpDefault, or
     a chest.xp.<id> override), chest luck, Scavenger, chat, titles.
  B2 CHEST LUCK   chance = min(luck.max, Exploration level x luck.perLevel + tree:fn:bonus "Exploration.ELuck"): one extra
     ItemModule.getRandomItemDrops(droplist) roll into the OPENER's inventory (getCombinedStorageHotbarBackpack = storage first,
     dropped at the feet when full), never into the chest. Scavenger (tree:fn:bonus "Exploration.EScav"): coins:fn:add of
     scav.coinsPerLevel x level.
  A5 MAP COVERAGE ExpTick (1 s, world thread): new chunk (ChunkUtil.indexChunkFromBlock of TransformComponent.getPosition) not in the
     profile's set for this world -> recorded; paid chunks.xp x chunks.zoneMult[Z] while the per-world paid counter is below
     chunks.maxPaidPerWorld. Skipped (no record, no XP): creative, MovementStates.flying, gliding / mounting when their switches are
     off, no MovementStatesComponent, excluded worlds. Teleports count (Skyy Q8). One aggregated chat line per chunks.feedbackMs
     (/explore quiet hides it).
  A6 ZONES        Player.getWorldMapTracker().getCurrentZone().regionName() (the engine's zone key, e.g. Zone1_Tier1), kept per
     profile (the engine's own discovered set is per account). 27 regions have a Discovery block; names baked from server.lang.
  D3 TITLES       21 titles (Exploration levels, zone sets, chest and chunk counts). EARNED IS DERIVED, never stored; only the selected
     id is saved. Display = chat prefix: ChatHook registered with EventRegistry.registerAsyncGlobal((short) titles.chatPriority 30000,
     PlayerChatEvent, Function) (above EventPriority.LAST 21844, so after every standard handler) returns future.thenApply(ChatWrap),
     which wraps the PREVIOUS formatter in a TitleFormatter (the RPGLeveling 0.3.13 RpgChatFormatHook pattern). The formatter runs on
     the async chat thread and only reads ExpTitles.CHAT (UUID -> {name, color}, filled by ExpTick).
  XP              every source adds to the profile's OWED ledger; ExpXp.flush sends skill:fn:addxp Object[]{UUID, "Exploration",
     Long(min(owed, 500000)), "exploration", pkey} right after an award and every bridge.retryMs while owed > 0 (never while the
     player is in creative - SkyySkills would drop it). TRUE = owed -> earned. FALSE / no Function (no SkyySkills, or 0.4 without the
     Exploration row) = it waits; the page says "N Exploration XP waiting for SkyySkills 0.4.1". Nothing here multiplies XP.

BRIDGE (System.getProperties().get("skyy.bridge"))
  reads  skill:fn:addxp, skill:fn:level, skill:fn:xp, skill:<uuid> (SkyySkills), tree:fn:bonus, tree:names (SkyyTrees), coins:fn:add
         (SkyyCoins), profile:fn:key, profile:epoch:<uuid>, profile:busy:<uuid> (SkyyProfiles)
  writes explore:<uuid> = "level:12,zones:7/27,chests:12,chunks:1204,title:wayfarer", explore:title:<uuid> = selected title name
         (absent = none), explore:fn:title (Function UUID -> String or null), skill:stats:Exploration (Function Object[]{UUID,
         Integer level, Boolean next} -> List of String, read by the SkyySkills Stats page). UUID-keyed values describe the ACTIVE
         profile, are republished within 1 s of an epoch change, removed for players gone 30 s (retainOnline) and in shutdown.

STORAGE (tools/PROFILES-CONTRACT.md)  <world>/mods/Skyy_SkyyExploration/
  config.properties (defaults written on first run; /exploreadmin reload)
  chests/<worldFile>.log   loot chest registry journal per world (NOT per profile), replayed in setup() before any chunk loads,
                           compacted at load when lines > 2 x live + 1000. worldFile = name with chars outside [A-Za-z0-9.-] -> '-',
                           + '-' + Integer.toHexString(name.hashCode())
  players/<pkey>.properties name, v, title, quiet, owed, earned, chests, luck, total, zones, paid.<worldFile> (atomic tmp + ATOMIC_MOVE,
                           5 x 20 ms retries; a file that exists but cannot be read is NEVER overwritten - that player earns nothing
                           until it reads, the log warns, the page says so)
  players/<pkey>/chests.txt           opened loot chests "<worldFile> x y z" (append-only; the chest count is derived from it)
  players/<pkey>/chunks/<worldFile>.bin  chunk indices, 8-byte big-endian longs, append-only (a torn last record is ignored), loaded
                           lazily on the player's world thread the first time they tick in that world
  Appends go through one ordered queue written by ExpSaver every 2 s; dirty property files every 10 s; saveSoon (scheduler) after
  every chest, zone and XP payment; full flush in shutdown(). Player files are only READ on world threads.

PAGE /explore (inline, HANDOFF section 2): tabs Overview | Zones | Titles, cards, zone lists, title rows with Use buttons, "< Skills"
  and "Exploration tree" (runs the command while this page is open; the new page replaces it). Rebuilt only on clicks.
COMMANDS (HANDOFF command rules): /explore (aliases exploration, discoveries), /explore quiet, /title (alias titles), /title <title>
  (usage variant; id, name without spaces, 3+ letter prefix of exactly one title - "wor" fits two and asks for more letters, off /
  none) - all hytale:Adventurer. /exploreadmin reload | stats |
  resetme - requirePermission("skyyexploration.admin") + setPermissionGroups(new String[0]).

ENGINE RULES KEPT  one registerSystem per class (ChestSpawnSys, ChestSpawnLateSys, ChestOpenSys, ExpTick); components / inventory only on
  the world thread (the award and the luck roll run in world tasks, never inside a system iteration); items to storage first; no
  lambdas / generics / varargs / autoboxing / enhanced-for / inner classes / String switch / try-with-resources; methods added before
  their callers.

UNVERIFIED (needs Skyy's in-game test, spec section 6): the BEFORE ordering really sees the drop list of freshly generated chests
  (/exploreadmin stats capture counter must rise in new terrain); UseBlockEvent$Post fires for Open_Container chests (the 1 s window
  scan is the backup); the chat prefix survives other chat mods (Essentials inside Skyys-Modpack); getCurrentZone() reports the Zone1
  regions; MovementStates.flying is true under /fly and creative flight.
"""
import sys, os, json, re, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.explore"

T = {
    "PKG": PKG,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "CMGR": "com.hypixel.hytale.server.core.command.system.CommandManager",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PGM": "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "ARCH": "com.hypixel.hytale.component.Archetype",
    "ADDR": "com.hypixel.hytale.component.AddReason",
    "REMR": "com.hypixel.hytale.component.RemoveReason",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
    "ORD": "com.hypixel.hytale.component.dependency.Order",
    "SSYS": "com.hypixel.hytale.builtin.adventure.stash.StashPlugin$StashSystem",
    "ICB": "com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock",
    "BSI": "com.hypixel.hytale.server.core.modules.block.BlockModule$BlockStateInfo",
    "BMOD": "com.hypixel.hytale.server.core.modules.block.BlockModule",
    "CSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.ChunkSection",
    "BSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "FBU": "com.hypixel.hytale.server.core.util.FillerBlockUtil",
    "PBI": "com.hypixel.hytale.server.core.modules.interaction.components.PlacedByInteractionComponent",
    "UBE": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent",
    "UBP": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Post",
    "V3I": "org.joml.Vector3i",
    "V3D": "org.joml.Vector3d",
    "CBW": "com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow",
    "BWIN": "com.hypixel.hytale.server.core.entity.entities.player.windows.BlockWindow",
    "WMGR": "com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager",
    "IMOD": "com.hypixel.hytale.server.core.modules.item.ItemModule",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "SIC": "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "WMT": "com.hypixel.hytale.server.core.universe.world.WorldMapTracker",
    "ZDI": "com.hypixel.hytale.server.core.universe.world.WorldMapTracker$ZoneDiscoveryInfo",
    "MSC": "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "MVT": "com.hypixel.hytale.protocol.MovementStates",
    "GM": "com.hypixel.hytale.protocol.GameMode",
    "PCE": "com.hypixel.hytale.server.core.event.events.player.PlayerChatEvent",
    "PCF": "com.hypixel.hytale.server.core.event.events.player.PlayerChatEvent$Formatter",
    "EREG": "com.hypixel.hytale.event.EventRegistry",
    "UUC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "ETU": "com.hypixel.hytale.server.core.util.EventTitleUtil",
    "TRC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "LOS": "it.unimi.dsi.fastutil.longs.LongOpenHashSet",
}

# every engine member this mod touches (javassist would also fail to compile; the probe names the drift early)
for c, m in (("ICB", "getComponentType"), ("ICB", "getDroplist"), ("ICB", "getWindows"), ("BSI", "getComponentType"), ("BSI", "getIndex"),
             ("BSI", "getSectionRef"), ("CSEC", "getComponentType"), ("CSEC", "getX"), ("CSEC", "getY"), ("CSEC", "getZ"),
             ("CHU", "xFromIndex"), ("CHU", "yFromIndex"), ("CHU", "zFromIndex"), ("CHU", "worldCoordFromLocalCoord"),
             ("CHU", "indexChunkFromBlock"), ("PBI", "getComponentType"), ("PBI", "getWhoPlacedUuid"), ("ORD", "BEFORE"),
             ("RSYS", "onEntityAdded"), ("RSYS", "onEntityRemove"), ("ADDR", "SPAWN"), ("REMR", "REMOVE"), ("REMR", "UNLOAD"),
             ("REMR", "BUILDER_TOOLS_UNDO"), ("SSYS", "onEntityAdded"), ("SDEP", "getSystemClass"), ("UBE", "getTargetBlock"),
             ("BWIN", "getX"), ("BWIN", "getY"), ("BWIN", "getZ"), ("PLA", "getWindowManager"), ("WMGR", "getWindows"),
             ("BSEC", "getComponentType"), ("BSEC", "getFiller"), ("FBU", "unpackX"), ("FBU", "unpackY"), ("FBU", "unpackZ"),
             ("BMOD", "getBlockEntity"), ("IMOD", "get"), ("IMOD", "getRandomItemDrops"), ("PLA", "getInventory"),
             ("INV", "getCombinedStorageHotbarBackpack"), ("SIC", "addOrDropItemStack"), ("PLA", "getWorldMapTracker"),
             ("WMT", "getCurrentZone"), ("ZDI", "regionName"), ("ZDI", "zoneName"), ("MSC", "getComponentType"),
             ("MSC", "getMovementStates"), ("MVT", "flying"), ("MVT", "gliding"), ("MVT", "mounting"), ("PLA", "getGameMode"),
             ("PLA", "isWaitingForClientReady"), ("PLA", "getPageManager"), ("GM", "Creative"), ("PCE", "getFormatter"),
             ("PCE", "setFormatter"), ("PCE", "getSender"), ("PCE", "DEFAULT_FORMATTER"), ("PCF", "format"),
             ("EREG", "registerAsyncGlobal"), ("MSG", "join"), ("MSG", "raw"), ("MSG", "color"), ("MSG", "translation"),
             ("UUC", "getComponentType"), ("UUC", "getUuid"), ("ETU", "showEventTitleToPlayer"), ("TRC", "getComponentType"),
             ("TRC", "getPosition"), ("V3D", "x"), ("V3D", "z"), ("V3I", "x"), ("V3I", "y"), ("V3I", "z"), ("CHS", "getWorld"),
             ("CHS", "getStore"), ("CHS", "getChunkSectionReferenceAtBlock"), ("WLD", "getName"), ("WLD", "execute"),
             ("WLD", "getChunkStore"), ("UNI", "get"), ("UNI", "getPlayer"), ("UNI", "getPlayers"), ("PR", "getUuid"),
             ("PR", "getReference"), ("PR", "getUsername"), ("PR", "sendMessage"), ("PR", "hasPermission"), ("PR", "isValid"),
             ("PR", "getComponentType"), ("ITM", "getAssetMap"), ("ITM", "getTranslationMessage"), ("IS", "getItemId"),
             ("IS", "getQuantity"), ("IS", "isEmpty"), ("PGM", "openCustomPage"), ("PAGE", "rebuild"), ("EVD", "of"),
             ("CMGR", "get"), ("CMGR", "handleCommand"), ("HSV", "SCHEDULED_EXECUTOR"), ("AC", "setPermissionGroups"),
             ("AC", "requirePermission"), ("AC", "addSubCommand"), ("AC", "addUsageVariant"), ("AC", "withRequiredArg"),
             ("AC", "addAliases"), ("ETS", "tick"), ("ETS", "isParallel"), ("EES", "handle"), ("ARCH", "empty"),
             ("ST", "getComponent"), ("ST", "getExternalData"), ("CB", "getComponent"), ("CAC", "getComponent"), ("REF", "isValid"),
             ("REF", "getStore"), ("QRY", "and"), ("LOS", "add"), ("LOS", "contains"), ("LOS", "size"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getChunkStoreRegistry"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEventRegistry"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem"),
             ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove")):
    B.probe(pool, T.get(c, c), m)

LEFT = re.compile(r"@[A-Z][A-Z0-9_]*@")
def sub(src):
    out = src
    for k in sorted(T, key=len, reverse=True):
        out = out.replace("@" + k + "@", T[k])
    left = LEFT.findall(out)
    if left:
        raise SystemExit("unreplaced tokens %s in:\n%s" % (left, out[:300]))
    return out
def _mk(kind, cls, src):
    s = sub(src)
    try:
        if kind == "M": cls.addMethod(CtNewMethod.make(s, cls))
        elif kind == "F": cls.addField(CtField.make(s, cls))
        else: cls.addConstructor(CtNewConstructor.make(s, cls))
    except Exception as e:
        print("COMPILE ERROR in", cls.getName(), ":", str(e)[:400])
        print(s[:1500])
        raise
def M(cls, src): _mk("M", cls, src)
def F(cls, src): _mk("F", cls, src)
def C(cls, src): _mk("C", cls, src)

# ================= Assets.zip: zones, region names, loot drop lists, icons =================
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
with zipfile.ZipFile(ASSETS) as z:
    NAMES_ALL = z.namelist()
    ITEM_IDS = set(os.path.basename(n)[:-5] for n in NAMES_ALL if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    LANG = {}
    for line in z.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            LANG[k.strip()] = v.strip()
    DISC = {}
    for n in NAMES_ALL:
        mm = re.match(r"Server/World/Default/Zones/([^/]+)/Zone\.json$", n)
        if mm:
            dj = json.loads(z.read(n))
            if dj.get("Discovery"):
                DISC[mm.group(1)] = dj["Discovery"]
    SPAWN_DL = set()
    def _walk(o):
        if isinstance(o, dict):
            for kk, vv in o.items():
                if kk == "Droplist" and isinstance(vv, str): SPAWN_DL.add(vv)
                _walk(vv)
        elif isinstance(o, list):
            for x in o: _walk(x)
    for n in NAMES_ALL:
        if n.startswith("Server/Item/Block/Spawners/") and n.endswith(".json"):
            _walk(json.loads(z.read(n)))
    DROP_IDS = set(os.path.basename(n)[:-5] for n in NAMES_ALL if n.startswith("Server/Drops/") and n.endswith(".json"))

def must(i):
    if i not in ITEM_IDS: raise SystemExit("unknown item id: " + i)
    return i

# ---- regions (spec 2.6 / 2.15): the 27 zone folders with a Discovery block, names from server.lang
assert len(DISC) == 27, sorted(DISC)
NAMED_XP = {"Zone1_Spawn": 250, "Zone1_Tier1": 500, "Zone1_Tier2": 1500, "Zone1_Tier3": 3000, "Oceans": 2000,
            "Zone2_Tier1": 5000, "Zone2_Tier2": 8000, "Zone2_Tier3": 12000, "Zone3_Tier1": 15000, "Zone3_Tier2": 22000,
            "Zone3_Tier3": 30000, "Zone4_Tier4": 45000, "Zone4_Tier5": 60000}
HIDDEN_XP = {1: 100, 2: 500, 3: 1500, 4: 4000}
GROUPS = [("Emerald_Wilds", "#8fe08a", 0), ("Howling_Sands", "#f0d060", 0), ("Oceans", "#7fd0ff", 0),
          ("Whisperfrost_Frontiers", "#bfe6ff", 1), ("Devastated_Lands", "#ff9a70", 1)]
GIDX = dict((g[0], i) for i, g in enumerate(GROUPS))
ZONE_IDS = ["Oceans", "Emerald_Wilds", "Howling_Sands", "Whisperfrost_Frontiers", "Devastated_Lands", "Void"]
ZONE_NAMES = [LANG["map.zone." + zid] for zid in ZONE_IDS]
REG = []
for rid, dj in DISC.items():
    zn = dj["ZoneName"]
    assert zn in GIDX, (rid, zn)
    shown = bool(dj.get("Display"))
    zm = re.match(r"Zone(\d)_", rid)
    znum = int(zm.group(1)) if zm else 0
    if shown:
        assert rid in NAMED_XP, rid
        xp = NAMED_XP[rid]
    else:
        assert znum in HIDDEN_XP, rid
        xp = HIDDEN_XP[znum]
    name = LANG["map.region." + rid]
    tm = re.search(r"_Tier(\d)$", rid)
    if not shown and tm:
        name = "%s - Tier %s" % (name, tm.group(1))
    REG.append(dict(id=rid, name=name, zone=LANG["map.zone." + zn], group=GIDX[zn], shown=shown, xp=xp))
REG.sort(key=lambda r: (r["group"], not r["shown"], r["id"]))
assert sum(1 for r in REG if r["shown"]) == 13
assert sum(r["xp"] for r in REG if r["shown"]) == 204250 and sum(r["xp"] for r in REG if not r["shown"]) == 26200
for g in range(len(GROUPS)):
    nm = [r["name"] for r in REG if r["group"] == g]
    assert len(nm) == len(set(nm)), nm
assert [sum(1 for r in REG if r["group"] == g) for g in range(5)] == [6, 5, 1, 9, 6]
NAMED_IDS = [r["id"] for r in REG if r["shown"]]

# ---- loot drop lists (spec 2.14 / 2.15): every spawner-table drop list + the two extra ones must exist; XP formula per id
EXTRA_DL = ["Drop_Goblin_Thief", "Trork_Camp_Chest"]
assert len(SPAWN_DL) == 46, len(SPAWN_DL)
DLS = sorted(SPAWN_DL) + EXTRA_DL
for dl in DLS:
    if dl not in DROP_IDS: raise SystemExit("drop list %s has no Server/Drops/**/%s.json" % (dl, dl))
ZM, TM, BASE, XDEF = [1, 2, 4, 8], [1, 1.5, 2, 3, 4], 400, 500
def chest_xp(dl):
    mz = re.match(r"Zone(\d)_.+_Tier(\d+)$", dl)
    if mz and 1 <= int(mz.group(1)) <= 4 and 1 <= int(mz.group(2)) <= 5:
        return int(round(BASE * ZM[int(mz.group(1)) - 1] * TM[int(mz.group(2)) - 1]))
    return XDEF
DL_XP = dict((dl, chest_xp(dl)) for dl in DLS)
assert DL_XP["Zone1_Goblin_Tier1"] == 400 and DL_XP["Zone4_Encounters_Tier4"] == 9600 and DL_XP["Portals_Oasis"] == 500
assert all(re.match(r"Zone\d_.+_Tier\d+$", dl) for dl in SPAWN_DL if dl != "Portals_Oasis")

# ---- titles (spec 2.8): id, name, kind (0 level, 1 zone, 2 chest, 3 chunk), number requirement, zone list, text
TITLES = [
    ("wanderer", "Wanderer", 0, 5, "", "Exploration 5"),
    ("pathfinder", "Pathfinder", 0, 10, "", "Exploration 10"),
    ("trailblazer", "Trailblazer", 0, 15, "", "Exploration 15"),
    ("wayfarer", "Wayfarer", 0, 20, "", "Exploration 20"),
    ("explorer", "Explorer", 0, 25, "", "Exploration 25"),
    ("voyager", "Voyager", 0, 30, "", "Exploration 30"),
    ("cartographer", "Cartographer", 0, 40, "", "Exploration 40"),
    ("pioneer", "Pioneer", 0, 50, "", "Exploration 50"),
    ("worldwalker", "Worldwalker", 0, 75, "", "Exploration 75"),
    ("echoseeker", "Echo Seeker", 0, 100, "", "Exploration 100"),
    ("wildswalker", "Wilds Walker", 1, 0, "Zone1_Spawn,Zone1_Tier1,Zone1_Tier2,Zone1_Tier3", "Discover the 4 Emerald Wilds regions"),
    ("sandstrider", "Sand Strider", 1, 0, "Zone2_Tier1,Zone2_Tier2,Zone2_Tier3", "Discover the 3 Howling Sands regions"),
    ("frostranger", "Frost Ranger", 1, 0, "Zone3_Tier1,Zone3_Tier2,Zone3_Tier3", "Discover the 3 Whisperfrost regions"),
    ("ashwalker", "Ash Walker", 1, 0, "Zone4_Tier4,Zone4_Tier5", "Discover the 2 Devastated Lands regions"),
    ("deepdiver", "Deep Diver", 1, 0, "Oceans", "Discover the Crystalline Depths"),
    ("worldseer", "World Seer", 1, 0, ",".join(NAMED_IDS), "Discover all 13 named regions"),
    ("treasurehunter", "Treasure Hunter", 2, 25, "", "Open 25 loot chests"),
    ("relicseeker", "Relic Seeker", 2, 100, "", "Open 100 loot chests"),
    ("hoarder", "Hoarder", 2, 250, "", "Open 250 loot chests"),
    ("roamer", "Roamer", 3, 1000, "", "Explore 1,000 chunks"),
    ("farstrider", "Far Strider", 3, 10000, "", "Explore 10,000 chunks"),
]
assert len(TITLES) == 21 and len(set(t[0] for t in TITLES)) == 21
for t in TITLES:
    assert re.match(r"^[a-z]+$", t[0]), t
    for r in (t[4].split(",") if t[4] else []): assert r in DISC, (t, r)
KIND_COLOR = ["#9fd0ff", "#9adf86", "#ffd27a", "#c8a0ff"]

# ---- page icons
CARD_ICON = [must(i) for i in ("Tool_Map", "Objective_Treasure_Map", "Furniture_Ancient_Chest_Small", "Deco_Map", "Rock_Gem_Ruby", "Deco_Scroll")]
CARD_HEAD = ["Exploration level", "Zones", "Loot chests", "Map", "Chest luck", "Title"]
CARD_COLOR = ["#e0a040", "#9adf86", "#ffd27a", "#c8a0ff", "#ff9a9a", "#9fd0ff"]

def jstr(xs): return "new String[] { " + ", ".join(json.dumps(x) for x in xs) + " }"
def jint(xs): return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }"
def jlong(xs): return "new long[] { " + ", ".join("%dL" % x for x in xs) + " }"
def jbool(xs): return "new boolean[] { " + ", ".join("true" if x else "false" for x in xs) + " }"

# ================= default config.properties (spec 2.14) =================
DL = ["# SkyyExploration %s - /exploreadmin reload re-reads this file (perm skyyexploration.admin). Comments on their own lines." % VERSION,
      "# Exploration XP goes to SkyySkills 0.4.1 (skill:fn:addxp). Every source pays once per profile. XP boosters never apply.",
      "# Worlds that never pay (instances, private islands): name prefixes and exact names, comma lists",
      "exploration.excludeWorldPrefixes=instance-,skyy-island-",
      "exploration.excludeWorlds=",
      "# Skyy's rule: nothing pays (and nothing is recorded) while flying or in creative. false/true turns that refusal off.",
      "noFlyingXp=true",
      "creativeXp=false",
      "# ---- loot chests: the first open of each world-generated loot chest (player-placed chests never count)",
      "# chests.enabled=false stops the XP / luck / coins of chest opens; loot chests are still recorded when they generate",
      "chests.enabled=true",
      "# XP = base x zoneMult[zone 1..4] x tierMult[tier 1..5] for Zone<Z>_<Faction>_Tier<T> drop lists; other drop lists pay xpDefault",
      "chests.base=400",
      "chests.zoneMult=1,2,4,8",
      "chests.tierMult=1,1.5,2,3,4",
      "chests.xpDefault=500",
      "# Override one chest type: remove the # in front of its line (the number shown is what the formula pays today)"]
for dl in DLS:
    DL.append("# chest.xp.%s=%d" % (dl, DL_XP[dl]))
DL += ["# How long the open check waits for the chest window (ms): first check next tick, then every pollMs until pollMaxMs",
       "chests.pollMs=100",
       "chests.pollMaxMs=2000",
       "# ---- chest luck: chance of ONE extra roll of the chest's drop list into your inventory (storage first)",
       "# chance = min(max, Exploration level x perLevel + the Treasure Sense tree node)",
       "luck.enabled=true",
       "luck.perLevel=0.003",
       "luck.max=0.5",
       "# Scavenger tree node: coins = coinsPerLevel x Exploration level (needs SkyyCoins)",
       "scav.coinsPerLevel=10",
       "# ---- map coverage: XP for every new chunk you walk into (per profile, per world; teleports count)",
       "chunks.enabled=true",
       "chunks.xp=60",
       "# multiplier by zone 1..4 of the region you stand in (oceans and hand-built worlds: 1)",
       "chunks.zoneMult=1,1.5,2,3",
       "# at most this many PAID chunks per world per profile (later chunks are still recorded, for titles)",
       "chunks.maxPaidPerWorld=25000",
       "chunks.payWhileGliding=true",
       "chunks.payWhileMounted=true",
       "# one aggregated chat line at most every feedbackMs (/explore quiet hides it)",
       "chunks.feedbackMs=30000",
       "# ---- zones: Hytale's own regions, the first time your profile enters each one",
       "zones.enabled=true",
       "# true = also show a title banner (the engine already shows its own banner once per account)",
       "zones.banner=false",
       "zone.xpDefault=1000"]
for r in REG:
    DL.append("# %s (%s)%s" % (r["name"], r["zone"], "" if r["shown"] else " - hidden region"))
    DL.append("zone.xp.%s=%d" % (r["id"], r["xp"]))
DL += ["# ---- titles: [Title] in front of your chat messages (chatPriority is read at server start only)",
       "titles.chatPrefix=true",
       "titles.chatPriority=30000",
       "# ---- how often XP waiting for SkyySkills is sent again (ms)",
       "bridge.retryMs=5000",
       "# display only (/explore card): SkyySkills' perk.exploration.staminaPerLevel - keep both the same",
       "display.staminaPerLevel=0.1"]
DEFAULTS = "\n".join(DL) + "\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)

# ================= classes =================
defs = pool.makeClass(PKG + ".ExpDefs")
cfg = pool.makeClass(PKG + ".ExpCfg")
dat = pool.makeClass(PKG + ".ExpData")
est = pool.makeClass(PKG + ".ExpState")
eio = pool.makeClass(PKG + ".ExpIO")
reg = pool.makeClass(PKG + ".ChestReg")
sto = pool.makeClass(PKG + ".ExpStore")
stk = pool.makeClass(PKG + ".SaveTask")
skl = pool.makeClass(PKG + ".ExpSkill")
exx = pool.makeClass(PKG + ".ExpXp")
ttl = pool.makeClass(PKG + ".ExpTitles")
awd = pool.makeClass(PKG + ".ExpAward")
ock = pool.makeClass(PKG + ".OpenCheck")
css = pool.makeClass(PKG + ".ChestSpawnSys", pool.get(T["RSYS"]))
csl = pool.makeClass(PKG + ".ChestSpawnLateSys", css)
cos = pool.makeClass(PKG + ".ChestOpenSys", pool.get(T["EES"]))
tick = pool.makeClass(PKG + ".ExpTick", pool.get(T["ETS"]))
svr = pool.makeClass(PKG + ".ExpSaver")
tfm = pool.makeClass(PKG + ".TitleFormatter")
cwr = pool.makeClass(PKG + ".ChatWrap")
chk = pool.makeClass(PKG + ".ChatHook")
sfn = pool.makeClass(PKG + ".ExpStatsFn")
tfn = pool.makeClass(PKG + ".ExpTitleFn")
page = pool.makeClass(PKG + ".ExplorePage", pool.get(T["PAGE"]))
qcmd = pool.makeClass(PKG + ".ExploreQuietCmd", pool.get(T["APC"]))
ecmd = pool.makeClass(PKG + ".ExploreCmd", pool.get(T["APC"]))
tset = pool.makeClass(PKG + ".TitleSetCmd", pool.get(T["APC"]))
tcmd = pool.makeClass(PKG + ".TitleCmd", pool.get(T["APC"]))
arl = pool.makeClass(PKG + ".ExAdminReloadCmd", pool.get(T["APC"]))
ast = pool.makeClass(PKG + ".ExAdminStatsCmd", pool.get(T["APC"]))
ars = pool.makeClass(PKG + ".ExAdminResetCmd", pool.get(T["APC"]))
acmd = pool.makeClass(PKG + ".ExploreAdminCmd", pool.get(T["APC"]))
pl = pool.makeClass(PKG + ".SkyyExplorationPlugin", pool.get(T["JP"]))

# ================= ExpDefs: generated tables + pure helpers =================
F(defs, "public static final String[] R_ID = %s;" % jstr([r["id"] for r in REG]))
F(defs, "public static final String[] R_NAME = %s;" % jstr([r["name"] for r in REG]))
F(defs, "public static final String[] R_ZONE = %s;" % jstr([r["zone"] for r in REG]))
F(defs, "public static final int[] R_GROUP = %s;" % jint([r["group"] for r in REG]))
F(defs, "public static final boolean[] R_SHOWN = %s;" % jbool([r["shown"] for r in REG]))
F(defs, "public static final int NR = %d;" % len(REG))
F(defs, "public static final int NAMED = 13;")
F(defs, "public static final String[] G_NAME = %s;" % jstr([LANG["map.zone." + g[0]] for g in GROUPS]))
F(defs, "public static final String[] G_COLOR = %s;" % jstr([g[1] for g in GROUPS]))
F(defs, "public static final int[] G_SIDE = %s;" % jint([g[2] for g in GROUPS]))
F(defs, "public static final String[] ZN_ID = %s;" % jstr(ZONE_IDS))
F(defs, "public static final String[] ZN_NAME = %s;" % jstr(ZONE_NAMES))
F(defs, "public static final String[] T_ID = %s;" % jstr([t[0] for t in TITLES]))
F(defs, "public static final String[] T_NAME = %s;" % jstr([t[1] for t in TITLES]))
F(defs, "public static final int[] T_KIND = %s;" % jint([t[2] for t in TITLES]))
F(defs, "public static final long[] T_REQ = %s;" % jlong([t[3] for t in TITLES]))
F(defs, "public static final String[] T_ZONES = %s;" % jstr([t[4] for t in TITLES]))
F(defs, "public static final String[] T_TEXT = %s;" % jstr([t[5] for t in TITLES]))
F(defs, "public static final int NT = %d;" % len(TITLES))
F(defs, "public static final String[] KIND_COLOR = %s;" % jstr(KIND_COLOR))
M(defs, r"""
public static int region(String r) {
  if (r == null) return -1;
  for (int i = 0; i < R_ID.length; i++) if (R_ID[i].equals(r)) return i;
  return -1;
}""")
M(defs, r"""
public static String regionName(String r) {
  int i = region(r);
  if (i >= 0) return R_NAME[i];
  return r == null ? "" : r.replace('_', ' ');
}""")
M(defs, r"""
public static String regionZone(String r) {
  int i = region(r);
  return i >= 0 ? R_ZONE[i] : "";
}""")
M(defs, r"""
public static String zoneName(String zid) {
  if (zid == null) return "";
  for (int i = 0; i < ZN_ID.length; i++) if (ZN_ID[i].equals(zid)) return ZN_NAME[i];
  return zid.replace('_', ' ');
}""")
# "Zone3_Tier1" / "Zone3_Kweebec_Tier2" -> 3; anything else 0
M(defs, r"""
public static int zoneNum(String id) {
  if (id == null || id.length() < 6 || !id.startsWith("Zone")) return 0;
  char c = id.charAt(4);
  if (c < '1' || c > '9' || id.charAt(5) != '_') return 0;
  return c - '0';
}""")
M(defs, r"""
public static int tierNum(String id) {
  if (id == null) return 0;
  int p = id.lastIndexOf("_Tier");
  if (p < 0) return 0;
  String s = id.substring(p + 5);
  if (s.length() == 0 || s.length() > 2) return 0;
  try { return Integer.parseInt(s); } catch (Throwable t) { return 0; }
}""")
M(defs, r"""
public static String dlLabel(String dl) {
  int z = zoneNum(dl);
  int t = tierNum(dl);
  if (z > 0 && t > 0) {
    int a = dl.indexOf('_');
    int b = dl.lastIndexOf("_Tier");
    String f = "";
    if (a > 0 && b > a) f = dl.substring(a + 1, b);
    if (f.length() == 0 || f.equals("Encounters")) f = "Treasure";
    return f.replace('_', ' ') + " chest tier " + t;
  }
  return "Loot chest";
}""")
M(defs, r"""
public static long pack(int x, int y, int z) {
  return (((long) x) & 0x3FFFFFFL) << 38 | (((long) z) & 0x3FFFFFFL) << 12 | (((long) y) & 0xFFFL);
}""")
M(defs, r"""
public static int title(String id) {
  if (id == null || id.length() == 0) return -1;
  for (int i = 0; i < T_ID.length; i++) if (T_ID[i].equals(id)) return i;
  return -1;
}""")
# /title argument, lower case without spaces / _ / - / '
M(defs, r"""
public static String normTitle(String s) {
  if (s == null) return "";
  String t = s.trim().toLowerCase();
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (c != ' ' && c != '_' && c != '-' && c != '\'') sb.append(c);
  }
  return sb.toString();
}""")
# /title argument: -3 = a prefix of more than one title, -2 = off/none, -1 = unknown, else the title index (id, name without spaces,
# 3+ letter id prefix that fits exactly one title; any case). "wor" / "worl" / "world" fit Worldwalker AND World Seer -> -3
M(defs, r"""
public static int resolveTitle(String s) {
  if (s == null) return -1;
  String t = normTitle(s);
  if (t.length() == 0) return -1;
  if (t.equals("off") || t.equals("none")) return -2;
  for (int i = 0; i < T_ID.length; i++) if (T_ID[i].equals(t)) return i;
  for (int i = 0; i < T_ID.length; i++) if (T_NAME[i].toLowerCase().replace(" ", "").equals(t)) return i;
  if (t.length() >= 3) {
    int hit = -1;
    for (int i = 0; i < T_ID.length; i++) {
      if (!T_ID[i].startsWith(t)) continue;
      if (hit >= 0) return -3;
      hit = i;
    }
    return hit;
  }
  return -1;
}""")
# names of the titles whose id starts with the argument (the /title "type more letters" hint)
M(defs, r"""
public static String titleMatches(String s) {
  String t = normTitle(s);
  StringBuilder sb = new StringBuilder();
  if (t.length() == 0) return "";
  for (int i = 0; i < T_ID.length; i++) {
    if (!T_ID[i].startsWith(t)) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(T_NAME[i]);
  }
  return sb.toString();
}""")
# compact number without commas: 950, 12.3k, 1.25m (Trees / Skills fmt)
M(defs, r"""
public static String fmt(long n) {
  if (n < 0L) return "-" + fmt(n == Long.MIN_VALUE ? Long.MAX_VALUE : -n);
  if (n < 10000L) return String.valueOf(n);
  if (n < 1000000L) { long t = n / 100L; return (t / 10L) + "." + (t % 10L) + "k"; }
  if (n < 1000000000L) { long h = n / 10000L; return (h / 100L) + "." + ((h % 100L) < 10L ? "0" : "") + (h % 100L) + "m"; }
  long g = n / 10000000L;
  return (g / 100L) + "." + ((g % 100L) < 10L ? "0" : "") + (g % 100L) + "b";
}""")
M(defs, r"""
public static String grp(long n) {
  boolean neg = n < 0L;
  String s = String.valueOf(neg ? (n == Long.MIN_VALUE ? Long.MAX_VALUE : -n) : n);
  StringBuilder sb = new StringBuilder();
  int len = s.length();
  for (int i = 0; i < len; i++) {
    if (i > 0 && (len - i) % 3 == 0) sb.append(',');
    sb.append(s.charAt(i));
  }
  return (neg ? "-" : "") + sb.toString();
}""")
M(defs, r"""
public static String num(double v) {
  long t = Math.round(v * 1000.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = -t;
  long w = t / 1000L;
  long f = t % 1000L;
  if (f == 0L) return sign + w;
  String fs = String.valueOf(f + 1000L).substring(1);
  while (fs.endsWith("0")) fs = fs.substring(0, fs.length() - 1);
  return sign + w + "." + fs;
}""")
M(defs, r"""
public static String pct(double f) {
  return num(f * 100.0) + "%";
}""")
# fallback item name when an item has no translation (chat only)
M(defs, r"""
public static String label(String id) {
  if (id == null) return "";
  String s = id;
  if (s.startsWith("Ingredient_Bar_")) s = s.substring(15) + " Bar";
  else if (s.startsWith("Ore_")) s = s.substring(4) + " Ore";
  else if (s.startsWith("Rock_Gem_")) s = s.substring(9);
  else if (s.startsWith("Ingredient_")) s = s.substring(11);
  else {
    int u = s.indexOf('_');
    if (u > 0 && u < s.length() - 1) s = s.substring(u + 1);
  }
  return s.replace('_', ' ');
}""")

# ================= ExpCfg: config.properties =================
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static @LOG@ LOG;")
F(cfg, "public static final String DEFAULTS = " + json.dumps(DEFAULTS) + ";")
F(cfg, "public static final java.util.concurrent.ConcurrentHashMap LASTWARN = new java.util.concurrent.ConcurrentHashMap();")
for decl in ('String[] EX_PREFIX = new String[] { "instance-", "skyy-island-" }', "String[] EX_WORLDS = new String[0]",
             "boolean NO_FLYING = true", "boolean CREATIVE_XP = false",
             "boolean CHESTS_ON = true", "long CHEST_BASE = 400L", "double[] CHEST_ZM = new double[] { 1.0, 2.0, 4.0, 8.0 }",
             "double[] CHEST_TM = new double[] { 1.0, 1.5, 2.0, 3.0, 4.0 }", "long CHEST_DEF = 500L", "long POLL_MS = 100L",
             "long POLL_MAX_MS = 2000L", "java.util.HashMap CHEST_XP = new java.util.HashMap()",
             "boolean LUCK_ON = true", "double LUCK_PER = 0.003", "double LUCK_MAX = 0.5", "long SCAV_PER = 10L",
             "boolean CHUNKS_ON = true", "long CHUNK_XP = 60L", "double[] CHUNK_ZM = new double[] { 1.0, 1.5, 2.0, 3.0 }",
             "long CHUNK_CAP = 25000L", "boolean PAY_GLIDE = true", "boolean PAY_MOUNT = true", "long FEEDBACK_MS = 30000L",
             "boolean ZONES_ON = true", "boolean BANNER = false", "long ZONE_DEF = 1000L", "java.util.HashMap ZONE_XP = new java.util.HashMap()",
             "boolean CHAT_PREFIX = true", "int CHAT_PRIORITY = 30000", "long RETRY_MS = 5000L", "double STA_PER = 0.1"):
    F(cfg, "public static volatile %s;" % decl)
M(cfg, r"""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyExploration] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyExploration] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void debug(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.FINE).log("[SkyyExploration] " + m); } catch (Throwable t) { }
}""")
# at most one line per key per ms
M(cfg, r"""
public static void warnEvery(String key, long ms, String m) {
  long now = System.currentTimeMillis();
  Object o = LASTWARN.get(key);
  if (o != null && now - ((Long) o).longValue() < ms) return;
  LASTWARN.put(key, Long.valueOf(now));
  warn(m);
}""")
M(cfg, r"""
public static String str(java.util.Properties p, String k, String d) {
  String v = p.getProperty(k);
  return v == null ? d : v.trim();
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static double dbl(java.util.Properties p, String k, double d) {
  try {
    String v = p.getProperty(k);
    if (v == null) return d;
    double x = Double.parseDouble(v.trim());
    return (Double.isNaN(x) || Double.isInfinite(x)) ? d : x;
  } catch (Throwable t) { return d; }
}""")
M(cfg, r"""
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim();
  if (v.equalsIgnoreCase("true")) return true;
  if (v.equalsIgnoreCase("false")) return false;
  return d;
}""")
M(cfg, r"""
public static long clampL(long v, long lo, long hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}""")
M(cfg, r"""
public static double clampD(double v, double lo, double hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}""")
M(cfg, r"""
public static String[] split(String v) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (v != null) {
    String[] xs = v.split(",");
    for (int i = 0; i < xs.length; i++) { String x = xs[i].trim(); if (x.length() > 0) out.add(x); }
  }
  String[] r = new String[out.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) out.get(i);
  return r;
}""")
M(cfg, r"""
public static double[] dlist(String v, double[] def, String key) {
  String[] xs = split(v);
  if (xs.length != def.length) { warn(key + " needs " + def.length + " numbers - using the default"); return def; }
  double[] r = new double[xs.length];
  try {
    for (int i = 0; i < xs.length; i++) {
      r[i] = Double.parseDouble(xs[i]);
      if (Double.isNaN(r[i]) || r[i] < 0.0 || r[i] > 1000.0) { warn(key + " numbers must be 0..1000 - using the default"); return def; }
    }
  } catch (Throwable t) { warn(key + " is not a number list - using the default"); return def; }
  return r;
}""")
M(cfg, r"""
public static void apply(java.util.Properties p) {
  EX_PREFIX = split(str(p, "exploration.excludeWorldPrefixes", "instance-,skyy-island-"));
  EX_WORLDS = split(str(p, "exploration.excludeWorlds", ""));
  NO_FLYING = bool(p, "noFlyingXp", true);
  CREATIVE_XP = bool(p, "creativeXp", false);
  CHESTS_ON = bool(p, "chests.enabled", true);
  CHEST_BASE = clampL(lng(p, "chests.base", 400L), 0L, 100000L);
  CHEST_ZM = dlist(str(p, "chests.zoneMult", "1,2,4,8"), new double[] { 1.0, 2.0, 4.0, 8.0 }, "chests.zoneMult");
  CHEST_TM = dlist(str(p, "chests.tierMult", "1,1.5,2,3,4"), new double[] { 1.0, 1.5, 2.0, 3.0, 4.0 }, "chests.tierMult");
  CHEST_DEF = clampL(lng(p, "chests.xpDefault", 500L), 0L, 400000L);
  POLL_MS = clampL(lng(p, "chests.pollMs", 100L), 20L, 5000L);
  POLL_MAX_MS = clampL(lng(p, "chests.pollMaxMs", 2000L), 100L, 30000L);
  LUCK_ON = bool(p, "luck.enabled", true);
  LUCK_PER = clampD(dbl(p, "luck.perLevel", 0.003), 0.0, 1.0);
  LUCK_MAX = clampD(dbl(p, "luck.max", 0.5), 0.0, 1.0);
  SCAV_PER = clampL(lng(p, "scav.coinsPerLevel", 10L), 0L, 1000000L);
  CHUNKS_ON = bool(p, "chunks.enabled", true);
  CHUNK_XP = clampL(lng(p, "chunks.xp", 60L), 0L, 100000L);
  CHUNK_ZM = dlist(str(p, "chunks.zoneMult", "1,1.5,2,3"), new double[] { 1.0, 1.5, 2.0, 3.0 }, "chunks.zoneMult");
  CHUNK_CAP = clampL(lng(p, "chunks.maxPaidPerWorld", 25000L), 0L, 100000000L);
  PAY_GLIDE = bool(p, "chunks.payWhileGliding", true);
  PAY_MOUNT = bool(p, "chunks.payWhileMounted", true);
  FEEDBACK_MS = clampL(lng(p, "chunks.feedbackMs", 30000L), 1000L, 3600000L);
  ZONES_ON = bool(p, "zones.enabled", true);
  BANNER = bool(p, "zones.banner", false);
  ZONE_DEF = clampL(lng(p, "zone.xpDefault", 1000L), 0L, 400000L);
  CHAT_PREFIX = bool(p, "titles.chatPrefix", true);
  CHAT_PRIORITY = (int) clampL(lng(p, "titles.chatPriority", 30000L), -32768L, 32767L);
  RETRY_MS = clampL(lng(p, "bridge.retryMs", 5000L), 1000L, 600000L);
  STA_PER = clampD(dbl(p, "display.staminaPerLevel", 0.1), 0.0, 1000.0);
  java.util.HashMap cx = new java.util.HashMap();
  java.util.HashMap zx = new java.util.HashMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("chest.xp.") && k.length() > 9) {
      long v = lng(p, k, -1L);
      if (v >= 0L) cx.put(k.substring(9), Long.valueOf(clampL(v, 0L, 400000L)));
      else warn(k + " is not a number - ignored");
    } else if (k.startsWith("zone.xp.") && k.length() > 8) {
      long v = lng(p, k, -1L);
      if (v >= 0L) zx.put(k.substring(8), Long.valueOf(clampL(v, 0L, 400000L)));
      else warn(k + " is not a number - ignored");
    }
  }
  CHEST_XP = cx;
  ZONE_XP = zx;
}""")
M(cfg, r"""
public static synchronized String load() {
  java.util.Properties p = new java.util.Properties();
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
      info("wrote default " + FILE);
    }
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  } catch (Throwable t) { warn("could not read config.properties (built-in defaults used): " + t); }
  apply(p);
  return "chests " + (CHESTS_ON ? "on" : "off") + ", luck " + (LUCK_ON ? "on" : "off") + ", chunks " + (CHUNKS_ON ? "on" : "off") + ", zones " + (ZONES_ON ? "on" : "off") + ", " + CHEST_XP.size() + " chest / " + ZONE_XP.size() + " zone XP lines";
}""")
M(cfg, r"""
public static boolean excluded(String wn) {
  if (wn == null) return true;
  String l = wn.toLowerCase();
  String[] px = EX_PREFIX;
  for (int i = 0; i < px.length; i++) if (px[i].length() > 0 && l.startsWith(px[i].toLowerCase())) return true;
  String[] ex = EX_WORLDS;
  for (int i = 0; i < ex.length; i++) if (ex[i].equalsIgnoreCase(wn)) return true;
  return false;
}""")
M(cfg, r"""
public static long chestXp(String dl) {
  if (dl == null) return CHEST_DEF;
  Object o = CHEST_XP.get(dl);
  if (o instanceof Long) return ((Long) o).longValue();
  int z = @PKG@.ExpDefs.zoneNum(dl);
  int t = @PKG@.ExpDefs.tierNum(dl);
  double[] zm = CHEST_ZM;
  double[] tm = CHEST_TM;
  if (z >= 1 && z <= zm.length && t >= 1 && t <= tm.length) return clampL(Math.round((double) CHEST_BASE * zm[z - 1] * tm[t - 1]), 0L, 400000L);
  return CHEST_DEF;
}""")
M(cfg, r"""
public static long zoneXp(String r) {
  if (r == null) return 0L;
  Object o = ZONE_XP.get(r);
  if (o instanceof Long) return ((Long) o).longValue();
  return ZONE_DEF;
}""")
M(cfg, r"""
public static double chunkMult(String region) {
  int z = @PKG@.ExpDefs.zoneNum(region);
  double[] m = CHUNK_ZM;
  if (z >= 1 && z <= m.length) return m[z - 1];
  return 1.0;
}""")

# ================= ExpData: one profile's exploration record =================
F(dat, "public String key;")
F(dat, "public String name;")
F(dat, "public boolean bad;")
F(dat, "public boolean quiet;")
F(dat, 'public String title = "";')
# counters: written only inside the synchronized ExpStore mutators (on the owner's world thread), read without the lock for display
# (/exploreadmin stats reads every online player's record from the admin's world thread; ExpSaver.retain reads touched on the
# scheduler) - volatile gives those readers the latest value (JMM visibility, no torn longs); no compound update runs outside the lock
F(dat, "public volatile long owed;")
F(dat, "public volatile long earned;")
F(dat, "public volatile long chests;")
F(dat, "public volatile long luck;")
F(dat, "public volatile long total;")
F(dat, "public volatile long touched;")
F(dat, "public boolean noLoad;")
F(dat, "public java.util.concurrent.ConcurrentHashMap zones = new java.util.concurrent.ConcurrentHashMap();")    # region -> TRUE
F(dat, "public java.util.concurrent.ConcurrentHashMap opened = new java.util.concurrent.ConcurrentHashMap();")   # worldFile -> LongOpenHashSet
F(dat, "public java.util.concurrent.ConcurrentHashMap chunks = new java.util.concurrent.ConcurrentHashMap();")   # worldFile -> LongOpenHashSet (lazy)
F(dat, "public java.util.concurrent.ConcurrentHashMap paid = new java.util.concurrent.ConcurrentHashMap();")     # worldFile -> long[1]
C(dat, "public ExpData() { }")

# ================= ExpState: per-player tick state (memory only, the player's world thread) =================
for decl in ("double acc", "boolean hasLast", "long lastChunk", "String lastWf", "long pendXp", "long pendN", "long pendStart",
             "boolean pendCapped", "long lastFlush"):
    F(est, "public %s;" % decl)
C(est, "public ExpState() { }")

# ================= ExpIO: bridge, profile key, ordered append queue =================
F(eio, "public static final java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();")
F(eio, "public static final java.util.ArrayList RETRY = new java.util.ArrayList();")
M(eio, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# the contract's helper, verbatim (tools/PROFILES-CONTRACT.md)
M(eio, r"""
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
M(eio, r"""
public static boolean busy(java.util.UUID u) {
  try { return bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return false; }
}""")
M(eio, r"""
public static java.util.function.Function fn(String key) {
  try {
    Object o = bridge().get(key);
    if (o instanceof java.util.function.Function) return (java.util.function.Function) o;
  } catch (Throwable t) { }
  return null;
}""")
M(eio, r"""
public static byte[] utf8(String s) {
  return s.getBytes(java.nio.charset.StandardCharsets.UTF_8);
}""")
# op 0 = append bytes, 1 = delete the file, 2 = delete every file in the directory; e[3] = attempts
M(eio, r"""
public static void append(java.nio.file.Path p, byte[] b) {
  Q.add(new Object[] { Integer.valueOf(0), p, b, Integer.valueOf(0) });
}""")
M(eio, r"""
public static void deleteLater(java.nio.file.Path p) {
  Q.add(new Object[] { Integer.valueOf(1), p, null, Integer.valueOf(0) });
}""")
M(eio, r"""
public static void clearDirLater(java.nio.file.Path p) {
  Q.add(new Object[] { Integer.valueOf(2), p, null, Integer.valueOf(0) });
}""")
M(eio, r"""
public static boolean writeAppend(java.nio.file.Path p, byte[] b) {
  try {
    java.nio.file.Files.createDirectories(p.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(p, b, new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
    return true;
  } catch (Throwable t) {
    @PKG@.ExpCfg.warnEvery("append", 60000L, "could not append to " + p + " (retried): " + t);
    return false;
  }
}""")
M(eio, r"""
public static void clearDir(java.nio.file.Path d) {
  try {
    if (!java.nio.file.Files.isDirectory(d, new java.nio.file.LinkOption[0])) return;
    java.util.stream.Stream s = java.nio.file.Files.list(d);
    java.util.List l = null;
    try { l = (java.util.List) s.collect(java.util.stream.Collectors.toList()); } finally { s.close(); }
    for (int i = 0; i < l.size(); i++) {
      java.nio.file.Path f = (java.nio.file.Path) l.get(i);
      if (java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) java.nio.file.Files.deleteIfExists(f);
    }
  } catch (Throwable t) { @PKG@.ExpCfg.warn("could not clear " + d + ": " + t); }
}""")
M(eio, r"""
public static void requeue(java.util.ArrayList items) {
  for (int i = 0; i < items.size(); i++) {
    Object[] e = (Object[]) items.get(i);
    int n = ((Integer) e[3]).intValue() + 1;
    if (n > 30) { @PKG@.ExpCfg.warnEvery("dropappend", 60000L, "gave up appending to " + e[1] + " after 30 tries"); continue; }
    e[3] = Integer.valueOf(n);
    RETRY.add(e);
  }
}""")
# the ONLY writer of every append-only file (ExpSaver every 2 s + shutdown); consecutive appends to one file are merged, order kept
M(eio, r"""
public static synchronized void drain() {
  java.util.ArrayList work = new java.util.ArrayList();
  for (int i = 0; i < RETRY.size(); i++) work.add(RETRY.get(i));
  RETRY.clear();
  Object o = Q.poll();
  while (o != null) { work.add(o); o = Q.poll(); }
  if (work.isEmpty()) return;
  java.nio.file.Path cur = null;
  java.io.ByteArrayOutputStream buf = null;
  java.util.ArrayList items = new java.util.ArrayList();
  for (int i = 0; i < work.size(); i++) {
    Object[] e = (Object[]) work.get(i);
    int op = ((Integer) e[0]).intValue();
    java.nio.file.Path p = (java.nio.file.Path) e[1];
    byte[] b = null;
    if (op == 0) b = (byte[]) e[2];
    if (op == 0 && cur != null && p.equals(cur)) { buf.write(b, 0, b.length); items.add(e); continue; }
    if (cur != null) {
      if (!writeAppend(cur, buf.toByteArray())) requeue(items);
      cur = null;
      buf = null;
      items = new java.util.ArrayList();
    }
    if (op == 0) {
      cur = p;
      buf = new java.io.ByteArrayOutputStream();
      buf.write(b, 0, b.length);
      items.add(e);
    } else if (op == 1) {
      try { java.nio.file.Files.deleteIfExists(p); } catch (Throwable t) { @PKG@.ExpCfg.warn("could not delete " + p + ": " + t); }
    } else {
      clearDir(p);
    }
  }
  if (cur != null && !writeAppend(cur, buf.toByteArray())) requeue(items);
}""")
M(eio, r"""
public static java.util.Properties readProps(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  return p;
}""")
M(eio, r"""
public static void moveRetry(java.nio.file.Path from, java.nio.file.Path to) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")

# ================= ChestReg: the per-world loot chest registry (NOT per profile) =================
F(reg, "public static java.nio.file.Path DIR;")
F(reg, "public static final java.util.concurrent.ConcurrentHashMap W = new java.util.concurrent.ConcurrentHashMap();")      # wf -> CHM Long -> "dl|placedBy"
F(reg, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")  # wf -> world name
F(reg, "public static final java.util.concurrent.ConcurrentHashMap WF = new java.util.concurrent.ConcurrentHashMap();")     # world name -> wf
F(reg, "public static final java.util.concurrent.ConcurrentHashMap CAPT = new java.util.concurrent.ConcurrentHashMap();")   # wf -> AtomicLong
F(reg, "public static final java.util.concurrent.ConcurrentHashMap FILES = new java.util.concurrent.ConcurrentHashMap();")  # wf -> TRUE (header written)
F(reg, "public static volatile boolean LATE = false;")
F(reg, "public static volatile boolean ORDERED = false;")
F(reg, "public static boolean FAILED_ONCE = false;")
M(reg, r"""
public static String wf(String wn) {
  if (wn == null) return "null";
  Object c = WF.get(wn);
  if (c != null) return (String) c;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < wn.length(); i++) {
    char ch = wn.charAt(i);
    boolean ok = (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '.' || ch == '-';
    if (ok) sb.append(ch); else sb.append('-');
  }
  String r = sb.toString() + "-" + Integer.toHexString(wn.hashCode());
  WF.put(wn, r);
  return r;
}""")
M(reg, r"""
public static java.util.concurrent.ConcurrentHashMap map(String wf) {
  Object o = W.get(wf);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = W.putIfAbsent(wf, n);
  return prev != null ? (java.util.concurrent.ConcurrentHashMap) prev : n;
}""")
M(reg, r"""
public static java.nio.file.Path file(String wf) {
  return DIR.resolve(wf + ".log");
}""")
M(reg, r"""
public static void counted(String wf) {
  Object o = CAPT.get(wf);
  if (o == null) {
    java.util.concurrent.atomic.AtomicLong n = new java.util.concurrent.atomic.AtomicLong();
    Object prev = CAPT.putIfAbsent(wf, n);
    o = prev != null ? prev : n;
  }
  ((java.util.concurrent.atomic.AtomicLong) o).incrementAndGet();
}""")
M(reg, r"""
public static long captured(String wf) {
  Object o = CAPT.get(wf);
  return o == null ? 0L : ((java.util.concurrent.atomic.AtomicLong) o).get();
}""")
# capture thread (world thread, inside a system): memory + queued journal line only, never file I/O
M(reg, r"""
public static void put(String wn, String wf, int x, int y, int z, String dl, String pb) {
  java.util.concurrent.ConcurrentHashMap m = map(wf);
  String v = dl + "|" + pb;
  Object prev = m.put(Long.valueOf(@PKG@.ExpDefs.pack(x, y, z)), v);
  if (v.equals(prev)) return;
  counted(wf);
  if (NAMES.putIfAbsent(wf, wn) == null && FILES.putIfAbsent(wf, Boolean.TRUE) == null) @PKG@.ExpIO.append(file(wf), @PKG@.ExpIO.utf8("# world " + wn + "\n"));
  @PKG@.ExpIO.append(file(wf), @PKG@.ExpIO.utf8("A " + x + " " + y + " " + z + " " + dl + " " + pb + "\n"));
}""")
M(reg, r"""
public static boolean remove(String wf, int x, int y, int z) {
  Object o = W.get(wf);
  if (o == null) return false;
  Object prev = ((java.util.concurrent.ConcurrentHashMap) o).remove(Long.valueOf(@PKG@.ExpDefs.pack(x, y, z)));
  if (prev == null) return false;
  @PKG@.ExpIO.append(file(wf), @PKG@.ExpIO.utf8("R " + x + " " + y + " " + z + "\n"));
  return true;
}""")
M(reg, r"""
public static String get(String wf, int x, int y, int z) {
  Object o = W.get(wf);
  if (o == null) return null;
  Object v = ((java.util.concurrent.ConcurrentHashMap) o).get(Long.valueOf(@PKG@.ExpDefs.pack(x, y, z)));
  return v == null ? null : (String) v;
}""")
M(reg, r"""
public static int size(String wf) {
  Object o = W.get(wf);
  return o == null ? 0 : ((java.util.concurrent.ConcurrentHashMap) o).size();
}""")
# world position of a block entity: exactly StashPlugin.stash offsets 82-165 (section ref -> ChunkSection, index -> local x/y/z)
M(reg, r"""
public static int[] posOf(@CAC@ acc, @BSI@ info) {
  if (info == null) return null;
  @REF@ sr = info.getSectionRef();
  if (sr == null || !sr.isValid()) return null;
  @CSEC@ cs = (@CSEC@) acc.getComponent(sr, @CSEC@.getComponentType());
  if (cs == null) return null;
  int idx = info.getIndex();
  int[] r = new int[3];
  r[0] = @CHU@.worldCoordFromLocalCoord(cs.getX(), @CHU@.xFromIndex(idx));
  r[1] = @CHU@.worldCoordFromLocalCoord(cs.getY(), @CHU@.yFromIndex(idx));
  r[2] = @CHU@.worldCoordFromLocalCoord(cs.getZ(), @CHU@.zFromIndex(idx));
  return r;
}""")
# multi-block origin (StashCommand.getItemContainerBlock offsets 120-226); null = no filler / not loaded. World thread.
M(reg, r"""
public static int[] origin(@WLD@ w, int x, int y, int z) {
  try {
    @CHS@ cs = w.getChunkStore();
    if (cs == null) return null;
    @REF@ sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return null;
    @BSEC@ bs = (@BSEC@) cs.getStore().getComponent(sr, @BSEC@.getComponentType());
    if (bs == null) return null;
    int f = bs.getFiller(x, y, z);
    if (f == 0) return null;
    return new int[] { x - @FBU@.unpackX(f), y - @FBU@.unpackY(f), z - @FBU@.unpackZ(f) };
  } catch (Throwable t) { return null; }
}""")
# the registered origin for a used / open block position, or null
M(reg, r"""
public static int[] find(@WLD@ w, String wf, int x, int y, int z) {
  if (size(wf) == 0) return null;
  if (get(wf, x, y, z) != null) return new int[] { x, y, z };
  int[] o = origin(w, x, y, z);
  if (o != null && get(wf, o[0], o[1], o[2]) != null) return o;
  return null;
}""")
# UUID string of the player who placed the block entity at that spot, or null (world thread)
M(reg, r"""
public static String placedByAt(@WLD@ w, int x, int y, int z) {
  try {
    @REF@ be = @BMOD@.getBlockEntity(w, x, y, z);
    if (be == null || !be.isValid()) return null;
    @PBI@ c = (@PBI@) be.getStore().getComponent(be, @PBI@.getComponentType());
    if (c == null || c.getWhoPlacedUuid() == null) return null;
    return c.getWhoPlacedUuid().toString();
  } catch (Throwable t) { return null; }
}""")
# atomic rewrite with only the live entries (setup only, before any capture can append)
M(reg, r"""
public static void compact(java.nio.file.Path f, String wn, java.util.concurrent.ConcurrentHashMap m, int oldLines) {
  try {
    StringBuilder sb = new StringBuilder();
    if (wn != null) sb.append("# world ").append(wn).append('\n');
    java.util.Iterator it = m.entrySet().iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      long k = ((Long) e.getKey()).longValue();
      int x = (int) (k >> 38);
      int z = (int) ((k << 26) >> 38);
      int y = (int) ((k << 52) >> 52);
      String v = (String) e.getValue();
      int bar = v.indexOf('|');
      sb.append("A ").append(x).append(' ').append(y).append(' ').append(z).append(' ').append(v.substring(0, bar)).append(' ').append(v.substring(bar + 1)).append('\n');
    }
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, @PKG@.ExpIO.utf8(sb.toString()), new java.nio.file.OpenOption[0]);
    @PKG@.ExpIO.moveRetry(tmp, f);
    @PKG@.ExpCfg.info("compacted " + f.getFileName() + ": " + oldLines + " lines -> " + m.size() + " loot chests");
  } catch (Throwable t) { @PKG@.ExpCfg.warn("could not compact " + f + " (kept as it is): " + t); }
}""")
M(reg, r"""
public static void loadOne(java.nio.file.Path f) {
  String fn = f.getFileName().toString();
  if (!fn.endsWith(".log")) return;
  String wf = fn.substring(0, fn.length() - 4);
  java.util.concurrent.ConcurrentHashMap m = map(wf);
  FILES.put(wf, Boolean.TRUE);
  java.util.List lines = null;
  try { lines = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8); }
  catch (Throwable t) { @PKG@.ExpCfg.warn("could not read loot chest registry " + f + " (its chests do not count until it reads): " + t); return; }
  String wn = null;
  for (int i = 0; i < lines.size(); i++) {
    String l = ((String) lines.get(i)).trim();
    if (l.length() == 0) continue;
    if (l.startsWith("# world ")) { wn = l.substring(8); continue; }
    if (l.startsWith("#")) continue;
    String[] p = l.split(" ");
    try {
      if (p[0].equals("A") && p.length >= 6) {
        m.put(Long.valueOf(@PKG@.ExpDefs.pack(Integer.parseInt(p[1]), Integer.parseInt(p[2]), Integer.parseInt(p[3]))), p[4] + "|" + p[5]);
      } else if (p[0].equals("R") && p.length >= 4) {
        m.remove(Long.valueOf(@PKG@.ExpDefs.pack(Integer.parseInt(p[1]), Integer.parseInt(p[2]), Integer.parseInt(p[3]))));
      }
    } catch (Throwable t) { }
  }
  if (wn != null) { NAMES.put(wf, wn); WF.put(wn, wf); }
  if (lines.size() > 2 * m.size() + 1000) compact(f, wn, m, lines.size());
}""")
M(reg, r"""
public static int loadAll() {
  int n = 0;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.util.stream.Stream s = java.nio.file.Files.list(DIR);
    java.util.List l = null;
    try { l = (java.util.List) s.collect(java.util.stream.Collectors.toList()); } finally { s.close(); }
    for (int i = 0; i < l.size(); i++) loadOne((java.nio.file.Path) l.get(i));
    java.util.Iterator it = W.values().iterator();
    while (it.hasNext()) n = n + ((java.util.concurrent.ConcurrentHashMap) it.next()).size();
  } catch (Throwable t) { @PKG@.ExpCfg.warn("could not list the loot chest registry " + DIR + ": " + t); }
  return n;
}""")

# ================= ExpStore: per-profile files (PROFILES-CONTRACT) =================
F(sto, "public static java.nio.file.Path DIR;")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap OWNER = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap FAILS = new java.util.concurrent.ConcurrentHashMap();")
F(sto, "public static final Object IO = new Object();")
M(sto, r"""
public static java.nio.file.Path propsFile(String k) {
  return DIR.resolve(k + ".properties");
}""")
M(sto, r"""
public static java.nio.file.Path chestsFile(String k) {
  return DIR.resolve(k).resolve("chests.txt");
}""")
M(sto, r"""
public static java.nio.file.Path chunksDir(String k) {
  return DIR.resolve(k).resolve("chunks");
}""")
M(sto, r"""
public static java.nio.file.Path chunkFile(String k, String wf) {
  return chunksDir(k).resolve(wf + ".bin");
}""")
M(sto, r"""
public static java.util.Properties readLocked(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p;
  synchronized (IO) { p = @PKG@.ExpIO.readProps(f); }
  return p;
}""")
M(sto, r"""
public static long num(java.util.Properties p, String k) {
  try { String v = p.getProperty(k); if (v == null) return 0L; long x = Long.parseLong(v.trim()); return x < 0L ? 0L : x; } catch (Throwable t) { return 0L; }
}""")
M(sto, r"""
public static @LOS@ setFor(java.util.concurrent.ConcurrentHashMap m, String wf) {
  Object o = m.get(wf);
  if (o != null) return (@LOS@) o;
  @LOS@ s = new @LOS@();
  m.put(wf, s);
  return s;
}""")
# world thread only (TreeStore rule): the properties file and chests.txt; chunk files are loaded lazily per world (chunkSet)
M(sto, r"""
public static @PKG@.ExpData readFile(String k) {
  @PKG@.ExpData d = new @PKG@.ExpData();
  d.key = k;
  try {
    java.nio.file.Path f = propsFile(k);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = readLocked(f);
      String nm = p.getProperty("name");
      if (nm != null && nm.trim().length() > 0) d.name = nm.trim();
      String t = p.getProperty("title");
      d.title = t == null ? "" : t.trim();
      d.quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
      d.owed = num(p, "owed");
      d.earned = num(p, "earned");
      d.luck = num(p, "luck");
      d.total = num(p, "total");
      String zs = p.getProperty("zones");
      if (zs != null) {
        String[] xs = zs.split(",");
        for (int i = 0; i < xs.length; i++) { String x = xs[i].trim(); if (x.length() > 0) d.zones.put(x, Boolean.TRUE); }
      }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String key = (String) it.next();
        if (key.startsWith("paid.") && key.length() > 5) { long[] a = new long[1]; a[0] = num(p, key); d.paid.put(key.substring(5), a); }
      }
    }
    java.nio.file.Path cf = chestsFile(k);
    long n = 0L;
    if (java.nio.file.Files.exists(cf, new java.nio.file.LinkOption[0])) {
      java.util.List lines = java.nio.file.Files.readAllLines(cf, java.nio.charset.StandardCharsets.UTF_8);
      for (int i = 0; i < lines.size(); i++) {
        String[] q = ((String) lines.get(i)).trim().split(" ");
        if (q.length < 4) continue;
        try {
          long pk = @PKG@.ExpDefs.pack(Integer.parseInt(q[1]), Integer.parseInt(q[2]), Integer.parseInt(q[3]));
          if (setFor(d.opened, q[0]).add(pk)) n++;
        } catch (Throwable t2) { }
      }
    }
    d.chests = n;
  } catch (Throwable t) {
    d = new @PKG@.ExpData();
    d.key = k;
    d.bad = true;
    @PKG@.ExpCfg.warn("could not read exploration file " + k + " - it is NOT overwritten and that profile earns nothing until it reads; fix or delete it, then run /exploreadmin reload: " + t);
  }
  return d;
}""")
M(sto, r"""
public static synchronized @PKG@.ExpData install(String k, java.util.UUID u, @PKG@.ExpData d) {
  @PKG@.ExpData cur = (@PKG@.ExpData) DATA.get(k);
  if (cur != null) return cur;
  OWNER.put(k, u);
  DATA.put(k, d);
  return d;
}""")
M(sto, r"""
public static @PKG@.ExpData dataK(String k, java.util.UUID u) {
  @PKG@.ExpData d = (@PKG@.ExpData) DATA.get(k);
  if (d == null) d = install(k, u, readFile(k));
  d.touched = System.currentTimeMillis();
  return d;
}""")
M(sto, r"""
public static @PKG@.ExpData data(java.util.UUID u) {
  return dataK(@PKG@.ExpIO.pkey(u), u);
}""")
M(sto, r"""
public static @PKG@.ExpData cached(String k) {
  return (@PKG@.ExpData) DATA.get(k);
}""")
M(sto, r"""
public static @LOS@ readChunks(String k, String wf) {
  try {
    java.nio.file.Path f = chunkFile(k, wf);
    @LOS@ s = new @LOS@();
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return s;
    byte[] b = java.nio.file.Files.readAllBytes(f);
    java.nio.ByteBuffer bb = java.nio.ByteBuffer.wrap(b);
    int n = b.length / 8;
    for (int i = 0; i < n; i++) s.add(bb.getLong(i * 8));
    return s;
  } catch (Throwable t) {
    @PKG@.ExpCfg.warnEvery("chunks|" + k + "|" + wf, 300000L, "could not read chunk file of " + k + " in " + wf + " (no map XP there until it reads, retried every 30 s): " + t);
    return null;
  }
}""")
M(sto, r"""
public static synchronized @LOS@ installChunks(@PKG@.ExpData d, String wf, @LOS@ s) {
  Object o = d.chunks.get(wf);
  if (o != null) return (@LOS@) o;
  d.chunks.put(wf, s);
  return s;
}""")
# the profile's chunk set for one world, read from disk the first time (world thread); null = unreadable right now
M(sto, r"""
public static @LOS@ chunkSet(@PKG@.ExpData d, String wf) {
  Object o = d.chunks.get(wf);
  if (o != null) return (@LOS@) o;
  if (d.bad) return null;
  String fk = d.key + "|" + wf;
  Object last = FAILS.get(fk);
  long now = System.currentTimeMillis();
  if (last != null && now - ((Long) last).longValue() < 30000L) return null;
  @LOS@ s = d.noLoad ? new @LOS@() : readChunks(d.key, wf);
  if (s == null) { FAILS.put(fk, Long.valueOf(now)); return null; }
  FAILS.remove(fk);
  return installChunks(d, wf, s);
}""")
M(sto, r"""
public static void dirty(String k) {
  DIRTY.put(k, Boolean.TRUE);
}""")
# ---- mutations (one lock for all profile records; snap() reads under the same lock)
M(sto, r"""
public static synchronized boolean addZone(@PKG@.ExpData d, String r, long xp) {
  if (d.bad || r == null || d.zones.containsKey(r)) return false;
  d.zones.put(r, Boolean.TRUE);
  if (xp > 0L) d.owed = d.owed + xp;
  dirty(d.key);
  return true;
}""")
M(sto, r"""
public static synchronized boolean hasZone(@PKG@.ExpData d, String r) {
  return r != null && d.zones.containsKey(r);
}""")
M(sto, r"""
public static synchronized int knownZones(@PKG@.ExpData d) {
  int n = 0;
  for (int i = 0; i < @PKG@.ExpDefs.NR; i++) if (d.zones.containsKey(@PKG@.ExpDefs.R_ID[i])) n++;
  return n;
}""")
M(sto, r"""
public static synchronized int namedZones(@PKG@.ExpData d) {
  int n = 0;
  for (int i = 0; i < @PKG@.ExpDefs.NR; i++) if (@PKG@.ExpDefs.R_SHOWN[i] && d.zones.containsKey(@PKG@.ExpDefs.R_ID[i])) n++;
  return n;
}""")
# -2 = no set loaded, -1 = already known, 0 = recorded without pay (world cap), > 0 = recorded and paid (added to owed)
M(sto, r"""
public static synchronized long addChunk(@PKG@.ExpData d, String wf, long ck, long xp) {
  if (d.bad) return -2L;
  Object o = d.chunks.get(wf);
  if (o == null) return -2L;
  @LOS@ s = (@LOS@) o;
  if (!s.add(ck)) return -1L;
  d.total = d.total + 1L;
  Object po = d.paid.get(wf);
  long[] pd = null;
  if (po == null) { pd = new long[1]; d.paid.put(wf, pd); } else pd = (long[]) po;
  long got = 0L;
  if (pd[0] < @PKG@.ExpCfg.CHUNK_CAP && xp > 0L) { pd[0] = pd[0] + 1L; got = xp; d.owed = d.owed + xp; }
  dirty(d.key);
  @PKG@.ExpIO.append(chunkFile(d.key, wf), java.nio.ByteBuffer.allocate(8).putLong(ck).array());
  return got;
}""")
M(sto, r"""
public static synchronized long hereCount(@PKG@.ExpData d, String wf) {
  if (wf == null) return -1L;
  Object o = d.chunks.get(wf);
  return o == null ? -1L : (long) ((@LOS@) o).size();
}""")
M(sto, r"""
public static synchronized long paidHere(@PKG@.ExpData d, String wf) {
  if (wf == null) return 0L;
  Object o = d.paid.get(wf);
  return o == null ? 0L : ((long[]) o)[0];
}""")
M(sto, r"""
public static synchronized boolean isOpened(@PKG@.ExpData d, String wf, int x, int y, int z) {
  Object o = d.opened.get(wf);
  return o != null && ((@LOS@) o).contains(@PKG@.ExpDefs.pack(x, y, z));
}""")
# records a first open; false = this profile already opened it
M(sto, r"""
public static synchronized boolean addChest(@PKG@.ExpData d, String wf, int x, int y, int z) {
  if (d.bad) return false;
  if (!setFor(d.opened, wf).add(@PKG@.ExpDefs.pack(x, y, z))) return false;
  d.chests = d.chests + 1L;
  dirty(d.key);
  @PKG@.ExpIO.append(chestsFile(d.key), @PKG@.ExpIO.utf8(wf + " " + x + " " + y + " " + z + "\n"));
  return true;
}""")
M(sto, r"""
public static synchronized void addOwed(@PKG@.ExpData d, long xp) {
  if (xp <= 0L || d.bad) return;
  d.owed = d.owed + xp;
  dirty(d.key);
}""")
M(sto, r"""
public static synchronized long owedPeek(@PKG@.ExpData d, long max) {
  return d.owed < max ? d.owed : max;
}""")
M(sto, r"""
public static synchronized void paidOut(@PKG@.ExpData d, long amt) {
  d.owed = d.owed - amt;
  if (d.owed < 0L) d.owed = 0L;
  d.earned = d.earned + amt;
  dirty(d.key);
}""")
M(sto, r"""
public static synchronized void addLuck(@PKG@.ExpData d) {
  d.luck = d.luck + 1L;
  dirty(d.key);
}""")
M(sto, r"""
public static synchronized void setTitle(@PKG@.ExpData d, String id) {
  d.title = id == null ? "" : id;
  dirty(d.key);
}""")
M(sto, r"""
public static synchronized boolean flipQuiet(@PKG@.ExpData d) {
  d.quiet = !d.quiet;
  dirty(d.key);
  return d.quiet;
}""")
M(sto, r"""
public static synchronized void setName(@PKG@.ExpData d, String n) {
  if (n != null && n.length() > 0) d.name = n;
}""")
# /exploreadmin resetme: the record of this profile (owed / earned XP stay: XP already paid to SkyySkills stays there)
M(sto, r"""
public static synchronized void reset(@PKG@.ExpData d) {
  d.zones = new java.util.concurrent.ConcurrentHashMap();
  d.opened = new java.util.concurrent.ConcurrentHashMap();
  d.chunks = new java.util.concurrent.ConcurrentHashMap();
  d.paid = new java.util.concurrent.ConcurrentHashMap();
  d.chests = 0L;
  d.luck = 0L;
  d.total = 0L;
  d.title = "";
  d.noLoad = true;
  dirty(d.key);
}""")
M(sto, r"""
public static synchronized java.util.Properties snap(String k) {
  @PKG@.ExpData d = (@PKG@.ExpData) DATA.get(k);
  if (d == null || d.bad) return null;
  java.util.Properties p = new java.util.Properties();
  if (d.name != null) p.setProperty("name", d.name);
  p.setProperty("v", "1");
  p.setProperty("title", d.title == null ? "" : d.title);
  p.setProperty("quiet", d.quiet ? "true" : "false");
  p.setProperty("owed", String.valueOf(d.owed));
  p.setProperty("earned", String.valueOf(d.earned));
  p.setProperty("chests", String.valueOf(d.chests));
  p.setProperty("luck", String.valueOf(d.luck));
  p.setProperty("total", String.valueOf(d.total));
  StringBuilder zs = new StringBuilder();
  java.util.Iterator it = d.zones.keySet().iterator();
  while (it.hasNext()) { if (zs.length() > 0) zs.append(','); zs.append((String) it.next()); }
  p.setProperty("zones", zs.toString());
  java.util.Iterator pi = d.paid.entrySet().iterator();
  while (pi.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) pi.next();
    p.setProperty("paid." + (String) e.getKey(), String.valueOf(((long[]) e.getValue())[0]));
  }
  return p;
}""")
M(sto, r"""
public static boolean saveNow(String k) {
  try {
    java.util.Properties p = snap(k);
    if (p == null) return true;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyExploration - one profile's exploration record (titles are derived, only the selected one is stored)"); } finally { out.close(); }
    @PKG@.ExpIO.moveRetry(tmp, propsFile(k));
    return true;
  } catch (Throwable t) {
    @PKG@.ExpCfg.warn("could not save exploration record " + k + " (kept dirty, retried on the next save): " + t);
    return false;
  }
}""")
M(sto, r"""
public static boolean save(String k) {
  boolean r;
  synchronized (IO) { r = saveNow(k); }
  return r;
}""")
M(sto, r"""
public static void flushDirty() {
  java.util.ArrayList failed = new java.util.ArrayList();
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    it.remove();
    if (!save(k)) failed.add(k);
  }
  for (int i = 0; i < failed.size(); i++) DIRTY.put(failed.get(i), Boolean.TRUE);
}""")
stk.addInterface(pool.get("java.lang.Runnable"))
F(stk, "public String key;")
C(stk, "public SaveTask(String k) { this.key = k; }")
M(stk, r"""
public void run() {
  try { @PKG@.ExpIO.drain(); } catch (Throwable t0) { }
  try {
    @PKG@.ExpStore.DIRTY.remove(this.key);
    if (!@PKG@.ExpStore.save(this.key)) @PKG@.ExpStore.dirty(this.key);
  } catch (Throwable t) { @PKG@.ExpStore.dirty(this.key); }
}""")
M(sto, r"""
public static void saveSoon(String k) {
  dirty(k);
  try { @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.SaveTask(k)); } catch (Throwable t) { }
}""")
# drop cached records of players offline for a minute with nothing waiting to be saved (their appends left the queue long ago)
M(sto, r"""
public static void retain() {
  long now = System.currentTimeMillis();
  java.util.Iterator it = DATA.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String k = (String) e.getKey();
    @PKG@.ExpData d = (@PKG@.ExpData) e.getValue();
    Object o = OWNER.get(k);
    if (!(o instanceof java.util.UUID) || DIRTY.containsKey(k)) continue;
    if (now - d.touched < 60000L) continue;
    if (@UNI@.get().getPlayer((java.util.UUID) o) != null) continue;
    it.remove();
    OWNER.remove(k);
  }
}""")
M(sto, r"""
public static int dropBad() {
  int n = 0;
  java.util.Iterator it = DATA.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (((@PKG@.ExpData) e.getValue()).bad) { it.remove(); n++; }
  }
  FAILS.clear();
  return n;
}""")

# ================= ExpSkill: what other Skyy mods answer (all optional) =================
M(skl, r"""
public static boolean hasSkills() {
  return @PKG@.ExpIO.fn("skill:fn:level") != null;
}""")
# -1 = SkyySkills not loaded; else the active profile's Exploration level (0 on SkyySkills 0.4, which has no Exploration row)
M(skl, r"""
public static int level(java.util.UUID u) {
  java.util.function.Function f = @PKG@.ExpIO.fn("skill:fn:level");
  if (f == null) return -1;
  try {
    Object r = f.apply(new Object[] { u, "Exploration" });
    if (r instanceof Number) { int l = ((Number) r).intValue(); return l < 0 ? 0 : l; }
  } catch (Throwable t) { }
  return 0;
}""")
M(skl, r"""
public static long xp(java.util.UUID u) {
  java.util.function.Function f = @PKG@.ExpIO.fn("skill:fn:xp");
  if (f == null) return 0L;
  try {
    Object r = f.apply(new Object[] { u, "Exploration" });
    if (r instanceof Number) { long x = ((Number) r).longValue(); return x < 0L ? 0L : x; }
  } catch (Throwable t) { }
  return 0L;
}""")
# SkyySkills 0.4.1+ lists Exploration in skill:<uuid> ("...,Cooking:3,Exploration:12,...")
M(skl, r"""
public static boolean hasRow(java.util.UUID u) {
  try {
    Object o = @PKG@.ExpIO.bridge().get("skill:" + u.toString());
    return o instanceof String && ((String) o).indexOf("Exploration:") >= 0;
  } catch (Throwable t) { return false; }
}""")
M(skl, r"""
public static double treeBonus(java.util.UUID u, String node) {
  java.util.function.Function f = @PKG@.ExpIO.fn("tree:fn:bonus");
  if (f == null) return 0.0;
  try {
    Object r = f.apply(new Object[] { u, node });
    if (r instanceof Number) {
      double v = ((Number) r).doubleValue();
      if (Double.isNaN(v) || v < 0.0) return 0.0;
      return v > 1.0 ? 1.0 : v;
    }
  } catch (Throwable t) { }
  return 0.0;
}""")
# {chance, level part, tree part}
M(skl, r"""
public static double[] luck(java.util.UUID u, int lvl) {
  double[] r = new double[3];
  r[1] = (lvl < 0 ? 0 : lvl) * @PKG@.ExpCfg.LUCK_PER;
  r[2] = treeBonus(u, "Exploration.ELuck");
  double c = r[1] + r[2];
  r[0] = c > @PKG@.ExpCfg.LUCK_MAX ? @PKG@.ExpCfg.LUCK_MAX : c;
  return r;
}""")
M(skl, r"""
public static String treeNames() {
  try { Object o = @PKG@.ExpIO.bridge().get("tree:names"); return o instanceof String ? (String) o : ""; } catch (Throwable t) { return ""; }
}""")
M(skl, r"""
public static boolean coins(java.util.UUID u, long amount) {
  java.util.function.Function f = @PKG@.ExpIO.fn("coins:fn:add");
  if (f == null || amount <= 0L) return false;
  try { return f.apply(new Object[] { u, Long.valueOf(amount) }) != null; } catch (Throwable t) { return false; }
}""")

# ================= ExpXp: the owed ledger -> skill:fn:addxp (no boosters: base XP only) =================
F(exx, "public static boolean TOLD_MISSING = false;")
F(exx, "public static boolean TOLD_REFUSED = false;")
M(exx, r"""
public static void flush(java.util.UUID u, String k, @PKG@.ExpData d) {
  if (d == null || d.bad || d.owed <= 0L) return;
  java.util.function.Function f = @PKG@.ExpIO.fn("skill:fn:addxp");
  if (f == null) {
    if (!TOLD_MISSING) { TOLD_MISSING = true; @PKG@.ExpCfg.warn("skill:fn:addxp is missing (SkyySkills not loaded) - Exploration XP is kept in each profile's owed ledger and sent later"); }
    return;
  }
  int guard = 0;
  while (guard < 4) {
    guard++;
    long amt = @PKG@.ExpStore.owedPeek(d, 500000L);
    if (amt <= 0L) return;
    Object ok = null;
    try { ok = f.apply(new Object[] { u, "Exploration", Long.valueOf(amt), "exploration", k }); } catch (Throwable t) { ok = null; }
    if (!Boolean.TRUE.equals(ok)) {
      if (!TOLD_REFUSED) { TOLD_REFUSED = true; @PKG@.ExpCfg.warn("SkyySkills refused Exploration XP (needs SkyySkills 0.4.1 with the Exploration row and exploration.enabled=true; or its per-minute bridge cap) - it waits in the owed ledger and is retried every " + @PKG@.ExpCfg.RETRY_MS + " ms"); }
      return;
    }
    @PKG@.ExpStore.paidOut(d, amt);
    @PKG@.ExpStore.saveSoon(k);
  }
}""")

# ================= ExpTitles: earned (derived), the selected title, chat map, bridge =================
F(ttl, "public static final java.util.concurrent.ConcurrentHashMap CHAT = new java.util.concurrent.ConcurrentHashMap();")       # UUID -> String[]{name, color}
F(ttl, "public static final java.util.concurrent.ConcurrentHashMap KNOWN = new java.util.concurrent.ConcurrentHashMap();")      # pkey -> Long earned mask (baseline)
F(ttl, "public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> summary string
M(ttl, r"""
public static void say(@PR@ pr, String text, String color) {
  try { pr.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")
M(ttl, r"""
public static boolean earned(@PKG@.ExpData d, int lvl, int i) {
  if (d == null || d.bad || i < 0 || i >= @PKG@.ExpDefs.NT) return false;
  int k = @PKG@.ExpDefs.T_KIND[i];
  long req = @PKG@.ExpDefs.T_REQ[i];
  if (k == 0) return (long) lvl >= req;
  if (k == 2) return d.chests >= req;
  if (k == 3) return d.total >= req;
  String[] zs = @PKG@.ExpDefs.T_ZONES[i].split(",");
  for (int j = 0; j < zs.length; j++) if (!d.zones.containsKey(zs[j])) return false;
  return zs.length > 0;
}""")
M(ttl, r"""
public static long mask(@PKG@.ExpData d, int lvl) {
  long m = 0L;
  for (int i = 0; i < @PKG@.ExpDefs.NT; i++) if (earned(d, lvl, i)) m = m | (1L << i);
  return m;
}""")
M(ttl, r"""
public static int count(@PKG@.ExpData d, int lvl) {
  return Long.bitCount(mask(d, lvl));
}""")
# the selected title while it is earned, else -1 (a title that is not earned acts as none)
M(ttl, r"""
public static int selected(@PKG@.ExpData d, int lvl) {
  if (d == null || d.bad) return -1;
  int i = @PKG@.ExpDefs.title(d.title);
  if (i < 0 || !earned(d, lvl, i)) return -1;
  return i;
}""")
# newly earned titles post one chat line each; the first mask seen for a profile key is a baseline
M(ttl, r"""
public static void check(@PR@ pr, String k, @PKG@.ExpData d, int lvl) {
  if (d == null || d.bad) return;
  long m = mask(d, lvl);
  Object prev = KNOWN.put(k, Long.valueOf(m));
  if (prev == null) return;
  long fresh = m & ~((Long) prev).longValue();
  if (fresh == 0L) return;
  for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
    if ((fresh & (1L << i)) == 0L) continue;
    say(pr, "New title unlocked: " + @PKG@.ExpDefs.T_NAME[i] + " - use it with /title " + @PKG@.ExpDefs.T_ID[i], @PKG@.ExpDefs.KIND_COLOR[@PKG@.ExpDefs.T_KIND[i]]);
  }
}""")
M(ttl, r"""
public static String summary(@PKG@.ExpData d, int lvl) {
  int sel = selected(d, lvl);
  return "level:" + lvl + ",zones:" + @PKG@.ExpStore.knownZones(d) + "/" + @PKG@.ExpDefs.NR + ",chests:" + d.chests + ",chunks:" + d.total + ",title:" + (sel < 0 ? "" : @PKG@.ExpDefs.T_ID[sel]);
}""")
# explore:<uuid>, explore:title:<uuid> and the chat map describe the ACTIVE profile (written only when they change)
M(ttl, r"""
public static void publish(java.util.UUID u, @PKG@.ExpData d, int lvl) {
  try {
    java.util.Map b = @PKG@.ExpIO.bridge();
    String us = u.toString();
    String s = summary(d, lvl);
    if (!s.equals(b.get("explore:" + us))) b.put("explore:" + us, s);
    int sel = selected(d, lvl);
    if (sel < 0) {
      CHAT.remove(u);
      b.remove("explore:title:" + us);
    } else {
      String nm = @PKG@.ExpDefs.T_NAME[sel];
      Object cur = CHAT.get(u);
      if (!(cur instanceof String[]) || !nm.equals(((String[]) cur)[0])) CHAT.put(u, new String[] { nm, @PKG@.ExpDefs.KIND_COLOR[@PKG@.ExpDefs.T_KIND[sel]] });
      if (!nm.equals(b.get("explore:title:" + us))) b.put("explore:title:" + us, nm);
    }
    PUBLISHED.put(u, s);
  } catch (Throwable t) { }
}""")
M(ttl, r"""
public static void clearOne(java.util.UUID u) {
  try {
    CHAT.remove(u);
    java.util.Map b = @PKG@.ExpIO.bridge();
    b.remove("explore:" + u.toString());
    b.remove("explore:title:" + u.toString());
  } catch (Throwable t) { }
}""")
M(ttl, r"""
public static void clearAll() {
  java.util.Iterator it = PUBLISHED.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    clearOne(u);
  }
  CHAT.clear();
}""")
# /title <x> and the Titles tab: -2 = none; world thread
M(ttl, r"""
public static String choose(@PR@ pr, int i) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.bad) return "Your exploration file could not be read - nothing can change until an admin fixes it";
  int lvl = @PKG@.ExpSkill.level(u);
  int lv = lvl < 0 ? 0 : lvl;
  if (i == -2) {
    @PKG@.ExpStore.setTitle(d, "");
    @PKG@.ExpStore.saveSoon(k);
    publish(u, d, lv);
    return "Title removed";
  }
  if (i < 0 || i >= @PKG@.ExpDefs.NT) return "Unknown title - /title shows the list";
  if (!earned(d, lv, i)) return @PKG@.ExpDefs.T_NAME[i] + " is locked - " + @PKG@.ExpDefs.T_TEXT[i];
  @PKG@.ExpStore.setTitle(d, @PKG@.ExpDefs.T_ID[i]);
  @PKG@.ExpStore.saveSoon(k);
  publish(u, d, lv);
  return "Your title is now " + @PKG@.ExpDefs.T_NAME[i] + " - it shows in front of your chat messages";
}""")

# ================= ExpAward: first open of a loot chest (world task, never inside a system iteration) =================
F(awd, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")
F(awd, "public static boolean FAILED_ONCE = false;")
M(awd, r"""
public static String pendKey(java.util.UUID u, String wf, int x, int y, int z) {
  return u.toString() + "|" + wf + "|" + x + "|" + y + "|" + z;
}""")
M(awd, r"""
public static boolean creative(@PLA@ p) {
  if (@PKG@.ExpCfg.CREATIVE_XP) return false;
  try { return p != null && p.getGameMode() == @GM@.Creative; } catch (Throwable t) { return false; }
}""")
M(awd, r"""
public static boolean flying(@ST@ st, @REF@ ref) {
  if (!@PKG@.ExpCfg.NO_FLYING) return false;
  try {
    @MSC@ msc = (@MSC@) st.getComponent(ref, @MSC@.getComponentType());
    if (msc == null) return false;
    @MVT@ ms = msc.getMovementStates();
    return ms != null && ms.flying;
  } catch (Throwable t) { return false; }
}""")
# the chest's window list holds the player's UUIDComponent uuid while the chest is open for them (OpenContainerInteraction)
M(awd, r"""
public static boolean windowOpen(@PR@ pr, @WLD@ w, int x, int y, int z) {
  @REF@ be = @BMOD@.getBlockEntity(w, x, y, z);
  if (be == null || !be.isValid()) return false;
  @ICB@ c = (@ICB@) be.getStore().getComponent(be, @ICB@.getComponentType());
  if (c == null) return false;
  java.util.Map m = c.getWindows();
  if (m == null || m.isEmpty()) return false;
  java.util.UUID wid = pr.getUuid();
  try {
    @REF@ r = pr.getReference();
    if (r != null && r.isValid()) {
      @UUC@ uc = (@UUC@) r.getStore().getComponent(r, @UUC@.getComponentType());
      if (uc != null && uc.getUuid() != null) wid = uc.getUuid();
    }
  } catch (Throwable t) { }
  return m.containsKey(wid) || m.containsKey(pr.getUuid());
}""")
M(awd, r"""
public static String itemName(@IS@ is) {
  return @PKG@.ExpDefs.label(is.getItemId());
}""")
# B2: one extra roll of the chest's drop list into the opener's inventory, storage first (never into the chest)
M(awd, r"""
public static void luck(@PR@ pr, @PLA@ p, @REF@ ref, @ST@ st, java.util.UUID u, @PKG@.ExpData d, String dl, int lvl) {
  if (!@PKG@.ExpCfg.LUCK_ON || dl == null) return;
  double[] c = @PKG@.ExpSkill.luck(u, lvl);
  if (c[0] <= 0.0) return;
  if (c[0] < 1.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c[0]) return;
  java.util.List drops = @IMOD@.get().getRandomItemDrops(dl);
  if (drops == null || drops.isEmpty()) return;
  java.util.ArrayList parts = new java.util.ArrayList();
  parts.add(@MSG@.raw("Chest luck! Extra roll:").color("#ffd27a"));
  int given = 0;
  for (int i = 0; i < drops.size(); i++) {
    Object o = drops.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ is = (@IS@) o;
    if (is.isEmpty() || is.getItemId() == null) continue;
    @SIC@.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), is);
    given++;
    if (given <= 3) {
      parts.add(@MSG@.raw(" +" + is.getQuantity() + " ").color("#ffd27a"));
      @MSG@ nm = null;
      try {
        @ITM@ it = (@ITM@) @ITM@.getAssetMap().getAsset(is.getItemId());
        if (it != null) nm = it.getTranslationMessage();
      } catch (Throwable t) { nm = null; }
      if (nm == null) nm = @MSG@.raw(itemName(is));
      parts.add(nm.color("#ffd27a"));
    }
  }
  if (given == 0) return;
  if (given > 3) parts.add(@MSG@.raw(" ...").color("#ffd27a"));
  @PKG@.ExpStore.addLuck(d);
  @MSG@[] arr = new @MSG@[parts.size()];
  for (int i = 0; i < arr.length; i++) arr[i] = (@MSG@) parts.get(i);
  try { pr.sendMessage(@MSG@.join(arr)); } catch (Throwable t) { }
}""")
# 2.4b Scavenger (SkyyTrees 0.2 node): coins = scav.coinsPerLevel x Exploration level
M(awd, r"""
public static void scav(@PR@ pr, java.util.UUID u, int lvl) {
  if (lvl <= 0 || @PKG@.ExpCfg.SCAV_PER <= 0L) return;
  double c = @PKG@.ExpSkill.treeBonus(u, "Exploration.EScav");
  if (c <= 0.0) return;
  if (c < 1.0 && java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
  long amt = @PKG@.ExpCfg.SCAV_PER * (long) lvl;
  if (@PKG@.ExpSkill.coins(u, amt)) @PKG@.ExpTitles.say(pr, "Scavenger! +" + @PKG@.ExpDefs.grp(amt) + " coins", "#ffe08a");
}""")
M(awd, r"""
public static void chestOpened(@PR@ pr, @WLD@ w, String wf, int x, int y, int z, String key) {
  if (!@PKG@.ExpCfg.CHESTS_ON || pr == null || w == null) return;
  java.util.UUID u = pr.getUuid();
  @REF@ ref = pr.getReference();
  if (ref == null || !ref.isValid()) return;
  @ST@ st = ref.getStore();
  Object ext = st.getExternalData();
  if (!(ext instanceof @EST@)) return;
  @WLD@ pw = ((@EST@) ext).getWorld();
  if (pw == null || !w.getName().equals(pw.getName())) return;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return;
  if (creative(p) || flying(st, ref) || @PKG@.ExpIO.busy(u)) return;
  String k = @PKG@.ExpIO.pkey(u);
  if (key != null && !key.equals(k)) return;
  String ent = @PKG@.ChestReg.get(wf, x, y, z);
  if (ent == null) return;
  int bar = ent.indexOf('|');
  String dl = bar < 0 ? ent : ent.substring(0, bar);
  String rec = bar < 0 ? "-" : ent.substring(bar + 1);
  String who = @PKG@.ChestReg.placedByAt(w, x, y, z);
  if (who != null && !who.equals(rec)) {
    @PKG@.ChestReg.remove(wf, x, y, z);
    @PKG@.ExpCfg.debug("placed-by guard: " + w.getName() + " " + x + " " + y + " " + z + " placed by " + who + ", recorded " + rec + " - record dropped");
    return;
  }
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.bad) return;
  if (!@PKG@.ExpStore.addChest(d, wf, x, y, z)) return;
  long xp = @PKG@.ExpCfg.chestXp(dl);
  @PKG@.ExpStore.addOwed(d, xp);
  @PKG@.ExpStore.saveSoon(k);
  @PKG@.ExpXp.flush(u, k, d);
  int lvl = @PKG@.ExpSkill.level(u);
  int lv = lvl < 0 ? 0 : lvl;
  try { luck(pr, p, ref, st, u, d, dl, lv); } catch (Throwable t) { @PKG@.ExpCfg.warnEvery("luck", 60000L, "chest luck roll failed: " + t); }
  try { scav(pr, u, lv); } catch (Throwable t) { }
  @PKG@.ExpTitles.say(pr, "[Exploration] Loot chest found - " + @PKG@.ExpDefs.dlLabel(dl) + " - +" + @PKG@.ExpDefs.grp(xp) + " Exploration XP (" + @PKG@.ExpDefs.grp(d.chests) + (d.chests == 1L ? " chest)" : " chests)"), "#ffd27a");
  @PKG@.ExpTitles.check(pr, k, d, lv);
  @PKG@.ExpTitles.publish(u, d, lv);
}""")

# ================= OpenCheck: did the window really open? (HarvestTask pattern) =================
ock.addInterface(pool.get("java.lang.Runnable"))
for decl in ("java.util.UUID u", "@WLD@ w", "String wf", "int x", "int y", "int z", "String key", "int tries", "int maxTries", "boolean hop"):
    F(ock, "public %s;" % decl)
C(ock, r"""
public OpenCheck(java.util.UUID u, @WLD@ w, String wf, int x, int y, int z, String key) {
  this.u = u; this.w = w; this.wf = wf; this.x = x; this.y = y; this.z = z; this.key = key;
  this.tries = 0; this.hop = false;
  long m = @PKG@.ExpCfg.POLL_MAX_MS / @PKG@.ExpCfg.POLL_MS;
  this.maxTries = (int) (m < 1L ? 1L : m);
}""")
M(ock, r"""
public void run() {
  String pk = @PKG@.ExpAward.pendKey(this.u, this.wf, this.x, this.y, this.z);
  if (this.hop) {
    this.hop = false;
    try { this.w.execute(this); } catch (Throwable t) { @PKG@.ExpAward.PENDING.remove(pk); }
    return;
  }
  try {
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) { @PKG@.ExpAward.PENDING.remove(pk); return; }
    if (@PKG@.ExpAward.windowOpen(pr, this.w, this.x, this.y, this.z)) {
      @PKG@.ExpAward.PENDING.remove(pk);
      @PKG@.ExpAward.chestOpened(pr, this.w, this.wf, this.x, this.y, this.z, this.key);
      return;
    }
    this.tries++;
    if (this.tries > this.maxTries) { @PKG@.ExpAward.PENDING.remove(pk); return; }
    this.hop = true;
    @HSV@.SCHEDULED_EXECUTOR.schedule(this, @PKG@.ExpCfg.POLL_MS, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) {
    @PKG@.ExpAward.PENDING.remove(pk);
    if (!@PKG@.ExpAward.FAILED_ONCE) { @PKG@.ExpAward.FAILED_ONCE = true; @PKG@.ExpCfg.warn("loot chest open check failed (logged once): " + t); }
  }
}""")
# one pending check per player + chest; the award itself is idempotent per profile
M(awd, r"""
public static void queue(java.util.UUID u, @WLD@ w, String wf, int x, int y, int z, String key) {
  String pk = pendKey(u, wf, x, y, z);
  long now = System.currentTimeMillis();
  Object prev = PENDING.putIfAbsent(pk, Long.valueOf(now));
  if (prev != null) {
    if (prev instanceof Long && now - ((Long) prev).longValue() < 10000L) return;
    PENDING.put(pk, Long.valueOf(now));
  }
  try { w.execute(new @PKG@.OpenCheck(u, w, wf, x, y, z, key)); } catch (Throwable t) { PENDING.remove(pk); }
}""")

# ================= ChestSpawnSys / ChestSpawnLateSys: capture loot chests when their block entity is added =================
F(css, "public @QRY@ query;")
F(css, "public java.util.Set deps;")
F(css, "public static Class STASH;")
F(css, "public static boolean FAILED_ONCE = false;")
C(css, r"""
public ChestSpawnSys(boolean ordered) {
  super();
  this.query = @QRY@.and(new @QRY@[] { (@QRY@) @ICB@.getComponentType(), (@QRY@) @BSI@.getComponentType() });
  this.deps = new java.util.HashSet();
  if (ordered && STASH != null) this.deps.add(new @SDEP@(@ORD@.BEFORE, STASH));
}""")
C(css, "public ChestSpawnSys() { this(true); }")
M(css, r"""
public @QRY@ getQuery() {
  return this.query;
}""")
M(css, r"""
public java.util.Set getDependencies() {
  return this.deps;
}""")
M(css, r"""
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ store, @CB@ cb) {
  try {
    Object ext = store.getExternalData();
    if (!(ext instanceof @CHS@)) return;
    @WLD@ w = ((@CHS@) ext).getWorld();
    if (w == null) return;
    String wn = w.getName();
    if (@PKG@.ExpCfg.excluded(wn)) return;
    @ICB@ icb = (@ICB@) store.getComponent(ref, @ICB@.getComponentType());
    if (icb == null) return;
    @BSI@ info = (@BSI@) store.getComponent(ref, @BSI@.getComponentType());
    int[] p = @PKG@.ChestReg.posOf(store, info);
    if (p == null) return;
    String wf = @PKG@.ChestReg.wf(wn);
    String dl = icb.getDroplist();
    if (dl != null && dl.length() > 0 && dl.indexOf(' ') < 0 && dl.indexOf('|') < 0) {
      String pb = "-";
      try {
        @PBI@ pc = (@PBI@) store.getComponent(ref, @PBI@.getComponentType());
        if (pc != null && pc.getWhoPlacedUuid() != null) pb = pc.getWhoPlacedUuid().toString();
      } catch (Throwable t2) { pb = "-"; }
      @PKG@.ChestReg.put(wn, wf, p[0], p[1], p[2], dl, pb);
    } else if (reason == @ADDR@.SPAWN) {
      @PKG@.ChestReg.remove(wf, p[0], p[1], p[2]);
    }
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ExpCfg.warn("loot chest capture failed (logged once): " + t); }
  }
}""")
M(css, r"""
public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ store, @CB@ cb) {
  try {
    if (reason == @REMR@.UNLOAD) return;
    if (reason != @REMR@.REMOVE && reason != @REMR@.BUILDER_TOOLS_UNDO) return;
    Object ext = store.getExternalData();
    if (!(ext instanceof @CHS@)) return;
    @WLD@ w = ((@CHS@) ext).getWorld();
    if (w == null) return;
    String wn = w.getName();
    String wf = @PKG@.ChestReg.wf(wn);
    if (@PKG@.ChestReg.size(wf) == 0) return;
    @BSI@ info = (@BSI@) cb.getComponent(ref, @BSI@.getComponentType());
    int[] p = @PKG@.ChestReg.posOf(cb, info);
    if (p == null) return;
    @PKG@.ChestReg.remove(wf, p[0], p[1], p[2]);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ExpCfg.warn("loot chest removal failed (logged once): " + t); }
  }
}""")
# the unordered fallback: a different class (the registry is keyed by class), no dependency
C(csl, "public ChestSpawnLateSys() { super(false); }")

# ================= ChestOpenSys: UseBlockEvent$Post on the player -> OpenCheck =================
C(cos, "public ChestOpenSys() { super(@UBP@.class); }")
F(cos, "public static boolean FAILED_ONCE = false;")
M(cos, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
M(cos, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.ExpCfg.CHESTS_ON) return;
    @UBE@ e = (@UBE@) ev;
    @V3I@ tb = e.getTargetBlock();
    if (tb == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    String wn = w.getName();
    if (@PKG@.ExpCfg.excluded(wn)) return;
    String wf = @PKG@.ChestReg.wf(wn);
    int[] o = @PKG@.ChestReg.find(w, wf, tb.x(), tb.y(), tb.z());
    if (o == null) return;
    java.util.UUID u = pr.getUuid();
    String k = @PKG@.ExpIO.pkey(u);
    @PKG@.ExpData d = @PKG@.ExpStore.cached(k);
    if (d != null && @PKG@.ExpStore.isOpened(d, wf, o[0], o[1], o[2])) return;
    @PKG@.ExpAward.queue(u, w, wf, o[0], o[1], o[2], k);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ExpCfg.warn("chest use handler failed (logged once): " + t); }
  }
}""")

# ================= ExpTick: once per second per player on the world thread =================
C(tick, "public ExpTick() { super(); }")
F(tick, "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();")
F(tick, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")
F(tick, "public static boolean FAILED_ONCE = false;")
M(tick, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(tick, r"""
public boolean isParallel(int a, int b) {
  return false;
}""")
M(tick, r"""
public static @PKG@.ExpState state(java.util.UUID u) {
  @PKG@.ExpState s = (@PKG@.ExpState) ST.get(u);
  if (s == null) { s = new @PKG@.ExpState(); ST.put(u, s); }
  return s;
}""")
# PROFILES-CONTRACT 4.2: the first epoch seen is a baseline; an absent epoch is never recorded
M(tick, r"""
public static boolean epochChanged(java.util.UUID u) {
  long e = -1L;
  try {
    Object o = @PKG@.ExpIO.bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) e = ((Number) o).longValue();
  } catch (Throwable t) { }
  if (e < 0L) return false;
  Object last = EPOCH.put(u, Long.valueOf(e));
  return last != null && ((Long) last).longValue() != e;
}""")
# A5: new chunks (no record and no XP while blocked: creative, flying, gliding / mounted with their switch off, no movement states)
M(tick, r"""
public static void chunks(@ST@ store, @REF@ ref, @PKG@.ExpState s, @PKG@.ExpData d, String wf, @MVT@ ms, String region, boolean blocked, long now) {
  if (ms == null || blocked) { s.hasLast = false; return; }
  if (ms.gliding && !@PKG@.ExpCfg.PAY_GLIDE) { s.hasLast = false; return; }
  if (ms.mounting && !@PKG@.ExpCfg.PAY_MOUNT) { s.hasLast = false; return; }
  @TRC@ tc = (@TRC@) store.getComponent(ref, @TRC@.getComponentType());
  if (tc == null) return;
  @V3D@ pos = tc.getPosition();
  if (pos == null) return;
  long ck = @CHU@.indexChunkFromBlock(pos.x(), pos.z());
  if (s.hasLast && ck == s.lastChunk && wf.equals(s.lastWf)) return;
  s.hasLast = true;
  s.lastChunk = ck;
  s.lastWf = wf;
  if (@PKG@.ExpStore.chunkSet(d, wf) == null) return;
  long xp = Math.round((double) @PKG@.ExpCfg.CHUNK_XP * @PKG@.ExpCfg.chunkMult(region));
  long got = @PKG@.ExpStore.addChunk(d, wf, ck, xp);
  if (got < 0L) return;
  if (s.pendN == 0L) s.pendStart = now;
  s.pendN = s.pendN + 1L;
  s.pendXp = s.pendXp + got;
  if (got == 0L && xp > 0L) s.pendCapped = true;
}""")
M(tick, r"""
public static void feedback(@PR@ pr, @PKG@.ExpState s, @PKG@.ExpData d, String wf, long now) {
  if (s.pendN <= 0L || now - s.pendStart < @PKG@.ExpCfg.FEEDBACK_MS) return;
  long n = s.pendN;
  long xp = s.pendXp;
  boolean cap = s.pendCapped;
  s.pendN = 0L;
  s.pendXp = 0L;
  s.pendCapped = false;
  s.pendStart = 0L;
  if (d.quiet) return;
  long here = @PKG@.ExpStore.hereCount(d, wf);
  String hs = here >= 0L ? " (" + @PKG@.ExpDefs.grp(here) + " here)" : "";
  String what = @PKG@.ExpDefs.grp(n) + (n == 1L ? " new chunk" : " new chunks");
  String line = xp > 0L ? "+" + @PKG@.ExpDefs.grp(xp) + " Exploration XP from " + what + hs : what + " explored" + hs;
  if (cap) line = line + " - this world's chunk XP cap is reached";
  @PKG@.ExpTitles.say(pr, line, "#c8a0ff");
}""")
# A6: Hytale regions, per profile
M(tick, r"""
public static void zone(@PR@ pr, java.util.UUID u, @PKG@.ExpData d, String k, String region, String zname, boolean creative, @PKG@.ExpState s, long now) {
  if (region == null || region.length() == 0 || @PKG@.ExpStore.hasZone(d, region)) return;
  long xp = @PKG@.ExpCfg.zoneXp(region);
  if (!@PKG@.ExpStore.addZone(d, region, xp)) return;
  @PKG@.ExpStore.saveSoon(k);
  String zn = @PKG@.ExpDefs.regionZone(region);
  if (zn.length() == 0) zn = @PKG@.ExpDefs.zoneName(zname);
  int n = @PKG@.ExpStore.knownZones(d);
  @PKG@.ExpTitles.say(pr, "[Exploration] Discovered " + @PKG@.ExpDefs.regionName(region) + (zn.length() > 0 ? " (" + zn + ")" : "") + " +" + @PKG@.ExpDefs.grp(xp) + " Exploration XP (" + n + " of " + @PKG@.ExpDefs.NR + ")", "#9adf86");
  if (@PKG@.ExpCfg.BANNER) {
    try { @ETU@.showEventTitleToPlayer(pr, @MSG@.translation("server.map.region." + region), @MSG@.raw("+" + @PKG@.ExpDefs.grp(xp) + " Exploration XP"), false); } catch (Throwable t) { }
  }
  if (!creative) { s.lastFlush = now; @PKG@.ExpXp.flush(u, k, d); }
}""")
# backup open path: every open container window of the player at a recorded, unopened loot chest
M(tick, r"""
public static void scan(@PLA@ p, @WLD@ w, String wf, java.util.UUID u, String k, @PKG@.ExpData d) {
  if (@PKG@.ChestReg.size(wf) == 0) return;
  java.util.List ws = null;
  try { ws = p.getWindowManager().getWindows(); } catch (Throwable t) { return; }
  if (ws == null) return;
  for (int i = 0; i < ws.size(); i++) {
    Object o = ws.get(i);
    if (!(o instanceof @CBW@)) continue;
    @BWIN@ bw = (@BWIN@) o;
    int[] org = @PKG@.ChestReg.find(w, wf, bw.getX(), bw.getY(), bw.getZ());
    if (org == null) continue;
    if (@PKG@.ExpStore.isOpened(d, wf, org[0], org[1], org[2])) continue;
    @PKG@.ExpAward.queue(u, w, wf, org[0], org[1], org[2], k);
  }
}""")
M(tick, r"""
public static void second(@PR@ pr, @PLA@ p, @REF@ ref, @ST@ store, java.util.UUID u, @PKG@.ExpState s) {
  long now = System.currentTimeMillis();
  if (epochChanged(u)) {
    s.hasLast = false; s.pendN = 0L; s.pendXp = 0L; s.pendStart = 0L; s.pendCapped = false; s.lastFlush = 0L;
    @PKG@.ExpCfg.info("profile switch: " + u + " now explores as " + @PKG@.ExpIO.pkey(u));
  }
  Object ext = store.getExternalData();
  if (!(ext instanceof @EST@)) return;
  @WLD@ w = ((@EST@) ext).getWorld();
  if (w == null) return;
  String wn = w.getName();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.name == null) @PKG@.ExpStore.setName(d, pr.getUsername());
  int lvl = @PKG@.ExpSkill.level(u);
  int lv = lvl < 0 ? 0 : lvl;
  boolean creative = false;
  try { creative = p.getGameMode() == @GM@.Creative; } catch (Throwable t) { creative = false; }
  if (!d.bad) {
    @MVT@ ms = null;
    try {
      @MSC@ msc = (@MSC@) store.getComponent(ref, @MSC@.getComponentType());
      if (msc != null) ms = msc.getMovementStates();
    } catch (Throwable t) { ms = null; }
    String region = null;
    String zname = null;
    try {
      @WMT@ tr = p.getWorldMapTracker();
      if (tr != null) {
        @ZDI@ zi = tr.getCurrentZone();
        if (zi != null) { region = zi.regionName(); zname = zi.zoneName(); }
      }
    } catch (Throwable t) { region = null; }
    boolean noCreative = creative && !@PKG@.ExpCfg.CREATIVE_XP;
    boolean noFly = ms != null && ms.flying && @PKG@.ExpCfg.NO_FLYING;
    String wf = null;
    if (!@PKG@.ExpCfg.excluded(wn)) {
      wf = @PKG@.ChestReg.wf(wn);
      if (@PKG@.ExpCfg.CHUNKS_ON) chunks(store, ref, s, d, wf, ms, region, noCreative || noFly, now);
      if (@PKG@.ExpCfg.ZONES_ON && !noCreative && !noFly) zone(pr, u, d, k, region, zname, creative, s, now);
      if (@PKG@.ExpCfg.CHESTS_ON) scan(p, w, wf, u, k, d);
    } else s.hasLast = false;
    feedback(pr, s, d, wf, now);
    if (d.owed > 0L && !creative && now - s.lastFlush >= @PKG@.ExpCfg.RETRY_MS) { s.lastFlush = now; @PKG@.ExpXp.flush(u, k, d); }
    @PKG@.ExpTitles.check(pr, k, d, lv);
  }
  @PKG@.ExpTitles.publish(u, d, lv);
}""")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.ExpState s = state(u);
    s.acc = s.acc + (double) dt;
    if (s.acc < 1.0) return;
    s.acc = 0.0;
    second(pr, p, ref, store, u, s);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ExpCfg.warn("exploration tick failed (logged once): " + t); }
  }
}""")

# ================= ExpSaver: 2 s scheduler ticker (appends, dirty files, cleanup - never reads player files) =================
svr.addInterface(pool.get("java.lang.Runnable"))
F(svr, "public long n;")
C(svr, "public ExpSaver() { this.n = 0L; }")
M(svr, r"""
public static void retainOnline() {
  java.util.Iterator it = @PKG@.ExpTitles.PUBLISHED.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    if (@UNI@.get().getPlayer(u) != null) continue;
    it.remove();
    @PKG@.ExpTitles.clearOne(u);
    @PKG@.ExpTick.ST.remove(u);
    @PKG@.ExpTick.EPOCH.remove(u);
  }
}""")
M(svr, r"""
public void run() {
  this.n++;
  try { @PKG@.ExpIO.drain(); } catch (Throwable t) { @PKG@.ExpCfg.warnEvery("drain", 60000L, "append queue failed: " + t); }
  if (this.n % 5L == 0L) { try { @PKG@.ExpStore.flushDirty(); } catch (Throwable t) { } }
  if (this.n % 15L == 0L) {
    try { retainOnline(); } catch (Throwable t) { }
    try { @PKG@.ExpStore.retain(); } catch (Throwable t) { }
  }
}""")

# ================= chat title prefix: TitleFormatter / ChatWrap / ChatHook (async chat thread; reads ExpTitles.CHAT only) =================
tfm.addInterface(pool.get(T["PCF"]))
F(tfm, "public @PCF@ prev;")
C(tfm, "public TitleFormatter(@PCF@ p) { this.prev = p; }")
M(tfm, r"""
public @MSG@ format(@PR@ sender, String content) {
  @MSG@ m = this.prev.format(sender, content);
  try {
    if (!@PKG@.ExpCfg.CHAT_PREFIX || sender == null || m == null) return m;
    Object o = @PKG@.ExpTitles.CHAT.get(sender.getUuid());
    if (!(o instanceof String[])) return m;
    String[] t = (String[]) o;
    return @MSG@.join(new @MSG@[] { @MSG@.raw("[" + t[0] + "] ").color(t[1]), m });
  } catch (Throwable e) { return m; }
}""")
cwr.addInterface(pool.get("java.util.function.Function"))
C(cwr, "public ChatWrap() { }")
M(cwr, r"""
public Object apply(Object e) {
  try {
    if (!(e instanceof @PCE@)) return e;
    @PCE@ ev = (@PCE@) e;
    @PCF@ prev = ev.getFormatter();
    if (prev instanceof @PKG@.TitleFormatter) return ev;
    ev.setFormatter(new @PKG@.TitleFormatter(prev == null ? @PCE@.DEFAULT_FORMATTER : prev));
  } catch (Throwable t) { }
  return e;
}""")
chk.addInterface(pool.get("java.util.function.Function"))
F(chk, "public java.util.function.Function wrap;")
C(chk, "public ChatHook() { this.wrap = new @PKG@.ChatWrap(); }")
M(chk, r"""
public Object apply(Object f) {
  try {
    if (f instanceof java.util.concurrent.CompletableFuture) return ((java.util.concurrent.CompletableFuture) f).thenApply(this.wrap);
  } catch (Throwable t) { }
  return f;
}""")

# ================= skill:stats:Exploration (SkyySkills Stats page) + explore:fn:title =================
sfn.addInterface(pool.get("java.util.function.Function"))
C(sfn, "public ExpStatsFn() { }")
# lines use dashes instead of commas and colons, like the rest of that page (SkyyCooking's hook convention)
M(sfn, r"""
public Object apply(Object arg) {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    Object[] a = (Object[]) arg;
    if (!(a[0] instanceof java.util.UUID)) return out;
    java.util.UUID u = (java.util.UUID) a[0];
    int lv = 0;
    if (a.length > 1 && a[1] instanceof Number) lv = ((Number) a[1]).intValue();
    if (lv < 0) lv = 0;
    boolean next = a.length > 2 && Boolean.TRUE.equals(a[2]);
    String k = @PKG@.ExpIO.pkey(u);
    @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
    if (next) {
      double[] now = @PKG@.ExpSkill.luck(u, lv);
      double[] nx = @PKG@.ExpSkill.luck(u, lv + 1);
      if (@PKG@.ExpCfg.LUCK_ON && nx[0] - now[0] > 0.0000001) out.add("+" + @PKG@.ExpDefs.pct(nx[0] - now[0]) + " chest luck");
      for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
        if (@PKG@.ExpDefs.T_KIND[i] == 0 && @PKG@.ExpDefs.T_REQ[i] == (long) (lv + 1)) out.add("Unlocks the title " + @PKG@.ExpDefs.T_NAME[i]);
      }
      return out;
    }
    if (d.bad) { out.add("Your exploration file could not be read - ask an admin"); return out; }
    double[] l = @PKG@.ExpSkill.luck(u, lv);
    if (@PKG@.ExpCfg.LUCK_ON) out.add("+" + @PKG@.ExpDefs.pct(l[0]) + " chest luck - an extra roll from loot chests");
    out.add("Found " + @PKG@.ExpStore.knownZones(d) + " of " + @PKG@.ExpDefs.NR + " zones - " + @PKG@.ExpDefs.fmt(d.chests) + " loot chests - " + @PKG@.ExpDefs.fmt(d.total) + " chunks");
    int sel = @PKG@.ExpTitles.selected(d, lv);
    out.add(sel >= 0 ? "Title - " + @PKG@.ExpDefs.T_NAME[sel] + " (/title)" : "No title selected - " + @PKG@.ExpTitles.count(d, lv) + " earned (/title)");
    if (d.owed > 0L) out.add(@PKG@.ExpDefs.fmt(d.owed) + " Exploration XP still waiting to be paid");
  } catch (Throwable t) { }
  return out;
}""")
tfn.addInterface(pool.get("java.util.function.Function"))
C(tfn, "public ExpTitleFn() { }")
M(tfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof java.util.UUID)) return null;
    Object o = @PKG@.ExpTitles.CHAT.get(arg);
    if (o instanceof String[]) return ((String[]) o)[0];
  } catch (Throwable t) { }
  return null;
}""")

# ================= ExplorePage: the inline /explore page =================
def tbs(bg, hv, pr, fg, fgh):
    lab = "FontSize: 12, TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center"
    return ("Style: TextButtonStyle(Default: (Background: %s, LabelStyle: (%s)), Hovered: (Background: %s, LabelStyle: (%s)), "
            "Pressed: (Background: %s, LabelStyle: (%s)));") % (bg, lab % fg, hv, lab % fgh, pr, lab % fgh)
T["BSG"] = tbs("#27463a", "#3b6b54", "#172a22", "#dcffe8", "#ffffff")      # SkyySkills / SkyyTrees button style
T["BSOFF"] = tbs("#1d2c3c", "#2c4258", "#142030", "#b8c8d8", "#ffffff")
T["BTON"] = tbs("#6b4a1c", "#80592a", "#3a2810", "#ffffff", "#ffffff")
T["BTOFF"] = T["BSOFF"]
for k in ("BSG", "BSOFF", "BTON", "BTOFF"): assert '"' not in T[k] and "@" not in T[k]

F(page, "public int tab;")
F(page, "public String msg;")
F(page, 'public static final String[] TABS = new String[] { "Overview", "Zones", "Titles" };')
F(page, "public static final String[] CARD_ICON = %s;" % jstr(CARD_ICON))
F(page, "public static final String[] CARD_HEAD = %s;" % jstr(CARD_HEAD))
F(page, "public static final String[] CARD_COLOR = %s;" % jstr(CARD_COLOR))
F(page, 'public static final String NOTE = "Loot chests - new chunks - zones - once each per profile - nothing while flying or in creative - XP boosters never apply";')
F(page, 'public static final String BADNOTE = "Your exploration file could not be read - ask an admin (nothing is earned or saved until it is fixed)";')
C(page, r"""
public ExplorePage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab;
  this.msg = "";
}""")
M(page, r"""
public static void card(@UCB@ b, String parent, int i, String icon, String head, String val, String sub, String col) {
  b.appendInline(parent, "Group #SkyyExCard" + i + " { Anchor: (Width: 268, Height: 110); Background: #142030(0.9); LayoutMode: Left; Padding: (Horizontal: 8, Vertical: 6); }");
  b.appendInline("#SkyyExCard" + i, "Group { Anchor: (Width: 60, Height: 98); ItemIcon { Anchor: (Width: 52, Height: 52, Left: 0, Top: 22); ItemId: \"" + icon + "\"; } }");
  b.appendInline("#SkyyExCard" + i, "Group #SkyyExCardT" + i + " { Anchor: (Width: 184, Height: 98); LayoutMode: Top; }");
  b.appendInline("#SkyyExCardT" + i, "Label #SkyyExCardA" + i + " { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 11, TextColor: #9fb8cc, VerticalAlignment: Center); }");
  b.appendInline("#SkyyExCardT" + i, "Label #SkyyExCardB" + i + " { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
  b.appendInline("#SkyyExCardT" + i, "Label #SkyyExCardC" + i + " { Anchor: (Height: 46); Text: \"\"; Style: (FontSize: 11, TextColor: #c8d6e4, Wrap: true); }");
  b.set("#SkyyExCardA" + i + ".Text", head == null ? "" : head);
  b.set("#SkyyExCardB" + i + ".Text", val == null ? "" : val);
  b.set("#SkyyExCardC" + i + ".Text", sub == null ? "" : sub);
}""")
M(page, r"""
public static void line(@UCB@ b, String parent, String id, String text, String color, int size, int h) {
  b.appendInline(parent, "Label #" + id + " { Anchor: (Height: " + h + "); Text: \"\"; Style: (FontSize: " + size + ", TextColor: " + color + ", VerticalAlignment: Center, Wrap: true); }");
  b.set("#" + id + ".Text", text == null ? "" : text);
}""")
M(page, r"""
public static void overview(@UCB@ b, java.util.UUID u, @PKG@.ExpData d, int lvl, String wn) {
  int lv = lvl < 0 ? 0 : lvl;
  String[] val = new String[6];
  String[] sub = new String[6];
  boolean row = @PKG@.ExpSkill.hasRow(u);
  if (lvl < 0) { val[0] = "SkyySkills missing"; sub[0] = "Install SkyySkills 0.4.1 to level Exploration - your XP waits here"; }
  else if (!row) { val[0] = "Level " + lv; sub[0] = "Needs SkyySkills 0.4.1 (the Exploration row) - your XP waits here"; }
  else { val[0] = "Level " + lv; sub[0] = "+" + @PKG@.ExpDefs.num(lv * @PKG@.ExpCfg.STA_PER) + " max Stamina from Exploration"; }
  val[1] = @PKG@.ExpStore.knownZones(d) + " of " + @PKG@.ExpDefs.NR + " zones";
  sub[1] = @PKG@.ExpStore.namedZones(d) + " of " + @PKG@.ExpDefs.NAMED + " named regions";
  val[2] = @PKG@.ExpDefs.grp(d.chests) + (d.chests == 1L ? " loot chest" : " loot chests");
  sub[2] = @PKG@.ExpDefs.grp(d.luck) + (d.luck == 1L ? " chest luck roll won" : " chest luck rolls won") + (@PKG@.ExpCfg.CHESTS_ON ? "" : " - chest XP is off on this server");
  boolean ex = @PKG@.ExpCfg.excluded(wn);
  String wf = ex ? null : @PKG@.ChestReg.wf(wn);
  long here = wf == null ? -1L : @PKG@.ExpStore.hereCount(d, wf);
  if (ex) { val[3] = "No map XP here"; sub[3] = @PKG@.ExpDefs.grp(d.total) + " chunks in all worlds - this world does not count"; }
  else {
    val[3] = (here < 0L ? "-" : @PKG@.ExpDefs.grp(here)) + " chunks here";
    long left = @PKG@.ExpCfg.CHUNK_CAP - @PKG@.ExpStore.paidHere(d, wf);
    if (left < 0L) left = 0L;
    sub[3] = @PKG@.ExpDefs.grp(d.total) + " in all worlds - " + @PKG@.ExpDefs.grp(left) + " left to pay here";
  }
  double[] l = @PKG@.ExpSkill.luck(u, lv);
  if (@PKG@.ExpCfg.LUCK_ON) {
    val[4] = @PKG@.ExpDefs.pct(l[0]) + " chest luck";
    sub[4] = "level " + @PKG@.ExpDefs.pct(l[1]) + " + tree " + @PKG@.ExpDefs.pct(l[2]) + (l[1] + l[2] > @PKG@.ExpCfg.LUCK_MAX ? " (capped at " + @PKG@.ExpDefs.pct(@PKG@.ExpCfg.LUCK_MAX) + ")" : "");
  } else { val[4] = "Chest luck off"; sub[4] = "Turned off on this server"; }
  int sel = @PKG@.ExpTitles.selected(d, lv);
  val[5] = sel < 0 ? "No title" : @PKG@.ExpDefs.T_NAME[sel];
  sub[5] = @PKG@.ExpTitles.count(d, lv) + " of " + @PKG@.ExpDefs.NT + " titles - /title";
  for (int r = 0; r < 2; r++) {
    b.appendInline("#SkyyExBody", "Group #SkyyExRow" + r + " { Anchor: (Height: 116); LayoutMode: Left; Padding: (Top: 6); }");
    for (int c = 0; c < 3; c++) {
      int i = r * 3 + c;
      card(b, "#SkyyExRow" + r, i, CARD_ICON[i], CARD_HEAD[i], val[i], sub[i], CARD_COLOR[i]);
      if (c < 2) b.appendInline("#SkyyExRow" + r, "Label { Anchor: (Width: 12, Height: 110); Text: \"\"; }");
    }
  }
  b.appendInline("#SkyyExBody", "Label { Anchor: (Height: 10); Text: \"\"; }");
  if (d.owed > 0L) {
    String w = @PKG@.ExpDefs.grp(d.owed) + " Exploration XP waiting for SkyySkills 0.4.1";
    if (row) w = @PKG@.ExpDefs.grp(d.owed) + " Exploration XP on its way to SkyySkills";
    line(b, "#SkyyExBody", "SkyyExOwed", w, "#ffb080", 13, 24);
  }
  line(b, "#SkyyExBody", "SkyyExInfo0", "Loot chests - the first time you open a world chest (placed chests never count): XP by zone and tier plus a chance of an extra roll", "#c8d6e4", 12, 34);
  line(b, "#SkyyExBody", "SkyyExInfo1", "Map - every new chunk you walk into pays a little (not while flying - teleports are fine)", "#c8d6e4", 12, 22);
  line(b, "#SkyyExBody", "SkyyExInfo2", "Zones - the first time this profile enters each of Hytale's regions", "#c8d6e4", 12, 22);
  line(b, "#SkyyExBody", "SkyyExInfo3", "Each Exploration level gives a little max Stamina and coins (SkyySkills). /explore quiet hides the chunk XP line.", "#c8d6e4", 12, 22);
  line(b, "#SkyyExBody", "SkyyExInfo4", d.quiet ? "Chunk XP messages are hidden (/explore quiet)" : "", "#9fb8cc", 11, 20);
}""")
M(page, r"""
public static void zonesTab(@UCB@ b, @PKG@.ExpData d) {
  b.appendInline("#SkyyExBody", "Group #SkyyExZones { Anchor: (Height: 490); LayoutMode: Left; }");
  b.appendInline("#SkyyExZones", "Group #SkyyExZoneL { Anchor: (Width: 404, Height: 486); LayoutMode: Top; }");
  b.appendInline("#SkyyExZones", "Label { Anchor: (Width: 20, Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyExZones", "Group #SkyyExZoneR { Anchor: (Width: 404, Height: 486); LayoutMode: Top; }");
  for (int g = 0; g < @PKG@.ExpDefs.G_NAME.length; g++) {
    String par = @PKG@.ExpDefs.G_SIDE[g] == 0 ? "#SkyyExZoneL" : "#SkyyExZoneR";
    int n = 0;
    int f = 0;
    for (int i = 0; i < @PKG@.ExpDefs.NR; i++) {
      if (@PKG@.ExpDefs.R_GROUP[i] != g) continue;
      n++;
      if (@PKG@.ExpStore.hasZone(d, @PKG@.ExpDefs.R_ID[i])) f++;
    }
    b.appendInline(par, "Label #SkyyExZH" + g + " { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + @PKG@.ExpDefs.G_COLOR[g] + ", VerticalAlignment: Center); }");
    b.set("#SkyyExZH" + g + ".Text", @PKG@.ExpDefs.G_NAME[g] + "  (" + f + " of " + n + ")");
    for (int i = 0; i < @PKG@.ExpDefs.NR; i++) {
      if (@PKG@.ExpDefs.R_GROUP[i] != g) continue;
      boolean got = @PKG@.ExpStore.hasZone(d, @PKG@.ExpDefs.R_ID[i]);
      b.appendInline(par, "Label #SkyyExZ" + i + " { Anchor: (Height: 20); Text: \"\"; Style: (FontSize: 12, TextColor: " + (got ? "#9adf86" : "#7f94a8") + ", VerticalAlignment: Center); }");
      b.set("#SkyyExZ" + i + ".Text", "    " + @PKG@.ExpDefs.R_NAME[i] + "  - " + (got ? "found" : @PKG@.ExpDefs.grp(@PKG@.ExpCfg.zoneXp(@PKG@.ExpDefs.R_ID[i])) + " XP"));
    }
    b.appendInline(par, "Label { Anchor: (Height: 8); Text: \"\"; }");
  }
}""")
M(page, r"""
public static void titlesTab(@UCB@ b, @UEB@ ev, @PKG@.ExpData d, int lv) {
  int sel = @PKG@.ExpTitles.selected(d, lv);
  b.appendInline("#SkyyExBody", "Group #SkyyExTHead { Anchor: (Height: 38); LayoutMode: Left; }");
  b.appendInline("#SkyyExTHead", "Label #SkyyExCur { Anchor: (Width: 680, Height: 32); Text: \"\"; Style: (FontSize: 13, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center); }");
  b.set("#SkyyExCur.Text", "Your title: " + (sel < 0 ? "none" : @PKG@.ExpDefs.T_NAME[sel]) + "   -   " + @PKG@.ExpTitles.count(d, lv) + " of " + @PKG@.ExpDefs.NT + " earned - it shows in front of your chat messages");
  b.appendInline("#SkyyExTHead", "TextButton #SkyyExNone { Anchor: (Width: 140, Height: 30); Text: \"No title\"; @BSOFF@ }");
  ev.addEventBinding(@BT@.Activating, "#SkyyExNone", @EVD@.of("a", "exnone"));
  b.appendInline("#SkyyExBody", "Group #SkyyExTCols { Anchor: (Height: 452); LayoutMode: Left; }");
  b.appendInline("#SkyyExTCols", "Group #SkyyExTL { Anchor: (Width: 404, Height: 448); LayoutMode: Top; }");
  b.appendInline("#SkyyExTCols", "Label { Anchor: (Width: 20, Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyExTCols", "Group #SkyyExTR { Anchor: (Width: 404, Height: 448); LayoutMode: Top; }");
  int half = (@PKG@.ExpDefs.NT + 1) / 2;
  for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
    String par = i < half ? "#SkyyExTL" : "#SkyyExTR";
    boolean e = @PKG@.ExpTitles.earned(d, lv, i);
    String col = e ? @PKG@.ExpDefs.KIND_COLOR[@PKG@.ExpDefs.T_KIND[i]] : "#8a8a8a";
    b.appendInline(par, "Group #SkyyExT" + i + " { Anchor: (Height: 38); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyExT" + i, "Label #SkyyExTN" + i + " { Anchor: (Width: 150, Height: 30); Text: \"\"; Style: (FontSize: 13, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
    b.set("#SkyyExTN" + i + ".Text", @PKG@.ExpDefs.T_NAME[i]);
    b.appendInline("#SkyyExT" + i, "Label #SkyyExTQ" + i + " { Anchor: (Width: 170, Height: 30); Text: \"\"; Style: (FontSize: 11, TextColor: #9fb8cc, VerticalAlignment: Center, Wrap: true); }");
    b.set("#SkyyExTQ" + i + ".Text", @PKG@.ExpDefs.T_TEXT[i]);
    if (e && i != sel) {
      b.appendInline("#SkyyExT" + i, "TextButton #SkyyExUse" + i + " { Anchor: (Width: 70, Height: 28); Text: \"Use\"; @BSG@ }");
      ev.addEventBinding(@BT@.Activating, "#SkyyExUse" + i, @EVD@.of("a", "exuse" + i));
    } else {
      b.appendInline("#SkyyExT" + i, "Label #SkyyExTS" + i + " { Anchor: (Width: 70, Height: 28); Text: \"\"; Style: (FontSize: 12, RenderBold: true, TextColor: " + (e ? "#9adf86" : "#b07a68") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
      b.set("#SkyyExTS" + i + ".Text", e ? "In use" : "Locked");
    }
  }
}""")
M(page, r"""
public static String lvlText(java.util.UUID u, int lvl) {
  if (lvl < 0) return "SkyySkills not installed";
  return "Exploration " + lvl + " - " + @PKG@.ExpDefs.fmt(@PKG@.ExpSkill.xp(u)) + " XP";
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  int lvl = @PKG@.ExpSkill.level(u);
  int lv = lvl < 0 ? 0 : lvl;
  int t = this.tab;
  if (t < 0 || t > 2) t = 0;
  String wn = null;
  Object ext = st.getExternalData();
  if (ext instanceof @EST@) { @WLD@ w = ((@EST@) ext).getWorld(); if (w != null) wn = w.getName(); }
  b.appendInline((String) null, "Group #SkyyExRoot { Anchor: (Width: 860, Height: 620); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }");
  b.appendInline("#SkyyExRoot", "Group #SkyyExHead { Anchor: (Height: 36); LayoutMode: Left; }");
  for (int i = 0; i < 3; i++) {
    b.appendInline("#SkyyExHead", "TextButton #SkyyExTab" + i + " { Anchor: (Width: 120, Height: 32); Text: \"" + TABS[i] + "\"; " + (i == t ? "@BTON@" : "@BTOFF@") + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyExTab" + i, @EVD@.of("a", "extab" + i));
    b.appendInline("#SkyyExHead", "Label { Anchor: (Width: 6, Height: 32); Text: \"\"; }");
  }
  b.appendInline("#SkyyExHead", "Label #SkyyExLvl { Anchor: (Width: 440, Height: 32); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: #e0a040, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyExLvl.Text", lvlText(u, lvl));
  b.appendInline("#SkyyExRoot", "Label #SkyyExNote { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 11, TextColor: #9fb8cc, VerticalAlignment: Center); }");
  b.set("#SkyyExNote.Text", d.bad ? BADNOTE : NOTE);
  b.appendInline("#SkyyExRoot", "Group { Anchor: (Height: 2); Background: #e0a040; }");
  b.appendInline("#SkyyExRoot", "Group #SkyyExBody { Anchor: (Height: 500); LayoutMode: Top; Padding: (Top: 6); }");
  if (t == 0) overview(b, u, d, lvl, wn);
  else if (t == 1) zonesTab(b, d);
  else titlesTab(b, ev, d, lv);
  b.appendInline("#SkyyExRoot", "Group #SkyyExFoot { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 8); }");
  if (@PKG@.ExpSkill.hasSkills()) {
    b.appendInline("#SkyyExFoot", "TextButton #SkyyExSkills { Anchor: (Width: 130, Height: 32); Text: \"< Skills\"; @BSG@ }");
    ev.addEventBinding(@BT@.Activating, "#SkyyExSkills", @EVD@.of("a", "exskills"));
    b.appendInline("#SkyyExFoot", "Label { Anchor: (Width: 12, Height: 32); Text: \"\"; }");
  }
  if (@PKG@.ExpSkill.treeNames().indexOf("Exploration") >= 0) {
    b.appendInline("#SkyyExFoot", "TextButton #SkyyExTree { Anchor: (Width: 180, Height: 32); Text: \"Exploration tree\"; @BSG@ }");
    ev.addEventBinding(@BT@.Activating, "#SkyyExTree", @EVD@.of("a", "extree"));
    b.appendInline("#SkyyExFoot", "Label { Anchor: (Width: 12, Height: 32); Text: \"\"; }");
  }
  b.appendInline("#SkyyExFoot", "Label #SkyyExMsg { Anchor: (Width: 480, Height: 32); Text: \"\"; Style: (FontSize: 12, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyExMsg.Text", this.msg == null ? "" : this.msg);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (data.indexOf("exskills\"") >= 0) {
      if (!@PKG@.ExpSkill.hasSkills()) { this.msg = "SkyySkills is not installed - there is no skills page"; rebuild(); return; }
      @CMGR@.get().handleCommand(this.playerRef, "skills");
      return;
    }
    if (data.indexOf("extree\"") >= 0) {
      @CMGR@.get().handleCommand(this.playerRef, "tree exploration");
      return;
    }
    for (int i = 0; i < 3; i++) {
      if (data.indexOf("extab" + i + "\"") >= 0) { this.tab = i; this.msg = ""; rebuild(); return; }
    }
    if (data.indexOf("exnone\"") >= 0) { this.msg = @PKG@.ExpTitles.choose(this.playerRef, -2); rebuild(); return; }
    for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
      if (data.indexOf("exuse" + i + "\"") >= 0) { this.msg = @PKG@.ExpTitles.choose(this.playerRef, i); rebuild(); return; }
    }
  } catch (Throwable e) { @PKG@.ExpCfg.warn("explore page event failed: " + e); }
}""")

# ================= commands (HANDOFF command rules) =================
def open_body(tab):
    return r"""
  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new @PKG@.ExplorePage(pr, """ + tab + r"""));
  } catch (Throwable e) {
    @PKG@.ExpCfg.warn("explore page failed: " + e);
    pr.sendMessage(@MSG@.raw("[Exploration] could not open the exploration page"));
  }"""
C(qcmd, r"""
public ExploreQuietCmd() {
  super("quiet", "Toggle the aggregated chunk XP chat line (per profile)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(qcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.bad) { pr.sendMessage(@MSG@.raw("[Exploration] Your exploration file could not be read - nothing can change until an admin fixes it").color("#ff9090")); return; }
  boolean q = @PKG@.ExpStore.flipQuiet(d);
  @PKG@.ExpStore.saveSoon(k);
  pr.sendMessage(@MSG@.raw(q ? "[Exploration] Chunk XP messages hidden. /explore quiet again to show them." : "[Exploration] Chunk XP messages shown."));
}""")
C(ecmd, r"""
public ExploreCmd() {
  super("explore", "Your exploration: loot chests, map, zones and titles - /explore, /explore quiet");
  addAliases(new String[] { "exploration", "discoveries" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.ExploreQuietCmd());
}""")
M(ecmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
""" + open_body("0") + "\n}")
F(tset, "public @RA@ titleArg;")
C(tset, r"""
public TitleSetCmd() {
  super("Choose your title: /title <name>, /title off");
  this.titleArg = withRequiredArg("title", "a title (id or name without spaces) or off", @ATY@.STRING);
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(tset, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String a = String.valueOf(ctx.get(this.titleArg));
  int i = @PKG@.ExpDefs.resolveTitle(a);
  if (i == -1) { pr.sendMessage(@MSG@.raw("[Exploration] Unknown title '" + a + "' - /title opens the list, /title off removes yours").color("#ff9090")); return; }
  if (i == -3) { pr.sendMessage(@MSG@.raw("[Exploration] '" + a + "' fits more than one title (" + @PKG@.ExpDefs.titleMatches(a) + ") - type more letters, or /title to pick from the list").color("#ffb080")); return; }
  if (i < -2) return;
  String r = @PKG@.ExpTitles.choose(pr, i);
  pr.sendMessage(@MSG@.raw("[Exploration] " + r).color(r.indexOf("locked") >= 0 || r.indexOf("could not") >= 0 ? "#ffb080" : "#9fd0ff"));
}""")
C(tcmd, r"""
public TitleCmd() {
  super("title", "Your exploration titles: /title opens the list, /title <name> or /title off");
  addAliases(new String[] { "titles" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addUsageVariant(new @PKG@.TitleSetCmd());
}""")
M(tcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
""" + open_body("2") + "\n}")
ADMIN_CHECK = r"""  if (!pr.hasPermission("skyyexploration.admin")) { pr.sendMessage(@MSG@.raw("[Exploration] no permission (skyyexploration.admin)")); return; }
"""
C(arl, r"""
public ExAdminReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyExploration/config.properties");
  requirePermission("skyyexploration.admin");
  setPermissionGroups(new String[0]);
}""")
M(arl, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
""" + ADMIN_CHECK + r"""  int bad = @PKG@.ExpStore.dropBad();
  pr.sendMessage(@MSG@.raw("[Exploration] config reloaded: " + @PKG@.ExpCfg.load() + (bad > 0 ? "; " + bad + " unreadable player file(s) will be read again" : "") + " (titles.chatPriority needs a restart)"));
}""")
C(ast, r"""
public ExAdminStatsCmd() {
  super("stats", "(admin) Loot chest registry and online players' exploration counts");
  requirePermission("skyyexploration.admin");
  setPermissionGroups(new String[0]);
}""")
M(ast, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
""" + ADMIN_CHECK + r"""  pr.sendMessage(@MSG@.raw("[Exploration] capture: " + (@PKG@.ChestReg.LATE ? "LATE fallback (Hytale:Stash not loaded - drop lists are not cleared)" : (@PKG@.ChestReg.ORDERED ? "ordered BEFORE the stash roll" : "unordered (StashPlugin class not found)")) + " - chests " + (@PKG@.ExpCfg.CHESTS_ON ? "on" : "off")).color("#ffd27a"));
  java.util.Iterator it = @PKG@.ChestReg.W.keySet().iterator();
  int n = 0;
  while (it.hasNext() && n < 12) {
    String wf = (String) it.next();
    Object nm = @PKG@.ChestReg.NAMES.get(wf);
    pr.sendMessage(@MSG@.raw("  " + (nm == null ? wf : (String) nm) + ": " + @PKG@.ChestReg.size(wf) + " loot chests recorded, " + @PKG@.ChestReg.captured(wf) + " captured since start"));
    n++;
  }
  if (n == 0) pr.sendMessage(@MSG@.raw("  no loot chest recorded yet - explore NEW terrain (chests generated before this mod never count)"));
  java.util.Iterator pi = @UNI@.get().getPlayers().iterator();
  int m = 0;
  while (pi.hasNext() && m < 20) {
    Object o = pi.next();
    if (!(o instanceof @PR@)) continue;
    @PR@ p = (@PR@) o;
    String k = @PKG@.ExpIO.pkey(p.getUuid());
    @PKG@.ExpData d = @PKG@.ExpStore.cached(k);
    if (d == null) { pr.sendMessage(@MSG@.raw("  " + p.getUsername() + " (" + k + "): not loaded yet")); m++; continue; }
    pr.sendMessage(@MSG@.raw("  " + p.getUsername() + " (" + k + "): " + (d.bad ? "UNREADABLE FILE - " : "") + "zones " + @PKG@.ExpStore.knownZones(d) + "/" + @PKG@.ExpDefs.NR + ", chests " + d.chests + ", luck " + d.luck + ", chunks " + d.total + ", owed " + d.owed + ", paid " + d.earned));
    m++;
  }
}""")
C(ars, r"""
public ExAdminResetCmd() {
  super("resetme", "(admin, testing) Clear YOUR active profile's exploration record (XP already paid to SkyySkills stays)");
  requirePermission("skyyexploration.admin");
  setPermissionGroups(new String[0]);
}""")
M(ars, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
""" + ADMIN_CHECK + r"""  java.util.UUID u = pr.getUuid();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.bad) { pr.sendMessage(@MSG@.raw("[Exploration] your file could not be read - fix or delete it first")); return; }
  @PKG@.ExpStore.reset(d);
  @PKG@.ExpIO.deleteLater(@PKG@.ExpStore.chestsFile(k));
  @PKG@.ExpIO.clearDirLater(@PKG@.ExpStore.chunksDir(k));
  @PKG@.ExpStore.saveSoon(k);
  @PKG@.ExpTitles.KNOWN.remove(k);
  @PKG@.ExpState s = (@PKG@.ExpState) @PKG@.ExpTick.ST.get(u);
  if (s != null) { s.hasLast = false; s.pendN = 0L; s.pendXp = 0L; }
  pr.sendMessage(@MSG@.raw("[Exploration] Your exploration record on profile " + k + " was cleared (zones, loot chests, chunks, title). XP already paid to SkyySkills stays; " + d.owed + " XP still waiting is kept.").color("#ffd27a"));
}""")
C(acmd, r"""
public ExploreAdminCmd() {
  super("exploreadmin", "(admin) SkyyExploration: /exploreadmin reload | stats | resetme");
  requirePermission("skyyexploration.admin");
  setPermissionGroups(new String[0]);
  addSubCommand(new @PKG@.ExAdminReloadCmd());
  addSubCommand(new @PKG@.ExAdminStatsCmd());
  addSubCommand(new @PKG@.ExAdminResetCmd());
}""")
M(acmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Exploration] /exploreadmin reload | stats | resetme"));
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
F(pl, "public java.util.function.Function statsFn;")
F(pl, "public java.util.function.Function titleFn;")
C(pl, "public SkyyExplorationPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ExpCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyExploration");
  @PKG@.ExpCfg.FILE = base.resolve("config.properties");
  @PKG@.ExpStore.DIR = base.resolve("players");
  @PKG@.ChestReg.DIR = base.resolve("chests");
  String sum = @PKG@.ExpCfg.load();
  int chests = @PKG@.ChestReg.loadAll();
  Class stash = null;
  try { stash = Class.forName("@SSYS@"); } catch (Throwable t) { stash = null; }
  @PKG@.ChestSpawnSys.STASH = stash;
  String cap;
  try {
    getChunkStoreRegistry().registerSystem(new @PKG@.ChestSpawnSys(true));
    @PKG@.ChestReg.ORDERED = stash != null;
    cap = stash != null ? "capture ordered before the stash roll" : "capture UNORDERED (StashPlugin class not found)";
  } catch (IllegalArgumentException e) {
    @PKG@.ChestReg.LATE = true;
    @PKG@.ExpCfg.warn("could not order the loot chest capture before StashPlugin$StashSystem (" + e.getMessage() + ") - the Hytale:Stash plugin is not loaded (turned off in the server config, or its setup failed; core plugins always set up before Mods-folder plugins), so nobody clears drop lists; using the unordered fallback");
    getChunkStoreRegistry().registerSystem(new @PKG@.ChestSpawnLateSys());
    cap = "capture LATE fallback";
  }
  getEntityStoreRegistry().registerSystem(new @PKG@.ChestOpenSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.ExpTick());
  getCommandRegistry().registerCommand(new @PKG@.ExploreCmd());
  getCommandRegistry().registerCommand(new @PKG@.TitleCmd());
  getCommandRegistry().registerCommand(new @PKG@.ExploreAdminCmd());
  String chat = "chat prefix at priority " + @PKG@.ExpCfg.CHAT_PRIORITY;
  try {
    getEventRegistry().registerAsyncGlobal((short) @PKG@.ExpCfg.CHAT_PRIORITY, @PCE@.class, new @PKG@.ChatHook());
  } catch (Throwable t) {
    chat = "chat prefix NOT registered";
    @PKG@.ExpCfg.warn("could not register the chat title prefix (titles still show on /explore and the bridge): " + t);
  }
  java.util.Map b = @PKG@.ExpIO.bridge();
  this.statsFn = new @PKG@.ExpStatsFn();
  this.titleFn = new @PKG@.ExpTitleFn();
  b.put("skill:stats:Exploration", this.statsFn);
  b.put("explore:fn:title", this.titleFn);
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.ExpSaver(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  String sk = @PKG@.ExpSkill.hasSkills() ? "SkyySkills found" : "SkyySkills not loaded yet (XP waits in the owed ledger until it is)";
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyExploration] @VERSION@ ready - /explore, /title; " + sum + "; " + chests + " loot chests in the registry; " + cap + "; " + chat + "; " + sk);
}""".replace("@VERSION@", VERSION))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.ExpIO.drain(); } catch (Throwable t) { }
  try { @PKG@.ExpStore.flushDirty(); } catch (Throwable t) { }
  try { if (!@PKG@.ExpStore.DIRTY.isEmpty()) @PKG@.ExpStore.flushDirty(); } catch (Throwable t) { }
  try { @PKG@.ExpIO.drain(); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.ExpIO.bridge();
    if (this.statsFn != null) b.remove("skill:stats:Exploration", this.statsFn);
    if (this.titleFn != null) b.remove("explore:fn:title", this.titleFn);
  } catch (Throwable t) { }
  try { @PKG@.ExpTitles.clearAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

ALL = (defs, cfg, dat, est, eio, reg, sto, stk, skl, exx, ttl, awd, ock, css, csl, cos, tick, svr, tfm, cwr, chk, sfn, tfn, page,
       qcmd, ecmd, tset, tcmd, arl, ast, ars, acmd, pl)
for c in ALL:
    c.writeFile(OUT)
print("classes written:", len(ALL))
print("regions:", len(REG), "named XP", sum(r["xp"] for r in REG if r["shown"]), "all zones XP", sum(r["xp"] for r in REG),
      "- loot drop lists:", len(DLS), "chest XP", min(DL_XP.values()), "..", max(DL_XP.values()), "- titles:", len(TITLES))

jar = os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)
m = B.manifest("SkyyExploration", VERSION, "SkyWynn Exploration: Exploration XP (SkyySkills 0.4.1) for the first open of every world loot chest (plus chest luck - an extra roll), every new chunk you walk into (never while flying or in creative) and each of Hytale's zones - once per profile, no XP boosters. Titles earned at Exploration milestones show in front of your chat messages. /explore, /title. Per profile with SkyyProfiles (optional); reads SkyySkills / SkyyTrees / SkyyCoins through the skyy bridge; zero dependencies.", PKG + ".SkyyExplorationPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT, {})  # no assets: the page is built inline
if "--deploy" in sys.argv:   # only with Skyy's deploy OK (HANDOFF section 3); workflows never pass it
    B.deploy(jar, "SkyyExploration.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyExploration" % VERSION, disable_prefix="Skyy:")
