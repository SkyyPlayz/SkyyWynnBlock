"""0.5.1 (2026-09-25): SECURITY hotfix - /island reload clears its inherited permission groups (every player held
  skyyislands.admin through it). Notes in tools/islands_0_5_1_patch.py.
SkyyIslands 0.5 - build script. Copied from build_skyyislands_0.4.5.py (the live version) and edited; THIS script is the source
(no patch script: the change is too large for anchored replacements). The Java moved to the @TOKEN@ style of SkyyGuilds 0.1 so the
new code needs no doubled braces; every 0.4.5 class keeps its behaviour unless a 0.5 note below says otherwise.

0.5 (2026-09-24): ISLAND CO-OP + SETTINGS = research/Island-Settings-Spec.md SLICE A (Skyy's beta backlog item 7).
  Roles (spec 1.1): Owner (4, the profile that made the island) > Admin (3, a member the Owner promoted) > Member (2, co-op: their
    /island goes to the owner's island) > Trusted (1, build rights only, their /island stays their own) > Visitor (0) > Banned (-1,
    by player UUID = every profile). Server admins (skyyislands.admin) pass every flag and entry check.
  Home island (spec 1.3): IslandStore.homeKey(uuid) = the island the ACTIVE profile is a co-op member of (MEMBER_OF index, checked
    against the owner's file so a stale entry heals itself), else the profile's own key. /island, /island home, the SkyyProfiles
    switch teleport (it dispatches /island), /island info, /island menu and the bridge island:<uuid> use it; /island visit <player>
    goes to the TARGET's home island. A member's own island file/world is never touched: it is dormant and comes back on leave.
  Membership = the profile active at /island accept (one key per operation). One co-op per profile; a leader with members can't
    join; one role per player per island across profiles (anti item transfer); invite/trust/ban refuse the owner's own UUID.
  Commands (all subcommands of /island, every one setPermissionGroups hytale:Adventurer, required args only): info, home (go),
    menu (settings, options), visit (warp) <player>, invite (add) <player> = 60 s co-op invite, accept, decline, leave,
    kick (remove) <name>, promote <name>, demote <name>, disband (repeat within 10 s), trust <player>, untrust <name>,
    reset (3 runs within 20 s each, 24 h cooldown), expel <player>, ban <player>, unban <name>, bans (banlist), lock, unlock.
    Server admins only (skyyislands.admin, no Adventurer group): reload (config.properties + every island file, after hand edits).
    <name> args match the stored names (name.<key>) case-insensitively, a unique name prefix, a UUID or a profile key, so offline
    players can be kicked/untrusted/unbanned. The old flag form (/island --action invite --player X) still works (co-op invite).
  Island menu (/island menu): ONE inline page 1240 x 900 with 5 tabs - Overview (island box, Go to island, invite Accept/Decline,
    Disband / Reset for the owner, Leave for members, command help), Members (name TextField + Invite to co-op + Trust (build only);
    Enter only keeps the name - SkyyGuilds pattern; roster with Promote/Demote/Kick; pending invites; trusted list with Untrust,
    paged), Permissions (14 flags x Visitor/Trusted/Member/Admin click grid, BentoBox minimum-rank rule, read-only below Admin,
    Reset to defaults), Visitors (Public / Friends / Closed, limit -/+, visit ping, who is on the island now with Expel / Trust /
    Ban, the ban list with Unban), Island (PvP, mob spawning). Every click re-checks the clicker's rank and ends in rebuild();
    destructive buttons take 2 clicks (reset: 3); Go/Create/Leave/Reset act first and then close the page (SkyyMenu 0.1.2 order).
  Permission flags (spec 3.2 defaults, config defaults.perm.*): build, break, containers, doors, crafting, processing, beds, seats,
    harvest, animals, mobs, pickup, drop, other. Classifier = spec 3.3 (IslandPerms.useFlag/breakFlag/containerKind); breaking a
    container or furnace needs break AND its container flag. Guards: GuardDamage/Break/Place/Pickup/Use reworked onto the flags,
    NEW GuardDrop (DropItemEvent$PlayerRequest), GuardUseEntity (UseEntityEvent$Pre on a farm animal -> animals, other NPC -> other)
    and GuardHurt (DamageEventSystem in the filter damage group, SkyyClasses DamageLock pattern with Query.any(): an NPC victim hurt
    by a player -> animals or mobs). Farm animal = an NPC role under Server/NPC/Roles/Creature/Livestock + Critter (read from
    Assets.zip at BUILD time, 77 roles) + config animals.extra.
    Tightening vs spec 10.2: a player who holds a role on this island with ANOTHER profile (the owner on profile 2, a member or
    trusted player on the wrong profile) may only use doors and seats and fight hostile mobs there, whatever the grid says for
    visitors (the spec hard-denied only drop; chests/pickup/build would still move items between that player's profiles).
    Config perm.otherProfileStrict=false switches back to spec 10.2 (only drop refused); the Permissions tab states the rule.
  Visitors (spec 4.1): mode public|friends|closed, limit (1..visit.limitMax), 60 s expel block, ban list, lock/unlock, visit ping.
    Checked at /island visit (before the world loads), on ARRIVAL (IslandReady now schedules ArrivalTask on every PlayerReadyEvent
    after the first of the session: +1.5 s on the world thread) and by a 5 s sweep (SeenTick -> SweepTask on each island world that
    has players) that also catches /tpa, /teleport, respawns and settings changes. Turning PvP on sends visitors (not trusted/members)
    to the hub. PvP / mob spawning = WorldConfig.setPvpEnabled / setSpawningNPC + markChanged (vanilla command pattern), re-applied
    idempotently on arrival and by the sweep so a reset world or a reloaded island gets them back.
  /island reset (spec 1.7): Owner only, 3 runs within reset.confirmSeconds (20 s) each, reset.cooldownHours (24) cooldown, refused
    while creating or while profile:busy. Everyone but the owner on the old island goes to the hub (EvacTask), then the 0.4.5
    creation chain builds skyy-island-<key>-r<N> (fresh starter island + fresh starter kit) and the owner is teleported there.
    The reset bookkeeping (world.prev, world.old, resets, resetAt, kit removed) is written in the SAME synchronized step that
    switches world= (IslandStore.setWorldName, RESETTING map), so a failed spawn changes nothing. Members, admins, trusted, bans and
    settings stay. The old world folder stays on disk as a backup and stays protected (world.old is in the island registry); anyone
    who ends up in a retired world is sent to the hub (arrival + sweep). The late starter-kit check only fills the CURRENT world.
  Grass tint resend (spec 5): TintFix re-tints wrong columns and then calls world.getNotificationHandler().updateChunkTints(index)
    (vanilla /chunk tint) for every changed chunk - config tint.resend=tints|chunk|off (chunk = updateChunk(index), a full resend).
    Runs from ArrivalTask (+1.5 s and +6 s after the player is really in the island world - the 0.4.5 4 s command timer skipped
    islands that were still loading), from RelightNow (kept: relight + late kit) and from FillTask at creation.
  Storage (spec 9.1): islands/<pkey>.properties gains v=5, members, admins, trusted, banned, name.<key>, coopSince.<key>, ownerName,
    resets, resetAt, world.prev, world.old, settings, perm.<flag>, visit.mode, visit.prev, visit.limit, visit.notify, pvp, spawning.
    Every write sets v=5. Parsed settings are cached (IslandStore.SETTINGS, refreshed by every write) so guards never read disk.
    Hand edits of island files: /island reload (admin) or a restart. Writes retry 5 x 20 ms on Windows sharing violations.
  Config (spec 9.2, NEW Skyy_SkyyIslands/config.properties, written with defaults on first run; slice A keys only).
  MIGRATION (spec 6, at setup before anyone can connect): a file without v=5 is copied to <key>.properties.v4bak, every 0.4.x
    members= entry (they only ever meant build rights) moves to trusted=, and v=5 is written. Nobody becomes a Member by upgrading.
  Bridge (spec 9.3): island:<uuid> = HOME island world (members see "Your Island" on the co-op island in SkyyHud 0.3.8 unchanged);
    island:perm:fn (Object[]{UUID, world, flag} -> Boolean or null; flags = the 14 ids + enter + settings), island:role:fn
    (Object[]{UUID, world} -> owner|admin|member|trusted|visitor|banned or null), island:owner:fn (world -> owner key or null),
    island:coop:fn (UUID -> String[] UUIDs of that player's home co-op, owner first, empty without an island), island:epoch (Long,
    +1 on every membership/settings change).
  NOT in 0.5 (spec slice B, feasible, planned for 0.5.1): biome presets, weather lock, visitor landing point. Spec "Later": time lock,
    visits while the owner is offline, leader transfer, deleting the old world on reset, party/guild visit modes.
  UNVERIFIED in game: the tint packet repainting already-rendered grass; reset (new world while the old one is loaded, owner teleport,
    old world unloading with its folder kept); SendHomeTask (go() from a world-thread task); the 5-tab page + the name box; arrival
    check + sweep for /tpa arrivals and the retired-world redirect; GuardHurt / GuardUseEntity / GuardDrop firing; NPC role names
    matching the Assets.zip file names.
  REVIEW FIXES (2026-09-24, same version, before any deploy):
  - Island files: read0 returns null when the file EXISTS but can't be read (3 tries; Files.notExists decides "absent"), never an
    empty Properties, so no read-modify-write can store a blank island over a real one (0.4.5 had this gap with less at stake). Every
    mutation (co-op, trust, ban, settings, grid, reset world switch, kit mark, migration) aborts on it and the player gets "can't be
    read / could not save - nothing was changed"; a failed write is reported the same way (0.5 said "+done" before). Startup never
    migrates or rewrites an unreadable file: it stays untouched, its first world name stays protected, SeenTick retries it every
    30 s. The settings cache keeps the last good copy; without one it holds a 'bad' placeholder (IslandSettings.bad, re-read after
    5 s) that go/visit/info/page/sweep/arrival/bridge functions refuse to act on (no creating a second island over it). Mutations
    migrate a still-0.4.x file in memory first, so no write can store v=5 over 0.4.x build-rights members.
  - Locks: one monitor per island file key (lockOf) instead of the class-wide IslandStore monitor; a synchronized block holds one
    call of a *0 method. Retry sleeps now stall only that island. Lock order PUB -> key monitor; no key section takes another lock.
  - Creation / reset futures: BuildDone (whenComplete) clears that run's CREATING / RESETTING marks on failure and tells the player;
    go() also clears its mark when spawnInstance throws. setWorldName reads patiently (10 x 50 ms) and returns -1 when the file can't
    be read or written: nothing changes (a reset is abandoned, the owner is told, the new world stays registered as a retired world).
  - Starter kit: nothing is added unless the whole kit fits (canAddItemStacks); a full chest keeps the kit for a later arrival and
    tells the owner; every item's remainder is logged by id and quantity. KITDONE stops a second kit when the kit=1 write failed.
  - /island reload (admin, see Commands). Config perm.otherProfileStrict (see the tightening note). config.properties defaults are
    re-read from the build values on reload (a removed key goes back to its default).

0.4.5: starter-kit hotfix - the chest is read through world.getChunkStore().getStore() (was the entity store: 'Incorrect store
  for entity reference' on every new island). Notes in tools/islands_0_4_5_patch.py. KEPT in 0.5 (FillTask.starterKit).
0.4.4: per-profile storage (tools/PROFILES-CONTRACT.md). One island per profile (SkyyProfiles). Without SkyyProfiles everything
  behaves exactly like 0.4.3 (pkey(u) = uuid = profile 1). Island file = islands/<pkey>.properties; profile 1 = <uuid>.properties;
  a new profile's island is skyy-island-<pkey>. WORLD_OWNER holds the owner's profile KEY; CREATING is keyed by pkey; IslandBuild
  captures the key when /island starts. Bridge island:<uuid> publishes are serialized (IslandStore.PUB; lock order PUB -> IslandStore).
  GuardUse (UseBlockEvent$Pre, ICancellableEcsEvent). WARNED pruned with SEEN at logout.
0.4.3: commands for everyone (setPermissionGroups hytale:Adventurer) + real subcommands (addSubCommand) + positional forms; optional
  args are flags only. The old flag form (/island --action visit --player X) still works.
0.4.2: black grass fix - template WorldGen "Tint": "#5b9e28"; FillTask tints chunk (0,0); arrivals re-tint loaded chunks within 2.
0.4.1: ONE registered system per class - GuardSystem is a base class with one subclass per event.
0.4: starter kit in the island chest once per island (kit=1): WorldChunk.getBlockComponentEntity -> ItemContainerBlock, world thread.
0.3.1 / 0.3: /island visit open to everyone; island protection (DamageBlock/BreakBlock/PlaceBlock/InteractivelyPickupItem).
0.2.2: relight of chunks (-1..1)^2 4 s after every /island (ChunkLightingManager.invalidateLightInChunk); Env_Default_Void.
0.2.1: PlayerReadyEvent fires on EVERY world switch - login routing only on the first ready per online session (SEEN).
0.2: /sethub + fixed-point /hub + login routing to the hub + island world registry (tools/islands_0_2_patch.py).
0.1: InstancesPlugin.spawnInstance("SkyyIsland", "skyy-island-<key>", from, ret) copies the template (Void world gen, Global spawn
  8.5,129,8.5, RemovalConditions WorldEmpty, DeleteOnRemove=false); IslandBuild places a 12x12 island in chunk (0,0);
  teleportPlayerToLoadingInstance; later /island: Universe.getWorld(name) if loaded, else Universe.addWorld(name).
Run:   python build_skyyislands_0.5.py            -> SkyyIslands/SkyyIslands-0.5.jar  (never --deploy: tools/deploy_set.py deploys)
"""
import sys, os, json, re, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.5.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.islands"
T = {
    "JP":    "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":   "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":    "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":   "com.hypixel.hytale.component.Ref",
    "ST":    "com.hypixel.hytale.component.Store",
    "CA":    "com.hypixel.hytale.component.ComponentAccessor",
    "UNI":   "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":   "com.hypixel.hytale.server.core.universe.world.World",
    "WCFG":  "com.hypixel.hytale.server.core.universe.world.WorldConfig",
    "WCH":   "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "BCH":   "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
    "CHU":   "com.hypixel.hytale.math.util.ChunkUtil",
    "APC":   "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":   "com.hypixel.hytale.server.core.command.system.CommandContext",
    "MSG":   "com.hypixel.hytale.server.core.Message",
    "ATY":   "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "OA":    "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg",
    "RA":    "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "LOG":   "com.hypixel.hytale.logger.HytaleLogger",
    "INS":   "com.hypixel.hytale.builtin.instances.InstancesPlugin",
    "TRF":   "com.hypixel.hytale.math.vector.Transform",
    "TC":    "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "TP":    "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "EES":   "com.hypixel.hytale.component.system.EntityEventSystem",
    "ICB":   "com.hypixel.hytale.server.core.modules.block.components.ItemContainerBlock",
    "IS":    "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IC":    "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "ISTX":  "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "ACH":   "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":    "com.hypixel.hytale.component.CommandBuffer",
    "EV":    "com.hypixel.hytale.component.system.EcsEvent",
    "ICE":   "com.hypixel.hytale.component.system.ICancellableEcsEvent",
    "QRY":   "com.hypixel.hytale.component.query.Query",
    "ARCH":  "com.hypixel.hytale.component.Archetype",
    "SG":    "com.hypixel.hytale.component.SystemGroup",
    "EST":   "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "DBE":   "com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent",
    "BBE":   "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
    "PBE":   "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent",
    "PUE":   "com.hypixel.hytale.server.core.event.events.ecs.InteractivelyPickupItemEvent",
    "PRE":   "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "UBE":   "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent",
    "UBPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre",
    "UEE":   "com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent",
    "UEPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre",
    "DIE":   "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest",
    "DES":   "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMG":   "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC":  "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT":  "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DMOD":  "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "NPC":   "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "BTY":   "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BENCH": "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench",
    "BENT":  "com.hypixel.hytale.protocol.BenchType",
    "FARM":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.farming.FarmingData",
    "GATH":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering",
    "ITY":   "com.hypixel.hytale.protocol.InteractionType",
    "HSV":   "com.hypixel.hytale.server.core.HytaleServer",
    "R3F":   "com.hypixel.hytale.math.vector.Rotation3f",
    "PLA":   "com.hypixel.hytale.server.core.entity.entities.Player",
    "PAGE":  "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE":  "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":   "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":   "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":   "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":    "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PGE":   "com.hypixel.hytale.protocol.packets.interface_.Page",
    "NMT":   "com.hypixel.hytale.server.core.NameMatching",
    "PKG":   PKG,
    "VERSION": VERSION,
    # vanilla /help /who /ping permission-group line: every player in the default group may run the command
    "ADV":   'setPermissionGroups(new String[] { "hytale:Adventurer" });',
}
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
WNH = "com.hypixel.hytale.server.core.universe.world.WorldNotificationHandler"

