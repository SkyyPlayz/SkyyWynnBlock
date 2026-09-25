"""SkyyExploration 0.2 - build script (javassist via jpype, tools/skyybuild.py). Derived from the LIVE 0.1 (build_skyyexploration_0.1.py,
deployed 2026-09-24 22:53; copied and edited - 0.1 has no patch script and its file stays untouched). Owner: Skyy (they/them).
Spec: research/Exploration-0.2-Spec.md (server backbones: admin-placed discovery / secret spots + the island checklist, all set up IN
GAME, files always in sync - HANDOFF section 1 "In-game server setup", SkyWynn-Server-Setup-Plan.md). Every 0.1 feature, file and
bridge key keeps working; the 0.1 description below still holds.

Run:   python build_skyyexploration_0.2.py            -> SkyyExploration/SkyyExploration-0.2.jar
       python build_skyyexploration_0.2.py --deploy   -> also Mods/SkyyExploration.jar + enabled in the HUD mod world (ONLY with Skyy's OK;
                                                          workflows never pass it - tools/deploy_set.py is the deploy path)

0.2 (spec section numbers in brackets)
  SPOTS [3]  Admins place named discovery spots and hidden SECRET spots where they stand (/exploreadmin page or /exploreadmin spot ...).
     Each world's spots + checklist live in worlds/<worldFile>.properties (world= inside is authoritative). The game rewrites the file
     atomically after every in-game change (scheduler task: ids.properties first, then the world file); /exploreadmin reload reads hand
     edits. Hand-edit guard: after every read/write the file's {lastModified, size} is remembered; an in-game change to a world whose
     file differs is refused ("run /exploreadmin reload first"); a change whose file was hand-edited (or became unreadable) before its
     save ran is never written over the file, but it is not dropped silently either: the world stays marked "in-game change NOT saved"
     (/exploreadmin stats + the admin page) until /exploreadmin reload, and the admin who made it gets one chat line on their next tick;
     a file that does not parse keeps its old in-memory copy and refuses edits, and a file with bad lines loads its good lines but also
     refuses in-game edits until it is fixed (so the bad lines are never silently dropped by a rewrite).
     Detection: NO new system - ExpTick (0.1's Player ticker, world thread) runs spotCheck every spots.checkMs (333 ms). Each world has
     an immutable WorldDef snapshot with a fastutil Long2ObjectOpenHashMap chunk index (ChunkUtil.indexChunk -> SpotDef[] whose sphere
     touches that 32x32 column): one TransformComponent read + one primitive-key get, no allocation; the resolved world is cached in
     ExpState (same world name object + same SpotReg.GEN + same config generation). pkey() only on a hit. Flying / creative record
     nothing. First arrival per profile: engine banner (EventTitleUtil) + sound (SoundUtil.playSoundEvent2dToPlayer, SFX_Discovery_*,
     index cached, Integer.MIN_VALUE = missing) + chat + Exploration XP through 0.1's owed ledger (no boosters) + titles.
     Secret spots show as "??? Secret spot" on /explore until found (no name, XP or position anywhere, bridge included).
  CHECKLIST [4]  Per world: every spot with checklist=yes (automatic), chest (one recorded loot chest), chests N (open N loot chests in
     this world), zone (a Hytale region entered IN THIS WORLD - per profile per world from 0.2 on, players/<pkey>/zones.txt; 0.1's
     global region record still pays zone XP and titles but never ticks an entry), custom (admin text; ticked by command, the admin
     page or the bridge explore:fn:complete). Progress per profile per world, Checklist tab on /explore, explore:pct:<uuid>. Optional
     100% reward (XP + coins; coins only through coins:fn:add when SkyyCoins is present; both default 0 = off), paid once per profile
     per world.
  ADMIN PAGE /exploreadmin [6]  inline, 1120 x 900, tabs Spots | Checklist | Island; list left, editor right; text boxes use the
     verified SkyyGuilds / SkyySacks TextField pattern (several @Keys on one button = vanilla LaunchPadSettingsPage); rebuilt only after
     clicks, at most once a second; the permission is re-checked on every click; Remove needs a second click within 10 s.
     /exploreadmin set <key> <value> | get <key> change EVERY config.properties key in game (rewrites the file in place, then reloads).
     admin.log records who changed what. /exploreadmin help lists every command.
  PROFILES / MULTIPLAYER [8]  New per-profile files players/<pkey>/spots.txt, ticks.txt, done.txt, zones.txt (append-only, 0.1
     ignores them: 0.1 -> 0.2 needs no migration, rolling back 0.2 -> 0.1 loses nothing, no "never go back" rule). Spot / entry ids come from ONE
     global counter (worlds/ids.properties), never reused. The loot chest award (it holds 0.1's chest-luck roll, the only item move)
     now also waits profile.afterSwitchSeconds (30, SkyyVault rule) after a profile switch or a finished profile:busy - nothing is
     recorded meanwhile, so the next open after the wait counts ("Loot chests count again in N s", at most every 10 s).
  SETTINGS [9]  registers explore.chunkXp + explore.finds (research/Settings-Spec.md 3.12); only the chat lines are gated.
  Bridge adds: explore:pct:<uuid>, explore:fn:complete, explore:fn:pct, explore:<uuid> gains ",spots:<n>,secrets:<n>,island:<d>/<t>".
  LEFT OUT / NOT BUILT (server phase, spec 12): several islands per world, entry re-ordering, Echo Shards, warps, map reveal, finder sense,
     radius markers, undo, SkyyMenu "Mods" editor adoption. UNVERIFIED (spec 1 "NEEDS A TEST"): non-major banner look, quoted names in
     commands (underscores always work), three @Keys on one button of OUR inline page, spot-check cost with many players
     (/exploreadmin stats prints it); also GREEDY_STRING values with commas (/exploreadmin set chests.zoneMult 1,2,4,8).
  SMALL DEVIATIONS FROM THE SPEC: button labels use a dash instead of a colon / + / ? ("Secret - Yes", "Save radius and XP", "Sure -
     Remove") - a style choice only: HANDOFF section 2 says colons in inline Text are NOT proven to break anything (the old crash was an
     Anchow: typo), and the SkyySacks page still strips them, so the dash keeps our pages alike; the Island card shows "58% done" with
     the island name in its sub line (long names do not fit the 20 px value line); zone checklist entries are per world (review fix,
     see CHECKLIST - the spec used 0.1's global region record); WorldDef.bad is the SpotReg.BAD map; /exploreadmin set also checks the
     value type (true/false, on/off, yes/no; whole numbers; plain ASCII without backslashes - Properties reads the file as ISO-8859-1).
  REVIEW FIXES (2026-09-25): refused world saves are reported (above); zone entries per world (above); "check remove <spot>" and the
     Checklist tab's "Take off the checklist" confirm with a second call within 10 s like every other remove (spec 5 table); the 0.2
     config block is added through config.properties.tmp + an atomic move; SpotReg.edited() takes no lock when the file is unchanged
     (an admin command never waits behind another world's save); the chunk index is built in linear time.

---- 0.1 description (still true) ----

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

VERSION = "0.2"
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
    # 0.2 (spec section 1)
    "L2O": "it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap",
    "SEV": "com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent",
    "SNU": "com.hypixel.hytale.server.core.universe.world.SoundUtil",
    "SCAT": "com.hypixel.hytale.protocol.SoundCategory",
    "TP": "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "HR": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "TPH": "com.hypixel.hytale.builtin.teleport.components.TeleportHistory",
    "PGE": "com.hypixel.hytale.protocol.packets.interface_.Page",
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
             ("java.util.Map", "putIfAbsent"), ("java.util.Map", "remove"),
             # 0.2 (spec 10 "Tokens and probes")
             ("ETU", "showEventTitleToPlayer"), ("SNU", "playSoundEvent2dToPlayer"), ("SEV", "getAssetMap"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"), ("SCAT", "UI"),
             ("TP", "createForPlayer"), ("TP", "getComponentType"), ("R3F", "x"), ("R3F", "y"), ("R3F", "z"),
             ("HR", "getRotation"), ("HR", "getComponentType"), ("TPH", "append"), ("TPH", "getComponentType"),
             ("PGM", "setPage"), ("PGE", "None"), ("L2O", "get"), ("L2O", "put"), ("CHU", "indexChunk"),
             ("CHU", "chunkCoordinate"), ("ATY", "GREEDY_STRING"), ("ATY", "PLAYER_REF"), ("ATY", "STRING"), ("EVD", "append"),
             ("UEB", "addEventBinding"), ("ST", "addComponent"), ("ST", "ensureAndGetComponent"), ("PR", "getWorldUuid"),
             ("UNI", "getWorld"), ("V3D", "y"), ("CTX", "get"), ("WLD", "getName")):
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
    # 0.2: sound events (spec 1 "Sound ids"): Server/Audio/SoundEvents/**/<id>.json
    SOUND_IDS = set(os.path.basename(n)[:-5] for n in NAMES_ALL if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json"))

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
    # 0.2 (spec 7.4): kind 4 = discovery spots found (all worlds), kind 5 = secret spots found
    ("discoverer", "Discoverer", 4, 25, "", "Find 25 discovery spots"),
    ("secretkeeper", "Secret Keeper", 5, 10, "", "Find 10 secret spots"),
]
assert len(TITLES) == 23 and len(set(t[0] for t in TITLES)) == 23
assert len(TITLES) < 64   # the earned mask is a long
for t in TITLES:
    assert re.match(r"^[a-z]+$", t[0]), t
    for r in (t[4].split(",") if t[4] else []): assert r in DISC, (t, r)
KIND_COLOR = ["#9fd0ff", "#9adf86", "#ffd27a", "#c8a0ff", "#ffb070", "#d890ff"]

# ---- page icons (0.2: cards 6 Discoveries + 7 Island)
CARD_ICON = [must(i) for i in ("Tool_Map", "Objective_Treasure_Map", "Furniture_Ancient_Chest_Small", "Deco_Map", "Rock_Gem_Ruby", "Deco_Scroll",
                               "Furniture_Flag_Orange", "Deco_Book_Pile_Small")]
CARD_HEAD = ["Exploration level", "Zones", "Loot chests", "Map", "Chest luck", "Title", "Discoveries", "Island checklist"]
CARD_COLOR = ["#e0a040", "#9adf86", "#ffd27a", "#c8a0ff", "#ff9a9a", "#9fd0ff", "#ffb070", "#9adf86"]

# ---- 0.2 sounds (spec 1 / 2.5): the engine's zone-discovery sound events must exist
DISC_SOUNDS = ["SFX_Discovery_Z%d_%s" % (z, l) for z in (1, 2, 3, 4) for l in ("Short", "Medium")]
for sid in DISC_SOUNDS:
    if sid not in SOUND_IDS: raise SystemExit("sound event %s has no Server/Audio/SoundEvents/**/%s.json" % (sid, sid))
SND_SPOT, SND_SECRET, SND_CHECK = "SFX_Discovery_Z1_Short", "SFX_Discovery_Z1_Medium", "SFX_Discovery_Z2_Medium"
assert SND_SPOT in SOUND_IDS and SND_SECRET in SOUND_IDS and SND_CHECK in SOUND_IDS

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
# ---- 0.2 block (spec 2.5): appended ONCE to an existing 0.1 file (when no line holds spots.enabled=), part of a fresh file
B02 = ["# ---------- SkyyExploration 0.2: discovery spots, secret spots, island checklists ----------",
       "# Spots and checklists are set up IN GAME: /exploreadmin (admin page) or /exploreadmin spot|check|island ... (perm skyyexploration.admin).",
       "# Each world's list lives in worlds/<world>.properties. Any key in this file: /exploreadmin set <key> <value> (writes this file).",
       "spots.enabled=true",
       "# how often each player is checked against the spots of their world (ms): 250..500 = 4 to 2 times a second",
       "spots.checkMs=333",
       "spots.defaultRadius=6",
       "spots.maxRadius=64",
       "spots.defaultXp=500",
       "spots.secretXp=1500",
       "spots.maxPerWorld=500",
       "# banner (title in the middle of the screen) + sound on the first arrival; at most one banner per bannerGapMs per player",
       "spots.banner=true",
       "spots.bannerGapMs=5000",
       "spots.major=false",
       "spots.secretMajor=true",
       "# sound event ids (empty = no sound)",
       "spots.sound=" + SND_SPOT,
       "spots.secretSound=" + SND_SECRET,
       "checklist.enabled=true",
       "checklist.maxEntries=300",
       "# \"Add loot chest here\" takes the nearest recorded loot chest within this many blocks",
       "checklist.chestRadius=8",
       "checklist.sound=" + SND_CHECK,
       "# loot chests (the only item reward) wait this long after a profile switch (SkyyVault rule: SkyyProfiles keeps its switch marker 30 s)",
       "profile.afterSwitchSeconds=30",
       "# every in-game admin change is written to admin.log (who, when, what)",
       "admin.log=true"]
BLOCK02 = "\n".join(B02) + "\n"
DEFAULTS = "\n".join(DL) + "\n" + BLOCK02
assert all(ord(ch) < 128 for ch in DEFAULTS)

# ---- every key of the full DEFAULTS (0.1 + 0.2, including the "# key=" override lines) = what /exploreadmin set|get accept
KEY_RE = re.compile(r"^#?\s*([A-Za-z][A-Za-z0-9_.]*)=")
KEYS = []
for ln in DEFAULTS.splitlines():
    km = KEY_RE.match(ln.strip())
    if km and km.group(1) not in KEYS: KEYS.append(km.group(1))
for ln in B02:   # every 0.2 key appears exactly once in DEFAULTS
    km = KEY_RE.match(ln)
    if km and not ln.startswith("#"):
        assert sum(1 for x in DEFAULTS.splitlines() if x.startswith(km.group(1) + "=")) == 1, km.group(1)
assert len(KEYS) == len(set(KEYS))
# live (in-memory) value of every scalar key: (type, Java expression inside ExpCfg); b bool, l long/int, d double, s string, L list
LIVE = {
    "exploration.excludeWorldPrefixes": ("L", "join(EX_PREFIX)"), "exploration.excludeWorlds": ("L", "join(EX_WORLDS)"),
    "noFlyingXp": ("b", "NO_FLYING"), "creativeXp": ("b", "CREATIVE_XP"), "chests.enabled": ("b", "CHESTS_ON"),
    "chests.base": ("l", "CHEST_BASE"), "chests.zoneMult": ("L", "djoin(CHEST_ZM)"), "chests.tierMult": ("L", "djoin(CHEST_TM)"),
    "chests.xpDefault": ("l", "CHEST_DEF"), "chests.pollMs": ("l", "POLL_MS"), "chests.pollMaxMs": ("l", "POLL_MAX_MS"),
    "luck.enabled": ("b", "LUCK_ON"), "luck.perLevel": ("d", "LUCK_PER"), "luck.max": ("d", "LUCK_MAX"),
    "scav.coinsPerLevel": ("l", "SCAV_PER"), "chunks.enabled": ("b", "CHUNKS_ON"), "chunks.xp": ("l", "CHUNK_XP"),
    "chunks.zoneMult": ("L", "djoin(CHUNK_ZM)"), "chunks.maxPaidPerWorld": ("l", "CHUNK_CAP"),
    "chunks.payWhileGliding": ("b", "PAY_GLIDE"), "chunks.payWhileMounted": ("b", "PAY_MOUNT"), "chunks.feedbackMs": ("l", "FEEDBACK_MS"),
    "zones.enabled": ("b", "ZONES_ON"), "zones.banner": ("b", "BANNER"), "zone.xpDefault": ("l", "ZONE_DEF"),
    "titles.chatPrefix": ("b", "CHAT_PREFIX"), "titles.chatPriority": ("l", "CHAT_PRIORITY"), "bridge.retryMs": ("l", "RETRY_MS"),
    "display.staminaPerLevel": ("d", "STA_PER"),
    "spots.enabled": ("b", "SPOTS_ON"), "spots.checkMs": ("l", "SPOT_MS"), "spots.defaultRadius": ("l", "SPOT_R"),
    "spots.maxRadius": ("l", "SPOT_RMAX"), "spots.defaultXp": ("l", "SPOT_XP"), "spots.secretXp": ("l", "SECRET_XP"),
    "spots.maxPerWorld": ("l", "SPOT_MAX"), "spots.banner": ("b", "SPOT_BANNER"), "spots.bannerGapMs": ("l", "BANNER_GAP"),
    "spots.major": ("b", "MAJOR"), "spots.secretMajor": ("b", "SECRET_MAJOR"), "spots.sound": ("s", "SOUND"),
    "spots.secretSound": ("s", "SECRET_SOUND"), "checklist.enabled": ("b", "CHECK_ON"), "checklist.maxEntries": ("l", "CHECK_MAX"),
    "checklist.chestRadius": ("l", "CHEST_R"), "checklist.sound": ("s", "CHECK_SOUND"),
    "profile.afterSwitchSeconds": ("l", "AFTER_SWITCH_MS / 1000L"), "admin.log": ("b", "ADMIN_LOG"),
}
SCALAR_KEYS = [k for k in KEYS if not k.startswith("chest.xp.") and not k.startswith("zone.xp.")]
assert sorted(SCALAR_KEYS) == sorted(LIVE), (set(SCALAR_KEYS) ^ set(LIVE))
assert sum(1 for k in KEYS if k.startswith("chest.xp.")) == len(DLS) and sum(1 for k in KEYS if k.startswith("zone.xp.")) == len(REG)

# ================= classes =================
defs = pool.makeClass(PKG + ".ExpDefs")
cfg = pool.makeClass(PKG + ".ExpCfg")
dat = pool.makeClass(PKG + ".ExpData")
est = pool.makeClass(PKG + ".ExpState")
eio = pool.makeClass(PKG + ".ExpIO")
reg = pool.makeClass(PKG + ".ChestReg")
spd = pool.makeClass(PKG + ".SpotDef")         # 0.2
edf = pool.makeClass(PKG + ".EntryDef")        # 0.2
wdf = pool.makeClass(PKG + ".WorldDef")        # 0.2
srg = pool.makeClass(PKG + ".SpotReg")         # 0.2
wst = pool.makeClass(PKG + ".WorldSaveTask")   # 0.2
sto = pool.makeClass(PKG + ".ExpStore")
stk = pool.makeClass(PKG + ".SaveTask")
skl = pool.makeClass(PKG + ".ExpSkill")
exx = pool.makeClass(PKG + ".ExpXp")
ttl = pool.makeClass(PKG + ".ExpTitles")
esp = pool.makeClass(PKG + ".ExpSpot")         # 0.2
eck = pool.makeClass(PKG + ".ExpCheck")        # 0.2
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
cfn = pool.makeClass(PKG + ".ExpCompleteFn")   # 0.2
pfn = pool.makeClass(PKG + ".ExpPctFn")        # 0.2
page = pool.makeClass(PKG + ".ExplorePage", pool.get(T["PAGE"]))
aop = pool.makeClass(PKG + ".ExAdminOps")      # 0.2
apg = pool.makeClass(PKG + ".AdminPage", pool.get(T["PAGE"]))   # 0.2
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
# 0.2 text rules (spec 2.4): control characters, | and \ dropped, _ -> space, trimmed, clipped to max; "" = refused
M(defs, r"""
public static String clean(String s, int max) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    char c = s.charAt(i);
    if (c < ' ' || c == 127 || c == '|' || c == '\\') continue;
    if (c == '_') c = ' ';
    sb.append(c);
  }
  String t = sb.toString().trim();
  while (t.indexOf("  ") >= 0) t = t.replace("  ", " ");
  if (t.length() > max) t = t.substring(0, max).trim();
  return t;
}""")
# name key for unique / prefix matching: lower case, no spaces
M(defs, r"""
public static String nkey(String s) {
  if (s == null) return "";
  return clean(s, 200).toLowerCase().replace(" ", "");
}""")
M(defs, r"""
public static boolean isDigits(String s) {
  if (s == null || s.length() == 0 || s.length() > 15) return false;
  for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); if (c < '0' || c > '9') return false; }
  return true;
}""")
M(defs, r"""
public static int unX(long k) {
  return (int) (k >> 38);
}""")
M(defs, r"""
public static int unZ(long k) {
  return (int) ((k << 26) >> 38);
}""")
M(defs, r"""
public static int unY(long k) {
  return (int) ((k << 52) >> 52);
}""")
# "123" -> 123, anything else -> def (whole numbers only, commas allowed: 1,500)
M(defs, r"""
public static long parseNum(String s, long def) {
  if (s == null) return def;
  String t = s.trim().replace(",", "").replace("_", "");
  if (t.length() == 0 || t.length() > 12) return def;
  try { return Long.parseLong(t); } catch (Throwable e) { return def; }
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
             "boolean CHAT_PREFIX = true", "int CHAT_PRIORITY = 30000", "long RETRY_MS = 5000L", "double STA_PER = 0.1",
             # 0.2 (spec 2.5); BANNER stays zones.banner
             "boolean SPOTS_ON = true", "long SPOT_MS = 333L", "double SPOT_S = 0.333", "int SPOT_R = 6", "int SPOT_RMAX = 64",
             "long SPOT_XP = 500L", "long SECRET_XP = 1500L", "int SPOT_MAX = 500", "boolean SPOT_BANNER = true", "long BANNER_GAP = 5000L",
             "boolean MAJOR = false", "boolean SECRET_MAJOR = true", 'String SOUND = "%s"' % SND_SPOT, 'String SECRET_SOUND = "%s"' % SND_SECRET,
             "boolean CHECK_ON = true", "int CHECK_MAX = 300", "int CHEST_R = 8", 'String CHECK_SOUND = "%s"' % SND_CHECK,
             "long AFTER_SWITCH_MS = 30000L", "boolean ADMIN_LOG = true", "long CFG_GEN = 0L", "int[] SND_IDX = null"):
    F(cfg, "public static volatile %s;" % decl)
