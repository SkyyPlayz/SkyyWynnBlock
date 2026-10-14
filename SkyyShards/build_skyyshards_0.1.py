"""SkyyShards 0.1 - build script (javassist via jpype). A NEW mod: Gathering-Shards-Spec phase 5 (research/Gathering-Shards-Spec.md
sections 9, 10, 12, 15; docs/answered/skills.md 2026-10-11 SHARD ISLANDS / SHARDS 2 / SHARDS 3 + gear.md 2026-10-13 G7-G11 + skills.md
2026-10-13 SHARD SOURCES - they win over every older doc; the shard menu = research/cloud/shard-menu-1013/Shard-Menu-Spec.md, built on
the vanilla kit tools/skyyui.py because the Sky Window kit is not in the kit yet).
Run:   python SkyyShards/build_skyyshards_0.1.py   -> SkyyShards/SkyyShards-0.1.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.1.py   (bare JVM, -Xverify:all, every new code path executed)

SKYY'S WORDS (word for word in docs/answered): "we could make the shards mini islands you only accses from the shard placed on your island
(like a portal there.) the farming shard starts with 1 wheat island that is pretty small and a single T1 harvest spirit totem. (farm is
bigger than the spirits range so you can go in there and manually farm too" / "collections and xp are gained when you collect from the
shard" / "fixed slots, but i want the shar menu in the portal on your main island too" / "each shard has a max storage that needs
upgraded in the shard too" / popups G7 "One private world per profile", G8 "You + co-op members", G9 "50% XP, full collections",
G11 "Hub quest line" / "all T1 shards come from quests". Existing mods checked (spec section 2): nothing does instanced per-player
resource islands - we build our own.

ENGINE PROBES (run first, tools/dev/scratch/shards01/probe, a scratch server through tools/smoke_test.py; the probe jar never ships):
  S1 40 void shard worlds made from our own instance template (InstancesPlugin.spawnInstance): 631 ms for all 40 (15 ms each), 13,640
     blocks written through BlockOperations.setBlock in 2 s, every world ticking at the full 30 TPS while loaded; heap grew ~1.5 GB for 40
     loaded worlds (the probe's own estimate ~40 MB a world, noisy) -> shard.maxLoaded defaults to 20 and the idle unload to 120 s;
     removeWorld x40 = 3 s, every folder kept, isWorldLoadable stays true.
  S2 a removed world's folder stays; Universe.addWorld(name) on that folder THROWS "already exists on disk" on 0.7 -> SkyyShards reopens
     a saved shard world with Universe.loadWorld(name) (probe 2 reads the blocks back); new worlds are spawnInstance("SkyyShard", ...).
     The engine also loads EVERY world folder at server start, so the idle check unloads shard worlds 120 s after a restart.
  S3 desk: Interaction.CODEC is an AssetCodecMapCodec and PluginBase.getCodecRegistry(AssetCodecMapCodec) exists, so a mod could add an
     interaction type - not used in 0.1 (Enter is a menu button; step-on pads come with the totem round).
  S4 server side: a block item with the vanilla Platform_MagicInactive model + an OpenCustomUI Use interaction validates (only the
     missing server.lang name failed in probe 1 - shipped here) and BlockOperations.setBlock places it. That it DRAWS and OPENS on a
     client is UNVERIFIED (needs the game).

WHAT 0.1 IS (Server Setup -> Shards; shards.on defaults ON for the test world):
  - The FARMING SHARD item Skyy_Shard_Farming (a portal pad: the vanilla Platform_MagicInactive model, its texture recoloured gold at
    BUILD time - vanilla-derived, never committed; the icon is our own cloud art). Placed on your OWN island (the island owner's
    profile - PlaceBlockEvent, checked against SkyyIslands island:owner:fn; anywhere else = refused) it becomes your shard portal.
    Unbreakable; right-click = the shard menu (OpenCustomUI). One per profile; "Pick up Shard" in the menu (2 clicks) gives it back.
    The quest that hands it out is SkyyQuests' (G11); until then /shardadmin give <player> gives one.
  - ONE private SHARD WORLD per profile (skyy-shard-<pkey>, a Void instance template "SkyyShard"), made on the first Enter, reopened
    with Universe.loadWorld, unloaded by our own idle check after shard.unloadSec (120) with nobody inside (folder kept), at most
    shard.maxLoaded (20) loaded at once - more Enter clicks wait in a queue with a message and are told when a place is free.
  - The FARMING REGION (origin x 2048, z 0, y 100 - Mining 0 / Foraging 1024 / Farming 2048 / Ranching 3072 / Orchard 4096 / Combat
    5120): a HUB island (13 x 13, a stone plaza, the menu stand = the same shard block) + 6 FIXED SLOTS on a hexagon 48 blocks out; a
    filled slot gets its plank bridge (3 wide) and an island that grows IN PLACE: Small 13 x 13 / Medium 21 x 21 / Large 29 x 29
    (tilled soil + vanilla ETERNAL wheat, a grass rim, a stone totem pillar in the middle). Slot 1 starts as Wheat Small with ONE
    Harvest Spirit I totem (shown as particles above its pillar while someone is inside - spec 10.6 fallback; workers come later).
    Every Enter (and Grow) repairs the region: soil / rim / pillar / bridge blocks put back when different, crops only where the block
    is AIR (a ripe or growing crop is never reset); every shard.regrowSec while someone is inside only the crops on AIR are put back
    (regrow of broken crops; no soil reads, no relight - the full repair took ~40 ms on the world thread in the smoke self test).
  - PROTECTION in shard worlds = SkyyIslands 0.5.8's guards asking shard:fn:allowed (this mod): harvest / break / damage crops (any
    Plant_Crop_ block) and use them (F harvest), use the menu stand, pick up and drop items; everything else refused (place, break,
    use other blocks - no tilling, no building -, use NPCs, hurt NPCs). Without SkyyIslands 0.5.8 (no island:shardguard) Enter is
    refused, so a shard world is never open unguarded.
  - WHO: the island owner and co-op members (admin / member) may Enter (G8); Collect / buy storage / Grow = the owner profile, co-op
    too only with shard.coopCollect (default off); only the owner places / picks up; visitors and trusted players get a refusal line.
    Every build / click re-checks the role (not only Enter). A deleted (pending) / archived owner profile is closed to co-op. Inside a
    shard world the 1 s sweep sends anyone who is not owner / co-op (island:role:key:fn, SkyyIslands 0.5.8) / a server admin to the hub.
  - LAZY PRODUCTION (no ticking, offline maths - Pocket-Shards-Spec 8): per island rate (items / minute) = totem rate (Harvest Spirit I =
    totem.rate1, 1.0) x the size factor (1 / island.factor.medium 1.6 / island.factor.large 2.4). On every menu open / Collect / Grow:
    elapsed = now - last (at most shard.maxOfflineSec, 3 days), made = floor(elapsed x rate), last moves on by exactly the time those
    items took (the part-item stays), capped by the shard STORAGE (tier 1-5: storage.tier1..5 stacks of 100 per island; full = last =
    now, production stops). Settling never writes the file (a recompute from the saved last gives the same or less, never more).
  - COLLECT (per island or all): debit the shard file FIRST (written at once), give the wheat into the collector's inventory (storage,
    hotbar, backpack - each add counted before / after, stacks of 100), credit back what did not fit (written), then pay Farming XP =
    floor(given x xp.wheat x shard.xpPercent / 100) through skill:fn:addxp (source shard:farming) and the Wheat collection through
    coll:fn:add (source "shard", chunks of 256). If SkyyCollections refuses the source (bridge.add.sources lacks "shard"), the count waits
    in the collector's file (owed.coll) and is retried on every Collect - the menu says how to switch it on.
  - UPGRADES: Storage tier 2-5 (coins storage.coins.N + Enchanted Wheat storage.ench.N, items taken first and counted, coins after, items
    given back if the coins fail). Auto-Compactor and Time Compressor cards say "later update" (phase 7).
  - GROW: Small -> Medium (grow.medium.coins + grow.medium.seeds Eternal Wheat Seeds, Wheat collection grow.medium.coll IV) and Medium ->
    Large (grow.large.*, VI); the island is pasted bigger in place right away when the shard world is loaded (else on the next Enter).
  - THE SHARD MENU (one page, 1100 x 860, tabs Collect / Upgrades / Islands / Totems, the mockup's layout on the vanilla kit): portal
    view (right-click your portal: Enter Shard, Pick up Shard), hub view (the stand inside: Back to Island) and menu view (the SkyWynn
    Menu "Shards" tile, SkyyMenu 0.3.22, bridge shard:fn:open: everything but Pick up).
  - /shardadmin (skyyshards.admin): give <player> | info <player> | unplace <player> | unload <player>.
  - Bridge (java.lang types): shard:fn:allowed (Object[]{String world, String action, String blockId, UUID player} -> Boolean, null =
    not a shard world), shard:fn:open (UUID -> Boolean, world thread), shard:fn:world (String world -> owner pkey or null),
    shard:version "0.1".
  - Data: Skyy_SkyyShards/shards/<pkey>.properties (v=1; farming.placed, farming.storage, farming.i<n>.type / size / last / stored /
    totems; owed.coll.<item>); collect.log (one line per Collect: who, island, debit, given, back). Config: Skyy_SkyyShards/config.properties.
NOT in 0.1 (spec phases 6-8): totem crafting / tiers / slots / boosters / pick-up, the other five shards, compactor, time compressor,
  more crops, worker NPCs, step-on pads, the Void (Magic Bags) as the first Collect target (SkyySacks has no give bridge yet).
FLOOR for tools/deploy_set.py: once a shard world exists, SkyyShards 0.1 + SkyyIslands 0.5.8 are a floor (the engine loads every world
  folder at start; older SkyyIslands would leave a shard world unguarded if anyone reached it by /tp; a rollback without SkyyShards
  keeps the folder and the data file untouched).
REVIEW FIXES (2026-10-14, shards01fix; each has a "fix:" check in the harness):
  - role re-check at every page build / click and inside collect / buyStorage / grow (ShCore.gate); the sweep every 1 s (was 5 s) -
    a removed co-op member, someone logged out inside, or a /profiles switch inside a shard can no longer collect the old profile's shard.
  - ShRole.closed: SkyyProfiles profile:fn:state pending / archived = no co-op in that shard (SkyyIslands 0.5.8 RoleKeyFn also null).
  - island RESET: SkyyIslands 0.5.8 island:world:key:fn (owner key -> current island world). A placed record whose world is not the
    current island is stale: dropped when placing, no placing in a backup world, Enter refused, Back to Island goes to the hub, and Pick
    up Shard works from the menu view (gives the item back). Pick up gives the item FIRST and writes the record after (a refused write
    takes the item back) - never a shard twice; a missing portal block also gives the item back now.
  - Enter needs a placed shard (no world for a profile without one); Collect / buy / Grow need a shard that exists.
  - farming.paused = 1 while picked up / unplaced: no production until placed again (placing restarts the clocks).
  - buy storage / Grow: a refused save undoes the change and refunds the items + coins (coins:fn:add).
  - Farming XP that could not be paid waits in the collector's file (owed.xp) and is paid on the next Collect.
  - idle unload: at most 2 worlds a tick (the engine loads every world folder at start); an Enter on a loaded world restarts its idle
    clock; a teleport into a world that closed meanwhile tells the player.
  - Pick up Shard is shown only to the owner; page copy: no Sprites / range (0.1 has particles only).
REVIEW FIXES 2 (2026-10-14, shards01fix2; each has a "fix2:" check in the harness):
  - the shard world's own death rule: "Death": {"ItemsLossMode": "None"} (Default.json would drop 50 % into the void; Skyy's lock
    "island deaths keep items", the SkyyWorldGen 0.5.1 precedent).
  - a placed record that went stale (island reset) pauses production the first time it is seen (Collect / buy / Grow / the menu).
  - profile:busy:<uuid> (PROFILES-CONTRACT rule 5): Collect / buy / Grow / Pick up refused while it is set.
  - Collect writes lastCollect (the Collect tab's "Last collected ... ago").
  - unpaid XP / collection counts whose collector file cannot be read wait in memory (+ a WARN + a collect.log line), not dropped.
  - Pick up at the portal refuses while the portal's chunk is not loaded (no second portal block left behind).
  - swept / leaving players go to the REAL hub (SkyyIslands 0.5.8 island:fn:hub = /sethub), the default world spawn only as a fallback.
  - totem.particle is checked against the game's particle systems before it is sent to clients (unknown = the default + one WARN).
  - "Your Farming Shard is placed" is said only after the block is seen (1 s check; a chunk not loaded yet is checked again, 10 tries);
    a placement another rule cancelled says so.
  - page copy: the totem row no longer claims "the whole island"; the Islands map caption says more crops come later.
"""
import sys, os, re, json, zipfile, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG
import skyyui as SUI
import skyyart as SA

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SUI.verify()
KIT_ID = SUI.kit_id()
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