for c, m in ((T["INS"], "spawnInstance"), (T["INS"], "teleportPlayerToLoadingInstance"), (T["INS"], "teleportPlayerToInstance"),
             (T["INS"], "doesInstanceAssetExist"), (T["UNI"], "isWorldLoadable"), (T["UNI"], "addWorld"), (T["UNI"], "getDefaultWorld"),
             (T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"), (T["UNI"], "getPlayerByUsername"), (T["UNI"], "getWorld"),
             (T["WLD"], "getChunkAsync"), (T["WLD"], "getNotificationHandler"), (T["WLD"], "getPlayerRefs"), (T["WLD"], "getWorldConfig"),
             (T["WLD"], "getChunkIfLoaded"), (T["WLD"], "execute"), (T["WLD"], "getChunkStore"), (T["WLD"], "getChunkLighting"),
             (WNH, "updateChunkTints"), (WNH, "updateChunk"), (T["WCH"], "getIndex"), (T["WCH"], "setBlock"), (T["WCH"], "getBlockChunk"),
             (T["WCH"], "getBlockComponentEntity"), (T["BCH"], "setTint"), (T["BCH"], "getTint"),
             (T["WCFG"], "setPvpEnabled"), (T["WCFG"], "isPvpEnabled"), (T["WCFG"], "setSpawningNPC"), (T["WCFG"], "isSpawningNPC"),
             (T["WCFG"], "markChanged"), (T["WCFG"], "getSpawnProvider"),
             (T["CHU"], "indexChunk"), (T["TC"], "getTransform"), (T["TP"], "createForPlayer"), (T["CTX"], "provided"), (T["CTX"], "get"),
             (T["EST"], "getWorld"), (T["PR"], "hasPermission"), (T["PR"], "getWorldUuid"), (T["PR"], "getReference"),
             (T["PR"], "getUsername"), (T["PR"], "isValid"), (T["ICB"], "getItemContainer"), (T["IC"], "addItemStack"),
             (T["IC"], "canAddItemStacks"), (T["ISTX"], "succeeded"), (T["ISTX"], "getRemainder"), (T["IS"], "isEmpty"),
             (T["IS"], "getQuantity"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (T["PRE"], "getPlayerRef"), (T["MSG"], "raw"), (T["MSG"], "color"),
             (AC, "requirePermission"), (AC, "setPermissionGroups"), (AC, "addSubCommand"), (AC, "withRequiredArg"),
             (AC, "withOptionalArg"), (AC, "addAliases"), (T["ATY"], "PLAYER_REF"), (T["ATY"], "STRING"),
             (T["UBPRE"], "setCancelled"), (T["UBE"], "getBlockType"), (T["UBE"], "getInteractionType"), (T["DBE"], "getBlockType"),
             (T["BBE"], "getBlockType"), (T["UEE"], "getTargetEntity"), (T["UEPRE"], "setCancelled"), (T["DIE"], "setCancelled"),
             (T["ICE"], "setCancelled"), (T["DMG"], "getSource"), (T["DMG"], "setCancelled"), (T["DMG"], "isCancelled"),
             (T["DENT"], "getRef"), (T["DMOD"], "get"), (T["DMOD"], "getFilterDamageGroup"), (T["QRY"], "any"),
             (T["NPC"], "getComponentType"), (T["NPC"], "getRoleName"), (T["ACH"], "getComponent"), (T["ACH"], "getReferenceTo"),
             (T["CB"], "getComponent"), (T["BTY"], "getInteractions"), (T["BTY"], "getBench"), (T["BTY"], "getBeds"),
             (T["BTY"], "getSeats"), (T["BTY"], "getFarming"), (T["BTY"], "getGathering"), (T["BTY"], "isDoor"),
             (T["BENCH"], "getType"), (T["BENT"], "Processing"), (T["FARM"], "getStages"), (T["GATH"], "getHarvest"),
             (T["ITY"], "Primary"), (T["ITY"], "Use"), (T["ITY"], "Secondary"),
             (T["PAGE"], "rebuild"), (PGM, "openCustomPage"), (PGM, "setPage"), (T["PGE"], "None"), (T["PLA"], "getPageManager"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["EVD"], "append"),
             (T["BT"], "Activating"), (T["BT"], "Validating"), (T["LIFE"], "CanDismiss"),
             (T["NMT"], "EXACT_IGNORE_CASE"), (T["NMT"], "STARTS_WITH_IGNORE_CASE"),
             ("com.hypixel.hytale.component.system.ISystem", "getGroup"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry")):
    B.probe(pool, c, m)

# ---- build-time data: farm animal NPC roles from Assets.zip (read-only, in memory). Fallback = the list read on 2026-09-24.
ANIMALS_FALLBACK = ("Bison,Bison_Calf,Boar,Boar_Piglet,Bunny,Camel,Camel_Calf,Chicken,Chicken_Chick,Chicken_Desert,Chicken_Desert_Chick,"
                    "Cow,Cow_Calf,Frog_Blue,Frog_Green,Frog_Orange,Gecko,Goat,Goat_Kid,Horse,Horse_Foal,Meerkat,Mouflon,Mouflon_Lamb,Mouse,"
                    "Pig,Pig_Piglet,Pig_Wild,Pig_Wild_Piglet,Rabbit,Ram,Ram_Lamb,Sheep,Sheep_Lamb,Skrill,Skrill_Chick,Squirrel,Tamed_Bison,"
                    "Tamed_Bison_Calf,Tamed_Boar,Tamed_Boar_Piglet,Tamed_Bunny,Tamed_Camel,Tamed_Camel_Calf,Tamed_Chicken,Tamed_Chicken_Chick,"
                    "Tamed_Chicken_Desert,Tamed_Chicken_Desert_Chick,Tamed_Cow,Tamed_Cow_Calf,Tamed_Goat,Tamed_Goat_Kid,Tamed_Horse,"
                    "Tamed_Horse_Foal,Tamed_Mosshorn,Tamed_Mosshorn_Plain,Tamed_Mouflon,Tamed_Mouflon_Lamb,Tamed_Pig,Tamed_Pig_Piglet,"
                    "Tamed_Pig_Wild,Tamed_Pig_Wild_Piglet,Tamed_Rabbit,Tamed_Ram,Tamed_Ram_Lamb,Tamed_Sheep,Tamed_Sheep_Lamb,Tamed_Skrill,"
                    "Tamed_Skrill_Chick,Tamed_Turkey,Tamed_Turkey_Chick,Tamed_Warthog,Tamed_Warthog_Piglet,Turkey,Turkey_Chick,Warthog,"
                    "Warthog_Piglet")
ASSETS_ZIP = os.path.join(os.path.dirname(os.path.dirname(B.SERVER_JAR)), "Assets.zip")
try:
    with zipfile.ZipFile(ASSETS_ZIP) as az:
        _roles = sorted(set(os.path.basename(n)[:-5] for n in az.namelist()
                            if n.endswith(".json") and (n.startswith("Server/NPC/Roles/Creature/Livestock/") or n.startswith("Server/NPC/Roles/Creature/Critter/"))))
    ANIMALS_CSV = ",".join(r for r in _roles if re.match(r"^[A-Za-z0-9_]+$", r))
    print("farm animal roles from Assets.zip:", len(_roles))
except Exception as e:
    ANIMALS_CSV = ANIMALS_FALLBACK
    print("WARNING: could not read Assets.zip (%s) - using the built-in animal list" % e)
if not ANIMALS_CSV:
    ANIMALS_CSV = ANIMALS_FALLBACK

FLAGS = [  # id, grid label, hint, default minimum role (spec 3.2)
    ("build", "Place blocks", "Building", "trusted"),
    ("break", "Break blocks", "Hitting and breaking blocks", "trusted"),
    ("containers", "Chests and barrels", "Opening them - and breaking them", "member"),
    ("doors", "Doors and gates", "Doors, trapdoors, fence gates", "visitor"),
    ("crafting", "Crafting benches", "Workbench, Armory, Builders bench...", "trusted"),
    ("processing", "Furnaces", "Furnace, campfire, tannery, salvager", "member"),
    ("beds", "Beds", "Sleeping, setting your respawn", "member"),
    ("seats", "Chairs and benches", "Sitting down", "visitor"),
    ("harvest", "Crops and plants", "F-harvest and hitting crops", "member"),
    ("animals", "Farm animals", "Hurting and using farm animals", "member"),
    ("mobs", "Hostile mobs", "Fighting monsters", "visitor"),
    ("pickup", "Pick up items", "Picking up dropped items", "trusted"),
    ("drop", "Drop items", "Throwing items on the ground", "trusted"),
    ("other", "Other blocks", "Lanterns, coffins, teleporters...", "trusted"),
]
RANKS = ["visitor", "trusted", "member", "admin", "owner"]
CFG_TEXT = "\n".join([
    "# SkyyIslands %s - server settings (admins). Written with the defaults on first run; edit, then /island reload (or restart)." % VERSION,
    "# Island permission defaults = the lowest role that may do each thing on an island whose owner never changed that flag.",
    "# Roles: visitor < trusted < member < admin < owner.",
] + ["defaults.perm.%s=%s" % (f[0], f[3]) for f in FLAGS] + [
    "# Who may visit a new island: public | friends (co-op members + trusted) | closed (co-op members only)",
    "defaults.visit.mode=public",
    "defaults.visit.limit=5",
    "# 1 = the owner and members get a chat line when someone visits",
    "defaults.visit.notify=1",
    "# the highest visitor limit an owner can pick",
    "visit.limitMax=10",
    "# co-op size INCLUDING the owner",
    "coop.maxPlayers=5",
    "# may island admins invite co-op members? (only the owner kicks, promotes, disbands and resets)",
    "coop.adminsInvite=false",
    "invite.seconds=60",
    "trusted.max=20",
    "bans.max=100",
    "# an expelled player may not come back for this many seconds",
    "expel.cooldownSeconds=60",
    "reset.cooldownHours=24",
    "reset.confirmSeconds=20",
    "# grass colour fix after a re-tint: tints (send the new colours) | chunk (resend the whole chunk) | off",
    "tint.resend=tints",
    "# extra NPC role names that count as farm animals (pet mods), comma separated",
    "animals.extra=",
    "# true = a player who has a role on an island through ANOTHER of their profiles may only use doors and seats and fight mobs there",
    "# (no items can move between their profiles through that island, whatever the island grid allows visitors). false = spec 10.2:",
    "# only dropping items is refused for them, everything else follows the island's Permissions grid like any visitor.",
    "perm.otherProfileStrict=true",
    "",
])
CFG_JAVA = CFG_TEXT.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
assert "@" not in CFG_TEXT and "%%" not in CFG_TEXT

TOKEN = re.compile(r"@([A-Z][A-Z0-9]{1,6})@")


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


def K(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup) if isinstance(sup, str) else sup) if sup is not None else pool.makeClass(PKG + "." + name)


st_  = K("IslandStore")
cfg  = K("IslandCfg")
sets = K("IslandSettings")
perm = K("IslandPerms")
tint = K("TintFix")
fill = K("FillTask")
cfl  = K("ChunkFill")
reln = K("RelightNow")
relt = K("RelightTask")
bld  = K("IslandBuild")
bdn  = K("BuildDone")
icmd = K("IslandCmd", T["APC"])
hcmd = K("HubCmd", T["APC"])
shub = K("SetHubCmd", T["APC"])
shom = K("SendHomeTask")
shtk = K("SendHubTask")
evac = K("EvacTask")
swp  = K("SweepTask")
arr  = K("ArrivalTask")
ard  = K("ArrivalDispatch")
coop = K("IslandCoop")
pfn  = K("PermFn")
rfn  = K("RoleFn")
ofn  = K("OwnerFn")
cfn  = K("CoopFn")
guard = K("GuardSystem", T["EES"])
g1 = K("GuardDamage", guard)
g2 = K("GuardBreak", guard)
g3 = K("GuardPlace", guard)
g4 = K("GuardPickup", guard)
g5 = K("GuardUse", guard)
g6 = K("GuardDrop", guard)
g7 = K("GuardUseEntity", guard)
ghurt = K("GuardHurt", T["DES"])
page = K("IslandMenuPage", T["PAGE"])
rout = K("RouteTask")
disp = K("RouteDispatch")
rdy  = K("IslandReady")
seen = K("SeenTick")
pl   = K("SkyyIslandsPlugin", T["JP"])
ALL = [st_, cfg, sets, perm, tint, fill, cfl, reln, relt, bld, bdn, icmd, hcmd, shub, shom, shtk, evac, swp, arr, ard, coop, pfn, rfn, ofn,
       cfn, guard, g1, g2, g3, g4, g5, g6, g7, ghurt, page, rout, disp, rdy, seen]

# =====================================================================================================================
# IslandStore part 1: state, logging, bridge, profile keys, comma lists, chat
# =====================================================================================================================
for f in ("public static java.nio.file.Path DIR;",
          "public static @LOG@ LOG;",
          "public static final java.util.concurrent.ConcurrentHashMap CREATING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap WORLD_OWNER = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();",
          # 0.5: parsed island settings per owner key (refreshed by every write), member key -> owner key, invites, confirms ...
          "public static final java.util.concurrent.ConcurrentHashMap SETTINGS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap MEMBER_OF = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap INVITES = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap CONFIRM = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap EXPELLED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap PINGED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap EXPELLING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap RESETTING = new java.util.concurrent.ConcurrentHashMap();",
          # 0.5 review fixes: one monitor per island file key, keys whose file could not be read (-> retry time), kits placed this session
          "public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BAD = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap KITDONE = new java.util.concurrent.ConcurrentHashMap();",
          "public static int MIGRATED;",
          'public static final String READ_ERR = "-The island file can\'t be read right now - nothing was changed. Try again in a moment.";',
          'public static final String FILE_ERR = "-Could not save the island file right now - nothing was changed. Try again in a moment.";',
          "public static long ISLAND_EPOCH;",
          # serializes island:<uuid> publishes (read + bridge write inside, so the last publish always carries the newest state)
          "public static final Object PUB = new Object();",
          "public static final java.util.Set ISLAND_WORLDS = java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap());",
          "public static java.nio.file.Path HUB_FILE;",
          "public static volatile String HUB_WORLD;",
          "public static volatile double[] HUB_POS;",
          "public static volatile float[] HUB_ROT;"):
    F(st_, f)
M(st_, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyIslands] " + msg); } catch (Throwable t) { }
}""")
M(st_, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyIslands] " + msg); } catch (Throwable t) { }
}""")
M(st_, r"""
public static java.util.Map bridge() {
  java.util.Properties sp = System.getProperties();
  Object o = sp.get("skyy.bridge");
  if (o == null) {
    sp.putIfAbsent("skyy.bridge", new java.util.concurrent.ConcurrentHashMap());
    o = sp.get("skyy.bridge");
  }
  return (java.util.Map) o;
}""")
# tools/PROFILES-CONTRACT.md helper, verbatim: storage key of the player's ACTIVE profile (uuid = profile 1 = no SkyyProfiles)
M(st_, r"""
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
# profile key -> owning player (a key is "<uuid>" or "<uuid>-p<N>"; UUID.toString() is always 36 chars)
M(st_, r"""
public static java.util.UUID ownerUuid(String key) {
  if (key == null || key.length() < 36) return null;
  try { return java.util.UUID.fromString(key.substring(0, 36)); } catch (Throwable t) { return null; }
}""")
# /island info label: ONLY the display name SkyyProfiles publishes (profile:name:<uuid>); empty without one
M(st_, r"""
public static String profileLabel(java.util.UUID u) {
  try {
    Object n = bridge().get("profile:name:" + u);
    if (!(n instanceof String)) return "";
    String raw = ((String) n).trim();
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < raw.length() && sb.length() < 32; i++) {
      char c = raw.charAt(i);
      if (c >= ' ' && c != 127) sb.append(c);
    }
    String nm = sb.toString().trim();
    if (nm.length() > 0) return " (profile " + nm + ")";
  } catch (Throwable t) { }
  return "";
}""")
# display name of ANY profile key from SkyyProfiles' profile:list:<uuid> ("1:Apple:Archer,2:Banana:Mage"); "profile N" fallback
M(st_, r"""
public static String profileNameOf(String key) {
  String id = "1";
  if (key != null && key.length() > 38 && key.charAt(36) == '-' && key.charAt(37) == 'p') id = key.substring(38);
  try {
    java.util.UUID u = ownerUuid(key);
    Object l = u == null ? null : bridge().get("profile:list:" + u);
    if (l instanceof String) {
      String[] a = ((String) l).split(",");
      for (int i = 0; i < a.length; i++) {
        String[] p = a[i].split(":");
        if (p.length >= 2 && p[0].trim().equals(id) && p[1].trim().length() > 0) return p[1].trim();
      }
    }
  } catch (Throwable t) { }
  return "profile " + id;
}""")
M(st_, r"""
public static String trim(String s) {
  if (s == null) return null;
  String t = s.trim();
  return t.length() == 0 ? null : t;
}""")
# ---- comma lists (members/admins/trusted/banned): no spaces, no empties, no duplicates
M(st_, r"""
public static String[] split(String csv) {
  if (csv == null || csv.trim().length() == 0) return new String[0];
  String[] a = csv.split(",");
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < a.length; i++) {
    String x = a[i].trim();
    if (x.length() > 0 && !l.contains(x)) l.add(x);
  }
  String[] r = new String[l.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) l.get(i);
  return r;
}""")
M(st_, r"""
public static String join(String[] a) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length; i++) {
    if (a[i] == null || a[i].length() == 0) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(a[i]);
  }
  return sb.toString();
}""")
M(st_, r"""
public static String norm(String csv) {
  return join(split(csv));
}""")
M(st_, r"""
public static boolean contains(String csv, String item) {
  if (csv == null || item == null || item.length() == 0) return false;
  return ("," + csv + ",").indexOf("," + item + ",") >= 0;
}""")
M(st_, r"""
public static int count(String csv) {
  return split(csv).length;
}""")
M(st_, r"""
public static String csvAdd(String csv, String item) {
  String n = norm(csv);
  if (contains(n, item)) return n;
  return n.length() == 0 ? item : n + "," + item;
}""")
M(st_, r"""
public static String csvRemove(String csv, String item) {
  String[] a = split(csv);
  for (int i = 0; i < a.length; i++) if (a[i].equals(item)) a[i] = "";
  return join(a);
}""")
# first entry of a list that belongs to this player (its first 36 chars = the UUID), optionally skipping one key
M(st_, r"""
public static String uuidEntryExcept(String csv, String uuidStr, String except) {
  String[] a = split(csv);
  for (int i = 0; i < a.length; i++) {
    if (a[i].length() >= 36 && a[i].substring(0, 36).equalsIgnoreCase(uuidStr) && (except == null || !a[i].equals(except))) return a[i];
  }
  return null;
}""")
M(st_, r"""
public static String uuidEntry(String csv, String uuidStr) {
  return uuidEntryExcept(csv, uuidStr, null);
}""")
# ---- chat: results are "+..." success (green), "-..." refused (orange), "=..." info / confirm prompt (blue) - SkyyGuilds pattern
M(st_, r"""
public static void say(@PR@ p, String text, String color) {
  if (p == null || text == null) return;
  try { p.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")
M(st_, r"""
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#cfe3ff";
}""")
M(st_, r"""
public static String textOf(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")
M(st_, r"""
public static void tell(@PR@ p, String res) {
  if (res == null || res.length() == 0) return;
  say(p, "[Island] " + textOf(res), colorOf(res));
}""")
M(st_, r"""
public static @PR@ online(java.util.UUID u) {
  if (u == null) return null;
  try {
    @PR@ p = @UNI@.get().getPlayer(u);
    return (p != null && p.isValid()) ? p : null;
  } catch (Throwable t) { return null; }
}""")
# a LOADED world by name, or null (never throws: the page and chat helpers must not fail on a missing Universe)
M(st_, r"""
public static @WLD@ loadedWorld(String name) {
  if (name == null) return null;
  try {
    @WLD@ w = @UNI@.get().getWorld(name);
    return (w != null && w.isAlive()) ? w : null;
  } catch (Throwable t) { return null; }
}""")
M(st_, r"""
public static void sayU(java.util.UUID u, String text, String color) {
  say(online(u), text, color);
}""")
# a typed player name from the page TextField: letters, digits and underscores only (Hytale usernames), max 32 (SkyyParty 0.1.3)
M(st_, r"""
public static String cleanName(String s) {
  if (s == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length() && sb.length() < 32; i++) {
    char c = s.charAt(i);
    if (Character.isLetterOrDigit(c) || c == '_') sb.append(c);
  }
  return sb.toString();
}""")
# exact name (ignoring case) first, then prefix - SkyyParty 0.1.3 findOnline (verified in the beta)
M(st_, r"""
public static @PR@ findOnline(String name) {
  if (name == null || name.length() == 0) return null;
  @PR@ p = null;
  try { p = @UNI@.get().getPlayerByUsername(name, @NMT@.EXACT_IGNORE_CASE); } catch (Throwable t) { p = null; }
  if (p == null) {
    try { p = @UNI@.get().getPlayerByUsername(name, @NMT@.STARTS_WITH_IGNORE_CASE); } catch (Throwable t) { p = null; }
  }
  return (p != null && p.isValid()) ? p : null;
}""")

# =====================================================================================================================
# IslandCfg: Skyy_SkyyIslands/config.properties (spec 9.2, slice A keys)
# =====================================================================================================================
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static final String[] FLAG_IDS = new String[] { %s };" % ", ".join('"%s"' % f[0] for f in FLAGS))
F(cfg, "public static final int[] DEF_PERM = new int[] { %s };" % ", ".join(str(RANKS.index(f[3])) for f in FLAGS))
F(cfg, "public static final int[] BUILD_PERM = new int[] { %s };" % ", ".join(str(RANKS.index(f[3])) for f in FLAGS))
for f in ("public static int DEF_MODE = 0;", "public static int DEF_LIMIT = 5;", "public static boolean DEF_NOTIFY = true;",
          "public static int LIMIT_MAX = 10;", "public static int COOP_MAX = 5;", "public static boolean ADMINS_INVITE = false;",
          "public static int INVITE_SECONDS = 60;", "public static int TRUSTED_MAX = 20;", "public static int BANS_MAX = 100;",
          "public static int EXPEL_SECONDS = 60;", "public static long RESET_HOURS = 24L;", "public static int RESET_CONFIRM = 20;",
          "public static int TINT_RESEND = 1;",
          # 0.5 review: perm.otherProfileStrict (default true) = someone with a role here on ANOTHER profile only gets doors, seats, mobs
          "public static boolean STRICT_OTHER = true;",
          "public static String BASE_ANIMALS = \"\";",
          "public static volatile java.util.HashSet ANIMALS = new java.util.HashSet();"):
    F(cfg, f)
M(cfg, r"""
public static int rankOf(String v, int def) {
  if (v == null) return def;
  String s = v.trim().toLowerCase();
  if (s.equals("visitor") || s.equals("everyone") || s.equals("0")) return 0;
  if (s.equals("trusted") || s.equals("1")) return 1;
  if (s.equals("member") || s.equals("members") || s.equals("2")) return 2;
  if (s.equals("admin") || s.equals("admins") || s.equals("3")) return 3;
  if (s.equals("owner") || s.equals("4")) return 4;
  return def;
}""")
M(cfg, r"""
public static String rankName(int r) {
  if (r <= 0) return "visitor";
  if (r == 1) return "trusted";
  if (r == 2) return "member";
  if (r == 3) return "admin";
  return "owner";
}""")
M(cfg, r"""
public static int modeOf(String v, int def) {
  if (v == null) return def;
  String s = v.trim().toLowerCase();
  if (s.equals("public") || s.equals("0")) return 0;
  if (s.equals("friends") || s.equals("1")) return 1;
  if (s.equals("closed") || s.equals("2")) return 2;
  return def;
}""")
M(cfg, r"""
public static String modeName(int m) {
  if (m == 1) return "friends";
  if (m == 2) return "closed";
  return "public";
}""")
M(cfg, r"""
public static String modeLabel(int m) {
  if (m == 1) return "Friends only (co-op members + trusted)";
  if (m == 2) return "Closed (co-op members only)";
  return "Public (anyone)";
}""")
M(cfg, r"""
public static int flagIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < FLAG_IDS.length; i++) if (FLAG_IDS[i].equalsIgnoreCase(id.trim())) return i;
  return -1;
}""")
M(cfg, r"""
public static boolean isAnimal(String role) {
  return role != null && ANIMALS.contains(role);
}""")
M(cfg, r"""
public static long lng(java.util.Properties p, String key, long def, long min, long max) {
  long v = def;
  try { String s = p.getProperty(key); if (s != null && s.trim().length() > 0) v = Long.parseLong(s.trim()); } catch (Throwable t) { v = def; }
  if (v < min) v = min;
  if (v > max) v = max;
  return v;
}""")
M(cfg, r"""
public static void load(String animals) {
  BASE_ANIMALS = animals == null ? "" : animals;
  java.util.HashSet an = new java.util.HashSet();
  String[] a = animals == null ? new String[0] : animals.split(",");
  for (int i = 0; i < a.length; i++) if (a[i].trim().length() > 0) an.add(a[i].trim());
  try {
    if (FILE != null) {
      if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
        java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
        java.nio.file.Files.write(FILE, "%%CFGTEXT%%".getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
      }
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      for (int i = 0; i < FLAG_IDS.length; i++) {
        int r = rankOf(p.getProperty("defaults.perm." + FLAG_IDS[i]), BUILD_PERM[i]);
        if (r < 0) r = 0;
        if (r > 4) r = 4;
        DEF_PERM[i] = r;
      }
      DEF_MODE = modeOf(p.getProperty("defaults.visit.mode"), 0);
      LIMIT_MAX = (int) lng(p, "visit.limitMax", 10L, 1L, 100L);
      DEF_LIMIT = (int) lng(p, "defaults.visit.limit", 5L, 1L, (long) LIMIT_MAX);
      DEF_NOTIFY = !"0".equals(String.valueOf(p.getProperty("defaults.visit.notify", "1")).trim());
      COOP_MAX = (int) lng(p, "coop.maxPlayers", 5L, 1L, 50L);
      ADMINS_INVITE = "true".equalsIgnoreCase(String.valueOf(p.getProperty("coop.adminsInvite", "false")).trim());
      INVITE_SECONDS = (int) lng(p, "invite.seconds", 60L, 10L, 3600L);
      TRUSTED_MAX = (int) lng(p, "trusted.max", 20L, 0L, 500L);
      BANS_MAX = (int) lng(p, "bans.max", 100L, 0L, 1000L);
      EXPEL_SECONDS = (int) lng(p, "expel.cooldownSeconds", 60L, 0L, 86400L);
      RESET_HOURS = lng(p, "reset.cooldownHours", 24L, 0L, 8760L);
      RESET_CONFIRM = (int) lng(p, "reset.confirmSeconds", 20L, 5L, 300L);
      String tr = String.valueOf(p.getProperty("tint.resend", "tints")).trim().toLowerCase();
      TINT_RESEND = tr.equals("off") ? 0 : (tr.equals("chunk") ? 2 : 1);
      STRICT_OTHER = !"false".equalsIgnoreCase(String.valueOf(p.getProperty("perm.otherProfileStrict", "true")).trim());
      String ex = p.getProperty("animals.extra", "");
      String[] e = ex == null ? new String[0] : ex.split(",");
      for (int i = 0; i < e.length; i++) if (e[i].trim().length() > 0) an.add(e[i].trim());
    }
  } catch (Throwable t) { @PKG@.IslandStore.warn("could not read config.properties (defaults used): " + t); }
  ANIMALS = an;
}""".replace("%%CFGTEXT%%", CFG_JAVA))

# =====================================================================================================================
# IslandSettings: one island file, parsed (immutable after parse - a change writes the file and replaces the cache entry)
# =====================================================================================================================
for f in ("public String key;", "public String world;", "public String prev;", "public String old;", "public String members;",
          "public String admins;", "public String trusted;", "public String banned;", "public int[] perm;", "public int mode;",
          "public int prevMode;", "public int limit;", "public boolean notify;", "public boolean pvp;", "public boolean spawning;",
          "public String ownerName;", "public int resets;", "public long resetAt;", "public java.util.HashMap names;",
          "public java.util.HashMap since;", "public boolean note05;",
          # 0.5 review fix: true = the island file exists but could not be read (placeholder: no world, no lists; never acted on)
          "public boolean bad;", "public long badAt;"):
    F(sets, f)
C(sets, "public IslandSettings() { }")
M(sets, r"""
public static int num(String s, int def) {
  try { return s == null ? def : Integer.parseInt(s.trim()); } catch (Throwable t) { return def; }
}""")
M(sets, r"""
public static long lnum(String s, long def) {
  try { return s == null ? def : Long.parseLong(s.trim()); } catch (Throwable t) { return def; }
}""")
M(sets, r"""
public static @PKG@.IslandSettings parse(String key, java.util.Properties p) {
  @PKG@.IslandSettings s = new @PKG@.IslandSettings();
  s.key = key;
  s.world = @PKG@.IslandStore.trim(p.getProperty("world"));
  s.prev = @PKG@.IslandStore.trim(p.getProperty("world.prev"));
  s.old = @PKG@.IslandStore.norm(p.getProperty("world.old", ""));
  s.members = @PKG@.IslandStore.norm(p.getProperty("members", ""));
  String ad = @PKG@.IslandStore.norm(p.getProperty("admins", ""));
  String[] aa = @PKG@.IslandStore.split(ad);
  for (int i = 0; i < aa.length; i++) if (!@PKG@.IslandStore.contains(s.members, aa[i])) aa[i] = "";
  s.admins = @PKG@.IslandStore.join(aa);
  s.trusted = @PKG@.IslandStore.norm(p.getProperty("trusted", ""));
  s.banned = @PKG@.IslandStore.norm(p.getProperty("banned", ""));
  s.perm = new int[@PKG@.IslandCfg.FLAG_IDS.length];
  for (int i = 0; i < s.perm.length; i++) {
    int r = @PKG@.IslandCfg.rankOf(p.getProperty("perm." + @PKG@.IslandCfg.FLAG_IDS[i]), @PKG@.IslandCfg.DEF_PERM[i]);
    if (r < 0) r = 0;
    if (r > 4) r = 4;
    s.perm[i] = r;
  }
  s.mode = @PKG@.IslandCfg.modeOf(p.getProperty("visit.mode"), @PKG@.IslandCfg.DEF_MODE);
  s.prevMode = @PKG@.IslandCfg.modeOf(p.getProperty("visit.prev"), 0);
  int lim = num(p.getProperty("visit.limit"), @PKG@.IslandCfg.DEF_LIMIT);
  if (lim < 1) lim = 1;
  if (lim > @PKG@.IslandCfg.LIMIT_MAX) lim = @PKG@.IslandCfg.LIMIT_MAX;
  s.limit = lim;
  String nt = p.getProperty("visit.notify");
  s.notify = nt == null ? @PKG@.IslandCfg.DEF_NOTIFY : "1".equals(nt.trim());
  s.pvp = "1".equals(String.valueOf(p.getProperty("pvp", "0")).trim());
  s.spawning = "1".equals(String.valueOf(p.getProperty("spawning", "0")).trim());
  s.ownerName = @PKG@.IslandStore.trim(p.getProperty("ownerName"));
  s.resets = num(p.getProperty("resets"), 0);
  s.resetAt = lnum(p.getProperty("resetAt"), 0L);
  s.note05 = "1".equals(p.getProperty("note05"));
  s.names = new java.util.HashMap();
  s.since = new java.util.HashMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("name.") && k.length() > 5) s.names.put(k.substring(5), p.getProperty(k));
    else if (k.startsWith("coopSince.") && k.length() > 10) s.since.put(k.substring(10), p.getProperty(k));
  }
  return s;
}""")

# =====================================================================================================================
# IslandStore part 2: files, settings cache, registry, migration, home island, publish, mutations
# 0.5 review fix: every island file has its OWN monitor (lockOf(key)); a synchronized block holds exactly one call of a *0 method,
# which must only run under that key's monitor. read0 returns null when the file EXISTS but can't be read (never an empty
# Properties), so no read-modify-write can ever store a blank island over a real one; every mutation reports a file error instead.
# =====================================================================================================================
M(st_, r"""
public static Object lockOf(String key) {
  String k = key == null ? "" : key;
  Object o = LOCKS.get(k);
  if (o != null) return o;
  Object n = new Object();
  o = LOCKS.putIfAbsent(k, n);
  return o == null ? n : o;
}""")
# under lockOf(key). Empty Properties = the file does not exist; null = it exists (or can't be told apart) and could not be read
M(st_, r"""
public static java.util.Properties read0(String key, int tries, long waitMs) {
  java.nio.file.Path f = DIR.resolve(key + ".properties");
  Throwable last = null;
  for (int i = 0; i < tries; i++) {
    try {
      java.util.Properties p = new java.util.Properties();
      if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { p.load(in); } finally { in.close(); }
      } else if (!java.nio.file.Files.notExists(f, new java.nio.file.LinkOption[0])) {
        throw new java.io.IOException("can't tell whether the file exists");
      }
      return p;
    } catch (Throwable t) {
      last = t;
      if (i + 1 < tries) { try { Thread.sleep(waitMs); } catch (Throwable ie) { } }
    }
  }
  if (!BAD.containsKey(key)) warn("could not read island file " + key + " (" + tries + " tries): " + last + " - nothing was changed");
  return null;
}""")
# under lockOf(key). Marks the file as 0.5 format (v=5) and refreshes the settings cache; on failure the cache entry is dropped so
# the next read comes from disk. tmp + move with 5 x 20 ms retries (Windows sharing violations). true = written.
M(st_, r"""
public static boolean write0(String key, java.util.Properties p) {
  try {
    p.setProperty("v", "5");
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(key + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyIslands"); } finally { out.close(); }
    java.nio.file.Path dst = DIR.resolve(key + ".properties");
    Throwable last = null;
    for (int i = 0; i < 5; i++) {
      try {
        java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
        last = null;
        break;
      } catch (java.nio.file.FileSystemException e) {
        last = e;
        if (i < 4) { try { Thread.sleep(20L); } catch (Throwable ie) { } }
      }
    }
    if (last != null) throw last;
    SETTINGS.put(key, @PKG@.IslandSettings.parse(key, p));
    BAD.remove(key);
    return true;
  } catch (Throwable t) {
    SETTINGS.remove(key);
    warn("could not write island file " + key + ": " + t);
    return false;
  }
}""")
M(st_, r"""
public static boolean needsMigration(java.util.Properties p) {
  return p != null && p.size() > 0 && !"5".equals(String.valueOf(p.getProperty("v", "")).trim());
}""")
# spec 6 in memory: a 0.4.x file (no v=5) -> <key>.properties.v4bak (once), every members= entry (0.4.x build rights) -> trusted=
M(st_, r"""
public static int migrateProps(String key, java.util.Properties p) {
  java.nio.file.Path f = DIR.resolve(key + ".properties");
  java.nio.file.Path bak = DIR.resolve(key + ".properties.v4bak");
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]) && !java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0])) java.nio.file.Files.copy(f, bak, new java.nio.file.CopyOption[0]);
  } catch (Throwable t) { warn("could not back up " + key + " before migrating: " + t); }
  String[] m = split(p.getProperty("members", ""));
  String tr = norm(p.getProperty("trusted", ""));
  int n = 0;
  for (int i = 0; i < m.length; i++) {
    if (m[i].equals(key)) continue;
    tr = csvAdd(tr, m[i]);
    n++;
  }
  p.setProperty("trusted", tr);
  p.setProperty("members", "");
  p.remove("admins");
  if (n > 0) p.setProperty("note05", "1");
  p.setProperty("v", "5");
  return n;
}""")
# under lockOf(key): the file for a change (migrated first if it is still 0.4.x, so no write ever stores v=5 over 0.4.x members), or null
M(st_, r"""
public static java.util.Properties readForUpdate0(String key) {
  java.util.Properties p = read0(key, 3, 20L);
  if (needsMigration(p)) {
    int n = migrateProps(key, p);
    info("migrated " + n + " build-rights entries to Trusted in " + key + " (before a change)");
  }
  return p;
}""")
# island registry + MEMBER_OF index from one island file (first owner wins, as at startup)
M(st_, r"""
public static void register(String key, java.util.Properties p) {
  String w = trim(p.getProperty("world"));
  if (w != null) { ISLAND_WORLDS.add(w); WORLD_OWNER.put(w, key); }
  String[] old = split(p.getProperty("world.old", ""));
  for (int j = 0; j < old.length; j++) { ISLAND_WORLDS.add(old[j]); WORLD_OWNER.put(old[j], key); }
  String[] m = split(p.getProperty("members", ""));
  for (int j = 0; j < m.length; j++) {
    if (m[j].equals(key)) continue;
    Object prev = MEMBER_OF.putIfAbsent(m[j], key);
    if (prev != null && !prev.equals(key)) warn("profile " + m[j] + " is a co-op member of two islands (" + prev + " and " + key + ") - " + prev + " wins");
  }
}""")
# under lockOf(key): an unreadable file keeps its last good cached copy; without one the cache holds a 'bad' placeholder (no world, no
# lists) that callers refuse to act on and that is re-read after 5 s. The key goes on the BAD list (SeenTick retries it every 30 s).
M(st_, r"""
public static @PKG@.IslandSettings badSettings0(String key) {
  long now = System.currentTimeMillis();
  BAD.put(key, Long.valueOf(now));
  Object o = SETTINGS.get(key);
  if (o instanceof @PKG@.IslandSettings && !((@PKG@.IslandSettings) o).bad) return (@PKG@.IslandSettings) o;
  @PKG@.IslandSettings s = @PKG@.IslandSettings.parse(key, new java.util.Properties());
  s.bad = true;
  s.badAt = now;
  SETTINGS.put(key, s);
  return s;
}""")
# under lockOf(key): read + migrate (written back) + register + cache one island file; null = unreadable (nothing changed)
M(st_, r"""
public static @PKG@.IslandSettings loadOne0(String key, int tries) {
  java.util.Properties p = read0(key, tries, 20L);
  if (p == null) return null;
  if (needsMigration(p)) {
    int n = migrateProps(key, p);
    MIGRATED = MIGRATED + 1;
    if (write0(key, p)) info("migrated " + n + " build-rights entries to Trusted in " + key);
    else warn("migrated " + key + " in memory only (the file could not be written) - it is migrated again before its next change");
  }
  register(key, p);
  @PKG@.IslandSettings s = @PKG@.IslandSettings.parse(key, p);
  SETTINGS.put(key, s);
  BAD.remove(key);
  return s;
}""")
M(st_, r"""
public static @PKG@.IslandSettings settingsLoad0(String key) {
  Object o = SETTINGS.get(key);
  if (o instanceof @PKG@.IslandSettings) {
    @PKG@.IslandSettings c = (@PKG@.IslandSettings) o;
    if (!c.bad || System.currentTimeMillis() - c.badAt < 5000L) return c;
  }
  @PKG@.IslandSettings s = loadOne0(key, 2);
  if (s != null) return s;
  return badSettings0(key);
}""")
M(st_, r"""
public static @PKG@.IslandSettings settingsLoad(String key) {
  @PKG@.IslandSettings s = null;
  synchronized (lockOf(key)) { s = settingsLoad0(key); }
  return s;
}""")
M(st_, r"""
public static @PKG@.IslandSettings settings(String key) {
  if (key == null) return @PKG@.IslandSettings.parse("", new java.util.Properties());
  Object o = SETTINGS.get(key);
  if (o instanceof @PKG@.IslandSettings) {
    @PKG@.IslandSettings c = (@PKG@.IslandSettings) o;
    if (!c.bad || System.currentTimeMillis() - c.badAt < 5000L) return c;
  }
  return settingsLoad(key);
}""")
M(st_, r"""
public static boolean reloadOne0(String key) {
  if (loadOne0(key, 3) != null) return true;
  badSettings0(key);
  return false;
}""")
M(st_, r"""
public static boolean reloadOne(String key) {
  boolean ok = false;
  synchronized (lockOf(key)) { ok = reloadOne0(key); }
  return ok;
}""")
M(st_, r"""
public static synchronized void loadHub() {
  try {
    if (HUB_FILE == null || !java.nio.file.Files.exists(HUB_FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(HUB_FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    String w = p.getProperty("world");
    if (w == null || w.trim().isEmpty()) return;
    HUB_WORLD = w.trim();
    HUB_POS = new double[] { Double.parseDouble(p.getProperty("x", "0")), Double.parseDouble(p.getProperty("y", "100")), Double.parseDouble(p.getProperty("z", "0")) };
    HUB_ROT = new float[] { Float.parseFloat(p.getProperty("rx", "0")), Float.parseFloat(p.getProperty("ry", "0")), Float.parseFloat(p.getProperty("rz", "0")) };
  } catch (Throwable t) { warn("could not load hub.properties: " + t); }
}""")
M(st_, r"""
public static synchronized void saveHub(String world, double x, double y, double z, float rx, float ry, float rz) {
  HUB_WORLD = world; HUB_POS = new double[] { x, y, z }; HUB_ROT = new float[] { rx, ry, rz };
  try {
    java.nio.file.Files.createDirectories(HUB_FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.util.Properties p = new java.util.Properties();
    p.setProperty("world", world);
    p.setProperty("x", String.valueOf(x)); p.setProperty("y", String.valueOf(y)); p.setProperty("z", String.valueOf(z));
    p.setProperty("rx", String.valueOf(rx)); p.setProperty("ry", String.valueOf(ry)); p.setProperty("rz", String.valueOf(rz));
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(HUB_FILE, new java.nio.file.OpenOption[0]);
    try { p.store(out, "SkyyIslands hub point (/sethub)"); } finally { out.close(); }
  } catch (Throwable t) { warn("could not save hub.properties: " + t); }
}""")
# island file keys on disk (islands/<key>.properties with a valid owner UUID), in name order
M(st_, r"""
public static java.util.ArrayList islandKeys() {
  java.util.ArrayList keys = new java.util.ArrayList();
  try {
    if (DIR == null || !java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) return keys;
    java.util.ArrayList names = new java.util.ArrayList();
    java.util.stream.Stream st = java.nio.file.Files.list(DIR);
    try {
      java.util.Iterator it = st.iterator();
      while (it.hasNext()) {
        java.nio.file.Path f = (java.nio.file.Path) it.next();
        String n = f.getFileName().toString();
        if (n.endsWith(".properties")) names.add(n);
      }
    } finally { st.close(); }
    java.util.Collections.sort(names);
    for (int i = 0; i < names.size(); i++) {
      String n = (String) names.get(i);
      String key = n.substring(0, n.length() - 11);
      if (ownerUuid(key) != null) keys.add(key);
    }
  } catch (Throwable t) { warn("could not scan island files: " + t); }
  return keys;
}""")
# registry + migration + MEMBER_OF at plugin setup (before any player can connect). An unreadable file is left untouched (never
# migrated or rewritten); its first world name stays protected and SeenTick retries the file every 30 s.
M(st_, r"""
public static void loadIslandWorlds() {
  java.util.ArrayList keys = islandKeys();
  for (int i = 0; i < keys.size(); i++) {
    String key = (String) keys.get(i);
    try {
      if (!reloadOne(key)) {
        String guess = "skyy-island-" + key;
        ISLAND_WORLDS.add(guess);
        WORLD_OWNER.putIfAbsent(guess, key);
        warn("island file " + key + " could not be read at startup - left untouched (retried every 30 s and on /island reload; world " + guess + " stays protected meanwhile)");
      }
    } catch (Throwable t) { warn("could not load island file " + key + ": " + t); }
  }
  if (MIGRATED > 0) info("migrated " + MIGRATED + " island file(s) to the 0.5 format (backups: islands/*.properties.v4bak)");
}""")
# kit state: KITDONE remembers a kit placed this session even when its file write failed (no second kit); unreadable = 'given' for now
M(st_, r"""
public static boolean kitGiven0(String key) {
  if (KITDONE.containsKey(key)) return true;
  java.util.Properties p = read0(key, 3, 20L);
  if (p == null) return true;
  return "1".equals(p.getProperty("kit"));
}""")
M(st_, r"""
public static boolean kitGiven(String key) {
  boolean r = true;
  synchronized (lockOf(key)) { r = kitGiven0(key); }
  return r;
}""")
M(st_, r"""
public static boolean setKitGiven0(String key) {
  KITDONE.put(key, Boolean.TRUE);
  java.util.Properties p = readForUpdate0(key);
  if (p == null) { warn("starter kit placed for " + key + " but its island file could not be read - remembered until the next restart"); return false; }
  p.setProperty("kit", "1");
  return write0(key, p);
}""")
M(st_, r"""
public static boolean setKitGiven(String key) {
  boolean r = false;
  synchronized (lockOf(key)) { r = setKitGiven0(key); }
  return r;
}""")
M(st_, r"""
public static String ownerOf(String worldName) {
  return worldName == null ? null : (String) WORLD_OWNER.get(worldName);
}""")
M(st_, r"""
public static boolean isIslandWorld(String name) {
  return name != null && ISLAND_WORLDS.contains(name);
}""")
M(st_, r"""
public static String worldName(String key) {
  return settings(key).world;
}""")
# a reset backup world: registered to an owner whose CURRENT world is another one
M(st_, r"""
public static boolean isRetired(String wn) {
  String o = ownerOf(wn);
  if (o == null) return false;
  String cur = settings(o).world;
  return cur != null && !cur.equals(wn);
}""")
# spec 1.3: the island the ACTIVE profile is a co-op member of (checked against the owner's file), else the profile's own key.
# While the owner's file can't be read the membership is trusted (the caller then refuses with 'can't be read' instead of sending the
# member to their dormant own island or creating one).
M(st_, r"""
public static String homeKey(java.util.UUID u) {
  String k = pkey(u);
  Object o = MEMBER_OF.get(k);
  if (o instanceof String) {
    String ok = (String) o;
    if (!ok.equals(k)) {
      @PKG@.IslandSettings s = settings(ok);
      if (s.bad || contains(s.members, k)) return ok;
    }
  }
  return k;
}""")
M(st_, r"""
public static String ownerDisplay(String ownerKey, @PKG@.IslandSettings s) {
  String n = s == null ? null : s.ownerName;
  if (n == null || n.length() == 0) {
    @PR@ p = online(ownerUuid(ownerKey));
    if (p != null) n = p.getUsername();
  }
  return (n == null || n.length() == 0) ? "Unknown" : n;
}""")
M(st_, r"""
public static String nameOf(@PKG@.IslandSettings s, String key) {
  if (key == null) return "?";
  Object n = s == null ? null : s.names.get(key);
  if (n instanceof String && ((String) n).length() > 0) return (String) n;
  if (s != null && key.equals(s.key)) return ownerDisplay(key, s);
  @PR@ p = online(ownerUuid(key));
  if (p != null) return p.getUsername();
  return key.length() > 8 ? "Player " + key.substring(0, 8) : key;
}""")
# bridge island:<uuid> = world of the player's HOME island (UUID-keyed, contract rule 3), serialized under PUB (0.4.4); lock order
# PUB -> island key monitor (settings may load a file). A 'bad' home publishes nothing new (the last value stays).
M(st_, r"""
public static void publishNow(java.util.UUID u) {
  try {
    @PKG@.IslandSettings s = settings(homeKey(u));
    if (s.bad) return;
    String w = s.world;
    java.util.Map b = bridge();
    if (w == null) b.remove("island:" + u); else b.put("island:" + u, w);
  } catch (Throwable t) { }
}""")
M(st_, r"""
public static void publish(java.util.UUID u) {
  if (u == null) return;
  synchronized (PUB) { publishNow(u); }
}""")
M(st_, r"""
public static synchronized void bump() {
  ISLAND_EPOCH = ISLAND_EPOCH + 1L;
  try { bridge().put("island:epoch", Long.valueOf(ISLAND_EPOCH)); } catch (Throwable t) { }
}""")
# SeenTick (every 30 s): files that could not be read get another try; success registers their worlds and members
M(st_, r"""
public static int retryBad() {
  int n = 0;
  java.util.ArrayList l = new java.util.ArrayList(BAD.keySet());
  for (int i = 0; i < l.size(); i++) {
    String key = (String) l.get(i);
    try {
      if (reloadOne(key)) { n++; info("island file " + key + " can be read again - loaded"); }
    } catch (Throwable t) { }
  }
  return n;
}""")
# /island reload: every island file again (hand edits), then MEMBER_OF rebuilt: entries the owner's file no longer lists are dropped,
# every listed member is added (first owner wins). An unreadable file keeps its last good copy. {files, read, unreadable}
M(st_, r"""
public static int[] reloadAll() {
  java.util.ArrayList keys = islandKeys();
  int ok = 0;
  int bad = 0;
  for (int i = 0; i < keys.size(); i++) {
    String key = (String) keys.get(i);
    try { if (reloadOne(key)) ok++; else bad++; } catch (Throwable t) { bad++; }
  }
  java.util.Iterator it = MEMBER_OF.keySet().iterator();
  while (it.hasNext()) {
    Object mk = it.next();
    Object ov = MEMBER_OF.get(mk);
    if (!(ov instanceof String)) continue;
    @PKG@.IslandSettings s = settings((String) ov);
    if (!s.bad && !contains(s.members, String.valueOf(mk))) MEMBER_OF.remove(mk, ov);
  }
  for (int i = 0; i < keys.size(); i++) {
    String key = (String) keys.get(i);
    @PKG@.IslandSettings s = settings(key);
    if (s.bad) continue;
    String[] m = split(s.members);
    for (int j = 0; j < m.length; j++) if (!m[j].equals(key)) MEMBER_OF.putIfAbsent(m[j], key);
  }
  return new int[] { keys.size(), ok, bad };
}""")
M(st_, r"""
public static String reloadText() {
  @PKG@.IslandCfg.load(@PKG@.IslandCfg.BASE_ANIMALS);
  int[] r = reloadAll();
  int n = 0;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p != null && p.isValid()) { publish(p.getUuid()); n++; }
    }
  } catch (Throwable t) { }
  bump();
  info("reload: config re-read, " + r[1] + " of " + r[0] + " island files re-read" + (r[2] > 0 ? ", " + r[2] + " UNREADABLE (their last good copy stays in use)" : "") + ", " + n + " online players republished");
  return (r[2] > 0 ? "-" : "+") + "Reloaded config.properties and " + r[1] + " of " + r[0] + " island files" + (r[2] > 0 ? " - " + r[2] + " could not be read (their last good copy stays in use - see the server log)" : "") + ". " + n + " online players updated.";
}""")
# world= switch; when a reset is pending for this key (RESETTING) the reset bookkeeping is written in the same step.
# 1 = switched (reset), 0 = switched, -1 = the island file could not be read or written: NOTHING changed (a reset is abandoned; the new
# world stays registered to the owner, so it is protected and counts as a retired world). Reads patiently (10 x 50 ms).
M(st_, r"""
public static int setWorldName0(String key, String name) {
  Object r = RESETTING.remove(key);
  ISLAND_WORLDS.add(name);
  WORLD_OWNER.put(name, key);
  java.util.Properties p = read0(key, 10, 50L);
  if (p == null) return -1;
  if (needsMigration(p)) migrateProps(key, p);
  boolean reset = false;
  String cur = trim(p.getProperty("world"));
  if (r instanceof Object[] && cur != null && !cur.equals(name)) {
    Object[] a = (Object[]) r;
    p.setProperty("world.prev", cur);
    p.setProperty("world.old", csvAdd(p.getProperty("world.old", ""), cur));
    p.setProperty("resets", String.valueOf(((Integer) a[1]).intValue()));
    p.setProperty("resetAt", String.valueOf(System.currentTimeMillis()));
    p.remove("kit");
    reset = true;
  }
  p.setProperty("world", name);
  p.setProperty("created", String.valueOf(System.currentTimeMillis()));
  if (!write0(key, p)) return -1;
  if (reset) KITDONE.remove(key);
  return reset ? 1 : 0;
}""")
M(st_, r"""
public static int setWorldName(String key, String name) {
  int r = -1;
  synchronized (lockOf(key)) { r = setWorldName0(key, name); }
  return r;
}""")
M(st_, r"""
public static boolean setProps0(String key, String[] ks, String[] vs) {
  java.util.Properties p = readForUpdate0(key);
  if (p == null) return false;
  for (int i = 0; i < ks.length; i++) {
    if (vs[i] == null) p.remove(ks[i]); else p.setProperty(ks[i], vs[i]);
  }
  return write0(key, p);
}""")
M(st_, r"""
public static boolean setProps(String key, String[] ks, String[] vs) {
  boolean r = false;
  synchronized (lockOf(key)) { r = setProps0(key, ks, vs); }
  return r;
}""")
M(st_, r"""
public static void setName(String ok, String entry, String name) {
  if (ok == null || entry == null || name == null || name.length() == 0) return;
  @PKG@.IslandSettings s = settings(ok);
  if (s.bad || s.world == null) return;
  if (name.equals(s.names.get(entry))) return;
  setProps(ok, new String[] { "name." + entry }, new String[] { name });
}""")
M(st_, r"""
public static void setOwnerName(String ok, String name) {
  if (ok == null || name == null || name.length() == 0) return;
  @PKG@.IslandSettings s = settings(ok);
  if (s.bad || s.world == null || name.equals(s.ownerName)) return;
  setProps(ok, new String[] { "ownerName" }, new String[] { name });
}""")
# 0 joined, 1 co-op full, 2 banned, 3 already a member, 4 island file error (nothing changed)
M(st_, r"""
public static int joinCoop0(String ok, String k, String name, int maxMembers) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 4;
  String m = norm(p.getProperty("members", ""));
  if (contains(m, k)) return 3;
  if (k.length() >= 36 && contains(norm(p.getProperty("banned", "")), k.substring(0, 36))) return 2;
  if (count(m) >= maxMembers) return 1;
  p.setProperty("members", csvAdd(m, k));
  p.setProperty("trusted", csvRemove(p.getProperty("trusted", ""), k));
  if (name != null && name.length() > 0) p.setProperty("name." + k, name);
  p.setProperty("coopSince." + k, String.valueOf(System.currentTimeMillis()));
  return write0(ok, p) ? 0 : 4;
}""")
M(st_, r"""
public static int joinCoop(String ok, String k, String name, int maxMembers) {
  int r = 4;
  synchronized (lockOf(ok)) { r = joinCoop0(ok, k, name, maxMembers); }
  return r;
}""")
# 0 left, 1 not a member, 2 island file error
M(st_, r"""
public static int leaveCoop0(String ok, String k) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 2;
  String m = norm(p.getProperty("members", ""));
  if (!contains(m, k)) return 1;
  p.setProperty("members", csvRemove(m, k));
  p.setProperty("admins", csvRemove(p.getProperty("admins", ""), k));
  p.remove("coopSince." + k);
  return write0(ok, p) ? 0 : 2;
}""")
M(st_, r"""
public static int leaveCoop(String ok, String k) {
  int r = 2;
  synchronized (lockOf(ok)) { r = leaveCoop0(ok, k); }
  return r;
}""")
# the removed members (comma list, maybe empty), or null = island file error (nothing changed)
M(st_, r"""
public static String clearCoop0(String ok) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return null;
  String m = norm(p.getProperty("members", ""));
  String[] a = split(m);
  for (int i = 0; i < a.length; i++) p.remove("coopSince." + a[i]);
  p.setProperty("members", "");
  p.setProperty("admins", "");
  return write0(ok, p) ? m : null;
}""")
M(st_, r"""
public static String clearCoop(String ok) {
  String r = null;
  synchronized (lockOf(ok)) { r = clearCoop0(ok); }
  return r;
}""")
# 0 done, 1 not a member, 2 no change, 3 island file error
M(st_, r"""
public static int setAdmin0(String ok, String k, boolean on) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 3;
  if (!contains(norm(p.getProperty("members", "")), k)) return 1;
  String ad = norm(p.getProperty("admins", ""));
  if (on == contains(ad, k)) return 2;
  p.setProperty("admins", on ? csvAdd(ad, k) : csvRemove(ad, k));
  return write0(ok, p) ? 0 : 3;
}""")
M(st_, r"""
public static int setAdmin(String ok, String k, boolean on) {
  int r = 3;
  synchronized (lockOf(ok)) { r = setAdmin0(ok, k, on); }
  return r;
}""")
# 0 added, 1 added and another profile's entry of the same player removed (moved), 2 already trusted, 3 list full, 4 file error
M(st_, r"""
public static int trustKey0(String ok, String k, String name, int max) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 4;
  String tr = norm(p.getProperty("trusted", ""));
  if (contains(tr, k)) return 2;
  String uu = k.length() >= 36 ? k.substring(0, 36) : k;
  int moved = 0;
  String other = uuidEntry(tr, uu);
  while (other != null) {
    tr = csvRemove(tr, other);
    moved = 1;
    other = uuidEntry(tr, uu);
  }
  if (moved == 0 && count(tr) >= max) return 3;
  p.setProperty("trusted", csvAdd(tr, k));
  if (name != null && name.length() > 0) p.setProperty("name." + k, name);
  return write0(ok, p) ? moved : 4;
}""")
M(st_, r"""
public static int trustKey(String ok, String k, String name, int max) {
  int r = 4;
  synchronized (lockOf(ok)) { r = trustKey0(ok, k, name, max); }
  return r;
}""")
# 0 removed, 1 not trusted, 2 island file error
M(st_, r"""
public static int untrustKey0(String ok, String k) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 2;
  String tr = norm(p.getProperty("trusted", ""));
  if (!contains(tr, k)) return 1;
  p.setProperty("trusted", csvRemove(tr, k));
  return write0(ok, p) ? 0 : 2;
}""")
M(st_, r"""
public static int untrustKey(String ok, String k) {
  int r = 2;
  synchronized (lockOf(ok)) { r = untrustKey0(ok, k); }
  return r;
}""")
# 0 banned, 1 already banned, 2 list full, 3 island file error. A ban removes every trusted entry of that player.
M(st_, r"""
public static int banUuid0(String ok, String uu, String name, int max) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 3;
  String b = norm(p.getProperty("banned", ""));
  if (contains(b, uu)) return 1;
  if (count(b) >= max) return 2;
  p.setProperty("banned", csvAdd(b, uu));
  String tr = norm(p.getProperty("trusted", ""));
  String e = uuidEntry(tr, uu);
  while (e != null) {
    tr = csvRemove(tr, e);
    e = uuidEntry(tr, uu);
  }
  p.setProperty("trusted", tr);
  if (name != null && name.length() > 0) p.setProperty("name." + uu, name);
  return write0(ok, p) ? 0 : 3;
}""")
M(st_, r"""
public static int banUuid(String ok, String uu, String name, int max) {
  int r = 3;
  synchronized (lockOf(ok)) { r = banUuid0(ok, uu, name, max); }
  return r;
}""")
# 0 unbanned, 1 not banned, 2 island file error
M(st_, r"""
public static int unbanUuid0(String ok, String uu) {
  java.util.Properties p = readForUpdate0(ok);
  if (p == null) return 2;
  String b = norm(p.getProperty("banned", ""));
  if (!contains(b, uu)) return 1;
  p.setProperty("banned", csvRemove(b, uu));
  return write0(ok, p) ? 0 : 2;
}""")
M(st_, r"""
public static int unbanUuid(String ok, String uu) {
  int r = 2;
  synchronized (lockOf(ok)) { r = unbanUuid0(ok, uu); }
  return r;
}""")
# chat line to the island's owner and co-op members who are online (any profile), minus up to two players
M(st_, r"""
public static void notifyIsland(String ok, String text, String color, java.util.UUID ex1, java.util.UUID ex2) {
  try {
    @PKG@.IslandSettings s = settings(ok);
    java.util.HashSet done = new java.util.HashSet();
    java.util.UUID ou = ownerUuid(ok);
    if (ou != null && !ou.equals(ex1) && !ou.equals(ex2)) { done.add(ou); sayU(ou, text, color); }
    String[] m = split(s.members);
    for (int i = 0; i < m.length; i++) {
      java.util.UUID mu = ownerUuid(m[i]);
      if (mu == null || mu.equals(ex1) || mu.equals(ex2) || done.contains(mu)) continue;
      done.add(mu);
      sayU(mu, text, color);
    }
  } catch (Throwable t) { }
}""")

# =====================================================================================================================
# IslandPerms: flag ids, block classifier (spec 3.3), roles, entry rule (spec 4.1), the guard decision + message
# =====================================================================================================================
for i, f in enumerate(FLAGS):
    F(perm, "public static final int %s = %d;" % (f[0].upper(), i))
F(perm, "public static final String[] LABELS = new String[] { %s };" % ", ".join('"%s"' % f[1] for f in FLAGS))
F(perm, "public static final String[] HINTS = new String[] { %s };" % ", ".join('"%s"' % f[2] for f in FLAGS))
F(perm, 'public static final String[] SHORT = new String[] { "place blocks", "break blocks", "chests", "doors", "crafting benches", '
        '"furnaces", "beds", "seats", "crops", "farm animals", "hostile mobs", "pick up items", "drop items", "other blocks" };')
M(perm, r"""
public static boolean isCrop(@BTY@ bt) {
  try {
    @FARM@ f = bt.getFarming();
    return f != null && f.getStages() != null;
  } catch (Throwable t) { return false; }
}""")
M(perm, r"""
public static boolean isHarvestPlant(@BTY@ bt) {
  if (isCrop(bt)) return true;
  try {
    @GATH@ g = bt.getGathering();
    return g != null && g.getHarvest() != null && String.valueOf(bt.getId()).startsWith("Plant_");
  } catch (Throwable t) { return false; }
}""")
# -1, CONTAINERS or PROCESSING (breaking these drops their contents -> needs break AND this flag)
M(perm, r"""
public static int containerKind(@BTY@ bt) {
  if (bt == null) return -1;
  try {
    @BENCH@ b = bt.getBench();
    if (b != null && b.getType() == @BENT@.Processing) return PROCESSING;
    java.util.Map im = bt.getInteractions();
    Object rid = im == null ? null : im.get(@ITY@.Use);
    if (rid != null && String.valueOf(rid).indexOf("Container") >= 0) return CONTAINERS;
  } catch (Throwable t) { }
  return -1;
}""")
M(perm, r"""
public static int breakFlag(@BTY@ bt) {
  if (bt == null) return BREAK;
  return isHarvestPlant(bt) ? HARVEST : BREAK;
}""")
# UseBlockEvent$Pre: first match wins (spec 3.3); Primary = hitting the block = breaking it
M(perm, r"""
public static int useFlag(@BTY@ bt, @ITY@ t) {
  if (bt == null || t == null) return -1;
  if (t == @ITY@.Primary) return breakFlag(bt);
  if (t != @ITY@.Use && t != @ITY@.Secondary) return -1;
  try {
    if (bt.isDoor()) return DOORS;
    java.util.Map im = bt.getInteractions();
    Object rid = im == null ? null : im.get(t);
    if (rid != null && String.valueOf(rid).indexOf("Door") >= 0) return DOORS;
    @BENCH@ b = bt.getBench();
    if (b != null) return b.getType() == @BENT@.Processing ? PROCESSING : CRAFTING;
    if (bt.getBeds() != null) return BEDS;
    if (isCrop(bt)) return HARVEST;
    if (containerKind(bt) == CONTAINERS) return CONTAINERS;
    if (bt.getSeats() != null) return SEATS;
    if (String.valueOf(bt.getId()).startsWith("Coop_")) return ANIMALS;
  } catch (Throwable x) { }
  return OTHER;
}""")
# rank on the island of owner key 'owner': 4 owner, 3 admin, 2 member, 1 trusted, 0 visitor, -1 banned (spec 3.6)
M(perm, r"""
public static int rank(String owner, java.util.UUID u, @PKG@.IslandSettings s) {
  if (owner == null || u == null || s == null) return 0;
  String k = @PKG@.IslandStore.pkey(u);
  if (k.equals(owner)) return 4;
  if (@PKG@.IslandStore.contains(s.banned, u.toString())) return -1;
  if (u.equals(@PKG@.IslandStore.ownerUuid(owner))) return 0;
  if (@PKG@.IslandStore.contains(s.members, k)) return @PKG@.IslandStore.contains(s.admins, k) ? 3 : 2;
  if (@PKG@.IslandStore.contains(s.trusted, k)) return 1;
  return 0;
}""")
M(perm, r"""
public static int rankU(String owner, java.util.UUID u) {
  return rank(owner, u, @PKG@.IslandStore.settings(owner));
}""")
# the key through which this player holds a role here on ANOTHER profile (the owner key for the owner), else null
M(perm, r"""
public static String otherProfileKey(String owner, java.util.UUID u, @PKG@.IslandSettings s) {
  if (owner == null || u == null || s == null) return null;
  String k = @PKG@.IslandStore.pkey(u);
  if (k.equals(owner)) return null;
  if (u.equals(@PKG@.IslandStore.ownerUuid(owner))) return owner;
  String us = u.toString();
  String e = @PKG@.IslandStore.uuidEntryExcept(s.members, us, k);
  if (e == null) e = @PKG@.IslandStore.uuidEntryExcept(s.trusted, us, k);
  return e;
}""")
M(perm, r"""
public static boolean isAdmin(@PR@ pr) {
  try { return pr != null && pr.hasPermission("skyyislands.admin"); } catch (Throwable t) { return false; }
}""")
M(perm, r"""
public static String whoText(int min) {
  if (min <= 0) return "everyone";
  if (min == 1) return "trusted players and up";
  if (min == 2) return "co-op members only";
  if (min == 3) return "island admins only";
  return "the owner only";
}""")
M(perm, r"""
public static String roleName(int r) {
  if (r < 0) return "Banned";
  if (r == 0) return "Visitor";
  if (r == 1) return "Trusted";
  if (r == 2) return "Member";
  if (r == 3) return "Admin";
  return "Owner";
}""")
M(perm, r"""
public static String roleColor(int r) {
  if (r < 0) return "#ff8080";
  if (r == 1) return "#8fc8ff";
  if (r == 2) return "#7fe07f";
  if (r == 3) return "#c9a0ff";
  if (r >= 4) return "#ffd060";
  return "#c8d4e0";
}""")
# the flag decision without side effects (guards, island:perm:fn). Someone holding a role here on ANOTHER profile may only use doors
# and seats and fight hostile mobs (no item can cross between their profiles through this island) - config perm.otherProfileStrict
# (default true, the 0.5 tightening). false = spec 10.2: only 'drop' is refused for them, the rest follows the grid like any visitor.
M(perm, r"""
public static boolean allowedFor(String owner, @PKG@.IslandSettings s, int rank, java.util.UUID u, int flag, int extra) {
  if (rank >= 4) return true;
  if (rank < 0) return false;
  if (flag < 0 || flag >= s.perm.length) return true;
  if (rank == 0 && flag != DOORS && flag != SEATS && flag != MOBS && (@PKG@.IslandCfg.STRICT_OTHER || flag == DROP) && otherProfileKey(owner, u, s) != null) return false;
  if (rank < s.perm[flag]) return false;
  if (extra >= 0 && extra < s.perm.length && rank < s.perm[extra]) return false;
  return true;
}""")
M(perm, r"""
public static String denyText(String owner, @PKG@.IslandSettings s, int rank, java.util.UUID u, int flag, int extra) {
  if (rank < 0) return "[Island] You are banned from this island.";
  String ok = rank == 0 ? otherProfileKey(owner, u, s) : null;
  if (ok != null) {
    if (ok.equals(owner)) return "[Island] This island belongs to another of your profiles (" + @PKG@.IslandStore.profileNameOf(owner) + ") - switch to that profile to use it.";
    String role = @PKG@.IslandStore.contains(s.members, ok) ? "a co-op member" : "trusted";
    return "[Island] You are " + role + " here on your profile " + @PKG@.IslandStore.profileNameOf(ok) + " - switch to it to use this island.";
  }
  int f = flag;
  if (flag >= 0 && flag < s.perm.length && rank >= s.perm[flag] && extra >= 0) f = extra;
  if (f < 0 || f >= LABELS.length) return "[Island] You can't do that on this island.";
  return "[Island] " + LABELS[f] + " on " + @PKG@.IslandStore.ownerDisplay(owner, s) + "'s island: " + whoText(s.perm[f]) + ".";
}""")
# guard entry point (world thread): true = allowed. Server admins always pass. Throttled message (3 s, WARNED).
M(perm, r"""
public static boolean allow(@WLD@ w, @PR@ pr, int flag, int extra) {
  String owner = @PKG@.IslandStore.ownerOf(w.getName());
  if (owner == null) return true;
  java.util.UUID u = pr.getUuid();
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(owner);
  int rank = rank(owner, u, s);
  if (allowedFor(owner, s, rank, u, flag, extra)) return true;
  if (isAdmin(pr)) return true;
  Long last = (Long) @PKG@.IslandStore.WARNED.get(u);
  long now = System.currentTimeMillis();
  if (last == null || now - last.longValue() > 3000L) {
    @PKG@.IslandStore.WARNED.put(u, Long.valueOf(now));
    @PKG@.IslandStore.say(pr, denyText(owner, s, rank, u, flag, extra), "#ff9d6b");
  }
  return false;
}""")
# visitors (rank 0, not server admins) in a loaded island world; World.getPlayerRefs is a concurrent view (any thread)
M(perm, r"""
public static int visitorCount(@WLD@ w, String owner, @PKG@.IslandSettings s, java.util.UUID except) {
  int n = 0;
  if (w == null) return 0;
  try {
    java.util.Iterator it = w.getPlayerRefs().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null || !p.isValid()) continue;
      java.util.UUID pu = p.getUuid();
      if (pu == null || pu.equals(except)) continue;
      if (rank(owner, pu, s) != 0) continue;
      if (isAdmin(p)) continue;
      n++;
    }
  } catch (Throwable t) { }
  return n;
}""")
# spec 4.1 entry rule: null = may be on the island, else the reason. Callers let server admins through first.
M(perm, r"""
public static String mayEnter(String owner, @PKG@.IslandSettings s, int rank, java.util.UUID u, @WLD@ w, boolean checkLimit) {
  if (rank >= 2) return null;
  if (rank < 0) return "you are banned there";
  if (s.mode == 2) return "it is closed to visitors (co-op members only)";
  if (s.mode == 1 && rank < 1) return "only co-op members and trusted players may visit";
  if (s.world != null) {
    Long t = (Long) @PKG@.IslandStore.EXPELLED.get(s.world + "|" + u);
    if (t != null && System.currentTimeMillis() - t.longValue() < @PKG@.IslandCfg.EXPEL_SECONDS * 1000L) return "you were sent off it less than " + @PKG@.IslandCfg.EXPEL_SECONDS + " s ago";
  }
  if (checkLimit && rank == 0 && w != null) {
    int n = visitorCount(w, owner, s, u);
    if (n >= s.limit) return "it is full (" + n + " / " + s.limit + " visitors)";
  }
  return null;
}""")
M(perm, r"""
public static String visitorAllowedText(@PKG@.IslandSettings s) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.perm.length && i < SHORT.length; i++) {
    if (s.perm[i] > 0) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(SHORT[i]);
  }
  return sb.length() == 0 ? "look around" : sb.toString();
}""")

# =====================================================================================================================
# TintFix (spec 5): re-tint wrong grass columns, then tell the clients (vanilla /chunk tint: updateChunkTints)
# =====================================================================================================================
F(tint, "public static final int GRASS = -10772952;")
M(tint, r"""
public static int tintChunk(@WCH@ chunk) {
  int n = 0;
  try {
    @BCH@ bc = chunk.getBlockChunk();
    if (bc == null) return 0;
    for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) {
      if (bc.getTint(x, z) != GRASS) { bc.setTint(x, z, GRASS); n++; }
    }
    if (n > 0) { bc.markNeedsSaving(); chunk.markNeedsSaving(); }
  } catch (Throwable t) { @PKG@.IslandStore.warn("tint failed: " + t); }
  return n;
}""")
M(tint, r"""
public static void resend(@WLD@ w, @WCH@ chunk) {
  int m = @PKG@.IslandCfg.TINT_RESEND;
  if (m == 0 || w == null || chunk == null) return;
  try {
    if (m == 2) w.getNotificationHandler().updateChunk(chunk.getIndex());
    else w.getNotificationHandler().updateChunkTints(chunk.getIndex());
  } catch (Throwable t) { @PKG@.IslandStore.warn("tint resend failed: " + t); }
}""")
# world thread: every loaded chunk within 2 chunks of (0,0); costs nothing when all columns are already green
M(tint, r"""
public static int fix(@WLD@ w) {
  int cols = 0;
  int chunks = 0;
  if (w == null) return 0;
  try {
    for (int tx = -2; tx <= 2; tx++) for (int tz = -2; tz <= 2; tz++) {
      @WCH@ c = w.getChunkIfLoaded(@CHU@.indexChunk(tx, tz));
      if (c == null) continue;
      int n = tintChunk(c);
      if (n > 0) { resend(w, c); cols += n; chunks++; }
    }
    if (cols > 0) @PKG@.IslandStore.info("re-tinted " + cols + " columns in " + chunks + " chunk(s) of " + w.getName() + (@PKG@.IslandCfg.TINT_RESEND == 0 ? " (resend off)" : (@PKG@.IslandCfg.TINT_RESEND == 2 ? " and resent those chunks" : " and sent the new tints to the clients")));
  } catch (Throwable t) { @PKG@.IslandStore.warn("tint fix failed: " + t); }
  return cols;
}""")

# =====================================================================================================================
# FillTask (world thread): the starter island in chunk (0,0) + starter kit (0.4.5, kit read through the CHUNK store)
# =====================================================================================================================
fill.addInterface(pool.get("java.lang.Runnable"))
F(fill, "public @WLD@ world;")
F(fill, "public @WCH@ chunk;")
F(fill, "public java.util.concurrent.CompletableFuture done;")
C(fill, "public FillTask(@WLD@ w, @WCH@ c, java.util.concurrent.CompletableFuture d) { this.world = w; this.chunk = c; this.done = d; }")
M(fill, r"""
public static int starterKit(@WLD@ world, @WCH@ chunk) {
  int n = 0;
  try {
    @REF@ ref = chunk.getBlockComponentEntity(4, 129, 4);
    if (ref == null || !ref.isValid()) { @PKG@.IslandStore.info("starter kit: no chest entity at 4,129,4 in " + world.getName()); return -1; }
    @ST@ store = world.getChunkStore().getStore();   // 0.4.5: block-component refs live in the CHUNK store
    Object comp = store.getComponent(ref, @ICB@.getComponentType());
    if (!(comp instanceof @ICB@)) { @PKG@.IslandStore.info("starter kit: chest has no ItemContainerBlock in " + world.getName()); return -1; }
    @IC@ c = ((@ICB@) comp).getItemContainer();
    if (c == null) return -1;
    String[] ids = new String[] { "Bench_WorkBench", "Wood_Oak_Trunk", "Soil_Dirt", "Ingredient_Stick", "Food_Bread", "Skyy_Accessory_Bag" };
    int[] qty = new int[] { 1, 10, 8, 8, 5, 1 };
    java.util.ArrayList all = new java.util.ArrayList();
    for (int i = 0; i < ids.length; i++) all.add(new @IS@(ids[i], qty[i]));
    // 0.5 review: the late-kit path fills a chest players may already use - nothing is added unless the WHOLE kit fits (-2 = kept
    // for a later arrival, the island is not marked); every item's leftover is still checked and logged by id and quantity
    boolean room = true;
    try { room = c.canAddItemStacks(all); } catch (Throwable t) { room = true; }
    if (!room) { @PKG@.IslandStore.info("starter kit: the chest in " + world.getName() + " has no room for the " + ids.length + " kit stacks - kept for a later arrival"); return -2; }
    int lost = 0;
    for (int i = 0; i < ids.length; i++) {
      try {
        @ISTX@ tx = c.addItemStack((@IS@) all.get(i));
        int left = qty[i];
        if (tx != null) {
          @IS@ rem = tx.getRemainder();
          int rq = (rem == null || rem.isEmpty()) ? 0 : rem.getQuantity();
          left = tx.succeeded() ? rq : (rq > 0 ? rq : qty[i]);
        }
        if (left < qty[i]) n++;
        if (left > 0) { lost += left; @PKG@.IslandStore.warn("starter kit in " + world.getName() + ": " + left + " x " + ids[i] + " did not fit in the chest"); }
      } catch (Throwable t) { @PKG@.IslandStore.warn("starter kit item " + ids[i] + " (" + qty[i] + ") not placed: " + t); }
    }
    @PKG@.IslandStore.info("starter kit placed in " + world.getName() + " (" + n + " of " + ids.length + " stacks" + (lost > 0 ? ", " + lost + " items did not fit - see the warnings" : "") + ")");
  } catch (Throwable t) { @PKG@.IslandStore.warn("starter kit failed: " + t); return -1; }
  return n;
}""")
M(fill, r"""
public int put(int x, int y, int z, String id) {
  try { return chunk.setBlock(x, y, z, id) ? 1 : 0; } catch (Throwable t) { return 0; }
}""")
M(fill, r"""
public void run() {
  int n = 0;
  try {
    if (chunk.getBlock(8, 128, 8) != 0) { done.complete(world); return; }
    for (int x = 2; x <= 13; x++) for (int z = 2; z <= 13; z++) {
      boolean corner = (x == 2 || x == 13) && (z == 2 || z == 13);
      if (corner) continue;
      n += put(x, 128, z, "Soil_Grass");
      n += put(x, 127, z, "Soil_Dirt");
      if (x >= 3 && x <= 12 && z >= 3 && z <= 12) n += put(x, 126, z, "Soil_Dirt");
      if (x >= 4 && x <= 11 && z >= 4 && z <= 11) n += put(x, 125, z, "Rock_Stone");
      if (x >= 6 && x <= 9 && z >= 6 && z <= 9) n += put(x, 124, z, "Rock_Stone");
    }
    for (int y = 129; y <= 133; y++) n += put(11, y, 11, "Wood_Oak_Trunk");
    for (int x = 9; x <= 13; x++) for (int z = 9; z <= 13; z++) for (int y = 132; y <= 134; y++) {
      if (x == 11 && z == 11 && y <= 133) continue;
      boolean edge = (x == 9 || x == 13) && (z == 9 || z == 13);
      if (edge || (y == 134 && (x == 9 || x == 13 || z == 9 || z == 13))) continue;
      n += put(x, y, z, "Plant_Leaves_Oak");
    }
    n += put(11, 135, 11, "Plant_Leaves_Oak");
    n += put(4, 129, 4, "Furniture_Crude_Chest_Small");
    if (@PKG@.TintFix.tintChunk(chunk) > 0) @PKG@.TintFix.resend(world, chunk);
    String owner = @PKG@.IslandStore.ownerOf(world.getName());
    if (starterKit(world, chunk) >= 0 && owner != null) @PKG@.IslandStore.setKitGiven(owner);
    @PKG@.IslandStore.info("starter island placed in " + world.getName() + " (" + n + " blocks)");
  } catch (Throwable t) { @PKG@.IslandStore.warn("island fill failed: " + t); }
  done.complete(world);
}""")

# ChunkFill: Function<WorldChunk, CompletableFuture<World>>
cfl.addInterface(pool.get("java.util.function.Function"))
F(cfl, "public @WLD@ world;")
C(cfl, "public ChunkFill(@WLD@ w) { this.world = w; }")
M(cfl, r"""
public Object apply(Object chunk) {
  java.util.concurrent.CompletableFuture done = new java.util.concurrent.CompletableFuture();
  try {
    if (chunk == null) { @PKG@.IslandStore.warn("chunk (0,0) did not load, island left empty"); done.complete(world); return done; }
    world.execute(new @PKG@.FillTask(world, (@WCH@) chunk, done));
  } catch (Throwable t) { @PKG@.IslandStore.warn("island fill dispatch failed: " + t); done.complete(world); }
  return done;
}""")

# RelightNow (world thread) / RelightTask (scheduler, 4 s after /island): relight + tint fix (now with resend) + late starter kit
reln.addInterface(pool.get("java.lang.Runnable"))
F(reln, "public @WLD@ world;")
C(reln, "public RelightNow(@WLD@ w) { this.world = w; }")
M(reln, r"""
public void run() {
  int ok = 0;
  try {
    for (int cx = -1; cx <= 1; cx++) for (int cz = -1; cz <= 1; cz++) {
      try { if (world.getChunkLighting().invalidateLightInChunk(world.getChunkStore(), cx, cz)) ok++; } catch (Throwable t) { }
    }
    int tinted = @PKG@.TintFix.fix(world);
    @PKG@.IslandStore.info("relight queued for " + world.getName() + " (" + ok + "/9 chunks)" + (tinted > 0 ? ", re-tinted " + tinted + " columns" : ""));
    String owner = @PKG@.IslandStore.ownerOf(world.getName());
    // 0.5: only the owner's CURRENT world gets a late kit (never a reset backup world)
    if (owner != null && world.getName().equals(@PKG@.IslandStore.worldName(owner)) && !@PKG@.IslandStore.kitGiven(owner)) {
      @WCH@ c0 = world.getChunkIfLoaded(@CHU@.indexChunk(0, 0));
      int kr = c0 == null ? -1 : @PKG@.FillTask.starterKit(world, c0);
      if (kr >= 0) @PKG@.IslandStore.setKitGiven(owner);
      else if (kr == -2) {
        java.util.UUID ou = @PKG@.IslandStore.ownerUuid(owner);
        @PR@ op = @PKG@.IslandStore.online(ou);
        if (op != null && owner.equals(@PKG@.IslandStore.pkey(ou))) @PKG@.IslandStore.say(op, "[Island] Your starter kit is waiting: make room for 6 stacks in the chest your island started with (next to the spawn point), then use /island again.", "#ffe08a");
      }
    }
  } catch (Throwable t) { @PKG@.IslandStore.warn("relight failed: " + t); }
}""")
relt.addInterface(pool.get("java.lang.Runnable"))
F(relt, "public String name;")
C(relt, "public RelightTask(String n) { this.name = n; }")
M(relt, r"""
public void run() {
  try {
    @WLD@ w = @UNI@.get().getWorld(this.name);
    if (w == null || !w.isAlive()) return;
    w.execute(new @PKG@.RelightNow(w));
  } catch (Throwable t) { }
}""")
M(relt, r"""
public static void schedule(String name) {
  if (name == null) return;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.RelightTask(name), 4000L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")

# /hub helper (static, used by expel / sweep / arrival / evac / login routing): Teleport component on the player's world thread
M(hcmd, r"""
public static boolean sendToHub(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ from) {
  @UNI@ uni = @UNI@.get();
  @WLD@ target = null; @TRF@ where = null;
  if (@PKG@.IslandStore.HUB_WORLD != null) {
    target = uni.getWorld(@PKG@.IslandStore.HUB_WORLD);
    if (target != null && target.isAlive()) {
      double[] p = @PKG@.IslandStore.HUB_POS; float[] r = @PKG@.IslandStore.HUB_ROT;
      where = new @TRF@(p[0], p[1], p[2], r[0], r[1], r[2]);
    } else { @PKG@.IslandStore.warn("hub world '" + @PKG@.IslandStore.HUB_WORLD + "' is not loaded, using default spawn"); target = null; }
  }
  if (target == null) {
    target = uni.getDefaultWorld();
    if (target == null) return false;
    where = target.getWorldConfig().getSpawnProvider().getSpawnPoint(target, pr.getUuid());
  }
  if (where == null) return false;
  ((@CA@) store).addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(target, where));
  return true;
}""")

# IslandBuild: Function<World, CompletableFuture<World>> (thenCompose) - also finishes a reset (spec 1.7)
bld.addInterface(pool.get("java.util.function.Function"))
F(bld, "public String owner;")
C(bld, "public IslandBuild(String key) { this.owner = key; }")
M(bld, r"""
public Object apply(Object w) {
  @WLD@ world = (@WLD@) w;
  @PKG@.IslandStore.CREATING.remove(owner);
  try {
    int res = @PKG@.IslandStore.setWorldName(owner, world.getName());
    boolean reset = res == 1;
    if (res < 0) {
      @PKG@.IslandStore.warn("island world " + world.getName() + " for " + owner + " was made but the island file could not be saved - the island file is unchanged (a reset is abandoned; the new world stays protected as a retired world)");
      @PKG@.IslandStore.sayU(@PKG@.IslandStore.ownerUuid(owner), "[Island] Could not save the island file just now, so your island was not changed - try again in a moment.", "#ff9d6b");
    } else {
      @PKG@.IslandStore.info("island world for " + owner + " = " + world.getName() + (reset ? " (reset - the old world stays on disk as a backup)" : ""));
      @PKG@.IslandStore.publish(@PKG@.IslandStore.ownerUuid(owner));
    }
    if (reset) {
      @PKG@.IslandStore.bump();
      @PKG@.IslandSettings s = @PKG@.IslandStore.settings(owner);
      String[] m = @PKG@.IslandStore.split(s.members);
      for (int i = 0; i < m.length; i++) {
        java.util.UUID mu = @PKG@.IslandStore.ownerUuid(m[i]);
        @PR@ mp = @PKG@.IslandStore.online(mu);
        if (mp == null) continue;
        @PKG@.IslandStore.publish(mu);
        @PKG@.IslandStore.say(mp, "[Island] The island was reset - /island takes you to the fresh island.", "#ffe08a");
      }
    }
    @PKG@.RelightTask.schedule(world.getName());
    return world.getChunkAsync(@CHU@.indexChunk(0, 0)).thenCompose(new @PKG@.ChunkFill(world));
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("island build failed: " + t);
    return java.util.concurrent.CompletableFuture.completedFuture(world);
  }
}""")

# BuildDone: BiConsumer on the creation / reset future (0.5 review). When the chain fails it clears THIS run's CREATING / RESETTING
# marks at once (remove(key, mark): a newer run keeps its own) and tells the player, instead of waiting out the 60 s window in go().
bdn.addInterface(pool.get("java.util.function.BiConsumer"))
F(bdn, "public String key;")
F(bdn, "public Object createdMark;")
F(bdn, "public Object resetMark;")
F(bdn, "public @PR@ pr;")
C(bdn, "public BuildDone(String k, Object c, Object r, @PR@ p) { this.key = k; this.createdMark = c; this.resetMark = r; this.pr = p; }")
M(bdn, r"""
public void accept(Object result, Object err) {
  if (err == null) return;
  try {
    boolean early = false;
    if (this.createdMark != null && @PKG@.IslandStore.CREATING.remove(this.key, this.createdMark)) early = true;
    if (this.resetMark != null && @PKG@.IslandStore.RESETTING.remove(this.key, this.resetMark)) early = true;
    boolean reset = this.resetMark != null;
    @PKG@.IslandStore.warn("island " + (reset ? "reset" : "creation") + " for " + this.key + " failed " + (early ? "before the new world was made" : "after the new world was made") + ": " + err);
    String text = "[Island] Your island could not be created just now - try /island again in a moment.";
    if (!early) text = "[Island] The island was built but the trip there failed - use /island to go there.";
    else if (reset) text = "[Island] The reset failed before a new island was made - your island is unchanged. You can try /island reset again.";
    if (this.pr != null && this.pr.isValid()) @PKG@.IslandStore.say(this.pr, text, "#ff9d6b");
  } catch (Throwable t) { }
}""")

# =====================================================================================================================
# IslandCmd statics: go (0.4.5 + member wording), goHome (home island rule), info, visit (entry check first)
# =====================================================================================================================
F(icmd, "public @OA@ actionArg;")
F(icmd, "public @OA@ targetArg;")
M(icmd, r"""
public static @TRF@ here(@ST@ store, @REF@ ref) {
  try {
    @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
    if (tc != null && tc.getTransform() != null) return new @TRF@(tc.getTransform());
  } catch (Throwable t) { }
  return null;
}""")
M(icmd, r"""
public static synchronized java.util.concurrent.CompletableFuture openSaved(String name) {
  @UNI@ uni = @UNI@.get();
  @WLD@ again = uni.getWorld(name);
  if (again != null) return java.util.concurrent.CompletableFuture.completedFuture(again);
  try {
    return uni.addWorld(name);
  } catch (IllegalArgumentException dup) {
    again = uni.getWorld(name);
    if (again != null) return java.util.concurrent.CompletableFuture.completedFuture(again);
    throw dup;
  }
}""")
M(icmd, r"""
public static void go(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ from, String owner, boolean own) {
  java.util.UUID u = pr.getUuid();
  @UNI@ uni = @UNI@.get();
  @PKG@.IslandSettings s0 = @PKG@.IslandStore.settings(owner);
  if (s0.bad) { @PKG@.IslandStore.tell(pr, @PKG@.IslandStore.READ_ERR); return; }
  String name = s0.world;
  @TRF@ ret = here(store, ref);
  Long mark = null;
  Object rs = @PKG@.IslandStore.RESETTING.get(owner);
  if (rs instanceof Object[]) {
    Object[] ra = (Object[]) rs;
    if (ra.length > 2 && ra[2] instanceof Long && System.currentTimeMillis() - ((Long) ra[2]).longValue() < 60000L) { pr.sendMessage(@MSG@.raw("[Island] That island is being reset right now - try again in a few seconds.")); return; }
    @PKG@.IslandStore.RESETTING.remove(owner, rs);
  }
  try {
    if (name != null) {
      if (own) @PKG@.IslandStore.setOwnerName(owner, pr.getUsername());
      @WLD@ w = uni.getWorld(name);
      if (w != null && w.isAlive()) {
        if (from == w) { pr.sendMessage(@MSG@.raw("[Island] You are already on this island.")); return; }
        pr.sendMessage(@MSG@.raw("[Island] Teleporting..."));
        @INS@.teleportPlayerToInstance(ref, (@CA@) store, w, ret);
        @PKG@.RelightTask.schedule(name);
        return;
      }
      if (uni.isWorldLoadable(name)) {
        pr.sendMessage(@MSG@.raw("[Island] Loading the island..."));
        java.util.concurrent.CompletableFuture f = openSaved(name);
        @INS@.teleportPlayerToLoadingInstance(ref, (@CA@) store, f, ret, null);
        @PKG@.RelightTask.schedule(name);
        return;
      }
      @PKG@.IslandStore.warn("island world '" + name + "' for " + owner + " is gone from disk");
    }
    if (!own) { pr.sendMessage(@MSG@.raw("[Island] That island is not available right now - ask its owner.")); return; }
    Long since = (Long) @PKG@.IslandStore.CREATING.get(owner);
    if (since != null && System.currentTimeMillis() - since.longValue() < 60000L) { pr.sendMessage(@MSG@.raw("[Island] Your island is still being created, hold on...")); return; }
    mark = Long.valueOf(System.currentTimeMillis());
    @PKG@.IslandStore.CREATING.put(owner, mark);
    pr.sendMessage(@MSG@.raw("[Island] Creating your island... (first time only)"));
    java.util.concurrent.CompletableFuture f = @INS@.get().spawnInstance("SkyyIsland", "skyy-island-" + owner, from, ret);
    f = f.thenCompose(new @PKG@.IslandBuild(owner));
    f = f.whenComplete(new @PKG@.BuildDone(owner, mark, null, pr));
    @INS@.teleportPlayerToLoadingInstance(ref, (@CA@) store, f, ret, null);
  } catch (Throwable t) {
    if (mark != null) @PKG@.IslandStore.CREATING.remove(owner, mark);
    @PKG@.IslandStore.warn("/island failed for " + u + ": " + t);
    pr.sendMessage(@MSG@.raw("[Island] Could not open the island: " + t.getMessage()));
  }
}""")
M(icmd, r"""
public static void goHome(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  go(store, ref, pr, world, hk, hk.equals(k));
}""")
M(icmd, r"""
public static void info(@PR@ pr, @WLD@ world) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  int rank = @PKG@.IslandPerms.rank(hk, u, s);
  String prof = @PKG@.IslandStore.profileLabel(u);
  if (s.bad) {
    @PKG@.IslandStore.tell(pr, @PKG@.IslandStore.READ_ERR);
  } else if (s.world == null) {
    @PKG@.IslandStore.say(pr, "[Island]" + prof + " No island yet - /island creates one.", "#cfe3ff");
  } else {
    boolean loaded = @PKG@.IslandStore.loadedWorld(s.world) != null;
    String who = hk.equals(k) ? "your own island (you are the Owner)" : @PKG@.IslandStore.ownerDisplay(hk, s) + "'s island (you are a co-op " + @PKG@.IslandPerms.roleName(rank) + ")";
    @PKG@.IslandStore.say(pr, "[Island]" + prof + " Home island: " + who, "#ffe08a");
    @PKG@.IslandStore.say(pr, "[Island] Co-op " + (1 + @PKG@.IslandStore.count(s.members)) + "/" + @PKG@.IslandCfg.COOP_MAX + " - trusted " + @PKG@.IslandStore.count(s.trusted) + " - banned " + @PKG@.IslandStore.count(s.banned) + " - visits " + @PKG@.IslandCfg.modeName(s.mode) + " (limit " + s.limit + ") - PvP " + (s.pvp ? "on" : "off") + " - world " + s.world + (loaded ? " (loaded)" : " (unloaded)"), "#cfe3ff");
    String[] m = @PKG@.IslandStore.split(s.members);
    if (m.length > 0) {
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < m.length; i++) {
        if (i > 0) sb.append(", ");
        sb.append(@PKG@.IslandStore.nameOf(s, m[i]));
        if (@PKG@.IslandStore.contains(s.admins, m[i])) sb.append(" (admin)");
      }
      @PKG@.IslandStore.say(pr, "[Island] Members: " + @PKG@.IslandStore.ownerDisplay(hk, s) + " (owner), " + sb.toString(), "#cfe3ff");
    }
  }
  @PKG@.IslandStore.say(pr, "[Island] You are in world: " + world.getName() + "   (/island menu for everything)", "#9fb8d0");
}""")
M(icmd, r"""
public static void visit(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world, @PR@ target) {
  if (target == null || !target.isValid()) { @PKG@.IslandStore.tell(pr, "-That player is not online."); return; }
  java.util.UUID tu = target.getUuid();
  String tk = @PKG@.IslandStore.homeKey(tu);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(tk);
  if (s.bad) { @PKG@.IslandStore.tell(pr, @PKG@.IslandStore.READ_ERR); return; }
  if (s.world == null) { @PKG@.IslandStore.tell(pr, "-" + target.getUsername() + " has no island yet."); return; }
  java.util.UUID u = pr.getUuid();
  int rank = @PKG@.IslandPerms.rank(tk, u, s);
  String on = @PKG@.IslandStore.ownerDisplay(tk, s);
  if (!@PKG@.IslandPerms.isAdmin(pr)) {
    if (@PKG@.IslandStore.isRetired(s.world)) { @PKG@.IslandStore.tell(pr, "-That island is being reset - try again in a moment."); return; }
    String why = @PKG@.IslandPerms.mayEnter(tk, s, rank, u, @PKG@.IslandStore.loadedWorld(s.world), true);
    if (why != null) { @PKG@.IslandStore.tell(pr, "-You can't visit " + on + "'s island: " + why + "."); return; }
  }
  boolean memberThere = !tk.equals(@PKG@.IslandStore.pkey(tu));
  go(store, ref, pr, world, tk, false);
  if (rank <= 1) @PKG@.IslandStore.say(pr, "[Island] Visiting " + on + "'s island" + (memberThere ? " (" + target.getUsername() + " is a co-op member there)" : "") + (rank == 1 ? " - you are Trusted here: you may build." : " - the owner decides what visitors may do (/island menu on your own island shows the rules)."), "#cfe3ff");
}""")

# =====================================================================================================================
# Tasks (world thread): SendHubTask, SendHomeTask, EvacTask, SweepTask (+ WorldConfig apply), ArrivalTask / ArrivalDispatch
# =====================================================================================================================
shtk.addInterface(pool.get("java.lang.Runnable"))
F(shtk, "public @PR@ pr;")
F(shtk, "public String worldName;")
F(shtk, "public String text;")
C(shtk, "public SendHubTask(@PR@ p, String wn, String t) { this.pr = p; this.worldName = wn; this.text = t; }")
# the player's own world thread; at most one hub teleport per player per 4 s (the sweep runs every 5 s)
M(shtk, r"""
public static boolean now(@ST@ st, @REF@ ref, @PR@ pr, @WLD@ w, String text) {
  try {
    java.util.UUID u = pr.getUuid();
    long t = System.currentTimeMillis();
    Long last = (Long) @PKG@.IslandStore.EXPELLING.get(u);
    if (last != null && t - last.longValue() < 4000L) return false;
    @PKG@.IslandStore.EXPELLING.put(u, Long.valueOf(t));
    boolean ok = @PKG@.HubCmd.sendToHub(st, ref, pr, w);
    if (text != null) @PKG@.IslandStore.say(pr, text, "#ff9d6b");
    return ok;
  } catch (Throwable x) { @PKG@.IslandStore.warn("could not send a player to the hub: " + x); return false; }
}""")
M(shtk, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) return;
    @REF@ ref = pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    now(st, ref, pr, w, this.text);
  } catch (Throwable t) { @PKG@.IslandStore.warn("send-to-hub task failed: " + t); }
}""")
# kicked / disbanded member standing on the co-op island -> their own island (spec 1.6); skipped if they left or switched profile
shom.addInterface(pool.get("java.lang.Runnable"))
F(shom, "public @PR@ pr;")
F(shom, "public String key;")
F(shom, "public String worldName;")
C(shom, "public SendHomeTask(@PR@ p, String k, String wn) { this.pr = p; this.key = k; this.worldName = wn; }")
M(shom, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) return;
    if (!this.key.equals(@PKG@.IslandStore.pkey(pr.getUuid()))) return;
    @REF@ ref = pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    @PKG@.IslandCmd.go(st, ref, pr, w, this.key, true);
  } catch (Throwable t) { @PKG@.IslandStore.warn("send-home task failed: " + t); }
}""")
# reset: everyone on the old island except the owner -> hub (spec 1.7 step 2)
evac.addInterface(pool.get("java.lang.Runnable"))
F(evac, "public @WLD@ world;")
F(evac, "public java.util.UUID except;")
F(evac, "public String text;")
C(evac, "public EvacTask(@WLD@ w, java.util.UUID ex, String t) { this.world = w; this.except = ex; this.text = t; }")
M(evac, r"""
public void run() {
  try {
    if (world == null || !world.isAlive()) return;
    java.util.ArrayList l = new java.util.ArrayList(world.getPlayerRefs());
    for (int i = 0; i < l.size(); i++) {
      @PR@ p = (@PR@) l.get(i);
      if (p == null || !p.isValid() || p.getUuid().equals(this.except)) continue;
      @REF@ ref = p.getReference();
      if (ref == null) continue;
      @ST@ st = ref.getStore();
      if (st == null) continue;
      @PKG@.HubCmd.sendToHub(st, ref, p, world);
      @PKG@.IslandStore.say(p, this.text, "#ffe08a");
    }
  } catch (Throwable t) { @PKG@.IslandStore.warn("reset evacuation failed: " + t); }
}""")
swp.addInterface(pool.get("java.lang.Runnable"))
F(swp, "public @WLD@ world;")
F(swp, "public boolean visitors;")
C(swp, "public SweepTask(@WLD@ w, boolean v) { this.world = w; this.visitors = v; }")
# island PvP / mob spawning -> the world's own config (vanilla WorldConfigSetPvpCommand / SpawnCommand pattern), idempotent
M(swp, r"""
public static void apply(@WLD@ w, @PKG@.IslandSettings s) {
  try {
    @WCFG@ c = w.getWorldConfig();
    boolean ch = false;
    if (c.isPvpEnabled() != s.pvp) { c.setPvpEnabled(s.pvp); ch = true; }
    if (c.isSpawningNPC() != s.spawning) { c.setSpawningNPC(s.spawning); ch = true; }
    if (ch) {
      c.markChanged();
      @PKG@.IslandStore.info("island settings applied to " + w.getName() + ": PvP " + (s.pvp ? "on" : "off") + ", mob spawning " + (s.spawning ? "on" : "off"));
    }
  } catch (Throwable t) { @PKG@.IslandStore.warn("could not apply island settings to " + w.getName() + ": " + t); }
}""")
# world thread: apply the settings, then send off everyone who may not be here (spec 4.1 sweep, no limit clause; PvP-on expels visitors)
M(swp, r"""
public void run() {
  try {
    @WLD@ w = this.world;
    if (w == null || !w.isAlive()) return;
    String wn = w.getName();
    String owner = @PKG@.IslandStore.ownerOf(wn);
    if (owner == null) return;
    @PKG@.IslandSettings s = @PKG@.IslandStore.settings(owner);
    if (s.bad) return;
    boolean retired = @PKG@.IslandStore.isRetired(wn);
    if (!retired) apply(w, s);
    String on = @PKG@.IslandStore.ownerDisplay(owner, s);
    java.util.ArrayList l = new java.util.ArrayList(w.getPlayerRefs());
    for (int i = 0; i < l.size(); i++) {
      @PR@ p = (@PR@) l.get(i);
      if (p == null || !p.isValid()) continue;
      if (@PKG@.IslandPerms.isAdmin(p)) continue;
      java.util.UUID u = p.getUuid();
      String why = null;
      if (retired) why = "this island was reset - /island takes co-op members to the new one";
      else {
        int rank = @PKG@.IslandPerms.rank(owner, u, s);
        why = @PKG@.IslandPerms.mayEnter(owner, s, rank, u, w, false);
        if (why == null && this.visitors && rank == 0) why = "PvP was turned on here";
        if (why == null && this.visitors && rank >= 1) @PKG@.IslandStore.say(p, "[Island] PvP is now ON on this island - players can hurt each other.", "#ff9d6b");
      }
      if (why == null) continue;
      @REF@ ref = p.getReference();
      if (ref == null) continue;
      @ST@ st = ref.getStore();
      if (st == null) continue;
      @PKG@.SendHubTask.now(st, ref, p, w, "[Island] You were sent off " + on + "'s island: " + why + ".");
    }
  } catch (Throwable t) { @PKG@.IslandStore.warn("island sweep failed: " + t); }
}""")
M(swp, r"""
public static void now(String worldName, boolean visitors) {
  try {
    if (worldName == null) return;
    @WLD@ w = @UNI@.get().getWorld(worldName);
    if (w != null && w.isAlive()) w.execute(new @PKG@.SweepTask(w, visitors));
  } catch (Throwable t) { }
}""")
# arrival (spec 4.1 point 2 + spec 5): pass 1 = entry check, names, settings, tint fix, welcome, visit ping; pass 2 = late tint fix
arr.addInterface(pool.get("java.lang.Runnable"))
F(arr, "public @PR@ pr;")
F(arr, "public String worldName;")
F(arr, "public int pass;")
C(arr, "public ArrivalTask(@PR@ p, String wn, int ps) { this.pr = p; this.worldName = wn; this.pass = ps; }")
ard.addInterface(pool.get("java.lang.Runnable"))
F(ard, "public @PR@ pr;")
F(ard, "public String worldName;")
F(ard, "public int pass;")
C(ard, "public ArrivalDispatch(@PR@ p, String wn, int ps) { this.pr = p; this.worldName = wn; this.pass = ps; }")
M(ard, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) return;
    w.execute(new @PKG@.ArrivalTask(pr, this.worldName, this.pass));
  } catch (Throwable t) { }
}""")
M(arr, r"""
public static void schedule(@PR@ pr, String worldName, int pass, long delayMs) {
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.ArrivalDispatch(pr, worldName, pass), delayMs, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")
M(arr, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !w.getName().equals(this.worldName)) return;
    if (this.pass >= 2) { @PKG@.TintFix.fix(w); return; }
    String owner = @PKG@.IslandStore.ownerOf(this.worldName);
    if (owner == null) return;
    @REF@ ref = pr.getReference();
    if (ref == null) return;
    @ST@ st = ref.getStore();
    if (st == null) return;
    java.util.UUID u = pr.getUuid();
    boolean admin = @PKG@.IslandPerms.isAdmin(pr);
    @PKG@.IslandSettings s = @PKG@.IslandStore.settings(owner);
    if (s.bad) return;
    String on = @PKG@.IslandStore.ownerDisplay(owner, s);
    if (@PKG@.IslandStore.isRetired(this.worldName) && !admin) {
      @PKG@.SendHubTask.now(st, ref, pr, w, "[Island] This island was reset - /island takes co-op members to the new one.");
      return;
    }
    int rank = @PKG@.IslandPerms.rank(owner, u, s);
    if (!admin) {
      String why = @PKG@.IslandPerms.mayEnter(owner, s, rank, u, w, true);
      if (why != null) { @PKG@.SendHubTask.now(st, ref, pr, w, "[Island] You can't be on " + on + "'s island: " + why + "."); return; }
    }
    if (rank == 4) {
      @PKG@.IslandStore.setOwnerName(owner, pr.getUsername());
      if (s.note05) {
        @PKG@.IslandStore.setProps(owner, new String[] { "note05" }, new String[] { null });
        @PKG@.IslandStore.say(pr, "[Island] Island 0.5: /island invite now asks your friend to JOIN your island as a co-op member (/island accept). Your old build-rights invites are now Trusted (build only). Use /island trust for helpers, /island menu for everything.", "#ffe08a");
      }
    }
    else if (rank >= 1) @PKG@.IslandStore.setName(owner, @PKG@.IslandStore.pkey(u), pr.getUsername());
    @PKG@.SweepTask.apply(w, s);
    @PKG@.TintFix.fix(w);
    if (rank == 0 && !admin) {
      String ok = @PKG@.IslandPerms.otherProfileKey(owner, u, s);
      if (ok != null) {
        if (ok.equals(owner)) @PKG@.IslandStore.say(pr, "[Island] This island belongs to another of your profiles (" + @PKG@.IslandStore.profileNameOf(owner) + ") - you are a visitor here on this profile.", "#ffe08a");
        else @PKG@.IslandStore.say(pr, "[Island] You have a role here on your profile " + @PKG@.IslandStore.profileNameOf(ok) + " - on this profile you are a visitor.", "#ffe08a");
      } else {
        @PKG@.IslandStore.say(pr, "[Island] Visiting " + on + "'s island - PvP " + (s.pvp ? "ON" : "off") + " - visitors may: " + @PKG@.IslandPerms.visitorAllowedText(s) + ".", "#cfe3ff");
        if (s.notify) {
          String pk = owner + "|" + u;
          Long last = (Long) @PKG@.IslandStore.PINGED.get(pk);
          long now = System.currentTimeMillis();
          if (last == null || now - last.longValue() > 60000L) {
            @PKG@.IslandStore.PINGED.put(pk, Long.valueOf(now));
            @PKG@.IslandStore.notifyIsland(owner, "[Island] " + pr.getUsername() + " is visiting your island. /island menu (Visitors tab) to expel or ban.", "#ffe08a", u, null);
          }
        }
      }
    } else if (rank == 1) {
      @PKG@.IslandStore.say(pr, "[Island] Welcome to " + on + "'s island - you are Trusted here (you may build).", "#8fc8ff");
    }
    schedule(pr, this.worldName, 2, 4500L);
  } catch (Throwable t) { @PKG@.IslandStore.warn("arrival check failed: " + t); }
}""")

# =====================================================================================================================
# IslandCoop: every co-op / trust / visitor / settings action (commands AND page buttons). Each returns the result line for the
# acting player ("+" done, "-" refused, "=" info); other players get [Island] chat lines. Runs on the actor's world thread; file
# changes go through IslandStore's synchronized read-modify-write methods; teleports of OTHER players go to their world thread.
# =====================================================================================================================
M(coop, r"""
public static Object[] inviteFor(java.util.UUID u) {
  if (u == null) return null;
  Object o = @PKG@.IslandStore.INVITES.get(u);
  if (!(o instanceof Object[])) return null;
  Object[] inv = (Object[]) o;
  if (((Long) inv[2]).longValue() < System.currentTimeMillis()) return null;
  return inv;
}""")
# a <name> argument -> an entry of the list: exact key, stored name, full UUID, then a unique name prefix
M(coop, r"""
public static String findKey(@PKG@.IslandSettings s, String csv, String name) {
  if (s == null || name == null) return null;
  String want = name.trim();
  if (want.length() == 0) return null;
  String[] a = @PKG@.IslandStore.split(csv);
  for (int i = 0; i < a.length; i++) {
    if (a[i].equalsIgnoreCase(want)) return a[i];
  }
  for (int i = 0; i < a.length; i++) {
    Object n = s.names.get(a[i]);
    if (n instanceof String && ((String) n).equalsIgnoreCase(want)) return a[i];
  }
  if (want.length() == 36) {
    for (int i = 0; i < a.length; i++) {
      if (a[i].length() >= 36 && a[i].substring(0, 36).equalsIgnoreCase(want)) return a[i];
    }
  }
  String lw = want.toLowerCase();
  String hit = null;
  int hits = 0;
  for (int i = 0; i < a.length; i++) {
    Object n = s.names.get(a[i]);
    if (n instanceof String && ((String) n).toLowerCase().startsWith(lw)) { hit = a[i]; hits++; }
  }
  return hits == 1 ? hit : null;
}""")
# null = the pending invite can be accepted now, else the reason (spec 1.5 accept checks 3-5)
M(coop, r"""
public static String acceptProblem(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  Object[] inv = inviteFor(u);
  if (inv == null) return "you have no invite";
  String ok = (String) inv[0];
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(ok);
  if (s.bad) return "that island's file can't be read right now - try again in a moment";
  if (s.world == null) return "that island is gone";
  if (u.equals(@PKG@.IslandStore.ownerUuid(ok))) return "that island belongs to one of your own profiles";
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  if (!hk.equals(k)) return "you are in " + @PKG@.IslandStore.ownerDisplay(hk, @PKG@.IslandStore.settings(hk)) + "'s co-op - /island leave first";
  @PKG@.IslandSettings own = @PKG@.IslandStore.settings(k);
  if (own.bad) return "your own island file can't be read right now - try again in a moment";
  if (@PKG@.IslandStore.count(own.members) > 0) return "you lead a co-op island - /island disband first";
  String other = @PKG@.IslandStore.uuidEntryExcept(s.members + "," + s.trusted, u.toString(), k);
  if (other != null) return "your profile " + @PKG@.IslandStore.profileNameOf(other) + " already has a role on that island - switch to it, or ask the owner to remove it";
  if (@PKG@.IslandStore.contains(s.banned, u.toString())) return "you are banned from that island";
  if (1 + @PKG@.IslandStore.count(s.members) >= @PKG@.IslandCfg.COOP_MAX) return "that co-op is full";
  return null;
}""")
M(coop, r"""
public static String invite(@PR@ pr, @PR@ target) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  int rank = @PKG@.IslandPerms.rank(hk, u, s);
  String on = @PKG@.IslandStore.ownerDisplay(hk, s);
  if (!(rank == 4 || (rank == 3 && @PKG@.IslandCfg.ADMINS_INVITE))) return "-Only the island owner can invite co-op members (you are a co-op " + @PKG@.IslandPerms.roleName(rank) + " of " + on + "'s island). /island trust gives build rights.";
  if (s.world == null) return "-Create your island first: /island";
  if (target == null || !target.isValid()) return "-That player is not online.";
  java.util.UUID tu = target.getUuid();
  String tn = target.getUsername();
  if (tu.equals(u) || tu.equals(@PKG@.IslandStore.ownerUuid(hk))) return "-That is you (your own profiles can't join each other's islands).";
  if (@PKG@.IslandStore.contains(s.banned, tu.toString())) return "-" + tn + " is banned here - /island unban them first.";
  if (@PKG@.IslandStore.uuidEntry(s.members, tu.toString()) != null) return "-" + tn + " is already a co-op member of this island.";
  int count = 1 + @PKG@.IslandStore.count(s.members);
  if (count >= @PKG@.IslandCfg.COOP_MAX) return "-The co-op is full (" + count + " / " + @PKG@.IslandCfg.COOP_MAX + ").";
  long exp = System.currentTimeMillis() + @PKG@.IslandCfg.INVITE_SECONDS * 1000L;
  @PKG@.IslandStore.INVITES.put(tu, new Object[] { hk, u, Long.valueOf(exp), pr.getUsername(), on });
  @PKG@.IslandStore.say(target, "[Island] " + pr.getUsername() + " invited you to join " + (hk.equals(k) ? "their" : on + "'s") + " island as a co-op member. Type /island accept (or /island decline) within " + @PKG@.IslandCfg.INVITE_SECONDS + " s. Joining uses your current profile" + @PKG@.IslandStore.profileLabel(tu) + ". Your own island stays saved and comes back if you leave.", "#ffe08a");
  return "+Invited " + tn + " to the co-op - they have " + @PKG@.IslandCfg.INVITE_SECONDS + " s to /island accept.";
}""")
M(coop, r"""
public static String accept(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  Object[] inv = inviteFor(u);
  if (inv == null) { @PKG@.IslandStore.INVITES.remove(u); return "-You have no island invite (or it ran out)."; }
  if (@PKG@.IslandStore.bridge().get("profile:busy:" + u) != null) return "-Your profile is busy - try again in a moment.";
  String why = acceptProblem(pr);
  if (why != null) return "-You can't accept: " + why + ".";
  String ok = (String) inv[0];
  String k = @PKG@.IslandStore.pkey(u);
  int res = @PKG@.IslandStore.joinCoop(ok, k, pr.getUsername(), @PKG@.IslandCfg.COOP_MAX - 1);
  if (res == 1) return "-That co-op is full now.";
  if (res == 2) return "-You are banned from that island.";
  if (res == 3) return "-You are already a co-op member there.";
  if (res == 4) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.MEMBER_OF.put(k, ok);
  @PKG@.IslandStore.INVITES.remove(u);
  @PKG@.IslandStore.bump();
  @PKG@.IslandStore.publish(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(ok);
  @PKG@.IslandStore.notifyIsland(ok, "[Island] " + pr.getUsername() + " joined the island co-op.", "#8fe39a", u, null);
  @PKG@.IslandStore.info(pr.getUsername() + " (" + k + ") joined the co-op of " + ok);
  return "+You joined " + @PKG@.IslandStore.ownerDisplay(ok, s) + "'s island" + @PKG@.IslandStore.profileLabel(u) + "! /island now takes you there. /island leave brings you back to your own island.";
}""")
M(coop, r"""
public static String decline(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  Object o = @PKG@.IslandStore.INVITES.remove(u);
  if (!(o instanceof Object[])) return "-You have no island invite.";
  Object[] inv = (Object[]) o;
  @PKG@.IslandStore.sayU((java.util.UUID) inv[1], "[Island] " + pr.getUsername() + " declined your island invite.", "#ff9d6b");
  return "+Invite declined.";
}""")
# a kicked / disbanded member standing on the co-op island on THAT profile -> SendHomeTask on the island's world thread
M(coop, r"""
public static void sendHomeIfOn(@PR@ tp, String tk, String islandWorld) {
  try {
    if (tp == null || !tp.isValid() || islandWorld == null) return;
    if (!tk.equals(@PKG@.IslandStore.pkey(tp.getUuid()))) return;
    java.util.UUID wu = tp.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !islandWorld.equals(w.getName())) return;
    w.execute(new @PKG@.SendHomeTask(tp, tk, islandWorld));
  } catch (Throwable t) { @PKG@.IslandStore.warn("could not send a former member home: " + t); }
}""")
M(coop, r"""
public static String leave(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  if (hk.equals(k)) {
    if (@PKG@.IslandStore.count(@PKG@.IslandStore.settings(k).members) > 0) return "-You own this co-op - /island disband ends it.";
    return "-You are not in an island co-op.";
  }
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  int lr = @PKG@.IslandStore.leaveCoop(hk, k);
  if (lr == 2) return @PKG@.IslandStore.FILE_ERR;
  if (lr != 0) return "-You are not in an island co-op.";
  @PKG@.IslandStore.MEMBER_OF.remove(k, hk);
  @PKG@.IslandStore.bump();
  @PKG@.IslandStore.publish(u);
  @PKG@.IslandStore.notifyIsland(hk, "[Island] " + pr.getUsername() + " left the island co-op.", "#ff9d6b", u, null);
  String on = @PKG@.IslandStore.ownerDisplay(hk, s);
  if (world != null && store != null && ref != null && s.world != null && s.world.equals(world.getName())) @PKG@.IslandCmd.go(store, ref, pr, world, k, true);
  return "+You left " + on + "'s island. /island takes you to your own island again.";
}""")
M(coop, r"""
public static String kickByKey(@PR@ pr, String tk) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) != 4) return "-Only the island owner can remove co-op members.";
  if (tk == null || !@PKG@.IslandStore.contains(s.members, tk)) return "-That player is not a co-op member here.";
  String tn = @PKG@.IslandStore.nameOf(s, tk);
  int lr = @PKG@.IslandStore.leaveCoop(hk, tk);
  if (lr == 2) return @PKG@.IslandStore.FILE_ERR;
  if (lr != 0) return "-" + tn + " is not a co-op member any more.";
  @PKG@.IslandStore.MEMBER_OF.remove(tk, hk);
  @PKG@.IslandStore.bump();
  java.util.UUID tu = @PKG@.IslandStore.ownerUuid(tk);
  @PR@ tp = @PKG@.IslandStore.online(tu);
  String on = @PKG@.IslandStore.ownerDisplay(hk, s);
  if (tp != null) {
    @PKG@.IslandStore.publish(tu);
    @PKG@.IslandStore.say(tp, "[Island] You were removed from " + on + "'s island co-op. /island takes you to your own island.", "#ff9d6b");
    sendHomeIfOn(tp, tk, s.world);
  }
  @PKG@.IslandStore.notifyIsland(hk, "[Island] " + tn + " was removed from the co-op.", "#ff9d6b", u, tu);
  return "+Removed " + tn + " from the co-op.";
}""")
M(coop, r"""
public static String kick(@PR@ pr, String name) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) != 4) return "-Only the island owner can remove co-op members.";
  String tk = findKey(s, s.members, name);
  if (tk == null) {
    if (findKey(s, s.trusted, name) != null) return "-" + name + " is not a co-op member - use /island untrust.";
    return "-No co-op member called " + name + ".";
  }
  return kickByKey(pr, tk);
}""")
M(coop, r"""
public static String promoteKey(@PR@ pr, String tk, boolean up) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) != 4) return "-Only the island owner can promote or demote.";
  if (tk == null || !@PKG@.IslandStore.contains(s.members, tk)) return "-That player is not a co-op member here.";
  String tn = @PKG@.IslandStore.nameOf(s, tk);
  int r = @PKG@.IslandStore.setAdmin(hk, tk, up);
  if (r == 1) return "-" + tn + " is not a co-op member.";
  if (r == 2) return up ? "-" + tn + " is already an island admin." : "-" + tn + " is not an island admin.";
  if (r == 3) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  java.util.UUID tu = @PKG@.IslandStore.ownerUuid(tk);
  if (up) @PKG@.IslandStore.sayU(tu, "[Island] " + pr.getUsername() + " made you an island ADMIN - you can change the island settings in /island menu.", "#c9a0ff");
  else @PKG@.IslandStore.sayU(tu, "[Island] You are a co-op member again (no longer an island admin).", "#cfe3ff");
  return up ? "+" + tn + " is now an island admin (settings, trust, ban, lock)." : "+" + tn + " is a co-op member again.";
}""")
M(coop, r"""
public static String promote(@PR@ pr, String name, boolean up) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) != 4) return "-Only the island owner can promote or demote.";
  String tk = findKey(s, s.members, name);
  if (tk == null) return "-No co-op member called " + name + ".";
  return promoteKey(pr, tk, up);
}""")
M(coop, r"""
public static String disbandProblem(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  if (!hk.equals(k)) return "-Only the island owner can disband the co-op (you can /island leave).";
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(k);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (s.world == null) return "-You have no island.";
  if (@PKG@.IslandStore.count(s.members) == 0) return "-Your island has no co-op members.";
  return null;
}""")
M(coop, r"""
public static String disband(@PR@ pr, boolean confirmed) {
  String bad = disbandProblem(pr);
  if (bad != null) return bad;
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(k);
  String ck = "disband|" + u;
  long now = System.currentTimeMillis();
  if (!confirmed) {
    Object last = @PKG@.IslandStore.CONFIRM.get(ck);
    if (!(last instanceof Long) || now - ((Long) last).longValue() > 10000L) {
      @PKG@.IslandStore.CONFIRM.put(ck, Long.valueOf(now));
      return "=This removes all " + @PKG@.IslandStore.count(s.members) + " co-op member(s) from your island (trusted players, bans and settings stay). Type /island disband again within 10 s to confirm.";
    }
  }
  @PKG@.IslandStore.CONFIRM.remove(ck);
  String removed = @PKG@.IslandStore.clearCoop(k);
  if (removed == null) return @PKG@.IslandStore.FILE_ERR;
  String[] a = @PKG@.IslandStore.split(removed);
  for (int i = 0; i < a.length; i++) {
    @PKG@.IslandStore.MEMBER_OF.remove(a[i], k);
    java.util.UUID tu = @PKG@.IslandStore.ownerUuid(a[i]);
    @PR@ tp = @PKG@.IslandStore.online(tu);
    if (tp == null) continue;
    @PKG@.IslandStore.publish(tu);
    @PKG@.IslandStore.say(tp, "[Island] " + pr.getUsername() + " disbanded the island co-op. /island takes you to your own island again.", "#ff9d6b");
    sendHomeIfOn(tp, a[i], s.world);
  }
  @PKG@.IslandStore.bump();
  @PKG@.IslandStore.info(pr.getUsername() + " disbanded the co-op of " + k + " (" + a.length + " members)");
  return "+Co-op disbanded - " + a.length + " member(s) removed. Trusted players, bans and settings stay.";
}""")
M(coop, r"""
public static String trust(@PR@ pr, @PR@ target) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  int rank = @PKG@.IslandPerms.rank(hk, u, s);
  if (rank < 3) return "-Only the island owner and island admins can trust players.";
  if (s.world == null) return "-Create your island first: /island";
  if (target == null || !target.isValid()) return "-That player is not online.";
  java.util.UUID tu = target.getUuid();
  String tn = target.getUsername();
  if (tu.equals(u) || tu.equals(@PKG@.IslandStore.ownerUuid(hk))) return "-That is you (your own profiles can't be trusted on each other's islands).";
  if (@PKG@.IslandStore.contains(s.banned, tu.toString())) return "-" + tn + " is banned here - /island unban them first.";
  if (@PKG@.IslandStore.uuidEntry(s.members, tu.toString()) != null) return "-" + tn + " is a co-op member here already (members may do everything trusted players may).";
  String tk = @PKG@.IslandStore.pkey(tu);
  int r = @PKG@.IslandStore.trustKey(hk, tk, tn, @PKG@.IslandCfg.TRUSTED_MAX);
  if (r == 2) return "-" + tn + " is already trusted here.";
  if (r == 3) return "-The trusted list is full (" + @PKG@.IslandCfg.TRUSTED_MAX + ").";
  if (r == 4) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  String on = @PKG@.IslandStore.ownerDisplay(hk, s);
  @PKG@.IslandStore.say(target, "[Island] " + pr.getUsername() + " trusted you on " + on + "'s island: you may build there (/island visit " + on + "). Your own /island does not change.", "#8fc8ff");
  return "+" + tn + " is now Trusted: they may build on the island (not chests, furnaces, crops, beds or animals)." + (r == 1 ? " Their trust from another of their profiles moved to the current one" + @PKG@.IslandStore.profileLabel(tu) + "." : "");
}""")
M(coop, r"""
public static String untrustByKey(@PR@ pr, String tk) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) < 3) return "-Only the island owner and island admins can untrust players.";
  if (tk == null || !@PKG@.IslandStore.contains(s.trusted, tk)) return "-That player is not trusted here.";
  String tn = @PKG@.IslandStore.nameOf(s, tk);
  int ur = @PKG@.IslandStore.untrustKey(hk, tk);
  if (ur == 2) return @PKG@.IslandStore.FILE_ERR;
  if (ur != 0) return "-" + tn + " is not trusted any more.";
  @PKG@.IslandStore.bump();
  @PKG@.IslandStore.sayU(@PKG@.IslandStore.ownerUuid(tk), "[Island] You are no longer trusted on " + @PKG@.IslandStore.ownerDisplay(hk, s) + "'s island.", "#ff9d6b");
  return "+" + tn + " is no longer trusted (a visitor again).";
}""")
M(coop, r"""
public static String untrust(@PR@ pr, String name) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) < 3) return "-Only the island owner and island admins can untrust players.";
  String tk = findKey(s, s.trusted, name);
  if (tk == null) return "-Nobody called " + name + " is trusted here.";
  return untrustByKey(pr, tk);
}""")
M(coop, r"""
public static String expelOn(@PR@ pr, String ok, @PR@ target) {
  java.util.UUID u = pr.getUuid();
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(ok);
  int rank = @PKG@.IslandPerms.rank(ok, u, s);
  if (rank < 2) return "-Only the island's owner, admins and co-op members can expel visitors.";
  if (s.world == null) return "-That island does not exist.";
  if (target == null || !target.isValid()) return "-That player is not online.";
  java.util.UUID tu = target.getUuid();
  String tn = target.getUsername();
  if (tu.equals(u)) return "-That is you.";
  if (@PKG@.IslandPerms.rank(ok, tu, s) >= 2) return "-" + tn + " is a co-op member - only the owner can remove members (/island kick).";
  if (@PKG@.IslandPerms.isAdmin(target)) return "-" + tn + " is a server admin.";
  java.util.UUID wu = target.getWorldUuid();
  @WLD@ tw = null;
  if (wu != null) tw = @UNI@.get().getWorld(wu);
  if (tw == null || !s.world.equals(tw.getName())) return "-" + tn + " is not on the island right now.";
  @PKG@.IslandStore.EXPELLED.put(s.world + "|" + tu, Long.valueOf(System.currentTimeMillis()));
  @PKG@.IslandStore.EXPELLING.remove(tu);
  tw.execute(new @PKG@.SendHubTask(target, s.world, "[Island] " + pr.getUsername() + " sent you off " + @PKG@.IslandStore.ownerDisplay(ok, s) + "'s island. You can come back in " + @PKG@.IslandCfg.EXPEL_SECONDS + " s."));
  return "+Sent " + tn + " to the hub (they can't come back for " + @PKG@.IslandCfg.EXPEL_SECONDS + " s).";
}""")
# the island you stand on, else your home island (spec 8)
M(coop, r"""
public static String expel(@PR@ pr, @WLD@ world, @PR@ target) {
  String ok = null;
  if (world != null && @PKG@.IslandStore.isIslandWorld(world.getName())) ok = @PKG@.IslandStore.ownerOf(world.getName());
  if (ok == null) ok = @PKG@.IslandStore.homeKey(pr.getUuid());
  return expelOn(pr, ok, target);
}""")
M(coop, r"""
public static String ban(@PR@ pr, @PR@ target) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) < 3) return "-Only the island owner and island admins can ban.";
  if (s.world == null) return "-Create your island first: /island";
  if (target == null || !target.isValid()) return "-That player is not online.";
  java.util.UUID tu = target.getUuid();
  String tn = target.getUsername();
  if (tu.equals(u) || tu.equals(@PKG@.IslandStore.ownerUuid(hk))) return "-You can't ban yourself.";
  if (@PKG@.IslandStore.uuidEntry(s.members, tu.toString()) != null) return "-" + tn + " is a co-op member - the owner must /island kick them first.";
  if (@PKG@.IslandPerms.isAdmin(target)) return "-" + tn + " is a server admin.";
  boolean wasTrusted = @PKG@.IslandStore.uuidEntry(s.trusted, tu.toString()) != null;
  int r = @PKG@.IslandStore.banUuid(hk, tu.toString(), tn, @PKG@.IslandCfg.BANS_MAX);
  if (r == 1) return "-" + tn + " is already banned.";
  if (r == 2) return "-The ban list is full (" + @PKG@.IslandCfg.BANS_MAX + ").";
  if (r == 3) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  @PKG@.IslandStore.say(target, "[Island] You were banned from " + @PKG@.IslandStore.ownerDisplay(hk, s) + "'s island.", "#ff9d6b");
  java.util.UUID wu = target.getWorldUuid();
  @WLD@ tw = null;
  if (wu != null) tw = @UNI@.get().getWorld(wu);
  if (tw != null && s.world.equals(tw.getName())) {
    @PKG@.IslandStore.EXPELLING.remove(tu);
    tw.execute(new @PKG@.SendHubTask(target, s.world, null));
  }
  return "+" + tn + " is banned from the island" + (wasTrusted ? " (their trust was removed)" : "") + ".";
}""")
M(coop, r"""
public static String unbanByKey(@PR@ pr, String uu) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) < 3) return "-Only the island owner and island admins can unban.";
  if (uu == null || !@PKG@.IslandStore.contains(s.banned, uu)) return "-That player is not banned here.";
  String tn = @PKG@.IslandStore.nameOf(s, uu);
  int br = @PKG@.IslandStore.unbanUuid(hk, uu);
  if (br == 2) return @PKG@.IslandStore.FILE_ERR;
  if (br != 0) return "-" + tn + " is not banned any more.";
  @PKG@.IslandStore.bump();
  return "+" + tn + " is no longer banned.";
}""")
M(coop, r"""
public static String unban(@PR@ pr, String name) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (@PKG@.IslandPerms.rank(hk, u, s) < 3) return "-Only the island owner and island admins can unban.";
  String uu = findKey(s, s.banned, name);
  if (uu == null) return "-Nobody called " + name + " is banned here.";
  return unbanByKey(pr, uu);
}""")
M(coop, r"""
public static String bansText(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  if (@PKG@.IslandPerms.rank(hk, u, s) < 2) return "-Only the island's owner, admins and co-op members can see its ban list.";
  String[] b = @PKG@.IslandStore.split(s.banned);
  if (b.length == 0) return "=Nobody is banned from the island.";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < b.length; i++) {
    if (i > 0) sb.append(", ");
    sb.append(@PKG@.IslandStore.nameOf(s, b[i]));
  }
  return "=Banned (" + b.length + "): " + sb.toString();
}""")
M(coop, r"""
public static String editRefusal(@PKG@.IslandSettings s, int rank) {
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (rank < 3) return "-Only the island owner and island admins can change the island settings.";
  if (s.world == null) return "-Create your island first: /island";
  return null;
}""")
M(coop, r"""
public static String lock(@PR@ pr, boolean on) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  if (on) {
    if (s.mode == 2) return "-The island is already locked (Closed).";
    if (!@PKG@.IslandStore.setProps(hk, new String[] { "visit.prev", "visit.mode", "settings" }, new String[] { @PKG@.IslandCfg.modeName(s.mode), "closed", "1" })) return @PKG@.IslandStore.FILE_ERR;
    @PKG@.IslandStore.bump();
    @PKG@.SweepTask.now(s.world, false);
    return "+Island locked: only co-op members may be on it now (visitors and trusted players were sent off). /island unlock brings back " + @PKG@.IslandCfg.modeLabel(s.mode) + ".";
  }
  if (s.mode != 2) return "-The island is not locked.";
  int pm = s.prevMode == 2 ? 0 : s.prevMode;
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "visit.mode", "settings" }, new String[] { @PKG@.IslandCfg.modeName(pm), "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  return "+Island unlocked: visits are " + @PKG@.IslandCfg.modeLabel(pm) + " again.";
}""")
M(coop, r"""
public static String setMode(@PR@ pr, int m) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  if (m < 0 || m > 2) return "-Unknown visit mode.";
  if (m == s.mode) return "=Visits are already " + @PKG@.IslandCfg.modeLabel(m) + ".";
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "visit.mode", "settings" }, new String[] { @PKG@.IslandCfg.modeName(m), "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  if (m > s.mode) @PKG@.SweepTask.now(s.world, false);
  return "+Visits: " + @PKG@.IslandCfg.modeLabel(m) + "." + (m > s.mode ? " Anyone who may not stay is sent to the hub." : "");
}""")
M(coop, r"""
public static String changeLimit(@PR@ pr, int d) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  int n = s.limit + d;
  if (n < 1) n = 1;
  if (n > @PKG@.IslandCfg.LIMIT_MAX) n = @PKG@.IslandCfg.LIMIT_MAX;
  if (n == s.limit) return "=The visitor limit is " + n + " (1 to " + @PKG@.IslandCfg.LIMIT_MAX + ").";
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "visit.limit", "settings" }, new String[] { String.valueOf(n), "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  return "+Visitor limit: " + n + ". (Lowering it never sends anyone away.)";
}""")
M(coop, r"""
public static String toggleNotify(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  boolean nv = !s.notify;
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "visit.notify", "settings" }, new String[] { nv ? "1" : "0", "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  return nv ? "+Visit ping on: the owner and members get a chat line when someone visits." : "+Visit ping off.";
}""")
M(coop, r"""
public static String togglePvp(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  boolean nv = !s.pvp;
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "pvp", "settings" }, new String[] { nv ? "1" : "0", "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  @PKG@.SweepTask.now(s.world, nv);
  if (nv) @PKG@.IslandStore.notifyIsland(hk, "[Island] " + pr.getUsername() + " turned PvP ON on the island.", "#ff9d6b", u, null);
  return nv ? "+PvP is ON - visitors are sent to the hub; members and trusted players can hurt each other now." : "+PvP is off.";
}""")
M(coop, r"""
public static String toggleSpawning(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  boolean nv = !s.spawning;
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "spawning", "settings" }, new String[] { nv ? "1" : "0", "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  @PKG@.SweepTask.now(s.world, false);
  return nv ? "+Mob spawning on. (Void Sky islands have no wildlife, so nothing spawns until island biomes arrive.)" : "+Mob spawning off (mobs already there stay).";
}""")
# grid cell (spec 3.1): allowed -> min = role + 1 (denies it and every role to its left), denied -> min = role
M(coop, r"""
public static String clickPerm(@PR@ pr, int f, int r) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  if (f < 0 || f >= s.perm.length || r < 0 || r > 3) return "-Unknown permission.";
  int nm = r >= s.perm[f] ? r + 1 : r;
  if (!@PKG@.IslandStore.setProps(hk, new String[] { "perm." + @PKG@.IslandCfg.FLAG_IDS[f], "settings" }, new String[] { @PKG@.IslandCfg.rankName(nm), "1" })) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  return "+" + @PKG@.IslandPerms.LABELS[f] + ": " + @PKG@.IslandPerms.whoText(nm) + ".";
}""")
M(coop, r"""
public static String resetPerms(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  String bad = editRefusal(s, @PKG@.IslandPerms.rank(hk, u, s));
  if (bad != null) return bad;
  int n = @PKG@.IslandCfg.FLAG_IDS.length;
  String[] ks = new String[n + 1];
  String[] vs = new String[n + 1];
  for (int i = 0; i < n; i++) { ks[i] = "perm." + @PKG@.IslandCfg.FLAG_IDS[i]; vs[i] = null; }
  ks[n] = "settings";
  vs[n] = "1";
  if (!@PKG@.IslandStore.setProps(hk, ks, vs)) return @PKG@.IslandStore.FILE_ERR;
  @PKG@.IslandStore.bump();
  return "+Every permission is back to the server defaults.";
}""")
M(coop, r"""
public static String pendingText(String hk) {
  StringBuilder sb = new StringBuilder();
  long now = System.currentTimeMillis();
  java.util.Iterator it = @PKG@.IslandStore.INVITES.keySet().iterator();
  while (it.hasNext()) {
    Object key = it.next();
    Object o = @PKG@.IslandStore.INVITES.get(key);
    if (!(o instanceof Object[])) continue;
    Object[] inv = (Object[]) o;
    if (!hk.equals(inv[0])) continue;
    long left = (((Long) inv[2]).longValue() - now) / 1000L;
    if (left < 0L) continue;
    @PR@ p = @PKG@.IslandStore.online((java.util.UUID) key);
    if (sb.length() > 0) sb.append(", ");
    sb.append((p == null ? "someone" : p.getUsername()) + " (" + left + " s)");
  }
  return sb.toString();
}""")
M(coop, r"""
public static String hm(long ms) {
  long h = ms / 3600000L;
  long m = (ms % 3600000L) / 60000L;
  if (h > 0L) return h + " h " + m + " min";
  return (m < 1L ? 1L : m) + " min";
}""")
# spec 1.7 refusals; null = the owner may reset now
M(coop, r"""
public static String resetCheck(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  if (!hk.equals(k)) return "-Only the island owner can reset it (you are a co-op member of " + @PKG@.IslandStore.ownerDisplay(hk, @PKG@.IslandStore.settings(hk)) + "'s island).";
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(k);
  if (s.bad) return @PKG@.IslandStore.READ_ERR;
  if (s.world == null) return "-You have no island yet.";
  long now = System.currentTimeMillis();
  Long since = (Long) @PKG@.IslandStore.CREATING.get(k);
  if (since != null && now - since.longValue() < 60000L) return "-Your island is being created right now - wait a moment.";
  if (@PKG@.IslandStore.bridge().get("profile:busy:" + u) != null) return "-Your profile is busy - try again in a moment.";
  long cd = @PKG@.IslandCfg.RESET_HOURS * 3600000L;
  if (s.resetAt > 0L && now - s.resetAt < cd) return "-You can reset again in " + hm(cd - (now - s.resetAt)) + " (one reset every " + @PKG@.IslandCfg.RESET_HOURS + " h).";
  return null;
}""")
M(coop, r"""
public static String resetWarning(int step, boolean page) {
  if (step <= 1) return "=This DELETES every block and chest on your island, including your co-op members' things. Members, trusted players, bans and settings are kept. " + (page ? "Click again" : "Type /island reset again") + " within " + @PKG@.IslandCfg.RESET_CONFIRM + " s to continue.";
  return "=Last warning: " + (page ? "click once more" : "type /island reset once more") + " within " + @PKG@.IslandCfg.RESET_CONFIRM + " s and your island is rebuilt from scratch with a fresh starter kit. You can reset once every " + @PKG@.IslandCfg.RESET_HOURS + " h.";
}""")
# spec 1.7: evacuate the old island, then the 0.4.5 creation chain under a new world name; the bookkeeping lands in setWorldName
M(coop, r"""
public static String resetNow(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String bad = resetCheck(pr);
  if (bad != null) return bad;
  if (world == null || store == null || ref == null) return "-Could not read where you are - try /island reset again.";
  java.util.UUID u = pr.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(k);
  @UNI@ uni = @UNI@.get();
  int n = s.resets + 1;
  String nn = "skyy-island-" + k + "-r" + n;
  int guard = 0;
  while ((uni.isWorldLoadable(nn) || uni.getWorld(nn) != null || @PKG@.IslandStore.isIslandWorld(nn)) && guard < 100) {
    n++;
    nn = "skyy-island-" + k + "-r" + n;
    guard++;
  }
  String old = s.world;
  long now = System.currentTimeMillis();
  @WLD@ ow = uni.getWorld(old);
  if (ow != null && ow.isAlive()) {
    @PKG@.EvacTask ev = new @PKG@.EvacTask(ow, u, "[Island] " + pr.getUsername() + " reset this island - you were sent to the hub. /island takes co-op members to the new island.");
    if (ow == world) ev.run(); else ow.execute(ev);
  }
  Long mark = Long.valueOf(now);
  Object[] rmark = new Object[] { old, Integer.valueOf(n), mark };
  @PKG@.IslandStore.CREATING.put(k, mark);
  @PKG@.IslandStore.RESETTING.put(k, rmark);
  @TRF@ ret = @PKG@.IslandCmd.here(store, ref);
  try {
    java.util.concurrent.CompletableFuture f = @INS@.get().spawnInstance("SkyyIsland", nn, world, ret);
    f = f.thenCompose(new @PKG@.IslandBuild(k));
    f = f.whenComplete(new @PKG@.BuildDone(k, mark, rmark, pr));
    @INS@.teleportPlayerToLoadingInstance(ref, (@CA@) store, f, ret, null);
  } catch (Throwable t) {
    @PKG@.IslandStore.CREATING.remove(k, mark);
    @PKG@.IslandStore.RESETTING.remove(k, rmark);
    @PKG@.IslandStore.warn("island reset failed for " + k + ": " + t);
    return "-The reset failed: " + t.getMessage();
  }
  @PKG@.IslandStore.notifyIsland(k, "[Island] " + pr.getUsername() + " is resetting the island - /island takes you to the new one in a moment.", "#ffe08a", u, null);
  @PKG@.IslandStore.info("reset of " + k + ": " + old + " -> " + nn + " (old world folder kept as a backup)");
  return "+Resetting your island... a fresh island with a new starter kit is being built.";
}""")
M(coop, r"""
public static String resetCmd(@ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  java.util.UUID u = pr.getUuid();
  String ck = "reset|" + u;
  String bad = resetCheck(pr);
  if (bad != null) { @PKG@.IslandStore.CONFIRM.remove(ck); return bad; }
  long now = System.currentTimeMillis();
  int step = 0;
  Object o = @PKG@.IslandStore.CONFIRM.get(ck);
  if (o instanceof Object[]) {
    Object[] c = (Object[]) o;
    if (now - ((Long) c[1]).longValue() <= @PKG@.IslandCfg.RESET_CONFIRM * 1000L) step = ((Integer) c[0]).intValue();
  }
  step = step + 1;
  if (step < 3) {
    @PKG@.IslandStore.CONFIRM.put(ck, new Object[] { Integer.valueOf(step), Long.valueOf(now) });
    return resetWarning(step, false);
  }
  @PKG@.IslandStore.CONFIRM.remove(ck);
  return resetNow(store, ref, pr, world);
}""")

# =====================================================================================================================
# Bridge functions (spec 9.3) - plain classes, no lambdas
# =====================================================================================================================
for c in (pfn, rfn, ofn, cfn):
    c.addInterface(pool.get("java.util.function.Function"))
C(pfn, "public PermFn() { }")
C(rfn, "public RoleFn() { }")
C(ofn, "public OwnerFn() { }")
C(cfn, "public CoopFn() { }")
M(pfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || a[1] == null || a[2] == null) return null;
    java.util.UUID u = (java.util.UUID) a[0];
    String wn = String.valueOf(a[1]);
    String flag = String.valueOf(a[2]).trim();
    String owner = @PKG@.IslandStore.ownerOf(wn);
    if (owner == null) return null;
    @PR@ p = @PKG@.IslandStore.online(u);
    if (p != null && @PKG@.IslandPerms.isAdmin(p)) return Boolean.TRUE;
    @PKG@.IslandSettings s = @PKG@.IslandStore.settings(owner);
    if (s.bad) return null;
    int rank = @PKG@.IslandPerms.rank(owner, u, s);
    if (flag.equalsIgnoreCase("enter")) {
      if (@PKG@.IslandStore.isRetired(wn)) return Boolean.FALSE;
      @WLD@ w = @UNI@.get().getWorld(wn);
      boolean inside = false;
      if (p != null && w != null && p.getWorldUuid() != null) {
        @WLD@ pw = @UNI@.get().getWorld(p.getWorldUuid());
        inside = pw != null && wn.equals(pw.getName());
      }
      return Boolean.valueOf(@PKG@.IslandPerms.mayEnter(owner, s, rank, u, w, !inside) == null);
    }
    if (flag.equalsIgnoreCase("settings")) return Boolean.valueOf(rank >= 3);
    int f = @PKG@.IslandCfg.flagIndex(flag);
    if (f < 0) return null;
    return Boolean.valueOf(@PKG@.IslandPerms.allowedFor(owner, s, rank, u, f, -1));
  } catch (Throwable t) { return null; }
}""")
M(rfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || a[1] == null) return null;
    String owner = @PKG@.IslandStore.ownerOf(String.valueOf(a[1]));
    if (owner == null) return null;
    if (@PKG@.IslandStore.settings(owner).bad) return null;
    int r = @PKG@.IslandPerms.rankU(owner, (java.util.UUID) a[0]);
    if (r < 0) return "banned";
    if (r == 0) return "visitor";
    if (r == 1) return "trusted";
    if (r == 2) return "member";
    if (r == 3) return "admin";
    return "owner";
  } catch (Throwable t) { return null; }
}""")
M(ofn, r"""
public Object apply(Object o) {
  try { return o == null ? null : @PKG@.IslandStore.ownerOf(String.valueOf(o)); } catch (Throwable t) { return null; }
}""")
M(cfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof java.util.UUID)) return new String[0];
    String hk = @PKG@.IslandStore.homeKey((java.util.UUID) o);
    @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
    if (s.world == null) return new String[0];
    String[] m = @PKG@.IslandStore.split(s.members);
    String[] r = new String[m.length + 1];
    java.util.UUID ou = @PKG@.IslandStore.ownerUuid(hk);
    r[0] = ou == null ? hk : ou.toString();
    for (int i = 0; i < m.length; i++) {
      java.util.UUID mu = @PKG@.IslandStore.ownerUuid(m[i]);
      r[i + 1] = mu == null ? m[i] : mu.toString();
    }
    return r;
  } catch (Throwable t) { return new String[0]; }
}""")

