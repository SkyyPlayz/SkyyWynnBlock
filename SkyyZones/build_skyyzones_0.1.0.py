"""SkyyZones 0.1.0 - build script (javassist via jpype). A NEW mod: protected worlds + regions, phases Z0 + Z1 of
research/cloud/Zone-Regen-Spec.md (decisions: docs/answered/world.md lines 63, 75, 115; Skyy 2026-10-18 popup "Build SkyyZones
(Recommended)" = our own mod that borrows Protect Area's IDEAS only - enter / leave area titles, overlap priority, op bypass; Protect
Area is All Rights Reserved and its code was never read). Skyy was away (2026-10-20 "figure it out"): every [bracketed] default of the
spec's 'Questions for Skyy' is taken (one mod; break gate; placeholders; solo pack vanilla; ...).

Run:   python SkyyZones/build_skyyzones_0.1.0.py      -> SkyyZones/SkyyZones-0.1.0.jar   (no --deploy: tools/deploy_set.py installs the set)
Check: python SkyyZones/test_skyyzones_0.1.0.py       (bare JVMs, -Xverify:all, every new code path executed, engine-access audit)

WHAT 0.1.0 IS (Z1 - protection only; regrowing blocks = Z2, trees / crops = Z3, scaffolding = Z3b, gates + anti-abuse = Z4):
  - Two region MODES (spec 3.0): FULL = nothing breaks or is placed, a hit gives nothing (the break is cancelled in the handler, so the
    engine never rolls drops - Z19); SKYBLOCK = still nothing is placed and nothing breaks EXCEPT the block ids of the region's resource
    types (types.properties); those break exactly like vanilla for now (drop, XP, collections - Z2 adds the placeholder + regrow).
  - Deny by default (spec 3.1 / 3.2), first match wins: (1) a world that is neither in zones.worlds nor holds a region -> SkyyZones does
    nothing (player islands, shards, the solo pack: unprotected unless a region is drawn there); (2) builder mode (/zones build on,
    skyyzones.build, off at every login) or the op-bypass row (admins always pass, default OFF so admins test as players) -> allowed;
    (3) SKYBLOCK region + listed block -> break allowed; (4) region flags containers / furnaces -> chests / processing benches usable;
    (5) everything else in a protected world or inside a region -> refused (break, dig crack, place, F-harvest of crops, chests,
    furnaces, and a block USE (UseBlockEvent) while holding one of the use.tools items). Doors, seats, beds, crafting benches, NPCs, our
    Skyy_* blocks, picking up and dropping items stay allowed. A mob (any non-player entity) breaking / placing in a protected spot is
    refused (zones.blockMobs).
    GAP (fixer probe Z0b, re-checked at build): hoe tilling, shovel paths, buckets (scoop / pour), block-state cycling and other
    ChangeBlock / ChangeState / CycleBlockGroup / PlaceFluid / RefillContainer interactions (and the farming FertilizeSoil /
    UseWateringCan / ChangeFarmingStage ones) write the block straight from the item's
    interaction chain - no Break / Damage / Place / UseBlock event, no other cancellable hook (PlayerMouseButtonEvent's cancel is never
    read; vanilla TriggerVolume NoUse has the same gap). They can NOT be stopped in 0.1.0; Z2's regrow scan is the planned fix.
  - Guard order: every ZGuard system declares RootDependency.firstSet() (like the engine's own first systems), so it runs before other
    mods' handlers of the same event and they skip a cancelled one. Any Throwable inside a guard in a protected spot (not in builder
    mode) cancels the event (fail closed) and is counted (/zones info shows the count).
  - Overlap priority: where regions overlap the highest priority wins (ties: a SKYBLOCK region before a FULL one, then the smaller id -
    fixer 2); its mode and flags decide; in a SKYBLOCK top
    region the resource types of every SKYBLOCK region at that spot count (spec 5.3 "types are the union").
  - Regions: /zones region create <id> <full or skyblock> from the Zone Wand corners (our own item Skyy_Zones_Wand, a vanilla stick look;
    hit two blocks; the wand never breaks anything) or, without wand corners, the vanilla builder-tool selection (probe Z6: BuilderToolsPlugin
    .getState(Player, PlayerRef).getSelection() min / max); addbox / delete / mode / priority / title / types / flags. Data file
    Skyy_SkyyZones/regions.properties (spec 5.3 lines; written atomically on the scheduler thread, the old file copied to history/ first -
    newest 10 kept - and one line per change in region-changes.log). A file that cannot be read or holds a bad line blocks every region
    edit until it is fixed + /zones reload (never overwritten), while the good regions keep protecting; a region whose lines turn bad
    keeps protecting too (fail closed): its last good copy in memory, else the newest good copy in history/, else (world + boxes still
    readable) as a FULL region with those boxes. /zones reload first waits (max 1 s) for a pending regions.properties write.
    Fixer 2: a MISSING regions.properties or one with no region line never drops regions in memory (edits blocked; /zones reload clear
    accepts it, keeping the old text in history/); at a start a missing / blank file - or an unreadable one with nothing in memory - is
    covered by the newest good history/ copy. A file is read 3 times (100 ms apart) before it counts as unreadable. Unknown
    region.<id>.<field> lines (spec 5.3 placeAllow / gate = later phases) are kept verbatim and written back, never a problem.
    At most 64 boxes per region (spec 5.3).
  - /zones show [id|off] [seconds] (particle outline to YOU only, probe Z13), /zones info (what protects the block you look at), /zones list,
    /zones type <type> <ids|none|look> (look = add the block you look at to that type), /zones type add <type> <ids|look> (spec 5.1),
    /zones region create <id> <mode> [types] (spec 5.1), /zones show <seconds>, /zones reload clear.
  - Enter / leave area titles: entering a region that has a title shows a vanilla event title (subtitle "Protected area" / "Gathering
    area"), leaving shows a small notice; the same region's title waits titles.gapSec before it shows again.
  - Builder mode: /zones build on|off (or /zones build = toggle), skyyzones.build (ops have it), OFF at every login (memory only), and off
    when the node is gone (re-checked at most every 30 s at a protected action - fixer 2); while ON a
    BUILD MODE event title on switching + a reminder notice every build.remindSec (default 300, 0 = none) - a real HUD tag needs SkyyHud (listed for the
    main session); bridge zones:build:<uuid> = TRUE while ON for that later SkyyHud tag.
  - Server Setup -> Zones (tools/skyycfg.py, KEEP=10): zone protection (part switch, default ON), protected worlds, admins always bypass,
    mobs can't break, refusal note gap, use.tools, titles on / leave / gap, outline seconds / particle, build reminder, the resource-type
    table (types.properties), the regions table (one line per region; mode / priority / types / flags / title EDITABLE there - fixer 2,
    PROJECT-RULES 4; world, boxes, new regions and deletes stay commands: they need wand corners) and a "Re-read files" action. Region
    edits (command or table) are logged + versioned by this mod (history/, region-changes.log), not the kit.
  - Bridge (java.lang types only, never throwing): zones:version "0.1.0"; zones:fn:check apply(Object[] { String world, Integer x,
    Integer y, Integer z, String action (break / place / container / furnace), String blockId }) -> "allow" or "deny"; zones:fn:region
    apply(Object[] { world, x, y, z }) -> the top region id or null; zones:build:<uuid> Boolean.TRUE while that player is in builder mode.
  - Commands: /zones (skyyzones.build, setPermissionGroups(new String[0]) - never a player group) with usage variants for 1-4 words;
    every node overrides hasPermission so skyyzones.admin alone is enough too; admin actions check skyyzones.admin in code. Nothing replaced (new command name; /zone of SkyyWorldGen is unrelated).

Z0 ENGINE PROBES (read-only, HytaleServer.jar 0.7.2 bytecode; the answers this build relies on are re-checked below at build time):
  Z5  PlaceBlockEvent is only constructed by BlockPlaceUtils (a player placing) - a block written from code never fires it.
  Z5b A cancelled PlaceBlockEvent: placeBlock calls invalidateBlock and returns BEFORE removeItemStackFromSlot -> the held block stays in
      the hand (no item loss in a FULL region; fixer 2, re-checked at build).
  Z6  BuilderToolsPlugin.getState(Player, PlayerRef).getSelection() -> BlockSelection.hasSelectionBounds / getSelectionMin / Max: readable.
  Z9  EnvironmentBreakBlockEvent is a plain EcsEvent (NOT cancellable): fire spread (FireFluidTicker) and source-less explosions cannot be
      stopped by an event (WorldConfig.setDisabledFluidTickers can switch the fire ticker off per world - left to the world config);
      explosions WITH a source entity go through BlockHarvestUtils.damageSingleBlock -> DamageBlockEvent on that entity (our guard refuses
      it in a protected spot); fluids flowing fire no block event at all (builders avoid open source blocks near builds, spec 3.2).
  Z13 ParticleUtil.spawnParticleEffect(String, Vector3dc, List<Ref>, ComponentAccessor) = only the listed players (in-game PASS:
      SkyyTownProbe Q0 #4, 2026-10-10).
  Z14 No vanilla scaffold block / item in Assets.zip; PlaceBlockEvent carries getTargetBlock + getItemInHand + getRotation (an allow-list
      by the held block id is possible - Z3b).
  Z18 A cancelled DamageBlockEvent: damageSingleBlock calls BlockSection.invalidateBlock(x, y, z) and returns false BEFORE the health
      change -> no crack, the block is re-sent; a notification on a refused hit is a normal packet.
  Z19 A cancelled BreakBlockEvent: performBlockBreak calls invalidateBlock and returns BEFORE naturallyRemoveBlock (which rolls the
      drops) -> NO drop, no XP / collection (they wait for the uncancelled event).
  EXTRA  Vanilla 0.7 ships TriggerVolumes (builtin/triggervolumes: box / sphere / cylinder volumes, rules NoDestroy with ExceptBlocks /
      ExceptBlockTags / ExceptTools, NoBuild, NoUse, NoHarvest, NoDoorOpen, NoDamage, ShowEventTitleEffect, PermissionCondition) - a
      vanilla building block for FULL / SKYBLOCK-like areas (builder-tool UI only, no Server Setup, no regrow); noted for the main session.
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyui as SUI

VERSION = "0.1.0"
MOD = "SkyyZones"
HERE = os.path.dirname(os.path.abspath(__file__))
SUI.verify()
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
ASSETS_ZIP = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")

PKG = "com.skyy.zones"
ADMIN, BUILDN = "skyyzones.admin", "skyyzones.build"
WAND = "Skyy_Zones_Wand"
GOOD, BAD, INFO, WARN, MUTED, GOLD = (SUI.COLOR["success"], SUI.COLOR["error"], SUI.COLOR["info"], SUI.COLOR["warning"], SUI.COLOR["text"],
                                      SUI.COLOR["gold"])
T = {
    "PKG": PKG, "VERSION": VERSION, "ADMIN": ADMIN, "BUILDN": BUILDN, "WAND": WAND,
    "GOOD": GOOD, "BAD": BAD, "INFO": INFO, "WARN": WARN, "MUTED": MUTED, "GOLD": GOLD,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PM": "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "ICE": "com.hypixel.hytale.component.system.ICancellableEcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "ARCH": "com.hypixel.hytale.component.Archetype",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3I": "org.joml.Vector3i",
    "V3D": "org.joml.Vector3d",
    "V3DC": "org.joml.Vector3dc",
    "BBE": "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
    "DBE": "com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent",
    "PLBE": "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent",
    "UBE": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent",
    "UBPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "ICTX": "com.hypixel.hytale.server.core.entity.InteractionContext",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BENCH": "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench",
    "BENT": "com.hypixel.hytale.protocol.BenchType",
    "FARM": "com.hypixel.hytale.server.core.asset.type.blocktype.config.farming.FarmingData",
    "GATH": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering",
    "ITY": "com.hypixel.hytale.protocol.InteractionType",
    "PTU": "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "PSYS": "com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem",
    "ETU": "com.hypixel.hytale.server.core.util.EventTitleUtil",
    "NTU": "com.hypixel.hytale.server.core.util.NotificationUtil",
    "NST": "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle",
    "TGU": "com.hypixel.hytale.server.core.util.TargetUtil",
    "BTP": "com.hypixel.hytale.builtin.buildertools.BuilderToolsPlugin",
    "BTS": "com.hypixel.hytale.builtin.buildertools.BuilderToolsPlugin$BuilderState",
    "BSEL": "com.hypixel.hytale.server.core.prefab.selection.standard.BlockSelection",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
# every engine member this mod calls (API drift stops the build here, not in game)
for c, m in ((T["PM"], "get"), (T["PM"], "hasPermission"), (T["PR"], "getUuid"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getPacketHandler"), (T["PR"], "getComponentType"), (T["WLD"], "getName"), (T["WLD"], "getChunkStore"),
             (T["EST"], "getWorld"), (T["ST"], "getExternalData"), (T["ST"], "getComponent"), (T["CHS"], "getChunkReference"),
             (T["CHS"], "getChunkSectionReferenceAtBlock"), (T["CHS"], "getStore"), (T["BSEC"], "get"), (T["BSEC"], "getComponentType"),
             (T["CHU"], "indexChunkFromBlock"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["HSV"], "SCHEDULED_EXECUTOR"),
             (T["PLA"], "getComponentType"), (T["PLA"], "getInventory"), (T["INV"], "getCombinedStorageFirst"), (T["IC"], "getCapacity"),
             (T["IC"], "getItemStack"), (T["IC"], "addItemStack"), (T["IS"], "getItemId"), (T["IS"], "isEmpty"), (T["IS"], "getQuantity"),
             (T["TC"], "getComponentType"), (T["TC"], "getPosition"), (T["BBE"], "getTargetBlock"), (T["BBE"], "getItemInHand"),
             (T["BBE"], "getBlockType"), (T["DBE"], "getTargetBlock"), (T["DBE"], "getItemInHand"), (T["DBE"], "getBlockType"),
             (T["PLBE"], "getTargetBlock"), (T["PLBE"], "getItemInHand"), (T["UBE"], "getTargetBlock"), (T["UBE"], "getBlockType"),
             (T["UBE"], "getInteractionType"), (T["UBE"], "getContext"), (T["UBPRE"], "setCancelled"), (T["ICTX"], "getHeldItem"),
             (T["PDE"], "getPlayerRef"), (T["BTY"], "getId"), (T["BTY"], "getAssetMap"), (T["BTY"], "getBench"), (T["BTY"], "getInteractions"),
             (T["BTY"], "isDoor"), (T["BTY"], "getBeds"), (T["BTY"], "getSeats"), (T["BTY"], "getFarming"), (T["BTY"], "getGathering"),
             (T["BENCH"], "getType"), (T["FARM"], "getStages"), (T["GATH"], "getHarvest"), (T["ITY"], "Primary"), (T["ITY"], "Use"),
             (T["ITY"], "Secondary"), (T["PTU"], "spawnParticleEffect"), (T["PSYS"], "getAssetMap"), (T["ETU"], "showEventTitleToPlayer"),
             (T["NTU"], "sendNotification"), (T["NST"], "Warning"), (T["NST"], "Success"), (T["TGU"], "getTargetBlock"),
             (T["BTP"], "getState"), (T["BTS"], "getSelection"), (T["BSEL"], "hasSelectionBounds"), (T["BSEL"], "getSelectionMin"),
             (T["BSEL"], "getSelectionMax"),
             (T["ATY"], "STRING"), (AC, "requirePermission"), (AC, "setPermissionGroups"), (AC, "addUsageVariant"), (AC, "withRequiredArg"),
             (T["CTX"], "get"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"), (PB, "getEventRegistry"),
             (PB, "getEntityStoreRegistry"), (PB, "getCommandRegistry"), (PB, "getDataDirectory"), (PB, "getLogger"), (PB, "shutdown"),
             ("com.hypixel.hytale.component.system.EventSystem", "shouldProcessEvent")):
    B.probe(pool, c, m)
_sig = lambda cls, name: [str(x.getSignature()) for x in pool.get(cls).getDeclaredMethods() if str(x.getName()) == name]
for cls, name, sig in ((T["PTU"], "spawnParticleEffect", "(Ljava/lang/String;Lorg/joml/Vector3dc;Ljava/util/List;Lcom/hypixel/hytale/component/ComponentAccessor;)V"),
                       (T["ETU"], "showEventTitleToPlayer", "(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/Message;Lcom/hypixel/hytale/server/core/Message;Z)V"),
                       (T["NTU"], "sendNotification", "(Lcom/hypixel/hytale/server/core/io/PacketHandler;Lcom/hypixel/hytale/server/core/Message;Lcom/hypixel/hytale/protocol/packets/interface_/NotificationStyle;)V"),
                       (T["TGU"], "getTargetBlock", "(Lcom/hypixel/hytale/component/Ref;DLcom/hypixel/hytale/component/ComponentAccessor;)Lorg/joml/Vector3i;"),
                       (T["BTP"], "getState", "(Lcom/hypixel/hytale/server/core/entity/entities/Player;Lcom/hypixel/hytale/server/core/universe/PlayerRef;)Lcom/hypixel/hytale/builtin/buildertools/BuilderToolsPlugin$BuilderState;")):
    if sig not in _sig(cls, name):
        raise SystemExit("engine call shape changed: %s.%s%s" % (cls, name, sig))


# ---- Z0 desk probes, re-checked at every build (the guard design rests on them)
def _code(cls, name, sig=None):
    out = []
    for mm in pool.get(cls).getDeclaredMethods():
        if str(mm.getName()) != name or (sig and sig not in str(mm.getSignature())):
            continue
        mi = mm.getMethodInfo()
        cp = mi.getConstPool()
        refs = set()
        for i in range(1, cp.getSize()):
            tag = cp.getTag(i)
            if tag == 10:
                refs.add(str(cp.getMethodrefClassName(i)) + "." + str(cp.getMethodrefName(i)))
            elif tag == 11:
                refs.add(str(cp.getInterfaceMethodrefClassName(i)) + "." + str(cp.getInterfaceMethodrefName(i)))
        out.append(refs)
    return out


_brk = _code("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils", "performBlockBreak",
             "(Lorg/joml/Vector3i;Lcom/hypixel/hytale/server/core/asset/type/blocktype/config/BlockType;Lcom/hypixel/hytale/server/core/inventory/ItemStack;ILjava/lang/String;Ljava/lang/String;ILcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/component/Ref;")
if not _brk or not any(T["BBE"] + ".isCancelled" in r and T["BSEC"] + ".invalidateBlock" in r
                       and "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils.naturallyRemoveBlock" in r for r in _brk):
    raise SystemExit("Z19 changed: performBlockBreak no longer checks BreakBlockEvent.isCancelled before naturallyRemoveBlock")
_dmg = _code("com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils", "damageSingleBlock")
if not _dmg or not any(T["DBE"] + ".isCancelled" in r and T["BSEC"] + ".invalidateBlock" in r for r in _dmg):
    raise SystemExit("Z18 changed: damageSingleBlock no longer invalidates the block on a cancelled DamageBlockEvent")
if pool.get("com.hypixel.hytale.server.core.event.events.ecs.EnvironmentBreakBlockEvent").getSuperclass().getName() != "com.hypixel.hytale.component.system.EcsEvent":
    raise SystemExit("Z9 changed: EnvironmentBreakBlockEvent has a new super class (maybe cancellable now - guard it)")
with zipfile.ZipFile(B.SERVER_JAR) as _sj:
    _pbe_users = sorted(n for n in _sj.namelist() if n.endswith(".class") and n.startswith("com/hypixel/hytale/server/core/modules/")
                        and b"events/ecs/PlaceBlockEvent" in _sj.read(n))
if _pbe_users != ["com/hypixel/hytale/server/core/modules/blockhealth/BlockHealthSystems$PlaceBlockEventSystem.class",
                  "com/hypixel/hytale/server/core/modules/interaction/BlockPlaceUtils.class"]:
    raise SystemExit("Z5 changed: PlaceBlockEvent users in server.core.modules: %s" % _pbe_users)
# Z5b (fixer 2, critic 2's open point): a cancelled PlaceBlockEvent returns BEFORE the held block is taken from the hand (no item loss in
# a FULL region): in BlockPlaceUtils.placeBlock the isCancelled check comes before removeItemStackFromSlot
def _first_call(cls, name, callee):
    for mm in pool.get(cls).getDeclaredMethods():
        if str(mm.getName()) != name:
            continue
        mi = mm.getMethodInfo()
        cp = mi.getConstPool()
        it = mi.getCodeAttribute().iterator()
        while it.hasNext():
            i = it.next()
            if it.byteAt(i) in (182, 183, 184, 185):
                ref = it.u16bitAt(i + 1)
                nm = str(cp.getInterfaceMethodrefName(ref)) if it.byteAt(i) == 185 else str(cp.getMethodrefName(ref))
                if nm == callee:
                    return int(i)
    return -1
_pc, _pr = (_first_call("com.hypixel.hytale.server.core.modules.interaction.BlockPlaceUtils", "placeBlock", _n) for _n in ("isCancelled", "removeItemStackFromSlot"))
if _pc < 0 or _pr < 0 or _pc > _pr:
    raise SystemExit("Z5b changed: BlockPlaceUtils.placeBlock may take the held block before checking a cancelled PlaceBlockEvent (%d / %d)" % (_pc, _pr))
_ev = pool.get("com.hypixel.hytale.component.system.EntityEventSystem").getDeclaredMethod("handleInternal").getMethodInfo()
_evc = _ev.getConstPool()
if "shouldProcessEvent" not in [str(_evc.getMethodrefName(i)) for i in range(1, _evc.getSize()) if _evc.getTag(i) == 10]:
    raise SystemExit("EntityEventSystem.handleInternal no longer skips cancelled events (shouldProcessEvent)")
# Z0b (fixer): the interactions that write blocks / fluids with NO block event (hoe till, shovel path, bucket, state cycling) - a gap we
# document, never claim to guard; if the engine adds an event to one of them (or a new one appears) the build stops so the guard is re-checked
_EVK = (b"events/ecs/BreakBlockEvent", b"events/ecs/PlaceBlockEvent", b"events/ecs/UseBlockEvent", b"events/ecs/DamageBlockEvent",
        b"interaction/BlockHarvestUtils", b"interaction/BlockPlaceUtils")
with zipfile.ZipFile(B.SERVER_JAR) as _sj:
    _noev = sorted(n.rsplit("/", 1)[1][:-6] for n in _sj.namelist()
                   if n.startswith("com/hypixel/hytale/") and n.endswith("Interaction.class")
                   and any(k in _sj.read(n) for k in (b"\x00\x08setBlock", b"\x00\x08setFluid", b"\x00\x0asetTicking"))
                   and not any(k in _sj.read(n) for k in _EVK))
if _noev != ["ChangeBlockInteraction", "ChangeFarmingStageInteraction", "ChangeStateInteraction", "CycleBlockGroupInteraction",
             "FertilizeSoilInteraction", "PlaceFluidInteraction", "RefillContainerInteraction", "UseWateringCanInteraction"]:
    raise SystemExit("Z0b changed: block-writing interactions without a block event: %s (re-check what the guards can stop)" % _noev)
_ac = pool.get("com.hypixel.hytale.server.core.command.system.AbstractCommand").getDeclaredMethod("hasPermission")
if _ac.getModifiers() & 0x0010:
    raise SystemExit("AbstractCommand.hasPermission is final now - the admin-or-builder override cannot work")
B.probe(pool, "com.hypixel.hytale.component.dependency.RootDependency", "firstSet")
if pool.get("com.hypixel.hytale.component.system.EntityEventSystem").getMethod("getDependencies", "()Ljava/util/Set;").getModifiers() & 0x0010:
    raise SystemExit("EntityEventSystem.getDependencies is final now - the guards cannot ask to run first")
print("Z0 desk probes: Z5 Z5b Z9 Z18 Z19 + cancelled-event skip + Z0b (%d event-less block writers) re-checked" % len(_noev))

# ---- vanilla assets the wand JSON names (never copied: referenced by path)
with zipfile.ZipFile(ASSETS_ZIP) as _az:
    _an = set(_az.namelist())
    for _p in ("Common/Icons/ItemsGenerated/Ingredient_Stick.png", "Common/Items/Ingredients/Stick.blockymodel",
               "Common/Items/Ingredients/Stick_Texture.png", "Server/Item/Qualities/Tool.json", "Server/Particles/NPC/Emotions/Alerted.particlesystem"):
        if _p not in _an:
            raise SystemExit("vanilla asset %s is gone" % _p)
    if any(n.endswith("/" + WAND + ".json") for n in _an):
        raise SystemExit("%s is already a vanilla id" % WAND)
    _items = set(n.rsplit("/", 1)[1][:-5] for n in _an if n.startswith("Server/Item/Items/") and n.endswith(".json"))

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
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
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None, ifaces=()):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    for i in ifaces:
        c.addInterface(pool.get(i))
    return c


jl = json.dumps

# =====================================================================================================================================
# default files (the kit's DEFAULTS and the first-run files are the same text)
# =====================================================================================================================================
USE_TOOLS = ("Tool_Bark_Scraper*,Tool_Hoe*,Tool_Shovel*,Tool_Fertilizer*,Tool_Growth_Potion*,Tool_Sap_Shunt*,Tool_Shears*,Tool_Sickle*,"
             "Tool_Watering_Can*,Tool_Hammer*,Tool_Drill*,Container_Bucket*")
for _t in USE_TOOLS.split(","):
    _b = _t.rstrip("*")
    if not any(i.startswith(_b) for i in _items):
        raise SystemExit("use.tools default %s matches no vanilla item" % _t)
CONFIG_TEXT = "\n".join([
    "# SkyyZones settings (research/cloud/Zone-Regen-Spec.md). Change them in game: SkyWynn Menu -> Server Setup -> Zones, or edit here.",
    "# zones.on = the whole protection. zones.worlds = worlds protected EVERYWHERE (comma list; deny by default outside regions too).",
    "# A region (/zones region create) protects its own boxes in any world, listed or not.",
    "zones.on=true",
    "zones.worlds=",
    "# zones.opBypass = admins (skyyzones.admin) are never stopped. Off by default so admins test as players; /zones build on is the bypass.",
    "zones.opBypass=false",
    "# zones.blockMobs = mobs cannot break or place blocks in a protected spot.",
    "zones.blockMobs=true",
    "# msg.gapSec = seconds between two 'This area is protected.' notes for one player.",
    "msg.gapSec=2",
    "# use.tools = held items: USING a block (the block's own use action) while holding one is refused in a protected spot (* = any text).",
    "# NOT stoppable in Hytale 0.7 (no event): hoe tilling, shovel paths, buckets, watering cans, fertilizer used on their own.",
    "use.tools=" + USE_TOOLS,
    "# Area titles: a region with a title shows it when you walk in (titles.leave = a small note when you walk out).",
    "titles.on=true",
    "titles.leave=true",
    "titles.gapSec=10",
    "# /zones show: outline seconds + the particle (a short-lived vanilla particle system; looping ones would stay on screen).",
    "show.seconds=30",
    "show.particle=Alerted",
    "# build.remindSec = while builder mode is on, a reminder note every this many seconds (0 = none).",
    "build.remindSec=300",
    "",
])
TYPES = [("stone", "Rock_Stone,Rock_Shale,Rock_Slate,Rock_Basalt,Rock_Sandstone,Rock_Calcite,Rock_Chalk,Rock_Lime,Rock_Marble,Rock_Quartzite,Rock_Volcanic"),
         ("copper", "Ore_Copper*"), ("iron", "Ore_Iron*"), ("gold", "Ore_Gold*"), ("silver", "Ore_Silver*"), ("thorium", "Ore_Thorium*"),
         ("cobalt", "Ore_Cobalt*"), ("adamantite", "Ore_Adamantite*"), ("mithril", "Ore_Mithril*"), ("onyxium", "Ore_Onyxium*"),
         ("gem", "Rock_Gem_*,Ore_Prisma*"),
         # fixer 2 (C3 #7): a natural tree is trunk + branches + roots (the _Deco / _Full / _Half / plank pieces are built, not grown);
         # crops = the crop BLOCKS only (not the seed / _Item / _Eternal ids). Z1 lets an unripe crop break too - ripe-only is Z3 (spec 4.4).
         ("logs", "Wood_*_Trunk,Wood_*_Branch_Corner,Wood_*_Branch_Long,Wood_*_Branch_Short,Wood_*_Roots"), ("crops", "Plant_Crop_*_Block")]
for _tid, _pats in TYPES:
    for _p in _pats.split(","):
        _rx = re.compile("^" + re.escape(_p).replace(r"\*", ".*") + "$")
        if not any(_rx.match(i) for i in _items):
            raise SystemExit("type %s pattern %s matches no vanilla item id" % (_tid, _p))
    assert len(_pats) <= 200, "a type line longer than SkyyMenu's 200-character cell"
TYPES_TEXT = "\n".join([
    "# SkyyZones resource types: type.<id>=block ids, comma separated; * = any text (Ore_Copper* = every copper ore). A SKYBLOCK region",
    "# lists the types players may break there (/zones region types <region> stone,copper). Server Setup -> Zones -> Resource types.",
] + ["type.%s=%s" % (k, v) for k, v in TYPES] + [""])
REGIONS_HEAD = "\n".join([
    "# SkyyZones regions (research/cloud/Zone-Regen-Spec.md 5.3). Edit in game: /zones region ... (wand corners), or here, then /zones reload.",
    "# One region = these lines: region.<id>.world / mode (full or skyblock) / priority (higher wins where regions overlap) /",
    "# boxes (x,y,z..x,y,z;x,y,z..x,y,z) / types (resource types a SKYBLOCK region lets players break) / flags (containers,furnaces) / title.",
    "# Ids: a-z 0-9 _ (max 40). A bad line stops every region edit (never overwritten) until it is fixed and /zones reload runs.",
])

# =====================================================================================================================================
# ZApi: the harness's stand-in for the engine calls (null in game)
# =====================================================================================================================================
api = pool.makeInterface(PKG + ".ZApi")
for sig in ("public void notify(@PR@ pr, String text);", "public void title(@PR@ pr, String t, String sub);",
            "public void particle(String id, double x, double y, double z, java.util.List to, @ST@ st);",
            "public int[] target(@REF@ r, @ST@ st);", "public int[] selection(@REF@ r, @ST@ st, @PR@ pr);",
            "public int give(@REF@ r, @ST@ st, String id);", "public String blockAt(@WLD@ w, int x, int y, int z);"):
    api.addMethod(CtNewMethod.make(jv(sig), api))

# =====================================================================================================================================
# ZCfg: settings (the kit binds the fields), logging, bridge, permissions, the type table
# =====================================================================================================================================
cfg = mk("ZCfg")
for f in ("public static volatile boolean ON = true;", "public static volatile String WORLDS = \"\";",
          "public static volatile boolean OP_BYPASS = false;", "public static volatile boolean MOBS = true;",
          "public static volatile int MSG_GAP = 2;", "public static volatile String TOOLS = %s;" % jl(USE_TOOLS),
          "public static volatile boolean TITLES = true;", "public static volatile boolean LEAVE = true;",
          "public static volatile int TITLE_GAP = 10;", "public static volatile int SHOW_SECS = 30;",
          "public static volatile String PARTICLE = \"Alerted\";", "public static volatile int REMIND = 300;",
          "public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;", "public static java.nio.file.Path TFILE;",
          "public static @LOG@ LOG;", "public static volatile java.util.Map BRIDGE;",
          "public static volatile java.util.function.Function PERM_TEST;",
          "public static volatile java.util.HashMap TYPES = new java.util.HashMap();",
          "public static volatile String WSRC = null;", "public static volatile java.util.HashSet WSET = new java.util.HashSet();",
          "public static volatile String TSRC = null;", "public static volatile String[] TARR = new String[0];",
          "public static volatile java.util.ArrayList LINES;",
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String DEFAULT_TEXT = %s;" % jl(CONFIG_TEXT), "public static final String TYPES_TEXT = %s;" % jl(TYPES_TEXT)):
    F(cfg, f)
# LINES = harness sink (every log line); null in game
M(cfg, r"""
public static void info(String m) {
  try { java.util.ArrayList l = LINES; if (l != null) l.add("INFO " + m); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyZones] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warn(String m) {
  try { java.util.ArrayList l = LINES; if (l != null) l.add("WARN " + m); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyZones] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warnOnce(String key, String m) {
  if (key != null && WARNED.putIfAbsent(key, Boolean.TRUE) == null) warn(m);
}""")
M(cfg, r"""
public static java.util.Map bridge0() {
  Object o = System.getProperties().get("skyy.bridge");
  if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
  return (java.util.Map) o;
}""")
M(cfg, r"""
public static java.util.Map bridge() {
  java.util.Map m = BRIDGE;
  if (m != null) return m;
  synchronized (java.lang.System.class) { m = bridge0(); }
  BRIDGE = m;
  return m;
}""")
# the kit's PERM_FN too (CfgFn re-checks skyyzones.admin through it)
M(cfg, r"""
public static boolean permTest(java.util.UUID u, String node) {
  if (u == null || node == null) return false;
  try {
    java.util.function.Function f = PERM_TEST;
    if (f != null) return Boolean.TRUE.equals(f.apply(new Object[] { u, node }));
    return @PM@.get().hasPermission(u, node);
  } catch (Throwable t) { return false; }
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
public static int intOf(String v, int d, int lo, int hi) {
  int x = d;
  if (v != null) { try { x = Integer.parseInt(v.trim()); } catch (Throwable t) { x = d; } }
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}""")
M(cfg, r"""
public static String str(String v, String d, int max) {
  if (v == null) return d;
  String s = v.trim();
  if (s.length() > max) s = s.substring(0, max);
  return s;
}""")
M(cfg, r"""
public static String[] splitList(String s) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (s != null) {
    String[] a = s.split("[,;\\s]+");
    for (int i = 0; i < a.length; i++) { String t = a[i].trim(); if (t.length() > 0) out.add(t); }
  }
  return (String[]) out.toArray(new String[out.size()]);
}""")
M(cfg, r"""
public static boolean writeIfMissing(java.nio.file.Path f, String text) {
  try {
    if (f == null || java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return false;
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(f, text.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
    return true;
  } catch (Throwable t) { warn("could not write the default " + f + ": " + t); return false; }
}""")
# a properties file: empty when missing, null when it cannot be read
M(cfg, r"""
public static java.util.Properties read0(java.nio.file.Path f) throws java.io.IOException {
  java.util.Properties p = new java.util.Properties();
  if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
  }
  return p;
}""")
# fixer 2 (engine #1): a file briefly locked (the antivirus) is tried 3 times, 100 ms apart, before it counts as unreadable
M(cfg, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  Throwable last = null;
  for (int i = 0; i < 3; i++) {
    try { return read0(f); } catch (Throwable t) { last = t; }
    if (i < 2) { try { Thread.sleep(100L); } catch (Throwable t2) { break; } }
  }
  warn(f + " could not be read (3 tries): " + last);
  return null;
}""")
M(cfg, r"""
public static String loadCfg(boolean first) {
  boolean wrote = first && writeIfMissing(FILE, DEFAULT_TEXT);
  java.util.Properties p = read(FILE);
  if (p == null) { p = new java.util.Properties(); warn("config.properties could not be read - the built-in defaults are used (NO whole-world protection: zones.worlds is empty) until the next restart"); }
  ON = bool(p.getProperty("zones.on"), true);
  WORLDS = str(p.getProperty("zones.worlds"), "", 400);
  OP_BYPASS = bool(p.getProperty("zones.opBypass"), false);
  MOBS = bool(p.getProperty("zones.blockMobs"), true);
  MSG_GAP = intOf(p.getProperty("msg.gapSec"), 2, 0, 30);
  TOOLS = str(p.getProperty("use.tools"), %s, 600);
  TITLES = bool(p.getProperty("titles.on"), true);
  LEAVE = bool(p.getProperty("titles.leave"), true);
  TITLE_GAP = intOf(p.getProperty("titles.gapSec"), 10, 0, 600);
  SHOW_SECS = intOf(p.getProperty("show.seconds"), 30, 5, 300);
  PARTICLE = str(p.getProperty("show.particle"), "Alerted", 80);
  REMIND = intOf(p.getProperty("build.remindSec"), 300, 0, 3600);
  return (wrote ? "default config.properties written; " : "") + "protection " + (ON ? "ON" : "OFF") + ", protected worlds [" + WORLDS + "], admins bypass " + (OP_BYPASS ? "ON" : "off");
}""" % jl(USE_TOOLS))
# type id -> String[] patterns (a fresh map every load: readers never see a half-built one)
M(cfg, r"""
public static java.util.HashMap parseTypes(java.util.Properties p) {
  java.util.HashMap m = new java.util.HashMap();
  if (p == null) return m;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("type.")) continue;
    String id = k.substring(5).toLowerCase();
    if (!id.matches("[a-z0-9_]{1,32}")) { warnOnce("type:" + k, "types.properties: '" + k + "' is not a type id (a-z 0-9 _) - skipped"); continue; }
    String[] pats = splitList(p.getProperty(k));
    if (pats.length == 0) continue;
    m.put(id, pats);
  }
  return m;
}""")
M(cfg, r"""
public static String loadTypes(boolean first) {
  boolean wrote = first && writeIfMissing(TFILE, TYPES_TEXT);
  java.util.Properties p = read(TFILE);
  if (p == null) return "types.properties could not be read - the old types are kept (" + TYPES.size() + ")";
  java.util.HashMap m = parseTypes(p);
  TYPES = m;
  return (wrote ? "default types.properties written; " : "") + m.size() + " resource types";
}""")
# the kit's reload routine of the type table (runs after the kit wrote types.properties)
M(cfg, r"""
public static void reloadTypes() {
  info("resource types re-read: " + loadTypes(false));
}""")
M(cfg, r"""
public static boolean protectedWorld(String w) {
  if (w == null) return false;
  String src = WORLDS;
  if (src == null) src = "";
  if (!src.equals(WSRC)) {
    java.util.HashSet s = new java.util.HashSet();
    String[] a = splitList(src);
    for (int i = 0; i < a.length; i++) s.add(a[i].toLowerCase());
    WSET = s;
    WSRC = src;
  }
  return WSET.contains(w.toLowerCase());
}""")
M(cfg, r"""
public static String[] tools() {
  String src = TOOLS;
  if (src == null) src = "";
  if (!src.equals(TSRC)) {
    TARR = splitList(src);
    TSRC = src;
  }
  return TARR;
}""")
# ---- kit check= hooks (null = fine, text = refused)
M(cfg, r"""
public static String checkWorlds(String key, String value) {
  if (value == null) return null;
  String[] a = splitList(value);
  if (a.length > 32) return "At most 32 worlds.";
  for (int i = 0; i < a.length; i++) if (!a[i].matches("[A-Za-z0-9_.-]{1,64}")) return "'" + a[i] + "' is not a world folder name.";
  return null;
}""")
M(cfg, r"""
public static String checkPatterns(String value, int max) {
  if (value == null) return null;
  String[] a = splitList(value);
  if (a.length == 0) return "List at least one block id (* = any text).";
  if (a.length > max) return "At most " + max + " ids.";
  for (int i = 0; i < a.length; i++) if (!a[i].matches("[A-Za-z0-9_*+]{1,80}")) return "'" + a[i] + "' is not a block id pattern (letters, digits, _ and *).";
  return null;
}""")
M(cfg, r"""
public static String checkTools(String key, String value) {
  if (value == null || value.trim().length() == 0) return null;
  return checkPatterns(value, 64);
}""")
M(cfg, r"""
public static String checkType(String key, String value) {
  if (key == null || !key.startsWith("type[") || !key.endsWith("]")) return "Unknown table line.";
  String e = key.substring(5, key.length() - 1);
  if (!e.matches("[a-z0-9_]{1,32}")) return "A type id is 1-32 of a-z, 0-9 and _.";
  return checkPatterns(value, 64);
}""")
M(cfg, r"""
public static String checkParticle(String key, String value) {
  if (value == null) return null;
  String v = value.trim();
  if (!v.matches("[A-Za-z0-9_]{1,80}")) return "A particle system id: letters, digits and _.";
  try {
    Object m = @PSYS@.getAssetMap();
    if (m != null && @PSYS@.getAssetMap().getAsset(v) == null) return "No particle system '" + v + "' in the game files.";
  } catch (Throwable t) { }
  return null;
}""")
# the particle actually drawn: a hand-edited show.particle the game does not know falls back to Alerted (warned once). Checked at USE time
# (the asset map is complete then; at setup() it may not be) and only again when the setting changes.
F(cfg, "public static volatile String PSRC = null;")
F(cfg, "public static volatile String PVAL = \"Alerted\";")
M(cfg, r"""
public static String particle() {
  String v = PARTICLE;
  if (v == null) v = "Alerted";
  if (v.equals(PSRC)) return PVAL;
  String why = checkParticle("show.particle", v);
  String use = v;
  if (why != null) { use = "Alerted"; warnOnce("particle:" + v, "show.particle '" + v + "' cannot be drawn (" + why + ") - the outline uses Alerted"); }
  PVAL = use;
  PSRC = v;
  return use;
}""")

# =====================================================================================================================================
# ZRegion: one region (immutable once published: edits make a copy)
# =====================================================================================================================================
reg = mk("ZRegion")
for f in ("public String id;", "public String world;", "public int mode;", "public int priority;", "public int[] box;", "public String[] types;",
          "public String flags;", "public String title;", "public boolean fCont;", "public boolean fFurn;", "public java.util.TreeMap extra;",
          "public static final int FULL = 0;", "public static final int SKYBLOCK = 1;", "public static final int MAX_BOXES = 64;",
          "public static final int MAX_X = 512;", "public static final int MAX_Y = 384;", "public static final int MAX_Z = 512;"):
    F(reg, f)
# extra = region.<id>.<field> lines this version does not use (spec 5.3 placeAllow / gate, a later version's fields): kept verbatim
C(reg, "public ZRegion() { this.types = new String[0]; this.box = new int[0]; this.flags = \"\"; this.title = \"\"; this.extra = new java.util.TreeMap(); }")
M(reg, r"""
public void setFlags(String f) {
  this.flags = f == null ? "" : f;
  this.fCont = false;
  this.fFurn = false;
  String[] a = @PKG@.ZCfg.splitList(this.flags);
  for (int i = 0; i < a.length; i++) {
    if (a[i].equals("containers")) this.fCont = true;
    if (a[i].equals("furnaces")) this.fFurn = true;
  }
}""")
M(reg, r"""
public @PKG@.ZRegion copy() {
  @PKG@.ZRegion r = new @PKG@.ZRegion();
  r.id = this.id; r.world = this.world; r.mode = this.mode; r.priority = this.priority;
  r.box = (int[]) this.box.clone(); r.types = (String[]) this.types.clone(); r.title = this.title;
  r.extra = new java.util.TreeMap(this.extra);
  r.setFlags(this.flags);
  return r;
}""")
M(reg, "public int boxes() { return this.box == null ? 0 : this.box.length / 6; }")
M(reg, r"""
public boolean contains(int x, int y, int z) {
  int[] b = this.box;
  for (int i = 0; i + 5 < b.length; i = i + 6) {
    if (x >= b[i] && x <= b[i + 3] && y >= b[i + 1] && y <= b[i + 4] && z >= b[i + 2] && z <= b[i + 5]) return true;
  }
  return false;
}""")
# a box (6 ints min / max) within r blocks of x y z (show / list)
M(reg, r"""
public boolean near(int x, int y, int z, int r) {
  int[] b = this.box;
  for (int i = 0; i + 5 < b.length; i = i + 6) {
    if (x >= b[i] - r && x <= b[i + 3] + r && y >= b[i + 1] - r && y <= b[i + 4] + r && z >= b[i + 2] - r && z <= b[i + 5] + r) return true;
  }
  return false;
}""")
M(reg, "public String modeName() { return this.mode == 1 ? \"skyblock\" : \"full\"; }")
M(reg, r"""
public static int modeOf(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  if (t.equals("full")) return 0;
  if (t.equals("skyblock")) return 1;
  return -1;
}""")
M(reg, r"""
public static int[] norm(int ax, int ay, int az, int bx, int by, int bz) {
  return new int[] { Math.min(ax, bx), Math.min(ay, by), Math.min(az, bz), Math.max(ax, bx), Math.max(ay, by), Math.max(az, bz) };
}""")
# "" = fine, else why not
M(reg, r"""
public static String boxProblem(int[] b) {
  if (b == null || b.length != 6) return "no box";
  if (b[3] - b[0] + 1 > MAX_X || b[4] - b[1] + 1 > MAX_Y || b[5] - b[2] + 1 > MAX_Z) return "a box may be at most " + MAX_X + " x " + MAX_Y + " x " + MAX_Z + " blocks (this one is " + (b[3] - b[0] + 1) + " x " + (b[4] - b[1] + 1) + " x " + (b[5] - b[2] + 1) + ")";
  if (b[1] < -64 || b[4] > 511) return "y must stay between -64 and 511";
  return "";
}""")
M(reg, r"""
public static String boxText(int[] b) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i + 5 < b.length; i = i + 6) {
    if (sb.length() > 0) sb.append(';');
    sb.append(b[i]).append(',').append(b[i + 1]).append(',').append(b[i + 2]).append("..").append(b[i + 3]).append(',').append(b[i + 4]).append(',').append(b[i + 5]);
  }
  return sb.toString();
}""")
M(reg, r"""
public static String size(int[] b, int i) {
  return (b[i + 3] - b[i] + 1) + " x " + (b[i + 4] - b[i + 1] + 1) + " x " + (b[i + 5] - b[i + 2] + 1);
}""")
# null = a bad text; every box normalised + checked
M(reg, r"""
public static int[] parseBoxes(String s) {
  if (s == null) return null;
  String[] parts = s.trim().split(";");
  if (parts.length == 0 || parts.length > MAX_BOXES) return null;
  int[] out = new int[parts.length * 6];
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    int dd = p.indexOf("..");
    if (dd <= 0) return null;
    String[] a = p.substring(0, dd).split(",");
    String[] c = p.substring(dd + 2).split(",");
    if (a.length != 3 || c.length != 3) return null;
    int[] n = null;
    try {
      n = norm(Integer.parseInt(a[0].trim()), Integer.parseInt(a[1].trim()), Integer.parseInt(a[2].trim()), Integer.parseInt(c[0].trim()), Integer.parseInt(c[1].trim()), Integer.parseInt(c[2].trim()));
    } catch (Throwable t) { return null; }
    if (boxProblem(n).length() > 0) return null;
    System.arraycopy(n, 0, out, i * 6, 6);
  }
  return out;
}""")
M(reg, r"""
public static String join(String[] a) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < a.length; i++) { if (i > 0) sb.append(','); sb.append(a[i]); }
  return sb.toString();
}""")
M(reg, r"""
public String lines() {
  String p = "region." + this.id + ".";
  StringBuilder sb = new StringBuilder();
  sb.append(p + "world=" + this.world + "\n" + p + "mode=" + modeName() + "\n" + p + "priority=" + this.priority + "\n" + p + "boxes=" + boxText(this.box) + "\n"
    + p + "types=" + join(this.types) + "\n" + p + "flags=" + this.flags + "\n" + p + "title=" + this.title + "\n");
  java.util.Iterator it = this.extra.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    String v = String.valueOf(this.extra.get(k)).replace("\\", "\\\\").replace('\n', ' ').replace('\r', ' ');
    sb.append(p).append(k).append('=').append(v).append('\n');
  }
  return sb.toString();
}""")
M(reg, r"""
public String summary() {
  return this.id + " (" + modeName() + ", priority " + this.priority + ", " + boxes() + (boxes() == 1 ? " box" : " boxes")
    + (this.mode == 1 ? ", types " + (this.types.length == 0 ? "none" : join(this.types)) : "")
    + (this.flags.length() > 0 ? ", flags " + this.flags : "") + (this.title.length() > 0 ? ", title '" + this.title + "'" : "") + ")";
}""")

# =====================================================================================================================================
# ZIndex: the published, never-changed lookup (per world: regions by priority; a tie: SKYBLOCK before FULL (fixer 2, C3 #3 - spec 3.0
# "draw the resource area higher", so a mine drawn inside a town at the same priority still gathers), then the id a-z)
# =====================================================================================================================================
idx = mk("ZIndex")
F(idx, "public java.util.HashMap byWorld;")
F(idx, "public int count;")
C(idx, "public ZIndex() { this.byWorld = new java.util.HashMap(); this.count = 0; }")
M(idx, r"""
public static boolean before(@PKG@.ZRegion a, @PKG@.ZRegion b) {
  if (a.priority != b.priority) return a.priority > b.priority;
  if (a.mode != b.mode) return a.mode == 1;
  return a.id.compareTo(b.id) < 0;
}""")
M(idx, r"""
public static @PKG@.ZIndex build(java.util.Collection regs) {
  @PKG@.ZIndex ix = new @PKG@.ZIndex();
  java.util.HashMap lists = new java.util.HashMap();
  java.util.Iterator it = regs.iterator();
  while (it.hasNext()) {
    @PKG@.ZRegion r = (@PKG@.ZRegion) it.next();
    java.util.ArrayList l = (java.util.ArrayList) lists.get(r.world);
    if (l == null) { l = new java.util.ArrayList(); lists.put(r.world, l); }
    l.add(r);
    ix.count = ix.count + 1;
  }
  java.util.Iterator wi = lists.keySet().iterator();
  while (wi.hasNext()) {
    String w = (String) wi.next();
    java.util.ArrayList l = (java.util.ArrayList) lists.get(w);
    @PKG@.ZRegion[] a = (@PKG@.ZRegion[]) l.toArray(new @PKG@.ZRegion[l.size()]);
    for (int i = 1; i < a.length; i++) {
      @PKG@.ZRegion k = a[i];
      int j = i - 1;
      while (j >= 0 && before(k, a[j])) { a[j + 1] = a[j]; j = j - 1; }
      a[j + 1] = k;
    }
    ix.byWorld.put(w, a);
  }
  return ix;
}""")
M(idx, "public boolean has(String w) { return w != null && this.byWorld.containsKey(w); }")
M(idx, r"""
public @PKG@.ZRegion[] in(String w) {
  Object o = w == null ? null : this.byWorld.get(w);
  if (o == null) return new @PKG@.ZRegion[0];
  return (@PKG@.ZRegion[]) o;
}""")
M(idx, r"""
public java.util.ArrayList at(String w, int x, int y, int z) {
  java.util.ArrayList out = new java.util.ArrayList();
  @PKG@.ZRegion[] a = in(w);
  for (int i = 0; i < a.length; i++) if (a[i].contains(x, y, z)) out.add(a[i]);
  return out;
}""")
M(idx, r"""
public @PKG@.ZRegion top(String w, int x, int y, int z) {
  @PKG@.ZRegion[] a = in(w);
  for (int i = 0; i < a.length; i++) if (a[i].contains(x, y, z)) return a[i];
  return null;
}""")
M(idx, r"""
public @PKG@.ZRegion topTitled(String w, int x, int y, int z) {
  @PKG@.ZRegion[] a = in(w);
  for (int i = 0; i < a.length; i++) if (a[i].title.length() > 0 && a[i].contains(x, y, z)) return a[i];
  return null;
}""")

# =====================================================================================================================================
# ZRules: the pure decisions (no engine)
# =====================================================================================================================================
rules = mk("ZRules")
for f in ("public static final int BREAK = 0;", "public static final int PLACE = 1;", "public static final int CONTAINER = 2;",
          "public static final int FURNACE = 3;", "public static final int OTHER = 4;", "public static final int ALLOW = 0;",
          "public static final int DENY = 1;", "public static final int NOT_RES = 2;", "public static final int LOCKED = 3;",
          "public static final int NO_PLACE = 4;"):
    F(rules, f)
M(rules, r"""
public static String bare(String id) {
  if (id == null) return "";
  String s = id;
  while (s.startsWith("*")) s = s.substring(1);
  return s;
}""")
# * = any text (anywhere), a trailing + = * (the spec's prefix mark); case-insensitive
M(rules, r"""
public static boolean glob(String pat, String id) {
  if (pat == null || id == null) return false;
  String p = pat.toLowerCase();
  String s = id.toLowerCase();
  if (p.endsWith("+")) p = p.substring(0, p.length() - 1) + "*";
  int pi = 0;
  int si = 0;
  int star = -1;
  int mark = 0;
  int pl = p.length();
  int sl = s.length();
  while (si < sl) {
    if (pi < pl && p.charAt(pi) != '*' && p.charAt(pi) == s.charAt(si)) { pi++; si++; }
    else if (pi < pl && p.charAt(pi) == '*') { star = pi; mark = si; pi++; }
    else if (star >= 0) { pi = star + 1; mark++; si = mark; }
    else return false;
  }
  while (pi < pl && p.charAt(pi) == '*') pi++;
  return pi == pl;
}""")
M(rules, r"""
public static boolean anyGlob(String[] pats, String id) {
  if (pats == null || id == null || id.length() == 0) return false;
  for (int i = 0; i < pats.length; i++) if (glob(pats[i], id)) return true;
  return false;
}""")
M(rules, r"""
public static boolean typeHas(String type, String id) {
  Object o = @PKG@.ZCfg.TYPES.get(type);
  return o instanceof String[] && anyGlob((String[]) o, id);
}""")
M(rules, r"""
public static String listedType(@PKG@.ZRegion r, String id) {
  for (int i = 0; i < r.types.length; i++) if (typeHas(r.types[i], id)) return r.types[i];
  return null;
}""")
# the decision (spec 3.1 / 3.2): regions at the spot (top = highest priority); none -> the protected world's FULL default or nothing
M(rules, r"""
public static int decide(@PKG@.ZIndex ix, String w, boolean pw, int x, int y, int z, int act, String id) {
  if (act == OTHER) return ALLOW;
  java.util.ArrayList at = ix == null ? new java.util.ArrayList() : ix.at(w, x, y, z);
  if (at.isEmpty() && !pw) return ALLOW;
  @PKG@.ZRegion top = at.isEmpty() ? null : (@PKG@.ZRegion) at.get(0);
  if (act == PLACE) return NO_PLACE;
  if (act == CONTAINER) return top != null && top.fCont ? ALLOW : LOCKED;
  if (act == FURNACE) return top != null && top.fFurn ? ALLOW : LOCKED;
  if (top == null || top.mode != 1) return DENY;
  String b = bare(id);
  for (int i = 0; i < at.size(); i++) {
    @PKG@.ZRegion r = (@PKG@.ZRegion) at.get(i);
    if (r.mode == 1 && listedType(r, b) != null) return ALLOW;
  }
  return NOT_RES;
}""")
M(rules, r"""
public static String why(int code) {
  if (code == NOT_RES) return "You can only gather the marked resource blocks here.";
  if (code == LOCKED) return "That is locked in this area.";
  if (code == NO_PLACE) return "You can't place blocks in this area.";
  return "This area is protected.";
}""")
M(rules, r"""
public static String verdict(int code) {
  if (code == ALLOW) return "allowed";
  return "refused - " + why(code);
}""")
# UseBlockEvent (Use / Secondary) -> the action it counts as (facts read from the block type; pure so the harness can table it)
M(rules, r"""
public static int useKind(boolean skyy, boolean door, boolean craft, boolean proc, boolean bed, boolean seat, boolean crop, boolean cont, String held) {
  if (skyy || door || craft || bed || seat) return OTHER;
  if (proc) return FURNACE;
  if (cont) return CONTAINER;
  if (crop) return BREAK;
  if (held != null && anyGlob(@PKG@.ZCfg.tools(), held)) return BREAK;
  return OTHER;
}""")
M(rules, r"""
public static int useAction(@BTY@ bt, @ITY@ t, String held) {
  if (t == null) return OTHER;
  if (t == @ITY@.Primary) return BREAK;
  if (t != @ITY@.Use && t != @ITY@.Secondary) return OTHER;
  boolean skyy = false; boolean door = false; boolean craft = false; boolean proc = false; boolean bed = false; boolean seat = false;
  boolean crop = false; boolean cont = false;
  if (bt != null) {
    try {
      String id = bare(String.valueOf(bt.getId()));
      skyy = id.startsWith("Skyy_");
      door = bt.isDoor();
      java.util.Map im = bt.getInteractions();
      Object rid = im == null ? null : im.get(t);
      if (rid != null && String.valueOf(rid).indexOf("Door") >= 0) door = true;
      @BENCH@ b = bt.getBench();
      if (b != null) { if (b.getType() == @BENT@.Processing) proc = true; else craft = true; }
      bed = bt.getBeds() != null;
      seat = bt.getSeats() != null;
      @FARM@ f = bt.getFarming();
      if (f != null && f.getStages() != null) crop = true;
      @GATH@ g = bt.getGathering();
      if (g != null && g.getHarvest() != null && id.startsWith("Plant_")) crop = true;
      Object uid = im == null ? null : im.get(@ITY@.Use);
      if (uid != null && String.valueOf(uid).indexOf("Container") >= 0) cont = true;
    } catch (Throwable x) { }
  }
  return useKind(skyy, door, craft, proc, bed, seat, crop, cont, held);
}""")

# =====================================================================================================================================
# ZSave: the regions file writer (scheduler thread; newest text wins; history copy first; change log)
# =====================================================================================================================================
sav = mk("ZSave", None, ("java.lang.Runnable",))
for f in ("public long seq;", "public String text;", "public String line;", "public static long WRITTEN = 0L;",
          "public static volatile java.nio.file.Path FILE;", "public static volatile java.nio.file.Path HIST;",
          "public static volatile java.nio.file.Path LOGF;", "public static final int KEEP = 10;",
          "public static final java.util.concurrent.atomic.AtomicLong WRITES = new java.util.concurrent.atomic.AtomicLong();"):
    F(sav, f)
C(sav, "public ZSave(long seq, String text, String line) { this.seq = seq; this.text = text; this.line = line; }")
M(sav, r"""
public static String stamp() {
  return new java.text.SimpleDateFormat("yyyyMMdd-HHmmss-SSS").format(new java.util.Date());
}""")
M(sav, r"""
public static void prune() {
  try {
    if (HIST == null || !java.nio.file.Files.isDirectory(HIST, new java.nio.file.LinkOption[0])) return;
    java.util.ArrayList names = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(HIST, "regions.*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) names.add(((java.nio.file.Path) it.next()).getFileName().toString());
    } finally { ds.close(); }
    java.util.Collections.sort(names);
    for (int i = 0; i + KEEP < names.size(); i++) java.nio.file.Files.deleteIfExists(HIST.resolve((String) names.get(i)));
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("prune", "could not prune the regions history: " + t); }
}""")
M(sav, r"""
public static void logLine(String line) {
  if (line == null || LOGF == null) return;
  try {
    java.nio.file.Files.createDirectories(LOGF.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String l = new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(new java.util.Date()) + "\t" + line.replace('\n', ' ').replace('\r', ' ') + "\n";
    java.nio.file.Files.write(LOGF, l.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND, java.nio.file.StandardOpenOption.WRITE });
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("changelog", "could not write region-changes.log: " + t); }
}""")
# the write itself: never a text older than the newest written one; the file on disk is copied to history/ first (skipped if equal)
M(sav, r"""
public static synchronized boolean write(long seq, String text, String line) {
  logLine(line);
  if (seq <= WRITTEN || FILE == null) return false;
  try {
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]) && HIST != null) {
      byte[] old = java.nio.file.Files.readAllBytes(FILE);
      if (!new String(old, "UTF-8").equals(text)) {
        java.nio.file.Files.createDirectories(HIST, new java.nio.file.attribute.FileAttribute[0]);
        java.nio.file.Files.write(HIST.resolve("regions." + stamp() + ".properties"), old, new java.nio.file.OpenOption[0]);
        prune();
      }
    }
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    try {
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable am) {
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    WRITTEN = seq;
    WRITES.incrementAndGet();
    return true;
  } catch (Throwable t) { @PKG@.ZCfg.warn("could not write regions.properties (the change stays in memory; the next change or a restart writes again): " + t); return false; }
}""")
# a text kept in history/ by itself (/zones reload clear keeps the regions it removes)
M(sav, r"""
public static synchronized void keep(String text) {
  if (HIST == null || text == null) return;
  try {
    java.nio.file.Files.createDirectories(HIST, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(HIST.resolve("regions." + stamp() + ".properties"), text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    prune();
  } catch (Throwable t) { @PKG@.ZCfg.warn("could not keep the regions text in history/: " + t); }
}""")
M(sav, "public void run() { write(this.seq, this.text, this.line); }")
M(sav, "public static synchronized long written() { return WRITTEN; }")

# =====================================================================================================================================
# ZStore: the regions (memory + file)
# =====================================================================================================================================
sto = mk("ZStore")
for f in ("public static java.nio.file.Path FILE;", "public static final java.util.TreeMap REGIONS = new java.util.TreeMap();",
          "public static volatile @PKG@.ZIndex INDEX = new @PKG@.ZIndex();", "public static volatile String BAD = null;",
          "public static volatile boolean SYNC = false;", "public static long SEQ = 0L;", "public static volatile String LAST_TEXT = null;",
          "public static volatile long LAST_SEQ = 0L;", "public static final int MAX_REGIONS = 500;",
          "public static final String HEAD = %s;" % jl(REGIONS_HEAD)):
    F(sto, f)
M(sto, r"""
public static String text() {
  StringBuilder sb = new StringBuilder(HEAD);
  sb.append('\n');
  java.util.Iterator it = REGIONS.values().iterator();
  while (it.hasNext()) { sb.append('\n'); sb.append(((@PKG@.ZRegion) it.next()).lines()); }
  return sb.toString();
}""")
M(sto, r"""
public static void publish() {
  INDEX = @PKG@.ZIndex.build(new java.util.ArrayList(REGIONS.values()));
}""")
# called with the class lock held (every mutator is static synchronized)
M(sto, r"""
public static void save(String who, String what) {
  SEQ = SEQ + 1L;
  String t = text();
  LAST_TEXT = t;
  LAST_SEQ = SEQ;
  String line = (who == null ? "?" : who) + "\t" + what;
  @PKG@.ZCfg.info("regions: " + what + " by " + who);
  @PKG@.ZSave task = new @PKG@.ZSave(SEQ, t, line);
  if (SYNC) { task.run(); return; }
  try { @HSV@.SCHEDULED_EXECUTOR.execute(task); } catch (Throwable x) { task.run(); }
}""")
M(sto, r"""
public static void flush() {
  String t = LAST_TEXT;
  if (t != null) @PKG@.ZSave.write(LAST_SEQ, t, null);
}""")
# titleOk + typeList first (load / set call them: javassist has no forward references)
M(sto, r"""
public static boolean titleOk(String t) {
  return t != null && t.length() <= 40 && t.matches("[A-Za-z0-9 '!&.,()?:-]*");
}""")
M(sto, r"""
public static String typeList() {
  java.util.TreeSet s = new java.util.TreeSet(@PKG@.ZCfg.TYPES.keySet());
  StringBuilder sb = new StringBuilder();
  java.util.Iterator it = s.iterator();
  while (it.hasNext()) { if (sb.length() > 0) sb.append(", "); sb.append((String) it.next()); }
  return sb.length() == 0 ? "(none)" : sb.toString();
}""")
# one region from a properties file; why[0] = the first bad field (null = fine). A bad box text leaves r.box empty.
M(sto, r"""
public static @PKG@.ZRegion parseOne(java.util.Properties p, String id, String[] why) {
  String pre = "region." + id + ".";
  @PKG@.ZRegion r = new @PKG@.ZRegion();
  r.id = id;
  r.world = p.getProperty(pre + "world", "").trim();
  if (!r.world.matches("[A-Za-z0-9_.-]{1,64}")) why[0] = "world '" + r.world + "'";
  r.mode = @PKG@.ZRegion.modeOf(p.getProperty(pre + "mode", "full"));
  if (r.mode < 0) { why[0] = "mode '" + p.getProperty(pre + "mode") + "' (full or skyblock)"; r.mode = 0; }
  try { r.priority = Integer.parseInt(p.getProperty(pre + "priority", "0").trim()); } catch (Throwable t) { why[0] = "priority '" + p.getProperty(pre + "priority") + "'"; r.priority = 0; }
  if (r.priority < -1000 || r.priority > 1000) { why[0] = "priority " + r.priority + " (-1000 to 1000)"; r.priority = 0; }
  int[] b = @PKG@.ZRegion.parseBoxes(p.getProperty(pre + "boxes"));
  if (b == null) why[0] = "boxes '" + p.getProperty(pre + "boxes") + "'"; else r.box = b;
  String[] ty = @PKG@.ZCfg.splitList(p.getProperty(pre + "types", "").toLowerCase());
  for (int i = 0; i < ty.length; i++) if (!ty[i].matches("[a-z0-9_]{1,32}")) why[0] = "type '" + ty[i] + "'";
  r.types = ty;
  String[] fa = @PKG@.ZCfg.splitList(p.getProperty(pre + "flags", "").trim().toLowerCase());
  for (int i = 0; i < fa.length; i++) if (!fa[i].equals("containers") && !fa[i].equals("furnaces")) why[0] = "flag '" + fa[i] + "' (containers, furnaces)";
  r.setFlags(@PKG@.ZRegion.join(fa));
  r.title = p.getProperty(pre + "title", "").trim();
  if (!titleOk(r.title)) { why[0] = "title '" + r.title + "'"; r.title = ""; }
  return r;
}""")
# the newest good copy of one region in history/ (null = none)
M(sto, r"""
public static @PKG@.ZRegion fromHistory(String id) {
  try {
    java.nio.file.Path h = @PKG@.ZSave.HIST;
    if (h == null || !java.nio.file.Files.isDirectory(h, new java.nio.file.LinkOption[0])) return null;
    java.util.ArrayList names = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(h, "regions.*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) names.add(((java.nio.file.Path) it.next()).getFileName().toString());
    } finally { ds.close(); }
    java.util.Collections.sort(names);
    for (int i = names.size() - 1; i >= 0; i--) {
      java.util.Properties p = @PKG@.ZCfg.read(h.resolve((String) names.get(i)));
      if (p == null || p.getProperty("region." + id + ".world") == null) continue;
      String[] why = new String[1];
      @PKG@.ZRegion r = parseOne(p, id, why);
      if (why[0] == null) return r;
    }
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("histread", "could not read the regions history: " + t); }
  return null;
}""")
# a region whose new lines are bad keeps protecting (fail closed): its copy in memory, else the newest good history copy, else - world + boxes
# still readable - FULL with those boxes; only a region with no readable world or box is left out (warned). BAD blocks every edit meanwhile.
M(sto, r"""
public static @PKG@.ZRegion fallback(String id, @PKG@.ZRegion parsed, String why) {
  @PKG@.ZRegion old = (@PKG@.ZRegion) REGIONS.get(id);
  if (old != null) { @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " - it keeps protecting as before (its last good version) until fixed"); return old; }
  @PKG@.ZRegion h = fromHistory(id);
  if (h != null) { @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " - it protects as its newest good copy in history/ until fixed"); return h; }
  if (parsed.world.matches("[A-Za-z0-9_.-]{1,64}") && parsed.box.length >= 6) {
    parsed.mode = 0; parsed.types = new String[0]; parsed.setFlags("");
    @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " - it protects as a FULL region (nothing breaks) until fixed");
    return parsed;
  }
  @PKG@.ZCfg.warn("regions.properties: region " + id + " has a bad " + why + " and no readable world + boxes - it does NOT protect until fixed");
  return null;
}""")
# every region of one properties set. bad[0] = the first problem (null = fine), kept[0] = bad regions that still protect; fb = true: a bad
# region falls back (fallback()), warnings logged; fb = false (a history copy): bad regions are just skipped, nothing logged.
# Keys: region.<id>.<field>; world / mode / priority / boxes / types / flags / title are read; any OTHER field (spec 5.3 placeAllow / gate,
# a later version's lines) is kept verbatim in ZRegion.extra and written back (fixer 2, C3 #1) - only a non-region line is a problem.
M(sto, r"""
public static java.util.TreeMap parseAll(java.util.Properties p, String[] bad, int[] kept, boolean fb) {
  java.util.TreeMap ids = new java.util.TreeMap();
  java.util.regex.Pattern kp = java.util.regex.Pattern.compile("^region\\.([a-z0-9_]{1,40})\\.([A-Za-z][A-Za-z0-9_]{0,31})$");
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    java.util.regex.Matcher m = kp.matcher(k);
    if (!m.matches()) {
      if (bad[0] == null) bad[0] = "unknown line '" + k + "'";
      if (fb) @PKG@.ZCfg.warn("regions.properties: unknown line '" + k + "'");
      continue;
    }
    String id = m.group(1);
    String f = m.group(2);
    java.util.TreeMap ex = (java.util.TreeMap) ids.get(id);
    if (ex == null) { ex = new java.util.TreeMap(); ids.put(id, ex); }
    if (f.matches("world|mode|priority|boxes|types|flags|title")) continue;
    ex.put(f, p.getProperty(k));
    if (fb && !f.matches("placeAllow|gate|gateEntry")) @PKG@.ZCfg.warnOnce("extra:" + k, "regions.properties: '" + k + "' is not used by SkyyZones @VERSION@ - kept as it is");
  }
  java.util.TreeMap out = new java.util.TreeMap();
  java.util.Iterator ii = ids.keySet().iterator();
  while (ii.hasNext()) {
    String id = (String) ii.next();
    String[] why = new String[1];
    @PKG@.ZRegion r = parseOne(p, id, why);
    r.extra = new java.util.TreeMap((java.util.TreeMap) ids.get(id));
    if (why[0] != null) {
      if (bad[0] == null) bad[0] = "region " + id + ": bad " + why[0];
      if (!fb) continue;
      r = fallback(id, r, why[0]);
      if (r == null) continue;
      kept[0] = kept[0] + 1;
    }
    if (out.size() >= MAX_REGIONS) { if (bad[0] == null) bad[0] = "more than " + MAX_REGIONS + " regions"; continue; }
    out.put(id, r);
  }
  return out;
}""")
# the newest history copy that holds at least one good region (name[0] = its file name); null = none
M(sto, r"""
public static java.util.TreeMap fromHistoryAll(String[] name) {
  try {
    java.nio.file.Path h = @PKG@.ZSave.HIST;
    if (h == null || !java.nio.file.Files.isDirectory(h, new java.nio.file.LinkOption[0])) return null;
    java.util.ArrayList names = new java.util.ArrayList();
    java.nio.file.DirectoryStream ds = java.nio.file.Files.newDirectoryStream(h, "regions.*.properties");
    try {
      java.util.Iterator it = ds.iterator();
      while (it.hasNext()) names.add(((java.nio.file.Path) it.next()).getFileName().toString());
    } finally { ds.close(); }
    java.util.Collections.sort(names);
    for (int i = names.size() - 1; i >= 0; i--) {
      java.util.Properties p = @PKG@.ZCfg.read(h.resolve((String) names.get(i)));
      if (p == null) continue;
      java.util.TreeMap m = parseAll(p, new String[1], new int[1], false);
      if (!m.isEmpty()) { name[0] = (String) names.get(i); return m; }
    }
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("histread", "could not read the regions history: " + t); }
  return null;
}""")
M(sto, r"""
public static boolean blank(java.nio.file.Path f) {
  try { return new String(java.nio.file.Files.readAllBytes(f), "UTF-8").trim().length() == 0; } catch (Throwable t) { return false; }
}""")
# load (fail closed - protection never silently drops):
#  - a pending write lands first (max 1 s);
#  - a file that cannot be read (3 tries) keeps the regions in memory; with none in memory (a start) the newest good history copy protects;
#    edits are blocked meanwhile;
#  - fixer 2 (critic 2 #1): a MISSING file or one with NO region line while regions are in memory keeps them (edits blocked) - only
#    clear = true (/zones reload clear) accepts it; at a start (nothing in memory) a missing or blank file is restored from the newest
#    good history copy and written back (a file holding only comments = no regions on purpose);
#  - bad lines block edits; a bad region keeps protecting (fallback()).
M(sto, r"""
public static synchronized String load(boolean clear) {
  long until = System.currentTimeMillis() + 1000L;
  while (LAST_SEQ > @PKG@.ZSave.written() && System.currentTimeMillis() < until) { try { Thread.sleep(20L); } catch (Throwable t) { break; } }
  if (LAST_SEQ > @PKG@.ZSave.written()) @PKG@.ZCfg.warn("a regions.properties write is still pending - /zones reload reads the file as it is on disk");
  boolean exists = FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0]);
  java.util.Properties p = @PKG@.ZCfg.read(FILE);
  String[] hn = new String[1];
  if (p == null) {
    BAD = "regions.properties cannot be read";
    if (REGIONS.isEmpty()) {
      java.util.TreeMap h = fromHistoryAll(hn);
      if (h != null) {
        REGIONS.putAll(h);
        publish();
        @PKG@.ZCfg.warn("regions.properties cannot be read - the " + h.size() + " regions of history/" + hn[0] + " protect meanwhile; region edits are blocked until /zones reload reads the file");
        return "regions.properties UNREADABLE (" + h.size() + " regions from history/" + hn[0] + " protect)";
      }
      @PKG@.ZCfg.warn("regions.properties cannot be read and history/ has no copy - NO region protects until /zones reload reads it");
      return "regions.properties UNREADABLE - NO region protects";
    }
    @PKG@.ZCfg.warn("regions.properties cannot be read - the " + REGIONS.size() + " regions in memory keep protecting; region edits are blocked until /zones reload reads it");
    return "regions.properties UNREADABLE (" + REGIONS.size() + " regions kept)";
  }
  int n = 0;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) { if (((String) it.next()).startsWith("region.")) n++; }
  if (n == 0 && !clear) {
    String what = exists ? "holds no region" : "is missing";
    if (!REGIONS.isEmpty()) {
      BAD = "regions.properties " + what;
      @PKG@.ZCfg.warn("regions.properties " + what + " - the " + REGIONS.size() + " regions in memory keep protecting; region edits are blocked. Put the file back + /zones reload, or /zones reload clear to really remove every region");
      return "regions.properties " + (exists ? "EMPTY" : "MISSING") + " (" + REGIONS.size() + " regions kept; /zones reload clear removes them)";
    }
    if (!exists || blank(FILE)) {
      java.util.TreeMap h = fromHistoryAll(hn);
      if (h != null) {
        REGIONS.putAll(h);
        BAD = null;
        publish();
        save("SkyyZones", "restored " + h.size() + " regions from history/" + hn[0] + " (regions.properties " + (exists ? "was blank" : "was missing") + ")");
        @PKG@.ZCfg.warn("regions.properties " + (exists ? "was blank" : "was missing") + " - the " + h.size() + " regions of history/" + hn[0] + " are restored and written back (/zones reload clear removes every region)");
        return REGIONS.size() + " regions in " + INDEX.byWorld.size() + " worlds (RESTORED from history/" + hn[0] + ")";
      }
    }
  }
  String[] bad = new String[1];
  int[] kept = new int[1];
  java.util.TreeMap out = parseAll(p, bad, kept, true);
  int dropped = REGIONS.size();
  if (clear && n == 0 && dropped > 0) {
    @PKG@.ZSave.keep(text());
    @PKG@.ZSave.logLine("/zones reload clear\tevery region removed (" + dropped + "; the old text is in history/)");
    @PKG@.ZCfg.warn("/zones reload clear: every region removed (" + dropped + ") - the old text is kept in history/");
  }
  REGIONS.clear();
  REGIONS.putAll(out);
  BAD = bad[0];
  publish();
  if (clear && !exists) @PKG@.ZCfg.writeIfMissing(FILE, HEAD + "\n");
  return REGIONS.size() + " regions in " + INDEX.byWorld.size() + " worlds" + (bad[0] == null ? "" : " - PROBLEM: " + bad[0] + " (region edits blocked until fixed + /zones reload" + (kept[0] > 0 ? "; " + kept[0] + " bad " + (kept[0] == 1 ? "region keeps" : "regions keep") + " protecting" : "") + ")");
}""")
M(sto, "public static String load() { return load(false); }")
M(sto, r"""
public static String start() {
  String r = load(false);
  if (REGIONS.isEmpty() && BAD == null) @PKG@.ZCfg.writeIfMissing(FILE, HEAD + "\n");
  return r;
}""")
# ---- mutators: "!" + why = refused (nothing changed); else the answer
M(sto, r"""
public static String blocked() {
  String b = BAD;
  return b == null ? null : "!The regions file has a problem (" + b + ") - fix Skyy_SkyyZones/regions.properties, then /zones reload. Nothing was changed.";
}""")
M(sto, r"""
public static synchronized @PKG@.ZRegion get(String id) {
  return id == null ? null : (@PKG@.ZRegion) REGIONS.get(id);
}""")
M(sto, r"""
public static synchronized String create(String id, String world, String mode, int[] box, String who) {
  String bl = blocked(); if (bl != null) return bl;
  if (id == null || !id.matches("[a-z0-9_]{1,40}")) return "!A region id is 1-40 of a-z, 0-9 and _.";
  if (REGIONS.containsKey(id)) return "!Region " + id + " already exists (/zones region addbox " + id + " adds a box to it).";
  int m = @PKG@.ZRegion.modeOf(mode);
  if (m < 0) return "!The mode is full or skyblock.";
  if (REGIONS.size() >= MAX_REGIONS) return "!There are already " + MAX_REGIONS + " regions.";
  String bp = @PKG@.ZRegion.boxProblem(box);
  if (bp.length() > 0) return "!" + bp + ".";
  @PKG@.ZRegion r = new @PKG@.ZRegion();
  r.id = id; r.world = world; r.mode = m; r.priority = 0; r.box = (int[]) box.clone();
  REGIONS.put(id, r);
  publish();
  save(who, "create " + id + " " + r.modeName() + " in " + world + " " + @PKG@.ZRegion.boxText(r.box));
  return "Region " + id + " created (" + r.modeName() + ") in " + world + ": " + @PKG@.ZRegion.size(r.box, 0) + " blocks."
    + (m == 1 ? " Nothing breaks there until you list its resource types: /zones region types " + id + " stone,copper" : " Nothing breaks or is placed there now.");
}""")
M(sto, r"""
public static synchronized String delete(String id, String who) {
  String bl = blocked(); if (bl != null) return bl;
  @PKG@.ZRegion r = get(id);
  if (r == null) return "!No region " + id + ".";
  REGIONS.remove(id);
  publish();
  save(who, "delete " + id + " (was " + r.modeName() + " in " + r.world + " " + @PKG@.ZRegion.boxText(r.box) + ")");
  return "Region " + id + " deleted.";
}""")
M(sto, r"""
public static synchronized String addBox(String id, String world, int[] box, String who) {
  String bl = blocked(); if (bl != null) return bl;
  @PKG@.ZRegion r = get(id);
  if (r == null) return "!No region " + id + ".";
  if (!r.world.equals(world)) return "!Region " + id + " is in world " + r.world + " - stand in that world to add a box.";
  if (r.boxes() >= @PKG@.ZRegion.MAX_BOXES) return "!Region " + id + " already has " + @PKG@.ZRegion.MAX_BOXES + " boxes.";
  String bp = @PKG@.ZRegion.boxProblem(box);
  if (bp.length() > 0) return "!" + bp + ".";
  @PKG@.ZRegion n = r.copy();
  int[] nb = new int[r.box.length + 6];
  System.arraycopy(r.box, 0, nb, 0, r.box.length);
  System.arraycopy(box, 0, nb, r.box.length, 6);
  n.box = nb;
  REGIONS.put(id, n);
  publish();
  save(who, "addbox " + id + " " + @PKG@.ZRegion.boxText(box));
  return "Box " + n.boxes() + " added to " + id + " (" + @PKG@.ZRegion.size(box, 0) + " blocks).";
}""")
# one field of a region COPY n: mode / priority / title / types / flags; null = done (shown[0] = the value as shown), else "!" + why
M(sto, r"""
public static String applyField(@PKG@.ZRegion n, String field, String value, String[] shown) {
  String v = value == null ? "" : value.trim();
  shown[0] = v;
  if (field.equals("mode")) {
    int m = @PKG@.ZRegion.modeOf(v);
    if (m < 0) return "!The mode is full or skyblock.";
    n.mode = m; shown[0] = n.modeName();
  } else if (field.equals("priority")) {
    int pr = 0;
    try { pr = Integer.parseInt(v); } catch (Throwable t) { return "!The priority is a whole number from -1000 to 1000."; }
    if (pr < -1000 || pr > 1000) return "!The priority is a whole number from -1000 to 1000.";
    n.priority = pr; shown[0] = String.valueOf(pr);
  } else if (field.equals("title")) {
    String t = v.equalsIgnoreCase("none") ? "" : v.replace('_', ' ');
    if (!titleOk(t)) return "!A title is at most 40 letters, digits, spaces and ' ! & . , ( ) ? : - (type _ for a space).";
    n.title = t; shown[0] = t.length() == 0 ? "(none)" : t;
  } else if (field.equals("types")) {
    String[] a = v.equalsIgnoreCase("none") ? new String[0] : @PKG@.ZCfg.splitList(v.toLowerCase());
    for (int i = 0; i < a.length; i++) {
      if (!@PKG@.ZCfg.TYPES.containsKey(a[i])) return "!No resource type '" + a[i] + "'. Types: " + typeList() + " (Server Setup -> Zones -> Resource types, or /zones type <id> <block ids>).";
    }
    n.types = a; shown[0] = a.length == 0 ? "(none)" : @PKG@.ZRegion.join(a);
  } else if (field.equals("flags")) {
    String[] a = v.equalsIgnoreCase("none") ? new String[0] : @PKG@.ZCfg.splitList(v.toLowerCase());
    for (int i = 0; i < a.length; i++) if (!a[i].equals("containers") && !a[i].equals("furnaces")) return "!Flags: containers, furnaces (or none).";
    n.setFlags(@PKG@.ZRegion.join(a)); shown[0] = a.length == 0 ? "(none)" : n.flags;
  } else return "!Unknown region setting " + field + ".";
  return null;
}""")
M(sto, r"""
public static synchronized String set(String id, String field, String value, String who) {
  String bl = blocked(); if (bl != null) return bl;
  @PKG@.ZRegion r = get(id);
  if (r == null) return "!No region " + id + ".";
  @PKG@.ZRegion n = r.copy();
  String[] shown = new String[1];
  String e = applyField(n, field, value, shown);
  if (e != null) return e;
  REGIONS.put(id, n);
  publish();
  save(who, field + " " + id + " = " + shown[0]);
  return "Region " + id + ": " + field + " = " + shown[0] + "." + (field.equals("types") && n.mode != 1 ? " (It is a FULL region - types only count in skyblock mode: /zones region mode " + id + " skyblock)" : "");
}""")
# several fields at once, all or nothing (the Server Setup regions table): one change, one history copy, one change-log line
M(sto, r"""
public static synchronized String setMany(String id, String[] fields, String[] values, String who) {
  String bl = blocked(); if (bl != null) return bl;
  @PKG@.ZRegion r = get(id);
  if (r == null) return "!No region " + id + ".";
  @PKG@.ZRegion n = r.copy();
  StringBuilder sb = new StringBuilder();
  String[] shown = new String[1];
  for (int i = 0; i < fields.length; i++) {
    String e = applyField(n, fields[i], values[i], shown);
    if (e != null) return e;
    if (sb.length() > 0) sb.append(", ");
    sb.append(fields[i]).append(' ').append(shown[0]);
  }
  if (n.lines().equals(r.lines())) return "Region " + id + ": nothing changed.";
  REGIONS.put(id, n);
  publish();
  save(who, "edit " + id + ": " + sb.toString());
  return "Region " + id + " changed: " + sb.toString() + ".";
}""")
# the kit's "Re-read files" action + /zones reload
M(cfg, r"""
public static String reloadFiles(boolean clear) {
  String t = loadTypes(false);
  String r = @PKG@.ZStore.load(clear);
  return "Re-read: " + t + "; " + r + ".";
}""")
M(cfg, "public static String reloadFiles() { return reloadFiles(false); }")
M(cfg, r"""
public static Object[] reloadAction(java.util.UUID who, String name) {
  String m = reloadFiles();
  info(m + " (Server Setup, " + name + ")");
  return new Object[] { "ok", "", m };
}""")

# =====================================================================================================================================
# ZEng: the engine calls (API = the harness stand-in)
# =====================================================================================================================================
eng = mk("ZEng")
F(eng, "public static volatile @PKG@.ZApi API = null;")
F(eng, "public static boolean FAILED_ONCE = false;")
M(eng, r"""
public static void fail(String what, Throwable t) {
  @PKG@.ZCfg.warnOnce("eng:" + what, what + " failed (logged once): " + t);
}""")
M(eng, r"""
public static void notify(@PR@ pr, String text) {
  if (pr == null || text == null) return;
  @PKG@.ZApi a = API;
  if (a != null) { a.notify(pr, text); return; }
  try { @NTU@.sendNotification(pr.getPacketHandler(), @MSG@.raw(text), @NST@.Warning); } catch (Throwable t) { fail("notification", t); }
}""")
M(eng, r"""
public static void title(@PR@ pr, String t, String sub) {
  if (pr == null || t == null) return;
  @PKG@.ZApi a = API;
  if (a != null) { a.title(pr, t, sub); return; }
  try { @ETU@.showEventTitleToPlayer(pr, @MSG@.raw(t), @MSG@.raw(sub == null ? "" : sub), false); } catch (Throwable x) { fail("event title", x); }
}""")
M(eng, r"""
public static void particle(String id, double x, double y, double z, java.util.List to, @ST@ st) {
  @PKG@.ZApi a = API;
  if (a != null) { a.particle(id, x, y, z, to, st); return; }
  try { @PTU@.spawnParticleEffect(id, (@V3DC@) new @V3D@(x, y, z), to, (@CAC@) st); } catch (Throwable t) { fail("particle", t); }
}""")
M(eng, r"""
public static int[] target(@REF@ r, @ST@ st) {
  @PKG@.ZApi a = API;
  if (a != null) return a.target(r, st);
  try {
    @V3I@ v = @TGU@.getTargetBlock(r, 16.0, (@CAC@) st);
    if (v == null) return null;
    return new int[] { v.x, v.y, v.z };
  } catch (Throwable t) { fail("target block", t); return null; }
}""")
# probe Z6: the vanilla builder-tool selection (null = none / no BuilderTools)
M(eng, r"""
public static int[] selection(@REF@ r, @ST@ st, @PR@ pr) {
  @PKG@.ZApi a = API;
  if (a != null) return a.selection(r, st, pr);
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return null;
    @BTS@ bs = @BTP@.getState(p, pr);
    @BSEL@ s = bs == null ? null : bs.getSelection();
    if (s == null || !s.hasSelectionBounds()) return null;
    @V3I@ lo = s.getSelectionMin();
    @V3I@ hi = s.getSelectionMax();
    if (lo == null || hi == null) return null;
    return @PKG@.ZRegion.norm(lo.x, lo.y, lo.z, hi.x, hi.y, hi.z);
  } catch (Throwable t) { fail("builder selection", t); return null; }
}""")
M(eng, r"""
public static int count(@IC@ c, String id) {
  int n = 0;
  if (c == null) return 0;
  int cap = c.getCapacity();
  for (int i = 0; i < cap; i++) {
    @IS@ s = c.getItemStack((short) i);
    if (s != null && !s.isEmpty() && id.equals(s.getItemId())) n = n + s.getQuantity();
  }
  return n;
}""")
# 0 given, 1 already has one, 2 no room, 3 error (storage first; counted before and after)
M(eng, r"""
public static int give(@REF@ r, @ST@ st, String id) {
  @PKG@.ZApi a = API;
  if (a != null) return a.give(r, st, id);
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return 3;
    @IC@ c = p.getInventory().getCombinedStorageFirst();
    int before = count(c, id);
    if (before > 0) return 1;
    c.addItemStack(new @IS@(id, 1));
    return count(c, id) > before ? 0 : 2;
  } catch (Throwable t) { fail("give the wand", t); return 3; }
}""")
# the 0.7 recipe (SkyyMerchants MerchEng.block): loaded chunk + section only, never loads one; null = not loaded
M(eng, r"""
public static String blockAt(@WLD@ w, int x, int y, int z) {
  @PKG@.ZApi a = API;
  if (a != null) return a.blockAt(w, x, y, z);
  try {
    if (w == null || y < 0 || y >= 320) return null;
    @CHS@ cs = w.getChunkStore();
    @REF@ c = cs.getChunkReference(@CHU@.indexChunkFromBlock(x, z));
    if (c == null || !c.isValid()) return null;
    @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (r == null || !r.isValid()) return null;
    Object s = cs.getStore().getComponent(r, @BSEC@.getComponentType());
    if (!(s instanceof @BSEC@)) return null;
    Object t = @BTY@.getAssetMap().getAsset(((@BSEC@) s).get(x, y, z));
    if (!(t instanceof @BTY@)) return "Empty";
    return String.valueOf(((@BTY@) t).getId());
  } catch (Throwable t) { fail("block lookup", t); return null; }
}""")

# =====================================================================================================================================
# ZMsg: chat lines + the throttled refusal note
# =====================================================================================================================================
msg = mk("ZMsg")
F(msg, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
M(msg, r"""
public static void tell(@PR@ pr, String text, String color) {
  if (pr == null || text == null) return;
  try { pr.sendMessage(@MSG@.raw(text).color(color)); } catch (Throwable t) { }
}""")
M(msg, r"""
public static boolean due(java.util.UUID u, long now) {
  Long l = (Long) LAST.get(u);
  long gap = 1000L * (long) @PKG@.ZCfg.MSG_GAP;
  if (l != null && now - l.longValue() < gap) return false;
  LAST.put(u, Long.valueOf(now));
  return true;
}""")
M(msg, r"""
public static void refuse(@PR@ pr, String text) {
  if (pr == null) return;
  if (due(pr.getUuid(), System.currentTimeMillis())) @PKG@.ZEng.notify(pr, text);
}""")

# =====================================================================================================================================
# ZBuild: builder mode (memory only = off at every login / restart)
# =====================================================================================================================================
bld = mk("ZBuild")
F(bld, "public static final java.util.concurrent.ConcurrentHashMap ON = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> long[] { since, lastRemind, lastPermCheck }
F(bld, "public static final long RECHECK_MS = 30000L;")
M(bld, "public static boolean on(java.util.UUID u) { return u != null && ON.containsKey(u); }")
M(bld, r"""
public static void set(java.util.UUID u, String name, boolean on) {
  if (u == null) return;
  long now = System.currentTimeMillis();
  if (on) { ON.put(u, new long[] { now, now, now }); @PKG@.ZCfg.bridge().put("zones:build:" + u, Boolean.TRUE); }
  else { ON.remove(u); @PKG@.ZCfg.bridge().remove("zones:build:" + u, Boolean.TRUE); }
  @PKG@.ZCfg.info("builder mode " + (on ? "ON" : "off") + " for " + name);
}""")
# fixer 2 (engine #2): the node is re-checked at most every RECHECK_MS while builder mode is on - a builder who lost skyyzones.build (and
# skyyzones.admin) mid-session drops out of builder mode at their next protected action
M(bld, r"""
public static boolean bypass(@PR@ pr) {
  if (pr == null) return false;
  java.util.UUID u = pr.getUuid();
  if (u == null) return false;
  long[] s = (long[]) ON.get(u);
  if (s != null) {
    long now = System.currentTimeMillis();
    if (now - s[2] < RECHECK_MS) return true;
    s[2] = now;
    if (@PKG@.ZCfg.permTest(u, "@BUILDN@") || @PKG@.ZCfg.permTest(u, "@ADMIN@")) return true;
    set(u, pr.getUsername(), false);
    @PKG@.ZEng.notify(pr, "Builder mode off - you no longer have skyyzones.build.");
  }
  return @PKG@.ZCfg.OP_BYPASS && @PKG@.ZCfg.permTest(u, "@ADMIN@");
}""")
M(bld, r"""
public static void remind(@PR@ pr, java.util.UUID u, long now) {
  long[] s = (long[]) ON.get(u);
  if (s == null || @PKG@.ZCfg.REMIND <= 0) return;
  if (now - s[1] < 1000L * (long) @PKG@.ZCfg.REMIND) return;
  s[1] = now;
  @PKG@.ZEng.notify(pr, "Build mode is ON - protection does not stop you. /zones build off");
}""")
M(bld, r"""
public static void clearAll() {
  java.util.Iterator it = ON.keySet().iterator();
  while (it.hasNext()) { try { @PKG@.ZCfg.bridge().remove("zones:build:" + it.next(), Boolean.TRUE); } catch (Throwable t) { } }
  ON.clear();
}""")

# =====================================================================================================================================
# ZSel + ZWand: the Zone Wand corners (memory only, per player)
# =====================================================================================================================================
sel = mk("ZSel")
for f in ("public String world;", "public int ax;", "public int ay;", "public int az;", "public int bx;", "public int by;", "public int bz;",
          "public boolean a;", "public boolean b;", "public boolean nextB;", "public boolean last;", "public int lx;", "public int ly;", "public int lz;",
          "public long lt;"):
    F(sel, f)
C(sel, "public ZSel(String w) { this.world = w; }")
wnd = mk("ZWand")
F(wnd, "public static final String ID = \"@WAND@\";")
F(wnd, "public static final java.util.concurrent.ConcurrentHashMap SEL = new java.util.concurrent.ConcurrentHashMap();")
# null = the same block again while the hits keep coming (a held click fires many events; 400 ms after the last one it counts again,
# so the B corner can start the next box and a 1-block box is possible) - nothing to say
F(wnd, "public static final long REPEAT_MS = 400L;")
M(wnd, r"""
public static String hitAt(java.util.UUID u, String w, int x, int y, int z, long now) {
  @PKG@.ZSel s = (@PKG@.ZSel) SEL.get(u);
  if (s == null || !w.equals(s.world)) { s = new @PKG@.ZSel(w); SEL.put(u, s); }
  if (s.last && s.lx == x && s.ly == y && s.lz == z && now - s.lt < REPEAT_MS) { s.lt = now; return null; }
  s.last = true; s.lx = x; s.ly = y; s.lz = z; s.lt = now;
  if (!s.nextB) {
    s.ax = x; s.ay = y; s.az = z; s.a = true; s.nextB = true;
    return "Zone Wand: corner A = " + x + " " + y + " " + z + ". Now hit the opposite corner (B).";
  }
  s.bx = x; s.by = y; s.bz = z; s.b = true; s.nextB = false;
  int[] b = @PKG@.ZRegion.norm(s.ax, s.ay, s.az, s.bx, s.by, s.bz);
  String p = @PKG@.ZRegion.boxProblem(b);
  return "Zone Wand: corner B = " + x + " " + y + " " + z + " - box " + @PKG@.ZRegion.size(b, 0) + (p.length() > 0 ? " (too big: " + p + ")" : "")
    + ". Next: /zones region create <name> <full or skyblock> (or /zones region addbox <name>).";
}""")
M(wnd, "public static String hit(java.util.UUID u, String w, int x, int y, int z) { return hitAt(u, w, x, y, z, System.currentTimeMillis()); }")
M(wnd, r"""
public static int[] box(java.util.UUID u, String w) {
  @PKG@.ZSel s = (@PKG@.ZSel) SEL.get(u);
  if (s == null || !s.a || !s.b || w == null || !w.equals(s.world)) return null;
  return @PKG@.ZRegion.norm(s.ax, s.ay, s.az, s.bx, s.by, s.bz);
}""")
M(wnd, r"""
public static void use(@PR@ pr, String w, int x, int y, int z) {
  java.util.UUID u = pr.getUuid();
  if (!@PKG@.ZCfg.permTest(u, "@ADMIN@")) { @PKG@.ZMsg.refuse(pr, "Only zone admins can use the Zone Wand."); return; }
  String m = hit(u, w, x, y, z);
  if (m != null) @PKG@.ZMsg.tell(pr, m, "@INFO@");
}""")

# =====================================================================================================================================
# ZGuard: ONE registerSystem per class; the acting entity's event (Archetype.empty() like SkyyIslands' guards)
# =====================================================================================================================================
guard = mk("ZGuard", T["EES"])
for f in ("public static boolean FAILED_ONCE = false;",
          "public static final java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong ALLOWED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong BYPASSED = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong MOBS = new java.util.concurrent.atomic.AtomicLong();",
          "public static final java.util.concurrent.atomic.AtomicLong FAILS = new java.util.concurrent.atomic.AtomicLong();"):
    F(guard, f)
C(guard, "public ZGuard(Class cls) { super(cls); }")
M(guard, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
# first among the systems of the event (the engine's own RootDependency, like its first systems): other mods' handlers then skip a cancelled event
M(guard, r"""
public java.util.Set getDependencies() {
  return com.hypixel.hytale.component.dependency.RootDependency.firstSet();
}""")
# hooks the subclasses override (declared before handle(): javassist has no forward references)
M(guard, "public @V3I@ target(@EV@ ev) { return null; }")
M(guard, "public String held(@EV@ ev) { return null; }")
M(guard, "public String block(@EV@ ev) { return \"\"; }")
M(guard, "public int action(@EV@ ev, String held) { return @PKG@.ZRules.OTHER; }")
M(guard, "public boolean wandable(@EV@ ev) { return false; }")
M(guard, r"""
public static String idOf(@IS@ s) {
  if (s == null || s.isEmpty()) return null;
  return s.getItemId();
}""")
M(guard, r"""
public static String typeId(@BTY@ bt) {
  if (bt == null) return "";
  try { return @PKG@.ZRules.bare(String.valueOf(bt.getId())); } catch (Throwable t) { return ""; }
}""")
M(guard, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  boolean scoped = false;
  boolean free = false;
  try {
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    @V3I@ b = target(ev);
    if (b == null) return;
    String wn = w.getName();
    String held = held(ev);
    if (@PKG@.ZWand.ID.equals(held) && wandable(ev)) {
      if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
      @REF@ r0 = chunk.getReferenceTo(idx);
      @PR@ p0 = r0 == null ? null : (@PR@) st.getComponent(r0, @PR@.getComponentType());
      if (p0 != null) @PKG@.ZWand.use(p0, wn, b.x, b.y, b.z);
      return;
    }
    if (!@PKG@.ZCfg.ON) return;
    @PKG@.ZIndex ix = @PKG@.ZStore.INDEX;
    boolean pw = @PKG@.ZCfg.protectedWorld(wn);
    if (!pw && !ix.has(wn)) return;
    scoped = pw || ix.top(wn, b.x, b.y, b.z) != null;
    int act = action(ev, held);
    if (act == @PKG@.ZRules.OTHER) return;
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) {
      if (!@PKG@.ZCfg.MOBS || (act != @PKG@.ZRules.BREAK && act != @PKG@.ZRules.PLACE)) return;
      if (@PKG@.ZRules.decide(ix, wn, pw, b.x, b.y, b.z, act, block(ev)) != @PKG@.ZRules.ALLOW) {
        if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
        MOBS.incrementAndGet();
      }
      return;
    }
    if (@PKG@.ZBuild.bypass(pr)) { free = true; BYPASSED.incrementAndGet(); return; }
    int d = @PKG@.ZRules.decide(ix, wn, pw, b.x, b.y, b.z, act, block(ev));
    if (d == @PKG@.ZRules.ALLOW) { ALLOWED.incrementAndGet(); return; }
    if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
    REFUSED.incrementAndGet();
    @PKG@.ZMsg.refuse(pr, @PKG@.ZRules.why(d));
  } catch (Throwable t) {
    FAILS.incrementAndGet();
    boolean closed = false;
    if (scoped && !free && @PKG@.ZCfg.ON && ev instanceof @ICE@) { try { ((@ICE@) ev).setCancelled(true); closed = true; } catch (Throwable t2) { } }
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ZCfg.warn("guard failed (logged once; " + (closed ? "the action was REFUSED - fail closed" : "outside protection, nothing refused") + "; /zones info counts them): " + t); }
  }
}""")
gcls = []
for gname, gev in (("ZGuardBreak", "BBE"), ("ZGuardDamage", "DBE"), ("ZGuardPlace", "PLBE"), ("ZGuardUse", "UBPRE")):
    gc = mk(gname, PKG + ".ZGuard")
    C(gc, "public %s() { super(@%s@.class); }" % (gname, gev))
    gcls.append(gc)
gB, gD, gP, gU = gcls
for gc, ev in ((gB, "BBE"), (gD, "DBE")):
    M(gc, "public @V3I@ target(@EV@ ev) { return ev instanceof @X@ ? ((@X@) ev).getTargetBlock() : null; }".replace("@X@", "@%s@" % ev))
    M(gc, "public String held(@EV@ ev) { return ev instanceof @X@ ? @PKG@.ZGuard.idOf(((@X@) ev).getItemInHand()) : null; }".replace("@X@", "@%s@" % ev))
    M(gc, "public String block(@EV@ ev) { return ev instanceof @X@ ? @PKG@.ZGuard.typeId(((@X@) ev).getBlockType()) : \"\"; }".replace("@X@", "@%s@" % ev))
    M(gc, "public int action(@EV@ ev, String held) { return @PKG@.ZRules.BREAK; }")
    M(gc, "public boolean wandable(@EV@ ev) { return true; }")
M(gP, "public @V3I@ target(@EV@ ev) { return ev instanceof @PLBE@ ? ((@PLBE@) ev).getTargetBlock() : null; }")
M(gP, "public String held(@EV@ ev) { return ev instanceof @PLBE@ ? @PKG@.ZGuard.idOf(((@PLBE@) ev).getItemInHand()) : null; }")
M(gP, "public String block(@EV@ ev) { return ev instanceof @PLBE@ ? @PKG@.ZRules.bare(@PKG@.ZGuard.idOf(((@PLBE@) ev).getItemInHand())) : \"\"; }")
M(gP, "public int action(@EV@ ev, String held) { return @PKG@.ZRules.PLACE; }")
M(gU, "public @V3I@ target(@EV@ ev) { return ev instanceof @UBE@ ? ((@UBE@) ev).getTargetBlock() : null; }")
M(gU, r"""
public String held(@EV@ ev) {
  if (!(ev instanceof @UBE@)) return null;
  @ICTX@ c = ((@UBE@) ev).getContext();
  return c == null ? null : @PKG@.ZGuard.idOf(c.getHeldItem());
}""")
M(gU, "public String block(@EV@ ev) { return ev instanceof @UBE@ ? @PKG@.ZGuard.typeId(((@UBE@) ev).getBlockType()) : \"\"; }")
M(gU, r"""
public int action(@EV@ ev, String held) {
  if (!(ev instanceof @UBE@)) return @PKG@.ZRules.OTHER;
  @UBE@ e = (@UBE@) ev;
  return @PKG@.ZRules.useAction(e.getBlockType(), e.getInteractionType(), held);
}""")
M(gU, r"""
public boolean wandable(@EV@ ev) {
  if (!(ev instanceof @UBE@)) return false;
  @ITY@ t = ((@UBE@) ev).getInteractionType();
  return t == @ITY@.Primary || t == @ITY@.Use || t == @ITY@.Secondary;
}""")

# =====================================================================================================================================
# ZShow + ZTick: titles, the outline, the builder reminder (every 0.5 s per player, world thread)
# =====================================================================================================================================
shw = mk("ZShow")
for f in ("public String world;", "public String id;", "public long until;", "public long last;"):
    F(shw, f)
C(shw, "public ZShow(String w, String id, long until) { this.world = w; this.id = id; this.until = until; this.last = 0L; }")
tick = mk("ZTick", T["ETS"])
for f in ("public static final java.util.concurrent.ConcurrentHashMap ACC = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> double[1]
          "public static final java.util.concurrent.ConcurrentHashMap CUR = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> String[] { key, title }
          "public static final java.util.concurrent.ConcurrentHashMap SHOWN = new java.util.concurrent.ConcurrentHashMap();", # uuid|world|id -> Long
          "public static final java.util.concurrent.ConcurrentHashMap SHOW = new java.util.concurrent.ConcurrentHashMap();",  # uuid -> ZShow
          "public static boolean FAILED_ONCE = false;", "public static final int MAX_POINTS = 160;", "public static final int MAX_BOXES = 8;"):
    F(tick, f)
C(tick, "public ZTick() { super(); }")
M(tick, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(tick, "public boolean isParallel(int a, int b) { return false; }")
M(tick, r"""
public static void enter(@PR@ pr, java.util.UUID u, String w, @PKG@.ZRegion r, long now) {
  String k = u + "|" + w + "|" + r.id;
  Long l = (Long) SHOWN.get(k);
  if (l != null && now - l.longValue() < 1000L * (long) @PKG@.ZCfg.TITLE_GAP) return;
  SHOWN.put(k, Long.valueOf(now));
  @PKG@.ZEng.title(pr, r.title, r.mode == 1 ? "Gathering area" : "Protected area");
}""")
M(tick, r"""
public static void titles(@PR@ pr, java.util.UUID u, String w, int x, int y, int z, long now) {
  @PKG@.ZRegion t = @PKG@.ZStore.INDEX.topTitled(w, x, y, z);
  String key = t == null ? "" : w + "|" + t.id;
  String[] was = (String[]) CUR.get(u);
  if (was != null && was[0].equals(key)) return;
  CUR.put(u, new String[] { key, t == null ? "" : t.title, w });
  if (t != null) { enter(pr, u, w, t, now); return; }
  if (was != null && was[1].length() > 0 && was[2].equals(w) && @PKG@.ZCfg.LEAVE) @PKG@.ZEng.notify(pr, "You left " + was[1] + ".");
}""")
# the 12 edges of up to MAX_BOXES boxes near the player, at most MAX_POINTS markers per pass (step grows with the size), to YOU only
M(tick, r"""
public static int draw(@REF@ ref, @ST@ st, @PKG@.ZShow s, int px, int py, int pz) {
  java.util.ArrayList boxes = new java.util.ArrayList();
  @PKG@.ZRegion[] a = @PKG@.ZStore.INDEX.in(s.world);
  for (int i = 0; i < a.length && boxes.size() < MAX_BOXES; i++) {
    if (s.id.length() > 0 && !a[i].id.equals(s.id)) continue;
    int[] b = a[i].box;
    for (int j = 0; j + 5 < b.length && boxes.size() < MAX_BOXES; j = j + 6) {
      if (px < b[j] - 64 || px > b[j + 3] + 64 || pz < b[j + 2] - 64 || pz > b[j + 5] + 64) continue;
      boxes.add(new int[] { b[j], b[j + 1], b[j + 2], b[j + 3] + 1, b[j + 4] + 1, b[j + 5] + 1 });
    }
  }
  if (boxes.isEmpty()) return 0;
  long len = 0L;
  for (int i = 0; i < boxes.size(); i++) { int[] b = (int[]) boxes.get(i); len = len + 4L * (long) ((b[3] - b[0]) + (b[4] - b[1]) + (b[5] - b[2])); }
  int step = (int) Math.max(2L, (len + MAX_POINTS - 1) / MAX_POINTS);
  java.util.ArrayList to = new java.util.ArrayList();
  to.add(ref);
  String id = @PKG@.ZCfg.particle();
  int n = 0;
  for (int i = 0; i < boxes.size() && n < MAX_POINTS; i++) {
    int[] b = (int[]) boxes.get(i);
    int[] xs = new int[] { b[0], b[3] };
    int[] ys = new int[] { b[1], b[4] };
    int[] zs = new int[] { b[2], b[5] };
    for (int p = 0; p < 2; p++) for (int q = 0; q < 2; q++) {
      for (int v = b[0]; v <= b[3] && n < MAX_POINTS; v = v + step) { @PKG@.ZEng.particle(id, (double) v, (double) ys[p], (double) zs[q], to, st); n++; }
      for (int v = b[1]; v <= b[4] && n < MAX_POINTS; v = v + step) { @PKG@.ZEng.particle(id, (double) xs[p], (double) v, (double) zs[q], to, st); n++; }
      for (int v = b[2]; v <= b[5] && n < MAX_POINTS; v = v + step) { @PKG@.ZEng.particle(id, (double) xs[p], (double) ys[q], (double) v, to, st); n++; }
    }
  }
  return n;
}""")
M(tick, r"""
public static void show(@PR@ pr, java.util.UUID u, @REF@ ref, @ST@ st, String w, int x, int y, int z, long now) {
  @PKG@.ZShow s = (@PKG@.ZShow) SHOW.get(u);
  if (s == null) return;
  if (now > s.until || !s.world.equals(w)) { SHOW.remove(u); return; }
  if (now - s.last < 1000L) return;
  s.last = now;
  draw(ref, st, s, x, y, z);
}""")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CB@ cb) {
  try {
    boolean doTitles = @PKG@.ZCfg.ON && @PKG@.ZCfg.TITLES && @PKG@.ZStore.INDEX.count > 0;
    if (!doTitles && SHOW.isEmpty() && @PKG@.ZBuild.ON.isEmpty()) return;
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) st.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    double[] acc = (double[]) ACC.get(u);
    if (acc == null) { acc = new double[1]; ACC.put(u, acc); }
    acc[0] = acc[0] + (double) dt;
    if (acc[0] < 0.5) return;
    acc[0] = 0.0;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) return;
    @V3D@ p = tc.getPosition();
    int x = (int) Math.floor(p.x);
    int y = (int) Math.floor(p.y);
    int z = (int) Math.floor(p.z);
    long now = System.currentTimeMillis();
    String wn = w.getName();
    if (doTitles) titles(pr, u, wn, x, y, z, now);
    if (!SHOW.isEmpty()) show(pr, u, ref, st, wn, x, y, z, now);
    if (!@PKG@.ZBuild.ON.isEmpty()) @PKG@.ZBuild.remind(pr, u, now);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.ZCfg.warn("tick failed (logged once): " + t); }
  }
}""")
M(tick, r"""
public static void forget(java.util.UUID u) {
  ACC.remove(u);
  CUR.remove(u);
  SHOW.remove(u);
  String p = u + "|";
  java.util.Iterator it = SHOWN.keySet().iterator();
  while (it.hasNext()) { if (((String) it.next()).startsWith(p)) it.remove(); }
}""")

# =====================================================================================================================================
# ZFn: the bridge functions
# =====================================================================================================================================
fn = mk("ZFn", None, ("java.util.function.Function",))
F(fn, "public int mode;")
F(fn, "public static volatile @PKG@.ZFn CHECK = null;")
F(fn, "public static volatile @PKG@.ZFn REGION = null;")
C(fn, "public ZFn(int mode) { this.mode = mode; }")
M(fn, r"""
public static int num(Object o) {
  if (o instanceof Number) return ((Number) o).intValue();
  return Integer.parseInt(String.valueOf(o).trim());
}""")
M(fn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 4) return null;
    String w = String.valueOf(a[0]);
    int x = num(a[1]);
    int y = num(a[2]);
    int z = num(a[3]);
    @PKG@.ZIndex ix = @PKG@.ZStore.INDEX;
    if (this.mode == 1) { @PKG@.ZRegion r = ix.top(w, x, y, z); return r == null ? null : r.id; }
    if (!@PKG@.ZCfg.ON) return "allow";
    String act = a.length > 4 && a[4] != null ? String.valueOf(a[4]).toLowerCase() : "break";
    int ac = @PKG@.ZRules.BREAK;
    if (act.equals("place")) ac = @PKG@.ZRules.PLACE;
    else if (act.equals("container")) ac = @PKG@.ZRules.CONTAINER;
    else if (act.equals("furnace")) ac = @PKG@.ZRules.FURNACE;
    String id = a.length > 5 && a[5] != null ? String.valueOf(a[5]) : "";
    int d = @PKG@.ZRules.decide(ix, w, @PKG@.ZCfg.protectedWorld(w), x, y, z, ac, id);
    return d == @PKG@.ZRules.ALLOW ? "allow" : "deny";
  } catch (Throwable t) { return null; }
}""")
M(fn, r"""
public static void publish() {
  java.util.Map b = @PKG@.ZCfg.bridge();
  CHECK = new @PKG@.ZFn(0);
  REGION = new @PKG@.ZFn(1);
  b.put("zones:fn:check", CHECK);
  b.put("zones:fn:region", REGION);
  b.put("zones:version", "@VERSION@");
}""")
M(fn, r"""
public static void unpublish() {
  try {
    java.util.Map b = @PKG@.ZCfg.bridge();
    if (CHECK != null) b.remove("zones:fn:check", CHECK);
    if (REGION != null) b.remove("zones:fn:region", REGION);
    b.remove("zones:version", "@VERSION@");
  } catch (Throwable t) { }
  CHECK = null;
  REGION = null;
}""")

# =====================================================================================================================================
# ZRegKit: the regions table of Server Setup (a kit custom table; reads the published, never-changed INDEX - any thread; edits go
# through the synchronized ZStore like the commands)
# =====================================================================================================================================
rkit = mk("ZRegKit")
M(rkit, r"""
public static @PKG@.ZRegion find(String id) {
  if (id == null) return null;
  java.util.Iterator it = @PKG@.ZStore.INDEX.byWorld.values().iterator();
  while (it.hasNext()) {
    @PKG@.ZRegion[] a = (@PKG@.ZRegion[]) it.next();
    for (int i = 0; i < a.length; i++) if (a[i].id.equals(id)) return a[i];
  }
  return null;
}""")
M(rkit, r"""
public static String[] customKeys(String tableKey) {
  java.util.TreeSet ids = new java.util.TreeSet();
  java.util.Iterator it = @PKG@.ZStore.INDEX.byWorld.values().iterator();
  while (it.hasNext()) {
    @PKG@.ZRegion[] a = (@PKG@.ZRegion[]) it.next();
    for (int i = 0; i < a.length; i++) ids.add(a[i].id);
  }
  return (String[]) ids.toArray(new String[ids.size()]);
}""")
# region[<id>] -> one editable line (max 200: SkyyMenu's table cell), parts split by ';':
#   "<full|skyblock>; priority N; types a,b|none; flags x|none; title Text|none; world W; N box(es) X x Y x Z [+]"
# world + boxes are shown, not editable (boxes need wand corners). "" for the row itself, null = no such region.
M(rkit, r"""
public static String boxCell(@PKG@.ZRegion r) {
  return r.boxes() + (r.boxes() == 1 ? " box " : " boxes ") + @PKG@.ZRegion.size(r.box, 0) + (r.boxes() > 1 ? " +" : "");
}""")
M(rkit, r"""
public static String customGet(String key) {
  if (key == null || !key.startsWith("region[") || !key.endsWith("]")) return "";
  @PKG@.ZRegion r = find(key.substring(7, key.length() - 1));
  if (r == null) return null;
  String t = r.modeName() + "; priority " + r.priority + "; types " + (r.types.length == 0 ? "none" : @PKG@.ZRegion.join(r.types))
    + "; flags " + (r.flags.length() == 0 ? "none" : r.flags) + "; title " + (r.title.length() == 0 ? "none" : r.title) + "; world " + r.world + "; " + boxCell(r);
  return t.length() > 200 ? t.substring(0, 197) + "..." : t;
}""")
# fixer 2 (critic 3 #2, PROJECT-RULES 4 "editable in game"): mode / priority / types / flags / title change here (all or nothing, one
# history copy + change-log line, through ZStore like the commands); world + boxes, adding and removing a region stay commands (corners).
M(rkit, r"""
public static Object[] no(String m) {
  return new Object[] { "bad", "", m };
}""")
M(rkit, r"""
public static Object[] customSet(String key, String value) {
  if (key == null || !key.startsWith("region[") || !key.endsWith("]")) return no("Unknown regions line.");
  String id = key.substring(7, key.length() - 1);
  if (value == null) return no("Delete a region by command: /zones region delete " + id + ".");
  @PKG@.ZRegion r = @PKG@.ZStore.get(id);
  if (r == null) return no("A new region needs wand corners: /zones wand, then /zones region create " + id + " <full or skyblock>.");
  if (value.indexOf("...") >= 0) return no("This region's line is too long to edit here - use /zones region <mode, priority, types, flags or title> " + id + " <value>.");
  String[] parts = value.split(";");
  java.util.ArrayList fs = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  for (int i = 0; i < parts.length; i++) {
    String p = parts[i].trim();
    if (p.length() == 0) continue;
    int sp = p.indexOf(' ');
    String w = (sp < 0 ? p : p.substring(0, sp)).toLowerCase();
    String rest = sp < 0 ? "" : p.substring(sp + 1).trim();
    if (sp < 0 && @PKG@.ZRegion.modeOf(w) >= 0) { fs.add("mode"); vs.add(w); continue; }
    if (w.equals("mode") || w.equals("priority") || w.equals("types") || w.equals("flags") || w.equals("title")) { fs.add(w); vs.add(rest); continue; }
    if (w.equals("world")) { if (!rest.equals(r.world)) return no("A region's world can't change here (" + r.world + ")."); continue; }
    if (Character.isDigit(w.charAt(0))) { if (!p.equals(boxCell(r))) return no("Boxes change by command: /zones wand, then /zones region addbox " + id + "."); continue; }
    return no("Unknown part '" + p + "'. Parts: full or skyblock; priority N; types a,b; flags containers,furnaces; title Text (none clears).");
  }
  if (fs.isEmpty()) return no("Nothing to change.");
  String m = @PKG@.ZStore.setMany(id, (String[]) fs.toArray(new String[fs.size()]), (String[]) vs.toArray(new String[vs.size()]), "Server Setup");
  if (m.startsWith("!")) return no(m.substring(1));
  return new Object[] { "ok", customGet(key), m };
}""")

# =====================================================================================================================================
# the admin config kit (tools/CONFIG-CONTRACT.md): Server Setup -> Zones
# =====================================================================================================================================
CATS = [("zones", "Protection"), ("regions", "Regions"), ("titles", "Area titles"), ("tools", "Builder tools"), ("types", "Resource types")]
ROWS = [
    ("zones.on", "Zone protection (whole mod)", "zones", "bool", "true", "", "", "", "", "live,danger,part",
     "Off: no world or region is protected (nothing else changes). Regions stay saved.",
     "field:ZCfg.ON@config.properties:zones.on"),
    ("zones.worlds", "Protected worlds (whole world)", "zones", "text", "", "", "400", "", "", "live",
     "World folder names, comma list: protected everywhere. A region protects its boxes in any world.",
     "field:ZCfg.WORLDS@config.properties:zones.worlds;check=ZCfg.checkWorlds"),
    ("zones.opBypass", "Admins always bypass", "zones", "bool", "false", "", "", "", "", "live",
     "On: skyyzones.admin is never stopped. Off (default): admins use /zones build on like builders.",
     "field:ZCfg.OP_BYPASS@config.properties:zones.opBypass"),
    ("zones.blockMobs", "Mobs can't break blocks here", "zones", "bool", "true", "", "", "", "", "live",
     "Mobs (any non-player) can't break or place blocks in a protected spot.",
     "field:ZCfg.MOBS@config.properties:zones.blockMobs"),
    ("msg.gapSec", "Seconds between refusal notes", "zones", "int", "2", "0", "30", "", "s", "live",
     "One player gets 'This area is protected.' at most this often.", "field:ZCfg.MSG_GAP@config.properties:msg.gapSec"),
    ("use.tools", "Tools that change blocks", "zones", "text", USE_TOOLS, "", "600", "", "", "live,adv",
     "Holding one, using a block here is refused. Hoe tilling + buckets have no event in Hytale 0.7.",
     "field:ZCfg.TOOLS@config.properties:use.tools;check=ZCfg.checkTools"),
    ("titles.on", "Area titles", "titles", "bool", "true", "", "", "", "", "live",
     "Walking into a region with a title shows it (vanilla event title).", "field:ZCfg.TITLES@config.properties:titles.on"),
    ("titles.leave", "Note when you leave", "titles", "bool", "true", "", "", "", "", "live",
     "Walking out of a titled region shows a small 'You left ...' note.", "field:ZCfg.LEAVE@config.properties:titles.leave"),
    ("titles.gapSec", "Same title again after", "titles", "int", "10", "0", "600", "", "s", "live",
     "A region's title waits this long before it shows again for the same player.",
     "field:ZCfg.TITLE_GAP@config.properties:titles.gapSec"),
    ("show.seconds", "Outline time (/zones show)", "tools", "int", "30", "5", "300", "", "s", "live",
     "How long /zones show draws region outlines (to you only).", "field:ZCfg.SHOW_SECS@config.properties:show.seconds"),
    ("show.particle", "Outline particle", "tools", "text", "Alerted", "", "80", "", "", "live,adv",
     "A SHORT-LIVED vanilla particle system id (a looping one stays on screen).",
     "field:ZCfg.PARTICLE@config.properties:show.particle;check=ZCfg.checkParticle"),
    ("build.remindSec", "Build mode reminder", "tools", "int", "300", "0", "3600", "", "s", "live",
     "While builder mode is on, a reminder note this often (0 = none).", "field:ZCfg.REMIND@config.properties:build.remindSec"),
    ("reload.files", "Re-read regions + types files", "tools", "action", "", "", "", "Re-read files", "", "live",
     "Applies hand edits of regions.properties and types.properties (same as /zones reload).",
     "action:ZCfg.reloadAction"),
    ("region", "Regions", "regions", "table", "", "", "200", "text;none;Mode / priority / types / flags / title / world / boxes", "", "live",
     "Edit mode, priority, types, flags, title here. Tie: skyblock wins. New / boxes: /zones wand.",
     "custom:ZRegKit@config.properties"),
    ("type", "Resource types (types.properties)", "types", "table", "", "", "200", "text;none;Block ids", "", "live",
     "type id = block ids a SKYBLOCK region can let players break (comma list, * = any text).",
     "reload:ZCfg.reloadTypes@types.properties:type.;check=ZCfg.checkType"),
]
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Zones", VERSION=VERSION, NODE=ADMIN, CATS=CATS, ROWS=ROWS,
               FILES=["Skyy_SkyyZones/config.properties", "Skyy_SkyyZones/types.properties"],
               NOTE="Not stoppable in Hytale 0.7: fire, sourceless blasts, fluids, hoes, buckets. Keep lava + TNT out.",
               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT, "types.properties": TYPES_TEXT},
               PERM_FN="ZCfg.permTest")

# =====================================================================================================================================
# ZCmds: the command logic (world thread)
# =====================================================================================================================================
cmds = mk("ZCmds")
F(cmds, "public static final String ADMIN = \"@ADMIN@\";")
M(cmds, "public static boolean admin(@PR@ pr) { return pr != null && @PKG@.ZCfg.permTest(pr.getUuid(), ADMIN); }")
M(cmds, "public static void ok(@PR@ pr, String t) { @PKG@.ZMsg.tell(pr, t, \"@GOOD@\"); }")
M(cmds, "public static void bad(@PR@ pr, String t) { @PKG@.ZMsg.tell(pr, t, \"@BAD@\"); }")
M(cmds, "public static void say(@PR@ pr, String t) { @PKG@.ZMsg.tell(pr, t, \"@INFO@\"); }")
M(cmds, r"""
public static void result(@PR@ pr, String m) {
  if (m == null) return;
  if (m.startsWith("!")) bad(pr, m.substring(1)); else ok(pr, m);
}""")
M(cmds, r"""
public static void help(@PR@ pr) {
  say(pr, "SkyyZones - protected worlds and areas:");
  say(pr, "/zones info - what protects the block you look at   /zones list - the regions of this world");
  say(pr, "/zones show [region or off] [seconds] (or /zones show <seconds>) - outline the regions near you   /zones build on|off - builder mode (break + place anywhere)");
  if (!admin(pr)) return;
  say(pr, "/zones wand - the Zone Wand: hit two blocks = the corners of a box (or use the vanilla selection tool)");
  say(pr, "/zones region create <name> <full or skyblock> [types]   /zones region addbox <name>   /zones region delete <name>");
  say(pr, "/zones region mode|priority|title|types|flags <name> <value>   (title: _ = space; types: stone,copper; flags: containers,furnaces; none clears)");
  say(pr, "Overlap: the higher priority wins; on a tie a skyblock region wins, then the name first in a-z.");
  say(pr, "/zones type <type> <block ids, none, or look>   /zones type add <type> <block ids or look> (adds)   /zones protect on|off (this whole world)");
  say(pr, "/zones reload (re-read the files)   /zones reload clear (accept a regions file with no region: removes every region)");
}""")
M(cmds, r"""
public static void build(@PR@ pr, String v) {
  java.util.UUID u = pr.getUuid();
  boolean now = @PKG@.ZBuild.on(u);
  boolean want;
  if (v.equals("on")) want = true;
  else if (v.equals("off")) want = false;
  else if (v.equals("toggle")) want = !now;
  else { bad(pr, "Use /zones build on or /zones build off."); return; }
  if (want == now) { say(pr, "Builder mode is already " + (now ? "ON." : "off.")); return; }
  @PKG@.ZBuild.set(u, pr.getUsername(), want);
  if (want) {
    ok(pr, "Builder mode ON - protected areas do not stop you (break, place, chests). It switches off when you log out: /zones build off");
    @PKG@.ZEng.title(pr, "BUILD MODE", "Protection is off for you - /zones build off");
  } else ok(pr, "Builder mode off - protection applies to you again.");
}""")
M(cmds, r"""
public static void list(@PR@ pr, String wn) {
  @PKG@.ZRegion[] a = @PKG@.ZStore.INDEX.in(wn);
  say(pr, "World " + wn + ": " + (@PKG@.ZCfg.protectedWorld(wn) ? "protected everywhere (zones.worlds)" : "protected only inside regions") + (@PKG@.ZCfg.ON ? "" : " - ZONE PROTECTION IS OFF (Server Setup)") + "; " + a.length + (a.length == 1 ? " region" : " regions") + ":");
  for (int i = 0; i < a.length && i < 20; i++) say(pr, " " + a[i].summary());
  if (a.length > 20) say(pr, " ... and " + (a.length - 20) + " more (Skyy_SkyyZones/regions.properties).");
  String b = @PKG@.ZStore.BAD;
  if (b != null) bad(pr, "Regions file problem: " + b + " - edits are blocked until it is fixed + /zones reload.");
}""")
M(cmds, r"""
public static void show(@PR@ pr, String wn, String id, int secs) {
  java.util.UUID u = pr.getUuid();
  if (id.equals("off")) { @PKG@.ZTick.SHOW.remove(u); ok(pr, "Outline off."); return; }
  if (id.length() > 0) {
    @PKG@.ZRegion r = @PKG@.ZStore.get(id);
    if (r == null || !r.world.equals(wn)) { bad(pr, "No region " + id + " in this world (/zones list)."); return; }
  } else if (@PKG@.ZStore.INDEX.in(wn).length == 0) { bad(pr, "This world has no regions."); return; }
  @PKG@.ZTick.SHOW.put(u, new @PKG@.ZShow(wn, id, System.currentTimeMillis() + 1000L * (long) secs));
  ok(pr, "Outlining " + (id.length() > 0 ? "region " + id : "the regions within 64 blocks") + " for " + secs + " s (only you see it). /zones show off");
}""")
M(cmds, r"""
public static void info(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w) {
  String wn = w.getName();
  int[] p = @PKG@.ZEng.target(ref, st);
  boolean look = p != null;
  if (p == null) {
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) { bad(pr, "Could not tell where you are."); return; }
    @V3D@ v = tc.getPosition();
    p = new int[] { (int) Math.floor(v.x), (int) Math.floor(v.y) - 1, (int) Math.floor(v.z) };
  }
  String blk = @PKG@.ZEng.blockAt(w, p[0], p[1], p[2]);
  String id = blk == null ? "" : @PKG@.ZRules.bare(blk);
  boolean pw = @PKG@.ZCfg.protectedWorld(wn);
  @PKG@.ZIndex ix = @PKG@.ZStore.INDEX;
  say(pr, "Zones info - " + (look ? "the block you look at" : "the block under you") + ": " + (blk == null ? "(not loaded)" : blk) + " at " + p[0] + " " + p[1] + " " + p[2] + " in " + wn);
  say(pr, "World: " + (pw ? "protected everywhere (zones.worlds)" : "protected only inside regions") + (@PKG@.ZCfg.ON ? "" : " - ZONE PROTECTION IS OFF"));
  java.util.ArrayList at = ix.at(wn, p[0], p[1], p[2]);
  if (at.isEmpty()) say(pr, "Regions here: none");
  for (int i = 0; i < at.size(); i++) {
    @PKG@.ZRegion r = (@PKG@.ZRegion) at.get(i);
    String lt = r.mode == 1 ? @PKG@.ZRules.listedType(r, id) : null;
    say(pr, (i == 0 ? "Region here (wins): " : "Also here: ") + r.summary() + (lt != null ? " - this block is type " + lt : ""));
  }
  if (@PKG@.ZCfg.ON) {
    say(pr, "Break: " + @PKG@.ZRules.verdict(@PKG@.ZRules.decide(ix, wn, pw, p[0], p[1], p[2], @PKG@.ZRules.BREAK, id))
      + " | Place: " + @PKG@.ZRules.verdict(@PKG@.ZRules.decide(ix, wn, pw, p[0], p[1], p[2], @PKG@.ZRules.PLACE, id))
      + " | Chests: " + @PKG@.ZRules.verdict(@PKG@.ZRules.decide(ix, wn, pw, p[0], p[1], p[2], @PKG@.ZRules.CONTAINER, id)));
  }
  long gf = @PKG@.ZGuard.FAILS.get();
  if (gf > 0L) bad(pr, "Guard errors since start: " + gf + " (those actions were refused in protected spots - see the server log).");
  boolean bm = @PKG@.ZBuild.on(pr.getUuid());
  say(pr, "You: builder mode " + (bm ? "ON (nothing stops you)" : "off") + (@PKG@.ZCfg.OP_BYPASS && admin(pr) ? "; admins always bypass (Server Setup)" : ""));
}""")
M(cmds, r"""
public static void wand(@REF@ ref, @ST@ st, @PR@ pr) {
  int g = @PKG@.ZEng.give(ref, st, @PKG@.ZWand.ID);
  if (g == 0) ok(pr, "A Zone Wand is in your inventory. Hit two blocks (the opposite corners of a box), then /zones region create <name> <full or skyblock>. The wand never breaks anything.");
  else if (g == 1) say(pr, "You already have a Zone Wand.");
  else if (g == 2) bad(pr, "No room for the Zone Wand - free a slot and try again.");
  else bad(pr, "Could not give the Zone Wand - the server log has the details.");
}""")
M(cmds, r"""
public static void protect(@PR@ pr, String wn, String v) {
  String[] cur = @PKG@.ZCfg.splitList(@PKG@.ZCfg.WORLDS);
  StringBuilder sb = new StringBuilder();
  boolean had = false;
  for (int i = 0; i < cur.length; i++) {
    if (cur[i].equalsIgnoreCase(wn)) { had = true; continue; }
    if (sb.length() > 0) sb.append(',');
    sb.append(cur[i]);
  }
  boolean on;
  if (v.equals("on")) on = true; else if (v.equals("off")) on = false; else { bad(pr, "Use /zones protect on or /zones protect off."); return; }
  if (on == had) { say(pr, "World " + wn + " is already " + (had ? "protected everywhere." : "not protected outside regions.")); return; }
  if (on) { if (sb.length() > 0) sb.append(','); sb.append(wn); }
  String m = @PKG@.CfgFn.cmdSet("zones.worlds", sb.toString(), pr.getUuid(), pr.getUsername());
  say(pr, m);
  if (on) say(pr, "World " + wn + " is now protected everywhere: outside regions nothing breaks or is placed (builders: /zones build on).");
}""")
M(cmds, r"""
public static String look(@REF@ ref, @ST@ st, @WLD@ w, String t) {
  int[] p = @PKG@.ZEng.target(ref, st);
  if (p == null) return null;
  String blk = @PKG@.ZEng.blockAt(w, p[0], p[1], p[2]);
  if (blk == null) return null;
  String id = @PKG@.ZRules.bare(blk);
  if (id.length() == 0 || id.equals("Empty")) return null;
  Object o = @PKG@.ZCfg.TYPES.get(t);
  String[] cur = o instanceof String[] ? (String[]) o : new String[0];
  if (@PKG@.ZRules.anyGlob(cur, id)) return "=" + id;
  return cur.length == 0 ? id : @PKG@.ZRegion.join(cur) + "," + id;
}""")
M(cmds, r"""
public static void type(@REF@ ref, @ST@ st, @WLD@ w, @PR@ pr, String id, String v0) {
  String t = id.toLowerCase();
  String v = v0;
  if (v.equalsIgnoreCase("look")) {
    v = look(ref, st, w, t);
    if (v == null) { bad(pr, "Look at a block (within 16 blocks) to add it to type " + t + "."); return; }
    if (v.startsWith("=")) { say(pr, "Type " + t + " already covers " + v.substring(1) + "."); return; }
  }
  Object[] r;
  if (v.equalsIgnoreCase("none")) r = (Object[]) new @PKG@.CfgFn().apply(new Object[] { "remove", "type", t, pr.getUuid(), pr.getUsername(), "yes", "command" });
  else if (@PKG@.ZCfg.TYPES.containsKey(t)) r = (Object[]) new @PKG@.CfgFn().apply(new Object[] { "tset", "type", t, v, pr.getUuid(), pr.getUsername(), "yes", "command" });
  else r = (Object[]) new @PKG@.CfgFn().apply(new Object[] { "add", "type", t, v, pr.getUuid(), pr.getUsername(), "yes", "command" });
  if (r == null || r.length < 3) { bad(pr, "Could not change the type (see the server log)."); return; }
  String st = String.valueOf(r[0]);
  if (st.equals("ok") || st.equals("restart")) ok(pr, String.valueOf(r[2]) + " (types.properties is re-read in a moment)");
  else bad(pr, String.valueOf(r[2]));
}""")
# spec 5.1 form /zones type add <type> <ids|look>: ADDS to the type (the 3-word /zones type <type> <ids> replaces it)
M(cmds, r"""
public static void typeAdd(@REF@ ref, @ST@ st, @WLD@ w, @PR@ pr, String id, String v) {
  String t = id.toLowerCase();
  if (v.equalsIgnoreCase("look")) { type(ref, st, w, pr, t, "look"); return; }
  if (v.equalsIgnoreCase("none")) { bad(pr, "Use /zones type " + t + " none to remove a type."); return; }
  Object o = @PKG@.ZCfg.TYPES.get(t);
  String[] cur = o instanceof String[] ? (String[]) o : new String[0];
  String[] add = @PKG@.ZCfg.splitList(v);
  java.util.ArrayList all = new java.util.ArrayList(java.util.Arrays.asList(cur));
  for (int i = 0; i < add.length; i++) { if (!all.contains(add[i])) all.add(add[i]); }
  if (all.size() == cur.length) { say(pr, "Type " + t + " already lists " + v + "."); return; }
  type(ref, st, w, pr, t, @PKG@.ZRegion.join((String[]) all.toArray(new String[all.size()])));
}""")
M(cmds, r"""
public static void region(@REF@ ref, @ST@ st, @PR@ pr, String wn, String[] a) {
  String sub = a[1].toLowerCase();
  String id = a[2].toLowerCase();
  String who = pr.getUsername();
  if (a.length == 3 && sub.equals("delete")) { result(pr, @PKG@.ZStore.delete(id, who)); return; }
  if (a.length == 5 && sub.equals("create")) {
    String[] ty = @PKG@.ZCfg.splitList(a[4].toLowerCase());
    for (int i = 0; i < ty.length; i++) if (!@PKG@.ZCfg.TYPES.containsKey(ty[i])) { bad(pr, "No resource type '" + ty[i] + "'. Types: " + @PKG@.ZStore.typeList() + ". Nothing was created."); return; }
  }
  if ((a.length == 4 || a.length == 5) && sub.equals("create") || a.length == 3 && sub.equals("addbox")) {
    int[] b = @PKG@.ZWand.box(pr.getUuid(), wn);
    boolean viaSel = false;
    if (b == null) { b = @PKG@.ZEng.selection(ref, st, pr); viaSel = b != null; }
    if (b == null) { bad(pr, "Mark a box first: /zones wand and hit two corner blocks (or select with the vanilla selection tool)."); return; }
    String m = sub.equals("create") ? @PKG@.ZStore.create(id, wn, a[3], b, who) : @PKG@.ZStore.addBox(id, wn, b, who);
    result(pr, m);
    if (a.length == 5 && m != null && !m.startsWith("!")) result(pr, @PKG@.ZStore.set(id, "types", a[4], who));
    if (viaSel && m != null && !m.startsWith("!")) say(pr, "(Corners from the vanilla selection tool: " + @PKG@.ZRegion.boxText(b) + " in " + wn + " - /zones show " + id + " to check it.)");
    return;
  }
  if (a.length == 4 && (sub.equals("mode") || sub.equals("priority") || sub.equals("title") || sub.equals("types") || sub.equals("flags"))) {
    result(pr, @PKG@.ZStore.set(id, sub, a[3], who));
    return;
  }
  bad(pr, "Use /zones region create <name> <full or skyblock> [types], addbox <name>, delete <name>, or mode|priority|title|types|flags <name> <value>.");
}""")
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String[] a) {
  try {
    if (pr == null || w == null) return;
    if (a == null || a.length == 0) { help(pr); return; }
    String c = a[0].toLowerCase();
    String wn = w.getName();
    if (c.equals("help")) { help(pr); return; }
    if (c.equals("info") && a.length == 1) { info(ref, st, pr, w); return; }
    if (c.equals("list") && a.length == 1) { list(pr, wn); return; }
    if (c.equals("show") && a.length == 2 && a[1].matches("[0-9]{1,6}")) { show(pr, wn, "", @PKG@.ZCfg.intOf(a[1], @PKG@.ZCfg.SHOW_SECS, 5, 300)); return; }
    if (c.equals("show") && a.length <= 3) { show(pr, wn, a.length > 1 ? a[1].toLowerCase() : "", a.length > 2 ? @PKG@.ZCfg.intOf(a[2], @PKG@.ZCfg.SHOW_SECS, 5, 300) : @PKG@.ZCfg.SHOW_SECS); return; }
    if (c.equals("build") && a.length <= 2) { build(pr, a.length > 1 ? a[1].toLowerCase() : "toggle"); return; }
    if (!c.equals("wand") && !c.equals("reload") && !c.equals("protect") && !c.equals("type") && !c.equals("region")) { help(pr); return; }
    if (!admin(pr)) { bad(pr, "Only zone admins (skyyzones.admin) can use /zones " + c + "."); return; }
    if (c.equals("wand") && a.length == 1) { wand(ref, st, pr); return; }
    if (c.equals("reload") && a.length == 1) { say(pr, @PKG@.ZCfg.reloadFiles(false)); return; }
    if (c.equals("reload") && a.length == 2 && a[1].equalsIgnoreCase("clear")) { say(pr, @PKG@.ZCfg.reloadFiles(true)); return; }
    if (c.equals("protect") && a.length == 2) { protect(pr, wn, a[1].toLowerCase()); return; }
    if (c.equals("type") && a.length == 3) { type(ref, st, w, pr, a[1], a[2]); return; }
    if (c.equals("type") && a.length == 4 && a[1].equalsIgnoreCase("add")) { typeAdd(ref, st, w, pr, a[2], a[3]); return; }
    if (c.equals("region") && a.length >= 3) { region(ref, st, pr, wn, a); return; }
    help(pr);
  } catch (Throwable t) {
    @PKG@.ZCfg.warn("/zones failed: " + t);
    bad(pr, "Something went wrong - the server log has the details.");
  }
}""")