PKG = "com.skyy.shards"
T = {
    "JP":   "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI":  "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR":   "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF":  "com.hypixel.hytale.component.Ref",
    "ST":   "com.hypixel.hytale.component.Store",
    "CA":   "com.hypixel.hytale.component.ComponentAccessor",
    "UNI":  "com.hypixel.hytale.server.core.universe.Universe",
    "WLD":  "com.hypixel.hytale.server.core.universe.world.World",
    "EST":  "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CST":  "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "BOP":  "com.hypixel.hytale.server.core.universe.world.chunk.BlockOperations",
    "BSEC": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
    "BCH":  "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
    "WCH":  "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "CHU":  "com.hypixel.hytale.math.util.ChunkUtil",
    "BTY":  "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "INS":  "com.hypixel.hytale.builtin.instances.InstancesPlugin",
    "TRF":  "com.hypixel.hytale.math.vector.Transform",
    "TP":   "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "PTU":  "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "PSY":  "com.hypixel.hytale.server.core.asset.type.particle.config.ParticleSystem",
    "DAM":  "com.hypixel.hytale.assetstore.map.DefaultAssetMap",
    "V3D":  "org.joml.Vector3d",
    "V3DC": "org.joml.Vector3dc",
    "V3I":  "org.joml.Vector3i",
    "APC":  "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX":  "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY":  "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA":   "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG":  "com.hypixel.hytale.server.core.Message",
    "HSV":  "com.hypixel.hytale.server.core.HytaleServer",
    "LOG":  "com.hypixel.hytale.logger.HytaleLogger",
    "PLA":  "com.hypixel.hytale.server.core.entity.entities.Player",
    "INV":  "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC":   "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS":   "com.hypixel.hytale.server.core.inventory.ItemStack",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB":  "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB":  "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD":  "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT":   "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "PM":   "com.hypixel.hytale.server.core.permissions.PermissionsModule",
    "OCU":  "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction",
    "EES":  "com.hypixel.hytale.component.system.EntityEventSystem",
    "ACH":  "com.hypixel.hytale.component.ArchetypeChunk",
    "CB":   "com.hypixel.hytale.component.CommandBuffer",
    "EV":   "com.hypixel.hytale.component.system.EcsEvent",
    "QRY":  "com.hypixel.hytale.component.query.Query",
    "ARCH": "com.hypixel.hytale.component.Archetype",
    "PBE":  "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent",
    "PKG":  PKG,
    "VERSION": VERSION,
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
PGM = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
for c, m in ((T["UNI"], "get"), (T["UNI"], "getWorld"), (T["UNI"], "getWorlds"), (T["UNI"], "loadWorld"), (T["UNI"], "isWorldLoadable"),
             (T["UNI"], "removeWorld"), (T["UNI"], "getDefaultWorld"), (T["UNI"], "getPlayer"), (T["UNI"], "getPlayers"),
             (T["UNI"], "getPlayerByUsername"), (T["INS"], "spawnInstance"), (T["INS"], "get"), (T["WLD"], "getName"),
             (T["WLD"], "isAlive"), (T["WLD"], "execute"), (T["WLD"], "getPlayerCount"), (T["WLD"], "getPlayerRefs"),
             (T["WLD"], "getChunkStore"), (T["WLD"], "getChunkLighting"), (T["WLD"], "getEntityStore"), (T["WLD"], "getNotificationHandler"),
             (T["CST"], "getChunkReference"), (T["CST"], "getChunkReferenceAsync"), (T["CST"], "getChunkSectionReferenceAtBlock"),
             (T["CST"], "getChunkSectionReferenceAsync"), (T["CST"], "getStore"), (T["BOP"], "setBlock"), (T["BSEC"], "get"),
             (T["BSEC"], "getComponentType"), (T["BCH"], "getComponentType"), (T["BCH"], "setTint"), (T["BCH"], "getTint"),
             (T["BCH"], "markNeedsSaving"), (T["WCH"], "getComponentType"), (T["WCH"], "markNeedsSaving"), (T["CHU"], "indexChunk"),
             (T["BTY"], "getAssetMap"), (T["BTY"], "EMPTY"), (T["BTY"], "EMPTY_ID"), (T["BTY"], "getId"), (T["TP"], "createForPlayer"),
             (T["TP"], "getComponentType"), (T["PTU"], "spawnParticleEffect"), (T["PSY"], "getAssetMap"), (T["DAM"], "getAsset"), (T["PR"], "getUuid"), (T["PR"], "getUsername"),
             (T["PR"], "sendMessage"), (T["PR"], "isValid"), (T["PR"], "getReference"), (T["PR"], "getWorldUuid"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (T["EST"], "getWorld"), (T["ST"], "getExternalData"), (T["ST"], "getComponent"),
             (T["PLA"], "getInventory"), (T["PLA"], "getPageManager"), (T["PLA"], "getComponentType"), (T["INV"], "getStorage"),
             (T["INV"], "getHotbar"), (T["INV"], "getBackpack"), (T["IC"], "getCapacity"), (T["IC"], "getItemStack"),
             (T["IC"], "addItemStack"), (T["IC"], "removeItemStackFromSlot"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"),
             (T["IS"], "isEmpty"), (T["PBE"], "getItemInHand"), (T["PBE"], "getTargetBlock"), (T["PBE"], "setCancelled"),
             (T["OCU"], "registerSimple"), (PGM, "openCustomPage"), (T["PAGE"], "rebuild"), (T["PAGE"], "close"),
             (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"), (T["BT"], "Activating"),
             (T["LIFE"], "CanDismiss"), (T["PM"], "get"), (T["PM"], "hasPermission"), (T["MSG"], "raw"), (T["MSG"], "color"),
             (PB, "getDataDirectory"), (PB, "getCommandRegistry"), (PB, "getEntityStoreRegistry"), (PB, "getLogger"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "setPermissionGroups"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "requirePermission"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "withRequiredArg"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addUsageVariant"), (T["ATY"], "GREEDY_STRING")):
    B.probe(pool, c, m)

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
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:4000]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def jlit(s):
    return json.dumps(s)


def mk(name, sup=None, ifaces=()):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    for i in ifaces:
        c.addInterface(pool.get(i))
    return c


# ================= the shard model (0.1 = the Farming shard only) =================
KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]      # spec 9.1 region order, 1,024 blocks apart on x
KIND = "Farming"
KIND_KEY = "farming"
REGION_X, REGION_Z, Y = 1024 * KINDS.index(KIND), 0, 100
SHARD_ITEM = "Skyy_Shard_Farming"
PAGE_ID = "SkyyShardFarming"            # the OpenCustomUI page id of the farming shard block (registerSimple)
SLOTS = 6
RING = 48                               # spec 9.1: 6 fixed slots on a hexagon 48 blocks out
HALF = [6, 10, 14]                      # Small 13 x 13, Medium 21 x 21, Large 29 x 29 (spec 9.1); index = size - 1
SIZE_NAMES = ["Small", "Medium", "Large"]
HUB_HALF = 6
SLOT_POS = []
for _i in range(SLOTS):                 # slot 1 = north (-z), then clockwise
    _a = math.radians(-90 + 60 * _i)
    SLOT_POS.append((int(round(RING * math.cos(_a))), int(round(RING * math.sin(_a)))))
for _i in range(SLOTS):
    for _j in range(_i + 1, SLOTS):
        _d = math.hypot(SLOT_POS[_i][0] - SLOT_POS[_j][0], SLOT_POS[_i][1] - SLOT_POS[_j][1])
        assert _d - 2 * HALF[2] * math.sqrt(2) > 4 or _d > 2 * HALF[2] + 8, "slots %d / %d overlap at Large" % (_i, _j)
assert RING - HALF[2] - HUB_HALF >= 8, "the hub and a Large island leave a bridge"
CHUNKS = sorted(set(((REGION_X + dx) >> 5, (REGION_Z + dz) >> 5) for dx in range(-(RING + HALF[2] + 2), RING + HALF[2] + 3)
                    for dz in range(-(RING + HALF[2] + 2), RING + HALF[2] + 3)))
assert len(CHUNKS) <= 25, CHUNKS
CROP = {"type": "wheat", "name": "Wheat", "block": "Plant_Crop_Wheat_Block_Eternal", "item": "Plant_Crop_Wheat_Item", "coll": "Wheat",
        "ench": "Skyy_Ench_Wheat", "seed": "Plant_Seeds_Wheat_Eternal"}
BLOCKS = {"grass": "Soil_Grass", "dirt": "Soil_Dirt", "till": "Soil_Dirt_Tilled", "stone": "Rock_Stone", "brick": "Rock_Stone_Brick",
          "plank": "Wood_Softwood_Planks", "crop": CROP["block"], "stand": SHARD_ITEM}
PARTICLE = "Dust_Sparkles_Fine"
TOTEM_NAME = "Harvest Spirit"
ARRIVE = (REGION_X + 0.5, Y + 1.0, REGION_Z + 3.5)       # the hub plaza, facing the stand at (0, -3)
STAND = (REGION_X, Y + 1, REGION_Z - 3)

# ================= Assets.zip (read only): every vanilla id this mod names must exist; our ids must be new =================
import serverjar as _SJ
AZ = zipfile.ZipFile(_SJ.assets_zip())   # a cached copy of Assets.zip (read only; tools/serverjar.py)
AZN = set(AZ.namelist())
ITEMS = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZN if n.startswith("Server/Item/Items/") and n.endswith(".json"))
for _iid in list(BLOCKS.values())[:-1] + [CROP["item"], CROP["seed"], "Portal_Device"]:
    assert _iid in ITEMS, "vanilla item %s is not in Assets.zip" % _iid
assert SHARD_ITEM not in ITEMS, "our shard id clashes with a vanilla item"
assert any(n.endswith("/" + PARTICLE + ".particlesystem") for n in AZN), "particle system %s missing" % PARTICLE
_pd = json.loads(AZ.read(ITEMS["Portal_Device"]).decode("utf-8-sig"))["BlockType"]
assert _pd["CustomModel"] == "Blocks/Miscellaneous/Platform_MagicInactive.blockymodel" and _pd["HitboxType"] == "Pad_Portal"
_ICON_SRC = os.path.join(ROOT, "research", "cloud", "icons-1013", "icons", "Skyy_Shard_Portal_Farming.png")
assert os.path.isfile(_ICON_SRC), _ICON_SRC
# installed mods (read only): no other jar may already ship our ids
_mods = B.MODS_DIR
if os.path.isdir(_mods):
    for _f in os.listdir(_mods):
        if _f.lower().endswith((".jar", ".zip")) and not _f.startswith("SkyyShards"):
            try:
                with zipfile.ZipFile(os.path.join(_mods, _f)) as _z:
                    assert not [n for n in _z.namelist() if n.endswith("/" + SHARD_ITEM + ".json")], "%s ships %s" % (_f, SHARD_ITEM)
            except zipfile.BadZipFile:
                pass

# ================= config (the kit's DEFAULTS and the first-run file are the same text) =================
STORE_STACKS = [1, 3, 6, 12, 24]
STORE_COINS = [0, 5000, 25000, 100000, 400000]
STORE_ENCH = [0, 1, 4, 16, 64]
CONFIG_TEXT = "\n".join([
    "# SkyyShards settings (research/Gathering-Shards-Spec.md section 9). Change them in game: SkyWynn Menu -> Server Setup -> Shards.",
    "# shards.on = the whole shard feature (portals, the menu, entering). false: the menu and Enter say shards are switched off.",
    "shards.on=true",
    "# shard.maxLoaded = how many shard worlds may be loaded at once (one Java thread each). More Enter clicks wait in a queue.",
    "# (Not at server start: the game loads every world folder then; empty shard worlds unload 2 per second after shard.unloadSec.)",
    "shard.maxLoaded=20",
    "# shard.unloadSec = a shard world nobody is in unloads after this many seconds (the folder stays).",
    "shard.unloadSec=120",
    "# shard.coopCollect = co-op members may Collect, buy storage and Grow in the owner's shard (true) or only enter it (false).",
    "shard.coopCollect=false",
    "# shard.maxOfflineSec = production counts at most this long between two visits to the menu (259200 = 3 days).",
    "shard.maxOfflineSec=259200",
    "# shard.regrowSec = while someone is inside, broken crops grow back (and the region is repaired) this often.",
    "shard.regrowSec=90",
    "# shard.xpPercent = Farming XP paid at Collect, in percent of the overworld XP per item (Skyy G9: 50).",
    "shard.xpPercent=50",
    "# xp.wheat = the overworld Farming XP of one wheat (SkyySkills' wheat harvest).",
    "xp.wheat=4",
    "# totem.rate1 = items per minute of one Harvest Spirit I.",
    "totem.rate1=1",
    "# island.factor.medium / island.factor.large = production of a Medium / Large island compared with a Small one.",
    "island.factor.medium=1.6",
    "island.factor.large=2.4",
    "# storage.tierN = stacks of 100 each island of the shard holds at storage tier N.",
] + ["storage.tier%d=%d" % (i + 1, STORE_STACKS[i]) for i in range(5)] + [
    "# storage.coins.N / storage.ench.N = the cost of storage tier N (coins + Enchanted Wheat).",
] + ["storage.coins.%d=%d" % (i + 1, STORE_COINS[i]) for i in range(1, 5)] + ["storage.ench.%d=%d" % (i + 1, STORE_ENCH[i]) for i in range(1, 5)] + [
    "# grow.medium.* / grow.large.* = growing an island: coins, Eternal Seeds of its crop, the crop's collection tier needed.",
    "grow.medium.coins=5000",
    "grow.medium.seeds=8",
    "grow.medium.coll=4",
    "grow.large.coins=20000",
    "grow.large.seeds=24",
    "grow.large.coll=6",
    "# totem.particle = the particle shown above a working totem; totem.particleSec = how often (seconds).",
    "totem.particle=" + PARTICLE,
    "totem.particleSec=2",
    "",
])

cfg = mk("ShCfg")
for f in ("public static volatile boolean ON = true;", "public static volatile int MAX_LOADED = 20;", "public static volatile int UNLOAD_SEC = 120;", "public static volatile boolean COOP_COLLECT = false;",
          "public static volatile int MAX_OFF_SEC = 259200;", "public static volatile int REGROW_SEC = 90;", "public static volatile int XP_PCT = 50;",
          "public static volatile int XP_WHEAT = 4;", "public static volatile double RATE1 = 1.0;", "public static volatile double F_MED = 1.6;",
          "public static volatile double F_LARGE = 2.4;", "public static volatile int ST1 = 1;", "public static volatile int ST2 = 3;",
          "public static volatile int ST3 = 6;", "public static volatile int ST4 = 12;", "public static volatile int ST5 = 24;",
          "public static volatile int SC2 = 5000;", "public static volatile int SC3 = 25000;", "public static volatile int SC4 = 100000;",
          "public static volatile int SC5 = 400000;", "public static volatile int SE2 = 1;", "public static volatile int SE3 = 4;",
          "public static volatile int SE4 = 16;", "public static volatile int SE5 = 64;", "public static volatile int GM_COINS = 5000;",
          "public static volatile int GM_SEEDS = 8;", "public static volatile int GM_COLL = 4;", "public static volatile int GL_COINS = 20000;",
          "public static volatile int GL_SEEDS = 24;", "public static volatile int GL_COLL = 6;",
          "public static volatile String PARTICLE = %s;" % jlit(PARTICLE), "public static volatile int PART_SEC = 2;",
          "public static java.nio.file.Path DIR;", "public static java.nio.file.Path FILE;", "public static @LOG@ LOG;",
          "public static volatile java.util.Map BRIDGE;", "public static volatile java.util.function.Function PERM_TEST;",
          "public static volatile java.util.function.Function KEY_TEST;",
          "public static volatile java.util.function.Function PART_TEST;",
          "public static final java.util.concurrent.ConcurrentHashMap PART_SEEN = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
          "public static final String DEFAULT_TEXT = %s;" % jlit(CONFIG_TEXT)):
    F(cfg, f)

CATS = [("shards", "Shards"), ("production", "Production"), ("costs", "Costs")]
ROWS = [
    ("shards.on", "Shards (whole feature)", "shards", "bool", "true", "", "", "", "", "live",
     "Off: shard portals open no menu and nobody can enter a shard. Nothing is deleted.", "field:ShCfg.ON@config.properties:shards.on"),
    ("shard.maxLoaded", "Shard worlds loaded at once", "shards", "int", "20", "1", "500", "", "", "live",
     "One server thread each; more Enter clicks wait in a queue. Not at server start (empty ones unload).", "field:ShCfg.MAX_LOADED@config.properties:shard.maxLoaded"),
    ("shard.unloadSec", "Unload an empty shard after", "shards", "int", "120", "30", "3600", "", "s", "live",
     "Seconds with nobody inside before a shard world unloads (its folder stays).", "field:ShCfg.UNLOAD_SEC@config.properties:shard.unloadSec"),
    ("shard.coopCollect", "Co-op may collect and upgrade", "shards", "bool", "false", "", "", "", "", "live",
     "On: co-op may Collect, buy storage and Grow in the owner's shard. Off: co-op may only enter.", "field:ShCfg.COOP_COLLECT@config.properties:shard.coopCollect"),
    ("shard.regrowSec", "Crops grow back every", "shards", "int", "90", "10", "3600", "", "s", "live",
     "While someone is inside, broken crops grow back this often.", "field:ShCfg.REGROW_SEC@config.properties:shard.regrowSec"),
    ("shard.maxOfflineSec", "Longest production between visits", "production", "int", "259200", "3600", "2592000", "", "s", "live",
     "Production counts at most this long between two menu visits (259200 = 3 days).", "field:ShCfg.MAX_OFF_SEC@config.properties:shard.maxOfflineSec"),
    ("shard.xpPercent", "Collect XP (percent)", "production", "int", "50", "0", "100", "", "%", "live",
     "Farming XP paid at Collect, in percent of the overworld XP per item (Skyy: 50).", "field:ShCfg.XP_PCT@config.properties:shard.xpPercent"),
    ("xp.wheat", "Farming XP per wheat", "production", "int", "4", "0", "1000", "", "", "live",
     "The overworld Farming XP of one wheat (before the percent above).", "field:ShCfg.XP_WHEAT@config.properties:xp.wheat"),
    ("totem.rate1", "Harvest Spirit I items per minute", "production", "dec", "1", "0", "100", "", "", "live",
     "Items per minute of one Harvest Spirit I totem on a Small island.", "field:ShCfg.RATE1@config.properties:totem.rate1"),
    ("island.factor.medium", "Medium island factor", "production", "dec", "1.6", "1", "10", "", "x", "live",
     "Production of a Medium island compared with a Small one.", "field:ShCfg.F_MED@config.properties:island.factor.medium"),
    ("island.factor.large", "Large island factor", "production", "dec", "2.4", "1", "10", "", "x", "live",
     "Production of a Large island compared with a Small one.", "field:ShCfg.F_LARGE@config.properties:island.factor.large"),
] + [("storage.tier%d" % (i + 1), "Storage tier %d (stacks)" % (i + 1), "production", "int", str(STORE_STACKS[i]), "1", "1000", "", "", "live",
      "Stacks of 100 each island holds at storage tier %d." % (i + 1), "field:ShCfg.ST%d@config.properties:storage.tier%d" % (i + 1, i + 1))
     for i in range(5)] + \
    [("storage.coins.%d" % (i + 1), "Storage tier %d coins" % (i + 1), "costs", "int", str(STORE_COINS[i]), "0", "1000000000", "", "", "live",
      "Coins for storage tier %d." % (i + 1), "field:ShCfg.SC%d@config.properties:storage.coins.%d" % (i + 1, i + 1)) for i in range(1, 5)] + \
    [("storage.ench.%d" % (i + 1), "Storage tier %d Enchanted Wheat" % (i + 1), "costs", "int", str(STORE_ENCH[i]), "0", "10000", "", "", "live",
      "Enchanted Wheat for storage tier %d." % (i + 1), "field:ShCfg.SE%d@config.properties:storage.ench.%d" % (i + 1, i + 1)) for i in range(1, 5)] + [
    ("grow.medium.coins", "Grow to Medium: coins", "costs", "int", "5000", "0", "1000000000", "", "", "live", "Coins to grow an island to Medium.",
     "field:ShCfg.GM_COINS@config.properties:grow.medium.coins"),
    ("grow.medium.seeds", "Grow to Medium: Eternal Seeds", "costs", "int", "8", "0", "10000", "", "", "live", "Eternal Seeds of the crop to grow to Medium.",
     "field:ShCfg.GM_SEEDS@config.properties:grow.medium.seeds"),
    ("grow.medium.coll", "Grow to Medium: collection tier", "costs", "int", "4", "0", "20", "", "", "live", "The crop's collection tier needed for Medium.",
     "field:ShCfg.GM_COLL@config.properties:grow.medium.coll"),
    ("grow.large.coins", "Grow to Large: coins", "costs", "int", "20000", "0", "1000000000", "", "", "live", "Coins to grow an island to Large.",
     "field:ShCfg.GL_COINS@config.properties:grow.large.coins"),
    ("grow.large.seeds", "Grow to Large: Eternal Seeds", "costs", "int", "24", "0", "10000", "", "", "live", "Eternal Seeds of the crop to grow to Large.",
     "field:ShCfg.GL_SEEDS@config.properties:grow.large.seeds"),
    ("grow.large.coll", "Grow to Large: collection tier", "costs", "int", "6", "0", "20", "", "", "live", "The crop's collection tier needed for Large.",
     "field:ShCfg.GL_COLL@config.properties:grow.large.coll"),
    ("totem.particle", "Totem particle", "shards", "text", PARTICLE, "", "120", "", "", "live",
     "The vanilla particle system shown above a working totem.", "field:ShCfg.PARTICLE@config.properties:totem.particle"),
    ("totem.particleSec", "Totem particles every", "shards", "int", "2", "1", "60", "", "s", "live",
     "Seconds between two particle bursts above a working totem.", "field:ShCfg.PART_SEC@config.properties:totem.particleSec"),
]
kit = CFG.emit(pool, PKG, MOD="SkyyShards", TITLE="Shards", VERSION=VERSION, NODE="skyyshards.admin", CATS=CATS, ROWS=ROWS,
               FILES=["Skyy_SkyyShards/config.properties"], NOTE="Shard islands (Farming shard). Changes are live.",
               RELOAD=None, KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT})

# ================= ShCfg methods =================
M(cfg, r"""
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyShards] " + m); else System.out.println("[SkyyShards] " + m); } catch (Throwable t) { }
}""")
M(cfg, r"""
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyShards] " + m); else System.out.println("[SkyyShards] WARNING " + m); } catch (Throwable t) { }
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
# fix2: the totem particle actually sent to clients - an admin's totem.particle only when the game has that particle system (checked once
# per name; unknown or no asset map = the default + one WARN). PART_TEST = the harness's stand-in for the asset map lookup.
M(cfg, r"""
public static String particle() {
  String n = PARTICLE;
  if (n == null || n.length() == 0 || n.equals(@DEF@)) return @DEF@;
  Object seen = PART_SEEN.get(n);
  if (seen == null) {
    boolean good = false;
    try {
      if (PART_TEST != null) good = Boolean.TRUE.equals(PART_TEST.apply(n));
      else { @DAM@ m = @PSY@.getAssetMap(); good = m != null && m.getAsset((Object) n) != null; }
    } catch (Throwable t) { good = false; }
    seen = Boolean.valueOf(good);
    PART_SEEN.put(n, seen);
    if (!good) warnOnce("particle:" + n, "totem.particle '" + n + "' is not a particle system of this game - showing " + @DEF@ + " instead (Server Setup -> Shards)");
  }
  return Boolean.TRUE.equals(seen) ? n : @DEF@;
}""".replace("@DEF@", jlit(PARTICLE)))
M(cfg, r"""
public static java.util.function.Function fn(String key) {
  Object o = bridge().get(key);
  return o instanceof java.util.function.Function ? (java.util.function.Function) o : null;
}""")
# tools/PROFILES-CONTRACT.md helper (KEY_TEST = the harness's stand-in for profile:fn:key)
M(cfg, r"""
public static String pkey(java.util.UUID u) {
  try {
    java.util.function.Function f = KEY_TEST != null ? KEY_TEST : fn("profile:fn:key");
    if (f != null) {
      Object r = f.apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(cfg, r"""
public static boolean isAdmin(java.util.UUID u) {
  if (u == null) return false;
  try {
    java.util.function.Function f = PERM_TEST;
    if (f != null) return Boolean.TRUE.equals(f.apply(u));
    return @PM@.get().hasPermission(u, "skyyshards.admin");
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
public static double decOf(String v, double d, double lo, double hi) {
  double x = d;
  if (v != null) { try { x = Double.parseDouble(v.trim()); } catch (Throwable t) { x = d; } }
  if (Double.isNaN(x)) x = d;
  if (x < lo) x = lo;
  if (x > hi) x = hi;
  return x;
}""")
M(cfg, r"""
public static String num(long n) {
  String s = String.valueOf(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    if (i > 0 && (s.length() - i) % 3 == 0) sb.append(',');
    sb.append(s.charAt(i));
  }
  return (n < 0L ? "-" : "") + sb.toString();
}""")
M(cfg, r"""
public static String dec(double d) {
  long r = Math.round(d * 100.0);
  if (r % 100L == 0L) return String.valueOf(r / 100L);
  if (r % 10L == 0L) return (r / 100L) + "." + ((r % 100L) / 10L);
  return (r / 100L) + "." + ((r % 100L) < 10L ? "0" : "") + (r % 100L);
}""")
M(cfg, r"""
public static boolean writeDefaults() {
  try {
    if (FILE == null || java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return false;
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(FILE, DEFAULT_TEXT.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
    return true;
  } catch (Throwable t) { warn("could not write the default config.properties: " + t); return false; }
}""")
_load = ["  ON = bool(p.getProperty(\"shards.on\"), true);",
         "  MAX_LOADED = intOf(p.getProperty(\"shard.maxLoaded\"), 20, 1, 500);",
         "  UNLOAD_SEC = intOf(p.getProperty(\"shard.unloadSec\"), 120, 30, 3600);",
         "  COOP_COLLECT = bool(p.getProperty(\"shard.coopCollect\"), false);",
         "  REGROW_SEC = intOf(p.getProperty(\"shard.regrowSec\"), 90, 10, 3600);",
         "  MAX_OFF_SEC = intOf(p.getProperty(\"shard.maxOfflineSec\"), 259200, 3600, 2592000);",
         "  XP_PCT = intOf(p.getProperty(\"shard.xpPercent\"), 50, 0, 100);",
         "  XP_WHEAT = intOf(p.getProperty(\"xp.wheat\"), 4, 0, 1000);",
         "  RATE1 = decOf(p.getProperty(\"totem.rate1\"), 1.0, 0.0, 100.0);",
         "  F_MED = decOf(p.getProperty(\"island.factor.medium\"), 1.6, 1.0, 10.0);",
         "  F_LARGE = decOf(p.getProperty(\"island.factor.large\"), 2.4, 1.0, 10.0);"]
_load += ["  ST%d = intOf(p.getProperty(\"storage.tier%d\"), %d, 1, 1000);" % (i + 1, i + 1, STORE_STACKS[i]) for i in range(5)]
_load += ["  SC%d = intOf(p.getProperty(\"storage.coins.%d\"), %d, 0, 1000000000);" % (i + 1, i + 1, STORE_COINS[i]) for i in range(1, 5)]
_load += ["  SE%d = intOf(p.getProperty(\"storage.ench.%d\"), %d, 0, 10000);" % (i + 1, i + 1, STORE_ENCH[i]) for i in range(1, 5)]
_load += ["  GM_COINS = intOf(p.getProperty(\"grow.medium.coins\"), 5000, 0, 1000000000);",
          "  GM_SEEDS = intOf(p.getProperty(\"grow.medium.seeds\"), 8, 0, 10000);",
          "  GM_COLL = intOf(p.getProperty(\"grow.medium.coll\"), 4, 0, 20);",
          "  GL_COINS = intOf(p.getProperty(\"grow.large.coins\"), 20000, 0, 1000000000);",
          "  GL_SEEDS = intOf(p.getProperty(\"grow.large.seeds\"), 24, 0, 10000);",
          "  GL_COLL = intOf(p.getProperty(\"grow.large.coll\"), 6, 0, 20);",
          "  String pt = p.getProperty(\"totem.particle\");",
          "  PARTICLE = (pt == null || pt.trim().length() == 0) ? %s : pt.trim();" % jlit(PARTICLE),
          "  PART_SEC = intOf(p.getProperty(\"totem.particleSec\"), 2, 1, 60);"]
M(cfg, r"""
public static String loadCfg(boolean first) {
  java.util.Properties p = new java.util.Properties();
  boolean wrote = first && writeDefaults();
  try {
    if (FILE != null && java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
  } catch (Throwable t) { warn("config.properties could not be read - defaults are used: " + t); }
%s
  return (wrote ? "default config.properties written; " : "") + "shards " + (ON ? "ON" : "OFF") + ", max " + MAX_LOADED + " loaded, unload after " + UNLOAD_SEC + " s, Harvest Spirit I " + dec(RATE1) + " / min, XP " + XP_PCT + " %%";
}""" % "\n".join(_load))
M(cfg, r"""
public static int stacks(int tier) {
  if (tier <= 1) return ST1;
  if (tier == 2) return ST2;
  if (tier == 3) return ST3;
  if (tier == 4) return ST4;
  return ST5;
}""")
M(cfg, r"""
public static long storeCoins(int tier) {
  if (tier == 2) return (long) SC2;
  if (tier == 3) return (long) SC3;
  if (tier == 4) return (long) SC4;
  if (tier >= 5) return (long) SC5;
  return 0L;
}""")
M(cfg, r"""
public static int storeEnch(int tier) {
  if (tier == 2) return SE2;
  if (tier == 3) return SE3;
  if (tier == 4) return SE4;
  if (tier >= 5) return SE5;
  return 0;
}""")

# ================= ShStore: Skyy_SkyyShards/shards/<pkey>.properties (one profile), cached, written at once (tmp + move) =================
st = mk("ShStore")
for f in ("public static java.nio.file.Path DIR;",
          "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap BAD = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.atomic.AtomicLong WRITES = new java.util.concurrent.atomic.AtomicLong();",
          "public static volatile boolean FAIL_TEST = false;",
          "public static final java.util.concurrent.locks.ReentrantLock LOCK = new java.util.concurrent.locks.ReentrantLock();"):
    F(st, f)
M(st, r"""
public static boolean validKey(String k) {
  return k != null && k.length() >= 36 && k.length() <= 48 && k.matches("[0-9a-fA-F-]{36}(-p[0-9]{1,4})?");
}""")
M(st, r"""
public static java.util.Properties readNow(String k) {
  try {
    java.nio.file.Path f = DIR.resolve(k + ".properties");
    java.util.Properties p = new java.util.Properties();
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
    }
    BAD.remove(k);
    return p;
  } catch (Throwable t) {
    BAD.put(k, Boolean.TRUE);
    @PKG@.ShCfg.warnOnce("read:" + k, "could not read shards/" + k + ".properties - that shard stays closed and the file is never overwritten: " + t);
    return null;
  }
}""")
# the profile's live Properties (the cache owns it; callers change it only while holding ShStore.LOCK - a ReentrantLock, javassist's synchronized blocks hold one call - then save)
M(st, r"""
public static java.util.Properties get(String k) {
  if (!validKey(k) || DIR == null) return null;
  Object o = CACHE.get(k);
  if (o != null) return (java.util.Properties) o;
  java.util.Properties p = readNow(k);
  if (p == null) return null;
  Object prev = CACHE.putIfAbsent(k, p);
  return prev != null ? (java.util.Properties) prev : p;
}""")
M(st, r"""
public static void moveInto(java.nio.file.Path from, java.nio.file.Path to) throws java.io.IOException {
  try {
    java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  } catch (java.nio.file.AtomicMoveNotSupportedException e) {
    java.nio.file.Files.move(from, to, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
  }
}""")
# null = written; else the reason. An unreadable file is never overwritten. Shard files change only on a click (place, Collect, buy, grow,
# pick up) - written at once so the Collect debit is on disk before a single item is given.
M(st, r"""
public static synchronized String save(String k, java.util.Properties p) {
  if (!validKey(k) || p == null || DIR == null) return "bad profile key or no data folder";
  if (BAD.containsKey(k)) return "shards/" + k + ".properties could not be read - not overwritten";
  if (FAIL_TEST) return "test: the disk refused the write";
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(k + ".properties.tmp");
    java.util.Properties c = new java.util.Properties();
    c.putAll(p);
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try { c.store(out, "SkyyShards @VERSION@ - one profile's shards (research/Gathering-Shards-Spec.md 8)"); } finally { out.close(); }
    moveInto(tmp, DIR.resolve(k + ".properties"));
    WRITES.incrementAndGet();
    return null;
  } catch (Throwable t) { return "could not write shards/" + k + ".properties: " + t; }
}""")
M(st, r"""
public static synchronized void log(String line) {
  try {
    if (DIR == null) return;
    java.nio.file.Path f = DIR.getParent().resolve("collect.log");
    String l = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new java.util.Date()) + " " + line + "\n";
    java.nio.file.Files.write(f, l.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("log", "collect.log could not be written: " + t); }
}""")
M(st, r"""
public static long lng(java.util.Properties p, String key, long d) {
  if (p == null) return d;
  String v = p.getProperty(key);
  if (v == null) return d;
  try { return Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
M(st, r"""
public static int intv(java.util.Properties p, String key, int d, int lo, int hi) {
  long v = lng(p, key, (long) d);
  if (v < (long) lo) return lo;
  if (v > (long) hi) return hi;
  return (int) v;
}""")
M(st, r"""
public static String str(java.util.Properties p, String key) {
  if (p == null) return "";
  String v = p.getProperty(key);
  return v == null ? "" : v.trim();
}""")

# ================= ShMath: lazy production (spec 9.2; no ticking) - pure, any thread, under the ShStore lock when it changes a profile =================
mth = mk("ShMath")
F(mth, 'public static final String K = "%s";' % KIND_KEY)
F(mth, "public static final int SLOTS = %d;" % SLOTS)
M(mth, r"""
public static String ik(int slot, String f) {
  return K + ".i" + slot + "." + f;
}""")
M(mth, r"""
public static boolean hasIsland(java.util.Properties p, int slot) {
  return @PKG@.ShStore.str(p, ik(slot, "type")).length() > 0;
}""")
M(mth, r"""
public static int size(java.util.Properties p, int slot) {
  return @PKG@.ShStore.intv(p, ik(slot, "size"), 1, 1, 3);
}""")
M(mth, r"""
public static int storageTier(java.util.Properties p) {
  return @PKG@.ShStore.intv(p, K + ".storage", 1, 1, 5);
}""")
M(mth, r"""
public static long cap(java.util.Properties p) {
  return 100L * (long) @PKG@.ShCfg.stacks(storageTier(p));
}""")
# totems of an island: "harvest_spirit:1,..." -> the summed worker rate (items / minute on a Small island)
M(mth, r"""
public static double totemRate(java.util.Properties p, int slot) {
  String s = @PKG@.ShStore.str(p, ik(slot, "totems"));
  if (s.length() == 0) return 0.0;
  String[] a = s.split(",");
  double r = 0.0;
  for (int i = 0; i < a.length; i++) {
    String t = a[i].trim();
    if (t.startsWith("harvest_spirit:")) {
      int tier = 1;
      try { tier = Integer.parseInt(t.substring(15).trim()); } catch (Throwable x) { tier = 1; }
      if (tier >= 1) r += @PKG@.ShCfg.RATE1;
    }
  }
  return r;
}""")
M(mth, r"""
public static int totems(java.util.Properties p, int slot) {
  String s = @PKG@.ShStore.str(p, ik(slot, "totems"));
  return s.length() == 0 ? 0 : s.split(",").length;
}""")
M(mth, r"""
public static double factor(int size) {
  if (size >= 3) return @PKG@.ShCfg.F_LARGE;
  if (size == 2) return @PKG@.ShCfg.F_MED;
  return 1.0;
}""")
M(mth, r"""
public static double rate(java.util.Properties p, int slot) {
  if (!hasIsland(p, slot)) return 0.0;
  return totemRate(p, slot) * factor(size(p, slot));
}""")
# fix (critic): farming.paused = 1 while the shard is picked up / unplaced (set by pick up and every unplace, cleared by placing)
M(mth, r"""
public static boolean paused(java.util.Properties p) {
  return "1".equals(@PKG@.ShStore.str(p, K + ".paused"));
}""")
# fix (critic): the profile has a Farming Shard (it was placed once: an island exists)
M(mth, r"""
public static boolean owned(java.util.Properties p) {
  for (int i = 0; i < SLOTS; i++) if (hasIsland(p, i)) return true;
  return false;
}""")
# settle one island at `now` (ms): returns the items made. last moves on by exactly the time the made items took (the part-item stays
# for later); elapsed is capped at shard.maxOfflineSec; a full store stops production (last = now).
M(mth, r"""
public static long settle(java.util.Properties p, int slot, long now) {
  if (!hasIsland(p, slot)) return 0L;
  long last = @PKG@.ShStore.lng(p, ik(slot, "last"), now);
  long stored = @PKG@.ShStore.lng(p, ik(slot, "stored"), 0L);
  if (stored < 0L) stored = 0L;
  long cap = cap(p);
  double r = rate(p, slot);
  if (last > now) last = now;
  if (paused(p)) r = 0.0;   // fix (critic): a picked-up shard makes nothing until it is placed again
  long maxOff = 1000L * (long) @PKG@.ShCfg.MAX_OFF_SEC;
  if (now - last > maxOff) last = now - maxOff;
  long made = 0L;
  if (r <= 0.0 || stored >= cap) {
    last = now;
  } else {
    double perMs = r / 60000.0;
    made = (long) Math.floor((double) (now - last) * perMs);
    if (stored + made >= cap) { made = cap - stored; last = now; }
    else last = last + (long) Math.floor((double) made / perMs);
    stored += made;
  }
  p.setProperty(ik(slot, "last"), String.valueOf(last));
  p.setProperty(ik(slot, "stored"), String.valueOf(stored));
  return made;
}""")
M(mth, r"""
public static long settleAll(java.util.Properties p, long now) {
  long n = 0L;
  for (int i = 0; i < SLOTS; i++) n += settle(p, i, now);
  return n;
}""")
M(mth, r"""
public static long stored(java.util.Properties p, int slot) {
  long s = @PKG@.ShStore.lng(p, ik(slot, "stored"), 0L);
  return s < 0L ? 0L : s;
}""")
# ms until the island's store is full at today's rate (-1 = never / already full)
M(mth, r"""
public static long msToFull(java.util.Properties p, int slot) {
  double r = rate(p, slot);
  long left = cap(p) - stored(p, slot);
  if (r <= 0.0 || left <= 0L) return -1L;
  return (long) Math.ceil((double) left * 60000.0 / r);
}""")
# the first island of a new shard (spec 9.1: Wheat Small + one Harvest Spirit I)
M(mth, r"""
public static void starter(java.util.Properties p, long now) {
  if (!"1".equals(p.getProperty("v"))) p.setProperty("v", "1");
  if (p.getProperty(K + ".storage") == null) p.setProperty(K + ".storage", "1");
  boolean any = false;
  for (int i = 0; i < SLOTS; i++) if (hasIsland(p, i)) any = true;
  if (any) return;
  p.setProperty(ik(0, "type"), "wheat");
  p.setProperty(ik(0, "size"), "1");
  p.setProperty(ik(0, "last"), String.valueOf(now));
  p.setProperty(ik(0, "stored"), "0");
  p.setProperty(ik(0, "totems"), "harvest_spirit:1");
}""")
M(mth, r"""
public static String fmtMs(long ms) {
  if (ms < 0L) return "-";
  long m = (ms + 59999L) / 60000L;
  if (m < 60L) return m + " m";
  long h = m / 60L;
  if (h < 48L) return h + " h " + (m % 60L) + " m";
  return (h / 24L) + " d " + (h % 24L) + " h";
}""")

# ================= ShGeo: the region layout (spec 9.1), pure maths - every block the region wants =================
geo = mk("ShGeo")
F(geo, "public static final int OX = %d;" % REGION_X)
F(geo, "public static final int OZ = %d;" % REGION_Z)
F(geo, "public static final int Y = %d;" % Y)
F(geo, "public static final int[] SX = new int[] { %s };" % ", ".join(str(p[0]) for p in SLOT_POS))
F(geo, "public static final int[] SZ = new int[] { %s };" % ", ".join(str(p[1]) for p in SLOT_POS))
F(geo, "public static final int[] HALF = new int[] { %s };" % ", ".join(str(h) for h in HALF))
F(geo, "public static final int HUB = %d;" % HUB_HALF)
F(geo, "public static final int RING = %d;" % RING)
F(geo, "public static final int[] CX = new int[] { %s };" % ", ".join(str(c[0]) for c in CHUNKS))
F(geo, "public static final int[] CZ = new int[] { %s };" % ", ".join(str(c[1]) for c in CHUNKS))
F(geo, 'public static final String[] IDS = new String[] { %s };' % ", ".join(jlit(BLOCKS[k]) for k in ("grass", "dirt", "till", "stone", "brick", "plank", "crop", "stand")))
for _n, _k in enumerate(("GRASS", "DIRT", "TILL", "STONE", "BRICK", "PLANK", "CROP", "STAND")):
    F(geo, "public static final int %s = %d;" % (_k, _n))
M(geo, r"""
public static void add(java.util.ArrayList out, int x, int y, int z, int kind) {
  out.add(new int[] { x, y, z, kind });
}""")
# the hub island + the stand (the shard block itself = the hub's menu)
# out: a flat int list x, y, z, kind (kind = index into IDS) - the island of `size` around slot `slot`
M(geo, r"""
public static void island(java.util.ArrayList out, int slot, int size) {
  int h = HALF[size < 1 ? 0 : (size > 3 ? 2 : size - 1)];
  int cx = OX + SX[slot];
  int cz = OZ + SZ[slot];
  for (int dx = -h; dx <= h; dx++) for (int dz = -h; dz <= h; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    if (ax == h && az == h) continue;
    boolean rim = ax == h || az == h;
    boolean mid = ax <= 1 && az <= 1;
    int x = cx + dx; int z = cz + dz;
    if (rim) add(out, x, Y, z, GRASS);
    else if (mid) add(out, x, Y, z, BRICK);
    else { add(out, x, Y, z, TILL); add(out, x, Y + 1, z, CROP); }
    add(out, x, Y - 1, z, DIRT);
    if (ax <= h - 2 && az <= h - 2) add(out, x, Y - 2, z, STONE);
    if (ax <= h - 4 && az <= h - 4) add(out, x, Y - 3, z, STONE);
  }
  add(out, cx, Y + 1, cz, BRICK);
  add(out, cx, Y + 2, cz, BRICK);
}""")
M(geo, r"""
public static void hub(java.util.ArrayList out) {
  int h = HUB;
  for (int dx = -h; dx <= h; dx++) for (int dz = -h; dz <= h; dz++) {
    int ax = dx < 0 ? -dx : dx;
    int az = dz < 0 ? -dz : dz;
    if (ax + az > h + 3) continue;
    int x = OX + dx; int z = OZ + dz;
    add(out, x, Y, z, (ax <= 3 && az <= 3) ? BRICK : GRASS);
    add(out, x, Y - 1, z, DIRT);
    if (ax + az <= h) add(out, x, Y - 2, z, STONE);
    if (ax + az <= h - 3) add(out, x, Y - 3, z, STONE);
  }
  add(out, OX, Y + 1, OZ - 3, STAND);
}""")
# the plank bridge (3 wide) from the hub to the slot's Small rim; a bigger island covers its end
M(geo, r"""
public static void bridge(java.util.ArrayList out, int slot) {
  double dx = (double) SX[slot] / (double) RING;
  double dz = (double) SZ[slot] / (double) RING;
  java.util.HashSet seen = new java.util.HashSet();
  int end = RING - HALF[0];
  for (int s = (HUB - 1) * 2; s <= end * 2; s++) {
    double t = (double) s / 2.0;
    for (int w = -1; w <= 1; w++) {
      int x = (int) Math.round((double) OX + dx * t - dz * (double) w);
      int z = (int) Math.round((double) OZ + dz * t + dx * (double) w);
      String k = x + "," + z;
      if (seen.contains(k)) continue;
      seen.add(k);
      add(out, x, Y, z, PLANK);
    }
  }
}""")
# everything the profile's region wants, in paint order (hub, bridges, islands - a later block wins its position)
M(geo, r"""
public static java.util.ArrayList region(java.util.Properties p) {
  java.util.ArrayList out = new java.util.ArrayList();
  hub(out);
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(p, i)) bridge(out, i);
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(p, i)) island(out, i, @PKG@.ShMath.size(p, i));
  return out;
}""".replace("SLOTS_N()", str(SLOTS)))
# only the crops (the periodic regrow: no soil / rim / bridge reads every 90 s - perf; the full repair runs on Enter and after Grow)
M(geo, r"""
public static java.util.ArrayList crops(java.util.Properties p) {
  java.util.ArrayList all = region(p);
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < all.size(); i++) { int[] b = (int[]) all.get(i); if (b[3] == CROP) out.add(b); }
  return out;
}""")
# the island centre totem particles go above (x, y, z as doubles)
M(geo, r"""
public static double[] totemSpot(int slot) {
  return new double[] { (double) (OX + SX[slot]) + 0.5, (double) (Y + 3) + 0.4, (double) (OZ + SZ[slot]) + 0.5 };
}""")

# ================= ShFill (world thread): load the region's chunks + sections, then paint what differs (crops only on AIR) =================
fill = mk("ShFill", None, ("java.lang.Runnable", "java.util.function.BiConsumer"))
F(fill, "public @WLD@ world;")
F(fill, "public java.util.ArrayList want;")
F(fill, "public java.util.concurrent.CompletableFuture done;")
F(fill, "public int placed;")
F(fill, "public boolean cropsOnly;")
F(fill, "public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();")
F(fill, "public static final int GRASS_TINT = -10772952;")
C(fill, "public ShFill(@WLD@ w, java.util.ArrayList want, java.util.concurrent.CompletableFuture d) { this.world = w; this.want = want; this.done = d; this.placed = -1; }")
M(fill, r"""
public static @REF@ section(@WLD@ w, int x, int y, int z) {
  try {   // fix2: a world without its chunk store (closing / not ready) = not loaded, never a throw into Pick up / the checks
    @REF@ r = w.getChunkStore().getChunkSectionReferenceAtBlock(x, y, z);
    return (r == null || !r.isValid()) ? null : r;
  } catch (Throwable t) { return null; }
}""")
M(fill, r"""
public static int blockAt(@WLD@ w, int x, int y, int z) {
  @REF@ r = section(w, x, y, z);
  if (r == null) return -1;
  @BSEC@ bs = (@BSEC@) w.getChunkStore().getStore().getComponent(r, @BSEC@.getComponentType());
  return bs == null ? -1 : bs.get(x, y, z);
}""")
M(fill, r"""
public static String idAt(@WLD@ w, int x, int y, int z) {
  int b = blockAt(w, x, y, z);
  if (b < 0) return null;
  if (b == 0) return "";
  try { @BTY@ t = (@BTY@) @BTY@.getAssetMap().getAsset(b); return t == null ? "" : t.getId(); } catch (Throwable x) { return ""; }
}""")
M(fill, r"""
public static int put(@WLD@ w, int x, int y, int z, String id) {
  try {
    @REF@ r = section(w, x, y, z);
    if (r == null) return 0;
    int bid = @BTY@.getAssetMap().getIndex(id);
    if (bid == Integer.MIN_VALUE) return 0;
    @BTY@ type = (@BTY@) @BTY@.getAssetMap().getAsset(bid);
    if (type == null) return 0;
    return @BOP@.setBlock(w.getChunkStore(), r, x, y, z, bid, type, 0, 0, 0) ? 1 : 0;
  } catch (Throwable t) { return 0; }
}""")
M(fill, r"""
public static int clear(@WLD@ w, int x, int y, int z) {
  try {
    @REF@ r = section(w, x, y, z);
    if (r == null) return 0;
    return @BOP@.setBlock(w.getChunkStore(), r, x, y, z, @BTY@.EMPTY_ID, @BTY@.EMPTY, 0, 0, 0) ? 1 : 0;
  } catch (Throwable t) { return 0; }
}""")
M(fill, r"""
public static int tint(@WLD@ w, long idx) {
  int n = 0;
  try {
    @CST@ cs = w.getChunkStore();
    @REF@ r = cs.getChunkReference(idx);
    if (r == null || !r.isValid()) return 0;
    @ST@ s = cs.getStore();
    @BCH@ bc = (@BCH@) s.getComponent(r, @BCH@.getComponentType());
    if (bc == null) return 0;
    for (int x = 0; x < 32; x++) for (int z = 0; z < 32; z++) if (bc.getTint(x, z) != GRASS_TINT) { bc.setTint(x, z, GRASS_TINT); n++; }
    if (n > 0) {
      bc.markNeedsSaving();
      @WCH@ wc = (@WCH@) s.getComponent(r, @WCH@.getComponentType());
      if (wc != null) wc.markNeedsSaving();
      try { w.getNotificationHandler().updateChunkTints(idx); } catch (Throwable t2) { }
    }
  } catch (Throwable t) { }
  return n;
}""")
# paint: blocks that differ are set; a crop only where the block is AIR (a growing / ripe crop is never reset)
M(fill, r"""
public static int paint(@WLD@ w, java.util.ArrayList want) {
  int n = 0;
  for (int i = 0; i < want.size(); i++) {
    int[] b = (int[]) want.get(i);
    String id = @PKG@.ShGeo.IDS[b[3]];
    String cur = idAt(w, b[0], b[1], b[2]);
    if (cur == null) continue;
    if (b[3] == @PKG@.ShGeo.CROP) { if (cur.length() == 0) n += put(w, b[0], b[1], b[2], id); continue; }
    if (b[3] == @PKG@.ShGeo.STAND) { if (cur.indexOf(id) < 0) n += put(w, b[0], b[1], b[2], id); continue; }
    if (!id.equals(cur)) n += put(w, b[0], b[1], b[2], id);
  }
  return n;
}""")
M(fill, r"""
public void run() {
  int n = 0;
  try {
    n = paint(this.world, this.want);
    if (n > 0 && !this.cropsOnly) {
      for (int i = 0; i < @PKG@.ShGeo.CX.length; i++) {
        long idx = @CHU@.indexChunk(@PKG@.ShGeo.CX[i], @PKG@.ShGeo.CZ[i]);
        tint(this.world, idx);
        try { this.world.getChunkLighting().invalidateLightInChunkSections(this.world.getChunkStore(), @PKG@.ShGeo.CX[i], @PKG@.ShGeo.CZ[i], 0, 10); } catch (Throwable t2) { }
      }
    }
    RUNS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard region fill failed in " + this.world.getName() + ": " + t); }
  this.placed = n;
  this.done.complete(this.world);
}""")
M(fill, r"""
public void accept(Object res, Object err) {
  if (err != null) @PKG@.ShCfg.warn("shard chunk load for " + this.world.getName() + " reported: " + err);
  try { this.world.execute(this); }
  catch (Throwable t) { @PKG@.ShCfg.warn("shard fill dispatch failed: " + t); this.done.complete(this.world); }
}""")
# any thread: load every chunk + section of the region (the engine queues it), then paint on the world thread; never hangs.
# cropsOnly = the periodic regrow (only crops on AIR, no tint / relight)
M(fill, r"""
public static java.util.concurrent.CompletableFuture paintAsync(@WLD@ w, java.util.Properties p, boolean cropsOnly) {
  java.util.concurrent.CompletableFuture done = new java.util.concurrent.CompletableFuture();
  try {
    java.util.ArrayList want;
    @PKG@.ShStore.LOCK.lock(); try { want = cropsOnly ? @PKG@.ShGeo.crops(p) : @PKG@.ShGeo.region(p); } finally { @PKG@.ShStore.LOCK.unlock(); }
    @CST@ cs = w.getChunkStore();
    int n = @PKG@.ShGeo.CX.length;
    java.util.concurrent.CompletableFuture[] parts = new java.util.concurrent.CompletableFuture[n * 2];
    for (int i = 0; i < n; i++) {
      parts[2 * i] = cs.getChunkReferenceAsync(@CHU@.indexChunk(@PKG@.ShGeo.CX[i], @PKG@.ShGeo.CZ[i]));
      parts[2 * i + 1] = cs.getChunkSectionReferenceAsync(@PKG@.ShGeo.CX[i], 3, @PKG@.ShGeo.CZ[i]);
    }
    @PKG@.ShFill job = new @PKG@.ShFill(w, want, done);
    job.cropsOnly = cropsOnly;
    java.util.concurrent.CompletableFuture.allOf(parts).whenComplete(job);
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard fill dispatch failed: " + t); done.complete(w); }
  return done;
}""")
M(fill, r"""
public static java.util.concurrent.CompletableFuture region(@WLD@ w, java.util.Properties p) {
  return paintAsync(w, p, false);
}""")

# ================= ShSay: chat lines (any thread) =================
say = mk("ShSay")
M(say, r"""
public static void to(@PR@ pr, String text, String col) {
  try { if (pr != null && pr.isValid()) pr.sendMessage(@MSG@.raw(text).color(col)); } catch (Throwable t) { }
}""")
M(say, r"""
public static void toPlayer(java.util.UUID u, String text, String col) {
  try { to(@UNI@.get().getPlayer(u), text, col); } catch (Throwable t) { }
}""")

# ================= ShWorlds: one world per profile - names, open (load / create), the cap + queue, idle unload =================
wld = mk("ShWorlds")
for f in ('public static final String PREFIX = "skyy-shard-";',
          "public static final java.util.concurrent.ConcurrentHashMap EMPTY_SINCE = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentHashMap OPENING = new java.util.concurrent.ConcurrentHashMap();",
          "public static final java.util.concurrent.ConcurrentLinkedQueue QUEUE = new java.util.concurrent.ConcurrentLinkedQueue();",
          "public static final java.util.concurrent.atomic.AtomicLong UNLOADS = new java.util.concurrent.atomic.AtomicLong();",
          "public static volatile java.util.ArrayList TEST_WORLDS = null;"):
    F(wld, f)
M(wld, "public static String name(String k) { return PREFIX + k; }")
M(wld, "public static boolean isShard(String n) { return n != null && n.startsWith(PREFIX) && n.length() > PREFIX.length(); }")
M(wld, "public static String ownerOf(String n) { return isShard(n) ? n.substring(PREFIX.length()) : null; }")
# the loaded shard worlds' names (TEST_WORLDS = the harness's stand-in)
M(wld, r"""
public static java.util.ArrayList loaded() {
  if (TEST_WORLDS != null) return new java.util.ArrayList(TEST_WORLDS);
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getWorlds().values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @WLD@)) continue;
      @WLD@ w = (@WLD@) o;
      if (w.isAlive() && isShard(w.getName())) out.add(w.getName());
    }
  } catch (Throwable t) { }
  return out;
}""")
# room for one more loaded shard world? (the opening ones count)
M(wld, r"""
public static boolean room(String name) {
  java.util.ArrayList l = loaded();
  if (l.contains(name)) return true;
  int n = l.size();
  java.util.Iterator it = OPENING.keySet().iterator();
  while (it.hasNext()) { Object k = it.next(); if (!l.contains(k) && !name.equals(k)) n++; }
  return n < @PKG@.ShCfg.MAX_LOADED;
}""")
M(wld, r"""
public static int queuePos(java.util.UUID u) {
  int i = 1;
  java.util.Iterator it = QUEUE.iterator();
  while (it.hasNext()) { if (u.equals(it.next())) return i; i++; }
  return -1;
}""")
M(wld, r"""
public static int enqueue(java.util.UUID u) {
  if (!QUEUE.contains(u)) QUEUE.add(u);
  return queuePos(u);
}""")
op = mk("ShOpened", None, ("java.util.function.BiConsumer",))
F(op, "public String n;")
C(op, "public ShOpened(String n) { this.n = n; }")
M(op, r"""
public void accept(Object res, Object err) {
  @PKG@.ShWorlds.OPENING.remove(this.n);
  if (err != null) @PKG@.ShCfg.warn("shard world " + this.n + " did not open: " + err);
}""")

# any thread: the loaded world, else load the saved folder (0.7: loadWorld - addWorld throws on an existing folder, probe S2), else
# make it from our template (spawnInstance). null = no room (the caller queues the player).
M(wld, r"""
public static java.util.concurrent.CompletableFuture open(String k, @WLD@ from) {
  String n = name(k);
  @UNI@ uni = @UNI@.get();
  @WLD@ w = uni.getWorld(n);
  if (w != null && w.isAlive()) { EMPTY_SINCE.remove(n); return java.util.concurrent.CompletableFuture.completedFuture(w); }   // fix: an Enter restarts the idle clock
  Object busy = OPENING.get(n);
  if (busy instanceof java.util.concurrent.CompletableFuture) return (java.util.concurrent.CompletableFuture) busy;
  if (!room(n)) return null;
  java.util.concurrent.CompletableFuture f;
  if (uni.isWorldLoadable(n)) f = uni.loadWorld(n);
  else f = @INS@.get().spawnInstance("SkyyShard", n, from, new @TRF@(%s, %s, %s, 0.0f, 0.0f, 0.0f));
  OPENING.put(n, f);
  f.whenComplete(new @PKG@.ShOpened(n));
  return f;
}""" % (ARRIVE[0], ARRIVE[1], ARRIVE[2]))
# the 1 s tick (scheduler thread): unload shard worlds empty for shard.unloadSec - at most UNLOAD_PER_TICK a tick (the engine loads every
# world folder at start, so they all fall due together; removeWorld ~75 ms each on the shared scheduler thread, probe S1); tell the first
# queued player when there is room
F(wld, "public static volatile int UNLOAD_PER_TICK = 2;")
M(wld, r"""
public static int idle(long now) {
  int unloaded = 0;
  int tried = 0;
  java.util.ArrayList l = loaded();
  for (int i = 0; i < l.size(); i++) {
    String n = (String) l.get(i);
    @WLD@ w = TEST_WORLDS != null ? null : @UNI@.get().getWorld(n);
    int players = 0;
    try { players = w == null ? 0 : w.getPlayerCount(); } catch (Throwable t) { players = 1; }
    if (players > 0 || OPENING.containsKey(n)) { EMPTY_SINCE.remove(n); continue; }
    Object s = EMPTY_SINCE.get(n);
    if (s == null) { EMPTY_SINCE.put(n, Long.valueOf(now)); continue; }
    if (now - ((Long) s).longValue() < 1000L * (long) @PKG@.ShCfg.UNLOAD_SEC) continue;
    if (tried >= UNLOAD_PER_TICK) continue;   // the rest wait for the next tick (still due)
    tried++;
    EMPTY_SINCE.remove(n);
    boolean ok = false;
    try { ok = TEST_WORLDS != null ? TEST_WORLDS.remove(n) : @UNI@.get().removeWorld(n); } catch (Throwable t) { @PKG@.ShCfg.warn("could not unload " + n + ": " + t); }
    if (ok) { unloaded++; UNLOADS.incrementAndGet(); @PKG@.ShCfg.info("unloaded " + n + " (empty for " + @PKG@.ShCfg.UNLOAD_SEC + " s; its folder stays)"); }
  }
  java.util.Iterator it = EMPTY_SINCE.keySet().iterator();
  while (it.hasNext()) { if (!l.contains(it.next())) it.remove(); }
  if (!QUEUE.isEmpty() && room("")) {
    java.util.UUID u = (java.util.UUID) QUEUE.poll();
    if (u != null) @PKG@.ShSay.toPlayer(u, "[Shards] A shard place is free now - open your shard menu and press Enter Shard.", "#39f493");
  }
  return unloaded;
}""")
# ================= ShRole: who may do what (SkyyIslands bridge; spec 9.1 + G8) =================
role = mk("ShRole")
F(role, "public static volatile java.util.function.Function ROLE_TEST;")
F(role, "public static volatile java.util.function.Function OWNER_TEST;")
F(role, "public static volatile java.util.function.Function ROLEKEY_TEST;")
F(role, "public static volatile java.util.function.Function STATE_TEST;")
F(role, "public static volatile java.util.function.Function WORLDKEY_TEST;")
F(role, "public static volatile java.util.function.Function WORLD_TEST;")
# the island owner's profile key of an island world (SkyyIslands island:owner:fn) or null
M(role, r"""
public static String islandOwner(String world) {
  try {
    java.util.function.Function f = OWNER_TEST != null ? OWNER_TEST : @PKG@.ShCfg.fn("island:owner:fn");
    Object r = f == null ? null : f.apply(world);
    return r instanceof String && ((String) r).length() > 0 ? (String) r : null;
  } catch (Throwable t) { return null; }
}""")
# the player's role on an island world: owner | admin | member | trusted | visitor | banned | null
M(role, r"""
public static String onIsland(java.util.UUID u, String world) {
  try {
    java.util.function.Function f = ROLE_TEST != null ? ROLE_TEST : @PKG@.ShCfg.fn("island:role:fn");
    Object r = f == null ? null : f.apply(new Object[] { u, world });
    return r instanceof String ? (String) r : null;
  } catch (Throwable t) { return null; }
}""")
# the player's role on the island of an owner KEY (SkyyIslands 0.5.8 island:role:key:fn) - used inside the shard world
M(role, r"""
public static String ofKey(java.util.UUID u, String key) {
  try {
    java.util.function.Function f = ROLEKEY_TEST != null ? ROLEKEY_TEST : @PKG@.ShCfg.fn("island:role:key:fn");
    Object r = f == null ? null : f.apply(new Object[] { u, key });
    return r instanceof String ? (String) r : null;
  } catch (Throwable t) { return null; }
}""")
# fix (critic): the owner profile is deleted (pending, undo window) or archived (SkyyProfiles profile:fn:state) = closed to co-op
M(role, r"""
public static boolean closed(String key) {
  try {
    java.util.function.Function f = STATE_TEST != null ? STATE_TEST : @PKG@.ShCfg.fn("profile:fn:state");
    Object r = f == null || key == null ? null : f.apply(key);
    return "pending".equals(r) || "archived".equals(r);
  } catch (Throwable t) { return false; }
}""")
# fix (critic): the owner key's CURRENT island world (SkyyIslands 0.5.8 island:world:key:fn) or null (unknown / no bridge)
M(role, r"""
public static String currentWorld(String key) {
  try {
    java.util.function.Function f = WORLDKEY_TEST != null ? WORLDKEY_TEST : @PKG@.ShCfg.fn("island:world:key:fn");
    Object r = f == null || key == null ? null : f.apply(key);
    return r instanceof String && ((String) r).length() > 0 ? (String) r : null;
  } catch (Throwable t) { return null; }
}""")
# does a world exist (loaded or saved on disk)? any doubt = yes (WORLD_TEST = the harness's stand-in)
M(role, r"""
public static boolean exists(String name) {
  try {
    if (WORLD_TEST != null) return !Boolean.FALSE.equals(WORLD_TEST.apply(name));
    @UNI@ u = @UNI@.get();
    if (u == null) return true;
    return u.getWorld(name) != null || u.isWorldLoadable(name);
  } catch (Throwable t) { return true; }
}""")
# fix (critic): is a "placed" record (world|x|y|z) of owner `key` stale? its world is not the owner's current island (an island reset
# keeps the old world on disk as a backup) - or, without the island:world:key:fn bridge, the world is gone
M(role, r"""
public static boolean stale(String placed, String key) {
  if (placed == null) return false;
  int bar = placed.indexOf('|');
  if (bar <= 0) return false;
  String pw = placed.substring(0, bar);
  String cur = currentWorld(key);
  if (cur != null) return !cur.equals(pw);
  return !exists(pw);
}""")
M(role, r"""
public static boolean coop(String r) {
  return "owner".equals(r) || "admin".equals(r) || "member".equals(r);
}""")
# may this player be inside the shard world of `key`? (owner profile, co-op, server admin)
M(role, r"""
public static boolean mayBeIn(java.util.UUID u, String key) {
  if (u == null || key == null) return false;
  if (key.equals(@PKG@.ShCfg.pkey(u))) return true;
  if (@PKG@.ShCfg.isAdmin(u)) return true;
  if (closed(key)) return false;   // fix (critic): no co-op in a deleted / archived profile's shard
  return coop(ofKey(u, key));
}""")
# fix (critic): may this player Collect / buy storage / Grow in the shard of `key`? the owner profile; co-op only with shard.coopCollect
M(role, r"""
public static boolean mayManage(java.util.UUID u, String key) {
  if (u == null || key == null) return false;
  if (key.equals(@PKG@.ShCfg.pkey(u))) return true;
  if (!@PKG@.ShCfg.COOP_COLLECT || closed(key)) return false;
  return coop(ofKey(u, key));
}""")
# SkyyIslands 0.5.8+ guards shard worlds (island:shardguard) - never open one unguarded
M(role, r"""
public static boolean guarded() {
  return "1".equals(String.valueOf(@PKG@.ShCfg.bridge().get("island:shardguard")));
}""")

# ================= ShGate: shard:fn:allowed (SkyyIslands 0.5.8's guards ask it for every action in a shard world) =================
gate = mk("ShGate", None, ("java.util.function.Function",))
F(gate, "public static final java.util.concurrent.atomic.AtomicLong ASKED = new java.util.concurrent.atomic.AtomicLong();")
C(gate, "public ShGate() { }")
M(gate, r"""
public static boolean crop(String id) {
  return id != null && id.indexOf("Plant_Crop_") >= 0;
}""")
M(gate, r"""
public static Boolean allowed(String world, String action, String block) {
  if (!@PKG@.ShWorlds.isShard(world)) return null;
  ASKED.incrementAndGet();
  String a = action == null ? "" : action;
  if (a.equals("break") || a.equals("damage")) return Boolean.valueOf(crop(block));
  if (a.equals("use")) return Boolean.valueOf(crop(block) || (block != null && block.indexOf("@SHARD@") >= 0));
  if (a.equals("pickup") || a.equals("drop")) return Boolean.TRUE;
  return Boolean.FALSE;
}""".replace("@SHARD@", SHARD_ITEM))
M(gate, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 2 || a[0] == null) return null;
    return allowed(String.valueOf(a[0]), a[1] == null ? null : String.valueOf(a[1]), a.length > 2 && a[2] != null ? String.valueOf(a[2]) : "");
  } catch (Throwable t) { return Boolean.FALSE; }
}""")

# ================= ShInv: count / give / take plain items (storage, hotbar, backpack; every move counted before and after) =================
inv = mk("ShInv")
M(inv, r"""
public static int countIn(@IC@ c, String id) {
  if (c == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short i = 0; i < cap; i++) {
    @IS@ it = c.getItemStack(i);
    if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n += it.getQuantity();
  }
  return n;
}""")
M(inv, r"""
public static @IC@[] containers(@ST@ st, @REF@ ref) {
  try {
    @PLA@ pl = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ in = pl == null ? null : pl.getInventory();
    if (in == null) return null;
    return new @IC@[] { in.getStorage(), in.getHotbar(), in.getBackpack() };
  } catch (Throwable t) { return null; }
}""")
M(inv, r"""
public static long count(@IC@[] cs, String id) {
  if (cs == null) return 0L;
  long n = 0L;
  for (int i = 0; i < cs.length; i++) n += (long) countIn(cs[i], id);
  return n;
}""")
# give up to qty (stacks of 100), storage first; returns what really arrived (counted)
M(inv, r"""
public static long give(@IC@[] cs, String id, long qty) {
  if (cs == null || qty <= 0L) return 0L;
  long added = 0L;
  for (int i = 0; i < cs.length && added < qty; i++) {
    if (cs[i] == null) continue;
    while (added < qty) {
      int chunk = (int) Math.min(100L, qty - added);
      int before = countIn(cs[i], id);
      try { cs[i].addItemStack(new @IS@(id, chunk)); } catch (Throwable t) { @PKG@.ShCfg.warnOnce("give:" + id, "could not give " + id + ": " + t); }
      int after = countIn(cs[i], id);
      int got = after - before;
      if (got > 0) added += (long) got;
      if (got < chunk) break;
    }
  }
  return added > qty ? qty : added;
}""")
# take exactly qty plain items (slot by slot, counted); returns what was really taken
M(inv, r"""
public static long take(@IC@[] cs, String id, long qty) {
  if (cs == null || qty <= 0L) return 0L;
  long taken = 0L;
  for (int i = 0; i < cs.length && taken < qty; i++) {
    @IC@ c = cs[i];
    if (c == null) continue;
    short cap = c.getCapacity();
    for (short s = 0; s < cap && taken < qty; s++) {
      @IS@ it = c.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      int want = (int) Math.min((long) it.getQuantity(), qty - taken);
      int before = countIn(c, id);
      try { c.removeItemStackFromSlot(s, want); } catch (Throwable t) { @PKG@.ShCfg.warnOnce("take:" + id, "could not take " + id + ": " + t); }
      int after = countIn(c, id);
      if (before > after) taken += (long) (before - after);
    }
  }
  return taken;
}""")

# ================= ShPay: coins, XP, collections (bridges; java.lang types only) =================
pay = mk("ShPay")
F(pay, "public static volatile java.util.Map TEST_FNS = null;")
M(pay, r"""
public static java.util.function.Function f(String key) {
  java.util.Map t = TEST_FNS;
  if (t != null) { Object o = t.get(key); return o instanceof java.util.function.Function ? (java.util.function.Function) o : null; }
  return @PKG@.ShCfg.fn(key);
}""")
M(pay, r"""
public static long coins(java.util.UUID u) {
  try {
    java.util.function.Function g = f("coins:fn:get");
    Object r = g == null ? null : g.apply(u);
    return r instanceof Number ? ((Number) r).longValue() : -1L;
  } catch (Throwable t) { return -1L; }
}""")
M(pay, r"""
public static boolean takeCoins(java.util.UUID u, long n) {
  if (n <= 0L) return true;
  try {
    java.util.function.Function g = f("coins:fn:take");
    if (g == null) return false;
    return Boolean.TRUE.equals(g.apply(new Object[] { u, Long.valueOf(n) }));
  } catch (Throwable t) { return false; }
}""")
# fix (critic): a refund (coins:fn:add, Object[]{UUID, Long delta} -> Long new balance); true = paid
M(pay, r"""
public static boolean addCoins(java.util.UUID u, long n) {
  if (n <= 0L) return true;
  try {
    java.util.function.Function g = f("coins:fn:add");
    if (g == null) return false;
    return g.apply(new Object[] { u, Long.valueOf(n) }) instanceof Number;
  } catch (Throwable t) { return false; }
}""")
M(pay, r"""
public static int collTier(java.util.UUID u, String coll) {
  try {
    java.util.function.Function g = f("coll:fn:tier");
    Object r = g == null ? null : g.apply(new Object[] { u, coll });
    return r instanceof Number ? ((Number) r).intValue() : -1;
  } catch (Throwable t) { return -1; }
}""")
M(pay, r"""
public static boolean xp(java.util.UUID u, long n) {
  if (n <= 0L) return true;
  try {
    java.util.function.Function g = f("skill:fn:addxp");
    if (g == null) return false;
    return Boolean.TRUE.equals(g.apply(new Object[] { u, "Farming", Long.valueOf(n), "shard:farming", @PKG@.ShCfg.pkey(u) }));
  } catch (Throwable t) { return false; }
}""")
# credit n of item to the collector's collection in chunks of 256; returns what was credited (stops at the first refusal)
M(pay, r"""
public static long coll(java.util.UUID u, String item, long n) {
  long done = 0L;
  try {
    java.util.function.Function g = f("coll:fn:add");
    if (g == null) return 0L;
    String k = @PKG@.ShCfg.pkey(u);
    while (done < n) {
      long c = Math.min(256L, n - done);
      if (!Boolean.TRUE.equals(g.apply(new Object[] { u, item, Long.valueOf(c), "shard", k }))) break;
      done += c;
    }
  } catch (Throwable t) { }
  return done;
}""")

# ================= ShWorld2: enter / leave / repaint / sweep / particles (world threads) =================
w2 = mk("ShWorld2")
hop = mk("ShHop", None, ("java.lang.Runnable", "java.util.function.BiConsumer"))
F(hop, "public @REF@ ref;")
F(hop, "public @WLD@ from;")
F(hop, "public @WLD@ to;")
F(hop, "public @TRF@ where;")
F(hop, "public java.util.UUID u;")
F(hop, "public String key;")
C(hop, "public ShHop(@REF@ r, @WLD@ f, @TRF@ where, java.util.UUID u, String key) { this.ref = r; this.from = f; this.where = where; this.u = u; this.key = key; }")
M(hop, r"""
public void run() {
  try {
    if (this.ref == null || !this.ref.isValid()) return;
    if (this.to == null || !this.to.isAlive()) { @PKG@.ShSay.toPlayer(this.u, "[Shards] Your shard closed while it was opening - press Enter Shard again.", "#ff6b6b"); return; }
    @ST@ st = this.ref.getStore();
    if (st == null) return;
    ((@CA@) st).addComponent(this.ref, @TP@.getComponentType(), @TP@.createForPlayer(this.to, this.where));
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard teleport failed: " + t); }
}""")
# the shard world is open (any thread): paint the region, then hop to the player's world thread for the teleport
M(hop, r"""
public void accept(Object res, Object err) {
  try {
    if (err != null || !(res instanceof @WLD@)) { @PKG@.ShSay.toPlayer(this.u, "[Shards] Your shard could not be opened - try again in a minute.", "#ff6b6b"); return; }
    this.to = (@WLD@) res;
    if (this.key != null) {
      java.util.Properties p = @PKG@.ShStore.get(this.key);
      if (p != null) { this.key = null; @PKG@.ShFill.region(this.to, p).whenComplete(this); return; }
    }
    if (this.from == null || !this.from.isAlive()) return;
    this.from.execute(this);
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard enter failed: " + t); }
}""")
M(w2, r"""
public static @TRF@ arrival() {
  return new @TRF@(%s, %s, %s, 0.0f, 0.0f, 0.0f);
}""" % ARRIVE)
# Enter: called on the player's world thread from the menu. "+..." = on the way, "-..." refused, "=..." queued
M(w2, r"""
public static String enter(@ST@ st, @REF@ ref, java.util.UUID u, String k, @WLD@ from) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (!@PKG@.ShRole.guarded()) return "-Shard worlds need SkyyIslands 0.5.8 or newer (it protects them) - ask an admin.";
  if (!@PKG@.ShRole.mayBeIn(u, k)) return "-Only the island owner and co-op members can enter this shard.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (from != null && from.getName().equals(@PKG@.ShWorlds.name(k))) return "=You are already in this shard.";
  String placed;   // fix (critic): only a PLACED shard opens (no world for a profile without one; a reset island's old portal does not count)
  @PKG@.ShStore.LOCK.lock(); try { placed = @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed"); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (placed.length() == 0 || !@PKG@.ShMath.owned(p)) return "-No Farming Shard is placed. Place it on your island first - the shard opens from there.";
  if (@PKG@.ShRole.stale(placed, k)) return "-Your island was reset, so the shard portal is gone. Use Pick up Shard in this menu to get it back, then place it again.";
  java.util.concurrent.CompletableFuture f = @PKG@.ShWorlds.open(k, from);
  if (f == null) {
    int pos = @PKG@.ShWorlds.enqueue(u);
    return "=Every shard place is busy (" + @PKG@.ShCfg.MAX_LOADED + " loaded). You are number " + pos + " in the queue - you will be told when it is free.";
  }
  @PKG@.ShWorlds.QUEUE.remove(u);
  f.whenComplete(new @PKG@.ShHop(ref, from, arrival(), u, k));
  return "+Opening your Farming Shard...";
}""")
M(w2, r"""
public static boolean hub(@ST@ st, @REF@ ref, java.util.UUID u) {
  try {   // fix2: the REAL hub first (SkyyIslands 0.5.8 island:fn:hub = /sethub; this player's own world thread)
    java.util.function.Function hf = @PKG@.ShCfg.fn("island:fn:hub");
    if (hf != null && u != null && Boolean.TRUE.equals(hf.apply(u))) return true;
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("hubfn", "island:fn:hub failed - using the default world spawn (logged once): " + t); }
  try {
    @WLD@ d = @UNI@.get().getDefaultWorld();
    if (d == null) return false;
    java.util.concurrent.CompletableFuture f = d.getWorldConfig().getSpawnProvider().getSpawnPointAsync(d, u);
    Object o = f == null ? null : f.getNow(null);
    if (!(o instanceof @TRF@)) return false;
    ((@CA@) st).addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(d, (@TRF@) o));
    return true;
  } catch (Throwable t) { return false; }
}""")
# Back to the island: the portal's island world (loaded) at the portal, else the hub (default world spawn)
M(w2, r"""
public static String leave(@ST@ st, @REF@ ref, java.util.UUID u, String k) {
  java.util.Properties p = @PKG@.ShStore.get(k);
  String placed = p == null ? "" : @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed");
  @UNI@ uni = @UNI@.get();
  try {
    if (placed.length() > 0 && !@PKG@.ShRole.stale(placed, k)) {   // fix (critic): never back into a reset island's old (backup) world
      String[] a = placed.split("\\|");
      if (a.length == 4) {
        @WLD@ w = uni.getWorld(a[0]);
        if (w != null && w.isAlive()) {
          @TRF@ t = new @TRF@(Double.parseDouble(a[1]) + 0.5, Double.parseDouble(a[2]) + 1.0, Double.parseDouble(a[3]) + 1.5, 0.0f, 0.0f, 0.0f);
          ((@CA@) st).addComponent(ref, @TP@.getComponentType(), @TP@.createForPlayer(w, t));
          return "+Back to your island.";
        }
      }
    }
    if (hub(st, ref, u)) return "+Your island is not loaded - sent to the hub (use /island).";
  } catch (Throwable t) { @PKG@.ShCfg.warn("leave failed: " + t); }
  return "-Could not leave the shard - use /island or /hub.";
}""")
# the periodic regrow (ShTick, every shard.regrowSec while someone is inside): crops on AIR only
M(w2, r"""
public static boolean regrow(String k) {
  try {
    @WLD@ w = @UNI@.get().getWorld(@PKG@.ShWorlds.name(k));
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (w == null || !w.isAlive() || p == null) return false;
    @PKG@.ShFill.paintAsync(w, p, true);
    return true;
  } catch (Throwable t) { return false; }
}""")
# paint the profile's whole region again if its shard world is loaded (after Grow)
M(w2, r"""
public static boolean repaint(String k) {
  try {
    @WLD@ w = @UNI@.get().getWorld(@PKG@.ShWorlds.name(k));
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (w == null || !w.isAlive() || p == null) return false;
    @PKG@.ShFill.region(w, p);
    return true;
  } catch (Throwable t) { return false; }
}""")

# ================= ShCore: the actions (world thread; every one re-checks its rules) =================
core = mk("ShCore")
F(core, 'public static final String ITEM = "%s";' % CROP["item"])
F(core, 'public static final String ENCH = "%s";' % CROP["ench"])
F(core, 'public static final String SEED = "%s";' % CROP["seed"])
F(core, 'public static final String COLL = "%s";' % CROP["coll"])
F(core, 'public static final String SHARD = "%s";' % SHARD_ITEM)
F(core, "public static volatile long NOW_TEST = 0L;")
F(core, "public static final java.util.concurrent.ConcurrentHashMap MEM_OWED = new java.util.concurrent.ConcurrentHashMap();")
# fix2: what waits in memory when the collector's file cannot be read (key "<pkey>|<owed key>") - taken once, never twice
M(core, r"""
public static long memTake(String ck, String key) {
  Object m = MEM_OWED.remove(ck + "|" + key);
  return m instanceof Long ? ((Long) m).longValue() : 0L;
}""")
M(core, r"""
public static void memKeep(String ck, String key, long left, java.util.UUID u) {
  if (left <= 0L) return;
  Object o = MEM_OWED.get(ck + "|" + key);
  long had = o instanceof Long ? ((Long) o).longValue() : 0L;
  MEM_OWED.put(ck + "|" + key, Long.valueOf(had + left));
  @PKG@.ShCfg.warnOnce("memowed:" + ck, "the collector file of " + ck + " could not be read - " + key + " " + left + " waits in memory until the next Collect (collect.log)");
  @PKG@.ShStore.log(u + " " + ck + " " + key + " " + left + " WAITS IN MEMORY (collector file unreadable)");
}""")
M(core, "public static long now() { long t = NOW_TEST; return t > 0L ? t : System.currentTimeMillis(); }")
# the collection credit for `add` new items + whatever waited from earlier refusals (owed.coll.<item> in the COLLECTOR's file)
M(core, r"""
public static long owed(java.util.UUID u, long add) {
  String ck = @PKG@.ShCfg.pkey(u);
  java.util.Properties q = @PKG@.ShStore.get(ck);
  long due = add;
  String key = "owed.coll." + ITEM;
  due += memTake(ck, key);   // fix2
  if (q != null) { @PKG@.ShStore.LOCK.lock(); try { due += @PKG@.ShStore.lng(q, key, 0L); } finally { @PKG@.ShStore.LOCK.unlock(); } }
  if (due <= 0L) return 0L;
  long done = @PKG@.ShPay.coll(u, ITEM, due);
  long left = due - done;
  if (q == null) memKeep(ck, key, left, u);   // fix2: never dropped without a trace
  if (q != null) {
    @PKG@.ShStore.LOCK.lock(); try {
      long had = @PKG@.ShStore.lng(q, key, 0L);
      if (left != had) {
        if (left > 0L) q.setProperty(key, String.valueOf(left)); else q.remove(key);
        String e = @PKG@.ShStore.save(ck, q);
        if (e != null) @PKG@.ShCfg.warn("the waiting collection count could not be saved: " + e);
      }
    } finally { @PKG@.ShStore.LOCK.unlock(); }
  }
  return left;
}""")
# fix2: profile:busy:<uuid> = the live inventory may not belong to the active profile (tools/PROFILES-CONTRACT.md rule 5)
M(core, r"""
public static boolean busy(java.util.UUID u) {
  try { return u != null && Boolean.TRUE.equals(@PKG@.ShCfg.bridge().get("profile:busy:" + u)); } catch (Throwable t) { return false; }
}""")
# fix2: a placed record that went stale (the island was reset; its portal sits in the old backup world) pauses production the first time
# it is seen: settled up to now, then farming.paused = 1 (Pick up / placing again clears it as usual). The bridge is asked outside the lock.
M(core, r"""
public static boolean pauseStale(String k, java.util.Properties p) {
  if (k == null || p == null) return false;
  String placed;
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShMath.paused(p)) return false;
    placed = @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed");
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (placed.length() == 0 || !@PKG@.ShRole.stale(placed, k)) return false;
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShMath.paused(p) || !placed.equals(@PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed"))) return false;
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    @PKG@.ShMath.settleAll(p, now());
    p.setProperty(@PKG@.ShMath.K + ".paused", "1");
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warn("could not pause a reset island's shard: " + e); return false; }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShStore.log(k + " placed record " + placed + " is stale (island reset) - production paused until the shard is placed again");
  return true;
}""")
# fix (critic): who may Collect / buy / Grow here (re-checked at every action, not only at Enter): null = yes, else the refusal line
M(core, r"""
public static String gate(java.util.UUID u, String k, java.util.Properties p) {
  if (busy(u)) return "-Your profile is still loading - try again in a moment.";   // fix2: PROFILES-CONTRACT rule 5
  pauseStale(k, p);   // fix2: a portal left in a reset island makes nothing
  if (!@PKG@.ShRole.mayBeIn(u, k)) return "-Only the island owner and co-op members can use this shard.";
  if (!@PKG@.ShRole.mayManage(u, k)) return "-Only the island owner can collect and upgrade this shard.";
  boolean own;
  @PKG@.ShStore.LOCK.lock(); try { own = @PKG@.ShMath.owned(p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (!own) return "-No Farming Shard yet - it comes from the hub quest line.";
  return null;
}""")
# fix (critic): Farming XP for `add` items' worth + whatever waited (owed.xp in the COLLECTOR's file); returns what still waits (-1 = nothing due)
M(core, r"""
public static long owedXp(java.util.UUID u, long add) {
  String ck = @PKG@.ShCfg.pkey(u);
  java.util.Properties q = @PKG@.ShStore.get(ck);
  long due = add;
  String key = "owed.xp";
  due += memTake(ck, key);   // fix2
  if (q != null) { @PKG@.ShStore.LOCK.lock(); try { due += @PKG@.ShStore.lng(q, key, 0L); } finally { @PKG@.ShStore.LOCK.unlock(); } }
  if (due <= 0L) return -1L;
  long left = @PKG@.ShPay.xp(u, due) ? 0L : due;
  if (q == null) memKeep(ck, key, left, u);   // fix2: never dropped without a trace
  if (q != null) {
    @PKG@.ShStore.LOCK.lock(); try {
      long had = @PKG@.ShStore.lng(q, key, 0L);
      if (left != had) {
        if (left > 0L) q.setProperty(key, String.valueOf(left)); else q.remove(key);
        String e = @PKG@.ShStore.save(ck, q);
        if (e != null) @PKG@.ShCfg.warn("the waiting Farming XP could not be saved: " + e);
      }
    } finally { @PKG@.ShStore.LOCK.unlock(); }
  }
  return left;
}""")
# Collect `slot` (-1 = every island) for player u from profile k's shard. Returns "+..." / "-..." (status line).
M(core, r"""
public static String collect(java.util.UUID u, String k, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read - ask an admin to look at the server log.";
  String no = gate(u, k, p);
  if (no != null) return no;
  long want = 0L; long given = 0L; long back = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    long now = now();
    @PKG@.ShMath.settleAll(p, now);
    long[] take = new long[@PKG@.ShMath.SLOTS];
    for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) {
      if (slot >= 0 && i != slot) continue;
      take[i] = @PKG@.ShMath.stored(p, i);
      want += take[i];
    }
    if (want <= 0L) return "=Nothing is stored there yet.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    for (int i = 0; i < take.length; i++) if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(i, "stored"), String.valueOf(@PKG@.ShMath.stored(p, i) - take[i]));
    p.setProperty("lastCollect", String.valueOf(now));   // fix2: the Collect tab's "Last collected ... ago"
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warn("Collect refused (debit not written): " + err); return "-Collect failed: the shard file could not be saved. Nothing was taken."; }
    given = @PKG@.ShInv.give(cs, ITEM, want);
    back = want - given;
    if (back > 0L) {
      for (int i = take.length - 1; i >= 0 && back > 0L; i--) {
        if (take[i] <= 0L) continue;
        long r = Math.min(take[i], back);
        p.setProperty(@PKG@.ShMath.ik(i, "stored"), String.valueOf(@PKG@.ShMath.stored(p, i) + r));
        back -= r;
      }
      back = want - given;
      String e2 = @PKG@.ShStore.save(k, p);
      if (e2 != null) @PKG@.ShCfg.warn("Collect: " + back + " items that did not fit are back in memory but not on disk yet: " + e2);
    }
    @PKG@.ShStore.log(u + " " + k + " slot " + slot + " debit " + want + " given " + given + " back " + back);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String extra = "";
  if (given > 0L) {
    long xp = given * (long) @PKG@.ShCfg.XP_WHEAT * (long) @PKG@.ShCfg.XP_PCT / 100L;
    long xpLeft = owedXp(u, xp);   // fix (critic): unpaid XP waits in the collector's file and is paid on a later Collect
    if (xpLeft > 0L) extra = extra + " (" + @PKG@.ShCfg.num(xpLeft) + " Farming XP waits - paid on your next Collect)";
    else if (xp > 0L) extra = extra + " +" + @PKG@.ShCfg.num(xp) + " Farming XP";
    long owedC = owed(u, given);
    if (owedC > 0L) extra = extra + " - " + @PKG@.ShCfg.num(owedC) + " Wheat collection count waiting";
  }
  if (given <= 0L) return "-Your inventory is full - nothing was collected.";
  return "+Collected " + @PKG@.ShCfg.num(given) + " Wheat" + extra + (back > 0L ? ". " + @PKG@.ShCfg.num(back) + " did not fit and stay in the shard." : ".");
}""")
# buy the next storage tier: items first (counted), then coins; items back when the coins fail
M(core, r"""
public static String buyStorage(java.util.UUID u, String k, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gate(u, k, p);
  if (no != null) return no;
  @PKG@.ShStore.LOCK.lock(); try {
    int t = @PKG@.ShMath.storageTier(p);
    if (t >= 5) return "=Storage is at the highest tier.";
    int nt = t + 1;
    long coins = @PKG@.ShCfg.storeCoins(nt);
    long ench = (long) @PKG@.ShCfg.storeEnch(nt);
    long have = @PKG@.ShInv.count(cs, ENCH);
    if (have < ench) return "-You need " + ench + " Enchanted Wheat (you have " + have + ").";
    long purse = @PKG@.ShPay.coins(u);
    if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
    long now = now();
    @PKG@.ShMath.settleAll(p, now);
    long got = @PKG@.ShInv.take(cs, ENCH, ench);
    if (got < ench) { @PKG@.ShInv.give(cs, ENCH, got); return "-The Enchanted Wheat could not be taken - nothing was bought."; }
    if (!@PKG@.ShPay.takeCoins(u, coins)) { long r = @PKG@.ShInv.give(cs, ENCH, got); @PKG@.ShStore.log(u + " " + k + " storage refund " + r + " of " + got + " " + ENCH); return "-The coins could not be taken - your Enchanted Wheat is back."; }
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    p.setProperty(@PKG@.ShMath.K + ".storage", String.valueOf(nt));
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {   // fix (critic): not saved = undone + everything paid goes back
      p.clear(); p.putAll(old);
      long ri = @PKG@.ShInv.give(cs, ENCH, got);
      boolean rc = @PKG@.ShPay.addCoins(u, coins);
      @PKG@.ShStore.log(u + " " + k + " storage " + t + " -> " + nt + " SAVE FAILED " + e + " - refund " + ri + " of " + got + " " + ENCH + ", coins " + (rc ? coins : 0L) + " of " + coins);
      @PKG@.ShCfg.warn("storage tier not saved, refunded: " + e);
      return "-The upgrade could not be saved - your Enchanted Wheat" + (rc ? " and coins are" : " is") + " back." + (rc ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
    }
    @PKG@.ShStore.log(u + " " + k + " storage " + t + " -> " + nt + " paid " + coins + " coins + " + got + " " + ENCH);
    return "+Storage is now tier " + nt + ": " + @PKG@.ShCfg.num(@PKG@.ShMath.cap(p)) + " items per island.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# grow an island one size (coins, Eternal Seeds, the crop collection tier); pasted at once if the shard world is loaded
M(core, r"""
public static String grow(java.util.UUID u, String k, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String no = gate(u, k, p);
  if (no != null) return no;
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!@PKG@.ShMath.hasIsland(p, slot)) return "-That slot has no island yet.";
    int sz = @PKG@.ShMath.size(p, slot);
    if (sz >= 3) return "=That island is fully grown.";
    long coins = sz == 1 ? (long) @PKG@.ShCfg.GM_COINS : (long) @PKG@.ShCfg.GL_COINS;
    long seeds = sz == 1 ? (long) @PKG@.ShCfg.GM_SEEDS : (long) @PKG@.ShCfg.GL_SEEDS;
    int need = sz == 1 ? @PKG@.ShCfg.GM_COLL : @PKG@.ShCfg.GL_COLL;
    int tier = @PKG@.ShPay.collTier(u, COLL);
    if (need > 0 && tier < need) return "-Needs Wheat collection " + need + " (you: " + (tier < 0 ? "?" : String.valueOf(tier)) + ").";
    long have = @PKG@.ShInv.count(cs, SEED);
    if (have < seeds) return "-You need " + seeds + " Eternal Wheat Seeds (you have " + have + ").";
    long purse = @PKG@.ShPay.coins(u);
    if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
    @PKG@.ShMath.settle(p, slot, now());
    long got = @PKG@.ShInv.take(cs, SEED, seeds);
    if (got < seeds) { @PKG@.ShInv.give(cs, SEED, got); return "-The seeds could not be taken - nothing was bought."; }
    if (!@PKG@.ShPay.takeCoins(u, coins)) { long r = @PKG@.ShInv.give(cs, SEED, got); @PKG@.ShStore.log(u + " " + k + " grow refund " + r + " of " + got + " " + SEED); return "-The coins could not be taken - your seeds are back."; }
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    p.setProperty(@PKG@.ShMath.ik(slot, "size"), String.valueOf(sz + 1));
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {   // fix (critic): not saved = undone + everything paid goes back
      p.clear(); p.putAll(old);
      long ri = @PKG@.ShInv.give(cs, SEED, got);
      boolean rc = @PKG@.ShPay.addCoins(u, coins);
      @PKG@.ShStore.log(u + " " + k + " grow slot " + slot + " SAVE FAILED " + e + " - refund " + ri + " of " + got + " " + SEED + ", coins " + (rc ? coins : 0L) + " of " + coins);
      @PKG@.ShCfg.warn("grow not saved, refunded: " + e);
      return "-The island could not be saved - your seeds" + (rc ? " and coins are" : " are") + " back." + (rc ? "" : " Ask an admin about the " + @PKG@.ShCfg.num(coins) + " coins (collect.log).");
    }
    @PKG@.ShStore.log(u + " " + k + " grow slot " + slot + " " + sz + " -> " + (sz + 1) + " paid " + coins + " coins + " + got + " " + SEED);
    res = "+The Wheat island grew to " + (sz == 1 ? "Medium" : "Large") + ".";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k);
  return res;
}""")

# ================= ShPlace: placing the shard item (PlaceBlockEvent) + the 1 s check that the block really landed =================
place = mk("ShPlace", T["EES"])
F(place, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")
F(place, "public static volatile java.util.function.Function BLOCK_TEST = null;")
C(place, "public ShPlace() { super(@PBE@.class); }")
M(place, "public @QRY@ getQuery() { return @ARCH@.empty(); }")
# does a world exist (loaded or saved on disk)? any doubt = yes (ShRole.WORLD_TEST = the harness's stand-in)
M(place, r"""
public static boolean worldExists(String name) {
  return @PKG@.ShRole.exists(name);
}""")
# the rules (pure; world thread): null = allowed and recorded (pending until the block is seen), else the refusal line
M(place, r"""
public static String decide(java.util.UUID u, String world, int x, int y, int z, long now) {
  if (!@PKG@.ShCfg.ON) return "Shards are switched off on this server.";
  if (@PKG@.ShWorlds.isShard(world)) return "A shard portal goes on your own island, not inside a shard.";
  String owner = @PKG@.ShRole.islandOwner(world);
  if (owner == null) return "Place your Farming Shard on your own island.";
  if (!owner.equals(@PKG@.ShCfg.pkey(u))) return "Only the island owner can place a shard here (on their current profile).";
  String cur = @PKG@.ShRole.currentWorld(owner);   // fix (critic): not in a reset island's old (backup) world
  if (cur != null && !cur.equals(world)) return "Place your Farming Shard on your current island.";
  java.util.Properties p = @PKG@.ShStore.get(owner);
  if (p == null) return "Your shard file could not be read - ask an admin to look at the server log.";
  @PKG@.ShStore.LOCK.lock(); try {
    String placed = @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed");
    if (@PKG@.ShRole.stale(placed, owner)) {   // fix (critic): the old portal's world is not the owner's current island (a reset keeps the old world as a backup) or is gone: forget it
      @PKG@.ShStore.log(owner + " placed record " + placed + " dropped (not the current island any more)");
      placed = "";
    }
    if (placed.length() > 0) return "Your Farming Shard is already placed (" + placed.replace('|', ' ') + "). Pick it up from its menu first.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    @PKG@.ShMath.starter(p, now);
    @PKG@.ShMath.settleAll(p, now);   // fix (critic): a paused (picked-up) shard made nothing meanwhile: its clocks start now
    p.remove(@PKG@.ShMath.K + ".paused");
    p.setProperty(@PKG@.ShMath.K + ".placed", world + "|" + x + "|" + y + "|" + z);
    String e = @PKG@.ShStore.save(owner, p);
    if (e != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warn("shard placement not saved: " + e); return "Your shard could not be saved - nothing was placed."; }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  PENDING.put(owner, new Object[] { world, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z), Long.valueOf(now), u, Integer.valueOf(0) });
  return null;
}""")
M(place, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @PBE@)) return;
    @PBE@ e = (@PBE@) ev;
    @IS@ hand = e.getItemInHand();
    if (hand == null || hand.isEmpty() || !"@SHARD@".equals(hand.getItemId())) return;
    if (e.isCancelled()) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (w == null || pr == null) { e.setCancelled(true); return; }
    @V3I@ b = e.getTargetBlock();
    String no = decide(pr.getUuid(), w.getName(), b.x, b.y, b.z, System.currentTimeMillis());
    if (no != null) { e.setCancelled(true); @PKG@.ShSay.to(pr, "[Shards] " + no, "#ff6b6b"); return; }
    // fix2: "placed" is said by the 1 s check once the block is really there (another rule may still cancel this event)
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard placement check failed: " + t); }
}""".replace("@SHARD@", SHARD_ITEM))
M(place, r"""
public static boolean unplace(String k, String where) {
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return false;
  @PKG@.ShStore.LOCK.lock(); try {
    if (!where.equals(@PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed"))) return false;
    @PKG@.ShMath.settleAll(p, @PKG@.ShCore.now());
    p.remove(@PKG@.ShMath.K + ".placed");
    p.setProperty(@PKG@.ShMath.K + ".paused", "1");
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) @PKG@.ShCfg.warn("could not undo a cancelled shard placement: " + e);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShCfg.info("shard placement at " + where + " for " + k + " was cancelled by another rule - record undone");
  return true;
}""")
# fix2: the placement's chat line, said once the check knows (seen = placed, gone = undone)
M(place, r"""
public static void told(Object[] a, boolean placed) {
  try {
    java.util.UUID u = (java.util.UUID) a[5];
    if (placed) @PKG@.ShSay.toPlayer(u, "[Shards] Your Farming Shard is placed. Right-click it to open the shard menu.", "#39f493");
    else @PKG@.ShSay.toPlayer(u, "[Shards] Your Farming Shard could not be placed there (another rule stopped it) - it is still in your inventory.", "#ff6b6b");
  } catch (Throwable t) { }
}""")
# fix2: the chunk was not loaded yet: check again (10 tries, 1 s apart); a newer placement of the same owner is never overwritten
M(place, r"""
public static boolean again(String k, Object[] a, long now) {
  int tries = a.length > 6 && a[6] instanceof Integer ? ((Integer) a[6]).intValue() : 0;
  if (tries >= 10) { @PKG@.ShCfg.info("shard placement " + a[0] + " for " + k + " could not be checked (chunk not loaded) - the record stays"); return false; }
  Object[] b = new Object[] { a[0], a[1], a[2], a[3], Long.valueOf(now), a[5], Integer.valueOf(tries + 1) };
  return PENDING.putIfAbsent(k, b) == null;
}""")
chk = mk("ShCheck", None, ("java.lang.Runnable",))
for f in ("public String k;", "public Object[] a;"):
    F(chk, f)