# =====================================================================================================================
# Guards (ONE registerSystem per class). Base = EntityEventSystem on the acting player (0.3/0.4.4 pattern); the subclasses say
# which flag an event needs. GuardHurt is a DamageEventSystem (filter group) whose entity is the VICTIM.
# =====================================================================================================================
C(guard, "public GuardSystem(Class cls) { super(cls); }")
M(guard, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
# hooks the subclasses override (declared before handle(): javassist has no forward references)
M(guard, r"""
public int flagFor(@EV@ ev, @ST@ st) {
  return -1;
}""")
M(guard, r"""
public int extraFlag(@EV@ ev) {
  return -1;
}""")
M(guard, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    if (!@PKG@.IslandStore.isIslandWorld(w.getName())) return;
    int flag = flagFor(ev, st);
    if (flag < 0) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (@PKG@.IslandPerms.allow(w, pr, flag, extraFlag(ev))) return;
    if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
  } catch (Throwable t) { @PKG@.IslandStore.warn("guard failed: " + t); }
}""")
for gc, gname, gev in ((g1, "GuardDamage", "DBE"), (g2, "GuardBreak", "BBE"), (g3, "GuardPlace", "PBE"), (g4, "GuardPickup", "PUE"),
                       (g5, "GuardUse", "UBPRE"), (g6, "GuardDrop", "DIE"), (g7, "GuardUseEntity", "UEPRE")):
    C(gc, "public %s() { super(@%s@.class); }" % (gname, gev))
for gc, ev in ((g1, "DBE"), (g2, "BBE")):
    M(gc, r"""