# =====================================================================================================================================
# the command: /zones (+ usage variants for 1, 2, 3, 4 and 5 words - HANDOFF COMMAND RULES 2); skyyzones.build, never a player group
# =====================================================================================================================================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# skyyzones.admin alone opens /zones too (the engine checks only the one requirePermission node; Server Setup admins are not refused)
HASP = r"""
public boolean hasPermission(com.hypixel.hytale.server.core.command.system.CommandSender s) {
  if (s == null) return false;
  try { if (s.hasPermission("@ADMIN@")) return true; } catch (Throwable t) { }
  return super.hasPermission(s);
}"""
VARIANTS = [("ZCmd1", ["word"], "(builders) /zones info, list, show, build, help; (admins) wand, reload"),
            ("ZCmd2", ["word", "value"], "(builders) /zones show <region, off or seconds>, /zones build <on or off>; (admins) /zones protect <on or off>, /zones reload clear"),
            ("ZCmd3", ["word", "name", "value"], "(builders) /zones show <region> <seconds>; (admins) /zones region <delete or addbox> <name>, /zones type <type> <block ids, none or look>"),
            ("ZCmd4", ["word", "what", "name", "value"], "(admins) /zones region <create, mode, priority, title, types, flags> <name> <value>, /zones type add <type> <ids or look>"),
            ("ZCmd5", ["word", "what", "name", "value", "types"], "(admins) /zones region create <name> <full or skyblock> <types, e.g. stone,copper>")]