C(chk, "public ShCheck(String k, Object[] a) { this.k = k; this.a = a; }")
M(chk, r"""
public void run() {
  try {
    String wn = (String) this.a[0];
    int x = ((Integer) this.a[1]).intValue(); int y = ((Integer) this.a[2]).intValue(); int z = ((Integer) this.a[3]).intValue();
    @WLD@ w = @UNI@.get().getWorld(wn);
    if (w == null) return;
    String id = @PKG@.ShFill.idAt(w, x, y, z);
    if (id == null) { @PKG@.ShPlace.again(this.k, this.a, System.currentTimeMillis()); return; }   // fix2: checked again, not forgotten
    if (id.indexOf("@SHARD@") < 0) { if (@PKG@.ShPlace.unplace(this.k, wn + "|" + x + "|" + y + "|" + z)) @PKG@.ShPlace.told(this.a, false); }
    else @PKG@.ShPlace.told(this.a, true);
  } catch (Throwable t) { }
}""".replace("@SHARD@", SHARD_ITEM))

# 1 s later (scheduler): the block must be there (another guard may have cancelled the place) - else the record is undone
M(place, r"""
public static int verify(long now) {
  int undone = 0;
  java.util.Iterator it = PENDING.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry en = (java.util.Map.Entry) it.next();
    Object[] a = (Object[]) en.getValue();
    if (now - ((Long) a[4]).longValue() < 1000L) continue;
    it.remove();
    String k = (String) en.getKey();
    String wn = (String) a[0];
    int x = ((Integer) a[1]).intValue(); int y = ((Integer) a[2]).intValue(); int z = ((Integer) a[3]).intValue();
    if (BLOCK_TEST != null) {
      Object bt = BLOCK_TEST.apply(a);
      if (bt == null) { again(k, a, now); continue; }   // fix2: the harness's "chunk not loaded"
      if (!Boolean.TRUE.equals(bt)) { if (unplace(k, wn + "|" + x + "|" + y + "|" + z)) told(a, false); undone++; }
      else told(a, true);
      continue;
    }
    @WLD@ w = @UNI@.get().getWorld(wn);
    if (w == null || !w.isAlive()) continue;
    w.execute(new @PKG@.ShCheck(k, a));
  }
  return undone;
}""")
# ================= ShTick: 1 s scheduler tick - idle unload + queue, regrow, sweep, particles, pending placements =================
tick = mk("ShTick", None, ("java.lang.Runnable",))
sweep = mk("ShSweep", None, ("java.lang.Runnable",))
part = mk("ShParticles", None, ("java.lang.Runnable",))
F(tick, "public static final java.util.concurrent.ConcurrentHashMap LAST_REGROW = new java.util.concurrent.ConcurrentHashMap();")
F(tick, "public static final java.util.concurrent.atomic.AtomicLong TICKS = new java.util.concurrent.atomic.AtomicLong();")
F(tick, "public long n;")
C(tick, "public ShTick() { this.n = 0L; }")
F(sweep, "public @WLD@ w;")
C(sweep, "public ShSweep(@WLD@ w) { this.w = w; }")
# world thread: anyone in a shard world who may not be there goes to the hub
M(sweep, r"""
public void run() {
  try {
    String k = @PKG@.ShWorlds.ownerOf(this.w.getName());
    java.util.Iterator it = this.w.getPlayerRefs().iterator();
    while (it.hasNext()) {
      @PR@ pr = (@PR@) it.next();
      if (pr == null || !pr.isValid()) continue;
      if (@PKG@.ShRole.mayBeIn(pr.getUuid(), k)) continue;
      @REF@ r = pr.getReference();
      if (r == null || !r.isValid()) continue;
      if (@PKG@.ShWorld2.hub(r.getStore(), r, pr.getUuid())) @PKG@.ShSay.to(pr, "[Shards] This shard belongs to someone else's island - sent to the hub.", "#ffcc00");
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("sweep", "the shard sweep failed (logged once): " + t); }
}""")
F(part, "public @WLD@ w;")
F(part, "public static final java.util.concurrent.atomic.AtomicLong BURSTS = new java.util.concurrent.atomic.AtomicLong();")
C(part, "public ShParticles(@WLD@ w) { this.w = w; }")
M(part, r"""
public void run() {
  try {
    String k = @PKG@.ShWorlds.ownerOf(this.w.getName());
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null) return;
    long now = @PKG@.ShCore.now();
    for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) {
      boolean work;
      @PKG@.ShStore.LOCK.lock(); try {
        if (!@PKG@.ShMath.hasIsland(p, i) || @PKG@.ShMath.totems(p, i) <= 0) continue;
        @PKG@.ShMath.settle(p, i, now);
        work = @PKG@.ShMath.stored(p, i) < @PKG@.ShMath.cap(p);
      } finally { @PKG@.ShStore.LOCK.unlock(); }
      if (!work) continue;
      double[] s = @PKG@.ShGeo.totemSpot(i);
      @PTU@.spawnParticleEffect(@PKG@.ShCfg.particle(), (@V3DC@) new @V3D@(s[0], s[1], s[2]), (@CA@) this.w.getEntityStore().getStore());
      BURSTS.incrementAndGet();
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("particles", "totem particles failed (logged once): " + t); }
}""")
M(tick, r"""
public void run() {
  try {
    this.n++;
    TICKS.incrementAndGet();
    long now = System.currentTimeMillis();
    @PKG@.ShWorlds.idle(now);
    @PKG@.ShPlace.verify(now);
    java.util.ArrayList l = @PKG@.ShWorlds.loaded();
    for (int i = 0; i < l.size(); i++) {
      String nm = (String) l.get(i);
      @WLD@ w = @UNI@.get().getWorld(nm);
      if (w == null || !w.isAlive()) continue;
      int pc = 0;
      try { pc = w.getPlayerCount(); } catch (Throwable t) { pc = 0; }
      if (pc <= 0) continue;
      w.execute(new @PKG@.ShSweep(w));   // fix (critic): every second, not every 5 s (a removed co-op member / a profile switch)
      if (@PKG@.ShCfg.PART_SEC > 0 && this.n % (long) @PKG@.ShCfg.PART_SEC == 0L) w.execute(new @PKG@.ShParticles(w));
      Object last = LAST_REGROW.get(nm);
      if (last == null) { LAST_REGROW.put(nm, Long.valueOf(now)); continue; }
      if (now - ((Long) last).longValue() >= 1000L * (long) @PKG@.ShCfg.REGROW_SEC) {
        LAST_REGROW.put(nm, Long.valueOf(now));
        @PKG@.ShWorld2.regrow(@PKG@.ShWorlds.ownerOf(nm));
      }
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("tick", "the shard tick failed (logged once): " + t); }
}""")