F(cfg, "public static final String BLOCK02 = " + json.dumps(BLOCK02) + ";")
F(cfg, "public static final String[] KEYS = %s;" % jstr(KEYS))
F(cfg, "public static final String[] KEY_TYPE = %s;" % jstr([LIVE[k][0] if k in LIVE else "l" for k in KEYS]))
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
  SPOTS_ON = bool(p, "spots.enabled", true);
  SPOT_MS = clampL(lng(p, "spots.checkMs", 333L), 250L, 500L);
  SPOT_S = (double) SPOT_MS / 1000.0;
  SPOT_RMAX = (int) clampL(lng(p, "spots.maxRadius", 64L), 4L, 128L);
  SPOT_R = (int) clampL(lng(p, "spots.defaultRadius", 6L), 1L, (long) SPOT_RMAX);
  SPOT_XP = clampL(lng(p, "spots.defaultXp", 500L), 0L, 400000L);
  SECRET_XP = clampL(lng(p, "spots.secretXp", 1500L), 0L, 400000L);
  SPOT_MAX = (int) clampL(lng(p, "spots.maxPerWorld", 500L), 1L, 5000L);
  SPOT_BANNER = bool(p, "spots.banner", true);
  BANNER_GAP = clampL(lng(p, "spots.bannerGapMs", 5000L), 0L, 600000L);
  MAJOR = bool(p, "spots.major", false);
  SECRET_MAJOR = bool(p, "spots.secretMajor", true);
  SOUND = str(p, "spots.sound", "SFX_Discovery_Z1_Short");
  SECRET_SOUND = str(p, "spots.secretSound", "SFX_Discovery_Z1_Medium");
  CHECK_ON = bool(p, "checklist.enabled", true);
  CHECK_MAX = (int) clampL(lng(p, "checklist.maxEntries", 300L), 1L, 2000L);
  CHEST_R = (int) clampL(lng(p, "checklist.chestRadius", 8L), 1L, 64L);
  CHECK_SOUND = str(p, "checklist.sound", "SFX_Discovery_Z2_Medium");
  AFTER_SWITCH_MS = clampL(lng(p, "profile.afterSwitchSeconds", 30L), 0L, 120L) * 1000L;
  ADMIN_LOG = bool(p, "admin.log", true);
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
# 0.2: sound index cache, (Integer.MIN_VALUE + 1) = not resolved yet (0 can be a real index)
M(cfg, r"""
public static int[] newSnd() {
  int[] a = new int[3];
  for (int i = 0; i < 3; i++) a[i] = Integer.MIN_VALUE + 1;
  return a;
}""")
# ExpIO.moveRetry (tmp + atomic move, 5 x 20 ms retries on a Windows sharing violation) is added here because ExpCfg.ensureDefaults
# needs it - javassist compiles methods in script order; it uses nothing of ours
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
# 0.2 (spec 2.5 / 2.8): add the 0.2 block ONCE to a 0.1 file - 0.1 lines stay byte for byte. "Has it" = some line, with any leading
# '#' and spaces removed, starts with spots.enabled= (an admin who commented the key out does not get the block twice). Review fix: the
# whole new file (old bytes + block) goes to config.properties.tmp and replaces the file by an atomic move (like setKey), so a crash
# mid-write can never leave a torn block that the next start would add a second time
M(cfg, r"""
public static void ensureDefaults() {
  try {
    byte[] raw = java.nio.file.Files.readAllBytes(FILE);
    String s = new String(raw, java.nio.charset.StandardCharsets.ISO_8859_1);
    String[] ls = s.split("\n");
    for (int i = 0; i < ls.length; i++) {
      String t = ls[i].trim();
      while (t.startsWith("#")) t = t.substring(1).trim();
      if (t.startsWith("spots.enabled=")) return;
    }
    String all = s + (s.length() > 0 && !s.endsWith("\n") ? "\n" : "") + BLOCK02;
    java.nio.file.Path tmp = FILE.resolveSibling("config.properties.tmp");
    java.nio.file.Files.write(tmp, all.getBytes(java.nio.charset.StandardCharsets.ISO_8859_1), new java.nio.file.OpenOption[0]);
    @PKG@.ExpIO.moveRetry(tmp, FILE);
    info("added the 0.2 block (discovery spots, island checklists) to " + FILE);
  } catch (Throwable t) { warn("could not add the 0.2 block to config.properties (built-in defaults used for the 0.2 keys; the file is unchanged): " + t); }
}""")
M(cfg, r"""
public static synchronized String load() {
  java.util.Properties p = new java.util.Properties();
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
      info("wrote default " + FILE);
    } else ensureDefaults();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  } catch (Throwable t) { warn("could not read config.properties (built-in defaults used): " + t); }
  apply(p);
  SND_IDX = newSnd();
  CFG_GEN = CFG_GEN + 1L;
  return "chests " + (CHESTS_ON ? "on" : "off") + ", luck " + (LUCK_ON ? "on" : "off") + ", chunks " + (CHUNKS_ON ? "on" : "off") + ", zones " + (ZONES_ON ? "on" : "off") + ", spots " + (SPOTS_ON ? "on" : "off") + ", checklists " + (CHECK_ON ? "on" : "off") + ", " + CHEST_XP.size() + " chest / " + ZONE_XP.size() + " zone XP lines";
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
# ---- 0.2: why a world is excluded (admin page / command replies)
M(cfg, r"""
public static String excludedWhy(String wn) {
  if (wn == null) return "no world";
  String l = wn.toLowerCase();
  String[] px = EX_PREFIX;
  for (int i = 0; i < px.length; i++) if (px[i].length() > 0 && l.startsWith(px[i].toLowerCase())) return "its name starts with " + px[i] + " - exploration.excludeWorldPrefixes";
  return "listed in exploration.excludeWorlds";
}""")
M(cfg, r"""
public static String join(String[] a) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); sb.append(a[i]); }
  return sb.toString();
}""")
M(cfg, r"""
public static String djoin(double[] a) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); sb.append(@PKG@.ExpDefs.num(a[i])); }
  return sb.toString();
}""")
_live = "\n".join('  if (k.equals("%s")) return String.valueOf(%s);' % (k, LIVE[k][1]) for k in sorted(LIVE))
M(cfg, r"""
public static String live(String k) {
  if (k == null) return null;
  if (k.startsWith("chest.xp.")) return String.valueOf(chestXp(k.substring(9)));
  if (k.startsWith("zone.xp.")) return String.valueOf(zoneXp(k.substring(8)));
""" + _live + r"""
  return null;
}""")
# -1 = not a key. chest.xp.<droplist> / zone.xp.<region> accept any id (letters, digits, _), not only the ones listed in the file
M(cfg, r"""
public static int keyIndex(String k) {
  if (k == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}""")
M(cfg, r"""
public static String keyType(String k) {
  int i = keyIndex(k);
  if (i >= 0) return KEY_TYPE[i];
  String id = null;
  if (k != null && k.startsWith("chest.xp.")) id = k.substring(9);
  else if (k != null && k.startsWith("zone.xp.")) id = k.substring(8);
  if (id == null || id.length() == 0 || id.length() > 80) return null;
  for (int j = 0; j < id.length(); j++) {
    char c = id.charAt(j);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return null;
  }
  return "l";
}""")
# the text after "key=" on the first uncommented line, or null
M(cfg, r"""
public static synchronized String fileValue(String k) {
  try {
    String s = new String(java.nio.file.Files.readAllBytes(FILE), java.nio.charset.StandardCharsets.ISO_8859_1);
    String[] ls = s.split("\n");
    for (int i = 0; i < ls.length; i++) {
      String t = ls[i].trim();
      if (t.startsWith(k + "=")) return t.substring(k.length() + 1).trim();
    }
  } catch (Throwable t) { }
  return null;
}""")
# cached sound index (spec 2.5): 0 spot, 1 secret, 2 checklist; Integer.MIN_VALUE = missing (one WARN, nothing played)
M(cfg, r"""
public static int sound(int i) {
  int[] a = SND_IDX;
  if (a == null) { a = newSnd(); SND_IDX = a; }
  int v = a[i];
  if (v != Integer.MIN_VALUE + 1) return v;
  String id = i == 0 ? SOUND : (i == 1 ? SECRET_SOUND : CHECK_SOUND);
  int idx = Integer.MIN_VALUE;
  if (id != null && id.length() > 0) {
    try { idx = @SEV@.getAssetMap().getIndex(id); } catch (Throwable t) { idx = Integer.MIN_VALUE; }
    if (idx == Integer.MIN_VALUE) warnEvery("sound|" + id, 3600000L, "sound event '" + id + "' is not in the game assets - it is not played (spots.sound / spots.secretSound / checklist.sound)");
  }
  a[i] = idx;
  return idx;
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
# 0.2 (spec 2.7): found spots per world, ticked custom entries, worlds whose 100% reward was paid; counters of found spots (all worlds)
F(dat, "public java.util.concurrent.ConcurrentHashMap found = new java.util.concurrent.ConcurrentHashMap();")    # wf -> CHM spotId -> TRUE
F(dat, "public java.util.concurrent.ConcurrentHashMap ticks = new java.util.concurrent.ConcurrentHashMap();")    # entryId -> TRUE
F(dat, "public java.util.concurrent.ConcurrentHashMap doneW = new java.util.concurrent.ConcurrentHashMap();")    # wf -> TRUE
# review fix: Hytale regions entered PER WORLD (checklist zone entries only; d.zones stays 0.1's global record for zone XP + titles)
F(dat, "public java.util.concurrent.ConcurrentHashMap zoneW = new java.util.concurrent.ConcurrentHashMap();")    # wf -> CHM region -> TRUE
F(dat, "public volatile long spots;")
F(dat, "public volatile long secrets;")
F(dat, "public volatile boolean checkDirty;")
C(dat, "public ExpData() { this.checkDirty = true; }")

# ================= ExpState: per-player tick state (memory only, the player's world thread) =================
for decl in ("double acc", "boolean hasLast", "long lastChunk", "String lastWf", "long pendXp", "long pendN", "long pendStart",
             "boolean pendCapped", "long lastFlush",
             # 0.2 (spec 2.7): spot check accumulator, the spot we stand in, banner gap, pct cache, busy edge, the cached world of the
             # spot check (same world name object + same SpotReg.GEN + same config generation = reuse, no lookup), chest gate message
             "double spotAcc", "String inside", "String insideWf", "long lastBanner", "String pctWf", "long pctGen", "long pctCfg",
             "String pctStr", "boolean wasBusy", "int[] tmp", "String spWn", "long spGen", "long spCfg", "Object spWd", "long lastGateMsg"):
    F(est, "public %s;" % decl)
C(est, "public ExpState() { this.tmp = new int[4]; this.pctGen = -1L; this.spGen = -1L; }")

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

# ---- 0.2: profile switch times (SkyyVault afterSwitch idea, spec 8), the last epoch seen per UUID (moved here from ExpTick so the
# chest award can see a switch the 1 s tick has not noticed yet), admin.log, the settings registry helpers (Settings-Spec 1.3)
F(eio, "public static final java.util.concurrent.ConcurrentHashMap SWITCHED = new java.util.concurrent.ConcurrentHashMap();")  # UUID -> Long
F(eio, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")     # UUID -> Long
F(eio, "public static java.nio.file.Path ADMIN;")
M(eio, r"""
public static long epochNow(java.util.UUID u) {
  try {
    Object o = bridge().get("profile:epoch:" + u.toString());
    if (o instanceof Number) return ((Number) o).longValue();
  } catch (Throwable t) { }
  return -1L;
}""")
# ms the chest award still waits after a profile switch / finished profile:busy (0 = go); a new epoch the tick has not seen yet waits
# the full time (the tick records the switch within 1 s)
M(eio, r"""
public static long switchWait(java.util.UUID u) {
  long gap = @PKG@.ExpCfg.AFTER_SWITCH_MS;
  if (gap <= 0L) return 0L;
  long e = epochNow(u);
  Object last = EPOCH.get(u);
  if (e >= 0L && last != null && ((Long) last).longValue() != e) return gap;
  Object at = SWITCHED.get(u);
  if (at == null) return 0L;
  long left = gap - (System.currentTimeMillis() - ((Long) at).longValue());
  return left > 0L ? left : 0L;
}""")
M(eio, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
M(eio, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyExploration", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")
# TRUE = the setting was written through settings:fn:set; null = no settings registry (SkyyMenu 0.2 not installed)
M(eio, r"""
public static Boolean setSetting(java.util.UUID u, String key, boolean v) {
  try {
    Object f = bridge().get("settings:fn:set");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key, Boolean.valueOf(v) });
      return Boolean.TRUE.equals(r) ? Boolean.TRUE : Boolean.FALSE;
    }
  } catch (Throwable t) { return Boolean.FALSE; }
  return null;
}""")
# admin.log (spec 2.6): "2026-09-24 22:10:03 | Skyy 3f2a... | fens | spot add s3 ..." through the ordered append queue
M(eio, r"""
public static void adminLog(@PR@ pr, String world, String what) {
  try {
    if (!@PKG@.ExpCfg.ADMIN_LOG || ADMIN == null) return;
    String t = java.time.LocalDateTime.now().withNano(0).toString().replace('T', ' ');
    String who = pr == null ? "console" : pr.getUsername() + " " + pr.getUuid();
    String w = what == null ? "" : what.replace('\n', ' ').replace('\r', ' ');
    append(ADMIN, utf8(t + " | " + who + " | " + (world == null ? "-" : world) + " | " + w + "\n"));
  } catch (Throwable e) { }
}""")

# (ExpCfg.setKey is added here, after the ExpIO helpers it uses - javassist compiles methods in script order)
# 0.2 (spec 5 "set"): rewrite config.properties IN PLACE - the first "key=" line is replaced, else the first commented "# key=" line
# (un-commented), else the line is appended; bytes read and written as ISO-8859-1 (what Properties.load reads) so every other line
# stays byte for byte; CRLF files keep CRLF. Then load(). Returns { reply, old value or null, new value }.
M(cfg, r"""
public static synchronized String[] setKey(String key, String val) {
  String k = key == null ? "" : key.trim();
  String ty = keyType(k);
  if (ty == null) return new String[] { "-Unknown key '" + k + "' - the keys are the lines of config.properties (/exploreadmin help)", null, null };
  String v = val == null ? "" : val.trim();
  if (v.length() > 200) return new String[] { "-A value can be at most 200 characters (nothing changed)", null, null };
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (c < ' ' || c > '~' || c == '\\') return new String[] { "-Values are plain text without \\ or special characters (nothing changed)", null, null };
  }
  if (ty.equals("b")) {
    String l = v.toLowerCase();
    if (l.equals("true") || l.equals("on") || l.equals("yes") || l.equals("1")) v = "true";
    else if (l.equals("false") || l.equals("off") || l.equals("no") || l.equals("0")) v = "false";
    else return new String[] { "-" + k + " is true or false (nothing changed)", null, null };
  } else if (ty.equals("l")) {
    try { Long.parseLong(v); } catch (Throwable t) { return new String[] { "-" + k + " is a whole number (nothing changed)", null, null }; }
  } else if (ty.equals("d")) {
    try { Double.parseDouble(v); } catch (Throwable t) { return new String[] { "-" + k + " is a number such as 0.25 (nothing changed)", null, null }; }
  }
  String old = null;
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) load();
    String s = new String(java.nio.file.Files.readAllBytes(FILE), java.nio.charset.StandardCharsets.ISO_8859_1);
    String nl = s.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    String[] ls = s.split("\n", -1);
    int hit = -1;
    int hitC = -1;
    for (int i = 0; i < ls.length; i++) {
      String t = ls[i].trim();
      if (t.startsWith(k + "=")) { hit = i; break; }
      if (hitC < 0 && t.startsWith("#")) {
        String c = t;
        while (c.startsWith("#")) c = c.substring(1).trim();
        if (c.startsWith(k + "=")) hitC = i;
      }
    }
    StringBuilder sb = new StringBuilder();
    int at = hit >= 0 ? hit : hitC;
    if (hit >= 0) old = ls[hit].trim().substring(k.length() + 1).trim();
    for (int i = 0; i < ls.length; i++) {
      String line = ls[i];
      if (line.endsWith("\r")) line = line.substring(0, line.length() - 1);
      if (i == at) line = k + "=" + v;
      if (i == ls.length - 1 && line.length() == 0) break;
      sb.append(line).append(nl);
    }
    if (at < 0) sb.append(k).append('=').append(v).append(nl);
    java.nio.file.Path tmp = FILE.resolveSibling("config.properties.tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes(java.nio.charset.StandardCharsets.ISO_8859_1), new java.nio.file.OpenOption[0]);
    @PKG@.ExpIO.moveRetry(tmp, FILE);
  } catch (Throwable t) {
    warn("could not write config.properties for " + k + ": " + t);
    return new String[] { "-Could not write config.properties (" + t.getClass().getSimpleName() + ") - nothing changed", null, null };
  }
  load();
  String now = live(k);
  String res = "+" + k + " = " + v + (old == null ? " (was not in the file)" : " (was " + old + ")");
  boolean clamped = false;
  if (now != null && !now.equals(v) && !ty.equals("L") && !ty.equals("s")) {
    try { clamped = Double.parseDouble(now) != Double.parseDouble(v); } catch (Throwable t) { clamped = !ty.equals("b"); }
  }
  if (clamped) res = res + " - outside the allowed range, the server uses " + now;
  res = res + (k.equals("titles.chatPriority") ? " - needs a restart" : " - applied now");
  return new String[] { res, old, v };
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
# 0.2 (spec 4.1): the nearest recorded loot chest within r blocks of x y z, or null (one walk per admin click; compact() unpack math)
M(reg, r"""
public static int[] nearest(String wf, int x, int y, int z, int r) {
  Object o = W.get(wf);
  if (o == null) return null;
  int[] best = null;
  long bd = (long) r * (long) r + 1L;
  java.util.Iterator it = ((java.util.concurrent.ConcurrentHashMap) o).keySet().iterator();
  while (it.hasNext()) {
    long k = ((Long) it.next()).longValue();
    int cx = @PKG@.ExpDefs.unX(k);
    int cy = @PKG@.ExpDefs.unY(k);
    int cz = @PKG@.ExpDefs.unZ(k);
    long dx = (long) (cx - x);
    long dy = (long) (cy - y);
    long dz = (long) (cz - z);
    long d = dx * dx + dy * dy + dz * dz;
    if (d < bd) { bd = d; best = new int[] { cx, cy, cz }; }
  }
  return best;
}""")

# ================= 0.2: SpotDef / EntryDef / WorldDef (spec 2.7, fields + constructor only) =================
for decl in ("String id", "long n", "String name", "int x", "int y", "int z", "int r", "double cx", "double cy", "double cz", "double r2",
             "long xp", "boolean secret", "boolean check"):
    F(spd, "public %s;" % decl)
C(spd, r"""
public SpotDef(String id, long n, String name, int x, int y, int z, int r, long xp, boolean secret, boolean check) {
  this.id = id; this.n = n; this.name = name; this.x = x; this.y = y; this.z = z; this.r = r;
  this.cx = (double) x + 0.5; this.cy = (double) y; this.cz = (double) z + 0.5; this.r2 = (double) r * (double) r;
  this.xp = xp; this.secret = secret; this.check = check;
}""")
# type 1 chest (arg "x y z"), 2 chests (cnt = N), 3 zone (arg = region id), 4 custom
for decl in ("String id", "long n", "int type", "String arg", "String text", "int x", "int y", "int z", "long cnt"):
    F(edf, "public %s;" % decl)
C(edf, r"""
public EntryDef(String id, long n, int type, String arg, String text, int x, int y, int z, long cnt) {
  this.id = id; this.n = n; this.type = type; this.arg = arg; this.text = text; this.x = x; this.y = y; this.z = z; this.cnt = cnt;
}""")
# an IMMUTABLE snapshot of one world's setup: every change builds a new one (copy-on-write, readers never lock)
for decl in ("String wf", "String world", "String name", "boolean checklist", "long rewardXp", "long rewardCoins", "long spotXp",
             "long secretXp", "@PKG@.SpotDef[] spots", "@PKG@.EntryDef[] entries", "@L2O@ index", "int secrets", "int checks"):
    F(wdf, "public %s;" % decl)
C(wdf, "public WorldDef() { }")

# ================= 0.2: SpotReg - every world's spots + checklist (worlds/<wf>.properties), the id counter, the hand-edit guard ===========
F(srg, "public static java.nio.file.Path DIR;")
F(srg, "public static final java.util.concurrent.ConcurrentHashMap W = new java.util.concurrent.ConcurrentHashMap();")      # wf -> WorldDef
F(srg, "public static final java.util.concurrent.ConcurrentHashMap ENTRY = new java.util.concurrent.ConcurrentHashMap();")  # entry id -> wf
F(srg, "public static final java.util.concurrent.ConcurrentHashMap STAMP = new java.util.concurrent.ConcurrentHashMap();")  # wf -> long[2]
F(srg, "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();")  # wf -> TRUE
F(srg, "public static final java.util.concurrent.ConcurrentHashMap FILE = new java.util.concurrent.ConcurrentHashMap();")   # wf -> Path
F(srg, "public static final java.util.concurrent.ConcurrentHashMap BAD = new java.util.concurrent.ConcurrentHashMap();")    # wf -> reason
F(srg, "public static final Object IO = new Object();")   # lock order: IO -> SpotReg.class (mutations take only the class lock)
F(srg, "public static volatile long GEN = 0L;")
F(srg, "public static long NEXT = 1L;")
F(srg, "public static long IDS_DISK = -1L;")
# spot check cost (spec 5 "stats"): every check counted, 1 in 16 timed; ExpSaver keeps the last 10 s window
F(srg, "public static final java.util.concurrent.atomic.AtomicLong CHECKS = new java.util.concurrent.atomic.AtomicLong();")
F(srg, "public static final java.util.concurrent.atomic.AtomicLong TIMED = new java.util.concurrent.atomic.AtomicLong();")
F(srg, "public static final java.util.concurrent.atomic.AtomicLong NANOS = new java.util.concurrent.atomic.AtomicLong();")
F(srg, "public static volatile long[] LAST10 = new long[3];")
F(srg, "public static long[] PREV10 = new long[3];")
M(srg, r"""
public static @PKG@.WorldDef blank(String world, String wf) {
  @PKG@.WorldDef w = new @PKG@.WorldDef();
  w.wf = wf; w.world = world; w.name = world; w.checklist = true; w.rewardXp = 0L; w.rewardCoins = 0L; w.spotXp = -1L; w.secretXp = -1L;
  w.spots = new @PKG@.SpotDef[0]; w.entries = new @PKG@.EntryDef[0];
  return w;
}""")
M(srg, r"""
public static @PKG@.WorldDef copy(@PKG@.WorldDef o) {
  @PKG@.WorldDef w = new @PKG@.WorldDef();
  w.wf = o.wf; w.world = o.world; w.name = o.name; w.checklist = o.checklist; w.rewardXp = o.rewardXp; w.rewardCoins = o.rewardCoins;
  w.spotXp = o.spotXp; w.secretXp = o.secretXp; w.spots = o.spots; w.entries = o.entries;
  return w;
}""")
M(srg, r"""
public static void sortSpots(@PKG@.SpotDef[] a) {
  for (int i = 1; i < a.length; i++) {
    @PKG@.SpotDef v = a[i];
    int j = i - 1;
    while (j >= 0 && a[j].n > v.n) { a[j + 1] = a[j]; j--; }
    a[j + 1] = v;
  }
}""")
M(srg, r"""
public static void sortEntries(@PKG@.EntryDef[] a) {
  for (int i = 1; i < a.length; i++) {
    @PKG@.EntryDef v = a[i];
    int j = i - 1;
    while (j >= 0 && a[j].n > v.n) { a[j + 1] = a[j]; j--; }
    a[j + 1] = v;
  }
}""")
# spec 2.7 index build: chunk column key -> SpotDef[] of the spots whose sphere touches that 32x32 column. Two passes, linear in the
# number of (spot, column) cells: pass 1 collects each column's spots in an ArrayList (amortized O(1) append), pass 2 turns every list
# into the exact-size array the spot check reads (review fix: growing each bucket by one array copy per spot was quadratic per column)
M(srg, r"""
public static @L2O@ index(@PKG@.SpotDef[] sp) {
  if (sp == null || sp.length == 0) return null;
  @L2O@ m = new @L2O@();
  java.util.ArrayList keys = new java.util.ArrayList();
  for (int i = 0; i < sp.length; i++) {
    @PKG@.SpotDef s = sp[i];
    int x0 = @CHU@.chunkCoordinate(s.x - s.r);
    int x1 = @CHU@.chunkCoordinate(s.x + s.r + 1);
    int z0 = @CHU@.chunkCoordinate(s.z - s.r);
    int z1 = @CHU@.chunkCoordinate(s.z + s.r + 1);
    for (int cx = x0; cx <= x1; cx++) {
      for (int cz = z0; cz <= z1; cz++) {
        long k = @CHU@.indexChunk(cx, cz);
        java.util.ArrayList a = (java.util.ArrayList) m.get(k);
        if (a == null) { a = new java.util.ArrayList(4); m.put(k, a); keys.add(Long.valueOf(k)); }
        a.add(s);
      }
    }
  }
  for (int i = 0; i < keys.size(); i++) {
    long k = ((Long) keys.get(i)).longValue();
    java.util.ArrayList a = (java.util.ArrayList) m.get(k);
    @PKG@.SpotDef[] b = new @PKG@.SpotDef[a.size()];
    for (int j = 0; j < b.length; j++) b[j] = (@PKG@.SpotDef) a.get(j);
    m.put(k, b);
  }
  return m;
}""")
M(srg, r"""
public static @PKG@.WorldDef finish(@PKG@.WorldDef w) {
  w.index = index(w.spots);
  int se = 0;
  int ch = 0;
  for (int i = 0; i < w.spots.length; i++) { if (w.spots[i].secret) se++; if (w.spots[i].check) ch++; }
  w.secrets = se;
  w.checks = ch + w.entries.length;
  return w;
}""")
M(srg, r"""
public static @PKG@.WorldDef byWf(String wf) {
  return wf == null ? null : (@PKG@.WorldDef) W.get(wf);
}""")
M(srg, r"""
public static @PKG@.WorldDef byName(String wn) {
  if (wn == null) return null;
  return (@PKG@.WorldDef) W.get(@PKG@.ChestReg.wf(wn));
}""")
M(srg, r"""
public static java.nio.file.Path fileOf(String wf) {
  Object o = FILE.get(wf);
  return o != null ? (java.nio.file.Path) o : DIR.resolve(wf + ".properties");
}""")
M(srg, r"""
public static String fileName(String wf) {
  return "worlds/" + fileOf(wf).getFileName().toString();
}""")
M(srg, r"""
public static long[] stampOf(java.nio.file.Path f) {
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return null;
    return new long[] { java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis(), java.nio.file.Files.size(f) };
  } catch (Throwable t) { return null; }
}""")
# spec 2.3 hand-edit guard: the file differs from what the game last read or wrote (appeared, vanished or changed)
M(srg, r"""
public static boolean editedNow(String wf) {
  long[] now = stampOf(fileOf(wf));
  Object o = STAMP.get(wf);
  if (o == null) return now != null;
  if (now == null) return true;
  long[] st = (long[]) o;
  return now[0] != st[0] || now[1] != st[1];
}""")
# review fix: the usual answer (file unchanged) needs no lock, so an admin command on world A never waits on the world thread behind a
# slow save of world B (IO is shared). Only a file that LOOKS changed takes IO and checks again: that rules out the short window of a
# save of this same world (file moved, STAMP not yet updated) and a running reload (STAMP being replaced). A lock-free "unchanged"
# cannot be wrong: the stamps really match
M(srg, r"""
public static boolean edited(String wf) {
  if (!editedNow(wf)) return false;
  boolean r;
  synchronized (IO) { r = editedNow(wf); }
  return r;
}""")
# null = in-game changes of this world are allowed; else the refusal ("-...")
M(srg, r"""
public static String guard(String wf) {
  Object b = BAD.get(wf);
  if (b != null) return "-" + fileName(wf) + " " + (String) b + " - fix it, then /exploreadmin reload (nothing changed; the file is never overwritten)";
  if (edited(wf)) return "-" + fileName(wf) + " was edited outside the game - run /exploreadmin reload first (nothing changed)";
  return null;
}""")
M(srg, r"""
public static String typeName(int t) {
  if (t == 1) return "chest";
  if (t == 2) return "chests";
  if (t == 3) return "zone";
  return "custom";
}""")
M(srg, r"""
public static String defText(int type, String arg, long cnt) {
  if (type == 1) return "Hidden loot chest";
  if (type == 2) return "Open " + cnt + " loot chests on this island";
  if (type == 3) return @PKG@.ExpDefs.regionName(arg);
  return "Task";
}""")
M(srg, r"""
public static int[] xyz(String s) {
  if (s == null) return null;
  String[] q = s.trim().split(" +");
  if (q.length != 3) return null;
  try { return new int[] { Integer.parseInt(q[0]), Integer.parseInt(q[1]), Integer.parseInt(q[2]) }; } catch (Throwable t) { return null; }
}""")
M(srg, r"""
public static @PKG@.SpotDef parseSpot(String id, String v) {
  if (id == null || v == null || id.length() < 2 || id.charAt(0) != 's' || !@PKG@.ExpDefs.isDigits(id.substring(1))) return null;
  long n = Long.parseLong(id.substring(1));
  String[] q = v.split("\\|", 6);
  if (q.length < 6) return null;
  int[] p = xyz(q[0]);
  if (p == null) return null;
  long r = @PKG@.ExpDefs.parseNum(q[1], -1L);
  long xp = @PKG@.ExpDefs.parseNum(q[2], -1L);
  if (r < 0L || xp < 0L) return null;
  String sec = q[3].trim().toLowerCase();
  String chk = q[4].trim().toLowerCase();
  boolean st = sec.equals("true") || sec.equals("yes");
  boolean ct = chk.equals("true") || chk.equals("yes");
  if (!(st || sec.equals("false") || sec.equals("no")) || !(ct || chk.equals("false") || chk.equals("no"))) return null;
  String nm = @PKG@.ExpDefs.clean(q[5], 40);
  if (nm.length() == 0) return null;
  int rr = (int) @PKG@.ExpCfg.clampL(r, 1L, (long) @PKG@.ExpCfg.SPOT_RMAX);
  return new @PKG@.SpotDef("s" + n, n, nm, p[0], p[1], p[2], rr, @PKG@.ExpCfg.clampL(xp, 0L, 400000L), st, ct);
}""")
M(srg, r"""
public static @PKG@.EntryDef parseEntry(String id, String v, String fname) {
  if (id == null || v == null || !@PKG@.ExpDefs.isDigits(id)) return null;
  long n = Long.parseLong(id);
  String[] q = v.split("\\|", 3);
  if (q.length < 2) return null;
  String ty = q[0].trim().toLowerCase();
  String arg = q[1].trim();
  String tx = q.length > 2 ? @PKG@.ExpDefs.clean(q[2], 80) : "";
  String nid = String.valueOf(n);
  if (ty.equals("chest")) {
    int[] p = xyz(arg);
    if (p == null) return null;
    return new @PKG@.EntryDef(nid, n, 1, p[0] + " " + p[1] + " " + p[2], tx.length() > 0 ? tx : defText(1, arg, 0L), p[0], p[1], p[2], 0L);
  }
  if (ty.equals("chests")) {
    long c = @PKG@.ExpDefs.parseNum(arg, -1L);
    if (c < 1L) return null;
    c = @PKG@.ExpCfg.clampL(c, 1L, 100000L);
    return new @PKG@.EntryDef(nid, n, 2, String.valueOf(c), tx.length() > 0 ? tx : defText(2, arg, c), 0, 0, 0, c);
  }
  if (ty.equals("zone")) {
    if (arg.length() == 0 || arg.indexOf(' ') >= 0) return null;
    if (@PKG@.ExpDefs.region(arg) < 0) @PKG@.ExpCfg.warn(fname + ": check." + id + " names the region '" + arg + "', which is not one of Hytale's 27 regions - kept (it counts only if the game reports that region)");
    return new @PKG@.EntryDef(nid, n, 3, arg, tx.length() > 0 ? tx : defText(3, arg, 0L), 0, 0, 0, 0L);
  }
  if (ty.equals("custom")) {
    if (tx.length() == 0) return null;
    return new @PKG@.EntryDef(nid, n, 4, "", tx, 0, 0, 0, 0L);
  }
  return null;
}""")
# { WorldDef or null, Integer bad lines, String error }; UTF-8, Properties.load(Reader); world= is authoritative, not the file name
M(srg, r"""
public static Object[] parse(java.nio.file.Path f) {
  String fname = "worlds/" + f.getFileName().toString();
  java.util.Properties p = new java.util.Properties();
  try {
    java.io.Reader rd = new java.io.InputStreamReader(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]), java.nio.charset.StandardCharsets.UTF_8);
    try { p.load(rd); } finally { rd.close(); }
  } catch (Throwable t) { return new Object[] { null, Integer.valueOf(0), t.getClass().getSimpleName() + " " + t.getMessage() }; }
  String world = p.getProperty("world");
  if (world == null || world.trim().length() == 0) return new Object[] { null, Integer.valueOf(0), "it has no world= line" };
  world = world.trim();
  @PKG@.WorldDef w = blank(world, @PKG@.ChestReg.wf(world));
  String nm = @PKG@.ExpDefs.clean(p.getProperty("name"), 80);
  if (nm.length() > 0) w.name = nm;
  w.checklist = @PKG@.ExpCfg.bool(p, "checklist", true);
  w.rewardXp = @PKG@.ExpCfg.clampL(@PKG@.ExpCfg.lng(p, "reward.xp", 0L), 0L, 400000L);
  w.rewardCoins = @PKG@.ExpCfg.clampL(@PKG@.ExpCfg.lng(p, "reward.coins", 0L), 0L, 1000000000L);
  w.spotXp = @PKG@.ExpCfg.clampL(@PKG@.ExpCfg.lng(p, "spotXp", -1L), -1L, 400000L);
  w.secretXp = @PKG@.ExpCfg.clampL(@PKG@.ExpCfg.lng(p, "secretXp", -1L), -1L, 400000L);
  java.util.ArrayList sl = new java.util.ArrayList();
  java.util.ArrayList el = new java.util.ArrayList();
  java.util.HashMap ids = new java.util.HashMap();
  int bad = 0;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String key = (String) it.next();
    if (key.startsWith("spot.")) {
      @PKG@.SpotDef s = null;
      try { s = parseSpot(key.substring(5), p.getProperty(key)); } catch (Throwable t) { s = null; }
      if (s != null && ids.containsKey(s.id)) { bad++; @PKG@.ExpCfg.warn(fname + ": " + key + " repeats the spot id " + s.id + " - skipped"); }
      else if (s == null) { bad++; @PKG@.ExpCfg.warn(fname + ": bad line " + key + " skipped (spot.s<n>=<x> <y> <z>|<radius>|<xp>|<true/false>|<true/false>|<name>)"); }
      else { sl.add(s); ids.put(s.id, Boolean.TRUE); }
    } else if (key.startsWith("check.")) {
      @PKG@.EntryDef e = null;
      try { e = parseEntry(key.substring(6), p.getProperty(key), fname); } catch (Throwable t) { e = null; }
      if (e != null && ids.containsKey(e.id)) { bad++; @PKG@.ExpCfg.warn(fname + ": " + key + " repeats the entry id " + e.id + " - skipped"); }
      else if (e == null) { bad++; @PKG@.ExpCfg.warn(fname + ": bad line " + key + " skipped (check.<n>=chest|x y z|text, chests|N|text, zone|region|text or custom||text)"); }
      else { el.add(e); ids.put(e.id, Boolean.TRUE); }
    }
  }
  @PKG@.SpotDef[] sa = new @PKG@.SpotDef[sl.size()];
  for (int i = 0; i < sa.length; i++) sa[i] = (@PKG@.SpotDef) sl.get(i);
  @PKG@.EntryDef[] ea = new @PKG@.EntryDef[el.size()];
  for (int i = 0; i < ea.length; i++) ea[i] = (@PKG@.EntryDef) el.get(i);
  sortSpots(sa);
  sortEntries(ea);
  w.spots = sa;
  w.entries = ea;
  finish(w);
  return new Object[] { w, Integer.valueOf(bad), null };
}""")
# our own writer (not Properties.store): stable order + comments; names / texts are sanitized, so no escaping is needed (world: \ doubled)
M(srg, r"""
public static String text(@PKG@.WorldDef wd) {
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyExploration 0.2 - discovery spots and the island checklist of the world \"").append(wd.world).append("\".\n");
  sb.append("# Set this up IN GAME: /exploreadmin (admin page) or /exploreadmin spot|check|island ... - the game rewrites this file after every change.\n");
  sb.append("# Hand edits: stop the server first, or run /exploreadmin reload right after saving (in-game changes are refused while this file differs\n");
  sb.append("# from what the game last read or wrote).\n");
  sb.append("world=").append(wd.world.replace("\\", "\\\\")).append('\n');
  sb.append("name=").append(wd.name).append('\n');
  sb.append("checklist=").append(wd.checklist ? "true" : "false").append('\n');
  sb.append("reward.xp=").append(wd.rewardXp).append('\n');
  sb.append("reward.coins=").append(wd.rewardCoins).append('\n');
  sb.append("# default XP for NEW spots on this island (-1 = config spots.defaultXp / spots.secretXp)\n");
  sb.append("spotXp=").append(wd.spotXp).append('\n');
  sb.append("secretXp=").append(wd.secretXp).append('\n');
  sb.append("# spot.<id>=<x> <y> <z>|<radius>|<xp>|<secret true/false>|<on checklist true/false>|<name>\n");
  for (int i = 0; i < wd.spots.length; i++) {
    @PKG@.SpotDef s = wd.spots[i];
    sb.append("spot.").append(s.id).append('=').append(s.x).append(' ').append(s.y).append(' ').append(s.z).append('|').append(s.r).append('|').append(s.xp).append('|').append(s.secret ? "true" : "false").append('|').append(s.check ? "true" : "false").append('|').append(s.name).append('\n');
  }
  sb.append("# check.<id>=<type>|<arg>|<text>   type = chest (arg \"x y z\") | chests (arg N) | zone (arg region id) | custom (arg empty)\n");
  for (int i = 0; i < wd.entries.length; i++) {
    @PKG@.EntryDef e = wd.entries[i];
    sb.append("check.").append(e.id).append('=').append(typeName(e.type)).append('|').append(e.arg).append('|').append(e.text).append('\n');
  }
  return sb.toString();
}""")
M(srg, r"""
public static boolean isDefault(@PKG@.WorldDef w) {
  return w.spots.length == 0 && w.entries.length == 0 && w.name.equals(w.world) && w.checklist && w.rewardXp == 0L && w.rewardCoins == 0L && w.spotXp < 0L && w.secretXp < 0L;
}""")
# { file text or null, the id counter, "write" | "del" | "skip" } read under the class lock
M(srg, r"""
public static synchronized String[] snapWorld(String wf) {
  @PKG@.WorldDef wd = (@PKG@.WorldDef) W.get(wf);
  if (wd == null) return new String[] { null, String.valueOf(NEXT), "skip" };
  if (isDefault(wd)) return new String[] { null, String.valueOf(NEXT), "del" };
  return new String[] { text(wd), String.valueOf(NEXT), "write" };
}""")
# review fix: a change that passed guard() but whose file was hand-edited (or became unreadable) before the save task ran is never
# written - and it is no longer dropped silently: the world STAYS in DIRTY (so /exploreadmin stats and the admin page show
# "in-game change NOT saved" until /exploreadmin reload clears it), and the admin who made it gets one chat line on their next tick.
# Retrying cannot overwrite the hand edit: editedNow stays true until a reload re-reads the file (which also clears DIRTY)
F(srg, "public static final java.util.concurrent.ConcurrentHashMap LASTBY = new java.util.concurrent.ConcurrentHashMap();")  # wf -> UUID of the last in-game change
F(srg, "public static final java.util.concurrent.ConcurrentHashMap LOST = new java.util.concurrent.ConcurrentHashMap();")    # admin UUID -> chat line (ExpTick sends it)
M(srg, r"""
public static void lostChange(String wf, String why) {
  if (!DIRTY.containsKey(wf)) return;
  Object by = LASTBY.remove(wf);
  if (!(by instanceof java.util.UUID)) return;
  @PKG@.WorldDef wd = (@PKG@.WorldDef) W.get(wf);
  String wn = wd == null ? wf : wd.world;
  LOST.put(by, "[Exploration] Your last change in " + wn + " was NOT saved: " + fileName(wf) + " " + why + ". It stays active until /exploreadmin reload loads the file - then make the change again.");
}""")
# under IO: never writes a bad or hand-edited file; ids.properties first, then the world file (both tmp + atomic move)
M(srg, r"""
public static boolean saveLocked(String wf) {
  if (BAD.containsKey(wf)) { lostChange(wf, "could not be read"); @PKG@.ExpCfg.warnEvery("savebad|" + wf, 60000L, fileName(wf) + " is not saved: it could not be read (never overwritten) - fix it and /exploreadmin reload (the in-game change stays unsaved until then)"); return true; }
  if (editedNow(wf)) { lostChange(wf, "was edited outside the game before the game could write it"); @PKG@.ExpCfg.warnEvery("saveedit|" + wf, 60000L, fileName(wf) + " changed on disk since the game read it - the in-game change is NOT written (hand edits are never overwritten); /exploreadmin reload loads the file"); return true; }
  DIRTY.remove(wf);
  String[] sn = snapWorld(wf);
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    long nx = Long.parseLong(sn[1]);
    if (nx != IDS_DISK) {
      java.nio.file.Path idf = DIR.resolve("ids.properties");
      java.nio.file.Path it = DIR.resolve("ids.properties.tmp");
      java.nio.file.Files.write(it, @PKG@.ExpIO.utf8("# SkyyExploration 0.2 - the next spot / checklist entry id (ids are never reused; do not lower it)\nnext=" + nx + "\n"), new java.nio.file.OpenOption[0]);
      @PKG@.ExpIO.moveRetry(it, idf);
      IDS_DISK = nx;
    }
    if (sn[2].equals("skip")) return true;
    java.nio.file.Path f = fileOf(wf);
    if (sn[2].equals("del")) {
      java.nio.file.Files.deleteIfExists(f);
      STAMP.remove(wf);
      return true;
    }
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, @PKG@.ExpIO.utf8(sn[0]), new java.nio.file.OpenOption[0]);
    @PKG@.ExpIO.moveRetry(tmp, f);
    long[] st = stampOf(f);
    if (st != null) STAMP.put(wf, st);
    FILE.put(wf, f);
    return true;
  } catch (Throwable t) {
    @PKG@.ExpCfg.warnEvery("save|" + wf, 60000L, "could not save " + fileName(wf) + " (kept in memory, retried every 2 s): " + t);
    return false;
  }
}""")
M(srg, r"""
public static boolean saveSync(String wf) {
  boolean r;
  synchronized (IO) { r = saveLocked(wf); }
  return r;
}""")
M(srg, r"""
public static void saveWorld(String wf) {
  if (!saveSync(wf)) DIRTY.put(wf, Boolean.TRUE);
}""")
wst.addInterface(pool.get("java.lang.Runnable"))
F(wst, "public String wf;")
C(wst, "public WorldSaveTask(String wf) { this.wf = wf; }")
M(wst, r"""
public void run() {
  try { @PKG@.SpotReg.saveWorld(this.wf); } catch (Throwable t) { @PKG@.SpotReg.DIRTY.put(this.wf, Boolean.TRUE); }
}""")
M(srg, r"""
public static void saveSoon(String wf) {
  DIRTY.put(wf, Boolean.TRUE);
  try { @HSV@.SCHEDULED_EXECUTOR.execute(new @PKG@.WorldSaveTask(wf)); } catch (Throwable t) { }
}""")
# every in-game change (ExAdminOps) names its admin, who is told if the save has to be refused (lostChange)
M(srg, r"""
public static void saveSoon(String wf, java.util.UUID by) {
  if (by != null) LASTBY.put(wf, by);
  saveSoon(wf);
}""")
# "", or " - in-game change NOT saved" while a refused save waits for /exploreadmin reload (stats + admin page)
M(srg, r"""
public static String unsaved(String wf) {
  return DIRTY.containsKey(wf) && (BAD.containsKey(wf) || edited(wf)) ? " - an in-game change is NOT saved" : "";
}""")
M(srg, r"""
public static void flushDirty() {
  java.util.ArrayList l = new java.util.ArrayList(DIRTY.keySet());
  for (int i = 0; i < l.size(); i++) saveWorld((String) l.get(i));
}""")
# called INSIDE a synchronized mutation: publish the new snapshot, keep ENTRY in step, GEN + 1, save soon (by the caller)
M(srg, r"""
public static void install(@PKG@.WorldDef cur, @PKG@.WorldDef nw) {
  finish(nw);
  W.put(nw.wf, nw);
  if (cur != null) {
    for (int i = 0; i < cur.entries.length; i++) if (nw.wf.equals(ENTRY.get(cur.entries[i].id))) ENTRY.remove(cur.entries[i].id);
  }
  for (int i = 0; i < nw.entries.length; i++) ENTRY.put(nw.entries[i].id, nw.wf);
  if (!FILE.containsKey(nw.wf)) FILE.put(nw.wf, DIR.resolve(nw.wf + ".properties"));
  GEN = GEN + 1L;
  DIRTY.put(nw.wf, Boolean.TRUE);
}""")
M(srg, r"""
public static void replaceAll(java.util.concurrent.ConcurrentHashMap dst, java.util.HashMap src) {
  java.util.Iterator it = dst.keySet().iterator();
  while (it.hasNext()) if (!src.containsKey(it.next())) it.remove();
  dst.putAll(src);
}""")
M(srg, r"""
public static long maxN(@PKG@.WorldDef w) {
  long m = 0L;
  for (int i = 0; i < w.spots.length; i++) if (w.spots[i].n > m) m = w.spots[i].n;
  for (int i = 0; i < w.entries.length; i++) if (w.entries[i].n > m) m = w.entries[i].n;
  return m;
}""")
M(srg, r"""
public static synchronized String summary() {
  int ws = 0;
  int sp = 0;
  int se = 0;
  int ce = 0;
  java.util.Iterator it = W.values().iterator();
  while (it.hasNext()) {
    @PKG@.WorldDef w = (@PKG@.WorldDef) it.next();
    ws++;
    sp = sp + w.spots.length;
    se = se + w.secrets;
    ce = ce + w.checks;
  }
  return ws + (ws == 1 ? " world, " : " worlds, ") + sp + " spots (" + se + " secret), " + ce + " checklist entries" + (BAD.isEmpty() ? "" : ", " + BAD.size() + " world file(s) NOT READABLE (see the log)");
}""")
# (re)read every world file (setup + /exploreadmin reload, after flushDirty); a file that does not parse keeps the copy loaded before
M(srg, r"""
public static synchronized String loadAllLocked() {
  java.util.HashMap nW = new java.util.HashMap();
  java.util.HashMap nFile = new java.util.HashMap();
  java.util.HashMap nBad = new java.util.HashMap();
  java.util.HashMap nMod = new java.util.HashMap();
  long top = 0L;
  long fileNext = 0L;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path idf = DIR.resolve("ids.properties");
    if (java.nio.file.Files.exists(idf, new java.nio.file.LinkOption[0])) {
      try { fileNext = @PKG@.ExpDefs.parseNum(@PKG@.ExpIO.readProps(idf).getProperty("next"), 0L); } catch (Throwable t) { @PKG@.ExpCfg.warn("could not read worlds/ids.properties (the counter is rebuilt from the world files): " + t); }
    }
    IDS_DISK = fileNext;
    java.util.stream.Stream st = java.nio.file.Files.list(DIR);
    java.util.List l = null;
    try { l = (java.util.List) st.collect(java.util.stream.Collectors.toList()); } finally { st.close(); }
    String[] names = new String[l.size()];
    for (int i = 0; i < names.length; i++) names[i] = ((java.nio.file.Path) l.get(i)).getFileName().toString();
    java.util.Arrays.sort(names);
    for (int i = 0; i < names.length; i++) {
      String fn = names[i];
      if (!fn.endsWith(".properties") || fn.equals("ids.properties")) continue;
      java.nio.file.Path f = DIR.resolve(fn);
      Object[] r = parse(f);
      @PKG@.WorldDef d = (@PKG@.WorldDef) r[0];
      if (d == null) {
        String g = fn.substring(0, fn.length() - 11);
        java.util.Iterator fi = FILE.entrySet().iterator();
        while (fi.hasNext()) { java.util.Map.Entry fe = (java.util.Map.Entry) fi.next(); if (f.equals(fe.getValue())) g = (String) fe.getKey(); }
        nBad.put(g, "could not be read (" + r[2] + ")");
        nFile.put(g, f);
        Object old = W.get(g);
        if (old != null) { nW.put(g, old); top = Math.max(top, maxN((@PKG@.WorldDef) old)); }
        @PKG@.ExpCfg.warn("worlds/" + fn + " could not be read (" + r[2] + ") - " + (old != null ? "the copy read before stays active" : "no spots load from it") + "; in-game edits of that world are refused until it is fixed and /exploreadmin reload runs (the file is never overwritten)");
        continue;
      }
      top = Math.max(top, maxN(d));
      long lm = 0L;
      try { lm = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis(); } catch (Throwable t) { lm = 0L; }
      Object pm = nMod.get(d.wf);
      if (pm != null) {
        if (lm <= ((Long) pm).longValue()) { @PKG@.ExpCfg.warn("worlds/" + fn + " also claims the world '" + d.world + "' - the newer file " + ((java.nio.file.Path) nFile.get(d.wf)).getFileName() + " wins, this one is ignored"); continue; }
        @PKG@.ExpCfg.warn("worlds/" + fn + " also claims the world '" + d.world + "' and is newer - it wins, " + ((java.nio.file.Path) nFile.get(d.wf)).getFileName() + " is ignored");
      }
      nW.put(d.wf, d);
      nFile.put(d.wf, f);
      nMod.put(d.wf, Long.valueOf(lm));
      int bad = ((Integer) r[1]).intValue();
      if (bad > 0) nBad.put(d.wf, "has " + bad + " bad line(s) (see the server log)"); else nBad.remove(d.wf);
    }
    java.util.ArrayList keys = new java.util.ArrayList(nFile.keySet());
    for (int i = 0; i < keys.size(); i++) {
      String wf = (String) keys.get(i);
      if (!nW.containsKey(wf) || nBad.containsKey(wf) && nW.get(wf) == W.get(wf)) continue;
      java.nio.file.Path f = (java.nio.file.Path) nFile.get(wf);
      java.nio.file.Path canon = DIR.resolve(wf + ".properties");
      if (!f.equals(canon) && !java.nio.file.Files.exists(canon, new java.nio.file.LinkOption[0])) {
        try { @PKG@.ExpIO.moveRetry(f, canon); nFile.put(wf, canon); @PKG@.ExpCfg.info("renamed worlds/" + f.getFileName() + " to " + canon.getFileName() + " (the world '" + ((@PKG@.WorldDef) nW.get(wf)).world + "')"); }
        catch (Throwable t) { @PKG@.ExpCfg.warn("could not rename worlds/" + f.getFileName() + " to " + canon.getFileName() + " (used as it is): " + t); }
      }
    }
  } catch (Throwable t) {
    @PKG@.ExpCfg.warn("could not list " + DIR + " (spots and checklists unchanged): " + t);
    return summary();
  }
  java.util.HashMap nEntry = new java.util.HashMap();
  java.util.HashMap nStamp = new java.util.HashMap();
  java.util.ArrayList order = new java.util.ArrayList(nW.keySet());
  String[] oa = new String[order.size()];
  for (int i = 0; i < oa.length; i++) oa[i] = ((java.nio.file.Path) nFile.get(order.get(i))).getFileName().toString() + "\n" + (String) order.get(i);
  java.util.Arrays.sort(oa);
  for (int i = 0; i < oa.length; i++) {
    String wf = oa[i].substring(oa[i].indexOf('\n') + 1);
    @PKG@.WorldDef d = (@PKG@.WorldDef) nW.get(wf);
    java.util.ArrayList keep = new java.util.ArrayList();
    for (int j = 0; j < d.entries.length; j++) {
      String id = d.entries[j].id;
      if (nEntry.containsKey(id)) { @PKG@.ExpCfg.warn(fileName(wf) + ": check." + id + " is already used by " + (String) nEntry.get(id) + " - this line is dropped"); continue; }
      nEntry.put(id, wf);
      keep.add(d.entries[j]);
    }
    if (keep.size() != d.entries.length) {
      @PKG@.WorldDef c = copy(d);
      @PKG@.EntryDef[] ea = new @PKG@.EntryDef[keep.size()];
      for (int j = 0; j < ea.length; j++) ea[j] = (@PKG@.EntryDef) keep.get(j);
      c.entries = ea;
      nW.put(wf, finish(c));
    }
    if (!(nBad.containsKey(wf) && nW.get(wf) == W.get(wf))) {
      long[] s = stampOf((java.nio.file.Path) nFile.get(wf));
      if (s != null) nStamp.put(wf, s);
    } else {
      Object os = STAMP.get(wf);
      if (os != null) nStamp.put(wf, os);
    }
  }
  replaceAll(W, nW);
  replaceAll(FILE, nFile);
  replaceAll(BAD, nBad);
  replaceAll(STAMP, nStamp);
  replaceAll(ENTRY, nEntry);
  DIRTY.clear();
  long nx = Math.max(Math.max(NEXT, fileNext), top + 1L);
  NEXT = nx < 1L ? 1L : nx;
  GEN = GEN + 1L;
  return summary();
}""")
M(srg, r"""
public static String loadAll() {
  String r;
  synchronized (IO) { r = loadAllLocked(); }
  return r;
}""")
# ---- lookups (snapshot reads, no lock)
M(srg, r"""
public static @PKG@.SpotDef spotById(@PKG@.WorldDef wd, String id) {
  if (wd == null || id == null) return null;
  for (int i = 0; i < wd.spots.length; i++) if (wd.spots[i].id.equals(id)) return wd.spots[i];
  return null;
}""")
M(srg, r"""
public static @PKG@.EntryDef entryById(@PKG@.WorldDef wd, String id) {
  if (wd == null || id == null) return null;
  for (int i = 0; i < wd.entries.length; i++) if (wd.entries[i].id.equals(id)) return wd.entries[i];
  return null;
}""")
# spec 2.2: "s<digits>" = a spot id; else the name (any case, spaces / _ ignored): exact, or a unique 3+ letter prefix
M(srg, r"""
public static @PKG@.SpotDef resolveSpot(@PKG@.WorldDef wd, String token, String[] err) {
  String t = token == null ? "" : token.trim();
  if (wd == null || wd.spots.length == 0) { err[0] = "-There are no spots in this world yet"; return null; }
  if (t.length() > 1 && (t.charAt(0) == 's' || t.charAt(0) == 'S') && @PKG@.ExpDefs.isDigits(t.substring(1))) {
    String id = "s" + Long.parseLong(t.substring(1));
    @PKG@.SpotDef s = spotById(wd, id);
    if (s != null) return s;
    err[0] = "-There is no spot " + id + " in this world (/exploreadmin spot list shows the ids)";
    return null;
  }
  String k = @PKG@.ExpDefs.nkey(t);
  if (k.length() == 0) { err[0] = "-Name a spot (its id such as s3, or its name)"; return null; }
  for (int i = 0; i < wd.spots.length; i++) if (@PKG@.ExpDefs.nkey(wd.spots[i].name).equals(k)) return wd.spots[i];
  if (k.length() >= 3) {
    @PKG@.SpotDef hit = null;
    StringBuilder sb = new StringBuilder();
    int n = 0;
    for (int i = 0; i < wd.spots.length; i++) {
      if (!@PKG@.ExpDefs.nkey(wd.spots[i].name).startsWith(k)) continue;
      n++;
      hit = wd.spots[i];
      if (n <= 5) { if (sb.length() > 0) sb.append(", "); sb.append(wd.spots[i].name).append(" (").append(wd.spots[i].id).append(')'); }
    }
    if (n == 1) return hit;
    if (n > 1) { err[0] = "-'" + t + "' fits " + sb.toString() + (n > 5 ? " ..." : "") + " - type more letters or use the id"; return null; }
  }
  err[0] = "-There is no spot called '" + t + "' in this world (/exploreadmin spot list)";
  return null;
}""")
M(srg, r"""
public static boolean nameTaken(@PKG@.WorldDef w, String name, String exceptId) {
  String k = @PKG@.ExpDefs.nkey(name);
  for (int i = 0; i < w.spots.length; i++) if (!w.spots[i].id.equals(exceptId) && @PKG@.ExpDefs.nkey(w.spots[i].name).equals(k)) return true;
  return false;
}""")
M(srg, r"""
public static synchronized long nextId() {
  long n = NEXT;
  NEXT = NEXT + 1L;
  return n;
}""")
# ---- mutations (spec 2.7: public static synchronized, build a NEW WorldDef, W.put). Return { null or "-refusal", id, note }
M(srg, r"""
public static synchronized String[] addSpot(String world, String wf, String name, int x, int y, int z, int r, long xp, boolean secret) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  if (cur == null) cur = blank(world, wf);
  if (cur.spots.length >= @PKG@.ExpCfg.SPOT_MAX) return new String[] { "-This world already has " + cur.spots.length + " spots (spots.maxPerWorld) - nothing added", null, null };
  if (nameTaken(cur, name, "")) return new String[] { "-A spot called " + name + " is already in this world - pick another name (nothing added)", null, null };
  boolean chk = cur.checks < @PKG@.ExpCfg.CHECK_MAX;
  long n = nextId();
  String id = "s" + n;
  @PKG@.SpotDef[] a = new @PKG@.SpotDef[cur.spots.length + 1];
  for (int i = 0; i < cur.spots.length; i++) a[i] = cur.spots[i];
  a[cur.spots.length] = new @PKG@.SpotDef(id, n, name, x, y, z, r, xp, secret, chk);
  @PKG@.WorldDef nw = copy(cur);
  nw.spots = a;
  install(cur == W.get(wf) ? cur : null, nw);
  return new String[] { null, id, chk ? "" : " - NOT on the checklist (checklist.maxEntries " + @PKG@.ExpCfg.CHECK_MAX + " reached)" };
}""")
M(srg, r"""
public static int spotIndex(@PKG@.WorldDef w, String id) {
  if (w == null) return -1;
  for (int i = 0; i < w.spots.length; i++) if (w.spots[i].id.equals(id)) return i;
  return -1;
}""")
M(srg, r"""
public static @PKG@.SpotDef[] cloneSpots(@PKG@.SpotDef[] a) {
  @PKG@.SpotDef[] b = new @PKG@.SpotDef[a.length];
  for (int i = 0; i < a.length; i++) b[i] = a[i];
  return b;
}""")
M(srg, r"""
public static @PKG@.EntryDef[] cloneEntries(@PKG@.EntryDef[] a) {
  @PKG@.EntryDef[] b = new @PKG@.EntryDef[a.length];
  for (int i = 0; i < a.length; i++) b[i] = a[i];
  return b;
}""")
M(srg, r"""
public static synchronized String moveSpot(String wf, String id, int x, int y, int z) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  int i = spotIndex(cur, id);
  if (i < 0) return "-That spot was removed - Refresh";
  @PKG@.SpotDef o = cur.spots[i];
  @PKG@.SpotDef[] a = cloneSpots(cur.spots);
  a[i] = new @PKG@.SpotDef(o.id, o.n, o.name, x, y, z, o.r, o.xp, o.secret, o.check);
  @PKG@.WorldDef nw = copy(cur);
  nw.spots = a;
  install(cur, nw);
  return null;
}""")
M(srg, r"""
public static synchronized String removeSpot(String wf, String id) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  int i = spotIndex(cur, id);
  if (i < 0) return "-That spot was removed - Refresh";
  @PKG@.SpotDef[] a = new @PKG@.SpotDef[cur.spots.length - 1];
  int j = 0;
  for (int k = 0; k < cur.spots.length; k++) if (k != i) { a[j] = cur.spots[k]; j++; }
  @PKG@.WorldDef nw = copy(cur);
  nw.spots = a;
  install(cur, nw);
  return null;
}""")
# field 0 name (s), 1 radius (a), 2 xp (a), 3 secret (a 1/0), 4 on checklist (a 1/0), 5 radius a + xp b
M(srg, r"""
public static synchronized String editSpot(String wf, String id, int field, String s, long a, long b) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  int i = spotIndex(cur, id);
  if (i < 0) return "-That spot was removed - Refresh";
  @PKG@.SpotDef o = cur.spots[i];
  String nm = o.name;
  int r = o.r;
  long xp = o.xp;
  boolean sec = o.secret;
  boolean chk = o.check;
  if (field == 0) {
    if (nameTaken(cur, s, o.id)) return "-Another spot in this world is already called " + s + " (nothing changed)";
    nm = s;
  } else if (field == 1) r = (int) a;
  else if (field == 2) xp = a;
  else if (field == 3) sec = a != 0L;
  else if (field == 4) {
    if (a != 0L && !o.check && cur.checks >= @PKG@.ExpCfg.CHECK_MAX) return "-The checklist is full (checklist.maxEntries " + @PKG@.ExpCfg.CHECK_MAX + ") - nothing changed";
    chk = a != 0L;
  } else if (field == 5) { r = (int) a; xp = b; }
  @PKG@.SpotDef[] arr = cloneSpots(cur.spots);
  arr[i] = new @PKG@.SpotDef(o.id, o.n, nm, o.x, o.y, o.z, r, xp, sec, chk);
  @PKG@.WorldDef nw = copy(cur);
  nw.spots = arr;
  install(cur, nw);
  return null;
}""")
M(srg, r"""
public static synchronized String[] addEntry(String world, String wf, int type, String arg, String text, int x, int y, int z, long cnt) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  if (cur == null) cur = blank(world, wf);
  if (cur.checks >= @PKG@.ExpCfg.CHECK_MAX) return new String[] { "-The checklist is full (checklist.maxEntries " + @PKG@.ExpCfg.CHECK_MAX + ", spot entries count too) - nothing added", null, null };
  for (int i = 0; i < cur.entries.length; i++) {
    @PKG@.EntryDef e = cur.entries[i];
    if (e.type != type) continue;
    if (type == 1 && e.x == x && e.y == y && e.z == z) return new String[] { "-That loot chest is already entry " + e.id + " (nothing added)", null, null };
    if (type == 2 && e.cnt == cnt) return new String[] { "-Open " + cnt + " loot chests is already entry " + e.id + " (nothing added)", null, null };
    if (type == 3 && e.arg.equalsIgnoreCase(arg)) return new String[] { "-" + e.text + " is already entry " + e.id + " (nothing added)", null, null };
  }
  long n = nextId();
  String id = String.valueOf(n);
  @PKG@.EntryDef[] a = new @PKG@.EntryDef[cur.entries.length + 1];
  for (int i = 0; i < cur.entries.length; i++) a[i] = cur.entries[i];
  a[cur.entries.length] = new @PKG@.EntryDef(id, n, type, arg, text, x, y, z, cnt);
  @PKG@.WorldDef nw = copy(cur);
  nw.entries = a;
  install(cur == W.get(wf) ? cur : null, nw);
  return new String[] { null, id, "" };
}""")
M(srg, r"""
public static int entryIndex(@PKG@.WorldDef w, String id) {
  if (w == null) return -1;
  for (int i = 0; i < w.entries.length; i++) if (w.entries[i].id.equals(id)) return i;
  return -1;
}""")
M(srg, r"""
public static synchronized String removeEntry(String wf, String id) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  int i = entryIndex(cur, id);
  if (i < 0) return "-That checklist entry was removed - Refresh";
  @PKG@.EntryDef[] a = new @PKG@.EntryDef[cur.entries.length - 1];
  int j = 0;
  for (int k = 0; k < cur.entries.length; k++) if (k != i) { a[j] = cur.entries[k]; j++; }
  @PKG@.WorldDef nw = copy(cur);
  nw.entries = a;
  install(cur, nw);
  return null;
}""")
M(srg, r"""
public static synchronized String textEntry(String wf, String id, String text) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  int i = entryIndex(cur, id);
  if (i < 0) return "-That checklist entry was removed - Refresh";
  @PKG@.EntryDef o = cur.entries[i];
  @PKG@.EntryDef[] a = cloneEntries(cur.entries);
  a[i] = new @PKG@.EntryDef(o.id, o.n, o.type, o.arg, text, o.x, o.y, o.z, o.cnt);
  @PKG@.WorldDef nw = copy(cur);
  nw.entries = a;
  install(cur, nw);
  return null;
}""")
# field 0 name (s), 1 checklist on/off (a), 2 rewards (a xp, b coins), 3 new-spot XP defaults (a spot, b secret; -1 = config)
M(srg, r"""
public static synchronized String setIsland(String world, String wf, int field, String s, long a, long b) {
  @PKG@.WorldDef cur = (@PKG@.WorldDef) W.get(wf);
  boolean had = cur != null;
  if (cur == null) cur = blank(world, wf);
  @PKG@.WorldDef nw = copy(cur);
  if (field == 0) nw.name = s;
  else if (field == 1) nw.checklist = a != 0L;
  else if (field == 2) { nw.rewardXp = a; nw.rewardCoins = b; }
  else if (field == 3) { nw.spotXp = a; nw.secretXp = b; }
  install(had ? cur : null, nw);
  return null;
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
# 0.2 (spec 2.1): new append-only per-profile files - 0.1 never opens them (rollback-safe)
F(sto, "public static final java.util.concurrent.ConcurrentHashMap PENDING_TICKS = new java.util.concurrent.ConcurrentHashMap();")  # pkey -> ArrayList "+id"/"-id"
M(sto, r"""
public static java.nio.file.Path spotsFile(String k) {
  return DIR.resolve(k).resolve("spots.txt");
}""")
M(sto, r"""
public static java.nio.file.Path ticksFile(String k) {
  return DIR.resolve(k).resolve("ticks.txt");
}""")
M(sto, r"""
public static java.nio.file.Path doneFile(String k) {
  return DIR.resolve(k).resolve("done.txt");
}""")
# review fix: "<worldFile> <region>" per line - the regions this profile entered in each world (checklist zone entries)
M(sto, r"""
public static java.nio.file.Path zonesFile(String k) {
  return DIR.resolve(k).resolve("zones.txt");
}""")
M(sto, r"""
public static java.util.concurrent.ConcurrentHashMap foundFor(@PKG@.ExpData d, String wf) {
  Object o = d.found.get(wf);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  d.found.put(wf, m);
  return m;
}""")
M(sto, r"""
public static java.util.concurrent.ConcurrentHashMap zoneFor(@PKG@.ExpData d, String wf) {
  Object o = d.zoneW.get(wf);
  if (o != null) return (java.util.concurrent.ConcurrentHashMap) o;
  java.util.concurrent.ConcurrentHashMap m = new java.util.concurrent.ConcurrentHashMap();
  d.zoneW.put(wf, m);
  return m;
}""")
M(sto, r"""
public static java.util.List lines(java.nio.file.Path f) throws java.io.IOException {
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return new java.util.ArrayList();
  return java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
}""")
# "+ id" / "- id" (file) or "+id" / "-id" (pending): replayed in order, idempotent
M(sto, r"""
public static void applyTick(@PKG@.ExpData d, String line) {
  String l = line.trim();
  if (l.length() < 2) return;
  char c = l.charAt(0);
  String id = l.substring(1).trim();
  if (!@PKG@.ExpDefs.isDigits(id)) return;
  if (c == '+') d.ticks.put(id, Boolean.TRUE);
  else if (c == '-') d.ticks.remove(id);
}""")
M(sto, r"""
public static void readNew(@PKG@.ExpData d, String k) throws java.io.IOException {
  java.util.List sl = lines(spotsFile(k));
  for (int i = 0; i < sl.size(); i++) {
    String[] q = ((String) sl.get(i)).trim().split(" ");
    if (q.length < 3 || q[1].length() < 2) continue;
    if (foundFor(d, q[0]).put(q[1], Boolean.TRUE) == null) {
      d.spots = d.spots + 1L;
      if (q[2].equals("s")) d.secrets = d.secrets + 1L;
    }
  }
  java.util.List tl = lines(ticksFile(k));
  for (int i = 0; i < tl.size(); i++) applyTick(d, (String) tl.get(i));
  java.util.List dl = lines(doneFile(k));
  for (int i = 0; i < dl.size(); i++) { String w = ((String) dl.get(i)).trim(); if (w.length() > 0) d.doneW.put(w, Boolean.TRUE); }
  java.util.List zl = lines(zonesFile(k));
  for (int i = 0; i < zl.size(); i++) {
    String[] q = ((String) zl.get(i)).trim().split(" ");
    if (q.length < 2 || q[0].length() == 0 || q[1].length() == 0) continue;
    zoneFor(d, q[0]).put(q[1], Boolean.TRUE);
  }
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
    readNew(d, k);
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
  Object pend = PENDING_TICKS.remove(k);
  if (pend != null && !d.bad) {
    java.util.ArrayList pl = (java.util.ArrayList) pend;
    for (int i = 0; i < pl.size(); i++) applyTick(d, (String) pl.get(i));
    d.checkDirty = true;
  }
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
  d.checkDirty = true;
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
  d.checkDirty = true;
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
# ---- 0.2 (spec 3.3 / 4.2 / 4.5): spot finds, custom ticks, the 100% reward flag, progress
M(sto, r"""
public static boolean hasSpot(@PKG@.ExpData d, String wf, String id) {
  Object o = d.found.get(wf);
  return o != null && ((java.util.concurrent.ConcurrentHashMap) o).containsKey(id);
}""")
# false = this profile already found it (or its record is unreadable)
M(sto, r"""
public static synchronized boolean addSpot(@PKG@.ExpData d, String wf, String id, boolean secret) {
  if (d.bad) return false;
  if (foundFor(d, wf).put(id, Boolean.TRUE) != null) return false;
  d.spots = d.spots + 1L;
  if (secret) d.secrets = d.secrets + 1L;
  d.checkDirty = true;
  dirty(d.key);
  @PKG@.ExpIO.append(spotsFile(d.key), @PKG@.ExpIO.utf8(wf + " " + id + " " + (secret ? "s" : "d") + "\n"));
  return true;
}""")
# review fix: checklist zone entries count only a region entered IN THAT WORLD (from 0.2 on): one trip can no longer tick the same
# region on two islands' checklists, and 0.1's global record does not pre-complete a zone entry an admin adds later
M(sto, r"""
public static boolean hasZoneHere(@PKG@.ExpData d, String wf, String region) {
  Object o = d.zoneW.get(wf);
  return o != null && ((java.util.concurrent.ConcurrentHashMap) o).containsKey(region);
}""")
# false = already recorded for this world (or the record is unreadable); append-only zones.txt, never read by 0.1
M(sto, r"""
public static synchronized boolean addZoneHere(@PKG@.ExpData d, String wf, String region) {
  if (d.bad || wf == null || region == null || region.length() == 0 || region.indexOf(' ') >= 0) return false;
  if (zoneFor(d, wf).put(region, Boolean.TRUE) != null) return false;
  d.checkDirty = true;
  @PKG@.ExpIO.append(zonesFile(d.key), @PKG@.ExpIO.utf8(wf + " " + region + "\n"));
  return true;
}""")
M(sto, r"""
public static synchronized int openedCount(@PKG@.ExpData d, String wf) {
  Object o = d.opened.get(wf);
  return o == null ? 0 : ((@LOS@) o).size();
}""")
# custom entry tick / untick for profile key k (bridge, admin command, admin page; any thread). Cached = at once; else queued for
# install(); the ticks.txt line is always appended (replay is idempotent). false = that record cannot be read
M(sto, r"""
public static synchronized boolean complete(String k, String id, boolean v) {
  @PKG@.ExpData d = (@PKG@.ExpData) DATA.get(k);
  if (d != null) {
    if (d.bad) return false;
    if (v) d.ticks.put(id, Boolean.TRUE); else d.ticks.remove(id);
    d.checkDirty = true;
  } else {
    Object o = PENDING_TICKS.get(k);
    java.util.ArrayList l = o == null ? new java.util.ArrayList() : (java.util.ArrayList) o;
    if (o == null) PENDING_TICKS.put(k, l);
    if (l.size() < 10000) l.add((v ? "+" : "-") + id);
  }
  @PKG@.ExpIO.append(ticksFile(k), @PKG@.ExpIO.utf8((v ? "+ " : "- ") + id + "\n"));
  return true;
}""")
# false = already paid for that world (done.txt keeps it: the reward never repeats)
M(sto, r"""
public static synchronized boolean markDone(@PKG@.ExpData d, String wf) {
  if (d.bad || d.doneW.containsKey(wf)) return false;
  d.doneW.put(wf, Boolean.TRUE);
  @PKG@.ExpIO.append(doneFile(d.key), @PKG@.ExpIO.utf8(wf + "\n"));
  return true;
}""")
M(sto, r"""
public static boolean isDone(@PKG@.ExpData d, String wf) {
  return d.doneW.containsKey(wf);
}""")
M(sto, r"""
public static synchronized boolean takeDirty(@PKG@.ExpData d) {
  boolean r = d.checkDirty;
  d.checkDirty = false;
  return r;
}""")
M(sto, r"""
public static synchronized boolean entryDone(@PKG@.ExpData d, @PKG@.WorldDef wd, @PKG@.EntryDef e) {
  if (e.type == 1) return isOpened(d, wd.wf, e.x, e.y, e.z);
  if (e.type == 2) return (long) openedCount(d, wd.wf) >= e.cnt;
  if (e.type == 3) return hasZoneHere(d, wd.wf, e.arg);
  return d.ticks.containsKey(e.id);
}""")
# out = { done, total, secrets found, secrets total }; zeros when checklists are off, no world def, or its checklist is off
M(sto, r"""
public static synchronized void progress(@PKG@.ExpData d, @PKG@.WorldDef wd, int[] out) {
  out[0] = 0; out[1] = 0; out[2] = 0; out[3] = 0;
  if (!@PKG@.ExpCfg.CHECK_ON || wd == null || !wd.checklist || d == null || d.bad) return;
  Object fo = d.found.get(wd.wf);
  java.util.concurrent.ConcurrentHashMap f = fo == null ? null : (java.util.concurrent.ConcurrentHashMap) fo;
  for (int i = 0; i < wd.spots.length; i++) {
    @PKG@.SpotDef s = wd.spots[i];
    boolean got = f != null && f.containsKey(s.id);
    if (s.check) { out[1] = out[1] + 1; if (got) out[0] = out[0] + 1; }
    if (s.secret) { out[3] = out[3] + 1; if (got) out[2] = out[2] + 1; }
  }
  for (int i = 0; i < wd.entries.length; i++) {
    out[1] = out[1] + 1;
    if (entryDone(d, wd, wd.entries[i])) out[0] = out[0] + 1;
  }
}""")
# { discovery spots found here, discovery spots here, secrets found here, secrets here } (display only, ignores the checklist switch)
M(sto, r"""
public static synchronized int[] spotCounts(@PKG@.ExpData d, @PKG@.WorldDef wd) {
  int[] r = new int[4];
  if (wd == null || d == null) return r;
  Object fo = d.found.get(wd.wf);
  java.util.concurrent.ConcurrentHashMap f = fo == null ? null : (java.util.concurrent.ConcurrentHashMap) fo;
  for (int i = 0; i < wd.spots.length; i++) {
    @PKG@.SpotDef s = wd.spots[i];
    boolean got = f != null && f.containsKey(s.id);
    int b = s.secret ? 2 : 0;
    r[b + 1] = r[b + 1] + 1;
    if (got) r[b] = r[b] + 1;
  }
  return r;
}""")
# /exploreadmin resetme: the record of this profile (owed / earned XP stay: XP already paid to SkyySkills stays there)
M(sto, r"""
public static synchronized void reset(@PKG@.ExpData d) {
  d.zones = new java.util.concurrent.ConcurrentHashMap();
  d.opened = new java.util.concurrent.ConcurrentHashMap();
  d.chunks = new java.util.concurrent.ConcurrentHashMap();
  d.paid = new java.util.concurrent.ConcurrentHashMap();
  d.found = new java.util.concurrent.ConcurrentHashMap();
  d.ticks = new java.util.concurrent.ConcurrentHashMap();
  d.doneW = new java.util.concurrent.ConcurrentHashMap();
  d.zoneW = new java.util.concurrent.ConcurrentHashMap();
  d.chests = 0L;
  d.luck = 0L;
  d.total = 0L;
  d.spots = 0L;
  d.secrets = 0L;
  d.checkDirty = true;
  d.title = "";
  d.noLoad = true;
  PENDING_TICKS.remove(d.key);
  dirty(d.key);
}""")
M(sto, r"""
public static synchronized java.util.Properties snap(String k) {
  @PKG@.ExpData d = (@PKG@.ExpData) DATA.get(k);
  if (d == null || d.bad) return null;
  java.util.Properties p = new java.util.Properties();
  if (d.name != null) p.setProperty("name", d.name);
  p.setProperty("v", "2");
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
F(ttl, "public static final java.util.concurrent.ConcurrentHashMap ISLAND = new java.util.concurrent.ConcurrentHashMap();")     # 0.2: UUID -> "done/total" here
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
  if (k == 4) return d.spots >= req;
  if (k == 5) return d.secrets >= req;
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
  if (!@PKG@.ExpIO.notifyOn(pr.getUuid(), "explore.finds")) return;
  for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
    if ((fresh & (1L << i)) == 0L) continue;
    say(pr, "New title unlocked: " + @PKG@.ExpDefs.T_NAME[i] + " - use it with /title " + @PKG@.ExpDefs.T_ID[i], @PKG@.ExpDefs.KIND_COLOR[@PKG@.ExpDefs.T_KIND[i]]);
  }
}""")
M(ttl, r"""
public static String summary(java.util.UUID u, @PKG@.ExpData d, int lvl) {
  int sel = selected(d, lvl);
  Object isl = u == null ? null : ISLAND.get(u);
  return "level:" + lvl + ",zones:" + @PKG@.ExpStore.knownZones(d) + "/" + @PKG@.ExpDefs.NR + ",chests:" + d.chests + ",chunks:" + d.total + ",title:" + (sel < 0 ? "" : @PKG@.ExpDefs.T_ID[sel]) + ",spots:" + d.spots + ",secrets:" + d.secrets + ",island:" + (isl == null ? "0/0" : (String) isl);
}""")
# explore:<uuid>, explore:title:<uuid> and the chat map describe the ACTIVE profile (written only when they change)
M(ttl, r"""
public static void publish(java.util.UUID u, @PKG@.ExpData d, int lvl) {
  try {
    java.util.Map b = @PKG@.ExpIO.bridge();
    String us = u.toString();
    String s = summary(u, d, lvl);
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
    ISLAND.remove(u);
    java.util.Map b = @PKG@.ExpIO.bridge();
    b.remove("explore:" + u.toString());
    b.remove("explore:title:" + u.toString());
    b.remove("explore:pct:" + u.toString());
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

# ================= 0.2 ExpSpot: first arrival at a discovery / secret spot (spec 3.3; world thread, inside the tick: packets, files and
# the XP ledger only - no component writes) =================
M(esp, r"""
public static void banner(@PR@ pr, String title, String sub, boolean major) {
  try { @ETU@.showEventTitleToPlayer(pr, @MSG@.raw(title), @MSG@.raw(sub), major); } catch (Throwable t) { }
}""")
# which: 0 spot, 1 secret, 2 checklist complete; the same packet the engine's own zone discovery sends (PlaySoundEvent2D)
M(esp, r"""
public static void sound(@PR@ pr, int which) {
  try {
    int idx = @PKG@.ExpCfg.sound(which);
    if (idx == Integer.MIN_VALUE) return;
    @SNU@.playSoundEvent2dToPlayer(pr, idx, @SCAT@.UI);
  } catch (Throwable t) { @PKG@.ExpCfg.warnEvery("playsound", 600000L, "could not play a discovery sound: " + t); }
}""")
M(esp, r"""
public static void found(@PR@ pr, java.util.UUID u, String k, @PKG@.ExpData d, @PKG@.WorldDef wd, @PKG@.SpotDef sp, @PKG@.ExpState s, boolean creative) {
  if (!@PKG@.ExpStore.addSpot(d, wd.wf, sp.id, sp.secret)) return;
  long now = System.currentTimeMillis();
  long xp = sp.xp;
  if (xp > 0L) @PKG@.ExpStore.addOwed(d, xp);
  @PKG@.ExpStore.saveSoon(k);
  if (!creative && xp > 0L) { s.lastFlush = now; @PKG@.ExpXp.flush(u, k, d); }
  String xs = xp > 0L ? " - +" + @PKG@.ExpDefs.grp(xp) + " Exploration XP" : "";
  if (@PKG@.ExpCfg.SPOT_BANNER && now - s.lastBanner >= @PKG@.ExpCfg.BANNER_GAP) {
    s.lastBanner = now;
    banner(pr, sp.name, (sp.secret ? "Secret" : "Discovery") + xs, sp.secret ? @PKG@.ExpCfg.SECRET_MAJOR : @PKG@.ExpCfg.MAJOR);
  }
  sound(pr, sp.secret ? 1 : 0);
  if (@PKG@.ExpIO.notifyOn(u, "explore.finds")) {
    int[] c = @PKG@.ExpStore.spotCounts(d, wd);
    if (sp.secret) @PKG@.ExpTitles.say(pr, "[Exploration] Secret found: " + sp.name + xs + " (" + c[2] + " of " + c[3] + " secrets on " + wd.name + ")", "#d890ff");
    else @PKG@.ExpTitles.say(pr, "[Exploration] Discovered " + sp.name + xs + " (" + c[0] + " of " + c[1] + " spots on " + wd.name + ")", "#ffb070");
  }
  int lvl = @PKG@.ExpSkill.level(u);
  int lv = lvl < 0 ? 0 : lvl;
  @PKG@.ExpTitles.check(pr, k, d, lv);
  @PKG@.ExpTitles.publish(u, d, lv);
}""")

# ================= 0.2 ExpCheck: the island checklist - completion reward, explore:pct, labels (spec 4.3 / 4.4) =================
M(eck, r"""
public static void complete(@PR@ pr, java.util.UUID u, String k, @PKG@.ExpData d, @PKG@.WorldDef wd, boolean creative) {
  if (!@PKG@.ExpStore.markDone(d, wd.wf)) return;
  StringBuilder rw = new StringBuilder();
  if (wd.rewardXp > 0L) {
    @PKG@.ExpStore.addOwed(d, wd.rewardXp);
    @PKG@.ExpStore.saveSoon(k);
    if (!creative) @PKG@.ExpXp.flush(u, k, d);
    rw.append(" +").append(@PKG@.ExpDefs.grp(wd.rewardXp)).append(" Exploration XP");
  }
  if (wd.rewardCoins > 0L) {
    if (rw.length() > 0) rw.append(',');
    if (@PKG@.ExpIO.fn("coins:fn:add") == null) rw.append(" (coins need SkyyCoins - not paid)");
    else if (!@PKG@.ExpIO.pkey(u).equals(k)) rw.append(" (coins not paid - your profile just changed)");
    else if (@PKG@.ExpSkill.coins(u, wd.rewardCoins)) rw.append(" +").append(@PKG@.ExpDefs.grp(wd.rewardCoins)).append(" coins");
    else rw.append(" (the coins could not be paid - SkyyCoins refused)");
  }
  @PKG@.ExpSpot.banner(pr, wd.name, "Checklist complete - 100%", true);
  @PKG@.ExpSpot.sound(pr, 2);
  if (@PKG@.ExpIO.notifyOn(u, "explore.finds")) @PKG@.ExpTitles.say(pr, "[Exploration] " + wd.name + " checklist complete (100%)!" + rw.toString(), "#ffe08a");
  @PKG@.ExpCfg.info("checklist complete: " + pr.getUsername() + " (" + k + ") finished " + wd.name + " (" + wd.world + ")" + rw.toString());
}""")
# only when the profile's record changed (checkDirty): every world with a checklist, 100% and not paid yet -> complete
M(eck, r"""
public static void scan(@PR@ pr, java.util.UUID u, String k, @PKG@.ExpData d, @PKG@.ExpState s, boolean creative) {
  java.util.Iterator it = @PKG@.SpotReg.W.values().iterator();
  while (it.hasNext()) {
    @PKG@.WorldDef wd = (@PKG@.WorldDef) it.next();
    if (!wd.checklist) continue;
    @PKG@.ExpStore.progress(d, wd, s.tmp);
    if (s.tmp[1] > 0 && s.tmp[0] == s.tmp[1] && !@PKG@.ExpStore.isDone(d, wd.wf)) complete(pr, u, k, d, wd, creative);
  }
}""")
M(eck, r"""
public static int pct(int done, int total) {
  return total <= 0 ? 0 : (int) ((long) done * 100L / (long) total);
}""")
# explore:pct:<uuid> = "<pct>|<done>|<total>|<island name>" for the current world (absent = no checklist here); cw "" = excluded world
M(eck, r"""
public static void publishPct(java.util.UUID u, @PKG@.ExpData d, String cw, @PKG@.ExpState s) {
  @PKG@.WorldDef wd = cw.length() == 0 ? null : @PKG@.SpotReg.byWf(cw);
  @PKG@.ExpStore.progress(d, wd, s.tmp);
  int done = s.tmp[0];
  int total = s.tmp[1];
  java.util.Map b = @PKG@.ExpIO.bridge();
  String key = "explore:pct:" + u.toString();
  if (total > 0) {
    String v = pct(done, total) + "|" + done + "|" + total + "|" + wd.name;
    if (!v.equals(s.pctStr) || !b.containsKey(key)) { b.put(key, v); s.pctStr = v; }
    @PKG@.ExpTitles.ISLAND.put(u, done + "/" + total);
  } else {
    if (s.pctStr != null || b.containsKey(key)) b.remove(key);
    s.pctStr = null;
    @PKG@.ExpTitles.ISLAND.put(u, "0/0");
  }
  s.pctWf = cw;
  s.pctGen = @PKG@.SpotReg.GEN;
  s.pctCfg = @PKG@.ExpCfg.CFG_GEN;
}""")
# the pct string for any cached profile + world name (explore:fn:pct; never reads files)
M(eck, r"""
public static String pctFor(@PKG@.ExpData d, @PKG@.WorldDef wd) {
  if (d == null || wd == null) return null;
  int[] t = new int[4];
  @PKG@.ExpStore.progress(d, wd, t);
  if (t[1] <= 0) return null;
  return pct(t[0], t[1]) + "|" + t[0] + "|" + t[1] + "|" + wd.name;
}""")

# ================= ExpAward: first open of a loot chest (world task, never inside a system iteration) =================
F(awd, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")
# 0.2: per-UUID tick state shared with ExpTick (ExpTick.ST is this map; defined here because ExpAward is compiled first)
F(awd, "public static final java.util.concurrent.ConcurrentHashMap ST = new java.util.concurrent.ConcurrentHashMap();")
M(awd, r"""
public static @PKG@.ExpState gate(java.util.UUID u) {
  @PKG@.ExpState s = (@PKG@.ExpState) ST.get(u);
  if (s == null) { s = new @PKG@.ExpState(); ST.put(u, s); }
  return s;
}""")
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
  if (!@PKG@.ExpIO.notifyOn(u, "explore.finds")) return;
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
  if (@PKG@.ExpSkill.coins(u, amt) && @PKG@.ExpIO.notifyOn(u, "explore.finds")) @PKG@.ExpTitles.say(pr, "Scavenger! +" + @PKG@.ExpDefs.grp(amt) + " coins", "#ffe08a");
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
  long wait = @PKG@.ExpIO.switchWait(u);
  if (wait > 0L) {
    @PKG@.ExpState gs = @PKG@.ExpAward.gate(u);
    long nowg = System.currentTimeMillis();
    if (nowg - gs.lastGateMsg >= 10000L) {
      gs.lastGateMsg = nowg;
      @PKG@.ExpTitles.say(pr, "[Exploration] Loot chests count again in " + ((wait + 999L) / 1000L) + " s (your profile just switched)", "#ffb080");
    }
    return;
  }
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
  if (@PKG@.ExpIO.notifyOn(u, "explore.finds")) @PKG@.ExpTitles.say(pr, "[Exploration] Loot chest found - " + @PKG@.ExpDefs.dlLabel(dl) + " - +" + @PKG@.ExpDefs.grp(xp) + " Exploration XP (" + @PKG@.ExpDefs.grp(d.chests) + (d.chests == 1L ? " chest)" : " chests)"), "#ffd27a");
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
# 0.2: the same maps as ExpAward.ST / ExpIO.EPOCH (the chest award reads them; ExpTick is compiled after it)
F(tick, "public static final java.util.concurrent.ConcurrentHashMap ST = @PKG@.ExpAward.ST;")
F(tick, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = @PKG@.ExpIO.EPOCH;")
F(tick, "public static boolean FAILED_ONCE = false;")
F(tick, "public static boolean SPOT_FAILED = false;")
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
public static void feedback(@PR@ pr, java.util.UUID u, @PKG@.ExpState s, @PKG@.ExpData d, String wf, long now) {
  if (s.pendN <= 0L || now - s.pendStart < @PKG@.ExpCfg.FEEDBACK_MS) return;
  long n = s.pendN;
  long xp = s.pendXp;
  boolean cap = s.pendCapped;
  s.pendN = 0L;
  s.pendXp = 0L;
  s.pendCapped = false;
  s.pendStart = 0L;
  if (d.quiet || !@PKG@.ExpIO.notifyOn(u, "explore.chunkXp")) return;
  long here = @PKG@.ExpStore.hereCount(d, wf);
  String hs = here >= 0L ? " (" + @PKG@.ExpDefs.grp(here) + " here)" : "";
  String what = @PKG@.ExpDefs.grp(n) + (n == 1L ? " new chunk" : " new chunks");
  String line = xp > 0L ? "+" + @PKG@.ExpDefs.grp(xp) + " Exploration XP from " + what + hs : what + " explored" + hs;
  if (cap) line = line + " - this world's chunk XP cap is reached";
  @PKG@.ExpTitles.say(pr, line, "#c8a0ff");
}""")
# A6: Hytale regions, per profile (zone XP + titles: 0.1's global record). 0.2 review fix: the region is also recorded for THIS world
# (wf) every time the player stands in it - only that per-world record completes checklist zone entries (no lock while known)
M(tick, r"""
public static void zone(@PR@ pr, java.util.UUID u, @PKG@.ExpData d, String k, String wf, String region, String zname, boolean creative, @PKG@.ExpState s, long now) {
  if (region == null || region.length() == 0) return;
  if (wf != null && !@PKG@.ExpStore.hasZoneHere(d, wf, region)) @PKG@.ExpStore.addZoneHere(d, wf, region);
  if (@PKG@.ExpStore.hasZone(d, region)) return;
  long xp = @PKG@.ExpCfg.zoneXp(region);
  if (!@PKG@.ExpStore.addZone(d, region, xp)) return;
  @PKG@.ExpStore.saveSoon(k);
  String zn = @PKG@.ExpDefs.regionZone(region);
  if (zn.length() == 0) zn = @PKG@.ExpDefs.zoneName(zname);
  int n = @PKG@.ExpStore.knownZones(d);
  if (@PKG@.ExpIO.notifyOn(u, "explore.finds")) @PKG@.ExpTitles.say(pr, "[Exploration] Discovered " + @PKG@.ExpDefs.regionName(region) + (zn.length() > 0 ? " (" + zn + ")" : "") + " +" + @PKG@.ExpDefs.grp(xp) + " Exploration XP (" + n + " of " + @PKG@.ExpDefs.NR + ")", "#9adf86");
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
# 0.2 spec 3.2: the spot check (world thread, every spots.checkMs; no allocation when no spot is hit: one TransformComponent read + one
# primitive-key get; the world is resolved once and cached in ExpState). pkey() only on a hit.
M(tick, r"""
public static void spotCheck(@PR@ pr, @PLA@ p, @REF@ ref, @ST@ store, java.util.UUID u, @PKG@.ExpState s) {
  if (!@PKG@.ExpCfg.SPOTS_ON || @PKG@.SpotReg.W.isEmpty()) { s.inside = null; return; }
  Object ext = store.getExternalData();
  if (!(ext instanceof @EST@)) return;
  @WLD@ w = ((@EST@) ext).getWorld();
  if (w == null) return;
  String wn = w.getName();
  @PKG@.WorldDef wd = null;
  if (wn == s.spWn && s.spGen == @PKG@.SpotReg.GEN && s.spCfg == @PKG@.ExpCfg.CFG_GEN) wd = (@PKG@.WorldDef) s.spWd;
  else {
    if (wn != null && !@PKG@.ExpCfg.excluded(wn)) wd = @PKG@.SpotReg.byName(wn);
    s.spWn = wn;
    s.spGen = @PKG@.SpotReg.GEN;
    s.spCfg = @PKG@.ExpCfg.CFG_GEN;
    s.spWd = wd;
  }
  if (wd == null || wd.index == null) { s.inside = null; return; }
  long c = @PKG@.SpotReg.CHECKS.incrementAndGet();
  long t0 = (c & 15L) == 0L ? System.nanoTime() : 0L;
  @TRC@ tc = (@TRC@) store.getComponent(ref, @TRC@.getComponentType());
  if (tc == null) return;
  @V3D@ pos = tc.getPosition();
  if (pos == null) return;
  double px = pos.x();
  double py = pos.y();
  double pz = pos.z();
  Object o = wd.index.get(@CHU@.indexChunkFromBlock(px, pz));
  if (o == null) { s.inside = null; if (t0 != 0L) { @PKG@.SpotReg.TIMED.incrementAndGet(); @PKG@.SpotReg.NANOS.addAndGet(System.nanoTime() - t0); } return; }
  @PKG@.SpotDef[] arr = (@PKG@.SpotDef[]) o;
  @PKG@.SpotDef hit = null;
  boolean any = false;
  for (int i = 0; i < arr.length; i++) {
    @PKG@.SpotDef sp = arr[i];
    double dx = px - sp.cx;
    double dy = py - sp.cy;
    double dz = pz - sp.cz;
    if (dx * dx + dy * dy + dz * dz > sp.r2) continue;
    any = true;
    if (sp.id.equals(s.inside) && wd.wf.equals(s.insideWf)) continue;
    if (hit == null) hit = sp;
  }
  if (t0 != 0L) { @PKG@.SpotReg.TIMED.incrementAndGet(); @PKG@.SpotReg.NANOS.addAndGet(System.nanoTime() - t0); }
  if (!any) { s.inside = null; return; }
  if (hit == null) return;
  boolean creative = false;
  try { creative = p.getGameMode() == @GM@.Creative; } catch (Throwable t) { creative = false; }
  if (creative && !@PKG@.ExpCfg.CREATIVE_XP) return;
  if (@PKG@.ExpAward.flying(store, ref)) return;
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.bad) return;
  s.inside = hit.id;
  s.insideWf = wd.wf;
  if (@PKG@.ExpStore.hasSpot(d, wd.wf, hit.id)) return;
  @PKG@.ExpSpot.found(pr, u, k, d, wd, hit, s, creative);
}""")
M(tick, r"""
public static void second(@PR@ pr, @PLA@ p, @REF@ ref, @ST@ store, java.util.UUID u, @PKG@.ExpState s) {
  long now = System.currentTimeMillis();
  if (epochChanged(u)) {
    s.hasLast = false; s.pendN = 0L; s.pendXp = 0L; s.pendStart = 0L; s.pendCapped = false; s.lastFlush = 0L;
    s.inside = null; s.insideWf = null; s.pctWf = null; s.pctStr = null; s.lastBanner = 0L; s.spWn = null;
    @PKG@.ExpIO.SWITCHED.put(u, Long.valueOf(now));
    @PKG@.ExpCfg.info("profile switch: " + u + " now explores as " + @PKG@.ExpIO.pkey(u));
  }
  boolean busyNow = @PKG@.ExpIO.busy(u);
  if (s.wasBusy && !busyNow) @PKG@.ExpIO.SWITCHED.put(u, Long.valueOf(now));
  s.wasBusy = busyNow;
  if (!@PKG@.SpotReg.LOST.isEmpty()) {
    Object lost = @PKG@.SpotReg.LOST.remove(u);
    if (lost instanceof String) @PKG@.ExpTitles.say(pr, (String) lost, "#ffb080");
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
      if (@PKG@.ExpCfg.ZONES_ON && !noCreative && !noFly) zone(pr, u, d, k, wf, region, zname, creative, s, now);
      if (@PKG@.ExpCfg.CHESTS_ON) scan(p, w, wf, u, k, d);
    } else s.hasLast = false;
    feedback(pr, u, s, d, wf, now);
    if (d.owed > 0L && !creative && now - s.lastFlush >= @PKG@.ExpCfg.RETRY_MS) { s.lastFlush = now; @PKG@.ExpXp.flush(u, k, d); }
    boolean ckd = @PKG@.ExpCfg.CHECK_ON && @PKG@.ExpStore.takeDirty(d);
    if (ckd) @PKG@.ExpCheck.scan(pr, u, k, d, s, creative);
    String cw = wf == null ? "" : wf;
    if (ckd || s.pctGen != @PKG@.SpotReg.GEN || s.pctCfg != @PKG@.ExpCfg.CFG_GEN || !cw.equals(s.pctWf)) @PKG@.ExpCheck.publishPct(u, d, cw, s);
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
    s.spotAcc = s.spotAcc + (double) dt;
    if (s.spotAcc >= @PKG@.ExpCfg.SPOT_S) {
      s.spotAcc = 0.0;
      try { spotCheck(pr, p, ref, store, u, s); } catch (Throwable t2) { if (!SPOT_FAILED) { SPOT_FAILED = true; @PKG@.ExpCfg.warn("spot check failed (logged once): " + t2); } }
    }
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
    @PKG@.ExpIO.SWITCHED.remove(u);
  }
}""")
# 0.2: the spot check window for /exploreadmin stats (every 10 s: checks, timed checks, timed nanoseconds)
M(svr, r"""
public static void window() {
  long[] now = new long[] { @PKG@.SpotReg.CHECKS.get(), @PKG@.SpotReg.TIMED.get(), @PKG@.SpotReg.NANOS.get() };
  long[] prev = @PKG@.SpotReg.PREV10;
  @PKG@.SpotReg.LAST10 = new long[] { now[0] - prev[0], now[1] - prev[1], now[2] - prev[2] };
  @PKG@.SpotReg.PREV10 = now;
}""")
M(svr, r"""
public void run() {
  this.n++;
  try { @PKG@.ExpIO.drain(); } catch (Throwable t) { @PKG@.ExpCfg.warnEvery("drain", 60000L, "append queue failed: " + t); }
  try { if (!@PKG@.SpotReg.DIRTY.isEmpty()) @PKG@.SpotReg.flushDirty(); } catch (Throwable t) { @PKG@.ExpCfg.warnEvery("worldsave", 60000L, "world file save failed: " + t); }
  if (this.n % 5L == 0L) { try { @PKG@.ExpStore.flushDirty(); } catch (Throwable t) { } try { window(); } catch (Throwable t) { } }
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
    Object isl = @PKG@.ExpTitles.ISLAND.get(u);
    String ip = "";
    if (isl instanceof String) {
      String is = (String) isl;
      int sl = is.indexOf('/');
      try { int dn = Integer.parseInt(is.substring(0, sl)); int tt = Integer.parseInt(is.substring(sl + 1)); if (tt > 0) ip = " - island checklist " + @PKG@.ExpCheck.pct(dn, tt) + "%"; } catch (Throwable t2) { }
    }
    out.add("Discoveries - " + @PKG@.ExpDefs.fmt(d.spots) + " spots found (" + @PKG@.ExpDefs.fmt(d.secrets) + " secret)" + ip);
    int sel = @PKG@.ExpTitles.selected(d, lv);
    out.add(sel >= 0 ? "Title - " + @PKG@.ExpDefs.T_NAME[sel] + " (/title)" : "No title selected - " + @PKG@.ExpTitles.count(d, lv) + " earned (/title)");
    if (d.owed > 0L) out.add(@PKG@.ExpDefs.fmt(d.owed) + " Exploration XP still waiting to be paid");
  } catch (Throwable t) { }
  return out;
}""")
# 0.2 explore:fn:complete (spec 4.5): Object[]{UUID, String pkey or null, entry id (String or Number), Boolean value (default TRUE)} ->
# Boolean. Any thread, never throws, never touches ECS, only CUSTOM entries (spots / chests / zones come from real play)
cfn.addInterface(pool.get("java.util.function.Function"))
C(cfn, "public ExpCompleteFn() { }")
M(cfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) a[0];
    String us = u.toString();
    String k = null;
    if (a[1] == null) k = @PKG@.ExpIO.pkey(u);
    else if (a[1] instanceof String) {
      String pk = (String) a[1];
      if (pk.equals(us)) k = pk;
      else if (pk.startsWith(us + "-p") && @PKG@.ExpDefs.isDigits(pk.substring(us.length() + 2))) k = pk;
    }
    if (k == null) return Boolean.FALSE;
    String id = null;
    if (a[2] instanceof Number) id = String.valueOf(((Number) a[2]).longValue());
    else if (a[2] instanceof String) id = ((String) a[2]).trim();
    if (id == null || !@PKG@.ExpDefs.isDigits(id)) return Boolean.FALSE;
    id = String.valueOf(Long.parseLong(id));
    boolean v = true;
    if (a.length > 3 && a[3] instanceof Boolean) v = ((Boolean) a[3]).booleanValue();
    Object wf = @PKG@.SpotReg.ENTRY.get(id);
    if (!(wf instanceof String)) return Boolean.FALSE;
    @PKG@.EntryDef e = @PKG@.SpotReg.entryById(@PKG@.SpotReg.byWf((String) wf), id);
    if (e == null || e.type != 4) return Boolean.FALSE;
    return @PKG@.ExpStore.complete(k, id, v) ? Boolean.TRUE : Boolean.FALSE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
# 0.2 explore:fn:pct: Object[]{UUID, String worldName} -> "73|11|15|Fens Island" or null (cached profiles only, never reads files)
pfn.addInterface(pool.get("java.util.function.Function"))
C(pfn, "public ExpPctFn() { }")
M(pfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return null;
    @PKG@.ExpData d = @PKG@.ExpStore.cached(@PKG@.ExpIO.pkey((java.util.UUID) a[0]));
    if (d == null || d.bad) return null;
    return @PKG@.ExpCheck.pctFor(d, @PKG@.SpotReg.byName((String) a[1]));
  } catch (Throwable t) { return null; }
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

# ================= ExplorePage: the inline /explore page (0.2: 1120 x 800, 4 tabs, 8 cards, Checklist tab; rebuilt only on clicks,
# at most once a second) =================
def tbs(bg, hv, pr, fg, fgh, size=14):
    lab = "FontSize: " + str(size) + ", TextColor: %s, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center"
    return ("Style: TextButtonStyle(Default: (Background: %s, LabelStyle: (%s)), Hovered: (Background: %s, LabelStyle: (%s)), "
            "Pressed: (Background: %s, LabelStyle: (%s)));") % (bg, lab % fg, hv, lab % fgh, pr, lab % fgh)
T["BSG"] = tbs("#27463a", "#3b6b54", "#172a22", "#dcffe8", "#ffffff")      # SkyySkills / SkyyTrees button style
T["BSOFF"] = tbs("#1d2c3c", "#2c4258", "#142030", "#b8c8d8", "#ffffff")
T["BTON"] = tbs("#6b4a1c", "#80592a", "#3a2810", "#ffffff", "#ffffff")
T["BTOFF"] = T["BSOFF"]
# admin page (spec 6.1): FontSize 16, red BRED for Remove / Sure
T["XG"] = tbs("#27463a", "#3b6b54", "#172a22", "#dcffe8", "#ffffff", 16)
T["XOFF"] = tbs("#1d2c3c", "#2c4258", "#142030", "#b8c8d8", "#ffffff", 16)
T["XON"] = tbs("#6b4a1c", "#80592a", "#3a2810", "#ffffff", "#ffffff", 16)
T["XRED"] = tbs("#6a2626", "#8a3434", "#401616", "#ffe0e0", "#ffffff", 16)
T["XBLU"] = tbs("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", "#ffffff", 16)
for k in ("BSG", "BSOFF", "BTON", "BTOFF", "XG", "XOFF", "XON", "XRED", "XBLU"): assert '"' not in T[k] and "@" not in T[k]

# ---- layout budgets (spec 7.1 / 7.2 / 6.2: build asserts)
EX_W, EX_H, EX_PADV = 1120, 800, 12
EX_HEAD, EX_NOTE, EX_ACC, EX_BODY, EX_FOOT = 48, 24, 2, 640, 52
assert 2 * EX_PADV + EX_HEAD + EX_NOTE + EX_ACC + EX_BODY + EX_FOOT <= EX_H
CARD_W, CARD_GAP = 258, 16
assert 4 * CARD_W + 3 * CARD_GAP == 1080
assert 4 * 150 + 4 * 8 + 440 <= 1080          # head: 4 tabs + the level label
assert 170 + 12 + 230 + 12 + 600 <= 1080      # foot
assert 2 * 158 + 10 + 28 + 50 + 4 * 28 + 24 <= EX_BODY   # overview: 2 card rows + owed + info lines
assert 48 + 30 + 4 + 16 + 8 + 9 * 46 + 48 + 26 <= EX_BODY   # checklist tab
assert 150 + 10 + 740 + 10 + 150 <= 1080 and 80 + 330 + 110 <= 530 and 530 + 20 + 530 == 1080
assert 44 + 12 * 44 <= EX_BODY and 190 + 250 + 80 <= 530   # titles tab (23 titles = 12 per column)
XA_W, XA_H, XA_PADV = 1120, 900, 12
XA_ROWS = [3, 52, 28, 690, 34, 52]
assert 2 * XA_PADV + sum(XA_ROWS) <= XA_H
assert 580 + 3 * 150 + 3 * 8 <= 1080 and 600 + 20 + 460 == 1080 and 170 + 10 + 890 <= 1080
assert 32 + 8 * 70 + 52 <= 690                               # list: header + 8 rows + pager
assert 10 + 460 + 10 + 110 <= 600 and 140 + 10 + 140 + 10 + 180 + 10 + 110 <= 600
for row in ([90, 350], [90, 100, 10, 60, 140], [200, 10, 230], [300, 10, 140], [90, 10, 130, 10, 200], [220, 10, 220],
            [140, 10, 140, 10, 140], [440], [215, 10, 215], [290, 10, 140], [210, 10, 220], [200, 10, 115, 10, 115],
            [140, 10, 140, 10, 150]):
    assert sum(row) <= 460, row
assert 30 + 3 * 52 + 26 + 10 + 30 + 4 * 52 + 30 <= 690        # spots detail
assert 30 + 4 * 52 + 26 + 10 + 30 + 3 * 52 + 30 <= 690        # checklist detail
assert 30 + 52 + 52 + 30 + 52 + 26 + 30 + 52 + 26 + 10 + 30 + 52 + 44 <= 690   # island detail

F(page, "public int tab;")
F(page, "public String msg;")
F(page, "public long lastBuild;")
F(page, "public String ckWorld;")
F(page, "public int ckPage;")
F(page, "public String[] ckList;")
F(page, "public int ckIdx;")
F(page, 'public static final String[] TABS = new String[] { "Overview", "Zones", "Titles", "Checklist" };')
F(page, "public static final String[] CARD_ICON = %s;" % jstr(CARD_ICON))
F(page, "public static final String[] CARD_HEAD = %s;" % jstr(CARD_HEAD))
F(page, "public static final String[] CARD_COLOR = %s;" % jstr(CARD_COLOR))
F(page, 'public static final String NOTE = "Loot chests - new chunks - zones - discoveries - once each per profile - nothing while flying or in creative - XP boosters never apply";')
F(page, 'public static final String BADNOTE = "Your exploration file could not be read - ask an admin (nothing is earned or saved until it is fixed)";')
C(page, r"""
public ExplorePage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab;
  this.msg = "";
  this.lastBuild = 0L;
  this.ckWorld = null;
  this.ckPage = 0;
  this.ckList = new String[0];
  this.ckIdx = 0;
}""")
M(page, r"""
public static void card(@UCB@ b, String parent, int i, String icon, String head, String val, String sub, String col) {
  b.appendInline(parent, "Group #SkyyExCard" + i + " { Anchor: (Width: 258, Height: 150); Background: #142030(0.9); LayoutMode: Left; Padding: (Horizontal: 8, Vertical: 6); }");
  b.appendInline("#SkyyExCard" + i, "Group { Anchor: (Width: 72, Height: 138); ItemIcon { Anchor: (Width: 60, Height: 60, Left: 0, Top: 39); ItemId: \"" + icon + "\"; } }");
  b.appendInline("#SkyyExCard" + i, "Group #SkyyExCardT" + i + " { Anchor: (Width: 170, Height: 138); LayoutMode: Top; }");
  b.appendInline("#SkyyExCardT" + i, "Label #SkyyExCardA" + i + " { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 13, TextColor: #9fb8cc, VerticalAlignment: Center); }");
  b.appendInline("#SkyyExCardT" + i, "Label #SkyyExCardB" + i + " { Anchor: (Height: 36); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
  b.appendInline("#SkyyExCardT" + i, "Label #SkyyExCardC" + i + " { Anchor: (Height: 78); Text: \"\"; Style: (FontSize: 13, TextColor: #c8d6e4, Wrap: true); }");
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
  String[] val = new String[8];
  String[] sub = new String[8];
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
  @PKG@.WorldDef wd = wf == null ? null : @PKG@.SpotReg.byWf(wf);
  val[6] = @PKG@.ExpDefs.grp(d.spots) + (d.spots == 1L ? " spot found" : " spots found");
  if (!@PKG@.ExpCfg.SPOTS_ON) sub[6] = "Spots are off on this server";
  else if (wd == null || wd.spots.length == 0) sub[6] = @PKG@.ExpDefs.grp(d.secrets) + (d.secrets == 1L ? " secret" : " secrets") + " - no spots in this world";
  else {
    int[] c = @PKG@.ExpStore.spotCounts(d, wd);
    int left = (c[1] - c[0]) + (c[3] - c[2]);
    sub[6] = @PKG@.ExpDefs.grp(d.secrets) + (d.secrets == 1L ? " secret" : " secrets") + " - " + left + (left == 1 ? " spot" : " spots") + " left here (" + (c[3] - c[2]) + " secret)";
  }
  int[] pg = new int[4];
  @PKG@.ExpStore.progress(d, wd, pg);
  if (pg[1] > 0) { val[7] = @PKG@.ExpCheck.pct(pg[0], pg[1]) + "% done"; sub[7] = wd.name + " - " + pg[0] + " of " + pg[1] + " done - Checklist tab"; }
  else { val[7] = "No checklist"; sub[7] = @PKG@.ExpCfg.CHECK_ON ? "No checklist in this world - the Checklist tab lists the islands" : "Island checklists are off on this server"; }
  for (int r = 0; r < 2; r++) {
    b.appendInline("#SkyyExBody", "Group #SkyyExRow" + r + " { Anchor: (Height: 158); LayoutMode: Left; Padding: (Top: 8); }");
    for (int c = 0; c < 4; c++) {
      int i = r * 4 + c;
      card(b, "#SkyyExRow" + r, i, CARD_ICON[i], CARD_HEAD[i], val[i], sub[i], CARD_COLOR[i]);
      if (c < 3) b.appendInline("#SkyyExRow" + r, "Label { Anchor: (Width: 16, Height: 150); Text: \"\"; }");
    }
  }
  b.appendInline("#SkyyExBody", "Label { Anchor: (Height: 10); Text: \"\"; }");
  if (d.owed > 0L) {
    String w = @PKG@.ExpDefs.grp(d.owed) + " Exploration XP waiting for SkyySkills 0.4.1";
    if (row) w = @PKG@.ExpDefs.grp(d.owed) + " Exploration XP on its way to SkyySkills";
    line(b, "#SkyyExBody", "SkyyExOwed", w, "#ffb080", 15, 28);
  }
  line(b, "#SkyyExBody", "SkyyExInfo0", "Loot chests - the first time you open a world chest (placed chests never count): XP by zone and tier plus a chance of an extra roll", "#c8d6e4", 15, 50);
  line(b, "#SkyyExBody", "SkyyExInfo1", "Map - every new chunk you walk into pays a little (not while flying - teleports are fine)", "#c8d6e4", 15, 28);
  line(b, "#SkyyExBody", "SkyyExInfo2", "Zones - the first time this profile enters each of Hytale's regions", "#c8d6e4", 15, 28);
  line(b, "#SkyyExBody", "SkyyExInfo5", "Discoveries - admins place named spots (and hidden secret spots) on islands - the first visit pays XP", "#c8d6e4", 15, 28);
  line(b, "#SkyyExBody", "SkyyExInfo3", "Each Exploration level gives a little max Stamina and coins (SkyySkills). /explore quiet hides the chunk XP line.", "#c8d6e4", 15, 28);
  line(b, "#SkyyExBody", "SkyyExInfo4", d.quiet ? "Chunk XP messages are hidden (/explore quiet)" : "", "#9fb8cc", 13, 24);
}""")
M(page, r"""
public static void zonesTab(@UCB@ b, @PKG@.ExpData d) {
  b.appendInline("#SkyyExBody", "Group #SkyyExZones { Anchor: (Height: 620); LayoutMode: Left; }");
  b.appendInline("#SkyyExZones", "Group #SkyyExZoneL { Anchor: (Width: 530, Height: 616); LayoutMode: Top; }");
  b.appendInline("#SkyyExZones", "Label { Anchor: (Width: 20, Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyExZones", "Group #SkyyExZoneR { Anchor: (Width: 530, Height: 616); LayoutMode: Top; }");
  for (int g = 0; g < @PKG@.ExpDefs.G_NAME.length; g++) {
    String par = @PKG@.ExpDefs.G_SIDE[g] == 0 ? "#SkyyExZoneL" : "#SkyyExZoneR";
    int n = 0;
    int f = 0;
    for (int i = 0; i < @PKG@.ExpDefs.NR; i++) {
      if (@PKG@.ExpDefs.R_GROUP[i] != g) continue;
      n++;
      if (@PKG@.ExpStore.hasZone(d, @PKG@.ExpDefs.R_ID[i])) f++;
    }
    b.appendInline(par, "Label #SkyyExZH" + g + " { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + @PKG@.ExpDefs.G_COLOR[g] + ", VerticalAlignment: Center); }");
    b.set("#SkyyExZH" + g + ".Text", @PKG@.ExpDefs.G_NAME[g] + "  (" + f + " of " + n + ")");
    for (int i = 0; i < @PKG@.ExpDefs.NR; i++) {
      if (@PKG@.ExpDefs.R_GROUP[i] != g) continue;
      boolean got = @PKG@.ExpStore.hasZone(d, @PKG@.ExpDefs.R_ID[i]);
      b.appendInline(par, "Label #SkyyExZ" + i + " { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: " + (got ? "#9adf86" : "#7f94a8") + ", VerticalAlignment: Center); }");
      b.set("#SkyyExZ" + i + ".Text", "    " + @PKG@.ExpDefs.R_NAME[i] + "  - " + (got ? "found" : @PKG@.ExpDefs.grp(@PKG@.ExpCfg.zoneXp(@PKG@.ExpDefs.R_ID[i])) + " XP"));
    }
    b.appendInline(par, "Label { Anchor: (Height: 8); Text: \"\"; }");
  }
}""")
M(page, r"""
public static void titlesTab(@UCB@ b, @UEB@ ev, @PKG@.ExpData d, int lv) {
  int sel = @PKG@.ExpTitles.selected(d, lv);
  b.appendInline("#SkyyExBody", "Group #SkyyExTHead { Anchor: (Height: 44); LayoutMode: Left; }");
  b.appendInline("#SkyyExTHead", "Label #SkyyExCur { Anchor: (Width: 880, Height: 38); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center); }");
  b.set("#SkyyExCur.Text", "Your title: " + (sel < 0 ? "none" : @PKG@.ExpDefs.T_NAME[sel]) + "   -   " + @PKG@.ExpTitles.count(d, lv) + " of " + @PKG@.ExpDefs.NT + " earned - it shows in front of your chat messages");
  b.appendInline("#SkyyExTHead", "TextButton #SkyyExNone { Anchor: (Width: 180, Height: 38); Text: \"No title\"; @BSOFF@ }");
  ev.addEventBinding(@BT@.Activating, "#SkyyExNone", @EVD@.of("a", "exnone"));
  b.appendInline("#SkyyExBody", "Group #SkyyExTCols { Anchor: (Height: 580); LayoutMode: Left; }");
  b.appendInline("#SkyyExTCols", "Group #SkyyExTL { Anchor: (Width: 530, Height: 576); LayoutMode: Top; }");
  b.appendInline("#SkyyExTCols", "Label { Anchor: (Width: 20, Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyExTCols", "Group #SkyyExTR { Anchor: (Width: 530, Height: 576); LayoutMode: Top; }");
  int half = (@PKG@.ExpDefs.NT + 1) / 2;
  for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
    String par = i < half ? "#SkyyExTL" : "#SkyyExTR";
    boolean e = @PKG@.ExpTitles.earned(d, lv, i);
    String col = e ? @PKG@.ExpDefs.KIND_COLOR[@PKG@.ExpDefs.T_KIND[i]] : "#8a8a8a";
    b.appendInline(par, "Group #SkyyExT" + i + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyExT" + i, "Label #SkyyExTN" + i + " { Anchor: (Width: 190, Height: 36); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
    b.set("#SkyyExTN" + i + ".Text", @PKG@.ExpDefs.T_NAME[i]);
    b.appendInline("#SkyyExT" + i, "Label #SkyyExTQ" + i + " { Anchor: (Width: 250, Height: 36); Text: \"\"; Style: (FontSize: 13, TextColor: #9fb8cc, VerticalAlignment: Center, Wrap: true); }");
    b.set("#SkyyExTQ" + i + ".Text", @PKG@.ExpDefs.T_TEXT[i]);
    if (e && i != sel) {
      b.appendInline("#SkyyExT" + i, "TextButton #SkyyExUse" + i + " { Anchor: (Width: 80, Height: 34); Text: \"Use\"; @BSG@ }");
      ev.addEventBinding(@BT@.Activating, "#SkyyExUse" + i, @EVD@.of("a", "exuse" + i));
    } else {
      b.appendInline("#SkyyExT" + i, "Label #SkyyExTS" + i + " { Anchor: (Width: 80, Height: 34); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + (e ? "#9adf86" : "#b07a68") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
      b.set("#SkyyExTS" + i + ".Text", e ? "In use" : "Locked");
    }
  }
}""")
# islands with a checklist (on, at least one entry): the current world first, then by name - world files (wf)
M(page, r"""
public static String[] islands(String curWf) {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.SpotReg.W.values().iterator();
  while (it.hasNext()) {
    @PKG@.WorldDef w = (@PKG@.WorldDef) it.next();
    if (w.checklist && w.checks > 0) l.add(w);
  }
  @PKG@.WorldDef[] a = new @PKG@.WorldDef[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (@PKG@.WorldDef) l.get(i);
  for (int i = 1; i < a.length; i++) {
    @PKG@.WorldDef v = a[i];
    int j = i - 1;
    while (j >= 0 && a[j].name.compareToIgnoreCase(v.name) > 0) { a[j + 1] = a[j]; j--; }
    a[j + 1] = v;
  }
  String[] r = new String[a.length];
  int n = 0;
  for (int i = 0; i < a.length; i++) if (a[i].wf.equals(curWf)) { r[n] = a[i].wf; n++; }
  for (int i = 0; i < a.length; i++) if (!a[i].wf.equals(curWf)) { r[n] = a[i].wf; n++; }
  return r;
}""")
M(page, r"""
public void checklistTab(@UCB@ b, @UEB@ ev, @PKG@.ExpData d, String wn) {
  String cur = wn == null || @PKG@.ExpCfg.excluded(wn) ? "" : @PKG@.ChestReg.wf(wn);
  if (!@PKG@.ExpCfg.CHECK_ON) { line(b, "#SkyyExBody", "SkyyExCkNone", "Island checklists are turned off on this server (checklist.enabled)", "#ffb080", 17, 60); this.ckList = new String[0]; return; }
  String[] isl = islands(cur);
  this.ckList = isl;
  if (isl.length == 0) { line(b, "#SkyyExBody", "SkyyExCkNone", "No island checklists on this server yet - admins set them up with /exploreadmin", "#9fb8cc", 17, 60); return; }
  int idx = 0;
  for (int i = 0; i < isl.length; i++) if (isl[i].equals(this.ckWorld)) idx = i;
  this.ckIdx = idx;
  this.ckWorld = isl[idx];
  @PKG@.WorldDef wd = @PKG@.SpotReg.byWf(isl[idx]);
  if (wd == null) return;
  int[] pg = new int[4];
  @PKG@.ExpStore.progress(d, wd, pg);
  b.appendInline("#SkyyExBody", "Group #SkyyExCkTop { Anchor: (Height: 48); LayoutMode: Left; }");
  b.appendInline("#SkyyExCkTop", "TextButton #SkyyExCkPrevW { Anchor: (Width: 150, Height: 42); Text: \"< Island\"; @BSOFF@ }");
  b.appendInline("#SkyyExCkTop", "Label { Anchor: (Width: 10, Height: 42); Text: \"\"; }");
  b.appendInline("#SkyyExCkTop", "Label #SkyyExCkName { Anchor: (Width: 740, Height: 42); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyExCkTop", "Label { Anchor: (Width: 10, Height: 42); Text: \"\"; }");
  b.appendInline("#SkyyExCkTop", "TextButton #SkyyExCkNextW { Anchor: (Width: 150, Height: 42); Text: \"Island >\"; @BSOFF@ }");
  ev.addEventBinding(@BT@.Activating, "#SkyyExCkPrevW", @EVD@.of("a", "exwp"));
  ev.addEventBinding(@BT@.Activating, "#SkyyExCkNextW", @EVD@.of("a", "exwn"));
  b.set("#SkyyExCkName.Text", wd.name + (wd.wf.equals(cur) ? " (you are here)" : "") + " - " + (idx + 1) + " of " + isl.length);
  line(b, "#SkyyExBody", "SkyyExCkHead", pg[0] + " of " + pg[1] + " done - " + @PKG@.ExpCheck.pct(pg[0], pg[1]) + "%" + (pg[3] > 0 ? " - secrets " + pg[2] + " of " + pg[3] : ""), "#e6eef6", 17, 30);
  b.appendInline("#SkyyExBody", "Label { Anchor: (Height: 4); Text: \"\"; }");
  int fill = pg[1] <= 0 ? 0 : (int) ((long) pg[0] * 1080L / (long) pg[1]);
  b.appendInline("#SkyyExBody", "Group #SkyyExCkBar { Anchor: (Width: 1080, Height: 16); Background: #1d2c3c; LayoutMode: Left; }");
  if (fill > 0) b.appendInline("#SkyyExCkBar", "Group #SkyyExCkFill { Anchor: (Width: " + fill + ", Height: 16); Background: #9adf86; }");
  b.appendInline("#SkyyExBody", "Label { Anchor: (Height: 8); Text: \"\"; }");
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < wd.spots.length; i++) if (wd.spots[i].check) rows.add(wd.spots[i]);
  for (int i = 0; i < wd.entries.length; i++) rows.add(wd.entries[i]);
  int pages = (rows.size() + 17) / 18;
  if (pages < 1) pages = 1;
  if (this.ckPage >= pages) this.ckPage = pages - 1;
  if (this.ckPage < 0) this.ckPage = 0;
  Object fo = d.found.get(wd.wf);
  java.util.concurrent.ConcurrentHashMap fm = fo == null ? null : (java.util.concurrent.ConcurrentHashMap) fo;
  b.appendInline("#SkyyExBody", "Group #SkyyExCkCols { Anchor: (Height: 414); LayoutMode: Left; }");
  b.appendInline("#SkyyExCkCols", "Group #SkyyExCkL { Anchor: (Width: 530, Height: 414); LayoutMode: Top; }");
  b.appendInline("#SkyyExCkCols", "Label { Anchor: (Width: 20, Height: 10); Text: \"\"; }");
  b.appendInline("#SkyyExCkCols", "Group #SkyyExCkR { Anchor: (Width: 530, Height: 414); LayoutMode: Top; }");
  for (int i = 0; i < 18; i++) {
    int at = this.ckPage * 18 + i;
    if (at >= rows.size()) break;
    Object o = rows.get(at);
    String par = i < 9 ? "#SkyyExCkL" : "#SkyyExCkR";
    boolean done = false;
    String text = "";
    String val = "";
    String tcol = "#e6eef6";
    if (o instanceof @PKG@.SpotDef) {
      @PKG@.SpotDef s = (@PKG@.SpotDef) o;
      done = fm != null && fm.containsKey(s.id);
      boolean hide = s.secret && !done;
      text = hide ? "??? Secret spot" : s.name;
      if (!hide && s.xp > 0L) val = "+" + @PKG@.ExpDefs.grp(s.xp) + " XP";
      tcol = hide ? "#d890ff" : (done ? "#c8f0c0" : "#e6eef6");
    } else {
      @PKG@.EntryDef e = (@PKG@.EntryDef) o;
      done = @PKG@.ExpStore.entryDone(d, wd, e);
      text = e.text;
      if (e.type == 2) { long oc = (long) @PKG@.ExpStore.openedCount(d, wd.wf); val = (oc > e.cnt ? e.cnt : oc) + "/" + e.cnt; }
      else if (e.type == 3) val = "region";
      tcol = done ? "#c8f0c0" : "#e6eef6";
    }
    b.appendInline(par, "Group #SkyyExCkRow" + i + " { Anchor: (Height: 46); LayoutMode: Left; }");
    b.appendInline("#SkyyExCkRow" + i, "Label #SkyyExCkS" + i + " { Anchor: (Width: 80, Height: 42); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (done ? "#9adf86" : "#7f94a8") + ", VerticalAlignment: Center); }");
    b.appendInline("#SkyyExCkRow" + i, "Label #SkyyExCkT" + i + " { Anchor: (Width: 330, Height: 42); Text: \"\"; Style: (FontSize: 15, TextColor: " + tcol + ", VerticalAlignment: Center, Wrap: true); }");
    b.appendInline("#SkyyExCkRow" + i, "Label #SkyyExCkV" + i + " { Anchor: (Width: 110, Height: 42); Text: \"\"; Style: (FontSize: 14, TextColor: #ffd27a, HorizontalAlignment: End, VerticalAlignment: Center); }");
    b.set("#SkyyExCkS" + i + ".Text", done ? "Done" : "-");
    b.set("#SkyyExCkT" + i + ".Text", text);
    b.set("#SkyyExCkV" + i + ".Text", val);
  }
  b.appendInline("#SkyyExBody", "Group #SkyyExCkPg { Anchor: (Height: 48); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline("#SkyyExCkPg", "TextButton #SkyyExCkPrev { Anchor: (Width: 150, Height: 42); Text: \"< Prev\"; @BSOFF@ }");
  b.appendInline("#SkyyExCkPg", "Label #SkyyExCkPgL { Anchor: (Width: 300, Height: 42); Text: \"\"; Style: (FontSize: 15, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyExCkPg", "TextButton #SkyyExCkNext { Anchor: (Width: 150, Height: 42); Text: \"Next >\"; @BSOFF@ }");
  ev.addEventBinding(@BT@.Activating, "#SkyyExCkPrev", @EVD@.of("a", "excp"));
  ev.addEventBinding(@BT@.Activating, "#SkyyExCkNext", @EVD@.of("a", "excn"));
  b.set("#SkyyExCkPgL.Text", "page " + (this.ckPage + 1) + " of " + pages);
  String rw;
  if (wd.rewardXp <= 0L && wd.rewardCoins <= 0L) rw = "No reward set for this island";
  else {
    rw = "Reward at 100%:" + (wd.rewardXp > 0L ? " +" + @PKG@.ExpDefs.grp(wd.rewardXp) + " Exploration XP" : "") + (wd.rewardCoins > 0L ? (wd.rewardXp > 0L ? "," : "") + " +" + @PKG@.ExpDefs.grp(wd.rewardCoins) + " coins" + (@PKG@.ExpIO.fn("coins:fn:add") == null ? " (needs SkyyCoins)" : "") : "");
    if (@PKG@.ExpStore.isDone(d, wd.wf)) rw = rw + " - paid";
  }
  line(b, "#SkyyExBody", "SkyyExCkFoot", rw, "#9fb8cc", 13, 26);
}""")
M(page, r"""
public static String lvlText(java.util.UUID u, int lvl) {
  if (lvl < 0) return "SkyySkills not installed";
  return "Exploration " + lvl + " - " + @PKG@.ExpDefs.fmt(@PKG@.ExpSkill.xp(u)) + " XP";
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.lastBuild = System.currentTimeMillis();
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  int lvl = @PKG@.ExpSkill.level(u);
  int lv = lvl < 0 ? 0 : lvl;
  int t = this.tab;
  if (t < 0 || t > 3) t = 0;
  String wn = null;
  Object ext = st.getExternalData();
  if (ext instanceof @EST@) { @WLD@ w = ((@EST@) ext).getWorld(); if (w != null) wn = w.getName(); }
  b.appendInline((String) null, "Group #SkyyExRoot { Anchor: (Width: 1120, Height: 800); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 12); LayoutMode: Top; }");
  b.appendInline("#SkyyExRoot", "Group #SkyyExHead { Anchor: (Height: 48); LayoutMode: Left; }");
  for (int i = 0; i < 4; i++) {
    b.appendInline("#SkyyExHead", "TextButton #SkyyExTab" + i + " { Anchor: (Width: 150, Height: 42); Text: \"" + TABS[i] + "\"; " + (i == t ? "@BTON@" : "@BTOFF@") + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyExTab" + i, @EVD@.of("a", "extab" + i));
    b.appendInline("#SkyyExHead", "Label { Anchor: (Width: 8, Height: 42); Text: \"\"; }");
  }
  b.appendInline("#SkyyExHead", "Label #SkyyExLvl { Anchor: (Width: 440, Height: 42); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #e0a040, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyExLvl.Text", lvlText(u, lvl));
  b.appendInline("#SkyyExRoot", "Label #SkyyExNote { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 13, TextColor: #9fb8cc, VerticalAlignment: Center); }");
  b.set("#SkyyExNote.Text", d.bad ? BADNOTE : NOTE);
  b.appendInline("#SkyyExRoot", "Group { Anchor: (Height: 2); Background: #e0a040; }");
  b.appendInline("#SkyyExRoot", "Group #SkyyExBody { Anchor: (Height: 640); LayoutMode: Top; Padding: (Top: 6); }");
  if (t == 0) overview(b, u, d, lvl, wn);
  else if (t == 1) zonesTab(b, d);
  else if (t == 2) titlesTab(b, ev, d, lv);
  else checklistTab(b, ev, d, wn);
  b.appendInline("#SkyyExRoot", "Group #SkyyExFoot { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 8); }");
  if (@PKG@.ExpSkill.hasSkills()) {
    b.appendInline("#SkyyExFoot", "TextButton #SkyyExSkills { Anchor: (Width: 170, Height: 42); Text: \"< Skills\"; @BSG@ }");
    ev.addEventBinding(@BT@.Activating, "#SkyyExSkills", @EVD@.of("a", "exskills"));
    b.appendInline("#SkyyExFoot", "Label { Anchor: (Width: 12, Height: 42); Text: \"\"; }");
  }
  if (@PKG@.ExpSkill.treeNames().indexOf("Exploration") >= 0) {
    b.appendInline("#SkyyExFoot", "TextButton #SkyyExTree { Anchor: (Width: 230, Height: 42); Text: \"Exploration tree\"; @BSG@ }");
    ev.addEventBinding(@BT@.Activating, "#SkyyExTree", @EVD@.of("a", "extree"));
    b.appendInline("#SkyyExFoot", "Label { Anchor: (Width: 12, Height: 42); Text: \"\"; }");
  }
  b.appendInline("#SkyyExFoot", "Label #SkyyExMsg { Anchor: (Width: 600, Height: 42); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffe08a, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyExMsg.Text", this.msg == null ? "" : this.msg);
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    if (System.currentTimeMillis() - this.lastBuild < 1000L) return;
    if (data.indexOf("exskills\"") >= 0) {
      if (!@PKG@.ExpSkill.hasSkills()) { this.msg = "SkyySkills is not installed - there is no skills page"; rebuild(); return; }
      @CMGR@.get().handleCommand(this.playerRef, "skills");
      return;
    }
    if (data.indexOf("extree\"") >= 0) {
      @CMGR@.get().handleCommand(this.playerRef, "tree exploration");
      return;
    }
    for (int i = 0; i < 4; i++) {
      if (data.indexOf("extab" + i + "\"") >= 0) { this.tab = i; this.msg = ""; this.ckPage = 0; rebuild(); return; }
    }
    int n = this.ckList == null ? 0 : this.ckList.length;
    if (data.indexOf("exwp\"") >= 0) { if (n > 0) { this.ckIdx = (this.ckIdx + n - 1) % n; this.ckWorld = this.ckList[this.ckIdx]; } this.ckPage = 0; rebuild(); return; }
    if (data.indexOf("exwn\"") >= 0) { if (n > 0) { this.ckIdx = (this.ckIdx + 1) % n; this.ckWorld = this.ckList[this.ckIdx]; } this.ckPage = 0; rebuild(); return; }
    if (data.indexOf("excp\"") >= 0) { this.ckPage = this.ckPage - 1; rebuild(); return; }
    if (data.indexOf("excn\"") >= 0) { this.ckPage = this.ckPage + 1; rebuild(); return; }
    if (data.indexOf("exnone\"") >= 0) { this.msg = @PKG@.ExpTitles.choose(this.playerRef, -2); rebuild(); return; }
    for (int i = 0; i < @PKG@.ExpDefs.NT; i++) {
      if (data.indexOf("exuse" + i + "\"") >= 0) { this.msg = @PKG@.ExpTitles.choose(this.playerRef, i); rebuild(); return; }
    }
  } catch (Throwable e) { @PKG@.ExpCfg.warn("explore page event failed: " + e); }
}""")

# ================= 0.2 ExAdminOps: every admin change, shared by the admin page and the commands (spec 6.5; the admin's world thread).
# Order in each op: permission, excluded world, bad / hand-edited file, parse + sanitize, SpotReg mutation, save soon, admin.log,
# ExpState.inside (add / move). Replies start with + (done), - (refused) or = (info / confirm). =================
F(aop, 'public static final String PERM = "skyyexploration.admin";')
F(aop, "public static final java.util.concurrent.ConcurrentHashMap CONFIRM = new java.util.concurrent.ConcurrentHashMap();")  # admin UUID -> "key|millis"
M(aop, r"""
public static String colorOf(String r) {
  if (r == null || r.length() == 0) return "#ffe08a";
  char c = r.charAt(0);
  if (c == '+') return "#9adf86";
  if (c == '-') return "#ffb080";
  if (c == '=') return "#9fd0ff";
  return "#ffe08a";
}""")
M(aop, r"""
public static String textOf(String r) {
  if (r == null) return "";
  if (r.length() > 0 && (r.charAt(0) == '+' || r.charAt(0) == '-' || r.charAt(0) == '=')) return r.substring(1);
  return r;
}""")
M(aop, r"""
public static void tell(@PR@ pr, String r) {
  if (pr == null || r == null) return;
  String col = colorOf(r);
  String[] ls = textOf(r).split("\n");
  for (int i = 0; i < ls.length; i++) {
    try { pr.sendMessage(@MSG@.raw((i == 0 ? "[Exploration] " : "  ") + ls[i]).color(col)); } catch (Throwable t) { }
  }
}""")
M(aop, r"""
public static boolean perm(@PR@ pr) {
  try { return pr != null && pr.hasPermission(PERM); } catch (Throwable t) { return false; }
}""")
M(aop, r"""
public static int[] pos(@REF@ ref, @ST@ st) {
  try {
    @TRC@ tc = (@TRC@) st.getComponent(ref, @TRC@.getComponentType());
    if (tc == null || tc.getPosition() == null) return null;
    @V3D@ p = tc.getPosition();
    return new int[] { (int) Math.floor(p.x()), (int) Math.floor(p.y()), (int) Math.floor(p.z()) };
  } catch (Throwable t) { return null; }
}""")
M(aop, r"""
public static @WLD@ worldOf(@ST@ st) {
  try {
    Object ext = st.getExternalData();
    if (ext instanceof @EST@) return ((@EST@) ext).getWorld();
  } catch (Throwable t) { }
  return null;
}""")
M(aop, r"""
public static String pre(@PR@ pr, @WLD@ w, boolean file) {
  if (!perm(pr)) return "-You are not an admin (skyyexploration.admin)";
  if (w == null) return "-Could not read your world";
  String wn = w.getName();
  if (@PKG@.ExpCfg.excluded(wn)) return "-This world never pays exploration (" + @PKG@.ExpCfg.excludedWhy(wn) + ") - spots and checklists only work in shared worlds";
  if (file) return @PKG@.SpotReg.guard(@PKG@.ChestReg.wf(wn));
  return null;
}""")
# 1 = yes (secret / yes / true / on / 1), 0 = no (open / no / false / off / 0), -1 = neither
M(aop, r"""
public static int yesNo(String s) {
  if (s == null) return -1;
  String l = s.trim().toLowerCase();
  if (l.equals("secret") || l.equals("yes") || l.equals("true") || l.equals("on") || l.equals("1") || l.equals("y")) return 1;
  if (l.equals("open") || l.equals("no") || l.equals("false") || l.equals("off") || l.equals("0") || l.equals("n")) return 0;
  return -1;
}""")
M(aop, r"""
public static long defaultXp(@PKG@.WorldDef w, boolean secret) {
  if (w != null) {
    long v = secret ? w.secretXp : w.spotXp;
    if (v >= 0L) return v;
  }
  return secret ? @PKG@.ExpCfg.SECRET_XP : @PKG@.ExpCfg.SPOT_XP;
}""")
M(aop, r"""
public static void selfInside(@PR@ pr, String id, String wf) {
  try {
    @PKG@.ExpState s = @PKG@.ExpTick.state(pr.getUuid());
    s.inside = id;
    s.insideWf = wf;
  } catch (Throwable t) { }
}""")
# true when a second click / command within 10 s confirms this key; else remembers it
M(aop, r"""
public static boolean confirm(@PR@ pr, String key) {
  java.util.UUID u = pr.getUuid();
  long now = System.currentTimeMillis();
  Object o = CONFIRM.get(u);
  if (o instanceof String) {
    String s = (String) o;
    int bar = s.lastIndexOf('|');
    if (bar > 0 && s.substring(0, bar).equals(key)) {
      long at = 0L;
      try { at = Long.parseLong(s.substring(bar + 1)); } catch (Throwable t) { at = 0L; }
      if (now - at < 10000L) { CONFIRM.remove(u); return true; }
    }
  }
  CONFIRM.put(u, key + "|" + now);
  return false;
}""")
M(aop, r"""
public static boolean pending(java.util.UUID u, String key) {
  Object o = CONFIRM.get(u);
  if (!(o instanceof String)) return false;
  String s = (String) o;
  int bar = s.lastIndexOf('|');
  if (bar <= 0 || !s.substring(0, bar).equals(key)) return false;
  try { return System.currentTimeMillis() - Long.parseLong(s.substring(bar + 1)) < 10000L; } catch (Throwable t) { return false; }
}""")
M(aop, r"""
public static String yn(boolean b) {
  return b ? "yes" : "no";
}""")
M(aop, r"""
public static java.util.ArrayList onlineIn(@WLD@ w) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (w == null) return out;
  String wn = w.getName();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      @PR@ p = (@PR@) o;
      java.util.UUID wu = p.getWorldUuid();
      @WLD@ pw = wu == null ? null : @UNI@.get().getWorld(wu);
      if (pw != null && wn.equals(pw.getName())) out.add(p);
    }
  } catch (Throwable t) { }
  return out;
}""")
M(aop, r"""
public static @PR@ findOnline(String name) {
  String n = name == null ? "" : name.trim();
  if (n.length() == 0) return null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(n)) return (@PR@) o;
    }
  } catch (Throwable t) { }
  return null;
}""")
# { found by, online here } for a spot; cached records only
M(aop, r"""
public static int[] foundBy(@PKG@.WorldDef wd, String id, java.util.ArrayList on) {
  int[] r = new int[2];
  for (int i = 0; i < on.size(); i++) {
    @PR@ p = (@PR@) on.get(i);
    r[1] = r[1] + 1;
    @PKG@.ExpData d = @PKG@.ExpStore.cached(@PKG@.ExpIO.pkey(p.getUuid()));
    if (d != null && @PKG@.ExpStore.hasSpot(d, wd.wf, id)) r[0] = r[0] + 1;
  }
  return r;
}""")
M(aop, r"""
public static int haveEntry(@PKG@.WorldDef wd, @PKG@.EntryDef e, java.util.ArrayList on) {
  int n = 0;
  for (int i = 0; i < on.size(); i++) {
    @PKG@.ExpData d = @PKG@.ExpStore.cached(@PKG@.ExpIO.pkey(((@PR@) on.get(i)).getUuid()));
    if (d != null && !d.bad && @PKG@.ExpStore.entryDone(d, wd, e)) n++;
  }
  return n;
}""")
M(aop, r"""
public static String entryKind(@PKG@.EntryDef e) {
  if (e.type == 1) return "loot chest - " + e.arg;
  if (e.type == 2) return "open " + e.cnt + " loot chests";
  if (e.type == 3) return "region " + e.arg;
  return "custom";
}""")
# ---- spots (spec 3.1)
M(aop, r"""
public static String spotAdd(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String name0, String rad, String xp0, String sec) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String name = @PKG@.ExpDefs.clean(name0, 40);
  if (name.length() == 0) return "-Give the spot a name (1 to 40 letters; _ becomes a space)";
  int[] p = pos(ref, st);
  if (p == null) return "-Could not read your position";
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef cur = @PKG@.SpotReg.byWf(wf);
  boolean secret = false;
  if (sec != null && sec.trim().length() > 0) {
    int yn = yesNo(sec);
    if (yn < 0) return "-The last word is secret or open (yes or no) - nothing added";
    secret = yn == 1;
  }
  String note = "";
  long r = (long) @PKG@.ExpCfg.SPOT_R;
  if (rad != null && rad.trim().length() > 0) {
    r = @PKG@.ExpDefs.parseNum(rad, -1L);
    if (r < 1L) return "-The radius is a whole number of blocks, 1 to " + @PKG@.ExpCfg.SPOT_RMAX + " - nothing added";
    if (r > (long) @PKG@.ExpCfg.SPOT_RMAX) { r = (long) @PKG@.ExpCfg.SPOT_RMAX; note = note + " (radius capped at spots.maxRadius " + r + ")"; }
  }
  long x = defaultXp(cur, secret);
  if (xp0 != null && xp0.trim().length() > 0) {
    x = @PKG@.ExpDefs.parseNum(xp0, -1L);
    if (x < 0L) return "-XP is a whole number, 0 to 400,000 - nothing added";
    if (x > 400000L) { x = 400000L; note = note + " (XP capped at 400,000)"; }
  }
  String[] res = @PKG@.SpotReg.addSpot(wn, wf, name, p[0], p[1], p[2], (int) r, x, secret);
  if (res[0] != null) return res[0];
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, wn, "spot add " + res[1] + " name=" + name + " pos=" + p[0] + " " + p[1] + " " + p[2] + " r=" + r + " xp=" + x + " secret=" + yn(secret) + " check=" + yn(res[2].length() == 0));
  selfInside(pr, res[1], wf);
  return "+Added " + (secret ? "secret spot " : "spot ") + name + " (" + res[1] + ") at " + p[0] + " " + p[1] + " " + p[2] + " - radius " + r + ", " + @PKG@.ExpDefs.grp(x) + " XP" + res[2] + note + ". Walk out and back in (adventure mode) to test it.";
}""")
M(aop, r"""
public static String spotMove(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String token) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wf = @PKG@.ChestReg.wf(w.getName());
  String[] err = new String[1];
  @PKG@.SpotDef sp = @PKG@.SpotReg.resolveSpot(@PKG@.SpotReg.byWf(wf), token, err);
  if (sp == null) return err[0];
  int[] p = pos(ref, st);
  if (p == null) return "-Could not read your position";
  String r = @PKG@.SpotReg.moveSpot(wf, sp.id, p[0], p[1], p[2]);
  if (r != null) return r;
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "spot move " + sp.id + " name=" + sp.name + " " + sp.x + " " + sp.y + " " + sp.z + " -> " + p[0] + " " + p[1] + " " + p[2]);
  selfInside(pr, sp.id, wf);
  return "+Moved " + sp.name + " (" + sp.id + ") to " + p[0] + " " + p[1] + " " + p[2] + " - the id and every find stay";
}""")
M(aop, r"""
public static String spotRemove(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String token) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wf = @PKG@.ChestReg.wf(w.getName());
  String[] err = new String[1];
  @PKG@.SpotDef sp = @PKG@.SpotReg.resolveSpot(@PKG@.SpotReg.byWf(wf), token, err);
  if (sp == null) return err[0];
  if (!confirm(pr, "rm|" + wf + "|" + sp.id)) return "=Remove " + sp.name + " (" + sp.id + ")" + (sp.check ? " and its checklist entry" : "") + "? Click again (or repeat the command) within 10 s to confirm";
  String r = @PKG@.SpotReg.removeSpot(wf, sp.id);
  if (r != null) return r;
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "spot remove " + sp.id + " name=" + sp.name + " pos=" + sp.x + " " + sp.y + " " + sp.z);
  return "+Removed " + sp.name + " (" + sp.id + "). Old finds of it stay in the players' files (harmless - ids are never reused)";
}""")
M(aop, r"""
public static String spotTp(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String token, boolean closePage) {
  String e = pre(pr, w, false);
  if (e != null) return e;
  String wf = @PKG@.ChestReg.wf(w.getName());
  String[] err = new String[1];
  @PKG@.SpotDef sp = @PKG@.SpotReg.resolveSpot(@PKG@.SpotReg.byWf(wf), token, err);
  if (sp == null) return err[0];
  if (st.getComponent(ref, @TP@.getComponentType()) != null) return "-You are already teleporting";
  @TRC@ mtc = (@TRC@) st.getComponent(ref, @TRC@.getComponentType());
  @HR@ mhr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
  @R3F@ hr = mhr != null ? mhr.getRotation() : null;
  @R3F@ rot = hr != null ? new @R3F@(hr.x, hr.y, hr.z) : new @R3F@();
  try {
    if (mtc != null && mtc.getPosition() != null) {
      @V3D@ p = mtc.getPosition();
      @TPH@ h = (@TPH@) st.ensureAndGetComponent(ref, @TPH@.getComponentType());
      if (h != null) h.append(w, new @V3D@(p.x(), p.y(), p.z()), new @R3F@(rot.x, rot.y, rot.z), "Exploration: " + sp.name);
    }
  } catch (Throwable t) { }
  try {
    st.addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(w, new @V3D@((double) sp.x + 0.5, (double) sp.y, (double) sp.z + 0.5), rot));
  } catch (Throwable t) {
    @PKG@.ExpCfg.warn("spot teleport failed: " + t);
    return "-Could not teleport (" + t.getClass().getSimpleName() + ")";
  }
  if (closePage) {
    try {
      @PLA@ pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      if (pl != null) pl.getPageManager().setPage(ref, st, @PGE@.None);
    } catch (Throwable t) { }
  }
  return "+Teleporting to " + sp.name + " (" + sp.id + ") - /tp back returns";
}""")
M(aop, r"""
public static String spotList(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w) {
  String e = pre(pr, w, false);
  if (e != null) return e;
  @PKG@.WorldDef wd = @PKG@.SpotReg.byName(w.getName());
  if (wd == null || wd.spots.length == 0) return "=No spots in this world yet - /exploreadmin opens the admin page, or /exploreadmin spot add <name>";
  int[] p = pos(ref, st);
  int n = wd.spots.length;
  double[] dist = new double[n];
  int[] ord = new int[n];
  for (int i = 0; i < n; i++) {
    ord[i] = i;
    @PKG@.SpotDef s = wd.spots[i];
    dist[i] = p == null ? 0.0 : Math.sqrt((double) ((long) (s.x - p[0]) * (s.x - p[0]) + (long) (s.y - p[1]) * (s.y - p[1]) + (long) (s.z - p[2]) * (s.z - p[2])));
  }
  for (int i = 1; i < n; i++) {
    int v = ord[i];
    int j = i - 1;
    while (j >= 0 && dist[ord[j]] > dist[v]) { ord[j + 1] = ord[j]; j--; }
    ord[j + 1] = v;
  }
  StringBuilder sb = new StringBuilder();
  sb.append("=").append(n).append(" spots in ").append(wd.name).append(" (").append(wd.secrets).append(" secret), nearest first:");
  for (int i = 0; i < n && i < 25; i++) {
    @PKG@.SpotDef s = wd.spots[ord[i]];
    sb.append('\n').append(s.id).append(' ').append(s.name).append(" - ").append(s.x).append(' ').append(s.y).append(' ').append(s.z).append(" - r").append(s.r).append(" - ").append(@PKG@.ExpDefs.grp(s.xp)).append(" XP").append(s.secret ? " - secret" : "").append(s.check ? " - on checklist" : "").append(" - ").append((long) dist[ord[i]]).append(" m");
  }
  if (n > 25) sb.append("\n... and ").append(n - 25).append(" more (the admin page lists all)");
  return sb.toString();
}""")
M(aop, r"""
public static String spotEdit(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String token, String field, String value) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wf = @PKG@.ChestReg.wf(w.getName());
  String[] err = new String[1];
  @PKG@.SpotDef sp = @PKG@.SpotReg.resolveSpot(@PKG@.SpotReg.byWf(wf), token, err);
  if (sp == null) return err[0];
  String f = field == null ? "" : field.trim().toLowerCase();
  String v = value == null ? "" : value.trim();
  String r;
  String what;
  String note = "";
  if (f.equals("name")) {
    String nm = @PKG@.ExpDefs.clean(v, 40);
    if (nm.length() == 0) return "-Type the new name (1 to 40 letters)";
    if (nm.equals(sp.name)) return "=" + sp.id + " is already called " + nm;
    r = @PKG@.SpotReg.editSpot(wf, sp.id, 0, nm, 0L, 0L);
    what = "name " + sp.name + " -> " + nm;
  } else if (f.equals("radius") || f.equals("r")) {
    long rv = @PKG@.ExpDefs.parseNum(v, -1L);
    if (rv < 1L) return "-The radius is a whole number of blocks, 1 to " + @PKG@.ExpCfg.SPOT_RMAX;
    if (rv > (long) @PKG@.ExpCfg.SPOT_RMAX) { rv = (long) @PKG@.ExpCfg.SPOT_RMAX; note = " (capped at spots.maxRadius)"; }
    r = @PKG@.SpotReg.editSpot(wf, sp.id, 1, null, rv, 0L);
    what = "radius " + sp.r + " -> " + rv;
  } else if (f.equals("xp")) {
    long xv = @PKG@.ExpDefs.parseNum(v, -1L);
    if (xv < 0L) return "-XP is a whole number, 0 to 400,000";
    if (xv > 400000L) { xv = 400000L; note = " (capped at 400,000)"; }
    r = @PKG@.SpotReg.editSpot(wf, sp.id, 2, null, xv, 0L);
    what = "xp " + sp.xp + " -> " + xv;
  } else if (f.equals("secret") || f.equals("checklist")) {
    int b = yesNo(v);
    if (b < 0) return "-" + f + " is yes or no";
    r = @PKG@.SpotReg.editSpot(wf, sp.id, f.equals("secret") ? 3 : 4, null, (long) b, 0L);
    what = f + " " + yn(f.equals("secret") ? sp.secret : sp.check) + " -> " + yn(b == 1);
  } else return "-The field is name, radius, xp, secret or checklist";
  if (r != null) return r;
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "spot edit " + sp.id + " " + what);
  return "+" + sp.id + " " + what + note;
}""")
# the page's "Save radius and XP": blank keeps the value
M(aop, r"""
public static String spotSetRX(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String id, String rad, String xp0) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wf = @PKG@.ChestReg.wf(w.getName());
  @PKG@.SpotDef sp = @PKG@.SpotReg.spotById(@PKG@.SpotReg.byWf(wf), id);
  if (sp == null) return "-That spot was removed - Refresh";
  long rv = (long) sp.r;
  long xv = sp.xp;
  String note = "";
  if (rad != null && rad.trim().length() > 0) {
    rv = @PKG@.ExpDefs.parseNum(rad, -1L);
    if (rv < 1L) return "-The radius is a whole number of blocks, 1 to " + @PKG@.ExpCfg.SPOT_RMAX;
    if (rv > (long) @PKG@.ExpCfg.SPOT_RMAX) { rv = (long) @PKG@.ExpCfg.SPOT_RMAX; note = " (radius capped at spots.maxRadius)"; }
  }
  if (xp0 != null && xp0.trim().length() > 0) {
    xv = @PKG@.ExpDefs.parseNum(xp0, -1L);
    if (xv < 0L) return "-XP is a whole number, 0 to 400,000";
    if (xv > 400000L) { xv = 400000L; note = note + " (XP capped at 400,000)"; }
  }
  if (rv == (long) sp.r && xv == sp.xp) return "=Nothing to save - radius " + sp.r + ", " + @PKG@.ExpDefs.grp(sp.xp) + " XP";
  String r = @PKG@.SpotReg.editSpot(wf, sp.id, 5, null, rv, xv);
  if (r != null) return r;
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "spot edit " + sp.id + " radius " + sp.r + " -> " + rv + " xp " + sp.xp + " -> " + xv);
  return "+" + sp.name + " (" + sp.id + "): radius " + rv + ", " + @PKG@.ExpDefs.grp(xv) + " XP" + note;
}""")
# ---- checklist (spec 4.1)
M(aop, r"""
public static String ckAdded(@PR@ pr, @WLD@ w, String[] res, String what) {
  if (res[0] != null) return res[0];
  String wf = @PKG@.ChestReg.wf(w.getName());
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "check add " + res[1] + " " + what);
  return "+Added checklist entry " + res[1] + " - " + what;
}""")
M(aop, r"""
public static String ckAddChest(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  int[] p = pos(ref, st);
  if (p == null) return "-Could not read your position";
  String wf = @PKG@.ChestReg.wf(w.getName());
  int[] c = @PKG@.ChestReg.nearest(wf, p[0], p[1], p[2], @PKG@.ExpCfg.CHEST_R);
  if (c == null) return "-Stand next to a loot chest (within " + @PKG@.ExpCfg.CHEST_R + " blocks, checklist.chestRadius) - a hand-placed chest counts when an admin made it a loot chest with /stash set <droplist>";
  String r = ckAdded(pr, w, @PKG@.SpotReg.addEntry(w.getName(), wf, 1, c[0] + " " + c[1] + " " + c[2], "Hidden loot chest", c[0], c[1], c[2], 0L), "loot chest at " + c[0] + " " + c[1] + " " + c[2]);
  if (r.startsWith("+") && !@PKG@.ExpCfg.CHESTS_ON) r = r + " (chests.enabled=false: chest opens are not recorded now, so nobody new can complete it)";
  return r;
}""")
M(aop, r"""
public static String ckAddChests(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String num) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  long n = @PKG@.ExpDefs.parseNum(num, -1L);
  if (n < 1L || n > 100000L) return "-Type how many loot chests (1 to 100,000)";
  String wf = @PKG@.ChestReg.wf(w.getName());
  return ckAdded(pr, w, @PKG@.SpotReg.addEntry(w.getName(), wf, 2, String.valueOf(n), "Open " + n + " loot chests on this island", 0, 0, 0, n), "open " + n + " loot chests");
}""")
# arg "" = the region you stand in, "all" = the 13 named regions (existing ones skipped), else a region id
M(aop, r"""
public static String ckAddZone(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String arg) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  String a = arg == null ? "" : arg.trim();
  if (a.equalsIgnoreCase("all")) {
    int added = 0;
    String last = null;
    for (int i = 0; i < @PKG@.ExpDefs.NR; i++) {
      if (!@PKG@.ExpDefs.R_SHOWN[i]) continue;
      String rid = @PKG@.ExpDefs.R_ID[i];
      String[] res = @PKG@.SpotReg.addEntry(wn, wf, 3, rid, @PKG@.ExpDefs.R_NAME[i], 0, 0, 0, 0L);
      if (res[0] == null) { added++; @PKG@.ExpIO.adminLog(pr, wn, "check add " + res[1] + " region " + rid); }
      else if (res[0].indexOf("full") >= 0) { last = res[0]; break; }
    }
    if (added > 0) @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
    return (added > 0 ? "+Added " + added + " region entries" : "=All 13 named regions are already on this checklist") + (last != null ? " - " + textOf(last) : "");
  }
  String rid = a;
  if (rid.length() == 0) {
    try {
      @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
      @ZDI@ zi = p == null || p.getWorldMapTracker() == null ? null : p.getWorldMapTracker().getCurrentZone();
      rid = zi == null ? null : zi.regionName();
    } catch (Throwable t) { rid = null; }
    if (rid == null || rid.length() == 0) return "-Hand-built worlds report no Hytale region - use a big discovery spot instead";
  } else {
    for (int j = 0; j < rid.length(); j++) {
      char c = rid.charAt(j);
      if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "-A region id is letters, digits and _ (for example Zone1_Tier1), or all";
    }
    for (int i = 0; i < @PKG@.ExpDefs.NR; i++) if (@PKG@.ExpDefs.R_ID[i].equalsIgnoreCase(rid)) rid = @PKG@.ExpDefs.R_ID[i];
  }
  boolean known = @PKG@.ExpDefs.region(rid) >= 0;
  String r = ckAdded(pr, w, @PKG@.SpotReg.addEntry(wn, wf, 3, rid, @PKG@.ExpDefs.regionName(rid), 0, 0, 0, 0L), "region " + @PKG@.ExpDefs.regionName(rid) + " (" + rid + ")");
  if (r.startsWith("+") && !known) r = r + " - not one of Hytale's 27 regions: it counts only if the game reports it";
  return r;
}""")
M(aop, r"""
public static String ckAddCustom(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String text) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String t = @PKG@.ExpDefs.clean(text, 80);
  if (t.length() == 0) return "-Type the task text (1 to 80 characters)";
  String wf = @PKG@.ChestReg.wf(w.getName());
  String r = ckAdded(pr, w, @PKG@.SpotReg.addEntry(w.getName(), wf, 4, "", t, 0, 0, 0, 0L), "custom: " + t);
  if (r.startsWith("+")) r = r + " - tick it with /exploreadmin check tick <player> <id>, the admin page or explore:fn:complete";
  return r;
}""")
# a spot token takes that spot off the checklist; digits = an entry of this world. Both need a second call within 10 s (spec 5 table;
# review fix: the spot case confirms too - the Checklist tab's "Take off the checklist" button comes here as well)
M(aop, r"""
public static String ckRemove(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String token) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String t = token == null ? "" : token.trim();
  String wf = @PKG@.ChestReg.wf(w.getName());
  @PKG@.WorldDef wd = @PKG@.SpotReg.byWf(wf);
  if (!@PKG@.ExpDefs.isDigits(t)) {
    String[] err = new String[1];
    @PKG@.SpotDef sp = @PKG@.SpotReg.resolveSpot(wd, t, err);
    if (sp == null) return err[0];
    if (!sp.check) return "=" + sp.name + " (" + sp.id + ") is not on the checklist";
    if (!confirm(pr, "ckoff|" + wf + "|" + sp.id)) return "=Take " + sp.name + " (" + sp.id + ") off the checklist (the spot stays)? Click again (or repeat the command) within 10 s to confirm";
    return spotEdit(pr, ref, st, w, sp.id, "checklist", "no");
  }
  String id = String.valueOf(Long.parseLong(t));
  @PKG@.EntryDef en = @PKG@.SpotReg.entryById(wd, id);
  if (en == null) {
    Object other = @PKG@.SpotReg.ENTRY.get(id);
    return other != null ? "-Entry " + id + " belongs to another world - go there to change it" : "-There is no checklist entry " + id + " (/exploreadmin check list)";
  }
  if (!confirm(pr, "ck|" + wf + "|" + id)) return "=Remove checklist entry " + id + " (" + en.text + ")? Click again (or repeat the command) within 10 s to confirm";
  String r = @PKG@.SpotReg.removeEntry(wf, id);
  if (r != null) return r;
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "check remove " + id + " " + entryKind(en) + " text=" + en.text);
  return "+Removed checklist entry " + id + " (" + en.text + ")";
}""")
M(aop, r"""
public static String ckText(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w, String token, String text) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String t = token == null ? "" : token.trim();
  if (!@PKG@.ExpDefs.isDigits(t)) return "-Use the entry number (/exploreadmin check list); spot names change on the Spots tab or with spot edit";
  String id = String.valueOf(Long.parseLong(t));
  String wf = @PKG@.ChestReg.wf(w.getName());
  @PKG@.EntryDef en = @PKG@.SpotReg.entryById(@PKG@.SpotReg.byWf(wf), id);
  if (en == null) return "-There is no checklist entry " + id + " in this world";
  String nt = @PKG@.ExpDefs.clean(text, 80);
  if (nt.length() == 0) return "-Type the new text (1 to 80 characters)";
  if (nt.equals(en.text)) return "=Entry " + id + " already says that";
  String r = @PKG@.SpotReg.textEntry(wf, id, nt);
  if (r != null) return r;
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, w.getName(), "check text " + id + " " + en.text + " -> " + nt);
  return "+Entry " + id + " now says: " + nt;
}""")
# tick / untick a CUSTOM entry (any world) for a player's ACTIVE profile (spec 5)
M(aop, r"""
public static String ckTick(@PR@ pr, @PR@ target, String token, boolean v) {
  if (!perm(pr)) return "-You are not an admin (skyyexploration.admin)";
  if (target == null) return "-That player is not online (type their exact name)";
  String t = token == null ? "" : token.trim();
  if (!@PKG@.ExpDefs.isDigits(t)) return "-Use the number of a custom entry (/exploreadmin check list)";
  String id = String.valueOf(Long.parseLong(t));
  Object wf = @PKG@.SpotReg.ENTRY.get(id);
  @PKG@.WorldDef wd = wf instanceof String ? @PKG@.SpotReg.byWf((String) wf) : null;
  @PKG@.EntryDef en = @PKG@.SpotReg.entryById(wd, id);
  if (en == null) return "-There is no checklist entry " + id;
  if (en.type != 4) return "-Entry " + id + " is a " + entryKind(en) + " entry - only custom entries are ticked by hand (the others come from real play)";
  String k = @PKG@.ExpIO.pkey(target.getUuid());
  if (!@PKG@.ExpStore.complete(k, id, v)) return "-" + target.getUsername() + "'s exploration file could not be read - nothing changed";
  @PKG@.ExpIO.adminLog(pr, wd.world, "check " + (v ? "tick " : "untick ") + id + " player=" + target.getUsername() + " profile=" + k);
  return "+" + (v ? "Ticked" : "Unticked") + " entry " + id + " (" + en.text + ") for " + target.getUsername() + " (profile " + k + ")";
}""")
M(aop, r"""
public static String ckList(@PR@ pr, @REF@ ref, @ST@ st, @WLD@ w) {
  String e = pre(pr, w, false);
  if (e != null) return e;
  @PKG@.WorldDef wd = @PKG@.SpotReg.byName(w.getName());
  if (wd == null || wd.checks == 0) return "=This world has no checklist entries yet - /exploreadmin opens the admin page (Checklist tab)";
  java.util.ArrayList on = onlineIn(w);
  StringBuilder sb = new StringBuilder();
  sb.append("=").append(wd.name).append(" checklist - ").append(wd.checks).append(" entries - checklist ").append(wd.checklist ? "ON" : "OFF").append(@PKG@.ExpCfg.CHECK_ON ? "" : " (checklist.enabled=false on this server)");
  int n = 0;
  for (int i = 0; i < wd.spots.length && n < 40; i++) {
    @PKG@.SpotDef s = wd.spots[i];
    if (!s.check) continue;
    int[] fb = foundBy(wd, s.id, on);
    sb.append('\n').append(s.id).append(" - ").append(s.secret ? "secret spot " : "spot ").append(s.name).append(" (").append(fb[0]).append(" of ").append(fb[1]).append(" online players have it)");
    n++;
  }
  for (int i = 0; i < wd.entries.length && n < 40; i++) {
    @PKG@.EntryDef en = wd.entries[i];
    sb.append('\n').append(en.id).append(" - ").append(entryKind(en)).append(" - ").append(en.text).append(" (").append(haveEntry(wd, en, on)).append(" online players have it)");
    n++;
  }
  if (wd.checks > n) sb.append("\n... and ").append(wd.checks - n).append(" more (the admin page lists all)");
  return sb.toString();
}""")
# ---- island values (spec 5 / 6.3)
M(aop, r"""
public static String islandShow(@PR@ pr, @WLD@ w) {
  String e = pre(pr, w, false);
  if (e != null) return e;
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef wd = @PKG@.SpotReg.byWf(wf);
  if (wd == null) wd = @PKG@.SpotReg.blank(wn, wf);
  return "=" + wd.name + " (world " + wn + ", file " + @PKG@.SpotReg.fileName(wf) + ")\nchecklist " + (wd.checklist ? "ON" : "OFF") + " - " + wd.checks + " entries - " + wd.spots.length + " spots (" + wd.secrets + " secret)"
    + "\nreward at 100%: " + @PKG@.ExpDefs.grp(wd.rewardXp) + " XP, " + @PKG@.ExpDefs.grp(wd.rewardCoins) + " coins" + (@PKG@.ExpIO.fn("coins:fn:add") == null ? " (coins need SkyyCoins)" : "")
    + "\nnew spot XP here: " + (wd.spotXp < 0L ? "config (" + @PKG@.ExpCfg.SPOT_XP + ")" : String.valueOf(wd.spotXp)) + ", secret " + (wd.secretXp < 0L ? "config (" + @PKG@.ExpCfg.SECRET_XP + ")" : String.valueOf(wd.secretXp))
    + "\n/exploreadmin island name <text> | checklist <on|off> | reward <xp> <coins> | defaults <spotXp> <secretXp>";
}""")
M(aop, r"""
public static String islandName(@PR@ pr, @WLD@ w, String text) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String t = @PKG@.ExpDefs.clean(text, 80);
  if (t.length() == 0) return "-Type the island name (1 to 80 characters)";
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef cur = @PKG@.SpotReg.byWf(wf);
  String old = cur == null ? wn : cur.name;
  if (t.equals(old)) return "=The island is already called " + t;
  @PKG@.SpotReg.setIsland(wn, wf, 0, t, 0L, 0L);
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, wn, "island name " + old + " -> " + t);
  return "+This island is now called " + t;
}""")
M(aop, r"""
public static String islandCheck(@PR@ pr, @WLD@ w, String onoff) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  int b = yesNo(onoff);
  if (b < 0) return "-Type on or off";
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef cur = @PKG@.SpotReg.byWf(wf);
  boolean old = cur == null || cur.checklist;
  if (old == (b == 1)) return "=The checklist of this world is already " + (old ? "ON" : "OFF");
  @PKG@.SpotReg.setIsland(wn, wf, 1, null, (long) b, 0L);
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, wn, "island checklist " + (old ? "on" : "off") + " -> " + (b == 1 ? "on" : "off"));
  return "+The checklist of this world is now " + (b == 1 ? "ON" : "OFF");
}""")
M(aop, r"""
public static String islandReward(@PR@ pr, @WLD@ w, String xp0, String co0) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef cur = @PKG@.SpotReg.byWf(wf);
  long ox = cur == null ? 0L : cur.rewardXp;
  long oc = cur == null ? 0L : cur.rewardCoins;
  long x = xp0 == null || xp0.trim().length() == 0 ? ox : @PKG@.ExpDefs.parseNum(xp0, -1L);
  long c = co0 == null || co0.trim().length() == 0 ? oc : @PKG@.ExpDefs.parseNum(co0, -1L);
  if (x < 0L || x > 400000L) return "-The XP reward is 0 to 400,000";
  if (c < 0L || c > 1000000000L) return "-The coin reward is 0 to 1,000,000,000";
  if (x == ox && c == oc) return "=The reward is already " + @PKG@.ExpDefs.grp(x) + " XP, " + @PKG@.ExpDefs.grp(c) + " coins";
  @PKG@.SpotReg.setIsland(wn, wf, 2, null, x, c);
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, wn, "island reward xp " + ox + " -> " + x + " coins " + oc + " -> " + c);
  return "+Reward at 100%: " + @PKG@.ExpDefs.grp(x) + " Exploration XP, " + @PKG@.ExpDefs.grp(c) + " coins" + (c > 0L && @PKG@.ExpIO.fn("coins:fn:add") == null ? " (coins need SkyyCoins - not installed now)" : "") + " - paid once per profile";
}""")
M(aop, r"""
public static String islandDefaults(@PR@ pr, @WLD@ w, String sp0, String se0) {
  String e = pre(pr, w, true);
  if (e != null) return e;
  String wn = w.getName();
  String wf = @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef cur = @PKG@.SpotReg.byWf(wf);
  long os = cur == null ? -1L : cur.spotXp;
  long oe = cur == null ? -1L : cur.secretXp;
  String a = sp0 == null ? "" : sp0.trim();
  String b = se0 == null ? "" : se0.trim();
  long s = a.length() == 0 || a.equals("-1") ? -1L : @PKG@.ExpDefs.parseNum(a, -2L);
  long c = b.length() == 0 || b.equals("-1") ? -1L : @PKG@.ExpDefs.parseNum(b, -2L);
  if (s < -1L || s > 400000L || c < -1L || c > 400000L) return "-New-spot XP is 0 to 400,000, or blank / -1 = the config value";
  if (s == os && c == oe) return "=Nothing changed";
  @PKG@.SpotReg.setIsland(wn, wf, 3, null, s, c);
  @PKG@.SpotReg.saveSoon(wf, pr.getUuid());
  @PKG@.ExpIO.adminLog(pr, wn, "island defaults spotXp " + os + " -> " + s + " secretXp " + oe + " -> " + c);
  return "+New spots here get " + (s < 0L ? "the config XP (" + @PKG@.ExpCfg.SPOT_XP + ")" : @PKG@.ExpDefs.grp(s) + " XP") + ", new secrets " + (c < 0L ? "the config XP (" + @PKG@.ExpCfg.SECRET_XP + ")" : @PKG@.ExpDefs.grp(c) + " XP");
}""")
# ---- config (spec 5 set / get): every key, the file always matches
M(aop, r"""
public static String setKey(@PR@ pr, String key, String value) {
  if (!perm(pr)) return "-You are not an admin (skyyexploration.admin)";
  String[] r = @PKG@.ExpCfg.setKey(key, value);
  if (r[0].startsWith("+")) @PKG@.ExpIO.adminLog(pr, "-", "set " + key.trim() + " " + (r[1] == null ? "(not in file)" : r[1]) + " -> " + r[2]);
  return r[0];
}""")
M(aop, r"""
public static String getKey(@PR@ pr, String key) {
  if (!perm(pr)) return "-You are not an admin (skyyexploration.admin)";
  String k = key == null ? "" : key.trim();
  if (@PKG@.ExpCfg.keyType(k) == null) return "-Unknown key '" + k + "' - the keys are the lines of config.properties";
  String fv = @PKG@.ExpCfg.fileValue(k);
  String lv = @PKG@.ExpCfg.live(k);
  return "=" + k + " = " + (fv == null ? "(not in the file - default " + lv + ")" : fv + (lv != null && !lv.equals(fv) ? " (the server uses " + lv + ")" : ""));
}""")
M(aop, r"""
public static String reload(@PR@ pr) {
  if (!perm(pr)) return "-You are not an admin (skyyexploration.admin)";
  try { @PKG@.SpotReg.flushDirty(); } catch (Throwable t) { }
  String c = @PKG@.ExpCfg.load();
  int bad = @PKG@.ExpStore.dropBad();
  String ws = @PKG@.SpotReg.loadAll();
  @PKG@.ExpIO.adminLog(pr, "-", "reload");
  return "+config reloaded: " + c + (bad > 0 ? "; " + bad + " unreadable player file(s) will be read again" : "") + "; " + ws + " (titles.chatPriority needs a restart)";
}""")
M(aop, r"""
public static String stats() {
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = @PKG@.SpotReg.W.values().iterator();
  int n = 0;
  sb.append("=Spots and checklists: ").append(@PKG@.SpotReg.summary()).append(" - spots ").append(@PKG@.ExpCfg.SPOTS_ON ? "on" : "OFF").append(", checklists ").append(@PKG@.ExpCfg.CHECK_ON ? "on" : "OFF");
  while (it.hasNext() && n < 12) {
    @PKG@.WorldDef w = (@PKG@.WorldDef) it.next();
    Object b = @PKG@.SpotReg.BAD.get(w.wf);
    String fs = (b != null ? "BAD (" + (String) b + ")" : (@PKG@.SpotReg.edited(w.wf) ? "EDITED BY HAND (reload)" : (@PKG@.SpotReg.DIRTY.containsKey(w.wf) ? "saving" : "ok"))) + @PKG@.SpotReg.unsaved(w.wf);
    sb.append('\n').append(w.world).append(" (").append(w.name).append("): ").append(w.spots.length).append(" spots (").append(w.secrets).append(" secret), ").append(w.checks).append(" checklist entries, file ").append(fs);
    n++;
  }
  long[] l = @PKG@.SpotReg.LAST10;
  String avg = l[1] > 0L ? @PKG@.ExpDefs.num((double) l[2] / (double) l[1] / 1000.0) : "-";
  sb.append("\nspot checks: ").append(l[0]).append(" in the last 10 s, ").append(avg).append(" us each (1 in 16 timed) - ").append(@PKG@.SpotReg.CHECKS.get()).append(" since start");
  return sb.toString();
}""")
M(aop, r"""
public static String help() {
  return "=/exploreadmin - the admin page (Spots | Checklist | Island)"
    + "\n/exploreadmin reload | stats | resetme | help"
    + "\n/exploreadmin set <key> <value> | get <key> - any config.properties key (the file is rewritten)"
    + "\n/exploreadmin spot add <name> [radius] [xp] [secret|open] - where you stand (_ = space in names)"
    + "\n/exploreadmin spot move|remove|tp <spot> - spot = id (s3) or name / 3+ letters; remove twice to confirm"
    + "\n/exploreadmin spot list | spot edit <spot> <name|radius|xp|secret|checklist> <value>"
    + "\n/exploreadmin check list | check add chest | check add chests <n> | check add zone [region|all] | check add custom <text>"
    + "\n/exploreadmin check remove <id|spot> (twice; a spot stays, it only leaves the checklist) | check text <id> <text> | check tick|untick <player> <id>"
    + "\n/exploreadmin island | island name <text> | island checklist <on|off> | island reward <xp> <coins> | island defaults <spotXp> <secretXp>";
}""")

# ================= 0.2 AdminPage: /exploreadmin (spec 6; inline, 1120 x 900, Spots | Checklist | Island; list left, editor right).
# No periodic updates, no timers, no hover handlers: rebuilt only after a click, at most once a second; the permission is re-checked
# on every click; the only close is after a teleport. Text boxes = the verified SkyyGuilds / SkyySacks TextField pattern. =================
for f in ("public int tab;", "public int page;", "public int sort;", "public String selSpot;", "public String selEntry;",
          "public boolean newSecret;", "public String msg;", "public long lastBuild;", "public String[] rowIds;",
          "public String kNName;", "public String kNRad;", "public String kNXp;", "public String kEName;", "public String kERad;",
          "public String kEXp;", "public String kCText;", "public String kCNum;", "public String kCEText;", "public String kCPlayer;",
          "public String kIName;", "public String kIRwXp;", "public String kIRwCo;", "public String kIDefSp;", "public String kIDefSe;"):
    F(apg, f)
F(apg, 'public static final String SG = "@XG@";')
F(apg, 'public static final String SOFF = "@XOFF@";')
F(apg, 'public static final String SON = "@XON@";')
F(apg, 'public static final String SRED = "@XRED@";')
F(apg, 'public static final String SBLU = "@XBLU@";')
C(apg, r"""
public AdminPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab; this.page = 0; this.sort = 0; this.selSpot = null; this.selEntry = null; this.newSecret = false; this.msg = "";
  this.lastBuild = 0L; this.rowIds = new String[8];
}""")
M(apg, r"""
public void clearKeeps() {
  this.kNName = null; this.kNRad = null; this.kNXp = null; this.kEName = null; this.kERad = null; this.kEXp = null;
  this.kCText = null; this.kCNum = null; this.kCEText = null; this.kCPlayer = null;
  this.kIName = null; this.kIRwXp = null; this.kIRwCo = null; this.kIDefSp = null; this.kIDefSe = null;
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr / SkyyGuilds 0.1.1, verified in game)
M(apg, r"""
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
M(apg, r"""
public static void gap(@UCB@ b, String par, int w, int h) {
  b.appendInline(par, "Label { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; }");
}""")
M(apg, r"""
public static void vgap(@UCB@ b, String par, int h) {
  b.appendInline(par, "Label { Anchor: (Height: " + h + "); Text: \"\"; }");
}""")
# a label whose text only ever reaches the client through b.set (any character is safe); align 0 start, 1 centre, 2 end
M(apg, r"""
public static void lab(@UCB@ b, String par, String id, String text, int w, int h, int size, boolean bold, String color, int align) {
  String an = w > 0 ? "Anchor: (Width: " + w + ", Height: " + h + ");" : "Anchor: (Height: " + h + ");";
  String al = align == 1 ? " HorizontalAlignment: Center," : (align == 2 ? " HorizontalAlignment: End," : "");
  b.appendInline(par, "Label #" + id + " { " + an + " Text: \"\"; Style: (FontSize: " + size + "," + (bold ? " RenderBold: true," : "") + " TextColor: " + color + "," + al + " VerticalAlignment: Center, Wrap: true); }");
  b.set("#" + id + ".Text", text == null ? "" : text);
}""")
# placeholders are plain words / digits only (they sit in the markup)
M(apg, r"""
public static String ph(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 30; i++) {
    char c = s.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == ' ' || c == '-' || c == '.') sb.append(c);
  }
  return sb.toString();
}""")
M(apg, r"""
public static void box(@UCB@ b, String par, String id, int w, int max, String placeholder, String val) {
  b.appendInline(par, "Group #" + id + "Box { Anchor: (Width: " + w + ", Height: 44); Background: #16263a; }");
  b.appendInline("#" + id + "Box", "TextField #" + id + " { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: " + max + "; PlaceholderText: \"" + ph(placeholder) + "\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
  if (val != null && val.length() > 0) b.set("#" + id + ".Value", val);
}""")
# label = a Java literal at every call site (button labels never carry dynamic text)
M(apg, r"""
public static void btn(@UCB@ b, @UEB@ ev, String par, String id, String label, String style, int w, @EVD@ data) {
  b.appendInline(par, "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: 44); Text: \"" + label + "\"; " + style + " }");
  ev.addEventBinding(@BT@.Activating, "#" + id, data);
}""")
M(apg, r"""
public static void row(@UCB@ b, String par, String id) {
  b.appendInline(par, "Group #" + id + " { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); }");
}""")
M(apg, r"""
public static void sep(@UCB@ b, String par) {
  b.appendInline(par, "Group { Anchor: (Height: 2); Background: #2c4258; }");
  b.appendInline(par, "Label { Anchor: (Height: 8); Text: \"\"; }");
}""")
# EventData.append is chainable (vanilla LaunchPad$LaunchPadSettingsPage sends four box values with one Save click)
M(apg, r"""
public static @EVD@ ev3(String a, String k1, String id1, String k2, String id2, String k3, String id3) {
  @EVD@ e = @EVD@.of("a", a);
  if (k1 != null) e = e.append(k1, id1);
  if (k2 != null) e = e.append(k2, id2);
  if (k3 != null) e = e.append(k3, id3);
  return e;
}""")
M(apg, r"""
public void pager(@UCB@ b, @UEB@ ev, boolean withSort) {
  b.appendInline("#SkyyXaList", "Group #SkyyXaPager { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); }");
  btn(b, ev, "#SkyyXaPager", "SkyyXaPrev", "< Prev", SOFF, 140, @EVD@.of("a", "xprev"));
  gap(b, "#SkyyXaPager", 10, 44);
  btn(b, ev, "#SkyyXaPager", "SkyyXaNext", "Next >", SOFF, 140, @EVD@.of("a", "xnext"));
  if (withSort) {
    gap(b, "#SkyyXaPager", 10, 44);
    if (this.sort == 1) btn(b, ev, "#SkyyXaPager", "SkyyXaSort", "Order - nearest", SOFF, 180, @EVD@.of("a", "xsort"));
    else btn(b, ev, "#SkyyXaPager", "SkyyXaSort", "Order - newest", SOFF, 180, @EVD@.of("a", "xsort"));
  }
}""")
M(apg, r"""
public void lists(@UCB@ b) {
  b.appendInline("#SkyyXaBody", "Group #SkyyXaList { Anchor: (Width: 600, Height: 690); LayoutMode: Top; }");
  gap(b, "#SkyyXaBody", 20, 10);
  b.appendInline("#SkyyXaBody", "Group #SkyyXaDet { Anchor: (Width: 460, Height: 690); LayoutMode: Top; }");
}""")
M(apg, r"""
public void spotsTab(@UCB@ b, @UEB@ ev, java.util.UUID u, @WLD@ w, String wf, @PKG@.WorldDef wd, int[] p) {
  lists(b);
  @PKG@.SpotDef[] sp = wd == null ? new @PKG@.SpotDef[0] : wd.spots;
  int n = sp.length;
  int[] ord = new int[n];
  double[] dist = new double[n];
  for (int i = 0; i < n; i++) {
    ord[i] = this.sort == 1 ? i : n - 1 - i;
    @PKG@.SpotDef s = sp[i];
    dist[i] = p == null ? 0.0 : Math.sqrt((double) ((long) (s.x - p[0]) * (s.x - p[0]) + (long) (s.y - p[1]) * (s.y - p[1]) + (long) (s.z - p[2]) * (s.z - p[2])));
  }
  if (this.sort == 1) {
    for (int i = 1; i < n; i++) {
      int v = ord[i];
      int j = i - 1;
      while (j >= 0 && dist[ord[j]] > dist[v]) { ord[j + 1] = ord[j]; j--; }
      ord[j + 1] = v;
    }
  }
  int pages = (n + 7) / 8;
  if (pages < 1) pages = 1;
  if (this.page >= pages) this.page = pages - 1;
  if (this.page < 0) this.page = 0;
  lab(b, "#SkyyXaList", "SkyyXaLHead", "Spots in this world - " + n + " (" + (wd == null ? 0 : wd.secrets) + " secret) - page " + (this.page + 1) + " of " + pages, 0, 32, 18, true, "#e6eef6", 0);
  this.rowIds = new String[8];
  java.util.ArrayList on = @PKG@.ExAdminOps.onlineIn(w);
  for (int i = 0; i < 8; i++) {
    int at = this.page * 8 + i;
    if (at >= n) break;
    @PKG@.SpotDef s = sp[ord[at]];
    this.rowIds[i] = s.id;
    boolean sel = s.id.equals(this.selSpot);
    boolean dup = @PKG@.SpotReg.nameTaken(wd, s.name, s.id);
    b.appendInline("#SkyyXaList", "Group #SkyyXaRow" + i + " { Anchor: (Height: 66); LayoutMode: Left; Background: " + (sel ? "#24405c" : "#142030") + "; Padding: (Left: 10); }");
    b.appendInline("#SkyyXaRow" + i, "Group #SkyyXaRowT" + i + " { Anchor: (Width: 460, Height: 66); LayoutMode: Top; }");
    lab(b, "#SkyyXaRowT" + i, "SkyyXaRowN" + i, s.name, 0, 34, 18, true, s.secret ? "#d890ff" : "#ffb070", 0);
    lab(b, "#SkyyXaRowT" + i, "SkyyXaRowS" + i, s.id + " - " + (s.secret ? "secret" : "discovery") + " - r " + s.r + " - " + @PKG@.ExpDefs.grp(s.xp) + " XP - " + (long) dist[ord[at]] + " m away" + (s.check ? " - on checklist" : "") + (dup ? " - SAME NAME TWICE" : ""), 0, 28, 14, false, dup ? "#ff9a70" : "#c8d6e4", 0);
    gap(b, "#SkyyXaRow" + i, 10, 48);
    if (sel) lab(b, "#SkyyXaRow" + i, "SkyyXaRowE" + i, "Editing", 110, 48, 15, true, "#9adf86", 1);
    else btn(b, ev, "#SkyyXaRow" + i, "SkyyXaEdit" + i, "Edit", SBLU, 110, @EVD@.of("a", "xedit" + i));
    vgap(b, "#SkyyXaList", 4);
  }
  if (n == 0) lab(b, "#SkyyXaList", "SkyyXaEmpty", "No spots in this world yet. Type a name on the right and click Add here - the spot is placed where you stand.", 0, 70, 16, false, "#9fb8cc", 0);
  pager(b, ev, true);
  long dx = @PKG@.ExAdminOps.defaultXp(wd, false);
  long ds = @PKG@.ExAdminOps.defaultXp(wd, true);
  lab(b, "#SkyyXaDet", "SkyyXaNewH", "New spot where you stand", 0, 30, 20, true, "#e6eef6", 0);
  row(b, "#SkyyXaDet", "SkyyXaNR1");
  lab(b, "#SkyyXaNR1", "SkyyXaNL1", "Name", 90, 44, 16, true, "#c8d6e4", 0);
  box(b, "#SkyyXaNR1", "SkyyXaNName", 350, 40, "Spot name", this.kNName);
  row(b, "#SkyyXaDet", "SkyyXaNR2");
  lab(b, "#SkyyXaNR2", "SkyyXaNL2", "Radius", 90, 44, 16, true, "#c8d6e4", 0);
  box(b, "#SkyyXaNR2", "SkyyXaNRad", 100, 3, String.valueOf(@PKG@.ExpCfg.SPOT_R), this.kNRad);
  gap(b, "#SkyyXaNR2", 10, 44);
  lab(b, "#SkyyXaNR2", "SkyyXaNL3", "XP", 60, 44, 16, true, "#c8d6e4", 0);
  box(b, "#SkyyXaNR2", "SkyyXaNXp", 140, 6, String.valueOf(this.newSecret ? ds : dx), this.kNXp);
  row(b, "#SkyyXaDet", "SkyyXaNR3");
  @EVD@ keepN = ev3("xnsec", "@XNName", "#SkyyXaNName.Value", "@XNRad", "#SkyyXaNRad.Value", "@XNXp", "#SkyyXaNXp.Value");
  if (this.newSecret) btn(b, ev, "#SkyyXaNR3", "SkyyXaNSec", "Secret - Yes", SON, 200, keepN);
  else btn(b, ev, "#SkyyXaNR3", "SkyyXaNSec", "Secret - No", SOFF, 200, keepN);
  gap(b, "#SkyyXaNR3", 10, 44);
  btn(b, ev, "#SkyyXaNR3", "SkyyXaAdd", "Add here", SG, 230, ev3("xadd", "@XNName", "#SkyyXaNName.Value", "@XNRad", "#SkyyXaNRad.Value", "@XNXp", "#SkyyXaNXp.Value"));
  lab(b, "#SkyyXaDet", "SkyyXaNHint", "Blank radius / XP = " + @PKG@.ExpCfg.SPOT_R + " / " + @PKG@.ExpDefs.grp(dx) + " (secret " + @PKG@.ExpDefs.grp(ds) + "). Admins in adventure mode discover spots too - build in creative, or use /exploreadmin resetme.", 0, 40, 14, false, "#9fb8cc", 0);
  sep(b, "#SkyyXaDet");
  @PKG@.SpotDef cur = @PKG@.SpotReg.spotById(wd, this.selSpot);
  if (cur == null) {
    lab(b, "#SkyyXaDet", "SkyyXaSelH", "Click Edit on a spot", 0, 30, 20, true, "#e6eef6", 0);
    lab(b, "#SkyyXaDet", "SkyyXaSelT", "Then rename it, change its radius or XP, make it secret, take it off the checklist, move it to where you stand, teleport to it or remove it.", 0, 60, 14, false, "#9fb8cc", 0);
    return;
  }
  lab(b, "#SkyyXaDet", "SkyyXaSelH", "Selected: " + cur.name + " (" + cur.id + ")", 0, 30, 20, true, cur.secret ? "#d890ff" : "#ffb070", 0);
  @EVD@ keepE1 = ev3("xesec", "@XEName", "#SkyyXaEName.Value", "@XERad", "#SkyyXaERad.Value", "@XEXp", "#SkyyXaEXp.Value");
  @EVD@ keepE2 = ev3("xechk", "@XEName", "#SkyyXaEName.Value", "@XERad", "#SkyyXaERad.Value", "@XEXp", "#SkyyXaEXp.Value");
  row(b, "#SkyyXaDet", "SkyyXaER1");
  box(b, "#SkyyXaER1", "SkyyXaEName", 300, 40, "Spot name", this.kEName != null ? this.kEName : cur.name);
  gap(b, "#SkyyXaER1", 10, 44);
  btn(b, ev, "#SkyyXaER1", "SkyyXaRen", "Rename", SG, 140, ev3("xren", "@XEName", "#SkyyXaEName.Value", null, null, null, null));
  row(b, "#SkyyXaDet", "SkyyXaER2");
  box(b, "#SkyyXaER2", "SkyyXaERad", 90, 3, "radius", this.kERad != null ? this.kERad : String.valueOf(cur.r));
  gap(b, "#SkyyXaER2", 10, 44);
  box(b, "#SkyyXaER2", "SkyyXaEXp", 130, 6, "XP", this.kEXp != null ? this.kEXp : String.valueOf(cur.xp));
  gap(b, "#SkyyXaER2", 10, 44);
  btn(b, ev, "#SkyyXaER2", "SkyyXaSave", "Save radius and XP", SG, 200, ev3("xsave", "@XERad", "#SkyyXaERad.Value", "@XEXp", "#SkyyXaEXp.Value", null, null));
  row(b, "#SkyyXaDet", "SkyyXaER3");
  if (cur.secret) btn(b, ev, "#SkyyXaER3", "SkyyXaESec", "Secret - Yes", SON, 220, keepE1);
  else btn(b, ev, "#SkyyXaER3", "SkyyXaESec", "Secret - No", SOFF, 220, keepE1);
  gap(b, "#SkyyXaER3", 10, 44);
  if (cur.check) btn(b, ev, "#SkyyXaER3", "SkyyXaEChk", "On checklist - Yes", SON, 220, keepE2);
  else btn(b, ev, "#SkyyXaER3", "SkyyXaEChk", "On checklist - No", SOFF, 220, keepE2);
  row(b, "#SkyyXaDet", "SkyyXaER4");
  btn(b, ev, "#SkyyXaER4", "SkyyXaMove", "Move here", SBLU, 140, @EVD@.of("a", "xmove"));
  gap(b, "#SkyyXaER4", 10, 44);
  btn(b, ev, "#SkyyXaER4", "SkyyXaTp", "Teleport", SBLU, 140, @EVD@.of("a", "xtp"));
  gap(b, "#SkyyXaER4", 10, 44);
  if (@PKG@.ExAdminOps.pending(u, "rm|" + wf + "|" + cur.id)) btn(b, ev, "#SkyyXaER4", "SkyyXaRm", "Sure - Remove", SRED, 140, @EVD@.of("a", "xrm"));
  else btn(b, ev, "#SkyyXaER4", "SkyyXaRm", "Remove", SRED, 140, @EVD@.of("a", "xrm"));
  int[] fb = @PKG@.ExAdminOps.foundBy(wd, cur.id, on);
  lab(b, "#SkyyXaDet", "SkyyXaEInfo", "at " + cur.x + " " + cur.y + " " + cur.z + " - found by " + fb[0] + " of " + fb[1] + " online players here", 0, 30, 14, false, "#9fb8cc", 0);
}""")
M(apg, r"""
public void checkTab(@UCB@ b, @UEB@ ev, java.util.UUID u, @WLD@ w, String wf, @PKG@.WorldDef wd, int[] p) {
  lists(b);
  java.util.ArrayList rows = new java.util.ArrayList();
  int spotRows = 0;
  if (wd != null) {
    for (int i = 0; i < wd.spots.length; i++) if (wd.spots[i].check) { rows.add(wd.spots[i]); spotRows++; }
    for (int i = 0; i < wd.entries.length; i++) rows.add(wd.entries[i]);
  }
  int n = rows.size();
  int pages = (n + 7) / 8;
  if (pages < 1) pages = 1;
  if (this.page >= pages) this.page = pages - 1;
  if (this.page < 0) this.page = 0;
  boolean on1 = (wd == null || wd.checklist) && @PKG@.ExpCfg.CHECK_ON;
  lab(b, "#SkyyXaList", "SkyyXaLHead", "Checklist - " + n + " entries (" + spotRows + " spots) - checklist " + ((wd == null || wd.checklist) ? "ON" : "OFF") + (@PKG@.ExpCfg.CHECK_ON ? "" : " - checklist.enabled=false") + " - page " + (this.page + 1) + " of " + pages, 0, 32, 18, true, on1 ? "#e6eef6" : "#ff9a70", 0);
  this.rowIds = new String[8];
  java.util.ArrayList on = @PKG@.ExAdminOps.onlineIn(w);
  for (int i = 0; i < 8; i++) {
    int at = this.page * 8 + i;
    if (at >= n) break;
    Object o = rows.get(at);
    String id = "";
    String name = "";
    String status = "";
    String col = "#9fd0ff";
    String scol = "#c8d6e4";
    if (o instanceof @PKG@.SpotDef) {
      @PKG@.SpotDef s = (@PKG@.SpotDef) o;
      int[] fb = @PKG@.ExAdminOps.foundBy(wd, s.id, on);
      id = s.id; name = s.name; col = s.secret ? "#d890ff" : "#ffb070";
      status = s.id + " - " + (s.secret ? "secret spot" : "spot") + " (edit it on the Spots tab) - " + fb[0] + " of " + fb[1] + " online have it";
    } else {
      @PKG@.EntryDef e = (@PKG@.EntryDef) o;
      id = e.id; name = e.text;
      boolean gone = e.type == 1 && @PKG@.ChestReg.get(wf, e.x, e.y, e.z) == null;
      status = e.id + " - " + @PKG@.ExAdminOps.entryKind(e) + " - " + @PKG@.ExAdminOps.haveEntry(wd, e, on) + " online players have it" + (gone ? " - chest gone (remove this entry?)" : "");
      if (gone) scol = "#ff9a70";
    }
    this.rowIds[i] = id;
    boolean sel = id.equals(this.selEntry);
    b.appendInline("#SkyyXaList", "Group #SkyyXaCRow" + i + " { Anchor: (Height: 66); LayoutMode: Left; Background: " + (sel ? "#24405c" : "#142030") + "; Padding: (Left: 10); }");
    b.appendInline("#SkyyXaCRow" + i, "Group #SkyyXaCRowT" + i + " { Anchor: (Width: 460, Height: 66); LayoutMode: Top; }");
    lab(b, "#SkyyXaCRowT" + i, "SkyyXaCRowN" + i, name, 0, 34, 18, true, col, 0);
    lab(b, "#SkyyXaCRowT" + i, "SkyyXaCRowS" + i, status, 0, 28, 14, false, scol, 0);
    gap(b, "#SkyyXaCRow" + i, 10, 48);
    if (sel) lab(b, "#SkyyXaCRow" + i, "SkyyXaCRowE" + i, "Editing", 110, 48, 15, true, "#9adf86", 1);
    else btn(b, ev, "#SkyyXaCRow" + i, "SkyyXaCEdit" + i, "Edit", SBLU, 110, @EVD@.of("a", "xcedit" + i));
    vgap(b, "#SkyyXaList", 4);
  }
  if (n == 0) lab(b, "#SkyyXaList", "SkyyXaEmpty", "No checklist entries in this world yet. Spots are added automatically; add loot chests, regions, chest counts or custom tasks on the right.", 0, 70, 16, false, "#9fb8cc", 0);
  pager(b, ev, false);
  lab(b, "#SkyyXaDet", "SkyyXaCAddH", "Add to the checklist", 0, 30, 20, true, "#e6eef6", 0);
  row(b, "#SkyyXaDet", "SkyyXaCR1");
  btn(b, ev, "#SkyyXaCR1", "SkyyXaCAddChest", "Add loot chest here", SG, 440, @EVD@.of("a", "xcchest"));
  row(b, "#SkyyXaDet", "SkyyXaCR2");
  btn(b, ev, "#SkyyXaCR2", "SkyyXaCAddZone", "Add region here", SG, 215, @EVD@.of("a", "xczone"));
  gap(b, "#SkyyXaCR2", 10, 44);
  btn(b, ev, "#SkyyXaCR2", "SkyyXaCAddAll", "Add all 13 regions", SG, 215, @EVD@.of("a", "xczall"));
  row(b, "#SkyyXaDet", "SkyyXaCR3");
  box(b, "#SkyyXaCR3", "SkyyXaCText", 290, 80, "Task text", this.kCText);
  gap(b, "#SkyyXaCR3", 10, 44);
  btn(b, ev, "#SkyyXaCR3", "SkyyXaCAddCustom", "Add custom", SG, 140, ev3("xccustom", "@XCText", "#SkyyXaCText.Value", null, null, null, null));
  row(b, "#SkyyXaDet", "SkyyXaCR4");
  box(b, "#SkyyXaCR4", "SkyyXaCNum", 210, 6, "10", this.kCNum);
  gap(b, "#SkyyXaCR4", 10, 44);
  btn(b, ev, "#SkyyXaCR4", "SkyyXaCAddCount", "Add open-N-chests", SG, 220, ev3("xccount", "@XCNum", "#SkyyXaCNum.Value", null, null, null, null));
  lab(b, "#SkyyXaDet", "SkyyXaCHint", @PKG@.ExpCfg.CHESTS_ON ? "Add loot chest here takes the nearest recorded loot chest within " + @PKG@.ExpCfg.CHEST_R + " blocks." : "chests.enabled=false - chest entries cannot complete while chest opens are off.", 0, 26, 14, false, @PKG@.ExpCfg.CHESTS_ON ? "#9fb8cc" : "#ff9a70", 0);
  sep(b, "#SkyyXaDet");
  String sel = this.selEntry;
  @PKG@.SpotDef cs = sel != null && sel.startsWith("s") ? @PKG@.SpotReg.spotById(wd, sel) : null;
  @PKG@.EntryDef ce = sel != null && !sel.startsWith("s") ? @PKG@.SpotReg.entryById(wd, sel) : null;
  if (cs != null && !cs.check) cs = null;
  if (cs != null) {
    lab(b, "#SkyyXaDet", "SkyyXaCSelH", "Selected: " + cs.name + " (" + cs.id + ") - spot", 0, 30, 20, true, cs.secret ? "#d890ff" : "#ffb070", 0);
    lab(b, "#SkyyXaDet", "SkyyXaCSelT", "This is a spot - edit it on the Spots tab. Taking it off the checklist keeps the spot.", 0, 44, 14, false, "#9fb8cc", 0);
    row(b, "#SkyyXaDet", "SkyyXaCR5");
    if (@PKG@.ExAdminOps.pending(u, "ckoff|" + wf + "|" + cs.id)) btn(b, ev, "#SkyyXaCR5", "SkyyXaCOff", "Sure - Take off the checklist", SRED, 440, @EVD@.of("a", "xcoff"));
    else btn(b, ev, "#SkyyXaCR5", "SkyyXaCOff", "Take off the checklist", SOFF, 440, @EVD@.of("a", "xcoff"));
    return;
  }
  if (ce == null) {
    lab(b, "#SkyyXaDet", "SkyyXaCSelH", "Click Edit on an entry", 0, 30, 20, true, "#e6eef6", 0);
    lab(b, "#SkyyXaDet", "SkyyXaCSelT", "Then change its text, tick or untick a custom task for an online player, or remove it.", 0, 44, 14, false, "#9fb8cc", 0);
    return;
  }
  lab(b, "#SkyyXaDet", "SkyyXaCSelH", "Selected: " + ce.id + " - " + @PKG@.ExAdminOps.entryKind(ce), 0, 30, 20, true, "#9fd0ff", 0);
  row(b, "#SkyyXaDet", "SkyyXaCR6");
  box(b, "#SkyyXaCR6", "SkyyXaCEText", 290, 80, "Entry text", this.kCEText != null ? this.kCEText : ce.text);
  gap(b, "#SkyyXaCR6", 10, 44);
  btn(b, ev, "#SkyyXaCR6", "SkyyXaCSave", "Save text", SG, 140, ev3("xcsave", "@XCEText", "#SkyyXaCEText.Value", null, null, null, null));
  if (ce.type == 4) {
    row(b, "#SkyyXaDet", "SkyyXaCR7");
    box(b, "#SkyyXaCR7", "SkyyXaCPlayer", 200, 32, "Player name", this.kCPlayer);
    gap(b, "#SkyyXaCR7", 10, 44);
    btn(b, ev, "#SkyyXaCR7", "SkyyXaCTick", "Tick", SG, 115, ev3("xctick", "@XCPlayer", "#SkyyXaCPlayer.Value", null, null, null, null));
    gap(b, "#SkyyXaCR7", 10, 44);
    btn(b, ev, "#SkyyXaCR7", "SkyyXaCUntick", "Untick", SOFF, 115, ev3("xcuntick", "@XCPlayer", "#SkyyXaCPlayer.Value", null, null, null, null));
  }
  row(b, "#SkyyXaDet", "SkyyXaCR8");
  if (@PKG@.ExAdminOps.pending(u, "ck|" + wf + "|" + ce.id)) btn(b, ev, "#SkyyXaCR8", "SkyyXaCRm", "Sure - Remove", SRED, 200, @EVD@.of("a", "xcrm"));
  else btn(b, ev, "#SkyyXaCR8", "SkyyXaCRm", "Remove", SRED, 200, @EVD@.of("a", "xcrm"));
  boolean gone = ce.type == 1 && @PKG@.ChestReg.get(wf, ce.x, ce.y, ce.z) == null;
  lab(b, "#SkyyXaDet", "SkyyXaCInfo", @PKG@.ExAdminOps.haveEntry(wd, ce, on) + " of " + on.size() + " online players here have it" + (gone ? " - the chest left the loot registry (broken?): done for those who opened it, impossible for others" : "") + (ce.type == 4 ? " - ticks go to the player's ACTIVE profile" : ""), 0, 44, 14, false, gone ? "#ff9a70" : "#9fb8cc", 0);
}""")
M(apg, r"""
public void switches(@UCB@ b, @UEB@ ev, String par) {
  lab(b, par, "SkyyXaSwH", "Server-wide switches (config.properties)", 0, 30, 17, true, "#e6eef6", 0);
  row(b, par, "SkyyXaSwR");
  if (@PKG@.ExpCfg.SPOTS_ON) btn(b, ev, "#SkyyXaSwR", "SkyyXaISpots", "All spots ON", SON, 220, @EVD@.of("a", "xispots"));
  else btn(b, ev, "#SkyyXaSwR", "SkyyXaISpots", "All spots OFF", SOFF, 220, @EVD@.of("a", "xispots"));
  gap(b, "#SkyyXaSwR", 10, 44);
  if (@PKG@.ExpCfg.CHECK_ON) btn(b, ev, "#SkyyXaSwR", "SkyyXaIChecks", "All checklists ON", SON, 220, @EVD@.of("a", "xichecks"));
  else btn(b, ev, "#SkyyXaSwR", "SkyyXaIChecks", "All checklists OFF", SOFF, 220, @EVD@.of("a", "xichecks"));
}""")
M(apg, r"""
public void islandTab(@UCB@ b, @UEB@ ev, java.util.UUID u, @WLD@ w, String wf, @PKG@.WorldDef wd) {
  lists(b);
  @PKG@.WorldDef d0 = wd != null ? wd : @PKG@.SpotReg.blank(w.getName(), wf);
  lab(b, "#SkyyXaList", "SkyyXaLHead", "Players in this world", 0, 32, 18, true, "#e6eef6", 0);
  java.util.ArrayList on = @PKG@.ExAdminOps.onlineIn(w);
  int[] t = new int[4];
  for (int i = 0; i < on.size() && i < 10; i++) {
    @PR@ pp = (@PR@) on.get(i);
    String k = @PKG@.ExpIO.pkey(pp.getUuid());
    @PKG@.ExpData d = @PKG@.ExpStore.cached(k);
    String prof = "";
    try { Object po = @PKG@.ExpIO.bridge().get("profile:" + pp.getUuid().toString()); if (po instanceof String) prof = " (profile " + (String) po + ")"; } catch (Throwable x) { }
    String line = "";
    if (d == null) line = pp.getUsername() + prof + " - not loaded yet";
    else if (d.bad) line = pp.getUsername() + prof + " - UNREADABLE exploration file";
    else {
      @PKG@.ExpStore.progress(d, wd, t);
      int[] c = @PKG@.ExpStore.spotCounts(d, wd);
      line = pp.getUsername() + prof + " - " + (t[1] > 0 ? t[0] + " of " + t[1] + " (" + @PKG@.ExpCheck.pct(t[0], t[1]) + "%)" : "no checklist") + " - " + (c[0] + c[2]) + " spots found here" + (@PKG@.ExpStore.isDone(d, wf) ? " - reward paid" : "");
    }
    lab(b, "#SkyyXaList", "SkyyXaIP" + i, line, 0, 40, 16, false, "#c8d6e4", 0);
  }
  if (on.size() > 10) lab(b, "#SkyyXaList", "SkyyXaIPMore", "... and " + (on.size() - 10) + " more", 0, 30, 14, false, "#9fb8cc", 0);
  vgap(b, "#SkyyXaList", 12);
  lab(b, "#SkyyXaList", "SkyyXaINote", "Every other number: /exploreadmin set <key> <value> (see config.properties) - /exploreadmin help lists every command. The file of this world: " + @PKG@.SpotReg.fileName(wf), 0, 70, 15, false, "#9fb8cc", 0);
  lab(b, "#SkyyXaDet", "SkyyXaIH", "Island", 0, 30, 20, true, "#e6eef6", 0);
  row(b, "#SkyyXaDet", "SkyyXaIR1");
  box(b, "#SkyyXaIR1", "SkyyXaIName", 300, 80, "Island name", this.kIName != null ? this.kIName : d0.name);
  gap(b, "#SkyyXaIR1", 10, 44);
  btn(b, ev, "#SkyyXaIR1", "SkyyXaISaveName", "Save name", SG, 140, ev3("xiname", "@XIName", "#SkyyXaIName.Value", null, null, null, null));
  row(b, "#SkyyXaDet", "SkyyXaIR2");
  if (d0.checklist) btn(b, ev, "#SkyyXaIR2", "SkyyXaIChk", "Checklist ON", SON, 300, @EVD@.of("a", "xichk"));
  else btn(b, ev, "#SkyyXaIR2", "SkyyXaIChk", "Checklist OFF", SOFF, 300, @EVD@.of("a", "xichk"));
  lab(b, "#SkyyXaDet", "SkyyXaIRwH", "Reward at 100% (XP and coins, 0 = none)", 0, 30, 17, true, "#e6eef6", 0);
  row(b, "#SkyyXaDet", "SkyyXaIR3");
  box(b, "#SkyyXaIR3", "SkyyXaIRwXp", 140, 6, "XP", this.kIRwXp != null ? this.kIRwXp : String.valueOf(d0.rewardXp));
  gap(b, "#SkyyXaIR3", 10, 44);
  box(b, "#SkyyXaIR3", "SkyyXaIRwCo", 140, 10, "coins", this.kIRwCo != null ? this.kIRwCo : String.valueOf(d0.rewardCoins));
  gap(b, "#SkyyXaIR3", 10, 44);
  btn(b, ev, "#SkyyXaIR3", "SkyyXaISaveRw", "Save rewards", SG, 150, ev3("xirw", "@XIRwXp", "#SkyyXaIRwXp.Value", "@XIRwCo", "#SkyyXaIRwCo.Value", null, null));
  lab(b, "#SkyyXaDet", "SkyyXaIRwN", @PKG@.ExpIO.fn("coins:fn:add") == null ? "coins need SkyyCoins (not installed now - the XP is still paid)" : "Paid once per profile when its checklist reaches 100%", 0, 26, 14, false, "#9fb8cc", 0);
  lab(b, "#SkyyXaDet", "SkyyXaIDfH", "Default XP for new spots here", 0, 30, 17, true, "#e6eef6", 0);
  row(b, "#SkyyXaDet", "SkyyXaIR4");
  box(b, "#SkyyXaIR4", "SkyyXaIDefSp", 140, 6, "spot XP", this.kIDefSp != null ? this.kIDefSp : (d0.spotXp < 0L ? "" : String.valueOf(d0.spotXp)));
  gap(b, "#SkyyXaIR4", 10, 44);
  box(b, "#SkyyXaIR4", "SkyyXaIDefSe", 140, 6, "secret XP", this.kIDefSe != null ? this.kIDefSe : (d0.secretXp < 0L ? "" : String.valueOf(d0.secretXp)));
  gap(b, "#SkyyXaIR4", 10, 44);
  btn(b, ev, "#SkyyXaIR4", "SkyyXaISaveDef", "Save defaults", SG, 150, ev3("xidef", "@XIDefSp", "#SkyyXaIDefSp.Value", "@XIDefSe", "#SkyyXaIDefSe.Value", null, null));
  lab(b, "#SkyyXaDet", "SkyyXaIDfN", "Blank or -1 = the config value (" + @PKG@.ExpDefs.grp(@PKG@.ExpCfg.SPOT_XP) + " / " + @PKG@.ExpDefs.grp(@PKG@.ExpCfg.SECRET_XP) + ")", 0, 26, 14, false, "#9fb8cc", 0);
  sep(b, "#SkyyXaDet");
  switches(b, ev, "#SkyyXaDet");
}""")
M(apg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.lastBuild = System.currentTimeMillis();
  java.util.UUID u = this.playerRef.getUuid();
  @WLD@ w = @PKG@.ExAdminOps.worldOf(st);
  String wn = w == null ? "?" : w.getName();
  boolean ex = w == null || @PKG@.ExpCfg.excluded(wn);
  String wf = ex ? null : @PKG@.ChestReg.wf(wn);
  @PKG@.WorldDef wd = wf == null ? null : @PKG@.SpotReg.byWf(wf);
  int[] p = @PKG@.ExAdminOps.pos(ref, st);
  int t = this.tab;
  if (t < 0 || t > 2) t = 0;
  b.appendInline((String) null, "Group #SkyyXaRoot { Anchor: (Width: 1120, Height: 900); Background: #0b1524(0.97); Padding: (Horizontal: 20, Vertical: 12); LayoutMode: Top; }");
  b.appendInline("#SkyyXaRoot", "Group { Anchor: (Height: 3); Background: #e0a040; }");
  b.appendInline("#SkyyXaRoot", "Group #SkyyXaHead { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); }");
  lab(b, "#SkyyXaHead", "SkyyXaTitle", "Exploration admin - " + (wd != null ? wd.name : wn), 580, 44, 24, true, "#ffe08a", 0);
  btn(b, ev, "#SkyyXaHead", "SkyyXaTab0", "Spots", t == 0 ? SON : SOFF, 150, @EVD@.of("a", "xtab0"));
  gap(b, "#SkyyXaHead", 8, 44);
  btn(b, ev, "#SkyyXaHead", "SkyyXaTab1", "Checklist", t == 1 ? SON : SOFF, 150, @EVD@.of("a", "xtab1"));
  gap(b, "#SkyyXaHead", 8, 44);
  btn(b, ev, "#SkyyXaHead", "SkyyXaTab2", "Island", t == 2 ? SON : SOFF, 150, @EVD@.of("a", "xtab2"));
  String fs = "";
  if (wf != null) {
    Object bad = @PKG@.SpotReg.BAD.get(wf);
    if (bad != null) fs = " - WORLD FILE " + ((String) bad).toUpperCase() + " (edits refused)";
    else if (@PKG@.SpotReg.edited(wf)) fs = " - WORLD FILE EDITED BY HAND (run /exploreadmin reload)";
    fs = fs + @PKG@.SpotReg.unsaved(wf);
  }
  String sub = "World " + wn + " - " + (wd == null ? "0 spots - 0 checklist entries" : wd.spots.length + " spots (" + wd.secrets + " secret) - " + wd.checks + " checklist entries") + (p != null ? " - you stand at " + p[0] + " " + p[1] + " " + p[2] : "") + fs;
  lab(b, "#SkyyXaRoot", "SkyyXaSub", sub, 0, 28, 15, false, fs.length() > 0 ? "#ff9a70" : "#9fb8cc", 0);
  b.appendInline("#SkyyXaRoot", "Group #SkyyXaBody { Anchor: (Height: 690); LayoutMode: Left; }");
  if (ex) {
    b.appendInline("#SkyyXaBody", "Group #SkyyXaEx { Anchor: (Width: 1080, Height: 690); LayoutMode: Top; }");
    lab(b, "#SkyyXaEx", "SkyyXaExT", "This world never pays exploration (" + @PKG@.ExpCfg.excludedWhy(wn) + ") - spots and checklists only work in shared worlds. Private islands and instances get a new copy per profile or per run.", 0, 90, 18, true, "#ffb080", 0);
    if (t == 2) switches(b, ev, "#SkyyXaEx");
  } else if (t == 0) spotsTab(b, ev, u, w, wf, wd, p);
  else if (t == 1) checkTab(b, ev, u, w, wf, wd, p);
  else islandTab(b, ev, u, w, wf, wd);
  lab(b, "#SkyyXaRoot", "SkyyXaMsg", @PKG@.ExAdminOps.textOf(this.msg), 0, 34, 17, true, @PKG@.ExAdminOps.colorOf(this.msg), 1);
  b.appendInline("#SkyyXaRoot", "Group #SkyyXaFoot { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); }");
  btn(b, ev, "#SkyyXaFoot", "SkyyXaRefresh", "Refresh", SOFF, 170, @EVD@.of("a", "xrefresh"));
  gap(b, "#SkyyXaFoot", 10, 44);
  lab(b, "#SkyyXaFoot", "SkyyXaHint", wf == null ? "Spots and checklists are set up in shared worlds - admin.log keeps who changed what" : "Changes save at once to " + @PKG@.SpotReg.fileName(wf) + " - admin.log keeps who changed what", 890, 44, 15, false, "#9fb8cc", 0);
}""")
M(apg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    long now = System.currentTimeMillis();
    if (now - this.lastBuild < 1000L) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    @PR@ pr = this.playerRef;
    if (!@PKG@.ExAdminOps.perm(pr)) { this.msg = "-You are no longer an admin (skyyexploration.admin)"; rebuild(); return; }
    @WLD@ w = @PKG@.ExAdminOps.worldOf(st);
    if (w == null) return;
    String wf = @PKG@.ChestReg.wf(w.getName());
    @PKG@.WorldDef wd = @PKG@.SpotReg.byWf(wf);
    if (a.equals("xtab0") || a.equals("xtab1") || a.equals("xtab2")) { this.tab = a.charAt(4) - '0'; this.page = 0; this.msg = ""; clearKeeps(); rebuild(); return; }
    if (a.equals("xrefresh")) { this.msg = ""; rebuild(); return; }
    if (a.equals("xprev")) { this.page = this.page - 1; rebuild(); return; }
    if (a.equals("xnext")) { this.page = this.page + 1; rebuild(); return; }
    if (a.equals("xsort")) { this.sort = 1 - this.sort; this.page = 0; rebuild(); return; }
    if (a.startsWith("xedit") || a.startsWith("xcedit")) {
      boolean ck = a.startsWith("xcedit");
      int i = -1;
      try { i = Integer.parseInt(a.substring(ck ? 6 : 5)); } catch (Throwable t) { i = -1; }
      if (i < 0 || i >= 8 || this.rowIds == null || this.rowIds[i] == null) return;
      String id = this.rowIds[i];
      boolean isSpot = id.startsWith("s");
      boolean exists = isSpot ? @PKG@.SpotReg.spotById(wd, id) != null : @PKG@.SpotReg.entryById(wd, id) != null;
      if (!exists) { this.msg = isSpot ? "-That spot was removed - Refresh" : "-That checklist entry was removed - Refresh"; rebuild(); return; }
      if (ck) { this.selEntry = id; this.kCEText = null; } else { this.selSpot = id; this.kEName = null; this.kERad = null; this.kEXp = null; }
      this.msg = "";
      rebuild();
      return;
    }
    if (a.equals("xnsec")) {
      this.kNName = jsonStr(data, "@XNName"); this.kNRad = jsonStr(data, "@XNRad"); this.kNXp = jsonStr(data, "@XNXp");
      this.newSecret = !this.newSecret;
      this.msg = "";
      rebuild();
      return;
    }
    String res = null;
    if (a.equals("xadd")) {
      String nm = jsonStr(data, "@XNName");
      String rd = jsonStr(data, "@XNRad");
      String xp = jsonStr(data, "@XNXp");
      res = @PKG@.ExAdminOps.spotAdd(pr, ref, st, w, nm, rd, xp, this.newSecret ? "secret" : "open");
      if (res.startsWith("+")) {
        this.kNName = null; this.kNRad = null; this.kNXp = null; this.newSecret = false;
        @PKG@.WorldDef nw = @PKG@.SpotReg.byWf(wf);
        String nk = @PKG@.ExpDefs.nkey(nm);
        if (nw != null) { for (int i = 0; i < nw.spots.length; i++) if (@PKG@.ExpDefs.nkey(nw.spots[i].name).equals(nk)) { this.selSpot = nw.spots[i].id; this.kEName = null; this.kERad = null; this.kEXp = null; } }
      } else { this.kNName = nm; this.kNRad = rd; this.kNXp = xp; }
    } else if (a.equals("xren")) {
      String v = jsonStr(data, "@XEName");
      res = @PKG@.ExAdminOps.spotEdit(pr, ref, st, w, this.selSpot == null ? "" : this.selSpot, "name", v);
      this.kEName = res.startsWith("-") ? v : null;
    } else if (a.equals("xsave")) {
      String rd = jsonStr(data, "@XERad");
      String xp = jsonStr(data, "@XEXp");
      res = @PKG@.ExAdminOps.spotSetRX(pr, ref, st, w, this.selSpot, rd, xp);
      if (res.startsWith("-")) { this.kERad = rd; this.kEXp = xp; } else { this.kERad = null; this.kEXp = null; }
    } else if (a.equals("xesec") || a.equals("xechk")) {
      this.kEName = jsonStr(data, "@XEName"); this.kERad = jsonStr(data, "@XERad"); this.kEXp = jsonStr(data, "@XEXp");
      @PKG@.SpotDef sp = @PKG@.SpotReg.spotById(wd, this.selSpot);
      if (sp == null) res = "-That spot was removed - Refresh";
      else if (a.equals("xesec")) res = @PKG@.ExAdminOps.spotEdit(pr, ref, st, w, sp.id, "secret", sp.secret ? "no" : "yes");
      else res = @PKG@.ExAdminOps.spotEdit(pr, ref, st, w, sp.id, "checklist", sp.check ? "no" : "yes");
      if (sp != null) {
        if (this.kEName.equals(sp.name)) this.kEName = null;
        if (this.kERad.equals(String.valueOf(sp.r))) this.kERad = null;
        if (this.kEXp.equals(String.valueOf(sp.xp))) this.kEXp = null;
      }
    } else if (a.equals("xmove")) {
      res = @PKG@.ExAdminOps.spotMove(pr, ref, st, w, this.selSpot == null ? "" : this.selSpot);
    } else if (a.equals("xtp")) {
      res = @PKG@.ExAdminOps.spotTp(pr, ref, st, w, this.selSpot == null ? "" : this.selSpot, true);
      if (res.startsWith("+")) { @PKG@.ExAdminOps.tell(pr, res); return; }
    } else if (a.equals("xrm")) {
      res = @PKG@.ExAdminOps.spotRemove(pr, ref, st, w, this.selSpot == null ? "" : this.selSpot);
      if (res.startsWith("+")) this.selSpot = null;
    } else if (a.equals("xcchest")) {
      res = @PKG@.ExAdminOps.ckAddChest(pr, ref, st, w);
    } else if (a.equals("xczone")) {
      res = @PKG@.ExAdminOps.ckAddZone(pr, ref, st, w, "");
    } else if (a.equals("xczall")) {
      res = @PKG@.ExAdminOps.ckAddZone(pr, ref, st, w, "all");
    } else if (a.equals("xccustom")) {
      String v = jsonStr(data, "@XCText");
      res = @PKG@.ExAdminOps.ckAddCustom(pr, ref, st, w, v);
      this.kCText = res.startsWith("-") ? v : null;
    } else if (a.equals("xccount")) {
      String v = jsonStr(data, "@XCNum");
      res = @PKG@.ExAdminOps.ckAddChests(pr, ref, st, w, v);
      this.kCNum = res.startsWith("-") ? v : null;
    } else if (a.equals("xcsave")) {
      String v = jsonStr(data, "@XCEText");
      res = @PKG@.ExAdminOps.ckText(pr, ref, st, w, this.selEntry == null ? "" : this.selEntry, v);
      this.kCEText = res.startsWith("-") ? v : null;
    } else if (a.equals("xctick") || a.equals("xcuntick")) {
      String v = jsonStr(data, "@XCPlayer");
      this.kCPlayer = v;
      res = @PKG@.ExAdminOps.ckTick(pr, @PKG@.ExAdminOps.findOnline(v), this.selEntry == null ? "" : this.selEntry, a.equals("xctick"));
    } else if (a.equals("xcrm")) {
      res = @PKG@.ExAdminOps.ckRemove(pr, ref, st, w, this.selEntry == null ? "" : this.selEntry);
      if (res.startsWith("+")) this.selEntry = null;
    } else if (a.equals("xcoff")) {
      res = @PKG@.ExAdminOps.ckRemove(pr, ref, st, w, this.selEntry == null ? "" : this.selEntry);
      if (res.startsWith("+")) this.selEntry = null;
    } else if (a.equals("xiname")) {
      String v = jsonStr(data, "@XIName");
      res = @PKG@.ExAdminOps.islandName(pr, w, v);
      this.kIName = res.startsWith("-") ? v : null;
    } else if (a.equals("xichk")) {
      res = @PKG@.ExAdminOps.islandCheck(pr, w, (wd == null || wd.checklist) ? "off" : "on");
    } else if (a.equals("xirw")) {
      String x = jsonStr(data, "@XIRwXp");
      String c = jsonStr(data, "@XIRwCo");
      res = @PKG@.ExAdminOps.islandReward(pr, w, x, c);
      if (res.startsWith("-")) { this.kIRwXp = x; this.kIRwCo = c; } else { this.kIRwXp = null; this.kIRwCo = null; }
    } else if (a.equals("xidef")) {
      String x = jsonStr(data, "@XIDefSp");
      String c = jsonStr(data, "@XIDefSe");
      res = @PKG@.ExAdminOps.islandDefaults(pr, w, x, c);
      if (res.startsWith("-")) { this.kIDefSp = x; this.kIDefSe = c; } else { this.kIDefSp = null; this.kIDefSe = null; }
    } else if (a.equals("xispots")) {
      res = @PKG@.ExAdminOps.setKey(pr, "spots.enabled", @PKG@.ExpCfg.SPOTS_ON ? "false" : "true");
    } else if (a.equals("xichecks")) {
      res = @PKG@.ExAdminOps.setKey(pr, "checklist.enabled", @PKG@.ExpCfg.CHECK_ON ? "false" : "true");
    } else return;
    this.msg = res == null ? "" : res;
    rebuild();
  } catch (Throwable e) { @PKG@.ExpCfg.warn("exploration admin page click failed: " + e); }
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
  super("quiet", "Toggle the aggregated chunk XP chat line (per profile; the same switch as /settings when SkyyMenu is installed)");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
# 0.2 (spec 9): with the settings registry (settings:fn:set) the shortcut flips explore.chunkXp; without it, 0.1's per-profile quiet flag
M(qcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.ExpIO.pkey(u);
  @PKG@.ExpData d = @PKG@.ExpStore.dataK(k, u);
  if (d.bad) { pr.sendMessage(@MSG@.raw("[Exploration] Your exploration file could not be read - nothing can change until an admin fixes it").color("#ff9090")); return; }
  if (@PKG@.ExpIO.fn("settings:fn:set") != null) {
    boolean shown = !d.quiet && @PKG@.ExpIO.notifyOn(u, "explore.chunkXp");
    Boolean r = @PKG@.ExpIO.setSetting(u, "explore.chunkXp", !shown);
    if (!Boolean.TRUE.equals(r)) { pr.sendMessage(@MSG@.raw("[Exploration] Could not save that setting right now - try again (or use /settings)").color("#ffb080")); return; }
    if (!shown && d.quiet) { @PKG@.ExpStore.flipQuiet(d); @PKG@.ExpStore.saveSoon(k); }
    pr.sendMessage(@MSG@.raw(shown ? "[Exploration] Chunk XP messages hidden (also in /settings). /explore quiet again to show them." : "[Exploration] Chunk XP messages shown (also in /settings)."));
    return;
  }
  boolean q = @PKG@.ExpStore.flipQuiet(d);
  @PKG@.ExpStore.saveSoon(k);
  pr.sendMessage(@MSG@.raw(q ? "[Exploration] Chunk XP messages hidden. /explore quiet again to show them." : "[Exploration] Chunk XP messages shown."));
}""")
C(ecmd, r"""
public ExploreCmd() {
  super("explore", "Your exploration: loot chests, map, zones, discoveries, titles and island checklists - /explore, /explore quiet");
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
  super("reload", "(admin) Re-read config.properties and every worlds/<world>.properties (pending in-game saves are written first)");
  requirePermission("skyyexploration.admin");
  setPermissionGroups(new String[0]);
}""")
M(arl, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.ExAdminOps.tell(pr, @PKG@.ExAdminOps.reload(pr));
}""")
C(ast, r"""
public ExAdminStatsCmd() {
  super("stats", "(admin) Loot chest registry, spots per world, the spot check cost and online players' exploration counts");
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
  @PKG@.ExAdminOps.tell(pr, @PKG@.ExAdminOps.stats());
  java.util.Iterator pi = @UNI@.get().getPlayers().iterator();
  int m = 0;
  while (pi.hasNext() && m < 20) {
    Object o = pi.next();
    if (!(o instanceof @PR@)) continue;
    @PR@ p = (@PR@) o;
    String k = @PKG@.ExpIO.pkey(p.getUuid());
    @PKG@.ExpData d = @PKG@.ExpStore.cached(k);
    if (d == null) { pr.sendMessage(@MSG@.raw("  " + p.getUsername() + " (" + k + "): not loaded yet")); m++; continue; }
    pr.sendMessage(@MSG@.raw("  " + p.getUsername() + " (" + k + "): " + (d.bad ? "UNREADABLE FILE - " : "") + "zones " + @PKG@.ExpStore.knownZones(d) + "/" + @PKG@.ExpDefs.NR + ", chests " + d.chests + ", luck " + d.luck + ", chunks " + d.total + ", spots " + d.spots + " (" + d.secrets + " secret), owed " + d.owed + ", paid " + d.earned));
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
  @PKG@.ExpIO.deleteLater(@PKG@.ExpStore.spotsFile(k));
  @PKG@.ExpIO.deleteLater(@PKG@.ExpStore.ticksFile(k));
  @PKG@.ExpIO.deleteLater(@PKG@.ExpStore.doneFile(k));
  @PKG@.ExpIO.deleteLater(@PKG@.ExpStore.zonesFile(k));
  @PKG@.ExpStore.saveSoon(k);
  @PKG@.ExpTitles.KNOWN.remove(k);
  @PKG@.ExpState s = (@PKG@.ExpState) @PKG@.ExpTick.ST.get(u);
  if (s != null) { s.hasLast = false; s.pendN = 0L; s.pendXp = 0L; s.inside = null; s.insideWf = null; s.pctWf = null; s.pctStr = null; }
  @PKG@.ExpIO.adminLog(pr, world == null ? "-" : world.getName(), "resetme profile=" + k);
  pr.sendMessage(@MSG@.raw("[Exploration] Your exploration record on profile " + k + " was cleared (zones, loot chests, chunks, title, spot finds, checklist ticks and paid checklist rewards). XP already paid to SkyySkills stays; " + d.owed + " XP still waiting is kept.").color("#ffd27a"));
}""")

# ---- 0.2 admin commands (spec 5). Every named command AND subcommand: requirePermission + setPermissionGroups(new String[0]) (0.1's
# admin pattern); usage variants (description-only constructor, picked by token count at every command level) carry their own
# requirePermission and no permission groups. Values with spaces or commas are GREEDY_STRING last arguments.
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
CMDS = []
def cmd(clsname, name, desc, args, body, subs=(), variants=()):
    """One admin AbstractPlayerCommand. name None = a usage variant. args = [(field, argName, argDesc, STRING|GREEDY_STRING|PLAYER_REF)]
    read into a0, a1, ... (PLAYER_REF -> @PR@ p<i>, null when absent)."""
    c = pool.makeClass(PKG + "." + clsname, pool.get(T["APC"]))
    for (fld, _an, _ad, _ty) in args:
        F(c, "public @RA@ %s;" % fld)
    if name is None:
        lines = ['super("%s");' % desc, 'requirePermission("skyyexploration.admin");']
    else:
        lines = ['super("%s", "%s");' % (name, desc), 'requirePermission("skyyexploration.admin");', "setPermissionGroups(new String[0]);"]
    for (fld, an, ad, ty) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (fld, an, ad, ty))
    for s in subs:
        lines.append("addSubCommand(new @PKG@.%s());" % s)
    for v in variants:
        lines.append("addUsageVariant(new @PKG@.%s());" % v)
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    reads = ""
    for i, a in enumerate(args):
        if a[3] == "PLAYER_REF":
            reads += "    Object o%d = ctx.get(this.%s);\n    @PR@ p%d = o%d instanceof @PR@ ? (@PR@) o%d : null;\n" % (i, a[0], i, i, i)
        else:
            reads += "    String a%d = String.valueOf(ctx.get(this.%s));\n" % (i, a[0])
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.ExpCfg.warn(\"/exploreadmin " + (name or clsname) + " failed: \" + t);\n"
      "    @PKG@.ExAdminOps.tell(pr, \"-Something went wrong - the server log has the details\");\n  }\n}")
    CMDS.append(c)
    return c

O = "@PKG@.ExAdminOps."
def T_(expr): return O + "tell(pr, " + expr + ");"
A_SPOT = ("spotArg", "spot", "spot id (s3) or name / first 3+ letters", "STRING")
cmd("ExAdminHelpCmd", "help", "(admin) Every /exploreadmin command", [], T_(O + "help()"))
cmd("ExAdminSetCmd", "set", "(admin) Change any config.properties key in game - set <key> <value> (the file is rewritten)",
    [("keyArg", "key", "a config.properties key", "STRING"), ("valArg", "value", "the new value (spaces and commas allowed)", "GREEDY_STRING")],
    T_(O + "setKey(pr, a0, a1)"))
cmd("ExAdminGetCmd", "get", "(admin) Show a config.properties value - get <key>", [("keyArg", "key", "a config.properties key", "STRING")],
    T_(O + "getKey(pr, a0)"))
# spot add <name> [radius] [xp] [secret|open] = 1 + 3 usage variants (token counts 2, 3, 4)
A_NAME = ("nameArg", "name", "spot name, one word - _ becomes a space", "STRING")
A_RAD = ("radArg", "radius", "radius in blocks", "STRING")
A_XP = ("xpArg", "xp", "Exploration XP for the first visit", "STRING")
A_SEC = ("secArg", "secret", "secret or open", "STRING")
cmd("ExSpotAdd2Cmd", None, "Add a spot where you stand with a radius - add <name> <radius>", [A_NAME, A_RAD],
    T_(O + 'spotAdd(pr, ref, store, world, a0, a1, "", "")'))
cmd("ExSpotAdd3Cmd", None, "Add a spot where you stand - add <name> <radius> <xp>", [A_NAME, A_RAD, A_XP],
    T_(O + 'spotAdd(pr, ref, store, world, a0, a1, a2, "")'))
cmd("ExSpotAdd4Cmd", None, "Add a spot where you stand - add <name> <radius> <xp> <secret|open>", [A_NAME, A_RAD, A_XP, A_SEC],
    T_(O + "spotAdd(pr, ref, store, world, a0, a1, a2, a3)"))
cmd("ExSpotAddCmd", "add", "(admin) Add a discovery spot where you stand - add <name> [radius] [xp] [secret|open]", [A_NAME],
    T_(O + 'spotAdd(pr, ref, store, world, a0, "", "", "")'), variants=("ExSpotAdd2Cmd", "ExSpotAdd3Cmd", "ExSpotAdd4Cmd"))
cmd("ExSpotMoveCmd", "move", "(admin) Move a spot to where you stand (its id and every find stay)", [A_SPOT],
    T_(O + "spotMove(pr, ref, store, world, a0)"))
cmd("ExSpotRemoveCmd", "remove", "(admin) Remove a spot - repeat within 10 s to confirm", [A_SPOT], T_(O + "spotRemove(pr, ref, store, world, a0)"))
cmd("ExSpotTpCmd", "tp", "(admin) Teleport to a spot of this world (/tp back returns)", [A_SPOT], T_(O + "spotTp(pr, ref, store, world, a0, false)"))
cmd("ExSpotListCmd", "list", "(admin) The spots of this world, nearest first", [], T_(O + "spotList(pr, ref, store, world)"))
cmd("ExSpotEditCmd", "edit", "(admin) Change a spot - edit <spot> <name|radius|xp|secret|checklist> <value>",
    [A_SPOT, ("fieldArg", "field", "name, radius, xp, secret or checklist", "STRING"), ("valArg", "value", "the new value", "GREEDY_STRING")],
    T_(O + "spotEdit(pr, ref, store, world, a0, a1, a2)"))
cmd("ExSpotCmd", "spot", "(admin) Discovery and secret spots - spot add | move | remove | tp | list | edit", [],
    T_('"=/exploreadmin spot add <name> [radius] [xp] [secret|open] | move <spot> | remove <spot> | tp <spot> | list | edit <spot> <field> <value> - or /exploreadmin for the page"'),
    subs=("ExSpotAddCmd", "ExSpotMoveCmd", "ExSpotRemoveCmd", "ExSpotTpCmd", "ExSpotListCmd", "ExSpotEditCmd"))
# check ...
A_ID = ("idArg", "id", "checklist entry number (or a spot id / name for remove)", "STRING")
cmd("ExCheckListCmd", "list", "(admin) The checklist of this world", [], T_(O + "ckList(pr, ref, store, world)"))
cmd("ExCkAddChestCmd", "chest", "(admin) Add the nearest recorded loot chest as an entry", [], T_(O + "ckAddChest(pr, ref, store, world)"))
cmd("ExCkAddChestsCmd", "chests", "(admin) Add an entry - open N loot chests in this world", [("numArg", "n", "how many loot chests", "STRING")],
    T_(O + "ckAddChests(pr, ref, store, world, a0)"))
cmd("ExCkAddZoneIdCmd", None, "Add a Hytale region by id, or all 13 named regions - zone <region|all>",
    [("regionArg", "region", "region id such as Zone1_Tier1, or all", "STRING")], T_(O + "ckAddZone(pr, ref, store, world, a0)"))
cmd("ExCkAddZoneCmd", "zone", "(admin) Add the Hytale region you stand in - zone [region|all]", [],
    T_(O + 'ckAddZone(pr, ref, store, world, "")'), variants=("ExCkAddZoneIdCmd",))
cmd("ExCkAddCustomCmd", "custom", "(admin) Add a custom task - custom <text>", [("textArg", "text", "the task text", "GREEDY_STRING")],
    T_(O + "ckAddCustom(pr, ref, store, world, a0)"))
cmd("ExCkAddCmd", "add", "(admin) check add chest | chests <n> | zone [region|all] | custom <text>", [],
    T_('"=/exploreadmin check add chest | chests <n> | zone [region|all] | custom <text>"'),
    subs=("ExCkAddChestCmd", "ExCkAddChestsCmd", "ExCkAddZoneCmd", "ExCkAddCustomCmd"))
cmd("ExCheckRemoveCmd", "remove", "(admin) Remove an entry, or take a spot off the checklist (repeat within 10 s)", [A_ID],
    T_(O + "ckRemove(pr, ref, store, world, a0)"))
cmd("ExCheckTextCmd", "text", "(admin) Change the text of an entry - text <id> <text>",
    [("idArg", "id", "checklist entry number", "STRING"), ("textArg", "text", "the new text", "GREEDY_STRING")],
    T_(O + "ckText(pr, ref, store, world, a0, a1)"))
A_PL = ("playerArg", "player", "an online player", "PLAYER_REF")
A_CID = ("idArg", "id", "custom entry number", "STRING")
cmd("ExCheckTickCmd", "tick", "(admin) Tick a custom entry for a player's active profile - tick <player> <id>", [A_PL, A_CID],
    T_(O + "ckTick(pr, p0, a1, true)"))
cmd("ExCheckUntickCmd", "untick", "(admin) Untick a custom entry for a player's active profile - untick <player> <id>", [A_PL, A_CID],
    T_(O + "ckTick(pr, p0, a1, false)"))
cmd("ExCheckCmd", "check", "(admin) The island checklist - check list | add | remove | text | tick | untick", [],
    T_('"=/exploreadmin check list | add chest | add chests <n> | add zone [region|all] | add custom <text> | remove <id> | text <id> <text> | tick <player> <id> | untick <player> <id>"'),
    subs=("ExCheckListCmd", "ExCkAddCmd", "ExCheckRemoveCmd", "ExCheckTextCmd", "ExCheckTickCmd", "ExCheckUntickCmd"))
# island ...
cmd("ExIslandNameCmd", "name", "(admin) The island name of this world - name <text>", [("textArg", "text", "island name", "GREEDY_STRING")],
    T_(O + "islandName(pr, world, a0)"))
cmd("ExIslandCheckCmd", "checklist", "(admin) This world's checklist on or off - checklist <on|off>", [("onArg", "state", "on or off", "STRING")],
    T_(O + "islandCheck(pr, world, a0)"))
cmd("ExIslandRewardCmd", "reward", "(admin) Reward at 100% - reward <xp> <coins> (0 = none; coins need SkyyCoins)",
    [("xpArg", "xp", "Exploration XP", "STRING"), ("coinArg", "coins", "coins", "STRING")], T_(O + "islandReward(pr, world, a0, a1)"))
cmd("ExIslandDefaultsCmd", "defaults", "(admin) XP of NEW spots here - defaults <spotXp> <secretXp> (-1 = config)",
    [("spArg", "spotXp", "XP of new discovery spots, -1 = config", "STRING"), ("seArg", "secretXp", "XP of new secret spots, -1 = config", "STRING")],
    T_(O + "islandDefaults(pr, world, a0, a1)"))
cmd("ExIslandCmd", "island", "(admin) This world's island - name, checklist switch, 100% reward, new-spot XP", [], T_(O + "islandShow(pr, world)"),
    subs=("ExIslandNameCmd", "ExIslandCheckCmd", "ExIslandRewardCmd", "ExIslandDefaultsCmd"))
C(acmd, r"""
public ExploreAdminCmd() {
  super("exploreadmin", "(admin) SkyyExploration admin page - /exploreadmin help lists every command");
  requirePermission("skyyexploration.admin");
  setPermissionGroups(new String[0]);
  addSubCommand(new @PKG@.ExAdminReloadCmd());
  addSubCommand(new @PKG@.ExAdminStatsCmd());
  addSubCommand(new @PKG@.ExAdminResetCmd());
  addSubCommand(new @PKG@.ExAdminHelpCmd());
  addSubCommand(new @PKG@.ExAdminSetCmd());
  addSubCommand(new @PKG@.ExAdminGetCmd());
  addSubCommand(new @PKG@.ExSpotCmd());
  addSubCommand(new @PKG@.ExCheckCmd());
  addSubCommand(new @PKG@.ExIslandCmd());
}""")
# 0.2: /exploreadmin opens the admin page (Spots tab); the 0.1 usage line lives in /exploreadmin help
M(acmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
""" + ADMIN_CHECK + r"""  try {
    @PLA@ player = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (player == null) { @PKG@.ExAdminOps.tell(pr, @PKG@.ExAdminOps.help()); return; }
    player.getPageManager().openCustomPage(ref, store, new @PKG@.AdminPage(pr, 0));
  } catch (Throwable e) {
    @PKG@.ExpCfg.warn("exploration admin page failed: " + e);
    @PKG@.ExAdminOps.tell(pr, @PKG@.ExAdminOps.help());
  }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
F(pl, "public java.util.function.Function statsFn;")
F(pl, "public java.util.function.Function titleFn;")
F(pl, "public java.util.function.Function completeFn;")
F(pl, "public java.util.function.Function pctFn;")
C(pl, "public SkyyExplorationPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ExpCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyExploration");
  @PKG@.ExpCfg.FILE = base.resolve("config.properties");
  @PKG@.ExpStore.DIR = base.resolve("players");
  @PKG@.ChestReg.DIR = base.resolve("chests");
  @PKG@.SpotReg.DIR = base.resolve("worlds");
  @PKG@.ExpIO.ADMIN = base.resolve("admin.log");
  String sum = @PKG@.ExpCfg.load();
  int chests = @PKG@.ChestReg.loadAll();
  String worlds = @PKG@.SpotReg.loadAll();
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
  this.completeFn = new @PKG@.ExpCompleteFn();
  this.pctFn = new @PKG@.ExpPctFn();
  b.put("explore:fn:complete", this.completeFn);
  b.put("explore:fn:pct", this.pctFn);
  @PKG@.ExpIO.regSetting("explore.chunkXp", "Exploration map XP", "skills", true, "+1,240 Exploration XP from 18 new chunks - at most every 30 s");
  @PKG@.ExpIO.regSetting("explore.finds", "Exploration finds", "skills", true, "Loot chests, chest luck, new zones, discoveries, checklists and new titles");
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.ExpSaver(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  String sk = @PKG@.ExpSkill.hasSkills() ? "SkyySkills found" : "SkyySkills not loaded yet (XP waits in the owed ledger until it is)";
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyExploration] @VERSION@ ready - /explore, /title, /exploreadmin (admin page); " + sum + "; " + chests + " loot chests in the registry; " + worlds + "; " + cap + "; " + chat + "; " + sk);
}""".replace("@VERSION@", VERSION))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.SpotReg.flushDirty(); } catch (Throwable t) { }
  try { @PKG@.ExpIO.drain(); } catch (Throwable t) { }
  try { @PKG@.ExpStore.flushDirty(); } catch (Throwable t) { }
  try { if (!@PKG@.ExpStore.DIRTY.isEmpty()) @PKG@.ExpStore.flushDirty(); } catch (Throwable t) { }
  try { @PKG@.ExpIO.drain(); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.ExpIO.bridge();
    if (this.statsFn != null) b.remove("skill:stats:Exploration", this.statsFn);
    if (this.titleFn != null) b.remove("explore:fn:title", this.titleFn);
    if (this.completeFn != null) b.remove("explore:fn:complete", this.completeFn);
    if (this.pctFn != null) b.remove("explore:fn:pct", this.pctFn);
  } catch (Throwable t) { }
  try { @PKG@.ExpTitles.clearAll(); } catch (Throwable t) { }
  super.shutdown();
}""")

ALL = (defs, cfg, dat, est, eio, reg, spd, edf, wdf, srg, wst, sto, stk, skl, exx, ttl, esp, eck, awd, ock, css, csl, cos, tick, svr,
       tfm, cwr, chk, sfn, tfn, cfn, pfn, page, aop, apg, qcmd, ecmd, tset, tcmd, arl, ast, ars, acmd, pl) + tuple(CMDS)
for c in ALL:
    c.writeFile(OUT)
print("classes written:", len(ALL), "(%d generated admin commands)" % len(CMDS))
print("config keys settable in game:", len(KEYS), "- admin page %d x %d, /explore %d x %d" % (XA_W, XA_H, EX_W, EX_H))
print("regions:", len(REG), "named XP", sum(r["xp"] for r in REG if r["shown"]), "all zones XP", sum(r["xp"] for r in REG),
      "- loot drop lists:", len(DLS), "chest XP", min(DL_XP.values()), "..", max(DL_XP.values()), "- titles:", len(TITLES))

jar = os.path.join(HERE, "SkyyExploration-%s.jar" % VERSION)
m = B.manifest("SkyyExploration", VERSION, "SkyWynn Exploration: Exploration XP (SkyySkills 0.4.1) for the first open of every world loot chest (plus chest luck - an extra roll), every new chunk you walk into (never while flying or in creative), each of Hytale's zones and admin-placed discovery and secret spots (banner + sound on the first visit) - once per profile, no XP boosters. Island checklists with a % per profile and an optional 100% reward. Everything is set up in game: /exploreadmin (admin page: spots, checklist, island) and /exploreadmin set <key> <value> for every config key - the files always match. Titles show in front of your chat messages. /explore, /title. Per profile with SkyyProfiles (optional); reads SkyySkills / SkyyTrees / SkyyCoins through the skyy bridge; zero dependencies.", PKG + ".SkyyExplorationPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT, {})  # no assets: the page is built inline
if "--deploy" in sys.argv:   # only with Skyy's deploy OK (HANDOFF section 3); workflows never pass it
    B.deploy(jar, "SkyyExploration.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyExploration" % VERSION, disable_prefix="Skyy:")