ARG_HELP = {"word": "info, list, show, build, help, wand, reload, protect, type or region", "value": "a value (on, off, a region name ...)",
            "name": "a region or type name", "what": "create, delete, addbox, mode, priority, title, types or flags",
            "types": "resource types, comma list (stone,copper)"}
vcls = []
for vname, args, desc in VARIANTS:
    vc = mk(vname, T["APC"])
    for i in range(len(args)):
        F(vc, "public @RA@ a%d;" % i)
    body = "\n".join('  this.a%d = withRequiredArg("%s", %s, @ATY@.STRING);' % (i, args[i] + str(i), jl(ARG_HELP[args[i]])) for i in range(len(args)))
    C(vc, r"""
public %s() {
  super(%s);
  requirePermission("@BUILDN@");
  setPermissionGroups(new String[0]);
%s
}""" % (vname, jl(desc), body))
    M(vc, HASP)
    get = " ".join("String s%d = String.valueOf(ctx.get(this.a%d));" % (i, i) for i in range(len(args)))
    arr = ", ".join("s%d" % i for i in range(len(args)))
    M(vc, EXEC + r""" {
  try {
    %s
    @PKG@.ZCmds.run(ref, store, pr, world, new String[] { %s });
  } catch (Throwable t) { @PKG@.ZCmds.help(pr); }
}""" % (get, arr))
    vcls.append(vc)