# Pick up (portal view, owner, the portal's world thread): remove the block, give the item (counted), clear the record
M(core, r"""
public static String pickup(java.util.UUID u, String k, @WLD@ here, @IC@[] cs) {
  if (!k.equals(@PKG@.ShCfg.pkey(u))) return "-Only the island owner can pick up the shard.";
  if (busy(u)) return "-Your profile is still loading - try again in a moment.";   // fix2: PROFILES-CONTRACT rule 5
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  String placed = "";
  String[] a = null;
  int mode = 0;   // 0 = at the portal, 1 = the portal's island was reset (stale record), 2 = the portal block is gone
  int x = 0; int y = 0; int z = 0;
  String id = null;
  @PKG@.ShStore.LOCK.lock(); try {
    placed = @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed");
    a = placed.split("\\|");
    if (placed.length() == 0 || a.length != 4) return "-Your shard is not placed.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (@PKG@.ShRole.stale(placed, k)) mode = 1;   // fix (critic): after an island reset the old portal is out of reach - the shard comes back from any menu
  else {
    if (here == null || !here.getName().equals(a[0])) return "-Stand by your shard portal to pick it up.";
    x = Integer.parseInt(a[1]); y = Integer.parseInt(a[2]); z = Integer.parseInt(a[3]);
    id = @PKG@.ShFill.idAt(here, x, y, z);
    if (id == null) return "-Your shard portal's spot is not loaded - stand right by it and try again.";   // fix2: never two portals for one record
    mode = id.indexOf(SHARD) < 0 ? 2 : 0;
  }
  // the item first (counted), then the record (production paused) is written; a refused write takes the item back - never a shard twice
  @PKG@.ShStore.LOCK.lock(); try {
    if (!placed.equals(@PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed"))) return "-Your shard changed meanwhile - open the menu again.";
    long got = @PKG@.ShInv.give(cs, SHARD, 1L);
    if (got < 1L) return "-Make room in your inventory first.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    @PKG@.ShMath.settleAll(p, now());
    p.remove(@PKG@.ShMath.K + ".placed");
    p.setProperty(@PKG@.ShMath.K + ".paused", "1");
    String e = @PKG@.ShStore.save(k, p);
    if (e != null) {
      p.clear(); p.putAll(old);
      long back = @PKG@.ShInv.take(cs, SHARD, 1L);
      @PKG@.ShStore.log(u + " " + k + " pickup " + placed + " SAVE FAILED " + e + " - item taken back " + back);
      return "-Your shard could not be saved - nothing changed.";
    }
    @PKG@.ShStore.log(u + " " + k + " pickup " + placed + (mode == 1 ? " (island reset)" : (mode == 2 ? " (block gone)" : "")));
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (mode == 0 && id != null) @PKG@.ShFill.clear(here, x, y, z);
  if (mode == 1) return "+Your island was reset - your Farming Shard is back in your inventory. Place it on your island again. Its islands and storage are kept.";
  return "+Your Farming Shard is in your inventory. Its islands, storage and totems are kept.";
}""")