public int flagFor(@EV@ ev, @ST@ st) {
  if (!(ev instanceof @XEV@)) return -1;
  return @PKG@.IslandPerms.breakFlag(((@XEV@) ev).getBlockType());
}""".replace("@XEV@", "@%s@" % ev))
    M(gc, r"""
public int extraFlag(@EV@ ev) {
  if (!(ev instanceof @XEV@)) return -1;
  return @PKG@.IslandPerms.containerKind(((@XEV@) ev).getBlockType());
}""".replace("@XEV@", "@%s@" % ev))
M(g3, "public int flagFor(@EV@ ev, @ST@ st) { return @PKG@.IslandPerms.BUILD; }")
M(g4, "public int flagFor(@EV@ ev, @ST@ st) { return @PKG@.IslandPerms.PICKUP; }")
M(g6, "public int flagFor(@EV@ ev, @ST@ st) { return @PKG@.IslandPerms.DROP; }")
M(g5, r"""
public int flagFor(@EV@ ev, @ST@ st) {
  if (!(ev instanceof @UBE@)) return -1;
  @UBE@ e = (@UBE@) ev;
  return @PKG@.IslandPerms.useFlag(e.getBlockType(), e.getInteractionType());
}""")
M(g5, r"""
public int extraFlag(@EV@ ev) {
  if (!(ev instanceof @UBE@)) return -1;
  @UBE@ e = (@UBE@) ev;
  if (e.getInteractionType() != @ITY@.Primary) return -1;
  return @PKG@.IslandPerms.containerKind(e.getBlockType());
}""")
# using an NPC: a farm animal needs 'animals', any other NPC 'other'; players / items are not guarded here
M(g7, r"""
public int flagFor(@EV@ ev, @ST@ st) {
  if (!(ev instanceof @UEE@)) return -1;
  @REF@ t = ((@UEE@) ev).getTargetEntity();
  if (t == null || !t.isValid()) return -1;
  Object n = st.getComponent(t, @NPC@.getComponentType());
  if (!(n instanceof @NPC@)) return -1;
  return @PKG@.IslandCfg.isAnimal(((@NPC@) n).getRoleName()) ? @PKG@.IslandPerms.ANIMALS : @PKG@.IslandPerms.OTHER;
}""")
C(ghurt, "public GuardHurt() { super(); }")
M(ghurt, r"""
public @QRY@ getQuery() {
  return @QRY@.any();
}""")
M(ghurt, r"""
public @SG@ getGroup() {
  return @DMOD@.get().getFilterDamageGroup();
}""")
M(ghurt, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @DMG@)) return;
    @DMG@ d = (@DMG@) ev;
    if (d.isCancelled()) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null || !@PKG@.IslandStore.isIslandWorld(w.getName())) return;
    Object npc = chunk.getComponent(idx, @NPC@.getComponentType());
    if (!(npc instanceof @NPC@)) return;
    @DSRC@ src = d.getSource();
    if (!(src instanceof @DENT@)) return;
    @REF@ att = ((@DENT@) src).getRef();
    if (att == null || !att.isValid()) return;
    @PR@ pr = (@PR@) buf.getComponent(att, @PR@.getComponentType());
    if (pr == null) return;
    int flag = @PKG@.IslandCfg.isAnimal(((@NPC@) npc).getRoleName()) ? @PKG@.IslandPerms.ANIMALS : @PKG@.IslandPerms.MOBS;
    if (@PKG@.IslandPerms.allow(w, pr, flag, -1)) return;
    d.setCancelled(true);
  } catch (Throwable t) { }
}""")