cmd = mk("ZCmd", T["APC"])
C(cmd, r"""
public ZCmd() {
  super("zones", "(builders + admins) SkyyZones protected areas: /zones lists what you can use");
  requirePermission("@BUILDN@");
  setPermissionGroups(new String[0]);
  addUsageVariant(new @PKG@.ZCmd1());
  addUsageVariant(new @PKG@.ZCmd2());
  addUsageVariant(new @PKG@.ZCmd3());
  addUsageVariant(new @PKG@.ZCmd4());
  addUsageVariant(new @PKG@.ZCmd5());
}""")
M(cmd, EXEC + r""" {
  @PKG@.ZCmds.run(ref, store, pr, world, new String[0]);
}""")
M(cmd, HASP)

# =====================================================================================================================================
# ZQuit: logout = builder mode off, corners / titles / outline forgotten
# =====================================================================================================================================
quit_ = mk("ZQuit", None, ("java.util.function.Consumer",))
C(quit_, "public ZQuit() { }")
M(quit_, r"""
public static void forget(java.util.UUID u, String name) {
  if (u == null) return;
  if (@PKG@.ZBuild.on(u)) @PKG@.ZBuild.set(u, name, false);
  @PKG@.ZWand.SEL.remove(u);
  @PKG@.ZMsg.LAST.remove(u);
  @PKG@.ZTick.forget(u);
}""")
M(quit_, r"""
public void accept(Object o) {
  try {
    if (!(o instanceof @PDE@)) return;
    @PR@ pr = ((@PDE@) o).getPlayerRef();
    if (pr != null) forget(pr.getUuid(), pr.getUsername());
  } catch (Throwable t) { @PKG@.ZCfg.warnOnce("quit", "logout clean-up failed (logged once): " + t); }
}""")