# ================= the page (tools/skyyui.py; inline only; ids SkyySh..., no underscores) =================
P = "SkyySh"
PW, PH = 1100, 860
sh = SUI.page_shell(P, PW, PH, title=SUI.J("this.title", "Farming Shard"), kind="decorated")
IW, IH = sh.inner_w, sh.inner_h
assert (IW, IH) == (1066, 788), (IW, IH)
G = SUI.COLOR
GOOD, BAD, INFO, GOLD, WARN, TEXT = G["success"], G["error"], G["info"], G["gold"], G["warning"], G["text"]
BODY = "#" + sh.body
J_ = SUI.J
SEG = {}          # segment name -> Appends (emitted inside a Java if-block)
ALL = SUI.Appends(sh.appends)


def seg(name):
    a = SUI.Appends()
    SEG[name] = a
    return a


# --- the summary strip (always)
STRIP_H = 84
base = sh.appends
base.append((BODY, SUI.panel(P + "Strip", "simple", w=IW, h=STRIP_H, layout="Left", pad=12)))
STRIP = "#" + P + "Strip"
base.append((STRIP, SUI.item_icon(P + "Icon", SHARD_ITEM, size=60)))
base.append((STRIP, SUI.spacer(w=12)))
base.append((STRIP, SUI.group(P + "Sum", layout="Top", w=480, h=60)))
base.text("#" + P + "Sum", P + "Sum1", J_("this.sum1", "1 island - 1 totem - 60 items / hour"), "bold", size=15, h=30, w=480)
base.text("#" + P + "Sum", P + "Sum2", J_("this.sum2", "Portal on your island"), "caption", size=13, h=26, w=480)
base.append((STRIP, SUI.group(P + "Sto", layout="Top", w=260, h=60)))
base.text("#" + P + "Sto", P + "Sto1", J_("this.sto1", "Storage 100 / 600 per island"), "default", size=14, h=30, w=260)
base.text("#" + P + "Sto", P + "Sto2", J_("this.sto2", "Full in 8 h 20 m"), "caption", size=13, h=26, w=260, col=J_("this.sto2c", GOOD))
base.append((STRIP, SUI.spacer(w=12)))
s_enter = seg("enter")
s_enter.append((STRIP, SUI.button(P + "Enter", "Enter Shard", "primary", w=200)))
s_back = seg("back")
s_back.append((STRIP, SUI.button(P + "Back", "Back to Island", "secondary", w=200)))
assert 60 + 12 + 480 + 260 + 12 + 200 <= IW - 24, "the strip is wider than the page"
# --- tabs
TABS = ["Collect", "Upgrades", "Islands", "Totems"]
TAB_IDS = [P + "Tab%d" % i for i in range(4)]
TAB_W = (IW - 3 * SUI.TAB_GAP) // 4
for t in range(4):
    a = seg("tabs%d" % t)
    a.extend(SUI.tab_row(BODY, P + "Tabs", TAB_IDS, TABS, t, w=TAB_W))