# =====================================================================================================================
# IslandMenuPage (/island menu): inline only (HANDOFF section 2), ids without underscores, root anchor Width/Height only,
# TextButton + EventData, rebuilt only after a click (never periodically), big and readable. Spec section 7.
# =====================================================================================================================
for f in ("public int tab;", "public String info;", "public String confirm;", "public long confirmUntil;", "public String keepName;",
          "public int trustPage;", "public int banPage;", "public int nid;", "public java.util.ArrayList rowKeys;",
          "public java.util.ArrayList trustKeys;", "public java.util.ArrayList visUuids;", "public java.util.ArrayList banKeys;"):
    F(page, f)
C(page, r"""
public IslandMenuPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = 0; this.info = ""; this.confirm = ""; this.confirmUntil = 0L; this.keepName = "";
  this.trustPage = 0; this.banPage = 0; this.nid = 0;
  this.rowKeys = new java.util.ArrayList(); this.trustKeys = new java.util.ArrayList();
  this.visUuids = new java.util.ArrayList(); this.banKeys = new java.util.ArrayList();
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
# one string value out of the page event JSON (SkyySacks 0.7.3 / SkyyGuilds 0.1 jsonStr, verified in game with TextFields)
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
public static String two(int n) {
  return n < 10 ? "0" + n : String.valueOf(n);
}""")
M(page, r"""
public static String date(String ms) {
  try { return new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date(Long.parseLong(ms.trim()))); } catch (Throwable t) { return "?"; }
}""")
M(page, r"""
public static int idx(String a, int from) {
  try { return Integer.parseInt(a.substring(from)); } catch (Throwable t) { return -1; }
}""")
M(page, r"""
public void lbl(@UCB@ b, String parent, int w, int h, int fs, boolean bold, String color, boolean center, String text) {
  String id = "SkyyIsL" + this.nid;
  this.nid = this.nid + 1;
  String anc = w > 0 ? "Anchor: (Width: " + w + ", Height: " + h + ");" : "Anchor: (Height: " + h + ");";
  b.appendInline(parent, "Label #" + id + " { " + anc + " Text: \"\"; Style: (FontSize: " + fs + (bold ? ", RenderBold: true" : "") + ", TextColor: " + color + (center ? ", HorizontalAlignment: Center" : "") + ", VerticalAlignment: Center); }");
  b.set("#" + id + ".Text", text == null ? "" : text);
}""")
M(page, r"""
public void gap(@UCB@ b, String parent, int w, int h) {
  if (w > 0) b.appendInline(parent, "Label { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"\"; }");
  else b.appendInline(parent, "Label { Anchor: (Height: " + h + "); Text: \"\"; }");
}""")
M(page, r"""
public void btn(@UCB@ b, @UEB@ ev, String parent, String id, String text, int w, int h, String st, String payload) {
  b.appendInline(parent, "TextButton #" + id + " { Anchor: (Width: " + w + ", Height: " + h + "); Text: \"" + safe(text) + "\"; " + st + " }");
  if (payload != null) ev.addEventBinding(@BT@.Activating, "#" + id, @EVD@.of("a", payload));
}""")
M(page, r"""
public String row(@UCB@ b, String parent, String id, int h, String bg) {
  b.appendInline(parent, "Group #" + id + " { Anchor: (Height: " + h + "); LayoutMode: Left;" + (bg == null ? "" : " Background: " + bg + ";") + " }");
  return "#" + id;
}""")
M(page, r"""
public void twoLine(@UCB@ b, String parent, int w, int h, String top, String bottom) {
  String a = "SkyyIsL" + this.nid;
  this.nid = this.nid + 1;
  String c = "SkyyIsL" + this.nid;
  this.nid = this.nid + 1;
  b.appendInline(parent, "Group { Anchor: (Width: " + w + ", Height: " + h + "); Label #" + a + " { Anchor: (Left: 12, Top: 1, Width: " + (w - 16) + ", Height: 20); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); } Label #" + c + " { Anchor: (Left: 12, Top: 21, Width: " + (w - 16) + ", Height: 15); Text: \"\"; Style: (FontSize: 12, TextColor: #9fb8d0, VerticalAlignment: Center); } }");
  b.set("#" + a + ".Text", top);
  b.set("#" + c + ".Text", bottom);
}""")
M(page, r"""
public void cell(@UCB@ b, String parent, int w, int h, String bg, String text) {
  String id = "SkyyIsL" + this.nid;
  this.nid = this.nid + 1;
  b.appendInline(parent, "Group { Anchor: (Width: " + w + ", Height: " + h + "); Background: " + bg + "; Label #" + id + " { Anchor: (Full: 0); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); } }");
  b.set("#" + id + ".Text", text);
}""")
M(page, r"""
public void dot(@UCB@ b, String parent, boolean on) {
  b.appendInline(parent, "Group { Anchor: (Width: 34, Height: 40); Group { Anchor: (Left: 10, Top: 13, Width: 14, Height: 14); Background: " + (on ? "#50d060" : "#55606e") + "; } }");
}""")
M(page, r"""
public void closePage(@REF@ ref, @ST@ st) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p != null) p.getPageManager().setPage(ref, st, @PGE@.None);
  } catch (Throwable t) { @PKG@.IslandStore.warn("could not close the island menu: " + t); }
}""")
M(page, r"""
public void buildTabs(@UCB@ b, @UEB@ ev) {
  String[] ids = new String[] { "SkyyIsTabOv", "SkyyIsTabMem", "SkyyIsTabPerm", "SkyyIsTabVis", "SkyyIsTabIsl" };
  String[] txt = new String[] { "Overview", "Members", "Permissions", "Visitors", "Island" };
  String[] pay = new String[] { "tabov", "tabmem", "tabperm", "tabvis", "tabisl" };
  b.appendInline("#SkyyIsRoot", "Group #SkyyIsTabs { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 2); }");
  for (int i = 0; i < 5; i++) {
    if (i > 0) gap(b, "#SkyyIsTabs", 12, 46);
    String st = i == this.tab ? style("#7a5a10", "#9a7418", "#4a3608", "#fff0c8", 18) : style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 18);
    btn(b, ev, "#SkyyIsTabs", ids[i], txt[i], 228, 46, st, pay[i]);
  }
}""")
M(page, r"""
public void buildOverview(@UCB@ b, @UEB@ ev, java.util.UUID u, String k, String hk, @PKG@.IslandSettings s, int rank) {
  String P = "#SkyyIsBody";
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 18);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 17);
  long now = System.currentTimeMillis();
  boolean has = s.world != null;
  if (!has && hk.equals(k)) {
    gap(b, P, 0, 24);
    lbl(b, P, 0, 44, 24, true, "#ffe08a", true, "You have no island yet");
    lbl(b, P, 0, 28, 16, false, "#cfe3ff", true, "Your private sky island is where you farm, build and later keep minions. It is created the first time you go there.");
    gap(b, P, 0, 10);
    String r = row(b, P, "SkyyIsCreateRow", 60, null);
    gap(b, r, 420, 56);
    btn(b, ev, r, "SkyyIsCreate", "Create my island", 360, 56, gs, "create");
  } else if (!has) {
    gap(b, P, 0, 24);
    lbl(b, P, 0, 34, 18, true, "#ff9d6b", true, "The island you are a co-op member of is not available right now - ask its owner.");
  } else {
    String on = @PKG@.IslandStore.ownerDisplay(hk, s);
    b.appendInline(P, "Group #SkyyIsBox { Anchor: (Height: 136); LayoutMode: Top; Background: #132236(0.95); Padding: (Horizontal: 16, Vertical: 6); }");
    lbl(b, "#SkyyIsBox", 0, 30, 19, true, "#ffe08a", false, "Owner: " + on + (hk.equals(k) ? "   (that is you)" : "   - you are a co-op " + @PKG@.IslandPerms.roleName(rank) + " here"));
    lbl(b, "#SkyyIsBox", 0, 30, 17, false, "#e6f2ff", false, "Co-op: " + (1 + @PKG@.IslandStore.count(s.members)) + " / " + @PKG@.IslandCfg.COOP_MAX + " players      Trusted: " + @PKG@.IslandStore.count(s.trusted) + "      Banned: " + @PKG@.IslandStore.count(s.banned));
    @WLD@ w = @PKG@.IslandStore.loadedWorld(s.world);
    int vis = w == null ? 0 : @PKG@.IslandPerms.visitorCount(w, hk, s, null);
    lbl(b, "#SkyyIsBox", 0, 30, 17, false, "#e6f2ff", false, "Visits: " + @PKG@.IslandCfg.modeLabel(s.mode) + " (limit " + s.limit + ")      Visitors now: " + vis + "      PvP: " + (s.pvp ? "ON" : "off") + "      Mob spawning: " + (s.spawning ? "on" : "off"));
    lbl(b, "#SkyyIsBox", 0, 30, 15, false, "#9fb8d0", false, "World: " + s.world + (w != null ? "  (loaded)" : "  (not loaded - it loads when someone goes there)"));
    gap(b, P, 0, 8);
    if (rank >= 2) {
      String r = row(b, P, "SkyyIsGoRow", 56, null);
      btn(b, ev, r, "SkyyIsGo", "Go to island", 320, 52, gs, "go");
      gap(b, r, 20, 52);
      lbl(b, r, 800, 52, 15, false, "#9fb8d0", false, "Same as /island. Closes this page and takes you there.");
    }
  }
  Object[] inv = @PKG@.IslandCoop.inviteFor(u);
  if (inv != null) {
    gap(b, P, 0, 8);
    long secs = (((Long) inv[2]).longValue() - now) / 1000L;
    String why = @PKG@.IslandCoop.acceptProblem(this.playerRef);
    String r = row(b, P, "SkyyIsInvRow", 60, "#1d3320(0.95)");
    gap(b, r, 14, 52);
    lbl(b, r, why == null ? 820 : 1000, 52, 16, true, "#ffe08a", false, inv[3] + " invited you to join " + inv[4] + "'s island - " + secs + " s left" + (why == null ? ". Joining uses your current profile." : "  (can't accept: " + why + ")"));
    if (why == null) {
      btn(b, ev, r, "SkyyIsAcc", "Accept", 150, 48, gs, "acc");
      gap(b, r, 10, 48);
    }
    btn(b, ev, r, "SkyyIsDec", "Decline", 150, 48, rs, "dec");
  }
  if (rank == 4 && has) {
    gap(b, P, 0, 10);
    lbl(b, P, 0, 28, 18, true, "#e6f2ff", false, "Owner actions");
    String r = row(b, P, "SkyyIsOwnRow", 58, null);
    int nm = @PKG@.IslandStore.count(s.members);
    if (nm > 0) {
      btn(b, ev, r, "SkyyIsDisb", this.confirm.equals("disb") ? "Click again to DISBAND" : "Disband co-op (" + nm + ")", 330, 52, rs, "disb");
      gap(b, r, 16, 52);
    }
    String rb = @PKG@.IslandCoop.resetCheck(this.playerRef);
    if (rb == null) {
      String t = this.confirm.equals("reset2") ? "Really? Last click" : (this.confirm.equals("reset1") ? "Delete everything?" : "Reset island");
      btn(b, ev, r, "SkyyIsReset", t, 330, 52, rs, "reset");
    } else lbl(b, r, 780, 52, 15, false, "#9fb8d0", false, "Reset island: " + @PKG@.IslandStore.textOf(rb));
    lbl(b, P, 0, 24, 13, false, "#9fb8d0", false, "Reset rebuilds your island from scratch with a fresh starter kit. Members, trusted players, bans and settings stay. Once every " + @PKG@.IslandCfg.RESET_HOURS + " h.");
  }
  if (rank == 2 || rank == 3) {
    gap(b, P, 0, 10);
    String r = row(b, P, "SkyyIsLeaveRow", 58, null);
    btn(b, ev, r, "SkyyIsLeave", this.confirm.equals("leave") ? "Click again to leave" : "Leave island", 300, 52, rs, "leave");
    gap(b, r, 20, 52);
    lbl(b, r, 820, 52, 15, false, "#cfe3ff", false, "Your own island stays saved and comes back when you leave.");
  }
  gap(b, P, 0, 14);
  lbl(b, P, 0, 28, 17, true, "#e6f2ff", false, "Commands");
  String[] help = new String[] {
    "/island - go to your island      /island menu - this page      /island info      /island visit <player>      /hub",
    "/island invite <player> - co-op invite (they type /island accept or /island decline)      /island leave",
    "/island kick <name> | promote <name> | demote <name>      /island disband      /island reset   (owner)",
    "/island trust <player> | untrust <name> - build rights only, their /island stays their own",
    "/island expel <player>      /island ban <player> | unban <name> | bans      /island lock | unlock" };
  for (int i = 0; i < help.length; i++) lbl(b, P, 0, 22, 14, false, "#b8c8d8", false, help[i]);
}""")
M(page, r"""
public void buildMembers(@UCB@ b, @UEB@ ev, java.util.UUID u, String k, String hk, @PKG@.IslandSettings s, int rank) {
  String P = "#SkyyIsBody";
  if (s.world == null) {
    gap(b, P, 0, 30);
    lbl(b, P, 0, 34, 18, true, "#cfe3ff", true, "Create your island first (Overview tab), then invite co-op members or trust builders here.");
    return;
  }
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 17);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 16);
  boolean canInv = rank == 4 || (rank == 3 && @PKG@.IslandCfg.ADMINS_INVITE);
  if (rank >= 3) {
    String r = row(b, P, "SkyyIsNameRow", 52, null);
    b.appendInline(r, "Group #SkyyIsNameBox { Anchor: (Width: 420, Height: 46); Background: #16263a; }");
    b.appendInline("#SkyyIsNameBox", "TextField #SkyyIsName { Anchor: (Full: 0); Padding: (Horizontal: 10); MaxLength: 32; PlaceholderText: \"Player name\"; PlaceholderStyle: (TextColor: #6e7da1, FontSize: 16); Style: (TextColor: #ffffff, FontSize: 16); }");
    if (this.keepName != null && this.keepName.length() > 0) b.set("#SkyyIsName.Value", this.keepName);
    ev.addEventBinding(@BT@.Validating, "#SkyyIsName", @EVD@.of("a", "name").append("@IsName", "#SkyyIsName.Value"), false);
    gap(b, r, 12, 46);
    if (canInv) {
      b.appendInline(r, "TextButton #SkyyIsInvBtn { Anchor: (Width: 270, Height: 46); Text: \"Invite to co-op\"; " + gs + " }");
      ev.addEventBinding(@BT@.Activating, "#SkyyIsInvBtn", @EVD@.of("a", "invite").append("@IsName", "#SkyyIsName.Value"));
      gap(b, r, 12, 46);
    }
    b.appendInline(r, "TextButton #SkyyIsTrustBtn { Anchor: (Width: 270, Height: 46); Text: \"Trust (build only)\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyIsTrustBtn", @EVD@.of("a", "trust").append("@IsName", "#SkyyIsName.Value"));
    lbl(b, P, 0, 24, 13, false, "#9fb8d0", false, (canInv ? "Invite to co-op = they join your island (their /island comes here).   " : "") + "Trust = build rights only, their /island stays their own.   Enter only keeps the name.");
  }
  String[] m = @PKG@.IslandStore.split(s.members);
  int total = m.length + 1;
  lbl(b, P, 0, 30, 18, true, "#e6f2ff", false, "Co-op members  (" + total + " / " + @PKG@.IslandCfg.COOP_MAX + ")");
  this.rowKeys = new java.util.ArrayList();
  int shown = total < 5 ? total : 5;
  for (int i = 0; i < shown; i++) {
    String key = i == 0 ? hk : m[i - 1];
    this.rowKeys.add(key);
    boolean me = key.equals(k);
    int rr = i == 0 ? 4 : (@PKG@.IslandStore.contains(s.admins, key) ? 3 : 2);
    java.util.UUID ku = @PKG@.IslandStore.ownerUuid(key);
    @PR@ op = @PKG@.IslandStore.online(ku);
    boolean on = op != null && key.equals(@PKG@.IslandStore.pkey(ku));
    String r = row(b, P, "SkyyIsMr" + i, 44, me ? "#1c2c44(0.95)" : "#142030(0.9)");
    dot(b, r, on);
    lbl(b, r, 300, 40, 18, true, on ? "#ffffff" : "#9aa6b4", false, @PKG@.IslandStore.nameOf(s, key) + (me ? "  (you)" : ""));
    lbl(b, r, 130, 40, 17, true, @PKG@.IslandPerms.roleColor(rr), false, @PKG@.IslandPerms.roleName(rr));
    Object since = s.since.get(key);
    lbl(b, r, 230, 40, 14, false, "#9fb8d0", false, i == 0 ? "leader" : (since instanceof String ? "since " + date((String) since) : "member") + (op != null && !on ? " - on another profile" : ""));
    if (rank == 4 && i > 0) {
      if (rr == 2) btn(b, ev, r, "SkyyIsPr" + i, "Promote", 140, 38, bs, "pr" + i);
      else btn(b, ev, r, "SkyyIsDm" + i, "Demote", 140, 38, bs, "dm" + i);
      gap(b, r, 8, 38);
      btn(b, ev, r, "SkyyIsKk" + i, this.confirm.equals("kk:" + key) ? "Sure?" : "Kick", 120, 38, rs, "kk" + i);
    }
    gap(b, P, 0, 2);
  }
  if (total > shown) lbl(b, P, 0, 22, 14, false, "#9fb8d0", false, "... and " + (total - shown) + " more - /island info lists everyone.");
  if (rank >= 3) {
    String pend = @PKG@.IslandCoop.pendingText(hk);
    if (pend.length() > 0) lbl(b, P, 0, 24, 14, true, "#ffe08a", false, "Invited: " + pend);
  }
  gap(b, P, 0, 6);
  String[] tr = @PKG@.IslandStore.split(s.trusted);
  lbl(b, P, 0, 30, 18, true, "#e6f2ff", false, "Trusted players - build only  (" + tr.length + " / " + @PKG@.IslandCfg.TRUSTED_MAX + ")");
  this.trustKeys = new java.util.ArrayList();
  if (tr.length == 0) {
    lbl(b, P, 0, 26, 14, false, "#9fb8d0", false, "Nobody yet. Trusted players may place and break blocks, use crafting benches and pick up items - not chests, furnaces, crops, beds or animals.");
    return;
  }
  int per = 10;
  int pages = (tr.length + per - 1) / per;
  if (this.trustPage >= pages) this.trustPage = pages - 1;
  if (this.trustPage < 0) this.trustPage = 0;
  int start = this.trustPage * per;
  for (int ri = 0; ri < 5; ri++) {
    int a0 = start + ri * 2;
    if (a0 >= tr.length || a0 >= start + per) break;
    String r = row(b, P, "SkyyIsTr" + ri, 42, ri % 2 == 0 ? "#132236(0.9)" : null);
    for (int c = 0; c < 2; c++) {
      int ix = a0 + c;
      if (ix >= tr.length) break;
      int slot = this.trustKeys.size();
      this.trustKeys.add(tr[ix]);
      if (c == 1) gap(b, r, 30, 40);
      String pn = tr[ix].length() > 36 ? "  (" + @PKG@.IslandStore.profileNameOf(tr[ix]) + ")" : "";
      lbl(b, r, 400, 40, 17, true, "#ffffff", false, "  " + @PKG@.IslandStore.nameOf(s, tr[ix]) + pn);
      if (rank >= 3) btn(b, ev, r, "SkyyIsUt" + slot, "Untrust", 150, 36, rs, "ut" + slot);
      else gap(b, r, 150, 36);
    }
  }
  if (pages > 1) {
    String r = row(b, P, "SkyyIsTNav", 40, null);
    gap(b, r, 380, 36);
    btn(b, ev, r, "SkyyIsTp", "< Prev", 120, 36, bs, "tp");
    lbl(b, r, 180, 36, 15, false, "#9fb8d0", true, "Page " + (this.trustPage + 1) + " / " + pages);
    btn(b, ev, r, "SkyyIsTn", "Next >", 120, 36, bs, "tn");
  }
}""")
M(page, r"""
public void buildPerms(@UCB@ b, @UEB@ ev, java.util.UUID u, String hk, @PKG@.IslandSettings s, int rank) {
  String P = "#SkyyIsBody";
  if (s.world == null) {
    gap(b, P, 0, 30);
    lbl(b, P, 0, 34, 18, true, "#cfe3ff", true, "Create your island first (Overview tab).");
    return;
  }
  boolean ed = rank >= 3;
  String r0 = row(b, P, "SkyyIsPTop", 46, null);
  lbl(b, r0, 860, 42, 14, false, "#cfe3ff", false, ed ? "Click a cell to allow or deny. Allowing a role also allows every role to its right; denying it also denies every role to its left." : "Only the owner and island admins can change these.");
  if (ed) {
    gap(b, r0, 20, 40);
    btn(b, ev, r0, "SkyyIsPdef", this.confirm.equals("pdef") ? "Click again to reset" : "Reset to defaults", 300, 40, style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 16), "pdef");
  }
  lbl(b, P, 0, 22, 13, false, "#9fb8d0", false, @PKG@.IslandCfg.STRICT_OTHER ? "Server rule: a player who has a role here on ANOTHER of their profiles only gets doors, seats and mobs while on the wrong profile (no items move between profiles)." : "Server rule: a player who has a role here on ANOTHER of their profiles can't drop items while on the wrong profile.");
  String rh = row(b, P, "SkyyIsPHdr", 30, null);
  lbl(b, rh, 450, 30, 15, true, "#9fb8d0", false, "   What");
  String[] cols = new String[] { "Visitor", "Trusted", "Member", "Admin" };
  for (int c = 0; c < 4; c++) {
    lbl(b, rh, 150, 30, 15, true, "#9fb8d0", true, cols[c]);
    gap(b, rh, 10, 30);
  }
  lbl(b, rh, 100, 30, 15, true, "#9fb8d0", true, "Owner");
  String letters = "vtma";
  for (int i = 0; i < s.perm.length && i < @PKG@.IslandPerms.LABELS.length; i++) {
    String r = row(b, P, "SkyyIsPRow" + i, 38, i % 2 == 0 ? "#132236(0.9)" : null);
    twoLine(b, r, 450, 38, @PKG@.IslandPerms.LABELS[i], @PKG@.IslandPerms.HINTS[i]);
    for (int c = 0; c < 4; c++) {
      boolean yes = c >= s.perm[i];
      String bg = yes ? "#2f6a3a" : "#6a2f2f";
      String code = two(i) + String.valueOf(letters.charAt(c));
      if (ed) btn(b, ev, r, "SkyyIsPc" + code, yes ? "YES" : "NO", 150, 34, style(bg, yes ? "#3f8a4c" : "#8a3f3f", bg, "#ffffff", 16), "pc" + code);
      else cell(b, r, 150, 34, bg, yes ? "YES" : "NO");
      gap(b, r, 10, 34);
    }
    lbl(b, r, 100, 34, 14, false, "#8f9aa8", true, "always");
  }
}""")
M(page, r"""
public void buildVisitors(@UCB@ b, @UEB@ ev, java.util.UUID u, String k, String hk, @PKG@.IslandSettings s, int rank) {
  String P = "#SkyyIsBody";
  if (s.world == null) {
    gap(b, P, 0, 30);
    lbl(b, P, 0, 34, 18, true, "#cfe3ff", true, "Create your island first (Overview tab).");
    return;
  }
  boolean ed = rank >= 3;
  String gold = style("#7a5a10", "#9a7418", "#4a3608", "#fff0c8", 16);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 16);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 16);
  String grey = style("#2a3340", "#3a4556", "#1a2230", "#c8d4e0", 16);
  lbl(b, P, 0, 30, 18, true, "#e6f2ff", false, "Who may visit");
  if (ed) {
    String r = row(b, P, "SkyyIsVmRow", 60, null);
    String[] t = new String[] { "Public (anyone)", "Friends (members + trusted)", "Closed (members only)" };
    for (int i = 0; i < 3; i++) {
      if (i > 0) gap(b, r, 20, 54);
      btn(b, ev, r, "SkyyIsVm" + i, t[i], 380, 54, i == s.mode ? gold : bs, "vm" + i);
    }
  } else lbl(b, P, 0, 34, 17, false, "#ffe08a", false, "Visits: " + @PKG@.IslandCfg.modeLabel(s.mode));
  String r2 = row(b, P, "SkyyIsVlRow", 52, null);
  lbl(b, r2, 170, 46, 17, true, "#e6f2ff", false, "Visitor limit");
  if (ed) {
    btn(b, ev, r2, "SkyyIsVlm", "-", 60, 44, bs, "vlm");
    lbl(b, r2, 80, 46, 20, true, "#ffe08a", true, String.valueOf(s.limit));
    btn(b, ev, r2, "SkyyIsVlp", "+", 60, 44, bs, "vlp");
  } else lbl(b, r2, 200, 46, 18, true, "#ffe08a", false, String.valueOf(s.limit));
  gap(b, r2, 60, 46);
  lbl(b, r2, 140, 46, 17, true, "#e6f2ff", false, "Visit ping");
  if (ed) btn(b, ev, r2, "SkyyIsVn", s.notify ? "On" : "Off", 140, 44, s.notify ? gs : grey, "vn");
  else lbl(b, r2, 140, 46, 17, true, "#ffe08a", false, s.notify ? "On" : "Off");
  lbl(b, r2, 480, 46, 13, false, "#9fb8d0", false, "   Ping = a chat line to the owner and members when someone visits.");
  gap(b, P, 0, 6);
  java.util.ArrayList vu = new java.util.ArrayList();
  java.util.ArrayList vn = new java.util.ArrayList();
  java.util.ArrayList vr = new java.util.ArrayList();
  @WLD@ w = @PKG@.IslandStore.loadedWorld(s.world);
  if (w != null) {
    java.util.Iterator it = w.getPlayerRefs().iterator();
    while (it.hasNext()) {
      @PR@ p = (@PR@) it.next();
      if (p == null || !p.isValid()) continue;
      vu.add(p.getUuid().toString());
      vn.add(p.getUsername());
      vr.add(Integer.valueOf(@PKG@.IslandPerms.isAdmin(p) ? 9 : @PKG@.IslandPerms.rank(hk, p.getUuid(), s)));
    }
  }
  String[] bn = @PKG@.IslandStore.split(s.banned);
  String rh = row(b, P, "SkyyIsVHdr", 30, null);
  lbl(b, rh, 700, 30, 16, true, "#9fb8d0", false, "   On the island now (" + vu.size() + ")" + (w == null ? " - the island is not loaded" : ""));
  gap(b, rh, 20, 30);
  lbl(b, rh, 470, 30, 16, true, "#9fb8d0", false, "Banned (" + bn.length + " / " + @PKG@.IslandCfg.BANS_MAX + ")");
  this.visUuids = new java.util.ArrayList();
  this.banKeys = new java.util.ArrayList();
  int per = 8;
  int bpages = (bn.length + per - 1) / per;
  if (bpages < 1) bpages = 1;
  if (this.banPage >= bpages) this.banPage = bpages - 1;
  if (this.banPage < 0) this.banPage = 0;
  int bstart = this.banPage * per;
  for (int i = 0; i < per; i++) {
    boolean hasV = i < vu.size();
    int bi = bstart + i;
    boolean hasB = bi < bn.length;
    if (!hasV && !hasB) break;
    String r = row(b, P, "SkyyIsVRow" + i, 42, i % 2 == 0 ? "#132236(0.9)" : null);
    if (hasV) {
      String us = (String) vu.get(i);
      this.visUuids.add(us);
      boolean me = us.equals(u.toString());
      int tr = ((Integer) vr.get(i)).intValue();
      boolean adm = tr == 9;
      int used = 0;
      lbl(b, r, 230, 40, 16, true, "#ffffff", false, "  " + vn.get(i) + (me ? " (you)" : ""));
      lbl(b, r, 120, 40, 15, true, adm ? "#ffb070" : @PKG@.IslandPerms.roleColor(tr), false, adm ? "Server admin" : @PKG@.IslandPerms.roleName(tr));
      used = 350;
      if (!me && !adm && tr <= 1 && rank >= 2) { btn(b, ev, r, "SkyyIsVe" + i, "Expel", 110, 36, bs, "ve" + i); gap(b, r, 6, 36); used += 116; }
      if (!me && !adm && tr == 0 && rank >= 3) { btn(b, ev, r, "SkyyIsVt" + i, "Trust", 110, 36, gs, "vt" + i); gap(b, r, 6, 36); used += 116; }
      if (!me && !adm && tr <= 1 && rank >= 3) { btn(b, ev, r, "SkyyIsVb" + i, this.confirm.equals("vb:" + us) ? "Sure?" : "Ban", 110, 36, rs, "vb" + i); used += 110; }
      if (used < 700) gap(b, r, 700 - used, 40);
    } else {
      this.visUuids.add("");
      gap(b, r, 700, 40);
    }
    gap(b, r, 20, 40);
    if (hasB) {
      this.banKeys.add(bn[bi]);
      lbl(b, r, 310, 40, 16, false, "#ffb0b0", false, @PKG@.IslandStore.nameOf(s, bn[bi]));
      if (rank >= 3) btn(b, ev, r, "SkyyIsVu" + i, "Unban", 140, 36, bs, "vu" + i);
    } else this.banKeys.add("");
  }
  if (vu.isEmpty() && bn.length == 0) lbl(b, P, 0, 30, 15, false, "#9fb8d0", false, "   Nobody is on the island right now, and nobody is banned.");
  gap(b, P, 0, 6);
  String rn = row(b, P, "SkyyIsVNav", 44, null);
  btn(b, ev, rn, "SkyyIsVr", "Refresh list", 180, 40, bs, "vr");
  if (bpages > 1) {
    gap(b, rn, 540, 40);
    btn(b, ev, rn, "SkyyIsBp", "< Prev", 120, 40, bs, "bp");
    lbl(b, rn, 150, 40, 15, false, "#9fb8d0", true, "Bans " + (this.banPage + 1) + " / " + bpages);
    btn(b, ev, rn, "SkyyIsBn", "Next >", 120, 40, bs, "bn");
  }
}""")
M(page, r"""
public void buildIsland(@UCB@ b, @UEB@ ev, java.util.UUID u, String hk, @PKG@.IslandSettings s, int rank) {
  String P = "#SkyyIsBody";
  if (s.world == null) {
    gap(b, P, 0, 30);
    lbl(b, P, 0, 34, 18, true, "#cfe3ff", true, "Create your island first (Overview tab).");
    return;
  }
  boolean ed = rank >= 3;
  String red = style("#7a2424", "#9a3030", "#4a1414", "#ffe6e6", 18);
  String grey = style("#2a3340", "#3a4556", "#1a2230", "#e6f2ff", 18);
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 18);
  gap(b, P, 0, 10);
  lbl(b, P, 0, 34, 20, true, "#e6f2ff", false, "Island rules");
  String r1 = row(b, P, "SkyyIsIpRow", 60, "#132236(0.9)");
  lbl(b, r1, 380, 56, 18, true, "#ffffff", false, "   PvP - players can hurt each other");
  if (ed) btn(b, ev, r1, "SkyyIsIp", s.pvp ? "ON" : "OFF", 180, 52, s.pvp ? red : grey, "ipvp");
  else lbl(b, r1, 180, 56, 18, true, s.pvp ? "#ff9d6b" : "#c8d4e0", true, s.pvp ? "ON" : "OFF");
  lbl(b, r1, 620, 56, 14, false, "#9fb8d0", false, "    Turning PvP on sends visitors to the hub. Members and trusted players stay.");
  gap(b, P, 0, 8);
  String r2 = row(b, P, "SkyyIsIsRow", 60, "#132236(0.9)");
  lbl(b, r2, 380, 56, 18, true, "#ffffff", false, "   Mob spawning");
  if (ed) btn(b, ev, r2, "SkyyIsIs", s.spawning ? "ON" : "OFF", 180, 52, s.spawning ? gs : grey, "ispawn");
  else lbl(b, r2, 180, 56, 18, true, "#c8d4e0", true, s.spawning ? "ON" : "OFF");
  lbl(b, r2, 620, 56, 14, false, "#9fb8d0", false, "    Needs a biome with wildlife - Void Sky (today's islands) has none, so nothing spawns yet.");
  gap(b, P, 0, 20);
  lbl(b, P, 0, 28, 15, false, "#cfe3ff", false, "Coming in a later version: island biome (grass colour, sky, weather, wildlife), a weather lock and a visitor landing point.");
  if (!ed) lbl(b, P, 0, 28, 15, false, "#9fb8d0", false, "Only the owner and island admins can change these.");
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  this.nid = 0;
  long now = System.currentTimeMillis();
  if (this.confirmUntil < now) this.confirm = "";
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.IslandStore.pkey(u);
  String hk = @PKG@.IslandStore.homeKey(u);
  @PKG@.IslandSettings s = @PKG@.IslandStore.settings(hk);
  int rank = @PKG@.IslandPerms.rank(hk, u, s);
  boolean has = s.world != null;
  b.appendInline((String) null, "Group #SkyyIsRoot { Anchor: (Width: 1240, Height: 900); Background: #0b1524(0.96); Padding: (Horizontal: 20, Vertical: 12); LayoutMode: Top; }");
  b.appendInline("#SkyyIsRoot", "Group { Anchor: (Height: 3); Background: #ffd070; }");
  lbl(b, "#SkyyIsRoot", 0, 44, 26, true, "#ffe08a", true, has ? @PKG@.IslandStore.ownerDisplay(hk, s) + "'s Island" : "Your Island");
  String sub = "Your role: " + @PKG@.IslandPerms.roleName(rank) + @PKG@.IslandStore.profileLabel(u);
  if (has) sub = sub + "      Co-op " + (1 + @PKG@.IslandStore.count(s.members)) + " / " + @PKG@.IslandCfg.COOP_MAX + "      Visits: " + @PKG@.IslandCfg.modeName(s.mode);
  lbl(b, "#SkyyIsRoot", 0, 28, 16, false, @PKG@.IslandPerms.roleColor(rank), true, sub);
  buildTabs(b, ev);
  gap(b, "#SkyyIsRoot", 0, 8);
  b.appendInline("#SkyyIsRoot", "Group #SkyyIsBody { Anchor: (Height: 640); LayoutMode: Top; }");
  try {
    if (s.bad) lbl(b, "#SkyyIsBody", 0, 60, 18, true, "#ff9d6b", true, "Your island file can't be read right now - click Refresh in a moment. Nothing was changed.");
    else if (this.tab == 1) buildMembers(b, ev, u, k, hk, s, rank);
    else if (this.tab == 2) buildPerms(b, ev, u, hk, s, rank);
    else if (this.tab == 3) buildVisitors(b, ev, u, k, hk, s, rank);
    else if (this.tab == 4) buildIsland(b, ev, u, hk, s, rank);
    else buildOverview(b, ev, u, k, hk, s, rank);
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("island menu tab " + this.tab + " failed: " + t);
    lbl(b, "#SkyyIsBody", 0, 34, 16, false, "#ff9d6b", true, "This tab could not be drawn - the server log has the details.");
  }
  lbl(b, "#SkyyIsRoot", 0, 32, 17, true, @PKG@.IslandStore.colorOf(this.info), true, @PKG@.IslandStore.textOf(this.info));
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 17);
  b.appendInline("#SkyyIsRoot", "Group #SkyyIsBottom { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 4); }");
  gap(b, "#SkyyIsBottom", 400, 44);
  btn(b, ev, "#SkyyIsBottom", "SkyyIsRef", "Refresh", 180, 44, bs, "refresh");
  gap(b, "#SkyyIsBottom", 20, 44);
  btn(b, ev, "#SkyyIsBottom", "SkyyIsClose", "Close", 180, 44, bs, "close");
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    @PR@ me = this.playerRef;
    java.util.UUID u = me.getUuid();
    long now = System.currentTimeMillis();
    if (this.confirmUntil < now) this.confirm = "";
    @WLD@ world = null;
    try {
      Object ext = st.getExternalData();
      if (ext instanceof @EST@) world = ((@EST@) ext).getWorld();
    } catch (Throwable t) { world = null; }
    if (a.equals("close")) { closePage(ref, st); return; }
    int nt = -1;
    if (a.equals("tabov")) nt = 0;
    else if (a.equals("tabmem")) nt = 1;
    else if (a.equals("tabperm")) nt = 2;
    else if (a.equals("tabvis")) nt = 3;
    else if (a.equals("tabisl")) nt = 4;
    if (nt >= 0) { this.tab = nt; this.info = ""; this.confirm = ""; rebuild(); return; }
    if (a.equals("refresh") || a.equals("vr")) { this.info = ""; this.confirm = ""; rebuild(); return; }
    String was = this.confirm;
    this.confirm = "";
    String res = null;
    String k = @PKG@.IslandStore.pkey(u);
    String hk = @PKG@.IslandStore.homeKey(u);
    if (a.equals("create")) {
      if (world != null) @PKG@.IslandCmd.go(st, ref, me, world, k, true);
      closePage(ref, st);
      return;
    }
    if (a.equals("go")) {
      if (world != null) @PKG@.IslandCmd.goHome(st, ref, me, world);
      closePage(ref, st);
      return;
    }
    if (a.equals("acc")) res = @PKG@.IslandCoop.accept(me);
    else if (a.equals("dec")) res = @PKG@.IslandCoop.decline(me);
    else if (a.equals("leave")) {
      if (was.equals("leave")) {
        res = @PKG@.IslandCoop.leave(st, ref, me, world);
        if (res.startsWith("+")) { @PKG@.IslandStore.tell(me, res); closePage(ref, st); return; }
      } else { this.confirm = "leave"; this.confirmUntil = now + 10000L; res = "=Click again within 10 s to leave. Your own island becomes your home again."; }
    } else if (a.equals("disb")) {
      if (was.equals("disb")) res = @PKG@.IslandCoop.disband(me, true);
      else {
        res = @PKG@.IslandCoop.disbandProblem(me);
        if (res == null) { this.confirm = "disb"; this.confirmUntil = now + 10000L; res = "=Click again within 10 s to remove every co-op member (trusted players, bans and settings stay)."; }
      }
    } else if (a.equals("reset")) {
      String bad = @PKG@.IslandCoop.resetCheck(me);
      if (bad != null) res = bad;
      else if (was.equals("reset2")) {
        res = @PKG@.IslandCoop.resetNow(st, ref, me, world);
        if (res.startsWith("+")) { @PKG@.IslandStore.tell(me, res); closePage(ref, st); return; }
      } else if (was.equals("reset1")) {
        this.confirm = "reset2"; this.confirmUntil = now + @PKG@.IslandCfg.RESET_CONFIRM * 1000L;
        res = @PKG@.IslandCoop.resetWarning(2, true);
      } else {
        this.confirm = "reset1"; this.confirmUntil = now + @PKG@.IslandCfg.RESET_CONFIRM * 1000L;
        res = @PKG@.IslandCoop.resetWarning(1, true);
      }
    } else if (a.equals("name")) {
      String nm = @PKG@.IslandStore.cleanName(jsonStr(data, "@IsName"));
      this.keepName = nm;
      res = nm.length() == 0 ? "=Type a player's name, then click Invite to co-op or Trust." : "=Click Invite to co-op or Trust (build only) for " + nm + ". Enter alone does nothing.";
    } else if (a.equals("invite") || a.equals("trust")) {
      String nm = @PKG@.IslandStore.cleanName(jsonStr(data, "@IsName"));
      if (nm.length() == 0) res = "-Type a player's name in the box first.";
      else {
        @PR@ t = @PKG@.IslandStore.findOnline(nm);
        if (t == null) res = "-Nobody called " + nm + " is online right now.";
        else res = a.equals("invite") ? @PKG@.IslandCoop.invite(me, t) : @PKG@.IslandCoop.trust(me, t);
      }
      this.keepName = res.startsWith("-") ? nm : "";
    } else if (a.equals("tp")) this.trustPage = this.trustPage - 1;
    else if (a.equals("tn")) this.trustPage = this.trustPage + 1;
    else if (a.equals("bp")) this.banPage = this.banPage - 1;
    else if (a.equals("bn")) this.banPage = this.banPage + 1;
    else if (a.equals("vm0")) res = @PKG@.IslandCoop.setMode(me, 0);
    else if (a.equals("vm1")) res = @PKG@.IslandCoop.setMode(me, 1);
    else if (a.equals("vm2")) res = @PKG@.IslandCoop.setMode(me, 2);
    else if (a.equals("vlm")) res = @PKG@.IslandCoop.changeLimit(me, -1);
    else if (a.equals("vlp")) res = @PKG@.IslandCoop.changeLimit(me, 1);
    else if (a.equals("vn")) res = @PKG@.IslandCoop.toggleNotify(me);
    else if (a.equals("ipvp")) res = @PKG@.IslandCoop.togglePvp(me);
    else if (a.equals("ispawn")) res = @PKG@.IslandCoop.toggleSpawning(me);
    else if (a.equals("pdef")) {
      if (was.equals("pdef")) res = @PKG@.IslandCoop.resetPerms(me);
      else { this.confirm = "pdef"; this.confirmUntil = now + 10000L; res = "=Click again within 10 s to put every permission back to the server defaults."; }
    } else if (a.startsWith("pc") && a.length() == 5) {
      int f = -1;
      try { f = Integer.parseInt(a.substring(2, 4)); } catch (Throwable t) { f = -1; }
      int r = "vtma".indexOf(a.charAt(4));
      if (f < 0 || r < 0) return;
      res = @PKG@.IslandCoop.clickPerm(me, f, r);
    } else if (a.length() >= 3) {
      String p2 = a.substring(0, 2);
      int i = idx(a, 2);
      if (i < 0) return;
      if (p2.equals("pr") || p2.equals("dm") || p2.equals("kk")) {
        if (i >= this.rowKeys.size()) return;
        String key = (String) this.rowKeys.get(i);
        if (p2.equals("pr")) res = @PKG@.IslandCoop.promoteKey(me, key, true);
        else if (p2.equals("dm")) res = @PKG@.IslandCoop.promoteKey(me, key, false);
        else if (was.equals("kk:" + key)) res = @PKG@.IslandCoop.kickByKey(me, key);
        else {
          this.confirm = "kk:" + key; this.confirmUntil = now + 10000L;
          res = "=Click Sure? within 10 s to remove " + @PKG@.IslandStore.nameOf(@PKG@.IslandStore.settings(hk), key) + " from the co-op.";
        }
      } else if (p2.equals("ut")) {
        if (i >= this.trustKeys.size()) return;
        res = @PKG@.IslandCoop.untrustByKey(me, (String) this.trustKeys.get(i));
      } else if (p2.equals("ve") || p2.equals("vt") || p2.equals("vb")) {
        if (i >= this.visUuids.size()) return;
        String us = (String) this.visUuids.get(i);
        if (us.length() == 0) return;
        @PR@ t = null;
        try { t = @PKG@.IslandStore.online(java.util.UUID.fromString(us)); } catch (Throwable x) { t = null; }
        if (t == null) res = "-That player is not online any more.";
        else if (p2.equals("ve")) res = @PKG@.IslandCoop.expelOn(me, hk, t);
        else if (p2.equals("vt")) res = @PKG@.IslandCoop.trust(me, t);
        else if (was.equals("vb:" + us)) res = @PKG@.IslandCoop.ban(me, t);
        else { this.confirm = "vb:" + us; this.confirmUntil = now + 10000L; res = "=Click Sure? within 10 s to ban " + t.getUsername() + " from the island."; }
      } else if (p2.equals("vu")) {
        if (i >= this.banKeys.size()) return;
        String bk = (String) this.banKeys.get(i);
        if (bk.length() == 0) return;
        res = @PKG@.IslandCoop.unbanByKey(me, bk);
      } else return;
    } else return;
    this.info = res == null ? "" : res;
    rebuild();
  } catch (Throwable t) { @PKG@.IslandStore.warn("island menu click failed: " + t); }
}""")