# =====================================================================================================================================
# the plugin
# =====================================================================================================================================
pl = mk("SkyyZonesPlugin", T["JP"])
C(pl, "public SkyyZonesPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public static String paths(java.nio.file.Path dir) {
  @PKG@.ZCfg.DIR = dir;
  @PKG@.ZCfg.FILE = dir.resolve("config.properties");
  @PKG@.ZCfg.TFILE = dir.resolve("types.properties");
  @PKG@.ZStore.FILE = dir.resolve("regions.properties");
  @PKG@.ZSave.FILE = dir.resolve("regions.properties");
  @PKG@.ZSave.HIST = dir.resolve("history");
  @PKG@.ZSave.LOGF = dir.resolve("region-changes.log");
  return @PKG@.ZCfg.loadCfg(true) + "; " + @PKG@.ZCfg.loadTypes(true) + "; " + @PKG@.ZStore.start();
}""")
M(pl, r"""
public void setup() {
  try {
    @PKG@.ZCfg.LOG = getLogger();
    java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyZones");
    String s = paths(dir);
    try { @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger()); } catch (Throwable t) { @PKG@.ZCfg.warn("Server Setup kit did not start: " + t); }
    getCommandRegistry().registerCommand(new @PKG@.ZCmd());
    getEntityStoreRegistry().registerSystem(new @PKG@.ZGuardBreak());
    getEntityStoreRegistry().registerSystem(new @PKG@.ZGuardDamage());
    getEntityStoreRegistry().registerSystem(new @PKG@.ZGuardPlace());
    getEntityStoreRegistry().registerSystem(new @PKG@.ZGuardUse());
    getEntityStoreRegistry().registerSystem(new @PKG@.ZTick());
    getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.ZQuit());
    @PKG@.ZFn.publish();
    getLogger().at(java.util.logging.Level.INFO).log("[SkyyZones] @VERSION@ ready - protected worlds + regions (FULL / SKYBLOCK, Z1: no regrow yet); " + s + (@PKG@.ZStore.BAD != null ? " - REGIONS FILE PROBLEM, region edits blocked (see the warnings above)" : "") + "; /zones (builders: skyyzones.build, admins: skyyzones.admin); Server Setup -> Zones; data in " + dir);
  } catch (Throwable t) {
    try { getLogger().at(java.util.logging.Level.SEVERE).log("[SkyyZones] setup failed - zone protection is NOT active: " + t); } catch (Throwable t2) { }
  }
}""")
M(pl, r"""
protected void shutdown() {
  try { @PKG@.ZFn.unpublish(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.ZStore.flush(); } catch (Throwable t) { }
  try { @PKG@.ZBuild.clearAll(); } catch (Throwable t) { }
  @PKG@.ZWand.SEL.clear();
  @PKG@.ZMsg.LAST.clear();
  @PKG@.ZTick.ACC.clear();
  @PKG@.ZTick.CUR.clear();
  @PKG@.ZTick.SHOW.clear();
  @PKG@.ZTick.SHOWN.clear();
  super.shutdown();
}""")

ALL = [api, cfg, reg, idx, rules, sav, sto, eng, msg, bld, sel, wnd, guard] + gcls + [shw, tick, fn, rkit, cmds] + vcls + [cmd, quit_, pl]
for c in ALL:
    c.writeFile(OUT)
kit.write(OUT)
print("classes written: %d (+%d kit)" % (len(ALL), len(kit.classes)))

# =====================================================================================================================================
# assets: the Zone Wand item (a vanilla stick look by path - nothing vanilla is copied) + its name
# =====================================================================================================================================
WAND_ITEM = {
    "TranslationProperties": {"Name": "server.items.%s.name" % WAND, "Description": "server.items.%s.description" % WAND},
    "Icon": "Icons/ItemsGenerated/Ingredient_Stick.png", "Categories": ["Items.Utility"], "MaxStack": 1, "Quality": "Tool",
    "PlayerAnimationsId": "Item", "Model": "Items/Ingredients/Stick.blockymodel", "Texture": "Items/Ingredients/Stick_Texture.png",
    "IconProperties": {"Scale": 1.21, "Rotation": [67, 330, 0], "Translation": [1.3, -1]},
    "ItemSoundSetId": "ISS_Items_Foliage", "DropOnDeath": False,
}
# Style Guide section 15 colours: actions yellow, what it does soft white, minor info dim grey (no < > inside the text: markup)
_Y, _W, _D = "#ffcc00", "#d6e4ee", "#7f93a6"
WAND_DESC = ('<color is="%s">Hit a block:</color> <color is="%s">corner A, then corner B of a zone box</color>\\n'
             '<color is="%s">Then:</color> <color is="%s">/zones region create NAME full (or skyblock)</color>\\n'
             '<color is="%s">Admin tool (SkyyZones). It never breaks anything.</color>') % (_Y, _W, _Y, _W, _D)
LANG = []
for _pre in ("", "server."):
    LANG += ["%sitems.%s.name=Zone Wand" % (_pre, WAND),
             "%sitems.%s.description=%s" % (_pre, WAND, WAND_DESC)]
FILES = {"Server/Item/Items/SkyyZones/%s.json" % WAND: json.dumps(WAND_ITEM, indent=2),
         "Server/Languages/en-US/server.lang": "\n".join(LANG) + "\n"}
jar = os.path.join(HERE, "%s-%s.jar" % (MOD, VERSION))
man = B.manifest(MOD, VERSION, "SkyWynn zone protection: protected worlds and regions for the server's hand-built zones. FULL areas (nothing breaks or is placed, no drops) and SKYBLOCK areas (only the listed resource blocks break - regrowing comes in a later version); deny by default; builder mode (/zones build on, off at login); regions drawn with the Zone Wand or the vanilla selection; area titles; overlap priority; Server Setup -> Zones. Player islands and the solo pack stay unprotected unless a region is drawn. Zero dependencies.", PKG + ".SkyyZonesPlugin")
man["IncludesAssetPack"] = True
B.assemble(jar, man, OUT, extra_files=FILES)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyZones must not ship .ui files: %s" % _bad)
if "--deploy" in sys.argv:
    raise SystemExit("SkyyZones: --deploy is not supported here - deploys go through tools/deploy_set.py")