TAB_H = SUI.BTN_H + 2 * SUI.TAB_MARGIN
CH = IH - STRIP_H - TAB_H - 34 - 50
assert CH >= 520, CH
base2 = SUI.Appends()          # after the tab content: status + footer (always)
LW, RW = 700, IW - 700 - 14
assert RW == 352


def panel_pair(a, tag):
    a.append((BODY, SUI.group(P + tag, layout="Left", w=IW, h=CH)))
    a.append(("#" + P + tag, SUI.panel(P + tag + "L", "simple", w=LW, h=CH, layout="Top", pad=12)))
    a.append(("#" + P + tag, SUI.spacer(w=14)))
    a.append(("#" + P + tag, SUI.panel(P + tag + "R", "simple", w=RW, h=CH, layout="Top", pad=12)))
    return "#" + P + tag + "L", "#" + P + tag + "R"


ROWW = LW - 24
# --- Collect tab
c0 = seg("c0")
L0, R0 = panel_pair(c0, "C")
c0.append((L0, SUI.label(P + "CHead", "Stored in this shard", "panelTitle", h=30)))
c0.text(L0, P + "CCap", "Your islands make items while you are away. Collect them here.", "caption", h=24)
for i in range(SLOTS):
    a = seg("crow%d" % i)
    rid = P + "CRow%d" % i
    a.append((L0, SUI.panel(rid, "row", w=ROWW, h=56, layout="Left", pad={"left": 8, "right": 8}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.item_icon(rid + "Ic", CROP["item"], size=40, anchor={"top": 8})))
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=330, h=56)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.cName[%d]" % i, "Wheat Island 1 - Small"), "rowName", size=15, h=28, w=330)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.cSub[%d]" % i, "60 / hour - full in 8 h 20 m"), "rowSub", size=12, h=24, w=330)
    a.text("#" + rid, rid + "Am", J_("this.cAmt[%d]" % i, "1,200 / 2,400"), "bold", size=16, h=56, w=150, align="End")
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Collect", "secondary", "small", w=100, anchor={"top": 12})))
ce = seg("cempty")
ce.append((L0, SUI.panel(P + "CEmpty", "well", w=ROWW, h=120, layout="Top")))
ce.text("#" + P + "CEmpty", P + "CEmpty1", "Nothing to collect yet", "bold", h=30, align="Center", w=ROWW - 16)
ce.text("#" + P + "CEmpty", P + "CEmpty2", "Your islands are growing. Come back soon.", "caption", h=26, align="Center", w=ROWW - 16)
c1 = seg("c1")
c1.append((R0, SUI.label(P + "CAllHead", "Collect all", "panelTitle", h=30)))
for j, (samp, col) in enumerate((("1,200 items", None), ("+2,400 Farming XP", GOOD), ("Wheat collection +1,200", GOLD),
                                  ("Last collected 7 h 37 m ago", None), ("Inventory first. What does not fit stays here.", None),
                                  ("XP and collections are paid when you collect.", None))):
    c1.text(R0, P + "CAll%d" % j, J_("this.cAll[%d]" % j, samp), "default" if j < 3 else "caption", size=15 if j < 3 else 13,
            h=30 if j < 3 else 26, w=RW - 24, col=col, wrap=j >= 3)
c1.append((R0, SUI.spacer(h=40)))
c1.append((R0, SUI.button(P + "CAll", "Collect all", "primary", w=RW - 24)))
# --- Upgrades tab: three cards
u0 = seg("u0")
u0.append((BODY, SUI.group(P + "U", layout="Left", w=IW, h=CH)))
CW_ = (IW - 2 * 14) // 3
assert CW_ * 3 + 28 <= IW
for ci, (cid, ctitle) in enumerate((("Store", "Storage"), ("Comp", "Auto-Compactor"), ("Time", "Time Compressor"))):
    if ci:
        u0.append(("#" + P + "U", SUI.spacer(w=14)))
    u0.append(("#" + P + "U", SUI.panel(P + "U" + cid, "simple", w=CW_, h=CH, layout="Top", pad=12)))
    u0.text("#" + P + "U" + cid, P + "U" + cid + "T", ctitle, "panelTitle", h=30)
US = "#" + P + "UStore"
for j, (samp, kind, col) in enumerate((("Tier 1 of 5", "bold", GOLD), ("Now: 100 items per island", "default", None),
                                       ("Next: 300 items per island", "default", GOOD),
                                       ("Each island of this shard holds this many items. A full island stops making items.", "caption", None),
                                       ("Cost", "section", None), ("5,000 coins (you: 12,000)", "default", J_("this.uCol[5]", GOOD)),
                                       ("1 Enchanted Wheat (you: 0)", "default", J_("this.uCol[6]", BAD)))):
    u0.text(US, P + "UStore%d" % j, J_("this.uTx[%d]" % j, samp), kind, size=14 if kind != "caption" else 13,
            h=48 if j == 3 else 28, w=CW_ - 24, col=col, wrap=j == 3)
u0.append((US, SUI.spacer(h=24)))
ub = seg("ubuy")
ub.append((US, SUI.button(P + "UBuy", "Buy upgrade", "primary", w=CW_ - 24)))
for cid, txt in (("Comp", "Turns 100 wheat into 1 Enchanted Wheat while you are away."), ("Time", "Makes this shard produce faster.")):
    u0.text("#" + P + "U" + cid, P + "U" + cid + "D", txt, "caption", h=48, w=CW_ - 24, wrap=True)
    u0.text("#" + P + "U" + cid, P + "U" + cid + "L", "Coming in a later update.", "bold", h=30, w=CW_ - 24, col=WARN)