# =====================================================================================================================
# /island subcommands (constructor + execute BEFORE the IslandCmd constructor that does addSubCommand(new ...)).
# Every one: setPermissionGroups hytale:Adventurer (@ADV@) and REQUIRED args only (optional args are flags, not positional).
# =====================================================================================================================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
SUBS = []


def sub(clsname, name, desc, body, aliases=(), args=()):
    """args = [(field, argName, argDesc, "PLAYER_REF" | "STRING")], read into a0, a1 (PlayerRef or null / String)."""
    c = K(clsname, T["APC"])
    for (fld, _an, _ad, _ty) in args:
        F(c, "public @RA@ %s;" % fld)
    lines = ['super("%s", "%s");' % (name, desc), "@ADV@"]
    if aliases:
        lines.append("addAliases(new String[] { %s });" % ", ".join('"%s"' % a for a in aliases))
    for (fld, an, ad, ty) in args:
        lines.append('this.%s = withRequiredArg("%s", "%s", @ATY@.%s);' % (fld, an, ad, ty))
    C(c, "public %s() {\n  %s\n}" % (clsname, "\n  ".join(lines)))
    reads = ""
    for i, (fld, an, ad, ty) in enumerate(args):
        if ty == "PLAYER_REF":
            reads += "    Object o%d = ctx.get(this.%s);\n    @PR@ a%d = null;\n    if (o%d instanceof @PR@) a%d = (@PR@) o%d;\n" % (i, fld, i, i, i, i)
        else:
            reads += "    String a%d = String.valueOf(ctx.get(this.%s));\n" % (i, fld)
    M(c, EXEC + " {\n  try {\n" + reads + "    " + body + "\n  } catch (Throwable t) {\n"
      "    @PKG@.IslandStore.warn(\"/island " + name + " failed: \" + t);\n"
      "    @PKG@.IslandStore.tell(pr, \"-Something went wrong - the server log has the details.\");\n  }\n}")
    SUBS.append(c)
    return c


S = "@PKG@.IslandStore.tell(pr, @PKG@.IslandCoop."
PLAYER = [("targetArg", "player", "an online player", "PLAYER_REF")]
NAME = [("nameArg", "name", "player name (works offline for list members)", "STRING")]
sub("IslandInfoCmd", "info", "Your home island: owner, your role, members, trusted, visits, world",
    "@PKG@.IslandCmd.info(pr, world);")
sub("IslandHomeCmd", "home", "Go to your island (same as /island; co-op members go to the co-op island)",
    "@PKG@.IslandCmd.goHome(store, ref, pr, world);", aliases=("go",))
sub("IslandMenuCmd", "menu", "Open the island menu: members, permissions, visitors, island settings", r"""@PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { @PKG@.IslandStore.tell(pr, "-Could not open the island menu."); return; }
    p.getPageManager().openCustomPage(ref, store, new @PKG@.IslandMenuPage(pr));""", aliases=("settings", "options"))
sub("IslandVisitCmd", "visit", "Visit a player's island (their co-op island if they are in one)",
    "@PKG@.IslandCmd.visit(store, ref, pr, world, a0);", aliases=("warp",), args=PLAYER)
sub("IslandInviteCmd", "invite", "Invite a player to JOIN your island as a co-op member (they /island accept)",
    S + "invite(pr, a0));", aliases=("add",), args=PLAYER)