# --- Islands tab: the slot map (absolute) + the side panel
i0 = seg("i0")
i0.append((BODY, SUI.group(P + "I", layout="Left", w=IW, h=CH)))
i0.append(("#" + P + "I", SUI.panel(P + "IMap", "well", w=LW, h=CH, layout=None, pad=0)))
i0.append(("#" + P + "I", SUI.spacer(w=14)))
i0.append(("#" + P + "I", SUI.panel(P + "IR", "simple", w=RW, h=CH, layout="Top", pad=12)))
MAPC = (LW // 2, CH // 2 + 10)
SBW, SBH = 160, 56
HBW, HBH = 150, 44
_boxes = [("hub", MAPC[0] - HBW // 2, MAPC[1] - HBH // 2, HBW, HBH)]
i0.text("#" + P + "IMap", P + "IMapT", "Pick a slot to see its island. Islands grow in place; more crops come in a later update.", "caption", w=LW - 24, h=26,
        anchor={"left": 12, "top": 8})
_boxes.append(("title", 12, 8, LW - 24, 26))
i0.append(("#" + P + "IMap", SUI.panel(P + "IHub", "row", w=HBW, h=HBH, layout="Top", anchor={"left": MAPC[0] - HBW // 2, "top": MAPC[1] - HBH // 2})))
i0.append(("#" + P + "IHub", SUI.label(P + "IHubT", "Hub", "bold", w=HBW, h=HBH, align="Center")))
SLOT_UI = []
for i in range(SLOTS):
    ang = math.radians(-90 + 60 * i)
    cx_, cy_ = MAPC[0] + 245 * math.cos(ang), MAPC[1] + 190 * math.sin(ang)
    L_, T_ = int(round(cx_ - SBW / 2)), int(round(cy_ - SBH / 2))
    SLOT_UI.append((L_, T_))
    _boxes.append(("slot%d" % i, L_, T_, SBW, SBH))
for nm_, l_, t_, w_, h_ in _boxes:
    assert l_ >= 4 and t_ >= 4 and l_ + w_ <= LW - 4 and t_ + h_ <= CH - 4, "map box %s outside: %s" % (nm_, (l_, t_, w_, h_))
for a_ in range(len(_boxes)):
    for b_ in range(a_ + 1, len(_boxes)):
        A_, B_ = _boxes[a_], _boxes[b_]
        gx = max(B_[1] - (A_[1] + A_[3]), A_[1] - (B_[1] + B_[3]))
        gy = max(B_[2] - (A_[2] + A_[4]), A_[2] - (B_[2] + B_[4]))
        assert max(gx, gy) >= 8, "map boxes %s and %s touch" % (A_[0], B_[0])
for i in range(SLOTS):
    for state in ("normal", "selected"):
        a = seg("islot%d%s" % (i, state[0]))
        sid = P + "ISl%d" % i
        a.append(("#" + P + "IMap", SUI.group(sid + "Pos", layout="Left", w=SBW, h=SBH, anchor={"left": SLOT_UI[i][0], "top": SLOT_UI[i][1]}, bg="row")))
        a.append(("#" + sid + "Pos", SUI.hover_row(sid + "Sel", state, h=SBH, w=SBW, pad=8, sound="light")))
        a.append(("#" + sid + "Sel", SUI.group(sid + "Tx", layout="Top", w=SBW - 16, h=SBH)))
        a.text("#" + sid + "Tx", sid + "A", J_("this.sName[%d]" % i, "Slot 1 - Wheat"), "rowName", size=14, h=28, w=SBW - 16)
        a.text("#" + sid + "Tx", sid + "B", J_("this.sSub[%d]" % i, "Small"), "rowSub", size=12, h=22, w=SBW - 16)
IR = "#" + P + "IR"
i1 = seg("iside")
i1.text(IR, P + "IRT", J_("this.iTitle", "Slot 1 - Wheat Island"), "panelTitle", h=30, w=RW - 24)
for j, samp in enumerate(("Size: Small (13 x 13)", "Makes 60 items / hour", "Totems: 1 Harvest Spirit I", "Next: Medium (21 x 21)",
                          "Would make 96 items / hour", "Cost", "5,000 coins (you: 12,000)", "8 Eternal Wheat Seeds (you: 0)",
                          "Wheat collection 4 (you: 2)")):
    kind = "section" if j == 5 else "default"
    i1.text(IR, P + "IR%d" % j, J_("this.iTx[%d]" % j, samp), kind, size=14, h=28, w=RW - 24,
            col=J_("this.iCol[%d]" % j, TEXT) if j not in (5,) else None)
i1.append((IR, SUI.spacer(h=12)))
ig = seg("igrow")
ig.append((IR, SUI.button(P + "IGrow", "Grow island", "primary", w=RW - 24)))
# --- Totems tab
t0 = seg("t0")
L3, R3 = panel_pair(t0, "T")
t0.append((L3, SUI.label(P + "THead", "Totems in this shard", "panelTitle", h=30)))
t0.text(L3, P + "TCap", "Each totem works its island and fills its storage.", "caption", h=24)
for i in range(SLOTS):
    a = seg("trow%d" % i)
    rid = P + "TRow%d" % i
    a.append((L3, SUI.panel(rid, "row", w=ROWW, h=56, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=470, h=56)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.tName[%d]" % i, "Harvest Spirit I - Wheat Island 1"), "rowName", size=15, h=28, w=470)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.tSub[%d]" % i, "60 items / hour - kept in the shard until you collect"), "rowSub", size=12, h=24, w=470)
    a.text("#" + rid, rid + "St", J_("this.tSt[%d]" % i, "Working"), "bold", size=14, h=56, w=176, align="End", col=J_("this.tCol[%d]" % i, GOOD))
t1 = seg("tside")
t1.append((R3, SUI.label(P + "TRHead", "About totems", "panelTitle", h=30)))
for j, txt in enumerate(("A Harvest Spirit harvests the crops of its island and keeps them in the shard until you collect.",
                         "The island is bigger than the spirit's range, so you can farm the rest by hand.",
                         "New totems, tiers and upgrade slots come in a later update.")):
    t1.text(R3, P + "TR%d" % j, txt, "caption", h=72, w=RW - 24, wrap=True)
# --- status + footer (always)
base2.text(BODY, P + "Status", J_("this.stText", ""), "bold", size=15, h=30, w=IW, align="Center", col=J_("this.stCol", INFO), anchor={"top": 4})
base2.append((BODY, SUI.group(P + "Foot", layout="Left", w=IW, h=SUI.BTN_H, anchor={"top": 6})))
FOOT = "#" + P + "Foot"
s_pick = seg("pick")
s_pick.append((FOOT, SUI.button(P + "Pick", "Pick up Shard", "secondary", w=200)))
s_pick.append((FOOT, SUI.spacer(w=IW - 200 - 172)))
s_nopick = seg("nopick")
s_nopick.append((FOOT, SUI.spacer(w=IW - 172)))
base3 = SUI.Appends()
base3.append((FOOT, SUI.button(P + "Close", "Close", "secondary", w=172, sound="cancel")))
# the page check: every element of every segment together (ids unique, parents exist, kit-proven markup)
for a_ in list(SEG.values()) + [base2, base3]:
    ALL.extend(a_)
_seen_ids = {}
for _p, _mk in ALL:
    for _m in re.finditer(r"(?:Group|Label|TextButton|Button|ItemIcon) #([A-Za-z0-9]+)", SUI.render(_mk)):
        _seen_ids.setdefault(_m.group(1), []).append(_p)
# segments that are exclusive (tabs / slot states / enter-back / pick-nopick) legitimately repeat ids: check one coherent variant each
VARIANTS = []
for t in range(4):
    for sel in range(SLOTS):
        v = SUI.Appends(sh.appends)
        v.extend(SEG["enter"])
        v.extend(SEG["tabs%d" % t])
        if t == 0:
            for k_ in ["c0"] + ["crow%d" % i for i in range(SLOTS)] + ["c1"]:
                v.extend(SEG[k_])
        elif t == 1:
            v.extend(SEG["u0"]); v.extend(SEG["ubuy"])
        elif t == 2:
            v.extend(SEG["i0"])
            for i in range(SLOTS):
                v.extend(SEG["islot%d%s" % (i, "s" if i == sel else "n")])
            v.extend(SEG["iside"]); v.extend(SEG["igrow"])
        else:
            v.extend(SEG["t0"])
            for i in range(SLOTS):
                v.extend(SEG["trow%d" % i])
            v.extend(SEG["tside"])
        v.extend(base2)
        v.extend(SEG["pick"])
        v.extend(base3)
        VARIANTS.append(v)
        if t != 2:
            break
for v in VARIANTS:
    v.check(P)
SUI.assert_proven([mk_ for v in VARIANTS for mk_ in v.markups()], what="SkyyShards shard menu")


def jseg(name):
    return SEG[name].java("b")


def binds(ids_vals):
    return "\n".join('  ev.addEventBinding(@BT@.Activating, "#%s", @EVD@.of("a", "%s"));' % (i, v) for i, v in ids_vals)


BUILD_JAVA = "\n".join([
    sh.appends.java("b"),
    "  if (this.view == 1) {", jseg("back"), binds([(P + "Back", "back")]), "  } else {", jseg("enter"), binds([(P + "Enter", "enter")]), "  }",
    "  if (this.tab == 0) {", jseg("tabs0"), "  } else if (this.tab == 1) {", jseg("tabs1"), "  } else if (this.tab == 2) {", jseg("tabs2"),
    "  } else {", jseg("tabs3"), "  }",
    binds([(TAB_IDS[i], "tab%d" % i) for i in range(4)]),
    "  if (this.tab == 0) {", jseg("c0"),
    "    if (this.cN == 0) {", jseg("cempty"), "    }",
] + ["    if (this.cN > %d) {\n%s\n%s\n    }" % (i, jseg("crow%d" % i), binds([(P + "CRow%dBtn" % i, "col%d" % i)])) for i in range(SLOTS)] + [
    jseg("c1"), binds([(P + "CAll", "colall")]),
    "  } else if (this.tab == 1) {", jseg("u0"), "    if (this.uCan) {", jseg("ubuy"), binds([(P + "UBuy", "buy")]), "    }",
    "  } else if (this.tab == 2) {", jseg("i0"),
] + ["    if (this.sel == %d) {\n%s\n    } else {\n%s\n    }\n%s" % (i, jseg("islot%ds" % i), jseg("islot%dn" % i), binds([(P + "ISl%dSel" % i, "slot%d" % i)]))
     for i in range(SLOTS)] + [
    jseg("iside"), "    if (this.iCan) {", jseg("igrow"), binds([(P + "IGrow", "grow")]), "    }",
    "  } else {", jseg("t0"),
] + ["    if (this.tN > %d) {\n%s\n    }" % (i, jseg("trow%d" % i)) for i in range(SLOTS)] + [
    jseg("tside"), "  }",
    base2.java("b"),
    "  if ((this.view == 0 && this.mine) || this.stale) {", jseg("pick"), binds([(P + "Pick", "pick")]), "  } else {", jseg("nopick"), "  }",
    base3.java("b"), binds([(P + "Close", "close")]),
])
PAGE_SRC = BUILD_JAVA
print("shard menu: %d segments, %d variants checked, page %d x %d, content %d px high" % (len(SEG), len(VARIANTS), PW, PH, CH))

# ================= ShPage =================
page = mk("ShPage", T["PAGE"])
for f in ("public java.util.UUID me;", "public boolean testMode;", "public String testWorld;", "public int view;", "public String key;",
          "public int tab;", "public int sel;", "public String title;", "public String sum1;", "public String sum2;", "public String sto1;",
          "public String sto2;", "public String sto2c;", "public int cN;", "public int[] cSlot;", "public String[] cName;", "public String[] cSub;",
          "public String[] cAmt;", "public String[] cAll;", "public String[] uTx;", "public String[] uCol;", "public boolean uCan;",
          "public String[] sName;", "public String[] sSub;", "public String iTitle;", "public String[] iTx;", "public String[] iCol;",
          "public boolean iCan;", "public int tN;", "public String[] tName;", "public String[] tSub;", "public String[] tSt;", "public String[] tCol;",
          "public String stText;", "public String stCol;", "public long pickArm;", "public String lastAction;", "public boolean fromMenu;",
          "public boolean mine;", "public boolean stale;"):
    F(page, f)
C(page, r"""
public ShPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.me = pr == null ? null : pr.getUuid();
  this.testMode = false;
  this.tab = 0; this.sel = 0; this.stText = ""; this.stCol = "@INFO@"; this.pickArm = 0L; this.lastAction = "";
}""".replace("@INFO@", INFO))
C(page, r"""
public ShPage(java.util.UUID u, String world) {
  super((@PR@) null, @LIFE@.CanDismiss);
  this.me = u;
  this.testMode = true;
  this.testWorld = world;
  this.tab = 0; this.sel = 0; this.stText = ""; this.stCol = "@INFO@"; this.pickArm = 0L; this.lastAction = "";
}""".replace("@INFO@", INFO))
M(page, r"""
public static @WLD@ worldOf(@ST@ st) {
  try {
    Object ext = st == null ? null : st.getExternalData();
    if (ext instanceof @EST@) return ((@EST@) ext).getWorld();
  } catch (Throwable t) { }
  return null;
}""")
M(page, r"""
public String worldName(@ST@ st) {
  if (this.testMode) return this.testWorld;
  @WLD@ w = worldOf(st);
  return w == null ? null : w.getName();
}""")
# which shard + which view: inside a shard world = hub view (that world's owner); on an island = portal view (the island owner's shard,
# co-op only); elsewhere = menu view (your own profile's shard). null = refused (this.stText says why)
M(page, r"""
public String resolve(@ST@ st) {
  String wn = worldName(st);
  if (@PKG@.ShWorlds.isShard(wn)) {   // fix (critic): re-checked on every build / click (a removed co-op member, a profile switch inside)
    this.view = 1;
    String sk = @PKG@.ShWorlds.ownerOf(wn);
    return @PKG@.ShRole.mayBeIn(this.me, sk) ? sk : null;
  }
  if (this.fromMenu) { this.view = 2; return @PKG@.ShCfg.pkey(this.me); }   // the SkyWynn Menu tile: your own shard, never the portal view
  String owner = wn == null ? null : @PKG@.ShRole.islandOwner(wn);
  if (owner != null) {
    java.util.Properties p = @PKG@.ShStore.get(owner);
    String placed = p == null ? "" : @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed");
    if (placed.startsWith(wn + "|")) {
      if (!@PKG@.ShRole.coop(@PKG@.ShRole.onIsland(this.me, wn)) && !@PKG@.ShCfg.isAdmin(this.me)) return null;
      if (!@PKG@.ShRole.mayBeIn(this.me, owner)) return null;   // fix (critic): a deleted / archived owner profile
      this.view = 0;
      return owner;
    }
  }
  this.view = 2;
  return @PKG@.ShCfg.pkey(this.me);
}""")
M(page, r"""
public void status(String r) {
  if (r == null || r.length() == 0) { this.stText = ""; return; }
  char c = r.charAt(0);
  this.stCol = c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@");
  this.stText = (c == '+' || c == '-' || c == '=') ? r.substring(1) : r;
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@INFO@", INFO))
M(page, r"""
public static String sizeName(int s) {
  return s >= 3 ? "Large (29 x 29)" : (s == 2 ? "Medium (21 x 21)" : "Small (13 x 13)");
}""")
M(page, r"""
public static long perHour(double perMin) {
  return (long) Math.floor(perMin * 60.0 + 0.0000001);
}""")
M(page, r"""
public static String have(long have, long need, String what) {
  return @PKG@.ShCfg.num(need) + " " + what + " (you: " + (have < 0L ? "?" : @PKG@.ShCfg.num(have)) + ")";
}""")
# every text of the page for profile k (settles first; never writes)
M(page, r"""
public void fill(String k, @IC@[] cs) {
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  this.key = k;
  this.cSlot = new int[6]; this.cName = new String[6]; this.cSub = new String[6]; this.cAmt = new String[6];
  this.cAll = new String[6]; this.uTx = new String[7]; this.uCol = new String[7];
  this.sName = new String[6]; this.sSub = new String[6]; this.iTx = new String[9]; this.iCol = new String[9];
  this.tName = new String[6]; this.tSub = new String[6]; this.tSt = new String[6]; this.tCol = new String[6];
  for (int i = 0; i < 6; i++) { this.cName[i] = ""; this.cSub[i] = ""; this.cAmt[i] = ""; this.cAll[i] = ""; this.sName[i] = ""; this.sSub[i] = ""; this.tName[i] = ""; this.tSub[i] = ""; this.tSt[i] = ""; this.tCol[i] = "@TEXT@"; }
  for (int i = 0; i < 7; i++) { this.uTx[i] = ""; this.uCol[i] = "@TEXT@"; }
  for (int i = 0; i < 9; i++) { this.iTx[i] = ""; this.iCol[i] = "@TEXT@"; }
  this.title = "Farming Shard";
  this.cN = 0; this.tN = 0; this.uCan = false; this.iCan = false;
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));   // fix (critic): Pick up only for the owner
  this.stale = false;
  this.sto2c = "@GOOD@";
  this.sum2 = this.view == 1 ? "You are in your Farming Shard. Use the stand or this menu." : (this.view == 0 ? "Your shard portal. Enter Shard takes you to its islands." : "Opened from the SkyWynn Menu.");
  if (p == null) { this.sum1 = "This shard's file could not be read."; this.sto1 = ""; this.sto2 = ""; return; }
  @PKG@.ShCore.pauseStale(k, p);   // fix2: a portal left in a reset island makes nothing from the first look on
  String placedNow;
  boolean ownedNow;
  @PKG@.ShStore.LOCK.lock(); try { placedNow = @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed"); ownedNow = @PKG@.ShMath.owned(p); } finally { @PKG@.ShStore.LOCK.unlock(); }
  this.stale = this.mine && placedNow.length() > 0 && @PKG@.ShRole.stale(placedNow, k);   // fix (critic): an island reset left the portal behind
  if (!ownedNow) this.sum2 = "No Farming Shard yet - it comes from the hub quest line.";
  else if (this.stale) this.sum2 = "Your island was reset - use Pick up Shard to get it back.";
  else if (placedNow.length() == 0 && this.view != 1) this.sum2 = "Not placed - production is paused. Place it on your island.";
  long now = @PKG@.ShCore.now();
  long total = 0L; long cap; int islands = 0; int totems = 0; double rate = 0.0; long minFull = -1L; boolean anyFull = false;
  long purse = @PKG@.ShPay.coins(this.me);
  @PKG@.ShStore.LOCK.lock(); try {
    @PKG@.ShMath.settleAll(p, now);
    cap = @PKG@.ShMath.cap(p);
    for (int i = 0; i < 6; i++) {
      boolean has = @PKG@.ShMath.hasIsland(p, i);
      int sz = has ? @PKG@.ShMath.size(p, i) : 0;
      this.sName[i] = "Slot " + (i + 1) + (has ? " - Wheat" : "");
      this.sSub[i] = has ? (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) : "Empty";
      if (!has) continue;
      islands++;
      long s = @PKG@.ShMath.stored(p, i);
      double r = @PKG@.ShMath.rate(p, i);
      int nt = @PKG@.ShMath.totems(p, i);
      totems += nt;
      rate += r;
      total += s;
      long tf = @PKG@.ShMath.msToFull(p, i);
      boolean full = s >= cap;
      if (full) anyFull = true;
      if (tf >= 0L && (minFull < 0L || tf < minFull)) minFull = tf;
      int c = this.cN;
      this.cSlot[c] = i;
      this.cName[c] = "Wheat Island " + (i + 1) + " - " + this.sSub[i];
      this.cSub[c] = perHour(r) + " / hour - " + (full ? "FULL - collect to restart it" : (tf < 0L ? "no totem works here" : "full in " + @PKG@.ShMath.fmtMs(tf)));
      this.cAmt[c] = @PKG@.ShCfg.num(s) + " / " + @PKG@.ShCfg.num(cap);
      this.cN = c + 1;
      if (nt > 0) {
        int t = this.tN;
        this.tName[t] = "Harvest Spirit I - Wheat Island " + (i + 1);
        this.tSub[t] = perHour(r) + " items / hour - kept in the shard until you collect";   // fix2: no "whole island" claim (the side panel: range)
        this.tSt[t] = full ? "Stopped: storage full" : "Working";
        this.tCol[t] = full ? "@BAD@" : "@GOOD@";
        this.tN = t + 1;
      }
    }
    int tier = @PKG@.ShMath.storageTier(p);
    this.uTx[0] = "Tier " + tier + " of 5";
    this.uTx[1] = "Now: " + @PKG@.ShCfg.num(cap) + " items per island";
    this.uTx[3] = "Each island of this shard holds this many items. A full island stops making items.";
    this.uTx[4] = "Cost";
    if (tier >= 5) {
      this.uTx[2] = "Fully upgraded";
      this.uCol[2] = "@GOLD@";
      this.uTx[5] = "Nothing left to buy here.";
    } else {
      long nc = @PKG@.ShCfg.storeCoins(tier + 1);
      long ne = (long) @PKG@.ShCfg.storeEnch(tier + 1);
      long he = @PKG@.ShInv.count(cs, @PKG@.ShCore.ENCH);
      this.uTx[2] = "Next: " + @PKG@.ShCfg.num(100L * (long) @PKG@.ShCfg.stacks(tier + 1)) + " items per island";
      this.uCol[2] = "@GOOD@";
      this.uTx[5] = have(purse, nc, "coins");
      this.uCol[5] = (purse < 0L || purse >= nc) ? "@GOOD@" : "@BAD@";
      this.uTx[6] = have(cs == null ? -1L : he, ne, "Enchanted Wheat");
      this.uCol[6] = (cs != null && he >= ne) ? "@GOOD@" : "@BAD@";
      this.uCan = true;
    }
    int s = this.sel < 0 || this.sel > 5 ? 0 : this.sel;
    boolean has = @PKG@.ShMath.hasIsland(p, s);
    if (!has) {
      this.iTitle = "Slot " + (s + 1) + " - empty";
      this.iTx[0] = "Pick a crop for this slot.";
      this.iTx[1] = "Wheat already has its island.";
      this.iTx[2] = "More crops come in a later update.";
    } else {
      int sz = @PKG@.ShMath.size(p, s);
      double r = @PKG@.ShMath.rate(p, s);
      this.iTitle = "Slot " + (s + 1) + " - Wheat Island";
      this.iTx[0] = "Size: " + sizeName(sz);
      this.iTx[1] = "Makes " + perHour(r) + " items / hour";
      this.iTx[2] = "Totems: " + @PKG@.ShMath.totems(p, s) + " Harvest Spirit I";
      if (sz >= 3) {
        this.iTx[3] = "Fully grown.";
        this.iCol[3] = "@GOLD@";
        this.iTx[4] = "Use totems to make more.";
      } else {
        double nr = @PKG@.ShMath.totemRate(p, s) * @PKG@.ShMath.factor(sz + 1);
        long nc = sz == 1 ? (long) @PKG@.ShCfg.GM_COINS : (long) @PKG@.ShCfg.GL_COINS;
        long ns = sz == 1 ? (long) @PKG@.ShCfg.GM_SEEDS : (long) @PKG@.ShCfg.GL_SEEDS;
        int ncl = sz == 1 ? @PKG@.ShCfg.GM_COLL : @PKG@.ShCfg.GL_COLL;
        long hs = @PKG@.ShInv.count(cs, @PKG@.ShCore.SEED);
        int ct = @PKG@.ShPay.collTier(this.me, @PKG@.ShCore.COLL);
        this.iTx[3] = "Next: " + sizeName(sz + 1);
        this.iCol[3] = "@GOOD@";
        this.iTx[4] = "Would make " + perHour(nr) + " items / hour";
        this.iCol[4] = "@GOOD@";
        this.iTx[5] = "Cost";
        this.iTx[6] = have(purse, nc, "coins");
        this.iCol[6] = (purse < 0L || purse >= nc) ? "@GOOD@" : "@BAD@";
        this.iTx[7] = have(cs == null ? -1L : hs, ns, "Eternal Wheat Seeds");
        this.iCol[7] = (cs != null && hs >= ns) ? "@GOOD@" : "@BAD@";
        this.iTx[8] = "Wheat collection " + ncl + " (you: " + (ct < 0 ? "?" : String.valueOf(ct)) + ")";
        this.iCol[8] = ct >= ncl ? "@GOOD@" : "@BAD@";
        this.iCan = true;
      }
    }
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  long xp = total * (long) @PKG@.ShCfg.XP_WHEAT * (long) @PKG@.ShCfg.XP_PCT / 100L;
  this.cAll[0] = @PKG@.ShCfg.num(total) + " items";
  this.cAll[1] = "+" + @PKG@.ShCfg.num(xp) + " Farming XP";
  this.cAll[2] = "Wheat collection +" + @PKG@.ShCfg.num(total);
  long lc = @PKG@.ShStore.lng(p, "lastCollect", 0L);
  this.cAll[3] = lc <= 0L ? "Never collected yet." : "Last collected " + @PKG@.ShMath.fmtMs(now - lc) + " ago.";
  this.cAll[4] = "Inventory first. What does not fit stays here.";
  this.cAll[5] = "XP and collections are paid when you collect.";
  this.sum1 = islands + (islands == 1 ? " island - " : " islands - ") + totems + (totems == 1 ? " totem - " : " totems - ") + perHour(rate) + " items / hour";
  this.sto1 = "Storage " + @PKG@.ShCfg.num(cap) + " per island";
  if (anyFull) { this.sto2 = "An island is FULL - collect now"; this.sto2c = "@BAD@"; }
  else if (totems == 0) { this.sto2 = "No totems - nothing is harvested"; this.sto2c = "@WARN@"; }
  else { this.sto2 = minFull < 0L ? "" : "First island full in " + @PKG@.ShMath.fmtMs(minFull); this.sto2c = "@GOOD@"; }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@GOLD@", GOLD).replace("@WARN@", WARN).replace("@TEXT@", TEXT))
F(page, "public static volatile @IC@[] TEST_INV = null;")
M(page, r"""
public @IC@[] invOf(@REF@ ref, @ST@ st) {
  if (this.testMode) return @PKG@.ShPage.TEST_INV;
  return @PKG@.ShInv.containers(st, ref);
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  String k = resolve(st);
  if (k == null) { this.view = 2; status("-Only the island owner and co-op members can use this shard."); }
  fill(k, invOf(ref, st));
  if (!@PKG@.ShCfg.ON) status("-Shards are switched off on this server.");
@PAGE_JAVA@
}""".replace("@PAGE_JAVA@", PAGE_SRC))
M(page, r"""
public static String jsonA(String data) {
  if (data == null) return "";
  int i = data.indexOf("\"a\"");
  if (i < 0) return "";
  i = data.indexOf(':', i + 3);
  if (i < 0) return "";
  int q = data.indexOf('"', i + 1);
  if (q < 0) return "";
  int e = data.indexOf('"', q + 1);
  if (e < 0) return "";
  return data.substring(q + 1, e);
}""")
# one click (world thread): the action, then the page is built again (never periodically)
M(page, r"""
public String act(String a, @REF@ ref, @ST@ st) {
  this.lastAction = a;
  if (a.startsWith("tab")) { int t = a.length() > 3 ? (int) (a.charAt(3) - '0') : 0; if (t >= 0 && t <= 3) this.tab = t; return ""; }
  if (a.startsWith("slot")) { int s = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (s >= 0 && s <= 5) this.sel = s; return ""; }
  String k = resolve(st);
  if (k == null) return "-Only the island owner and co-op members can use this shard.";
  java.util.UUID u = this.me;
  if (a.equals("colall")) return @PKG@.ShCore.collect(u, k, -1, invOf(ref, st));
  if (a.startsWith("col")) {
    int r = a.length() > 3 ? (int) (a.charAt(3) - '0') : -1;
    fill(k, invOf(ref, st));
    if (r < 0 || r >= this.cN) return "-That island is gone - the page is up to date now.";
    return @PKG@.ShCore.collect(u, k, this.cSlot[r], invOf(ref, st));
  }
  if (a.equals("buy")) return @PKG@.ShCore.buyStorage(u, k, invOf(ref, st));
  if (a.equals("grow")) return @PKG@.ShCore.grow(u, k, this.sel, invOf(ref, st));
  if (a.equals("enter")) {
    if (this.testMode) return "=test: enter";
    return @PKG@.ShWorld2.enter(st, ref, u, k, worldOf(st));
  }
  if (a.equals("back")) {
    if (this.testMode) return "=test: back";
    return @PKG@.ShWorld2.leave(st, ref, u, k);
  }
  if (a.equals("pick")) {
    fill(k, invOf(ref, st));
    if (!this.mine) return "-Only the island owner can pick up the shard.";
    if (this.view != 0 && !this.stale) return "-Pick up the shard at its portal.";
    long now = System.currentTimeMillis();
    if (now - this.pickArm > 10000L) { this.pickArm = now; return "=Click Pick up Shard again to pick it up. Its islands and storage are kept."; }
    this.pickArm = 0L;
    if (this.testMode) return "=test: pick";
    return @PKG@.ShCore.pickup(u, k, worldOf(st), invOf(ref, st));
  }
  return "";
}""")
M(page, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String a = jsonA(data);
  if (a.equals("close")) { if (!this.testMode) close(); return; }
  if (a.length() == 0) return;
  String r = "";
  try { r = act(a, ref, st); } catch (Throwable t) { @PKG@.ShCfg.warn("shard menu action " + a + " failed: " + t); r = "-Something went wrong - the server log has the details."; }
  if (r != null && r.length() > 0) status(r);
  if (!this.testMode) {
    if ((a.equals("enter") || a.equals("back")) && r != null && r.startsWith("+")) { close(); return; }
    rebuild();
  }
}""")
pfn = mk("ShPageFn", None, ("java.util.function.Function",))
C(pfn, "public ShPageFn() { }")
M(pfn, "public Object apply(Object o) { return new @PKG@.ShPage((@PR@) o); }")

# ================= bridge Functions: shard:fn:open (SkyyMenu tile, world thread) + shard:fn:world =================
bfn = mk("ShFn", None, ("java.util.function.Function",))
F(bfn, "public int mode;")
C(bfn, "public ShFn(int m) { this.mode = m; }")
M(bfn, r"""
public Object apply(Object o) {
  try {
    if (this.mode == 1) return o == null ? null : @PKG@.ShWorlds.ownerOf(String.valueOf(o));
    if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return Boolean.FALSE;
    @PKG@.ShPage pg = new @PKG@.ShPage(pr);
    pg.fromMenu = true;
    p.getPageManager().openCustomPage(r, st, pg);
    return Boolean.TRUE;
  } catch (Throwable t) { @PKG@.ShCfg.warn("shard:fn:open failed: " + t); return Boolean.FALSE; }
}""")

# ================= /shardadmin (skyyshards.admin): give <player> | info <player> | unplace <player> | unload <player> =================
adm = mk("ShAdmin")
M(adm, r"""
public static String keyOfName(String name) {
  @PR@ t = @UNI@.get().getPlayerByUsername(name, com.hypixel.hytale.server.core.NameMatching.EXACT_IGNORE_CASE);
  return t == null ? null : @PKG@.ShCfg.pkey(t.getUuid());
}""")
M(adm, r"""
public static java.util.ArrayList run(String args) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] a = args == null ? new String[0] : args.trim().split("\\s+");
  if (a.length < 2) { out.add("-Usage: /shardadmin give <player> | info <player> | unplace <player> | unload <player>"); return out; }
  String cmd = a[0].toLowerCase();
  @PR@ t = @UNI@.get().getPlayerByUsername(a[1], com.hypixel.hytale.server.core.NameMatching.EXACT_IGNORE_CASE);
  if (t == null || !t.isValid()) { out.add("-That player is not online."); return out; }
  String k = @PKG@.ShCfg.pkey(t.getUuid());
  if (cmd.equals("give")) {
    @REF@ r = t.getReference();
    if (r == null || !r.isValid()) { out.add("-That player is not in a world."); return out; }
    long got = @PKG@.ShInv.give(@PKG@.ShInv.containers(r.getStore(), r), @PKG@.ShCore.SHARD, 1L);
    out.add(got > 0L ? "+Gave a Farming Shard to " + t.getUsername() + "." : "-Their inventory is full.");
    if (got > 0L) @PKG@.ShSay.to(t, "[Shards] You got a Farming Shard. Place it on your island, then right-click it.", "#39f493");
    return out;
  }
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (cmd.equals("info")) {
    if (p == null) { out.add("-The shard file of " + t.getUsername() + " could not be read."); return out; }
    @PKG@.ShStore.LOCK.lock(); try {
      @PKG@.ShMath.settleAll(p, @PKG@.ShCore.now());
      out.add("=" + t.getUsername() + " (" + k + "): placed " + @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed") + ", storage tier " + @PKG@.ShMath.storageTier(p) + ", world " + @PKG@.ShWorlds.name(k) + (@PKG@.ShWorlds.loaded().contains(@PKG@.ShWorlds.name(k)) ? " (loaded)" : " (unloaded)"));
      for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) if (@PKG@.ShMath.hasIsland(p, i)) out.add("=  slot " + (i + 1) + ": wheat size " + @PKG@.ShMath.size(p, i) + ", stored " + @PKG@.ShMath.stored(p, i) + " / " + @PKG@.ShMath.cap(p) + ", totems " + @PKG@.ShStore.str(p, @PKG@.ShMath.ik(i, "totems")));
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    return out;
  }
  if (cmd.equals("unplace")) {
    if (p == null) { out.add("-The shard file of " + t.getUsername() + " could not be read."); return out; }
    String was;
    @PKG@.ShStore.LOCK.lock(); try {
      was = @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed");
      @PKG@.ShMath.settleAll(p, @PKG@.ShCore.now());
      p.remove(@PKG@.ShMath.K + ".placed");
      if (@PKG@.ShMath.owned(p)) p.setProperty(@PKG@.ShMath.K + ".paused", "1");
      String e = @PKG@.ShStore.save(k, p);
      if (e != null) { out.add("-Could not save: " + e); return out; }
    } finally { @PKG@.ShStore.LOCK.unlock(); }
    @PKG@.ShStore.log("admin unplace " + k + " was " + was);
    out.add("+" + t.getUsername() + "'s Farming Shard record is cleared (was: " + (was.length() == 0 ? "not placed" : was.replace('|', ' ')) + "). Its islands are kept; give a new shard item with /shardadmin give if the old block is gone.");
    return out;
  }
  if (cmd.equals("unload")) {
    String n = @PKG@.ShWorlds.name(k);
    @WLD@ w = @UNI@.get().getWorld(n);
    if (w == null) { out.add("=" + n + " is not loaded."); return out; }
    if (w.getPlayerCount() > 0) { out.add("-Someone is inside " + n + " - it unloads once it is empty."); return out; }
    out.add(@UNI@.get().removeWorld(n) ? "+Unloaded " + n + " (the folder stays)." : "-Could not unload " + n + ".");
    return out;
  }
  out.add("-Unknown: " + cmd + ". Usage: /shardadmin give <player> | info <player> | unplace <player> | unload <player>");
  return out;
}""")
M(adm, r"""
public static void send(@PR@ pr, java.util.ArrayList lines) {
  for (int i = 0; i < lines.size(); i++) {
    String l = String.valueOf(lines.get(i));
    char c = l.length() > 0 ? l.charAt(0) : ' ';
    String col = c == '+' ? "@GOOD@" : (c == '-' ? "@BAD@" : "@INFO@");
    @PKG@.ShSay.to(pr, "[Shards] " + (c == '+' || c == '-' || c == '=' ? l.substring(1) : l), col);
  }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@INFO@", INFO))
admv = mk("ShAdminArgsCmd", T["APC"])
F(admv, "public @RA@ argsArg;")
C(admv, r"""
public ShAdminArgsCmd() {
  super("(admin) give <player> | info <player> | unplace <player> | unload <player>");
  requirePermission("skyyshards.admin");
  this.argsArg = withRequiredArg("args", "give <player>, info <player>, unplace <player> or unload <player>", @ATY@.GREEDY_STRING);
}""")
M(admv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.ShAdmin.send(pr, @PKG@.ShAdmin.run(String.valueOf(ctx.get(this.argsArg)))); }
  catch (Throwable t) { @PKG@.ShCfg.warn("/shardadmin failed: " + t); }
}""")
admc = mk("ShAdminCmd", T["APC"])
C(admc, r"""
public ShAdminCmd() {
  super("shardadmin", "(admin) Shards: give <player> | info <player> | unplace <player> | unload <player>");
  requirePermission("skyyshards.admin");
  addUsageVariant(new @PKG@.ShAdminArgsCmd());
}""")
M(admc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.ShAdmin.send(pr, @PKG@.ShAdmin.run(""));
}""")

# ================= plugin =================
pl = mk("SkyyShardsPlugin", T["JP"])
F(pl, "public java.util.concurrent.ScheduledFuture ticker;")
C(pl, "public SkyyShardsPlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.ShCfg.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyShards");
  @PKG@.ShCfg.DIR = dir;
  @PKG@.ShCfg.FILE = dir.resolve("config.properties");
  String c = @PKG@.ShCfg.loadCfg(true);
  @PKG@.ShStore.DIR = dir.resolve("shards");
  java.util.Map b = @PKG@.ShCfg.bridge();
  b.put("shard:fn:allowed", new @PKG@.ShGate());
  b.put("shard:fn:open", new @PKG@.ShFn(0));
  b.put("shard:fn:world", new @PKG@.ShFn(1));
  b.put("shard:version", "@VERSION@");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@PAGEID@", new @PKG@.ShPageFn());
  getEntityStoreRegistry().registerSystem(new @PKG@.ShPlace());
  getCommandRegistry().registerCommand(new @PKG@.ShAdminCmd());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ShTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - Farming Shard (Skyy_Shard_Farming portal, menu page @PAGEID@), one shard world per profile (skyy-shard-<pkey>, Farming region at x @RX@), hub + 6 slots, Wheat island Small / Medium / Large, Harvest Spirit I, lazy production + storage + Collect; guards via SkyyIslands 0.5.8 (shard:fn:allowed" + (@PKG@.ShRole.guarded() ? ", island:shardguard seen" : ", island:shardguard not seen yet") + "); bridge shard:fn:allowed / open / world; " + c + "; data in " + dir);
}""".replace("@KITID@", KIT_ID).replace("@PAGEID@", PAGE_ID).replace("@RX@", str(REGION_X)))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  java.util.Map b = @PKG@.ShCfg.bridge();
  try { b.remove("shard:fn:allowed"); b.remove("shard:fn:open"); b.remove("shard:fn:world"); b.remove("shard:version"); } catch (Throwable t) { }
  super.shutdown();
}""")

ALLC = [cfg, st, mth, geo, fill, wld, op, say, role, gate, inv, pay, core, w2, hop, tick, sweep, part, place, chk, page, pfn, bfn, adm, admv, admc, pl]
for c in ALLC:
    c.writeFile(OUT)
kit.write(OUT)
print("classes written:", len(ALLC) + len(kit.classes), "(%d kit)" % len(kit.classes))

# ================= assets =================
template = {
    "$Comment": "SkyyShards shard world template - void world; the mod builds each region on first Enter",
    "RequiredPlugins": {}, "ChunkStorage": {"Type": "Hytale"}, "GameMode": "Adventure", "IsPvpEnabled": False, "IsSpawningNPC": False,
    "GameTime": "0001-01-01T09:00:00Z", "UUID": {"$binary": "AAAAAAAAAAAAAAAAAAAAAA==", "$type": "04"}, "GameplayConfig": "Default",
    # fix2: the world's own death rule (WorldConfig "Death" wins over the GameplayConfig - SkyyWorldGen 0.5.1 precedent): a void death
    # would otherwise drop half of every stack where nobody can reach it (Skyy's lock: island deaths keep items)
    "Death": {"ItemsLossMode": "None"},
    "IsCompassUpdating": True, "IsTicking": True, "Seed": 0, "IsGameTimePaused": False, "IsObjectiveMarkersEnabled": True,
    "IsAllNPCFrozen": False, "IsSavingPlayers": True, "WorldGen": {"Type": "Void", "Tint": "#5b9e28", "Environment": "Env_Default_Void"},   # ui-data: grass tint of the world template (not UI)
    "SpawnProvider": {"Id": "Global", "SpawnPoint": {"X": ARRIVE[0], "Y": ARRIVE[1], "Z": ARRIVE[2], "Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0}},
    "IsSpawnMarkersEnabled": True, "Instance": {"RemovalConditions": []}, "DeleteOnRemove": False, "Version": 4,
}
GOLD_RAMP = tuple(tuple(int(h_[k_:k_ + 2], 16) for k_ in (1, 3, 5)) for h_ in ("#5a3a00", "#c89411", "#ffe27a"))   # ui-data: texture ramp
TEX_PATH = "Blocks/SkyyShards/Shard_Farming.png"
ICON_PATH = "Icons/ItemsGenerated/%s.png" % SHARD_ITEM
_tex = SA.recolor(AZ.read("Common/Blocks/Miscellaneous/Platform_Magic_Blue2.png"), GOLD_RAMP, rank=0.35)
_icon = open(_ICON_SRC, "rb").read()
_ii = SA.png_decode(_icon)
assert (_ii.w, _ii.h) == (64, 64), (_ii.w, _ii.h)
item = {"TranslationProperties": {"Name": "server.items.%s.name" % SHARD_ITEM, "Description": "server.items.%s.description" % SHARD_ITEM},
        "Icon": ICON_PATH, "Categories": ["Blocks.Portals"], "PlayerAnimationsId": "Block", "MaxStack": 1,
        "BlockType": {"DrawType": "Model", "Material": "Solid", "Opacity": "Transparent",
                      "CustomModel": "Blocks/Miscellaneous/Platform_MagicInactive.blockymodel",
                      "CustomModelTexture": [{"Texture": TEX_PATH, "Weight": 1}],
                      "HitboxType": "Pad_Portal", "BlockParticleSetId": "Stone", "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone",
                      "VariantRotation": "NESW", "Gathering": {"Breaking": {"GatherType": "Unbreakable"}},
                      "Interactions": {"Use": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": PAGE_ID}}]}}}}
LANG = []
for pre in ("", "server."):
    LANG.append("%sitems.%s.name=Farming Shard" % (pre, SHARD_ITEM))
    LANG.append("%sitems.%s.description=A portal to your own Farming Shard islands. Place it on your island and right-click it." % (pre, SHARD_ITEM))
files = {
    "Server/Instances/SkyyShard/instance.bson": json.dumps(template, indent=2) + "\n",
    "Server/Instances/SkyyShard/resources/InstanceData.json": '{\n  "HadPlayer": false\n}\n',
    "Server/Item/Items/SkyyShards/%s.json" % SHARD_ITEM: json.dumps(item, indent=2),
    "Server/Languages/en-US/server.lang": "\n".join(LANG) + "\n",
}
jar = os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)
man = B.manifest("SkyyShards", VERSION, "SkyWynn Shards: the Farming Shard - a portal block you place on your island that opens your own private shard world (one per profile): a hub island with 6 fixed slots, a Wheat island that grows Small / Medium / Large in place, a Harvest Spirit totem that harvests while you are away (no ticking - counted when you open the menu), shard storage, Collect (Farming XP + collections are paid when you collect) and the shard menu. Protected by SkyyIslands 0.5.8. Server Setup: Shards.", PKG + ".SkyyShardsPlugin")
man["IncludesAssetPack"] = True
B.assemble(jar, man, OUT, extra_files=files)
with zipfile.ZipFile(jar, "a") as _jz:
    _jz.writestr("Common/" + TEX_PATH, _tex)
    _jz.writestr("Common/" + ICON_PATH, _icon)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyShards jar must not ship .ui files (inline pages only): %s" % _bad)
print("assembled", jar, os.path.getsize(jar), "bytes (with the generated gold portal texture + the icon)")
if "--deploy" in sys.argv:
    raise SystemExit("SkyyShards: --deploy is not supported here - deploys go through tools/deploy_set.py")