sub("IslandAcceptCmd", "accept", "Accept your island co-op invite (joins with your current profile)", S + "accept(pr));")
sub("IslandDeclineCmd", "decline", "Decline your island co-op invite", S + "decline(pr));")
sub("IslandLeaveCmd", "leave", "Leave the island co-op you are in (your own island comes back)", S + "leave(store, ref, pr, world));")
sub("IslandKickCmd", "kick", "Owner: remove a co-op member", S + "kick(pr, a0));", aliases=("remove",), args=NAME)
sub("IslandPromoteCmd", "promote", "Owner: make a co-op member an island admin (can change settings)", S + "promote(pr, a0, true));", args=NAME)
sub("IslandDemoteCmd", "demote", "Owner: make an island admin a normal co-op member", S + "promote(pr, a0, false));", args=NAME)
sub("IslandDisbandCmd", "disband", "Owner: end the co-op (repeat within 10 s); trusted players, bans and settings stay",
    S + "disband(pr, false));")
sub("IslandTrustCmd", "trust", "Owner/admin: give a player build rights on your island (not a co-op member)", S + "trust(pr, a0));", args=PLAYER)
sub("IslandUntrustCmd", "untrust", "Owner/admin: take a player's build rights away", S + "untrust(pr, a0));", args=NAME)
sub("IslandResetCmd", "reset", "Owner: rebuild your island from scratch with a fresh starter kit (3 times within 20 s; once per 24 h)",
    S + "resetCmd(store, ref, pr, world));")
sub("IslandExpelCmd", "expel", "Send a visitor or trusted player off the island to the hub (60 s block)", S + "expel(pr, world, a0));", args=PLAYER)
sub("IslandBanCmd", "ban", "Owner/admin: ban a player from your island (all their profiles)", S + "ban(pr, a0));", args=PLAYER)
sub("IslandUnbanCmd", "unban", "Owner/admin: lift an island ban", S + "unban(pr, a0));", args=NAME)
sub("IslandBansCmd", "bans", "List the players banned from your island", S + "bansText(pr));", aliases=("banlist",))
sub("IslandLockCmd", "lock", "Owner/admin: close the island to everyone but co-op members", S + "lock(pr, true));")
sub("IslandUnlockCmd", "unlock", "Owner/admin: restore the visit setting from before /island lock", S + "lock(pr, false));")
# 0.5 review: /island reload = server admins only (skyyislands.admin, NOT hytale:Adventurer) - config.properties + every island file
# again after hand edits (the /profileadmin reload pattern); an unreadable file keeps its last good copy
rlc = K("IslandReloadCmd", T["APC"])
C(rlc, r"""
public IslandReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyIslands/config.properties and every island file after hand edits");
  requirePermission("skyyislands.admin");
  setPermissionGroups(new String[0]);   // 0.5.1: do NOT inherit /island's hytale:Adventurer (it handed every player skyyislands.admin)
}""")
M(rlc, EXEC + r""" {
  try {
    if (!@PKG@.IslandPerms.isAdmin(pr)) { @PKG@.IslandStore.tell(pr, "-Only server admins (skyyislands.admin) can reload SkyyIslands."); return; }
    @PKG@.IslandStore.tell(pr, @PKG@.IslandStore.reloadText());
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("/island reload failed: " + t);
    @PKG@.IslandStore.tell(pr, "-Something went wrong - the server log has the details.");
  }
}""")
SUBS.append(rlc)

# ---- /island root: no positional token -> own execute (go home, or the old --action/--player flag form)
C(icmd, r"""
public IslandCmd() {
  super("island", "Your private island. /island (go) | menu | info | visit <player> | invite <player> | accept | leave | trust <player> | kick | reset - /island menu shows everything");
  addAliases(new String[] { "is" });
  this.actionArg = withOptionalArg("action", "old flag form: invite | visit | info | home (prefer /island visit <player>)", @ATY@.STRING);
  this.targetArg = withOptionalArg("player", "old flag form: player to invite / visit", @ATY@.PLAYER_REF);
  @ADV@
%s
}""" % "\n".join("  addSubCommand(new @PKG@.%s());" % c.getSimpleName() for c in SUBS))
M(icmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!ctx.provided(this.actionArg)) { goHome(store, ref, pr, world); return; }
    String a = String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase();
    if (a.equals("info")) { info(pr, world); return; }
    if (a.equals("home") || a.equals("go")) { goHome(store, ref, pr, world); return; }
    if (a.equals("menu") || a.equals("settings")) { @PKG@.IslandStore.tell(pr, "=Use /island menu"); return; }
    if (!ctx.provided(this.targetArg)) { @PKG@.IslandStore.tell(pr, "=Usage: /island | /island menu | /island invite <player> | /island visit <player> | /island info"); return; }
    @PR@ target = (@PR@) ctx.get(this.targetArg);
    if (target == null || !target.isValid()) { @PKG@.IslandStore.tell(pr, "-That player is not online."); return; }
    if (a.equals("invite") || a.equals("add")) { @PKG@.IslandStore.tell(pr, @PKG@.IslandCoop.invite(pr, target)); return; }
    if (a.equals("visit") || a.equals("warp")) { visit(store, ref, pr, world, target); return; }
    @PKG@.IslandStore.tell(pr, "=Usage: /island | /island menu | /island invite <player> | /island visit <player> | /island info");
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("/island error: " + t);
    @PKG@.IslandStore.tell(pr, "-Something went wrong: " + t.getMessage());
  }
}""")

# ================= /hub =================
C(hcmd, r"""
public HubCmd() {
  super("hub", "Leave your island and return to the main world");
  addAliases(new String[] { "lobby" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(hcmd, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    pr.sendMessage(@MSG@.raw("[Island] Warping to the hub..."));
    if (!sendToHub(store, ref, pr, world)) pr.sendMessage(@MSG@.raw("[Island] No hub is set and no default world spawn was found. An admin can stand somewhere and run /sethub."));
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("/hub failed: " + t);
    pr.sendMessage(@MSG@.raw("[Island] Could not warp: " + t.getMessage()));
  }
}""")

# ================= /sethub (admin) =================
C(shub, r"""
public SetHubCmd() {
  super("sethub", "(admin) Set the server hub point to where you stand");
  requirePermission("skyyislands.admin");
}""")
M(shub, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (@PKG@.IslandStore.isIslandWorld(world.getName())) { pr.sendMessage(@MSG@.raw("[Island] The hub cannot be inside an island world.")); return; }
    @TC@ tc = (@TC@) store.getComponent(ref, @TC@.getComponentType());
    if (tc == null || tc.getTransform() == null) { pr.sendMessage(@MSG@.raw("[Island] Could not read your position.")); return; }
    @TRF@ t = tc.getTransform();
    org.joml.Vector3d p = t.getPosition();
    @R3F@ r = t.getRotation();
    @PKG@.IslandStore.saveHub(world.getName(), p.x, p.y, p.z, r == null ? 0f : r.x, r == null ? 0f : r.y, r == null ? 0f : r.z);
    pr.sendMessage(@MSG@.raw("[Island] Hub set here in world '" + world.getName() + "' (" + (int) p.x + ", " + (int) p.y + ", " + (int) p.z + "). /hub and island logins now come here."));
  } catch (Throwable t) {
    @PKG@.IslandStore.warn("/sethub failed: " + t);
    pr.sendMessage(@MSG@.raw("[Island] Could not set the hub: " + t.getMessage()));
  }
}""")

# ================= login routing (0.2.1) + arrival (0.5): PlayerReadyEvent -> world thread =================
rout.addInterface(pool.get("java.lang.Runnable"))
F(rout, "public @PR@ pr;")
C(rout, "public RouteTask(@PR@ pr) { this.pr = pr; }")
M(rout, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null || !@PKG@.IslandStore.isIslandWorld(w.getName())) return;
    @REF@ r = pr.getReference();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    if (@PKG@.HubCmd.sendToHub(st, r, pr, w)) pr.sendMessage(@MSG@.raw("[Island] Welcome back! You start in the hub - /island takes you home."));
  } catch (Throwable t) { @PKG@.IslandStore.warn("login routing failed: " + t); }
}""")
disp.addInterface(pool.get("java.lang.Runnable"))
F(disp, "public @PR@ pr;")
C(disp, "public RouteDispatch(@PR@ pr) { this.pr = pr; }")
M(disp, r"""
public void run() {
  try {
    if (pr == null || !pr.isValid()) return;
    java.util.UUID wu = pr.getWorldUuid();
    if (wu == null) return;
    @WLD@ w = @UNI@.get().getWorld(wu);
    if (w == null) return;
    w.execute(new @PKG@.RouteTask(pr));
  } catch (Throwable t) { }
}""")
M(rout, r"""
public static void schedule(@PR@ pr) {
  @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.RouteDispatch(pr), 1500L, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
rdy.addInterface(pool.get("java.util.function.Consumer"))
C(rdy, "public IslandReady() { }")
# first ready of the online session = login routing (unchanged); every later ready inside an island world = ArrivalTask (+1.5 s)
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
    if (@PKG@.IslandStore.SEEN.putIfAbsent(pr.getUuid(), Boolean.TRUE) == null) { @PKG@.RouteTask.schedule(pr); return; }
    String wn = null;
    Object ext = st.getExternalData();
    if (ext instanceof @EST@) {
      @WLD@ w = ((@EST@) ext).getWorld();
      if (w != null) wn = w.getName();
    }
    if (wn == null || !@PKG@.IslandStore.isIslandWorld(wn)) return;
    @PKG@.ArrivalTask.schedule(pr, wn, 1, 1500L);
  } catch (Throwable t) { }
}""")

# ================= SeenTick (every 5 s): session pruning, island:<uuid> republish on profile switch, invite expiry, sweeps =========
seen.addInterface(pool.get("java.lang.Runnable"))
F(seen, "public int runs;")
C(seen, "public SeenTick() { }")
M(seen, r"""
public static void prune(java.util.concurrent.ConcurrentHashMap m, long now, long age) {
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = m.get(k);
    long t = -1L;
    if (v instanceof Long) t = ((Long) v).longValue();
    else if (v instanceof Object[] && ((Object[]) v).length > 1 && ((Object[]) v)[1] instanceof Long) t = ((Long) ((Object[]) v)[1]).longValue();
    if (t >= 0L && now - t > age) m.remove(k, v);
  }
}""")
M(seen, r"""
public void run() {
  try {
    java.util.HashSet online = new java.util.HashSet();
    java.util.ArrayList prs = new java.util.ArrayList();
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr != null && pr.isValid()) { online.add(pr.getUuid()); prs.add(pr); }
    }
    this.runs = this.runs + 1;
    if (this.runs % 2 == 0) {
      @PKG@.IslandStore.SEEN.keySet().retainAll(online);
      @PKG@.IslandStore.WARNED.keySet().retainAll(online);
      @PKG@.IslandStore.EXPELLING.keySet().retainAll(online);
    }
    @PKG@.IslandStore.EPOCH.keySet().retainAll(online);
    java.util.Map b = @PKG@.IslandStore.bridge();
    java.util.Iterator ou = online.iterator();
    while (ou.hasNext()) {
      java.util.UUID u = (java.util.UUID) ou.next();
      Object e = b.get("profile:epoch:" + u);
      String es = e == null ? "none" : String.valueOf(e);
      Object last = @PKG@.IslandStore.EPOCH.get(u);
      if (last != null && last.equals(es)) continue;
      @PKG@.IslandStore.EPOCH.put(u, es);
      @PKG@.IslandStore.publish(u);
    }
    long now = System.currentTimeMillis();
    java.util.Iterator ii = @PKG@.IslandStore.INVITES.keySet().iterator();
    while (ii.hasNext()) {
      Object tk = ii.next();
      Object o = @PKG@.IslandStore.INVITES.get(tk);
      if (!(o instanceof Object[])) continue;
      Object[] inv = (Object[]) o;
      if (((Long) inv[2]).longValue() >= now) continue;
      if (!@PKG@.IslandStore.INVITES.remove(tk, o)) continue;
      java.util.UUID tu = (java.util.UUID) tk;
      @PR@ tp = @PKG@.IslandStore.online(tu);
      @PKG@.IslandStore.sayU(tu, "[Island] The island invite from " + inv[3] + " ran out.", "#9fb8d0");
      @PKG@.IslandStore.sayU((java.util.UUID) inv[1], "[Island] Your island invite to " + (tp == null ? "that player" : tp.getUsername()) + " ran out.", "#9fb8d0");
    }
    if (this.runs % 6 == 0 && !@PKG@.IslandStore.BAD.isEmpty()) @PKG@.IslandStore.retryBad();
    prune(@PKG@.IslandStore.EXPELLED, now, @PKG@.IslandCfg.EXPEL_SECONDS * 1000L + 1000L);
    prune(@PKG@.IslandStore.PINGED, now, 60000L);
    prune(@PKG@.IslandStore.CONFIRM, now, 300000L);
    java.util.HashSet worlds = new java.util.HashSet();
    for (int i = 0; i < prs.size(); i++) {
      @PR@ p = (@PR@) prs.get(i);
      java.util.UUID wu = p.getWorldUuid();
      if (wu == null) continue;
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null || !w.isAlive()) continue;
      String wn = w.getName();
      if (!@PKG@.IslandStore.isIslandWorld(wn) || worlds.contains(wn)) continue;
      worlds.add(wn);
      w.execute(new @PKG@.SweepTask(w, false));
    }
  } catch (Throwable t) { }
}""")

# ================= plugin =================
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyIslandsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.IslandStore.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyyIslands");
  @PKG@.IslandStore.DIR = base.resolve("islands");
  @PKG@.IslandCfg.FILE = base.resolve("config.properties");
  @PKG@.IslandCfg.load("%%ANIMALS%%");
  getCommandRegistry().registerCommand(new @PKG@.IslandCmd());
  getCommandRegistry().registerCommand(new @PKG@.HubCmd());
  getCommandRegistry().registerCommand(new @PKG@.SetHubCmd());
  @PKG@.IslandStore.HUB_FILE = base.resolve("hub.properties");
  @PKG@.IslandStore.loadHub();
  @PKG@.IslandStore.loadIslandWorlds();
  java.util.Map b = @PKG@.IslandStore.bridge();
  b.put("island:perm:fn", new @PKG@.PermFn());
  b.put("island:role:fn", new @PKG@.RoleFn());
  b.put("island:owner:fn", new @PKG@.OwnerFn());
  b.put("island:coop:fn", new @PKG@.CoopFn());
  @PKG@.IslandStore.bump();
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.IslandReady());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardDamage());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardBreak());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardPlace());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardPickup());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardUse());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardDrop());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardUseEntity());
  getEntityStoreRegistry().registerSystem(new @PKG@.GuardHurt());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SeenTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  boolean tpl = false;
  try { tpl = @INS@.doesInstanceAssetExist("SkyyIsland"); } catch (Throwable t) { }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyIslands] @VERSION@ ready - /island [menu|info|home|visit|invite|accept|decline|leave|kick|promote|demote|disband|trust|untrust|reset|expel|ban|unban|bans|lock|unlock] /hub /sethub (players: hytale:Adventurer), /island reload (admin); co-op + island settings (14 permission flags, visitors, PvP, spawning), one island per profile (hub " + (@PKG@.IslandStore.HUB_WORLD == null ? "NOT set - run /sethub" : "in " + @PKG@.IslandStore.HUB_WORLD) + ", " + @PKG@.IslandStore.ISLAND_WORLDS.size() + " island worlds known, " + @PKG@.IslandStore.MEMBER_OF.size() + " co-op members, " + @PKG@.IslandCfg.ANIMALS.size() + " farm animal roles, template SkyyIsland " + (tpl ? "found" : "NOT FOUND - check Server/Instances in the jar") + ")");
}""".replace("%%ANIMALS%%", ANIMALS_CSV))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.IslandStore.bridge();
    b.remove("island:perm:fn"); b.remove("island:role:fn"); b.remove("island:owner:fn"); b.remove("island:coop:fn");
  } catch (Throwable t) { }
  super.shutdown();
}""")

for c in ALL + SUBS + [pl]:
    c.writeFile(OUT)
print("classes written:", len(ALL + SUBS) + 1)

template = {
    "$Comment": "SkyyIslands starter island template - void world; the mod places the island blocks on first visit",
    "RequiredPlugins": {},
    "ChunkStorage": {"Type": "Hytale"},
    "GameMode": "Adventure",
    "IsPvpEnabled": False,
    "IsSpawningNPC": False,
    "GameTime": "0001-01-01T09:00:00Z",
    "UUID": {"$binary": "AAAAAAAAAAAAAAAAAAAAAA==", "$type": "04"},
    "GameplayConfig": "Default",
    "IsCompassUpdating": True,
    "IsTicking": True,
    "Seed": 0,
    "IsGameTimePaused": False,
    "IsObjectiveMarkersEnabled": True,
    "IsAllNPCFrozen": False,
    "IsSavingPlayers": True,
    "WorldGen": {"Type": "Void", "Tint": "#5b9e28", "Environment": "Env_Default_Void"},
    "SpawnProvider": {"Id": "Global", "SpawnPoint": {"X": 8.5, "Y": 129.0, "Z": 8.5, "Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0}},
    "IsSpawnMarkersEnabled": True,
    "Instance": {"RemovalConditions": [{"Type": "WorldEmpty"}]},
    "DeleteOnRemove": False,
    "Version": 4,
}
files = {
    "Server/Instances/SkyyIsland/instance.bson": json.dumps(template, indent=2) + "\n",
    "Server/Instances/SkyyIsland/resources/InstanceData.json": '{\n  "HadPlayer": false\n}\n',
}

jar = os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)
m = B.manifest("SkyyIslands", VERSION, "SkyWynn private islands: /island creates and loads your own instanced sky island, co-op members (/island invite + accept) share it, trusted players build, /island menu = members, permission flags, visitors, PvP and spawning; /island reset; /hub (/sethub); one island per profile (SkyyProfiles). Zero dependencies.", PKG + ".SkyyIslandsPlugin")
B.assemble(jar, m, OUT, extra_files=files)
