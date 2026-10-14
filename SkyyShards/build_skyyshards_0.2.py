"""SkyyShards 0.2 - build script (javassist via jpype). Derived from build_skyyshards_0.1.py (the SET pin; a hand-written build script,
no patch chain). 0.2 = Gathering-Shards-Spec PHASE 6 (TOTEMS, research/Gathering-Shards-Spec.md 9.3 + the phase 6 row) + Rebirth-Spec R9
(research/cloud/Rebirth-Spec.md section 6: the shard crafting gate n >= 2). Skyy 2026-10-14: "Run everything you can in parallel. I want
everything on your list done by 5 pm when i get off work." Skyy's totem words (docs/answered/skills.md 2026-10-11): "upgraded to a totem
pole that is always actibe in an area around it" / popups "No fuel, optional booster" + "Both: tier by Upgrade, extras in slots" / "you can
right click them to see their info, upgrade them, give them modifiers, and pick them up to move them"; SHARD SOURCES 2026-10-13 "all T1
shards come from quests. (more can be crafter after rebirth 2.".
Run:   python SkyyShards/build_skyyshards_0.2.py   -> SkyyShards/SkyyShards-0.2.jar   (never --deploy: tools/deploy_set.py installs the set)
Check: python SkyyShards/test_skyyshards_0.2.py   (bare JVM, -Xverify:all, every new code path executed)

WHAT 0.2 ADDS (everything of 0.1 below stays unless said here):
  - ALL TOTEM TYPES (spec 9.3) as items Skyy_Totem_<Type> (MaxStack 1, NOT placeable by hand) carrying their own TIER DOCUMENT in the item
    metadata key "SkyyTotem" ({t type, tier 1-5, m1, m2 modifiers, bst booster ms left, uid}) - spec question 10 default: tiers, no rarity.
    Farming (works now): Harvest Spirit (worker), Rain (the MoreTotems Water Totem fold, MIT, credit Nagatwin), Fertilizer, Blessing of the
    Sun (day), Fairy Grove, Season Ward, Scarecrow, Pollinator, Harvest Moon (night + Enchanted crops), Compost, Mushroom / Shade (night).
    Ranching (Herd Pole), Foraging (Lumber Spirit, Sap Tap), Mining (Quarry Spirit, Auto-Smelt Pole, Geode Pole), Combat (Soul Cage, Lure Pole,
    Trophy Pole): the items exist and can be crafted only once their shard exists (phase 7) - the menu says "later update".
  - PLACING / PICKING UP happens in the shard menu (Totems tab: Place from your inventory onto the selected island's totem pads, Pick up):
    SkyyIslands 0.5.8's place guard passes no block id in shard worlds, so a hand-placed totem could not be told from building (DECISION -
    no SkyyIslands change this round). Placed totems are drawn as blocks Skyy_TotemBlock_<Type> on the island's pads (the vanilla Healing
    Totem statue model, our texture recoloured per type at BUILD time; Rain = the folded MoreTotems Water Totem model); RIGHT-CLICK one =
    the shard menu opened on the Totems tab with that totem selected (nearest pad to you). Pads per island: totem.pads.small / medium /
    large (3 / 4 / 5). Pick up returns the EXACT document (tier, both modifiers, booster time left, uid) - the item first, then the record
    (a refused save takes the item back by uid).
  - RATE MATH (spec 9.2 + "farm is bigger than the spirits range"): a worker (Harvest Spirit) harvests only the crops inside its range:
    worker rate = totem.rate<tier> x (crops within range / crops within the Harvest Spirit I range on a Small island) x modifiers x booster;
    range = totem.range<tier> (3 / 5 / 7 / 9 / 11) + 2 per Wider Area + 2 while boosted. So a Harvest Spirit I on the starter island still
    makes exactly 0.1's 1 item / minute; growing the island pays only once a totem's range reaches the new crops. island.factor.medium /
    large are NOT used any more (removed from Server Setup; old lines are ignored). Support totems add totem.support<tier> % each (Sun by
    day, Mushroom / Shade by night = x the day / night share moon.nightShare), Harvest Moon adds moon.bonus % at night. No worker = nothing.
  - MODIFIERS (2 slots, Skyy_TotemMod_<Kind>, crafted in the menu): Wider Area (+2 range), Faster (+20 %), Auto-Replant (+10 %), Compost
    (+10 %), Storage (+3 stacks for that island), Rare Finder (+100 % Enchanted crop chance). Removing one gives the item back.
  - BOOSTER slot (optional, no fuel - Skyy's popup): 1 Life / Water / Void Essence burns totem.boostSec (3600 s real time): +2 range and
    +totem.boostPct (25) % for that totem. The time left travels with the document when the totem is picked up.
  - HARVEST MOON (spec rule + question 14): at night only +moon.bonus % and a moon.enchChance (0.05) % chance per crop of a bonus Enchanted
    crop (Skyy_Ench_Wheat), x (1 + Rare Finders) x the owner's Moon Blade (bridge gear:fn:moonblade, Function(String pkey) -> Number 1-5;
    SkyyGear's sickle roll is NOT built yet - SkyyGear is in another round - so today the factor is 1). Lazy maths: the night share of the
    elapsed time, rolls seeded by island + clock so a re-settle never re-rolls. Enchanted crops are stored apart (farming.i<n>.ench), given
    at Collect and credited as 100 Wheat each (collections + XP, the alias rule).
  - TIER-UP: on the Anvil (spec 9.3) = SkyyGear (busy in another round, NOT built here). The Shards side + the bridge SkyyGear calls later:
    shard:fn:totem (Object[]{String op, String itemId, String docJson} -> String): op "cost" -> "Item:qty,Item:qty" (totem.upCost: tier
    I->II 1 Enchanted + 10 essence, II->III 2 + 25, III->IV 3 + 50, IV->V 5 + 100) or "err:<why>"; op "up" -> the new document JSON (tier+1)
    or "err:..."; op "describe" -> one line; op "key" -> "SkyyTotem". The totem page's Upgrade button calls gear:fn:anvil:open (UUID) when
    SkyyGear publishes it, else says the Anvil comes with the next SkyyGear update. /shardadmin totem <player> <type> [tier] gives any tier.
  - CRAFT tab (5th tab, crafting in the menu, items counted before / after, coins last, everything back on a failure): the 11 Farming totems
    (tier I), the 6 modifiers, and an extra FARMING SHARD - REBIRTH R9 GATE: only from rebirth 2 (rebirth:fn:count(pkey) >= craft.shardRebirth
    2; SkyyRebirth absent or the file still loading = refused). Recipes = Server Setup text rows craft.<ItemId> ("Item:qty,...;coins").
    SkyyArmory 0.1.25 publishes armory:fn:soulcage (the Soul Orb / Cage ladder) for the Soul Cage totem; NOTHING reads it yet - the Soul
    Cage recipe comes with the Combat Shard (phase 7).
  - Range circle: "Show range" draws the totem's range as particles for 10 s. Workers stay PARTICLES (spec 10.6 fallback; probe N1 not run).
  - Bridge added: shard:fn:totem (above). Read: gear:fn:moonblade, gear:fn:anvil:open, rebirth:fn:count (armory:fn:soulcage: phase 7).
  - Data: farming.i<n>.totems entries are now "type:tier:m1:m2:boostUntil:uid" (0.1's "harvest_spirit:1" still reads as a Harvest Spirit I),
    farming.i<n>.ench, totem.log (one line per totem place / pick up / modifier / booster / craft). ROLLBACK 0.2 -> 0.1: safe for the files
    (0.1 reads every Harvest Spirit entry as tier I and ignores the other types; ench counts and totem docs on items are ignored) but the
    totems placed with 0.2 stop working and 0.1 cannot pick them up - pick totems up before a rollback.
  REVIEW FIXES 3 (shards02fix, each a "fix3:" check in X16): totem place / pick up / modifiers / booster = the OWNER profile only (co-op
    never, even with shard.coopCollect); a totem whose uid is already placed (a crash copy) is refused and removed; /shardadmin give / totem
    for a player in another world is refused (inventory only on its own world thread); no page rebuild after the Anvil opened; a Farming
    Shard is crafted only when the profile's shard is not placed (a lost one) and none is in the inventory; the MIT notice ships in
    CREDITS-MoreTotems.txt.
  REVIEW FIXES 4 (shards02fix2, each a "fix4:" check in X16): ONE FARMING SHARD PER PROFILE, EVER - the craft is refused once the profile
    placed a shard (an island exists, also while it is picked up and stored in a chest / vault / auction) or crafted one (farming.crafted
    = 1, saved BEFORE the shard is handed out; a refused save gives everything back) - a lost shard = /shardadmin give (question); the
    worker cap totem.workerMax (default 12 = spec 9.2 / 9.3 ceiling, before the totem's own modifiers / booster); gear:fn:moonblade is never
    asked while ShStore.LOCK is held (warmed in ShCore.pauseStale / admin info, settle reads the cache); /shardadmin give / totem refused
    while the target switches profile; right-click selects the statue LOOKED AT (TargetUtil.getTargetBlockOrigin, 8 blocks), the nearest to
    the player only as a fallback. SkyyCollections 0.2.14 fix4: a shard chunk is never cut by cap.perCredit (above 256 = FALSE).
  NOT BUILT (FLOOR notes): the HANDHELD Rain Totem (Skyy 2026-10-11 popup "Rain Totem handheld: click = 30 s of rain, costs Mana") - the
    Rain Totem here is the placed pole only; the handheld one comes with the Mana round (question). Picking up a totem moves the totems on
    the higher pads down one pad (records are a list).

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
  - /shardadmin (skyyshards.admin): give <player> | info <player> | unplace <player> | unload <player> | totem <player> <type> [tier].
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

VERSION = "0.2"
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
    "BD":   "org.bson.BsonDocument",                                                        # 0.2: the totem document
    "BV":   "org.bson.BsonValue",
    "IDM":  "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata",
    "TCO":  "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",   # 0.2: the nearest totem pad
    "TU":   "com.hypixel.hytale.server.core.util.TargetUtil",                                # fix4: the totem block looked at
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
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addUsageVariant"), (T["ATY"], "GREEDY_STRING"),
             (T["IS"], "withMetadata"), (T["IS"], "getMetadata"), (T["IDM"], "KEYED_CODEC"), (T["BD"], "parse"), (T["BD"], "toJson"),
             (T["TCO"], "getComponentType"), (T["TCO"], "getPosition"), (T["IC"], "canAddItemStack"),
             (T["ST"], "isInThread"), (T["TU"], "getTargetBlockOrigin")):
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
TOTEM_PAGE_ID = "SkyyShardTotem"        # 0.2: the OpenCustomUI page id of every totem block (the menu on the Totems tab, nearest totem)
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

# ================= 0.2 TOTEMS (spec 9.3; Skyy's farming list of 12 = the 11 farming types + Herd Pole) =================
# key, item suffix, name, worker?, shards that accept it, effect (work = harvests, all = always, day / night = x the share, moon = Harvest
# Moon), the recolour ramp of its texture / icon (dark, mid, light)
TOTEMS = [
    ("harvest_spirit", "HarvestSpirit", "Harvest Spirit", True, ("Farming", "Ranching", "Orchard"), "work", ("#2f4a12", "#7fbf3a", "#e4ffb0")),   # ui-data: texture ramp (not UI)
    ("rain", "Rain", "Rain Totem", False, ("Farming", "Orchard"), "all", ("#0d2f5c", "#2f7fd6", "#bfe6ff")),   # ui-data: texture ramp (not UI)
    ("fertilizer", "Fertilizer", "Fertilizer Totem", False, ("Farming", "Orchard", "Foraging"), "all", ("#3a2410", "#8a5a2b", "#e0b98a")),   # ui-data: texture ramp (not UI)
    ("sun_blessing", "SunBlessing", "Blessing of the Sun", False, ("Farming",), "day", ("#6b3a00", "#f0a020", "#fff2a0")),   # ui-data: texture ramp (not UI)
    ("fairy_grove", "FairyGrove", "Fairy Grove", False, ("Farming",), "all", ("#4a1a5c", "#d070e0", "#ffe0ff")),   # ui-data: texture ramp (not UI)
    ("season_ward", "SeasonWard", "Season Ward", False, ("Farming", "Orchard"), "all", ("#1d3d3d", "#4fb0a8", "#d0fff6")),   # ui-data: texture ramp (not UI)
    ("scarecrow", "Scarecrow", "Scarecrow", False, ("Farming", "Ranching"), "all", ("#3d2a0a", "#b08a3c", "#f2deb0")),   # ui-data: texture ramp (not UI)
    ("pollinator", "Pollinator", "Pollinator", False, ("Farming", "Orchard"), "all", ("#4a3a00", "#e8c020", "#fff6b8")),   # ui-data: texture ramp (not UI)
    ("harvest_moon", "HarvestMoon", "Harvest Moon", False, ("Farming",), "moon", ("#141a3d", "#5a6ad8", "#e6e8ff")),   # ui-data: texture ramp (not UI)
    ("compost", "Compost", "Compost Pole", False, ("Farming",), "all", ("#22180c", "#5c4a2a", "#b0a070")),   # ui-data: texture ramp (not UI)
    ("mushroom_shade", "MushroomShade", "Mushroom Shade", False, ("Farming",), "night", ("#3d0f1a", "#a83a4a", "#ffd0d6")),   # ui-data: texture ramp (not UI)
    ("herd_pole", "HerdPole", "Herd Pole", False, ("Ranching",), "all", ("#3a2a1a", "#9a7a5a", "#f0e0c8")),   # ui-data: texture ramp (not UI)
    ("lumber_spirit", "LumberSpirit", "Lumber Spirit", True, ("Foraging",), "work", ("#1a2a10", "#4a7a2a", "#c0e0a0")),   # ui-data: texture ramp (not UI)
    ("sap_tap", "SapTap", "Sap Tap", False, ("Foraging",), "all", ("#3a1a00", "#c06a10", "#ffd8a0")),   # ui-data: texture ramp (not UI)
    ("quarry_spirit", "QuarrySpirit", "Quarry Spirit", True, ("Mining",), "work", ("#1e1e24", "#6a6a78", "#d8d8e6")),   # ui-data: texture ramp (not UI)
    ("autosmelt_pole", "AutoSmeltPole", "Auto-Smelt Pole", False, ("Mining",), "all", ("#3a0e00", "#d04a10", "#ffc890")),   # ui-data: texture ramp (not UI)
    ("geode_pole", "GeodePole", "Geode Pole", False, ("Mining",), "all", ("#2a0e3d", "#8a3ad0", "#ecd0ff")),   # ui-data: texture ramp (not UI)
    ("soul_cage", "SoulCage", "Soul Cage Totem", True, ("Combat",), "work", ("#0e1a2a", "#3aa0d0", "#d0f4ff")),   # ui-data: texture ramp (not UI)
    ("lure_pole", "LurePole", "Lure Pole", False, ("Combat",), "all", ("#3d0e0e", "#c03a3a", "#ffd0d0")),   # ui-data: texture ramp (not UI)
    ("trophy_pole", "TrophyPole", "Trophy Pole", False, ("Combat",), "all", ("#3d2e00", "#d0a020", "#fff0b0")),   # ui-data: texture ramp (not UI)
]
NT = len(TOTEMS)
EFF = {"work": 0, "all": 1, "day": 2, "night": 3, "moon": 4}
TOTEM_ITEM = ["Skyy_Totem_" + t[1] for t in TOTEMS]
TOTEM_BLOCK = ["Skyy_TotemBlock_" + t[1] for t in TOTEMS]
assert len(set(t[0] for t in TOTEMS)) == NT and all(":" not in t[0] and "," not in t[0] for t in TOTEMS)
FARM_TOTEMS = [i for i, t in enumerate(TOTEMS) if KIND in t[4]]
assert len(FARM_TOTEMS) == 11 and TOTEMS[0][0] == "harvest_spirit", FARM_TOTEMS
MODS = [("wider", "Wider", "Wider Area", "+2 range"), ("faster", "Faster", "Faster", "+20 % for this totem"),
        ("replant", "Replant", "Auto-Replant", "+10 % for this totem"), ("compost", "Compost", "Compost", "+10 % for this totem"),
        ("storage", "Storage", "Storage", "+3 stacks of storage for its island"),
        ("rare", "RareFinder", "Rare Finder", "+100 % Enchanted crop chance (Harvest Moon)")]
MOD_ITEM = ["Skyy_TotemMod_" + m[1] for m in MODS]
BOOSTERS = ["Ingredient_Life_Essence", "Ingredient_Water_Essence", "Ingredient_Void_Essence"]
PADS = [(0, -1), (1, 0), (0, 1), (-1, 0), (1, -1)]        # totem pads around the island pillar (on the 3 x 3 brick, y + 1), max 5
ROMAN = ["I", "II", "III", "IV", "V"]
RANGE_DEF = [3, 5, 7, 9, 11]                               # spec 9.3 range radius per tier
RATE_DEF = [1.0, 1.25, 1.5, 1.75, 2.0]                     # worker speed per tier (the range already multiplies - DECISION, PLACEHOLDER)
WMAX_DEF = 12.0                                             # fix4: spec 9.2 / 9.3 ceiling (tier 5 x size 2.4) - one worker's base items / min
# fix3 (review): items / min of ONE worker with these defaults (speed x crops in range / 20; no modifiers / booster) - QUESTION for Skyy:
#   Small  1.0  4.5  8.1  9.8 11.2  |  Medium 1.0  4.5 10.5 21.4 32.8  |  Large 1.0  4.5 10.5 21.4 36.8   (tiers I..V)
#   spec 9.2 / 9.3 had tier x size = at most 5 x 2.4 = 12 / min; a tier V with 2 Wider Areas on Large = 65 / min, 5 pads ~ 325 / min.
# fix4 (critics shards02): those numbers are now CAPPED by totem.workerMax (default 12 = the spec ceiling) before the totem's own modifiers /
#   booster: Small 1 4.5 8.1 9.8 11.2 | Medium 1 4.5 10.5 12 12 | Large 1 4.5 10.5 12 12; the best worker = 12 x Faster/Replant/Compost x
#   booster (at most 12 x 1.4 x 1.25 = 21 / min); 5 pads of tier V on Large ~ 60-105 / min before support totems. 0 = no cap (the old table).
SUPPORT_DEF = [5, 10, 15, 20, 25]                          # % per support totem by tier (PLACEHOLDER)
PADS_DEF = [3, 4, 5]
UP_DEF = "1:10,2:25,3:50,5:100"                            # Enchanted : essence for I->II .. IV->V (spec 9.3 PLACEHOLDER)


def _crop_tiles(size):
    h = HALF[size - 1]
    out = []
    for dx in range(-h, h + 1):
        for dz in range(-h, h + 1):
            ax, az = abs(dx), abs(dz)
            if ax == h and az == h:
                continue
            if ax == h or az == h or (ax <= 1 and az <= 1):
                continue
            out.append((dx, dz))
    return out


COV_R = 40
COV = [[sum(1 for (dx, dz) in _crop_tiles(s) if dx * dx + dz * dz <= r * r) for r in range(COV_R + 1)] for s in (1, 2, 3)]
assert [len(_crop_tiles(s)) for s in (1, 2, 3)] == [112, 352, 720] and COV[0][3] == 20 and COV[0][COV_R] == 112, (COV[0][:12],)
# the crafting recipes (Server Setup text rows craft.<ItemId> = "Item:qty,Item:qty;coins"; PLACEHOLDER numbers)
RECIPES = [
    (TOTEM_ITEM[0], "Plant_Crop_Wheat_Item:128,Ingredient_Life_Essence:8;500"),
    (TOTEM_ITEM[1], "Ingredient_Water_Essence:16,Plant_Crop_Wheat_Item:64;500"),
    (TOTEM_ITEM[2], "Ingredient_Life_Essence:24,Plant_Crop_Wheat_Item:64;1000"),
    (TOTEM_ITEM[3], "Ingredient_Fire_Essence:16,Skyy_Ench_Wheat:1;2000"),
    (TOTEM_ITEM[4], "Ingredient_Life_Essence:32,Skyy_Ench_Wheat:1;2000"),
    (TOTEM_ITEM[5], "Ingredient_Ice_Essence:16,Skyy_Ench_Wheat:1;2000"),
    (TOTEM_ITEM[6], "Plant_Crop_Wheat_Item:256,Wood_Softwood_Planks:32;1000"),
    (TOTEM_ITEM[7], "Ingredient_Life_Essence:16,Skyy_Ench_Wheat:2;3000"),
    (TOTEM_ITEM[8], "Ingredient_Void_Essence:16,Skyy_Ench_Wheat:4;10000"),
    (TOTEM_ITEM[9], "Plant_Crop_Wheat_Item:512,Ingredient_Life_Essence:8;1000"),
    (TOTEM_ITEM[10], "Ingredient_Void_Essence:8,Skyy_Ench_Wheat:1;2000"),
    (MOD_ITEM[0], "Skyy_Ench_Wheat:2,Ingredient_Life_Essence:16;5000"),
    (MOD_ITEM[1], "Skyy_Ench_Wheat:2,Ingredient_Lightning_Essence:16;5000"),
    (MOD_ITEM[2], "Plant_Seeds_Wheat_Eternal:4,Ingredient_Life_Essence:16;3000"),
    (MOD_ITEM[3], "Plant_Crop_Wheat_Item:640,Ingredient_Life_Essence:8;3000"),
    (MOD_ITEM[4], "Skyy_Ench_Wheat:4,Wood_Softwood_Planks:64;5000"),
    (MOD_ITEM[5], "Skyy_Ench_Wheat:8,Ingredient_Void_Essence:16;20000"),
    (SHARD_ITEM, "Skyy_Ench_Wheat:32,Ingredient_Life_Essence:64;100000"),
]
NREC = len(RECIPES)
SOUL_ORB = "Weapon_Wand_SoulOrb"                           # SkyyArmory's Soul Orb (the Soul Cage totem's core - phase 7; not used yet)

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
# 0.2: every vanilla id the totems / recipes / boosters name exists; our new ids are new
for _iid in BOOSTERS + ["Ingredient_Fire_Essence", "Ingredient_Ice_Essence", "Ingredient_Lightning_Essence"]:
    assert _iid in ITEMS, "vanilla item %s is not in Assets.zip" % _iid
for _rid, _rtxt in RECIPES:
    for _part in _rtxt.split(";")[0].split(","):
        _pid = _part.split(":")[0]
        assert _pid in ITEMS or _pid.startswith("Skyy_Ench_"), "recipe %s names unknown item %s" % (_rid, _pid)
for _iid in TOTEM_ITEM + TOTEM_BLOCK + MOD_ITEM:
    assert _iid not in ITEMS, "our id %s clashes with a vanilla item" % _iid
TOTEM_MODEL = "Items/Deployables/Healing_Totem/Healing_Totem.blockymodel"
TOTEM_TEX_SRC = "Common/Items/Deployables/Healing_Totem/Healing_Totem_Texture.png"
TOTEM_ICON_SRC = "Common/Icons/ItemsGenerated/Healing_Totem.png"
MOD_ICON_SRC = "Common/Icons/ItemsGenerated/Ingredient_Life_Essence.png"
for _n in ("Common/" + TOTEM_MODEL, TOTEM_TEX_SRC, TOTEM_ICON_SRC, MOD_ICON_SRC):
    assert _n in AZN, "vanilla asset %s missing" % _n
# the MoreTotems Water Totem fold (MIT, credit Nagatwin; docs/answered/gear.md 2026-10-11): read from Skyy's installed jar at BUILD time (read
# only, never committed); missing jar = the Rain totem uses the Healing Totem statue recoloured blue (the build says so)
MT_JAR = None
if os.path.isdir(B.MODS_DIR):
    for _f in sorted(os.listdir(B.MODS_DIR)):
        if _f.startswith("MoreTotemsPlugin") and _f.endswith(".jar"):
            MT_JAR = os.path.join(B.MODS_DIR, _f)
MT = {}
if MT_JAR:
    with zipfile.ZipFile(MT_JAR) as _z:
        _zn = set(_z.namelist())
        for _k, _n in (("model", "Common/Items/Deployables/Water_Totem/Water_Totem_Projectile.blockymodel"),
                       ("tex", "Common/Items/Deployables/Water_Totem/Water_Totem_Texture.png"), ("icon", "Common/Icons/ItemsGenerated/Water_Totem.png")):
            if _n in _zn:
                MT[_k] = _z.read(_n)
print("MoreTotems Water Totem fold:", ("from " + os.path.basename(MT_JAR) + " " + ",".join(sorted(MT))) if len(MT) == 3 else "NOT FOUND - the Rain totem uses the recoloured Healing Totem statue")
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
    "# totem.rate1 = items per minute of one Harvest Spirit I on the starter (Small) island.",
    "totem.rate1=1",
    "# totem.rate2..5 = the speed of a tier II..V worker (x the crops inside its range compared with a Harvest Spirit I on a Small island).",
] + ["totem.rate%d=%s" % (i + 1, ("%g" % RATE_DEF[i])) for i in range(1, 5)] + [
    "# totem.workerMax = the most items per minute one worker makes before its own modifiers / booster (spec ceiling 12; 0 = no cap).",
    "totem.workerMax=%g" % WMAX_DEF,
    "# totem.rangeN = the range (blocks, radius) of a tier N totem; a worker only harvests the crops inside it.",
] + ["totem.range%d=%d" % (i + 1, RANGE_DEF[i]) for i in range(5)] + [
    "# totem.supportN = percent more crops for the island from each tier N support totem (Rain, Fertilizer, Fairy Grove ...).",
] + ["totem.support%d=%d" % (i + 1, SUPPORT_DEF[i]) for i in range(5)] + [
    "# totem.pads.small / medium / large = totem pads on a Small / Medium / Large island.",
    "totem.pads.small=%d" % PADS_DEF[0], "totem.pads.medium=%d" % PADS_DEF[1], "totem.pads.large=%d" % PADS_DEF[2],
    "# totem.boostSec / totem.boostPct = one booster essence burns this long (real seconds) for +2 range and this percent more.",
    "totem.boostSec=3600", "totem.boostPct=25",
    "# totem.upCost = tier-up costs on the Anvil (SkyyGear), I->II .. IV->V, each Enchanted:essence.",
    "totem.upCost=" + UP_DEF,
    "# moon.nightShare = the share of time that is night (Harvest Moon, Mushroom Shade; the rest is day for the Blessing of the Sun).",
    "moon.nightShare=0.4",
    "# moon.bonus = Harvest Moon percent more crops at night; moon.enchChance = percent chance per crop at night of a bonus Enchanted crop.",
    "moon.bonus=25", "moon.enchChance=0.05",
    "# craft.shardRebirth = rebirths needed to craft an extra shard (Skyy: more can be crafted after rebirth 2).",
    "craft.shardRebirth=2",
    "# craft.<ItemId> = a menu recipe: Item:qty,Item:qty;coins (empty = that recipe is off).",
] + ["craft.%s=%s" % (_r[0], _r[1]) for _r in RECIPES] + [
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
          "public static volatile int XP_WHEAT = 4;", "public static volatile double RATE1 = 1.0;",
          "public static volatile double[] RATES = new double[] { %s };" % ", ".join(repr(x) for x in RATE_DEF),
          "public static volatile double WORKER_MAX = %r;" % WMAX_DEF,
          "public static volatile int[] RANGES = new int[] { %s };" % ", ".join(str(x) for x in RANGE_DEF),
          "public static volatile int[] SUPPORT = new int[] { %s };" % ", ".join(str(x) for x in SUPPORT_DEF),
          "public static volatile int[] PADS = new int[] { %s };" % ", ".join(str(x) for x in PADS_DEF),
          "public static volatile int BOOST_SEC = 3600;", "public static volatile int BOOST_PCT = 25;",
          "public static volatile String UP_COST = %s;" % jlit(UP_DEF), "public static volatile double NIGHT = 0.4;",
          "public static volatile int MOON_BONUS = 25;", "public static volatile double ENCH_CH = 0.05;", "public static volatile int SHARD_RB = 2;",
          "public static volatile String[] CRAFT = new String[] { %s };" % ", ".join(jlit(r[1]) for r in RECIPES),
          "public static final String[] CRAFT_ID = new String[] { %s };" % ", ".join(jlit(r[0]) for r in RECIPES),
          "public static final String[] DEF_CRAFT = new String[] { %s };" % ", ".join(jlit(r[1]) for r in RECIPES),
          "public static volatile int ST1 = 1;", "public static volatile int ST2 = 3;",
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

CATS = [("shards", "Shards"), ("production", "Production"), ("totems", "Totems"), ("costs", "Costs"), ("crafting", "Crafting")]
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
     "Items per minute of one Harvest Spirit I totem on a Small island.", "reload@config.properties:totem.rate1"),
] + [("totem.rate%d" % (i + 1), "Tier %s worker speed" % ROMAN[i], "totems", "dec", "%g" % RATE_DEF[i], "0", "100", "", "x", "live",
      "Speed of a tier %s worker, times the crops in its range (Harvest Spirit I on a Small island = 1)." % ROMAN[i],
      "reload@config.properties:totem.rate%d" % (i + 1)) for i in range(1, 5)] + \
    [("totem.workerMax", "Worker cap (items per minute)", "totems", "dec", "%g" % WMAX_DEF, "0", "1000", "", "", "live",
      "Most items per minute one worker makes before its own modifiers and booster (spec: 12). 0 = no cap.",
      "reload@config.properties:totem.workerMax")] + \
    [("totem.range%d" % (i + 1), "Tier %s range" % ROMAN[i], "totems", "int", str(RANGE_DEF[i]), "0", "30", "", "blocks", "live",
      "Range (radius) of a tier %s totem. A worker only harvests crops inside it." % ROMAN[i], "reload@config.properties:totem.range%d" % (i + 1))
     for i in range(5)] + \
    [("totem.support%d" % (i + 1), "Tier %s support bonus" % ROMAN[i], "totems", "int", str(SUPPORT_DEF[i]), "0", "1000", "", "%", "live",
      "Percent more crops from each tier %s support totem (Rain, Fertilizer, Fairy Grove ...)." % ROMAN[i],
      "reload@config.properties:totem.support%d" % (i + 1)) for i in range(5)] + [
    ("totem.pads.small", "Totem pads: Small island", "totems", "int", str(PADS_DEF[0]), "1", "5", "", "", "live", "Totems a Small island holds.",
     "reload@config.properties:totem.pads.small"),
    ("totem.pads.medium", "Totem pads: Medium island", "totems", "int", str(PADS_DEF[1]), "1", "5", "", "", "live", "Totems a Medium island holds.",
     "reload@config.properties:totem.pads.medium"),
    ("totem.pads.large", "Totem pads: Large island", "totems", "int", str(PADS_DEF[2]), "1", "5", "", "", "live", "Totems a Large island holds.",
     "reload@config.properties:totem.pads.large"),
    ("totem.boostSec", "Booster burns for", "totems", "int", "3600", "60", "86400", "", "s", "live",
     "Real seconds one booster essence lasts (+2 range and the boost below).", "reload@config.properties:totem.boostSec"),
    ("totem.boostPct", "Booster bonus", "totems", "int", "25", "0", "1000", "", "%", "live", "Percent more for a boosted totem.",
     "reload@config.properties:totem.boostPct"),
    ("totem.upCost", "Tier-up costs (Anvil)", "totems", "text", UP_DEF, "", "120", "", "", "live",
     "Enchanted:essence for I->II, II->III, III->IV, IV->V (the Anvil in SkyyGear uses them).", "reload@config.properties:totem.upCost"),
    ("moon.nightShare", "Night share of the day", "totems", "dec", "0.4", "0", "1", "", "", "live",
     "Share of the time that is night (Harvest Moon, Mushroom Shade; the rest is day for the Sun).", "reload@config.properties:moon.nightShare"),
    ("moon.bonus", "Harvest Moon bonus", "totems", "int", "25", "0", "1000", "", "%", "live", "Percent more crops at night from a Harvest Moon.",
     "reload@config.properties:moon.bonus"),
    ("moon.enchChance", "Harvest Moon Enchanted chance", "totems", "dec", "0.05", "0", "100", "", "%", "live",
     "Percent chance per crop at night of a bonus Enchanted crop (x Rare Finder, x Moon Blade).", "reload@config.properties:moon.enchChance"),
    ("craft.shardRebirth", "Rebirths to craft a shard", "costs", "int", "2", "0", "100", "", "", "live",
     "Rebirths a profile needs before it can craft an extra shard (Skyy: after rebirth 2).", "reload@config.properties:craft.shardRebirth"),
] + [("craft.%s" % _r[0], "Recipe: %s" % _r[0].replace("Skyy_TotemMod_", "Modifier ").replace("Skyy_Totem_", "Totem ").replace("Skyy_Shard_", "Shard "),
      "crafting", "text", _r[1], "", "300", "", "", "live", "Item:qty,Item:qty;coins - empty switches this recipe off.",
      "reload@config.properties:craft.%s" % _r[0]) for _r in RECIPES] + [("storage.tier%d" % (i + 1), "Storage tier %d (stacks)" % (i + 1), "production", "int", str(STORE_STACKS[i]), "1", "1000", "", "", "live",
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
               FILES=["Skyy_SkyyShards/config.properties"], NOTE="Shard islands (Farming shard + totems). Changes are live.",
               RELOAD="ShCfg.reloadKit", KEEP=10, DEFAULTS={"config.properties": CONFIG_TEXT})

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
         "  RATE1 = decOf(p.getProperty(\"totem.rate1\"), 1.0, 0.0, 100.0);"]
# 0.2: the totem rows (arrays are swapped whole - a reader never sees a half-filled table)
_load += ["  double[] rt = new double[5]; rt[0] = RATE1;"]
_load += ["  rt[%d] = decOf(p.getProperty(\"totem.rate%d\"), %r, 0.0, 100.0);" % (i, i + 1, RATE_DEF[i]) for i in range(1, 5)]
_load += ["  RATES = rt;", "  WORKER_MAX = decOf(p.getProperty(\"totem.workerMax\"), %r, 0.0, 1000.0);" % WMAX_DEF, "  int[] rg = new int[5];"]
_load += ["  rg[%d] = intOf(p.getProperty(\"totem.range%d\"), %d, 0, 30);" % (i, i + 1, RANGE_DEF[i]) for i in range(5)]
_load += ["  RANGES = rg;", "  int[] sp = new int[5];"]
_load += ["  sp[%d] = intOf(p.getProperty(\"totem.support%d\"), %d, 0, 1000);" % (i, i + 1, SUPPORT_DEF[i]) for i in range(5)]
_load += ["  SUPPORT = sp;", "  int[] pd = new int[3];"]
_load += ["  pd[%d] = intOf(p.getProperty(\"totem.pads.%s\"), %d, 1, 5);" % (i, n, PADS_DEF[i]) for i, n in enumerate(("small", "medium", "large"))]
_load += ["  PADS = pd;",
          "  BOOST_SEC = intOf(p.getProperty(\"totem.boostSec\"), 3600, 60, 86400);",
          "  BOOST_PCT = intOf(p.getProperty(\"totem.boostPct\"), 25, 0, 1000);",
          "  String uc = p.getProperty(\"totem.upCost\");",
          "  UP_COST = (uc == null || uc.trim().length() == 0) ? %s : uc.trim();" % jlit(UP_DEF),
          "  NIGHT = decOf(p.getProperty(\"moon.nightShare\"), 0.4, 0.0, 1.0);",
          "  MOON_BONUS = intOf(p.getProperty(\"moon.bonus\"), 25, 0, 1000);",
          "  ENCH_CH = decOf(p.getProperty(\"moon.enchChance\"), 0.05, 0.0, 100.0);",
          "  SHARD_RB = intOf(p.getProperty(\"craft.shardRebirth\"), 2, 0, 100);",
          "  String[] cr = new String[CRAFT_ID.length];",
          "  for (int ci = 0; ci < CRAFT_ID.length; ci++) { String cv = p.getProperty(\"craft.\" + CRAFT_ID[ci]); cr[ci] = cv == null ? DEF_CRAFT[ci] : cv.trim(); }",
          "  CRAFT = cr;"]
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
# 0.2: the kit's RELOAD (the totem / crafting rows are reload@ rows: arrays live in the loader, not in field: bindings)
M(cfg, r"""
public static void reloadKit() {
  try { info("settings re-read: " + loadCfg(false)); } catch (Throwable t) { warn("settings re-read failed: " + t); }
}""")
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
  if (p.getProperty("pkey") == null) p.setProperty("pkey", k);   // 0.2: the Harvest Moon roll seed + the Moon Blade lookup know whose shard it is
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

# ================= 0.2 ShTotem: the totem table, entries, documents and the per-totem maths (pure; any thread) =================
# An island's totems: farming.i<n>.totems = "type:tier:m1:m2:boostUntil:uid,..." (0.1: "harvest_spirit:1" = a Harvest Spirit I, no uid).
# Entry i stands on pad i. A field array f = { type, tier, m1, m2, boostUntil, uid } (tier "1".."5", boostUntil "0" = none).
tot = mk("ShTotem")
F(tot, "public static final String[] KEYS = new String[] { %s };" % ", ".join(jlit(t[0]) for t in TOTEMS))
F(tot, "public static final String[] ITEMS = new String[] { %s };" % ", ".join(jlit(x) for x in TOTEM_ITEM))
F(tot, "public static final String[] BLOCKS = new String[] { %s };" % ", ".join(jlit(x) for x in TOTEM_BLOCK))
F(tot, "public static final String[] NAMES = new String[] { %s };" % ", ".join(jlit(t[2]) for t in TOTEMS))
F(tot, "public static final boolean[] WORKER = new boolean[] { %s };" % ", ".join("true" if t[3] else "false" for t in TOTEMS))
F(tot, "public static final boolean[] FARM = new boolean[] { %s };" % ", ".join("true" if KIND in t[4] else "false" for t in TOTEMS))
F(tot, "public static final int[] EFFECT = new int[] { %s };" % ", ".join(str(EFF[t[5]]) for t in TOTEMS))
F(tot, "public static final String[] SHARD = new String[] { %s };" % ", ".join(jlit(t[4][0]) for t in TOTEMS))
F(tot, "public static final String[] MOD_KEYS = new String[] { %s };" % ", ".join(jlit(m[0]) for m in MODS))
F(tot, "public static final String[] MOD_ITEMS = new String[] { %s };" % ", ".join(jlit(x) for x in MOD_ITEM))
F(tot, "public static final String[] MOD_NAMES = new String[] { %s };" % ", ".join(jlit(m[2]) for m in MODS))
F(tot, "public static final String[] MOD_DESC = new String[] { %s };" % ", ".join(jlit(m[3]) for m in MODS))
F(tot, "public static final String[] BOOSTERS = new String[] { %s };" % ", ".join(jlit(x) for x in BOOSTERS))
F(tot, "public static final String[] ROMAN = new String[] { %s };" % ", ".join(jlit(x) for x in ROMAN))
F(tot, 'public static final String DOC_KEY = "SkyyTotem";')
F(tot, "public static final int[] PDX = new int[] { %s };" % ", ".join(str(p[0]) for p in PADS))
F(tot, "public static final int[] PDZ = new int[] { %s };" % ", ".join(str(p[1]) for p in PADS))
F(tot, "public static final int COV_R = %d;" % COV_R)
for _s in range(3):
    F(tot, "public static final int[] COV%d = new int[] { %s };" % (_s + 1, ", ".join(str(x) for x in COV[_s])))
F(tot, "public static volatile java.util.function.Function MOON_TEST = null;")      # harness: the gear:fn:moonblade stand-in
F(tot, "public static final java.util.concurrent.ConcurrentHashMap MOON_CACHE = new java.util.concurrent.ConcurrentHashMap();")
M(tot, r"""
public static int idx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(key)) return i;
  return -1;
}""")
M(tot, r"""
public static int itemIdx(String id) {
  if (id == null) return -1;
  for (int i = 0; i < ITEMS.length; i++) if (ITEMS[i].equals(id)) return i;
  return -1;
}""")
M(tot, r"""
public static int modIdx(String key) {
  if (key == null || key.length() == 0) return -1;
  for (int i = 0; i < MOD_KEYS.length; i++) if (MOD_KEYS[i].equals(key)) return i;
  return -1;
}""")
M(tot, r"""
public static int modItemIdx(String id) {
  if (id == null) return -1;
  for (int i = 0; i < MOD_ITEMS.length; i++) if (MOD_ITEMS[i].equals(id)) return i;
  return -1;
}""")
M(tot, r"""
public static boolean isBooster(String id) {
  if (id == null) return false;
  for (int i = 0; i < BOOSTERS.length; i++) if (BOOSTERS[i].equals(id)) return true;
  return false;
}""")
M(tot, r"""
public static int tierOf(String s) {
  int t = 1;
  try { t = Integer.parseInt(s.trim()); } catch (Throwable x) { t = 1; }
  if (t < 1) t = 1;
  if (t > 5) t = 5;
  return t;
}""")
# one entry -> { type, tier, m1, m2, boostUntil, uid } (missing parts = defaults; unknown modifiers dropped)
M(tot, r"""
public static String[] parse(String e) {
  String[] f = new String[] { "", "1", "", "", "0", "" };
  if (e == null) return f;
  String[] a = e.trim().split(":", -1);
  if (a.length > 0) f[0] = a[0].trim();
  if (a.length > 1) f[1] = String.valueOf(tierOf(a[1]));
  if (a.length > 2 && modIdx(a[2].trim()) >= 0) f[2] = a[2].trim();
  if (a.length > 3 && modIdx(a[3].trim()) >= 0) f[3] = a[3].trim();
  if (a.length > 4) { long u = 0L; try { u = Long.parseLong(a[4].trim()); } catch (Throwable x) { u = 0L; } f[4] = String.valueOf(u < 0L ? 0L : u); }
  if (a.length > 5) f[5] = a[5].trim().replace(",", "").replace(":", "");
  return f;
}""")
M(tot, r"""
public static String fmt(String[] f) {
  return f[0] + ":" + f[1] + ":" + f[2] + ":" + f[3] + ":" + f[4] + ":" + f[5];
}""")
M(tot, r"""
public static String[] entries(java.util.Properties p, int slot) {
  String s = @PKG@.ShStore.str(p, "@K@.i" + slot + ".totems");
  if (s.length() == 0) return new String[0];
  String[] a = s.split(",");
  int n = 0;
  for (int i = 0; i < a.length; i++) if (a[i].trim().length() > 0) n++;
  String[] out = new String[n];
  int j = 0;
  for (int i = 0; i < a.length; i++) if (a[i].trim().length() > 0) { out[j] = a[i].trim(); j++; }
  return out;
}""".replace("@K@", KIND_KEY))
M(tot, r"""
public static void setEntries(java.util.Properties p, int slot, String[] e) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < e.length; i++) { if (i > 0) sb.append(','); sb.append(e[i]); }
  p.setProperty("@K@.i" + slot + ".totems", sb.toString());
}""".replace("@K@", KIND_KEY))
M(tot, r"""
public static String newUid() {
  return java.util.UUID.randomUUID().toString().replace("-", "").substring(0, 12);
}""")
M(tot, r"""
public static int countMod(String[] f, String key) {
  int n = 0;
  if (key.equals(f[2])) n++;
  if (key.equals(f[3])) n++;
  return n;
}""")
M(tot, r"""
public static boolean boosted(String[] f, long t) {
  long u = 0L;
  try { u = Long.parseLong(f[4]); } catch (Throwable x) { u = 0L; }
  return u > t;
}""")
M(tot, r"""
public static int range(String[] f, long t) {
  int tier = tierOf(f[1]);
  int r = @PKG@.ShCfg.RANGES[tier - 1] + 2 * countMod(f, "wider") + (boosted(f, t) ? 2 : 0);
  return r < 0 ? 0 : r;
}""")
M(tot, r"""
public static int cov(int size, int r) {
  int rr = r < 0 ? 0 : (r > COV_R ? COV_R : r);
  if (size >= 3) return COV3[rr];
  if (size == 2) return COV2[rr];
  return COV1[rr];
}""")
M(tot, r"""
public static double ownMult(String[] f, long t) {
  double m = 1.0 + 0.2 * (double) countMod(f, "faster") + 0.1 * (double) countMod(f, "replant") + 0.1 * (double) countMod(f, "compost");
  if (boosted(f, t)) m = m * (1.0 + (double) @PKG@.ShCfg.BOOST_PCT / 100.0);
  return m;
}""")
# a worker's items / minute on an island of `size`: min(tier speed x (crops in range / crops in the Harvest Spirit I range on a Small
# island), totem.workerMax) x its own modifiers / booster
M(tot, r"""
public static double workerRate(String[] f, int size, long t) {
  int ti = idx(f[0]);
  if (ti < 0 || !WORKER[ti] || !FARM[ti]) return 0.0;
  int ref = cov(1, @PKG@.ShCfg.RANGES[0]);
  if (ref < 1) ref = 1;
  double reach = (double) cov(size, range(f, t)) / (double) ref;
  double base = @PKG@.ShCfg.RATES[tierOf(f[1]) - 1] * reach;
  double mx = @PKG@.ShCfg.WORKER_MAX;
  if (mx > 0.0 && base > mx) base = mx;   // fix4: spec 9.2 / 9.3 ceiling (totem.workerMax 12) before the totem's own modifiers / booster
  return base * ownMult(f, t);
}""")
# a support totem's percent (day / night ones x the share; Harvest Moon = moon.bonus at night)
M(tot, r"""
public static double supportPct(String[] f, long t) {
  int ti = idx(f[0]);
  if (ti < 0 || WORKER[ti] || !FARM[ti]) return 0.0;
  int e = EFFECT[ti];
  double base = e == 4 ? (double) @PKG@.ShCfg.MOON_BONUS : (double) @PKG@.ShCfg.SUPPORT[tierOf(f[1]) - 1];
  double share = 1.0;
  if (e == 2) share = 1.0 - @PKG@.ShCfg.NIGHT;
  if (e == 3 || e == 4) share = @PKG@.ShCfg.NIGHT;
  return base * share * ownMult(f, t);
}""")
# the island's rate at time t (items / minute; no worker = 0)
M(tot, r"""
public static double islandRate(java.util.Properties p, int slot, int size, long t) {
  String[] e = entries(p, slot);
  double w = 0.0;
  double s = 0.0;
  for (int i = 0; i < e.length; i++) {
    String[] f = parse(e[i]);
    w += workerRate(f, size, t);
    s += supportPct(f, t);
  }
  if (w <= 0.0) return 0.0;
  return w * (1.0 + s / 100.0);
}""")
# the next boost end in (from, to), else to (the settle splits time there)
M(tot, r"""
public static long nextBreak(java.util.Properties p, int slot, long from, long to) {
  String[] e = entries(p, slot);
  long b = to;
  for (int i = 0; i < e.length; i++) {
    String[] f = parse(e[i]);
    long u = 0L;
    try { u = Long.parseLong(f[4]); } catch (Throwable x) { u = 0L; }
    if (u > from && u < b) b = u;
  }
  return b;
}""")
M(tot, r"""
public static int modsOnIsland(java.util.Properties p, int slot, String key) {
  String[] e = entries(p, slot);
  int n = 0;
  for (int i = 0; i < e.length; i++) n += countMod(parse(e[i]), key);
  return n;
}""")
# the owner's Moon Blade factor (SkyyGear's sickle roll through gear:fn:moonblade, 1..5; absent = 1), cached 60 s per profile. fix4: while
# ShStore.LOCK is held (every settle) only the cache is read (stale value, else 1) - the bridge is asked by ShCore.pauseStale / the admin
# info BEFORE the lock (gate, start, the menu fill and Collect all pass there), so a later SkyyGear that hops threads can never deadlock
M(tot, r"""
public static double moonBlade(String k) {
  if (k == null) return 1.0;
  try {
    Object c = MOON_CACHE.get(k);
    long now = System.currentTimeMillis();
    if (c instanceof double[] && now - (long) ((double[]) c)[1] < 60000L) return ((double[]) c)[0];
    if (@PKG@.ShStore.LOCK.isHeldByCurrentThread()) return c instanceof double[] ? ((double[]) c)[0] : 1.0;   // fix4: no bridge call under the lock (warmed before it)
    java.util.function.Function g = MOON_TEST != null ? MOON_TEST : @PKG@.ShCfg.fn("gear:fn:moonblade");
    Object r = g == null ? null : g.apply(k);
    double m = r instanceof Number ? ((Number) r).doubleValue() : 1.0;
    if (Double.isNaN(m) || m < 1.0) m = 1.0;
    if (m > 5.0) m = 5.0;
    MOON_CACHE.put(k, new double[] { m, (double) now });
    return m;
  } catch (Throwable t) { return 1.0; }
}""")
# the chance per crop of a bonus Enchanted crop (a Harvest Moon on the island; night share x (1 + Rare Finders) x Moon Blade)
M(tot, r"""
public static double enchChance(java.util.Properties p, int slot) {
  String[] e = entries(p, slot);
  boolean moon = false;
  for (int i = 0; i < e.length; i++) if ("harvest_moon".equals(parse(e[i])[0])) moon = true;
  if (!moon) return 0.0;
  double c = @PKG@.ShCfg.ENCH_CH / 100.0 * @PKG@.ShCfg.NIGHT * (1.0 + (double) modsOnIsland(p, slot, "rare")) * moonBlade(p.getProperty("pkey"));
  return c > 1.0 ? 1.0 : (c < 0.0 ? 0.0 : c);
}""")
M(tot, r"""
public static String name(String[] f) {
  int ti = idx(f[0]);
  return (ti < 0 ? f[0] : NAMES[ti]) + " " + ROMAN[tierOf(f[1]) - 1];
}""")
# ---- the item document (key "SkyyTotem"): { v, t, tier, m1, m2, bst = booster ms left, uid }
M(tot, r"""
public static @BD@ doc(String[] f, long now) {
  long u = 0L;
  try { u = Long.parseLong(f[4]); } catch (Throwable x) { u = 0L; }
  long left = u > now ? u - now : 0L;
  @BD@ d = new @BD@();
  d.append("v", new org.bson.BsonInt32(1));
  d.append("t", new org.bson.BsonString(f[0]));
  d.append("tier", new org.bson.BsonInt32(tierOf(f[1])));
  d.append("m1", new org.bson.BsonString(f[2]));
  d.append("m2", new org.bson.BsonString(f[3]));
  d.append("bst", new org.bson.BsonInt64(left));
  d.append("uid", new org.bson.BsonString(f[5]));
  return d;
}""")
M(tot, r"""
public static String dstr(@BD@ d, String k) {
  try { @BV@ v = d.get(k); return v != null && v.isString() ? v.asString().getValue() : ""; } catch (Throwable t) { return ""; }
}""")
M(tot, r"""
public static long dlong(@BD@ d, String k) {
  try {
    @BV@ v = d.get(k);
    if (v == null) return 0L;
    if (v.isInt64()) return v.asInt64().getValue();
    if (v.isInt32()) return (long) v.asInt32().getValue();
  } catch (Throwable t) { }
  return 0L;
}""")
# a document -> fields (the booster's time left starts again at `now`); a type that does not match the item is refused (null)
M(tot, r"""
public static String[] fromDoc(@BD@ d, String itemId, long now) {
  int ti = itemIdx(itemId);
  if (ti < 0) return null;
  String[] f = new String[] { KEYS[ti], "1", "", "", "0", "" };
  if (d == null) return f;
  String t = dstr(d, "t");
  if (t.length() > 0 && !t.equals(KEYS[ti])) return null;
  f[1] = String.valueOf(tierOf(String.valueOf(dlong(d, "tier"))));
  if (modIdx(dstr(d, "m1")) >= 0) f[2] = dstr(d, "m1");
  if (modIdx(dstr(d, "m2")) >= 0) f[3] = dstr(d, "m2");
  long b = dlong(d, "bst");
  f[4] = String.valueOf(b > 0L ? now + b : 0L);
  f[5] = dstr(d, "uid").replace(",", "").replace(":", "");
  return f;
}""")
M(tot, r"""
public static @BD@ docOf(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return null;
    @BD@ md = s.getMetadata();
    if (md == null) return null;
    @BV@ v = md.get(DOC_KEY);
    return v != null && v.isDocument() ? v.asDocument() : null;
  } catch (Throwable t) { return null; }
}""")
M(tot, r"""
public static String desc(String[] f, long now) {
  int ti = idx(f[0]);
  StringBuilder sb = new StringBuilder();
  sb.append(ti >= 0 && WORKER[ti] ? "Worker - harvests the crops in range" : "Support - more crops for its island");
  sb.append("\nRange ").append(range(f, now)).append(" blocks");
  sb.append("\nModifiers: ").append(f[2].length() == 0 ? "-" : MOD_NAMES[modIdx(f[2])]).append(", ").append(f[3].length() == 0 ? "-" : MOD_NAMES[modIdx(f[3])]);
  long u = 0L;
  try { u = Long.parseLong(f[4]); } catch (Throwable x) { u = 0L; }
  if (u > now) sb.append("\nBooster: ").append((u - now + 59999L) / 60000L).append(" min left");
  if (ti >= 0 && !FARM[ti]) sb.append("\nWorks in the ").append(SHARD[ti]).append(" Shard (a later update).");
  sb.append("\nPlace it from the shard menu (Totems tab).");
  return sb.toString();
}""")
# the item stack for a totem (its document + the tier in the name)
M(tot, r"""
public static @IS@ stack(String[] f, long now) {
  int ti = idx(f[0]);
  if (ti < 0) return null;
  @IS@ s = new @IS@(ITEMS[ti], 1);
  s = s.withMetadata(DOC_KEY, (@BV@) doc(f, now));
  try { s = s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(@MSG@.raw(name(f)).color("@GOLDC@"), @MSG@.raw(desc(f, now)))); } catch (Throwable t) { }
  return s;
}""".replace("@GOLDC@", SUI.COLOR["gold"]))
# tier-up cost I->II .. IV->V from totem.upCost ("ench:essence,...") -> { enchanted, essence } or null (max tier / bad text)
M(tot, r"""
public static int[] upCost(int tier) {
  if (tier < 1 || tier >= 5) return null;
  try {
    String[] a = @PKG@.ShCfg.UP_COST.split(",");
    if (tier - 1 >= a.length) return null;
    String[] b = a[tier - 1].trim().split(":");
    int e = Integer.parseInt(b[0].trim());
    int s = Integer.parseInt(b[1].trim());
    if (e < 0 || s < 0) return null;
    return new int[] { e, s };
  } catch (Throwable t) { return null; }
}""")
# shard:fn:totem (SkyyGear's Anvil calls it later): Object[]{ String op, String itemId, String docJson } -> String
M(tot, r"""
public static String bridge(String op, String itemId, String json) {
  if ("key".equals(op)) return DOC_KEY;
  int ti = itemIdx(itemId);
  if (ti < 0) return "err:not a totem";
  @BD@ d = null;
  try { if (json != null && json.trim().length() > 0) d = @BD@.parse(json); } catch (Throwable t) { return "err:bad document"; }
  String[] f = fromDoc(d, itemId, 0L);
  if (f == null) return "err:the document is another totem type";
  int tier = tierOf(f[1]);
  if ("describe".equals(op)) return name(f) + " - range " + range(f, 0L) + " - " + (WORKER[ti] ? "worker" : "support");
  if (!FARM[ti]) return "err:its shard comes in a later update";
  int[] c = upCost(tier);
  if (c == null) return tier >= 5 ? "err:max tier" : "err:the tier-up cost setting is broken (totem.upCost)";
  if ("cost".equals(op)) return "@ENCH@:" + c[0] + ",Ingredient_Life_Essence:" + c[1];
  if ("up".equals(op)) {
    @BD@ nd = d == null ? doc(f, 0L) : d.clone();
    nd.put("tier", new org.bson.BsonInt32(tier + 1));
    if (!nd.containsKey("uid") || dstr(nd, "uid").length() == 0) nd.put("uid", new org.bson.BsonString(newUid()));
    return nd.toJson();
  }
  return "err:unknown op";
}""".replace("@ENCH@", CROP["ench"]))
# a readable name for an item id (the craft tab, chat lines)
M(tot, r"""
public static String pretty(String id) {
  if (id == null) return "";
  int ti = itemIdx(id);
  if (ti >= 0) return NAMES[ti] + " " + ROMAN[0];
  int mi = modItemIdx(id);
  if (mi >= 0) return MOD_NAMES[mi] + " modifier";
  if (id.equals("@SHARD@")) return "Farming Shard";
  String s = id;
  if (s.startsWith("Skyy_Ench_")) s = "Enchanted " + s.substring(10);
  else if (s.startsWith("Ingredient_")) s = s.substring(11);
  else if (s.startsWith("Plant_Crop_")) s = s.substring(11);
  else if (s.startsWith("Plant_Seeds_")) s = s.substring(12) + " Seeds";
  else if (s.startsWith("Weapon_Wand_")) s = s.substring(12);
  s = s.replace("_Item", "").replace('_', ' ');
  return s;
}""".replace("@SHARD@", SHARD_ITEM))
tfn = mk("ShTotemFn", None, ("java.util.function.Function",))
C(tfn, "public ShTotemFn() { }")
M(tfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return "err:bad arguments";
    Object[] a = (Object[]) o;
    if (a.length < 1) return "err:bad arguments";
    return @PKG@.ShTotem.bridge(String.valueOf(a[0]), a.length > 1 && a[1] != null ? String.valueOf(a[1]) : null, a.length > 2 && a[2] != null ? String.valueOf(a[2]) : null);
  } catch (Throwable t) { return "err:" + t; }
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
# 0.2: one island's cap = the shard storage + 3 stacks per Storage modifier on its totems
M(mth, r"""
public static long capOf(java.util.Properties p, int slot) {
  return cap(p) + 300L * (long) @PKG@.ShTotem.modsOnIsland(p, slot, "storage");
}""")
M(mth, r"""
public static int pads(int size) {
  int[] a = @PKG@.ShCfg.PADS;
  int n = a[size >= 3 ? 2 : (size == 2 ? 1 : 0)];
  return n < 1 ? 1 : (n > 5 ? 5 : n);
}""")
M(mth, r"""
public static int totems(java.util.Properties p, int slot) {
  return @PKG@.ShTotem.entries(p, slot).length;
}""")
# 0.2: the island's rate (items / minute) at time t
M(mth, r"""
public static double rate(java.util.Properties p, int slot, long t) {
  if (!hasIsland(p, slot)) return 0.0;
  return @PKG@.ShTotem.islandRate(p, slot, size(p, slot), t);
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
M(mth, r"""
public static long ench(java.util.Properties p, int slot) {
  long s = @PKG@.ShStore.lng(p, ik(slot, "ench"), 0L);
  return s < 0L ? 0L : s;
}""")
# settle one island at `now` (ms): returns the items made. 0.2: the rate is split at every booster end inside (last, now); last moves on by
# exactly the time the made items took (the part-item stays); elapsed is capped at shard.maxOfflineSec; a full store stops production
# (last = now). A Harvest Moon island rolls its bonus Enchanted crops (seeded by island + clock: settling again never re-rolls).
M(mth, r"""
public static long settle(java.util.Properties p, int slot, long now) {
  if (!hasIsland(p, slot)) return 0L;
  long last = @PKG@.ShStore.lng(p, ik(slot, "last"), now);
  long stored = @PKG@.ShStore.lng(p, ik(slot, "stored"), 0L);
  if (stored < 0L) stored = 0L;
  long cap = capOf(p, slot);
  if (last > now) last = now;
  long maxOff = 1000L * (long) @PKG@.ShCfg.MAX_OFF_SEC;
  if (now - last > maxOff) last = now - maxOff;
  long made = 0L;
  long from = last;
  if (paused(p) || stored >= cap) {   // fix (critic): a picked-up shard makes nothing until it is placed again
    last = now;
  } else {
    double acc = 0.0;
    long t = last;
    int guard = 0;
    while (t < now && guard < 64) {
      long b = @PKG@.ShTotem.nextBreak(p, slot, t, now);
      acc += (double) (b - t) * rate(p, slot, t) / 60000.0;
      t = b;
      guard++;
    }
    made = (long) Math.floor(acc + 0.000000001);
    if (made <= 0L) {
      made = 0L;
      if (acc <= 0.0) last = now;
    } else if (stored + made >= cap) {
      made = cap - stored; last = now;
    } else {
      double rem = (double) made;
      long u = last;
      boolean done = false;
      guard = 0;
      while (u < now && guard < 64 && !done) {
        long b = @PKG@.ShTotem.nextBreak(p, slot, u, now);
        double r = rate(p, slot, u);
        double seg = (double) (b - u) * r / 60000.0;
        if (r > 0.0 && rem <= seg + 0.000000001) { last = u + (long) Math.floor(rem * 60000.0 / r); done = true; }
        else { rem -= seg; u = b; }
        guard++;
      }
      if (!done) last = now;
    }
    stored += made;
  }
  p.setProperty(ik(slot, "last"), String.valueOf(last));
  p.setProperty(ik(slot, "stored"), String.valueOf(stored));
  if (made > 0L) {
    double c = @PKG@.ShTotem.enchChance(p, slot);
    if (c > 0.0) {
      String k = p.getProperty("pkey");
      long seed = ((long) slot * 1000003L) ^ (from * 31L) ^ (k == null ? 0L : (long) k.hashCode());
      java.util.Random rnd = new java.util.Random(seed);
      long hit = 0L;
      for (long i = 0L; i < made; i++) if (rnd.nextDouble() < c) hit++;
      if (hit > 0L) p.setProperty(ik(slot, "ench"), String.valueOf(ench(p, slot) + hit));
    }
  }
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
# ms until the island's store is full at the rate of `now` (-1 = never / already full)
M(mth, r"""
public static long msToFull(java.util.Properties p, int slot, long now) {
  double r = rate(p, slot, now);
  long left = capOf(p, slot) - stored(p, slot);
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
# 0.2: kind AIR (8) = an empty totem pad (a totem block there is cleared), kinds TOTEM (9) + type = that totem's block
F(geo, 'public static final String[] IDS = new String[] { %s };' % ", ".join([jlit(BLOCKS[k]) for k in ("grass", "dirt", "till", "stone", "brick", "plank", "crop", "stand")] + ['""'] + [jlit(x) for x in TOTEM_BLOCK]))
for _n, _k in enumerate(("GRASS", "DIRT", "TILL", "STONE", "BRICK", "PLANK", "CROP", "STAND", "AIR", "TOTEM")):
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
# 0.2: the pad position of pad `pad` on island `slot` (x, y, z)
M(geo, r"""
public static int[] padPos(int slot, int pad) {
  int k = pad < 0 ? 0 : (pad > 4 ? 4 : pad);
  return new int[] { OX + SX[slot] + @PKG@.ShTotem.PDX[k], Y + 1, OZ + SZ[slot] + @PKG@.ShTotem.PDZ[k] };
}""")
# 0.2: every pad of the island: entry i stands on pad i (its block), every other pad AIR (a totem block left there is cleared)
M(geo, r"""
public static void pads(java.util.ArrayList out, java.util.Properties p, int slot) {
  String[] e = @PKG@.ShTotem.entries(p, slot);
  for (int i = 0; i < 5; i++) {
    int[] q = padPos(slot, i);
    int ti = i < e.length ? @PKG@.ShTotem.idx(@PKG@.ShTotem.parse(e[i])[0]) : -1;
    add(out, q[0], q[1], q[2], ti >= 0 ? TOTEM + ti : AIR);
  }
}""")
# everything the profile's region wants, in paint order (hub, bridges, islands - a later block wins its position)
M(geo, r"""
public static java.util.ArrayList region(java.util.Properties p) {
  java.util.ArrayList out = new java.util.ArrayList();
  hub(out);
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(p, i)) bridge(out, i);
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(p, i)) island(out, i, @PKG@.ShMath.size(p, i));
  for (int i = 0; i < SLOTS_N(); i++) if (@PKG@.ShMath.hasIsland(p, i)) pads(out, p, i);   // 0.2: the totems on their pads
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
    if (b[3] == @PKG@.ShGeo.AIR) { if (cur.length() > 0) n += clear(w, b[0], b[1], b[2]); continue; }   // 0.2: an empty totem pad
    if (b[3] >= @PKG@.ShGeo.TOTEM) { if (cur.indexOf(id) < 0) n += put(w, b[0], b[1], b[2], id); continue; }   // 0.2: a totem (any rotation state)
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
  if (a.equals("use")) return Boolean.valueOf(crop(block) || (block != null && (block.indexOf("@SHARD@") >= 0 || block.indexOf("Skyy_TotemBlock_") >= 0)));   // 0.2: a totem opens its page
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

# 0.2: one stack WITH its metadata (a totem + its document): the first section that can take it; true = it arrived (counted by id)
M(inv, r"""
public static boolean giveStack(@IC@[] cs, @IS@ st) {
  if (cs == null || st == null) return false;
  String id = st.getItemId();
  int q = st.getQuantity();
  long before = count(cs, id);
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    boolean can = false;
    try { can = cs[i].canAddItemStack(st); } catch (Throwable t) { can = false; }
    if (!can) continue;
    try { cs[i].addItemStack(st); } catch (Throwable t) { @PKG@.ShCfg.warnOnce("givestack:" + id, "could not give " + id + ": " + t); }
    break;
  }
  return count(cs, id) >= before + (long) q;
}""")
# 0.2: every totem item in the inventory: Object[]{ Integer section, Integer slot, String itemId, BsonDocument or null }
M(inv, r"""
public static java.util.ArrayList totems(@IC@[] cs) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (cs == null) return out;
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    short cap = cs[i].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[i].getItemStack(s);
      if (it == null || it.isEmpty() || @PKG@.ShTotem.itemIdx(it.getItemId()) < 0) continue;
      out.add(new Object[] { Integer.valueOf(i), Integer.valueOf((int) s), it.getItemId(), @PKG@.ShTotem.docOf(it) });
    }
  }
  return out;
}""")
# 0.2: take ONE item from exactly that slot if it still holds `id` (and the same uid when one is given); true = one less (counted)
M(inv, r"""
public static boolean takeSlot(@IC@[] cs, int ci, int slot, String id, String uid) {
  if (cs == null || ci < 0 || ci >= cs.length || cs[ci] == null) return false;
  @IS@ it = cs[ci].getItemStack((short) slot);
  if (it == null || it.isEmpty() || !id.equals(it.getItemId())) return false;
  if (uid != null && uid.length() > 0 && !uid.equals(@PKG@.ShTotem.dstr(@PKG@.ShTotem.docOf(it), "uid"))) return false;
  long before = count(cs, id);
  try { cs[ci].removeItemStackFromSlot((short) slot, 1); } catch (Throwable t) { return false; }
  return count(cs, id) == before - 1L;
}""")
# 0.2: where the totem with this uid is (int[]{ section, slot }) or null
M(inv, r"""
public static int[] findUid(@IC@[] cs, String id, String uid) {
  java.util.ArrayList l = totems(cs);
  for (int i = 0; i < l.size(); i++) {
    Object[] a = (Object[]) l.get(i);
    if (!id.equals(a[2])) continue;
    if (uid.equals(@PKG@.ShTotem.dstr((@BD@) a[3], "uid"))) return new int[] { ((Integer) a[0]).intValue(), ((Integer) a[1]).intValue() };
  }
  return null;
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
  @PKG@.ShTotem.moonBlade(k);   // fix4: warm the Moon Blade cache outside ShStore.LOCK (settle reads only the cache)
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
# 0.2: + the bonus Enchanted crops (farming.i<n>.ench) - debited with the wheat, given as Skyy_Ench_Wheat, credited as 100 Wheat each
M(core, r"""
public static String collect(java.util.UUID u, String k, int slot, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read - ask an admin to look at the server log.";
  String no = gate(u, k, p);
  if (no != null) return no;
  long want = 0L; long given = 0L; long back = 0L;
  long wantE = 0L; long givenE = 0L; long backE = 0L;
  @PKG@.ShStore.LOCK.lock(); try {
    long now = now();
    @PKG@.ShMath.settleAll(p, now);
    long[] take = new long[@PKG@.ShMath.SLOTS];
    long[] takeE = new long[@PKG@.ShMath.SLOTS];
    for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) {
      if (slot >= 0 && i != slot) continue;
      take[i] = @PKG@.ShMath.stored(p, i);
      takeE[i] = @PKG@.ShMath.ench(p, i);
      want += take[i];
      wantE += takeE[i];
    }
    if (want + wantE <= 0L) return "=Nothing is stored there yet.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    for (int i = 0; i < take.length; i++) {
      if (take[i] > 0L) p.setProperty(@PKG@.ShMath.ik(i, "stored"), String.valueOf(@PKG@.ShMath.stored(p, i) - take[i]));
      if (takeE[i] > 0L) p.setProperty(@PKG@.ShMath.ik(i, "ench"), String.valueOf(@PKG@.ShMath.ench(p, i) - takeE[i]));
    }
    p.setProperty("lastCollect", String.valueOf(now));   // fix2: the Collect tab's "Last collected ... ago"
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); @PKG@.ShCfg.warn("Collect refused (debit not written): " + err); return "-Collect failed: the shard file could not be saved. Nothing was taken."; }
    given = @PKG@.ShInv.give(cs, ITEM, want);
    givenE = @PKG@.ShInv.give(cs, ENCH, wantE);
    back = want - given;
    backE = wantE - givenE;
    if (back > 0L || backE > 0L) {
      long b1 = back; long b2 = backE;
      for (int i = take.length - 1; i >= 0 && (b1 > 0L || b2 > 0L); i--) {
        if (take[i] > 0L && b1 > 0L) { long r = Math.min(take[i], b1); p.setProperty(@PKG@.ShMath.ik(i, "stored"), String.valueOf(@PKG@.ShMath.stored(p, i) + r)); b1 -= r; }
        if (takeE[i] > 0L && b2 > 0L) { long r = Math.min(takeE[i], b2); p.setProperty(@PKG@.ShMath.ik(i, "ench"), String.valueOf(@PKG@.ShMath.ench(p, i) + r)); b2 -= r; }
      }
      String e2 = @PKG@.ShStore.save(k, p);
      if (e2 != null) @PKG@.ShCfg.warn("Collect: " + back + " + " + backE + " Enchanted items that did not fit are back in memory but not on disk yet: " + e2);
    }
    @PKG@.ShStore.log(u + " " + k + " slot " + slot + " debit " + want + " given " + given + " back " + back + (wantE > 0L ? " ench debit " + wantE + " given " + givenE + " back " + backE : ""));
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  String extra = "";
  long base = given + 100L * givenE;   // the alias rule: an Enchanted crop counts as 100 of its base item
  if (base > 0L) {
    long xp = base * (long) @PKG@.ShCfg.XP_WHEAT * (long) @PKG@.ShCfg.XP_PCT / 100L;
    long xpLeft = owedXp(u, xp);   // fix (critic): unpaid XP waits in the collector's file and is paid on a later Collect
    if (xpLeft > 0L) extra = extra + " (" + @PKG@.ShCfg.num(xpLeft) + " Farming XP waits - paid on your next Collect)";
    else if (xp > 0L) extra = extra + " +" + @PKG@.ShCfg.num(xp) + " Farming XP";
    long owedC = owed(u, base);
    if (owedC > 0L) extra = extra + " - " + @PKG@.ShCfg.num(owedC) + " Wheat collection count waiting";
  }
  if (base <= 0L) return "-Your inventory is full - nothing was collected.";
  String got = @PKG@.ShCfg.num(given) + " Wheat" + (givenE > 0L ? " + " + @PKG@.ShCfg.num(givenE) + " Enchanted Wheat (Harvest Moon)" : "");
  long left = back + backE;
  return "+Collected " + got + extra + (left > 0L ? ". " + @PKG@.ShCfg.num(left) + " did not fit and stay in the shard." : ".");
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

F(core, "public static final java.util.concurrent.ConcurrentHashMap RANGE = new java.util.concurrent.ConcurrentHashMap();")   # world -> double[]{x, y, z, r, until}
# ================= 0.2 ShCore: TOTEM actions (menu clicks, world thread; each re-checks gate(); the item / record order never makes a copy) =================
M(core, r"""
public static void tlog(String line) {
  @PKG@.ShStore.log("totem " + line);
}""")
# the entry fields of pad `pad` on island `slot` (null = none)
M(core, r"""
public static String[] at(java.util.Properties p, int slot, int pad) {
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS || !@PKG@.ShMath.hasIsland(p, slot)) return null;
  String[] e = @PKG@.ShTotem.entries(p, slot);
  if (pad < 0 || pad >= e.length) return null;
  return @PKG@.ShTotem.parse(e[pad]);
}""")
M(core, r"""
public static void put(java.util.Properties p, int slot, int pad, String[] f) {
  String[] e = @PKG@.ShTotem.entries(p, slot);
  if (pad >= 0 && pad < e.length) { e[pad] = @PKG@.ShTotem.fmt(f); @PKG@.ShTotem.setEntries(p, slot, e); }
}""")
# the common start of a totem click: null = go on (p in out[0]), else the refusal line
M(core, r"""
public static String start(java.util.UUID u, String k, @IC@[] cs, Object[] out) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  String no = gate(u, k, p);
  if (no != null) return no;
  if (!k.equals(@PKG@.ShCfg.pkey(u))) return "-Only the island owner can place, pick up or change totems.";   // fix3: co-op never (even with shard.coopCollect)
  out[0] = p;
  return null;
}""")
# fix3: the island + pad already holding a totem with this uid (int[]{slot, pad}) or null - a crash between placing (record written) and
# the inventory save would leave the item AND the record; the copy is refused (and removed) instead of placed twice
M(core, r"""
public static int[] uidAt(java.util.Properties p, String uid) {
  if (uid == null || uid.length() == 0) return null;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
    if (!@PKG@.ShMath.hasIsland(p, s)) continue;
    String[] e = @PKG@.ShTotem.entries(p, s);
    for (int i = 0; i < e.length; i++) { String[] f = @PKG@.ShTotem.parse(e[i]); if (f != null && uid.equals(f[5])) return new int[] { s, i }; }
  }
  return null;
}""")
# Place the totem in inventory section ci, slot si onto island `slot` (the next free pad). The item is taken first (counted, same uid),
# then the record is written; a refused save gives the SAME document back.
M(core, r"""
public static String placeTotem(java.util.UUID u, String k, int slot, int ci, int si, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  if (slot < 0 || slot >= @PKG@.ShMath.SLOTS) return "-Pick an island first.";
  if (ci < 0 || ci >= cs.length || cs[ci] == null) return "-That totem is not in your inventory any more.";
  @IS@ it = cs[ci].getItemStack((short) si);
  String id = it == null || it.isEmpty() ? null : it.getItemId();
  int ti = @PKG@.ShTotem.itemIdx(id);
  if (ti < 0) return "-That totem is not in your inventory any more.";
  long now = now();
  @BD@ d = @PKG@.ShTotem.docOf(it);
  String[] f = @PKG@.ShTotem.fromDoc(d, id, now);
  if (f == null) return "-That totem's document does not match its item - ask an admin (totem.log).";
  if (!@PKG@.ShTotem.FARM[ti]) return "-The " + @PKG@.ShTotem.NAMES[ti] + " works in the " + @PKG@.ShTotem.SHARD[ti] + " Shard - that shard comes in a later update.";
  String docUid = @PKG@.ShTotem.dstr(d, "uid");
  if (f[5].length() == 0) f[5] = @PKG@.ShTotem.newUid();
  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    int[] dup = uidAt(p, docUid);   // fix3: this exact totem (uid) is placed already = a copy left by a crash -> removed, never placed twice
    if (dup != null) {
      boolean gone = @PKG@.ShInv.takeSlot(cs, ci, si, id, docUid);
      tlog(u + " " + k + " DUPLICATE uid " + docUid + " (placed on island " + (dup[0] + 1) + " pad " + (dup[1] + 1) + ") - copy removed " + gone);
      return "-This totem is already placed on island " + (dup[0] + 1) + " - this was a duplicate copy" + (gone ? " and was removed." : ".") + " (totem.log)";
    }
    if (!@PKG@.ShMath.hasIsland(p, slot)) return "-That slot has no island yet.";
    int sz = @PKG@.ShMath.size(p, slot);
    String[] e = @PKG@.ShTotem.entries(p, slot);
    int pads = @PKG@.ShMath.pads(sz);
    if (e.length >= pads) return "-No free totem pad on this island (" + e.length + " of " + pads + "). Grow it or pick a totem up first.";
    @PKG@.ShMath.settle(p, slot, now);
    if (!@PKG@.ShInv.takeSlot(cs, ci, si, id, docUid)) return "-That totem moved in your inventory - try again.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    String[] ne = new String[e.length + 1];
    for (int i = 0; i < e.length; i++) ne[i] = e[i];
    ne[e.length] = @PKG@.ShTotem.fmt(f);
    @PKG@.ShTotem.setEntries(p, slot, ne);
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) {
      p.clear(); p.putAll(old);
      boolean back = @PKG@.ShInv.giveStack(cs, @PKG@.ShTotem.stack(f, now));
      tlog(u + " " + k + " place " + @PKG@.ShTotem.fmt(f) + " SAVE FAILED " + err + " - item back " + back);
      return "-The totem could not be saved - " + (back ? "it is back in your inventory." : "ask an admin (totem.log).");
    }
    tlog(u + " " + k + " place slot " + slot + " pad " + e.length + " " + @PKG@.ShTotem.fmt(f));
    res = "+Placed " + @PKG@.ShTotem.name(f) + " on island " + (slot + 1) + " (pad " + (e.length + 1) + " of " + pads + ").";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k);
  return res;
}""")
# Pick up the totem on pad `pad`: the item with its EXACT document first (tier, modifiers, booster time left, uid), then the record;
# a refused save takes that item back by uid.
M(core, r"""
public static String pickTotem(java.util.UUID u, String k, int slot, int pad, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  long now = now();
  String res;
  @PKG@.ShStore.LOCK.lock(); try {
    String[] f = at(p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    if (@PKG@.ShTotem.idx(f[0]) < 0) return "-That totem's type is unknown on this server - ask an admin (totem.log).";
    @PKG@.ShMath.settle(p, slot, now);
    if (f[5].length() == 0) f[5] = @PKG@.ShTotem.newUid();
    @IS@ st = @PKG@.ShTotem.stack(f, now);
    if (!@PKG@.ShInv.giveStack(cs, st)) return "-Make room in your inventory first.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    String[] e = @PKG@.ShTotem.entries(p, slot);
    String[] ne = new String[e.length - 1];
    int j = 0;
    for (int i = 0; i < e.length; i++) if (i != pad) { ne[j] = e[i]; j++; }
    @PKG@.ShTotem.setEntries(p, slot, ne);
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) {
      p.clear(); p.putAll(old);
      int[] w = @PKG@.ShInv.findUid(cs, st.getItemId(), f[5]);
      boolean took = w != null && @PKG@.ShInv.takeSlot(cs, w[0], w[1], st.getItemId(), f[5]);
      tlog(u + " " + k + " pickup " + @PKG@.ShTotem.fmt(f) + " SAVE FAILED " + err + " - item taken back " + took);
      return "-The totem could not be saved - nothing changed.";
    }
    tlog(u + " " + k + " pickup slot " + slot + " pad " + pad + " " + @PKG@.ShTotem.fmt(f));
    res = "+" + @PKG@.ShTotem.name(f) + " is in your inventory - its tier, modifiers and booster stay with it.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
  @PKG@.ShWorld2.repaint(k);
  return res;
}""")
# add modifier `mi` (one item taken, counted) into the first free modifier slot
M(core, r"""
public static String addMod(java.util.UUID u, String k, int slot, int pad, int mi, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  if (mi < 0 || mi >= @PKG@.ShTotem.MOD_ITEMS.length) return "-You have no totem modifiers - craft them on the Craft tab.";
  String mid = @PKG@.ShTotem.MOD_ITEMS[mi];
  long now = now();
  @PKG@.ShStore.LOCK.lock(); try {
    String[] f = at(p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    int which = f[2].length() == 0 ? 2 : (f[3].length() == 0 ? 3 : -1);
    if (which < 0) return "-Both modifier slots are full - remove one first.";
    if (@PKG@.ShInv.count(cs, mid) < 1L) return "-You have no " + @PKG@.ShTotem.MOD_NAMES[mi] + " modifier.";
    @PKG@.ShMath.settle(p, slot, now);
    if (@PKG@.ShInv.take(cs, mid, 1L) < 1L) return "-The modifier could not be taken.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    f[which] = @PKG@.ShTotem.MOD_KEYS[mi];
    put(p, slot, pad, f);
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); long r = @PKG@.ShInv.give(cs, mid, 1L); tlog(u + " " + k + " addmod " + mid + " SAVE FAILED " + err + " - back " + r); return "-Could not be saved - your modifier is back."; }
    tlog(u + " " + k + " addmod slot " + slot + " pad " + pad + " " + mid + " -> " + @PKG@.ShTotem.fmt(f));
    return "+" + @PKG@.ShTotem.MOD_NAMES[mi] + " added to " + @PKG@.ShTotem.name(f) + " (" + @PKG@.ShTotem.MOD_DESC[mi] + ").";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# remove modifier slot 1 / 2: the item first, then the record (a refused save takes it back)
M(core, r"""
public static String removeMod(java.util.UUID u, String k, int slot, int pad, int which, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  long now = now();
  @PKG@.ShStore.LOCK.lock(); try {
    String[] f = at(p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    int fi = which == 2 ? 3 : 2;
    int mi = @PKG@.ShTotem.modIdx(f[fi]);
    if (mi < 0) return "=That modifier slot is empty.";
    String mid = @PKG@.ShTotem.MOD_ITEMS[mi];
    @PKG@.ShMath.settle(p, slot, now);
    if (@PKG@.ShInv.give(cs, mid, 1L) < 1L) return "-Make room in your inventory first.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    f[fi] = "";
    put(p, slot, pad, f);
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); long r = @PKG@.ShInv.take(cs, mid, 1L); tlog(u + " " + k + " removemod " + mid + " SAVE FAILED " + err + " - taken back " + r); return "-Could not be saved - nothing changed."; }
    tlog(u + " " + k + " removemod slot " + slot + " pad " + pad + " " + mid);
    return "+" + @PKG@.ShTotem.MOD_NAMES[mi] + " is back in your inventory.";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# the booster slot: one Life / Water / Void Essence burns totem.boostSec (real time) for +2 range and +totem.boostPct %
M(core, r"""
public static String addBooster(java.util.UUID u, String k, int slot, int pad, @IC@[] cs) {
  Object[] o = new Object[1];
  String no = start(u, k, cs, o);
  if (no != null) return no;
  java.util.Properties p = (java.util.Properties) o[0];
  long now = now();
  String bid = null;
  for (int i = 0; i < @PKG@.ShTotem.BOOSTERS.length && bid == null; i++) if (@PKG@.ShInv.count(cs, @PKG@.ShTotem.BOOSTERS[i]) > 0L) bid = @PKG@.ShTotem.BOOSTERS[i];
  if (bid == null) return "-A booster is 1 Life, Water or Void Essence - you have none.";
  @PKG@.ShStore.LOCK.lock(); try {
    String[] f = at(p, slot, pad);
    if (f == null) return "-That totem is gone - the page is up to date now.";
    if (@PKG@.ShTotem.boosted(f, now)) return "=A booster is already burning in this totem.";
    @PKG@.ShMath.settle(p, slot, now);
    if (@PKG@.ShInv.take(cs, bid, 1L) < 1L) return "-The essence could not be taken.";
    java.util.Properties old = new java.util.Properties();
    old.putAll(p);
    f[4] = String.valueOf(now + 1000L * (long) @PKG@.ShCfg.BOOST_SEC);
    put(p, slot, pad, f);
    String err = @PKG@.ShStore.save(k, p);
    if (err != null) { p.clear(); p.putAll(old); long r = @PKG@.ShInv.give(cs, bid, 1L); tlog(u + " " + k + " booster SAVE FAILED " + err + " - back " + r); return "-Could not be saved - your essence is back."; }
    tlog(u + " " + k + " booster slot " + slot + " pad " + pad + " " + bid + " until " + f[4]);
    return "+Booster burning for " + (@PKG@.ShCfg.BOOST_SEC / 60) + " min: +2 range and +" + @PKG@.ShCfg.BOOST_PCT + " % for " + @PKG@.ShTotem.name(f) + ".";
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# the range circle as particles for 10 s (ShTick draws it while someone is inside)
M(core, r"""
public static String showRange(String k, int slot, int pad) {
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (p == null) return "-This shard's file could not be read.";
  String[] f;
  @PKG@.ShStore.LOCK.lock(); try { f = at(p, slot, pad); } finally { @PKG@.ShStore.LOCK.unlock(); }
  if (f == null) return "-That totem is gone - the page is up to date now.";
  long now = now();
  int r = @PKG@.ShTotem.range(f, now);
  double[] c = @PKG@.ShGeo.totemSpot(slot);
  RANGE.put(@PKG@.ShWorlds.name(k), new double[] { c[0], (double) (@PKG@.ShGeo.Y + 1) + 0.3, c[2], (double) r, (double) (now + 10000L) });
  return "=Range " + r + " blocks - shown as sparkles around the island for 10 s (inside the shard).";
}""")
# Upgrade = the Anvil (SkyyGear). gear:fn:anvil:open (UUID -> Boolean, the player's world thread) when SkyyGear publishes it
M(core, r"""
public static String upgrade(java.util.UUID u) {
  try {
    java.util.function.Function g = @PKG@.ShPay.f("gear:fn:anvil:open");
    if (g != null && Boolean.TRUE.equals(g.apply(u))) return "+Opening the Anvil - pick the totem in your inventory there.";
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("anvil", "gear:fn:anvil:open failed: " + t); }
  return "=Totems tier up on the Anvil (Upgrade) - that comes with the next SkyyGear update. Pick the totem up to take it there.";
}""")
# ---- crafting (Craft tab). A recipe "Item:qty,Item:qty;coins" -> Object[]{ String[] ids, long[] qty, Long coins } or null (bad / empty)
M(core, r"""
public static Object[] recipe(String txt) {
  if (txt == null || txt.trim().length() == 0) return null;
  try {
    String t = txt.trim();
    long coins = 0L;
    int sc = t.indexOf(';');
    if (sc >= 0) { String c = t.substring(sc + 1).trim(); if (c.length() > 0) coins = Long.parseLong(c); t = t.substring(0, sc).trim(); }
    if (coins < 0L) return null;
    String[] a = t.length() == 0 ? new String[0] : t.split(",");
    String[] ids = new String[a.length];
    long[] q = new long[a.length];
    for (int i = 0; i < a.length; i++) {
      String[] b = a[i].trim().split(":");
      if (b.length != 2 || b[0].trim().length() == 0) return null;
      ids[i] = b[0].trim();
      q[i] = Long.parseLong(b[1].trim());
      if (q[i] < 1L || q[i] > 100000L) return null;
    }
    if (ids.length == 0 && coins == 0L) return null;
    return new Object[] { ids, q, Long.valueOf(coins) };
  } catch (Throwable x) { return null; }
}""")
# rebirths of a profile (SkyyRebirth rebirth:fn:count): -2 = still loading, 0 = none / no SkyyRebirth
M(core, r"""
public static int rebirths(String pk) {
  try {
    java.util.function.Function g = @PKG@.ShPay.f("rebirth:fn:count");
    if (g == null) return 0;
    Object r = g.apply(pk);
    if (r == null) return -2;
    return r instanceof Number ? ((Number) r).intValue() : 0;
  } catch (Throwable t) { return 0; }
}""")
# fix3: does this profile already have its Farming Shard (placed, or islands made = it was placed once and is picked up / in an inventory)?
F(core, 'public static final String HAVE_SHARD = "You already have your Farming Shard (one per profile). A lost one is replaced by an admin; crafting more shards opens with the other shards in a later update.";')
# fix4 (critics shards02): the profile HAD its Farming Shard - placed once (an island exists, even while it is picked up and sits in a chest,
# a vault or the auction house) or crafted once (farming.crafted = 1, saved BEFORE the shard is handed out). Neither ever clears, so a
# stored or traded shard can no longer be crafted again. A lost shard = /shardadmin give (QUESTION for Skyy; default admin).
M(core, r"""
public static boolean hasShard(String pk) {
  java.util.Properties p = @PKG@.ShStore.get(pk);
  if (p == null) return true;   // unreadable = assume yes (never a second shard by mistake)
  @PKG@.ShStore.LOCK.lock(); try {
    if (@PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed").length() > 0) return true;
    if ("1".equals(@PKG@.ShStore.str(p, @PKG@.ShMath.K + ".crafted"))) return true;
    return @PKG@.ShMath.owned(p);
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# fix4: farming.crafted on / off, saved (false = the file could not be saved; the value is put back)
M(core, r"""
public static boolean markCrafted(String pk, boolean on) {
  java.util.Properties p = @PKG@.ShStore.get(pk);
  if (p == null) return false;
  @PKG@.ShStore.LOCK.lock(); try {
    String key = @PKG@.ShMath.K + ".crafted";
    String had = p.getProperty(key);
    if (on) p.setProperty(key, "1"); else p.remove(key);
    String e = @PKG@.ShStore.save(pk, p);
    if (e == null) return true;
    if (had == null) p.remove(key); else p.setProperty(key, had);
    return false;
  } finally { @PKG@.ShStore.LOCK.unlock(); }
}""")
# null = this recipe may be crafted by u now (the gates only, not the items), else why not
M(core, r"""
public static String craftGate(java.util.UUID u, int ri) {
  if (ri < 0 || ri >= @PKG@.ShCfg.CRAFT_ID.length) return "Pick a recipe.";
  String id = @PKG@.ShCfg.CRAFT_ID[ri];
  if (recipe(@PKG@.ShCfg.CRAFT[ri]) == null) return "This recipe is switched off (Server Setup -> Shards -> Crafting).";
  int ti = @PKG@.ShTotem.itemIdx(id);
  if (ti >= 0 && !@PKG@.ShTotem.FARM[ti]) return "Works in the " + @PKG@.ShTotem.SHARD[ti] + " Shard - a later update.";
  if (id.equals(SHARD)) {   // Rebirth R9: extra shards are crafted from rebirth 2 (Skyy: "more can be crafter after rebirth 2")
    int n = rebirths(@PKG@.ShCfg.pkey(u));
    if (n == -2) return "Your rebirths are still loading - try again in a moment.";
    if (n < @PKG@.ShCfg.SHARD_RB) return "Crafting a shard needs rebirth " + @PKG@.ShCfg.SHARD_RB + " (you: " + (n < 0 ? 0 : n) + "). Your first shards come from quests.";
    if (hasShard(@PKG@.ShCfg.pkey(u))) return HAVE_SHARD;   // fix4: one Farming Shard per profile, ever (placed once or crafted once)
  }
  return null;
}""")
# craft recipe ri: every input counted and taken (all back if one falls short), coins last (items back if they fail), then the output
# (a totem = tier I with a fresh document); an output that does not fit gives everything back
M(core, r"""
public static String craft(java.util.UUID u, int ri, @IC@[] cs) {
  if (!@PKG@.ShCfg.ON) return "-Shards are switched off on this server.";
  if (cs == null) return "-Your inventory could not be read - try again.";
  if (busy(u)) return "-Your profile is still loading - try again in a moment.";
  String g = craftGate(u, ri);
  if (g != null) return "-" + g;
  if (SHARD.equals(@PKG@.ShCfg.CRAFT_ID[ri]) && @PKG@.ShInv.count(cs, SHARD) > 0L) return "-" + HAVE_SHARD;   // fix3: one in the inventory already
  Object[] r = recipe(@PKG@.ShCfg.CRAFT[ri]);
  String[] ids = (String[]) r[0];
  long[] q = (long[]) r[1];
  long coins = ((Long) r[2]).longValue();
  for (int i = 0; i < ids.length; i++) {
    long have = @PKG@.ShInv.count(cs, ids[i]);
    if (have < q[i]) return "-You need " + @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you have " + @PKG@.ShCfg.num(have) + ").";
  }
  long purse = @PKG@.ShPay.coins(u);
  if (coins > 0L && purse >= 0L && purse < coins) return "-You need " + @PKG@.ShCfg.num(coins) + " coins (you have " + @PKG@.ShCfg.num(purse) + ").";
  long[] took = new long[ids.length];
  boolean ok = true;
  for (int i = 0; i < ids.length && ok; i++) { took[i] = @PKG@.ShInv.take(cs, ids[i], q[i]); if (took[i] < q[i]) ok = false; }
  if (ok && !@PKG@.ShPay.takeCoins(u, coins)) ok = false;
  else if (ok) {
    String id = @PKG@.ShCfg.CRAFT_ID[ri];
    int ti = @PKG@.ShTotem.itemIdx(id);
    boolean out;
    String what;
    if (ti >= 0) {
      String[] f = new String[] { @PKG@.ShTotem.KEYS[ti], "1", "", "", "0", @PKG@.ShTotem.newUid() };
      out = @PKG@.ShInv.giveStack(cs, @PKG@.ShTotem.stack(f, now()));
      what = @PKG@.ShTotem.name(f);
    } else if (id.equals(SHARD) && !markCrafted(@PKG@.ShCfg.pkey(u), true)) {   // fix4: the mark is saved before the shard exists
      boolean rc0 = @PKG@.ShPay.addCoins(u, coins);
      for (int i = 0; i < ids.length; i++) if (took[i] > 0L) @PKG@.ShInv.give(cs, ids[i], took[i]);
      tlog(u + " craft " + id + " NOT SAVED - refund items, coins " + (rc0 ? coins : 0L) + " of " + coins);
      return "-Your shard file could not be saved - everything is back" + (rc0 ? "." : " except " + @PKG@.ShCfg.num(coins) + " coins (ask an admin, totem.log).");
    } else {
      out = @PKG@.ShInv.give(cs, id, 1L) >= 1L;
      what = @PKG@.ShTotem.pretty(id);
      if (!out && id.equals(SHARD)) markCrafted(@PKG@.ShCfg.pkey(u), false);   // fix4: no shard handed out = no mark
    }
    if (out) {
      tlog(u + " craft " + id + " paid " + coins + " coins + " + @PKG@.ShCfg.CRAFT[ri]);
      return "+Crafted " + what + ".";
    }
    boolean rc = @PKG@.ShPay.addCoins(u, coins);
    for (int i = 0; i < ids.length; i++) if (took[i] > 0L) @PKG@.ShInv.give(cs, ids[i], took[i]);
    tlog(u + " craft " + id + " NO ROOM - refund items, coins " + (rc ? coins : 0L) + " of " + coins);
    return "-Make room in your inventory first - everything is back" + (rc ? "." : " except " + @PKG@.ShCfg.num(coins) + " coins (ask an admin, totem.log).");
  }
  for (int i = 0; i < ids.length; i++) if (took[i] > 0L) @PKG@.ShInv.give(cs, ids[i], took[i]);
  return "-The items or coins could not be taken - everything is back.";
}""")
# the totem page's "nearest pad": the island + pad of the totem nearest to (x, z) within 6 blocks (int[]{slot, pad} or null)
M(core, r"""
public static int[] nearest(java.util.Properties p, double x, double z) {
  int[] best = null;
  double bd = 36.0;
  for (int s = 0; s < @PKG@.ShMath.SLOTS; s++) {
    if (!@PKG@.ShMath.hasIsland(p, s)) continue;
    int n = @PKG@.ShTotem.entries(p, s).length;
    for (int i = 0; i < n; i++) {
      int[] q = @PKG@.ShGeo.padPos(s, i);
      double dx = (double) q[0] + 0.5 - x;
      double dz = (double) q[2] + 0.5 - z;
      double d = dx * dx + dz * dz;
      if (d < bd) { bd = d; best = new int[] { s, i }; }
    }
  }
  return best;
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
        work = @PKG@.ShMath.stored(p, i) < @PKG@.ShMath.capOf(p, i) && @PKG@.ShMath.rate(p, i, now) > 0.0;   // 0.2: only a working island (a worker, room)
      } finally { @PKG@.ShStore.LOCK.unlock(); }
      if (!work) continue;
      double[] s = @PKG@.ShGeo.totemSpot(i);
      @PTU@.spawnParticleEffect(@PKG@.ShCfg.particle(), (@V3DC@) new @V3D@(s[0], s[1], s[2]), (@CA@) this.w.getEntityStore().getStore());
      BURSTS.incrementAndGet();
    }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("particles", "totem particles failed (logged once): " + t); }
}""")
# 0.2: the range circle (world thread): 24 sparkles on the circle, once a second until the 10 s are over
rng = mk("ShRange", None, ("java.lang.Runnable",))
F(rng, "public @WLD@ w;")
F(rng, "public double[] c;")
F(rng, "public static final java.util.concurrent.atomic.AtomicLong DRAWS = new java.util.concurrent.atomic.AtomicLong();")
C(rng, "public ShRange(@WLD@ w, double[] c) { this.w = w; this.c = c; }")
M(rng, r"""
public void run() {
  try {
    for (int i = 0; i < 24; i++) {
      double a = (double) i * Math.PI / 12.0;
      @PTU@.spawnParticleEffect(@PKG@.ShCfg.particle(), (@V3DC@) new @V3D@(this.c[0] + this.c[3] * Math.cos(a), this.c[1], this.c[2] + this.c[3] * Math.sin(a)), (@CA@) this.w.getEntityStore().getStore());
    }
    DRAWS.incrementAndGet();
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("range", "the range circle failed (logged once): " + t); }
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
      Object rc = @PKG@.ShCore.RANGE.get(nm);   // 0.2: a "Show range" circle
      if (rc instanceof double[]) { if ((long) ((double[]) rc)[4] < now) @PKG@.ShCore.RANGE.remove(nm); else w.execute(new @PKG@.ShRange(w, (double[]) rc)); }
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
TABS = ["Collect", "Upgrades", "Islands", "Totems", "Craft"]          # 0.2: + Craft
NTAB = len(TABS)
TAB_IDS = [P + "Tab%d" % i for i in range(NTAB)]
TAB_W = (IW - (NTAB - 1) * SUI.TAB_GAP) // NTAB
for t in range(NTAB):
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
# --- Totems tab (0.2: the selected island's totems, place from the inventory, the selected totem's page on the right)
t0 = seg("t0")
L3, R3 = panel_pair(t0, "T")
t0.append((L3, SUI.label(P + "THead", "Totems", "panelTitle", h=30)))
t0.text(L3, P + "TCap", J_("this.tCap", "Island 1 - Wheat Small - 1 of 3 pads (pick the island on the Islands tab)"), "caption", h=24, w=ROWW)
TROW_W_TX, TROW_W_ST, TROW_W_BTN = 430, 110, 100
assert TROW_W_TX + TROW_W_ST + TROW_W_BTN + 20 + 10 <= ROWW
for i in range(5):
    a = seg("trow%d" % i)
    rid = P + "TRow%d" % i
    a.append((L3, SUI.panel(rid, "row", w=ROWW, h=50, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=TROW_W_TX, h=50)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.tName[%d]" % i, "Harvest Spirit I"), "rowName", size=15, h=26, w=TROW_W_TX)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.tSub[%d]" % i, "Worker - range 3 - 1 / min"), "rowSub", size=12, h=22, w=TROW_W_TX)
    a.text("#" + rid, rid + "St", J_("this.tSt[%d]" % i, "Selected"), "bold", size=14, h=50, w=TROW_W_ST, align="End", col=GOLD)
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Open", "secondary", "small", w=TROW_W_BTN, anchor={"top": 9})))
te = seg("tempty")
te.text(L3, P + "TEmpty", "No totems on this island yet - place one from your inventory below.", "caption", h=30, w=ROWW)
t0b = seg("t0b")
t0b.append((L3, SUI.label(P + "TPHead", "Place from your inventory", "section", h=30)))
for i in range(4):
    a = seg("prow%d" % i)
    rid = P + "PRow%d" % i
    a.append((L3, SUI.panel(rid, "row", w=ROWW, h=40, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.text("#" + rid, rid + "Nm", J_("this.pName[%d]" % i, "Rain Totem I - modifiers: -"), "default", size=14, h=40, w=ROWW - 20 - 110)
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Place", "secondary", "small", w=100, anchor={"top": 4})))
pe = seg("pempty")
pe.text(L3, P + "PEmpty", "No totems in your inventory - craft one on the Craft tab.", "caption", h=30, w=ROWW)
t1 = seg("tside")
t1.text(R3, P + "TDT", J_("this.dTitle", "Harvest Spirit I"), "panelTitle", size=17, h=30, w=RW - 24)
for j in range(8):
    t1.text(R3, P + "TD%d" % j, J_("this.dTx[%d]" % j, "Worker - range 3 blocks"), "default", size=13, h=26, w=RW - 24, col=J_("this.dCol[%d]" % j, TEXT))
t1.append((R3, SUI.spacer(h=6)))
HB = (RW - 24 - 8) // 2
assert HB * 2 + 8 <= RW - 24
td = seg("tdbtn")
for gi, (b1, t1_, b2, t2_) in enumerate((("TModAdd", "Add modifier", "TModNext", "Other modifier"), ("TMod1", "Remove mod 1", "TMod2", "Remove mod 2"),
                                          ("TBoost", "Add booster", "TRange", "Show range"), ("TUp", "Upgrade", "TPick", "Pick up"))):
    gid = P + "TB%d" % gi
    td.append((R3, SUI.group(gid, layout="Left", w=RW - 24, h=SUI.BTN_SMALL_H, anchor={"bottom": 6})))
    td.append(("#" + gid, SUI.button(P + b1, t1_, "secondary", "small", w=HB)))
    td.append(("#" + gid, SUI.spacer(w=8)))
    td.append(("#" + gid, SUI.button(P + b2, t2_, "secondary", "small", w=HB)))
TD_BINDS = [(P + "TModAdd", "tmodadd"), (P + "TModNext", "tmodnext"), (P + "TMod1", "tmodrem1"), (P + "TMod2", "tmodrem2"),
            (P + "TBoost", "tboost"), (P + "TRange", "trange"), (P + "TUp", "tup"), (P + "TPick", "tpick")]
# --- Craft tab (0.2): one page of 7 recipes on the left, the picked recipe on the right
k0 = seg("k0")
L4, R4 = panel_pair(k0, "K")
k0.append((L4, SUI.label(P + "KHead", "Craft", "panelTitle", h=30)))
k0.text(L4, P + "KCap", J_("this.kCap", "Page 1 of 3 - totems come out at tier I; tier up on the Anvil."), "caption", h=24, w=ROWW)
KROWS = 7
for i in range(KROWS):
    a = seg("krow%d" % i)
    rid = P + "KRow%d" % i
    a.append((L4, SUI.panel(rid, "row", w=ROWW, h=50, layout="Left", pad={"left": 10, "right": 10}, anchor={"bottom": 4})))
    a.append(("#" + rid, SUI.group(rid + "Tx", layout="Top", w=TROW_W_TX, h=50)))
    a.text("#" + rid + "Tx", rid + "Nm", J_("this.kName[%d]" % i, "Harvest Spirit I"), "rowName", size=15, h=26, w=TROW_W_TX)
    a.text("#" + rid + "Tx", rid + "Sb", J_("this.kSub[%d]" % i, "128 Wheat, 8 Life Essence, 500 coins"), "rowSub", size=12, h=22, w=TROW_W_TX)
    a.text("#" + rid, rid + "St", J_("this.kSt[%d]" % i, "Ready"), "bold", size=14, h=50, w=TROW_W_ST, align="End", col=J_("this.kStC[%d]" % i, GOOD))
    a.append(("#" + rid, SUI.spacer(w=10)))
    a.append(("#" + rid, SUI.button(rid + "Btn", "Select", "secondary", "small", w=TROW_W_BTN, anchor={"top": 9})))
kp = seg("kpage")
kp.append((L4, SUI.group(P + "KPg", layout="Left", w=ROWW, h=SUI.BTN_SMALL_H, anchor={"top": 4})))
kp.append(("#" + P + "KPg", SUI.button(P + "KPrev", "Previous", "secondary", "small", w=160)))
kp.append(("#" + P + "KPg", SUI.spacer(w=ROWW - 320)))
kp.append(("#" + P + "KPg", SUI.button(P + "KNext", "Next", "secondary", "small", w=160)))
k1 = seg("kside")
k1.text(R4, P + "KT", J_("this.kTitle", "Harvest Spirit I"), "panelTitle", size=17, h=30, w=RW - 24)
for j in range(9):
    k1.text(R4, P + "KD%d" % j, J_("this.kTx[%d]" % j, "128 Wheat (you: 40)"), "default", size=13, h=26, w=RW - 24, col=J_("this.kCol[%d]" % j, TEXT))
k1.append((R4, SUI.spacer(h=10)))
kc = seg("kcraft")
kc.append((R4, SUI.button(P + "KCraft", "Craft", "primary", w=RW - 24)))
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
for t in range(NTAB):
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
        elif t == 3:
            v.extend(SEG["t0"])
            for i in range(5):
                v.extend(SEG["trow%d" % i])
            v.extend(SEG["t0b"])
            for i in range(4):
                v.extend(SEG["prow%d" % i])
            v.extend(SEG["tside"]); v.extend(SEG["tdbtn"])
        else:
            v.extend(SEG["k0"])
            for i in range(KROWS):
                v.extend(SEG["krow%d" % i])
            v.extend(SEG["kpage"]); v.extend(SEG["kside"]); v.extend(SEG["kcraft"])
        v.extend(base2)
        v.extend(SEG["pick"])
        v.extend(base3)
        VARIANTS.append(v)
        if t != 2:
            break
# 0.2: the empty-state variants of the Totems tab (no totem rows / no inventory rows)
v = SUI.Appends(sh.appends); v.extend(SEG["enter"]); v.extend(SEG["tabs3"]); v.extend(SEG["t0"]); v.extend(SEG["tempty"]); v.extend(SEG["t0b"])
v.extend(SEG["pempty"]); v.extend(SEG["tside"]); v.extend(base2); v.extend(SEG["nopick"]); v.extend(base3)
VARIANTS.append(v)
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
    "  } else if (this.tab == 3) {", jseg("tabs3"), "  } else {", jseg("tabs4"), "  }",
    binds([(TAB_IDS[i], "tab%d" % i) for i in range(NTAB)]),
    "  if (this.tab == 0) {", jseg("c0"),
    "    if (this.cN == 0) {", jseg("cempty"), "    }",
] + ["    if (this.cN > %d) {\n%s\n%s\n    }" % (i, jseg("crow%d" % i), binds([(P + "CRow%dBtn" % i, "col%d" % i)])) for i in range(SLOTS)] + [
    jseg("c1"), binds([(P + "CAll", "colall")]),
    "  } else if (this.tab == 1) {", jseg("u0"), "    if (this.uCan) {", jseg("ubuy"), binds([(P + "UBuy", "buy")]), "    }",
    "  } else if (this.tab == 2) {", jseg("i0"),
] + ["    if (this.sel == %d) {\n%s\n    } else {\n%s\n    }\n%s" % (i, jseg("islot%ds" % i), jseg("islot%dn" % i), binds([(P + "ISl%dSel" % i, "slot%d" % i)]))
     for i in range(SLOTS)] + [
    jseg("iside"), "    if (this.iCan) {", jseg("igrow"), binds([(P + "IGrow", "grow")]), "    }",
    "  } else if (this.tab == 3) {", jseg("t0"),
    "    if (this.tN == 0) {", jseg("tempty"), "    }",
] + ["    if (this.tN > %d) {\n%s\n%s\n    }" % (i, jseg("trow%d" % i), binds([(P + "TRow%dBtn" % i, "tsel%d" % i)])) for i in range(5)] + [
    jseg("t0b"),
    "    if (this.pN == 0) {", jseg("pempty"), "    }",
] + ["    if (this.pN > %d) {\n%s\n%s\n    }" % (i, jseg("prow%d" % i), binds([(P + "PRow%dBtn" % i, "tplace%d" % i)])) for i in range(4)] + [
    jseg("tside"), "    if (this.dHas) {", jseg("tdbtn"), binds(TD_BINDS), "    }",
    "  } else {", jseg("k0"),
] + ["    if (this.kN > %d) {\n%s\n%s\n    }" % (i, jseg("krow%d" % i), binds([(P + "KRow%dBtn" % i, "ksel%d" % i)])) for i in range(KROWS)] + [
    jseg("kpage"), binds([(P + "KPrev", "kprev"), (P + "KNext", "knext")]),
    jseg("kside"), "    if (this.kCan) {", jseg("kcraft"), binds([(P + "KCraft", "kcraft")]), "    }",
    "  }",
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
          "public boolean mine;", "public boolean stale;",
          # 0.2: the Totems tab (tpad = the selected pad; p* = inventory totems; d* = the selected totem; modSel = the modifier Add uses)
          "public int tpad;", "public String tCap;", "public int pN;", "public String[] pName;", "public int[] pCi;", "public int[] pSi;",
          "public boolean dHas;", "public String dTitle;", "public String[] dTx;", "public String[] dCol;", "public int modSel;", "public long tpickArm;",
          "public boolean fromTotem;", "public boolean near;", "public int tIsl;",
          # 0.2: the Craft tab
          "public int kPage;", "public int kSel;", "public int kN;", "public String kCap;", "public String[] kName;", "public String[] kSub;",
          "public String[] kSt;", "public String[] kStC;", "public int[] kIdx;", "public String kTitle;", "public String[] kTx;", "public String[] kCol;",
          "public boolean kCan;"):
    F(page, f)
C(page, r"""
public ShPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.me = pr == null ? null : pr.getUuid();
  this.testMode = false;
  this.tab = 0; this.sel = 0; this.stText = ""; this.stCol = "@INFO@"; this.pickArm = 0L; this.lastAction = "";
  this.tpad = 0; this.modSel = 0; this.tpickArm = 0L; this.kPage = 0; this.kSel = 0;
}""".replace("@INFO@", INFO))
C(page, r"""
public ShPage(java.util.UUID u, String world) {
  super((@PR@) null, @LIFE@.CanDismiss);
  this.me = u;
  this.testMode = true;
  this.testWorld = world;
  this.tab = 0; this.sel = 0; this.stText = ""; this.stCol = "@INFO@"; this.pickArm = 0L; this.lastAction = "";
  this.tpad = 0; this.modSel = 0; this.tpickArm = 0L; this.kPage = 0; this.kSel = 0;
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
# 0.2: a recipe's cost line ("128 Wheat, 8 Life Essence, 500 coins", cut at max chars) and "has every input"
M(page, r"""
public static String costText(Object[] rc, int max) {
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.ShCfg.num(q[i])).append(' ').append(@PKG@.ShTotem.pretty(ids[i])); }
  long c = ((Long) rc[2]).longValue();
  if (c > 0L) { if (sb.length() > 0) sb.append(", "); sb.append(@PKG@.ShCfg.num(c)).append(" coins"); }
  String s = sb.toString();
  return s.length() > max ? s.substring(0, max - 3) + "..." : s;
}""")
M(page, r"""
public static boolean haveAll(Object[] rc, @IC@[] cs) {
  if (cs == null) return false;
  String[] ids = (String[]) rc[0];
  long[] q = (long[]) rc[1];
  for (int i = 0; i < ids.length; i++) if (@PKG@.ShInv.count(cs, ids[i]) < q[i]) return false;
  return true;
}""")
# 0.2: the Totems tab texts (under the ShStore lock, settled already): the selected island (this.sel; the first island when that slot is
# empty), its totems on their pads, the inventory totems that could be placed, the selected totem's page
M(page, r"""
public void fillTotems(java.util.Properties p, @IC@[] cs, long now) {
  this.tName = new String[5]; this.tSub = new String[5]; this.tSt = new String[5];
  this.pName = new String[4]; this.pCi = new int[4]; this.pSi = new int[4];
  this.dTx = new String[8]; this.dCol = new String[8];
  for (int i = 0; i < 5; i++) { this.tName[i] = ""; this.tSub[i] = ""; this.tSt[i] = ""; }
  for (int i = 0; i < 4; i++) this.pName[i] = "";
  for (int i = 0; i < 8; i++) { this.dTx[i] = ""; this.dCol[i] = "@TEXT@"; }
  this.tN = 0; this.pN = 0; this.dHas = false; this.dTitle = "No totem selected"; this.tCap = "";
  int s = this.sel < 0 || this.sel > 5 ? 0 : this.sel;
  if (p != null && !@PKG@.ShMath.hasIsland(p, s)) { for (int i = 0; i < 6; i++) if (@PKG@.ShMath.hasIsland(p, i)) { s = i; break; } }
  this.tIsl = s;
  if (p == null || !@PKG@.ShMath.hasIsland(p, s)) { this.tCap = "No island yet."; }
  else {
    int sz = @PKG@.ShMath.size(p, s);
    String[] e = @PKG@.ShTotem.entries(p, s);
    this.tCap = "Island " + (s + 1) + " - Wheat " + (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) + " - " + e.length + " of " + @PKG@.ShMath.pads(sz) + " pads - " + @PKG@.ShCfg.dec(@PKG@.ShMath.rate(p, s, now)) + " items / min (pick the island on the Islands tab)";
    this.tN = e.length > 5 ? 5 : e.length;
    if (this.tpad >= this.tN) this.tpad = this.tN - 1;
    if (this.tpad < 0) this.tpad = 0;
    for (int i = 0; i < this.tN; i++) {
      String[] f = @PKG@.ShTotem.parse(e[i]);
      int ti = @PKG@.ShTotem.idx(f[0]);
      this.tName[i] = @PKG@.ShTotem.name(f);
      boolean wk = ti >= 0 && @PKG@.ShTotem.WORKER[ti];
      String eff = wk ? @PKG@.ShCfg.dec(@PKG@.ShTotem.workerRate(f, sz, now)) + " / min" : "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.supportPct(f, now)) + " %";
      this.tSub[i] = (wk ? "Worker" : "Support") + " - range " + @PKG@.ShTotem.range(f, now) + " - " + eff + (@PKG@.ShTotem.boosted(f, now) ? " - boosted" : "");
      this.tSt[i] = i == this.tpad ? "Selected" : "";
    }
    if (this.tN > 0) {
      String[] f = @PKG@.ShTotem.parse(e[this.tpad]);
      int ti = @PKG@.ShTotem.idx(f[0]);
      boolean wk = ti >= 0 && @PKG@.ShTotem.WORKER[ti];
      this.dHas = true;
      this.dTitle = @PKG@.ShTotem.name(f) + " - pad " + (this.tpad + 1);
      this.dTx[0] = wk ? "Worker: harvests the crops in its range." : (ti >= 0 && @PKG@.ShTotem.EFFECT[ti] == 4 ? "Harvest Moon: more crops at night + rare Enchanted crops." : "Support: more crops for the whole island.");
      int r = @PKG@.ShTotem.range(f, now);
      this.dTx[1] = "Range " + r + " blocks: " + @PKG@.ShTotem.cov(sz, r) + " of " + @PKG@.ShTotem.cov(sz, 99) + " crops";
      this.dTx[2] = wk ? "Makes " + @PKG@.ShCfg.dec(@PKG@.ShTotem.workerRate(f, sz, now)) + " items / min" : "+" + @PKG@.ShCfg.dec(@PKG@.ShTotem.supportPct(f, now)) + " % for this island";
      int m1 = @PKG@.ShTotem.modIdx(f[2]); int m2 = @PKG@.ShTotem.modIdx(f[3]);
      this.dTx[3] = "Modifier 1: " + (m1 < 0 ? "empty" : @PKG@.ShTotem.MOD_NAMES[m1] + " (" + @PKG@.ShTotem.MOD_DESC[m1] + ")");
      this.dTx[4] = "Modifier 2: " + (m2 < 0 ? "empty" : @PKG@.ShTotem.MOD_NAMES[m2] + " (" + @PKG@.ShTotem.MOD_DESC[m2] + ")");
      long u = 0L;
      try { u = Long.parseLong(f[4]); } catch (Throwable x) { u = 0L; }
      this.dTx[5] = u > now ? "Booster: " + ((u - now + 59999L) / 60000L) + " min left" : "Booster: empty (1 Life, Water or Void Essence)";
      this.dCol[5] = u > now ? "@GOOD@" : "@TEXT@";
      int pick = -1;
      for (int k = 0; k < @PKG@.ShTotem.MOD_ITEMS.length && pick < 0; k++) {
        int kk = (this.modSel + k) % @PKG@.ShTotem.MOD_ITEMS.length;
        if (@PKG@.ShInv.count(cs, @PKG@.ShTotem.MOD_ITEMS[kk]) > 0L) pick = kk;
      }
      if (pick >= 0) this.modSel = pick;
      this.dTx[6] = pick < 0 ? "Add modifier: you have none (Craft tab)" : "Add modifier adds: " + @PKG@.ShTotem.MOD_NAMES[pick] + " (you: " + @PKG@.ShInv.count(cs, @PKG@.ShTotem.MOD_ITEMS[pick]) + ")";
      this.dCol[6] = pick < 0 ? "@BAD@" : "@GOOD@";
      int[] c = @PKG@.ShTotem.upCost(@PKG@.ShTotem.tierOf(f[1]));
      this.dTx[7] = c == null ? "Highest tier." : "Upgrade (Anvil): " + c[0] + " Enchanted Wheat + " + c[1] + " Life Essence";
    }
  }
  java.util.ArrayList l = @PKG@.ShInv.totems(cs);
  for (int i = 0; i < l.size() && this.pN < 4; i++) {
    Object[] a = (Object[]) l.get(i);
    String[] f = @PKG@.ShTotem.fromDoc((@BD@) a[3], (String) a[2], now);
    if (f == null) continue;
    int ti = @PKG@.ShTotem.idx(f[0]);
    String m = (f[2].length() == 0 && f[3].length() == 0) ? "no modifiers" : "modifiers: " + (f[2].length() == 0 ? "-" : @PKG@.ShTotem.MOD_NAMES[@PKG@.ShTotem.modIdx(f[2])]) + ", " + (f[3].length() == 0 ? "-" : @PKG@.ShTotem.MOD_NAMES[@PKG@.ShTotem.modIdx(f[3])]);
    this.pName[this.pN] = @PKG@.ShTotem.name(f) + " - " + m + (ti >= 0 && !@PKG@.ShTotem.FARM[ti] ? " (" + @PKG@.ShTotem.SHARD[ti] + " Shard, later)" : "");
    this.pCi[this.pN] = ((Integer) a[0]).intValue();
    this.pSi[this.pN] = ((Integer) a[1]).intValue();
    this.pN++;
  }
}""".replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT))
# 0.2: the Craft tab texts (no shard file needed: crafting is personal)
M(page, r"""
public void fillCraft(@IC@[] cs) {
  this.kName = new String[@KR@]; this.kSub = new String[@KR@]; this.kSt = new String[@KR@]; this.kStC = new String[@KR@]; this.kIdx = new int[@KR@];
  this.kTx = new String[9]; this.kCol = new String[9];
  for (int i = 0; i < @KR@; i++) { this.kName[i] = ""; this.kSub[i] = ""; this.kSt[i] = ""; this.kStC[i] = "@TEXT@"; }
  for (int i = 0; i < 9; i++) { this.kTx[i] = ""; this.kCol[i] = "@TEXT@"; }
  int n = @PKG@.ShCfg.CRAFT_ID.length;
  int pages = (n + @KR@ - 1) / @KR@;
  if (this.kPage < 0) this.kPage = 0;
  if (this.kPage >= pages) this.kPage = pages - 1;
  if (this.kSel < 0 || this.kSel >= n) this.kSel = 0;
  this.kCap = "Page " + (this.kPage + 1) + " of " + pages + " - totems come out at tier I; they tier up on the Anvil.";
  this.kN = 0;
  for (int i = this.kPage * @KR@; i < n && this.kN < @KR@; i++) {
    int r = this.kN;
    String id = @PKG@.ShCfg.CRAFT_ID[i];
    this.kIdx[r] = i;
    this.kName[r] = @PKG@.ShTotem.pretty(id);
    Object[] rc = @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[i]);
    this.kSub[r] = rc == null ? "switched off" : costText(rc, 60);
    String g = @PKG@.ShCore.craftGate(this.me, i);
    boolean items = rc != null && haveAll(rc, cs);
    this.kSt[r] = i == this.kSel ? "Selected" : (g != null ? "Locked" : (items ? "Ready" : "Need items"));
    this.kStC[r] = i == this.kSel ? "@GOLD@" : (g != null ? "@BAD@" : (items ? "@GOOD@" : "@WARN@"));
    this.kN++;
  }
  String id = @PKG@.ShCfg.CRAFT_ID[this.kSel];
  this.kTitle = @PKG@.ShTotem.pretty(id);
  Object[] rc = @PKG@.ShCore.recipe(@PKG@.ShCfg.CRAFT[this.kSel]);
  String g = @PKG@.ShCore.craftGate(this.me, this.kSel);
  int j = 0;
  if (rc != null) {
    String[] ids = (String[]) rc[0];
    long[] q = (long[]) rc[1];
    for (int i = 0; i < ids.length && j < 6; i++) {
      long h = @PKG@.ShInv.count(cs, ids[i]);
      this.kTx[j] = @PKG@.ShCfg.num(q[i]) + " " + @PKG@.ShTotem.pretty(ids[i]) + " (you: " + (cs == null ? "?" : @PKG@.ShCfg.num(h)) + ")";
      this.kCol[j] = cs != null && h >= q[i] ? "@GOOD@" : "@BAD@";
      j++;
    }
    long coins = ((Long) rc[2]).longValue();
    if (coins > 0L) {
      long purse = @PKG@.ShPay.coins(this.me);
      this.kTx[j] = @PKG@.ShCfg.num(coins) + " coins (you: " + (purse < 0L ? "?" : @PKG@.ShCfg.num(purse)) + ")";
      this.kCol[j] = (purse < 0L || purse >= coins) ? "@GOOD@" : "@BAD@";
      j++;
    }
  }
  if (g != null) { this.kTx[j] = g; this.kCol[j] = "@BAD@"; j++; }
  int ti = @PKG@.ShTotem.itemIdx(id);
  int mi = @PKG@.ShTotem.modItemIdx(id);
  if (j < 9) this.kTx[j] = ti >= 0 ? (@PKG@.ShTotem.WORKER[ti] ? "A worker totem (tier I)." : "A support totem (tier I).") : (mi >= 0 ? @PKG@.ShTotem.MOD_DESC[mi] + "." : "A Farming Shard for a profile that never had one (rebirth 2; one per profile, ever - a lost one: ask an admin).");
  this.kCan = rc != null && g == null;
}""".replace("@KR@", str(KROWS)).replace("@GOOD@", GOOD).replace("@BAD@", BAD).replace("@TEXT@", TEXT).replace("@GOLD@", GOLD).replace("@WARN@", WARN))
# every text of the page for profile k (settles first; never writes)
M(page, r"""
public void fill(String k, @IC@[] cs) {
  java.util.Properties p = k == null ? null : @PKG@.ShStore.get(k);
  this.key = k;
  this.cSlot = new int[6]; this.cName = new String[6]; this.cSub = new String[6]; this.cAmt = new String[6];
  this.cAll = new String[6]; this.uTx = new String[7]; this.uCol = new String[7];
  this.sName = new String[6]; this.sSub = new String[6]; this.iTx = new String[9]; this.iCol = new String[9];
  for (int i = 0; i < 6; i++) { this.cName[i] = ""; this.cSub[i] = ""; this.cAmt[i] = ""; this.cAll[i] = ""; this.sName[i] = ""; this.sSub[i] = ""; }
  for (int i = 0; i < 7; i++) { this.uTx[i] = ""; this.uCol[i] = "@TEXT@"; }
  for (int i = 0; i < 9; i++) { this.iTx[i] = ""; this.iCol[i] = "@TEXT@"; }
  this.title = "Farming Shard";
  this.cN = 0; this.tN = 0; this.uCan = false; this.iCan = false;
  this.mine = k != null && this.me != null && k.equals(@PKG@.ShCfg.pkey(this.me));   // fix (critic): Pick up only for the owner
  this.stale = false;
  this.sto2c = "@GOOD@";
  this.sum2 = this.view == 1 ? "You are in your Farming Shard. Use the stand or this menu." : (this.view == 0 ? "Your shard portal. Enter Shard takes you to its islands." : "Opened from the SkyWynn Menu.");
  fillCraft(cs);   // 0.2
  if (p == null) { fillTotems(null, cs, @PKG@.ShCore.now()); this.sum1 = "This shard's file could not be read."; this.sto1 = ""; this.sto2 = ""; return; }
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
    fillTotems(p, cs, now);   // 0.2
    for (int i = 0; i < 6; i++) {
      boolean has = @PKG@.ShMath.hasIsland(p, i);
      int sz = has ? @PKG@.ShMath.size(p, i) : 0;
      this.sName[i] = "Slot " + (i + 1) + (has ? " - Wheat" : "");
      this.sSub[i] = has ? (sz >= 3 ? "Large" : (sz == 2 ? "Medium" : "Small")) : "Empty";
      if (!has) continue;
      islands++;
      long s = @PKG@.ShMath.stored(p, i);
      double r = @PKG@.ShMath.rate(p, i, now);
      long en = @PKG@.ShMath.ench(p, i);
      long icap = @PKG@.ShMath.capOf(p, i);
      int nt = @PKG@.ShMath.totems(p, i);
      totems += nt;
      rate += r;
      total += s;
      long tf = @PKG@.ShMath.msToFull(p, i, now);
      boolean full = s >= icap;
      if (full) anyFull = true;
      if (tf >= 0L && (minFull < 0L || tf < minFull)) minFull = tf;
      int c = this.cN;
      this.cSlot[c] = i;
      this.cName[c] = "Wheat Island " + (i + 1) + " - " + this.sSub[i];
      this.cSub[c] = perHour(r) + " / hour - " + (full ? "FULL - collect to restart it" : (tf < 0L ? "no worker totem here" : "full in " + @PKG@.ShMath.fmtMs(tf))) + (en > 0L ? " - +" + en + " Enchanted" : "");
      this.cAmt[c] = @PKG@.ShCfg.num(s) + " / " + @PKG@.ShCfg.num(icap);
      this.cN = c + 1;
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
      double r = @PKG@.ShMath.rate(p, s, now);
      this.iTitle = "Slot " + (s + 1) + " - Wheat Island";
      this.iTx[0] = "Size: " + sizeName(sz);
      this.iTx[1] = "Makes " + perHour(r) + " items / hour";
      this.iTx[2] = "Totems: " + @PKG@.ShMath.totems(p, s) + " of " + @PKG@.ShMath.pads(sz) + " pads (Totems tab)";
      if (sz >= 3) {
        this.iTx[3] = "Fully grown.";
        this.iCol[3] = "@GOLD@";
        this.iTx[4] = "Use totems to make more.";
      } else {
        double nr = @PKG@.ShTotem.islandRate(p, s, sz + 1, now);   // 0.2: more crops only where a totem's range reaches them
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
# fix4: the point a right-click selects by - the block the player looks at (the statue clicked; its origin) when there is one within 8
# blocks, else the player's own position (double[]{x, z}); pure, so the harness runs both branches
M(page, r"""
public static double[] aimPoint(@V3I@ b, double px, double pz) {
  if (b != null) return new double[] { (double) b.x + 0.5, (double) b.z + 0.5 };
  return new double[] { px, pz };
}""")
# 0.2: select the totem right-clicked (fix4: the one looked at; else the nearest to the player; the player's own world thread)
M(page, r"""
public void nearTo(@REF@ ref, @ST@ st, String k) {
  try {
    java.util.Properties p = @PKG@.ShStore.get(k);
    if (p == null || this.testMode) return;
    @TCO@ tc = (@TCO@) st.getComponent(ref, @TCO@.getComponentType());
    if (tc == null) return;
    org.joml.Vector3d v = tc.getPosition();
    @V3I@ b = null;
    try { b = @TU@.getTargetBlockOrigin(ref, 8.0, st); } catch (Throwable t2) { b = null; }   // fix4: the statue looked at
    double[] a = aimPoint(b, v.x, v.z);
    int[] n;
    @PKG@.ShStore.LOCK.lock(); try { n = @PKG@.ShCore.nearest(p, a[0], a[1]); } finally { @PKG@.ShStore.LOCK.unlock(); }
    if (n != null) { this.sel = n[0]; this.tpad = n[1]; }
  } catch (Throwable t) { @PKG@.ShCfg.warnOnce("near", "the nearest totem could not be found (logged once): " + t); }
}""")
M(page, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  String k = resolve(st);
  if (k == null) { this.view = 2; status("-Only the island owner and co-op members can use this shard."); }
  if (this.near && k != null) { this.near = false; this.tab = 3; nearTo(ref, st, k); }   // 0.2: right-clicked a totem block
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
  if (a.startsWith("tab")) { int t = a.length() > 3 ? (int) (a.charAt(3) - '0') : 0; if (t >= 0 && t <= 4) this.tab = t; return ""; }
  if (a.startsWith("slot")) { int s = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (s >= 0 && s <= 5) { this.sel = s; this.tpad = 0; } return ""; }
  if (a.startsWith("tsel")) { int t = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (t >= 0 && t <= 4) { this.tpad = t; this.tpickArm = 0L; } return ""; }
  if (a.startsWith("ksel")) { int t = a.length() > 4 ? (int) (a.charAt(4) - '0') : 0; if (t >= 0 && t < 7 && this.kIdx != null && t < this.kN) this.kSel = this.kIdx[t]; return ""; }
  if (a.equals("kprev")) { this.kPage = this.kPage - 1; return ""; }
  if (a.equals("knext")) { this.kPage = this.kPage + 1; return ""; }
  if (a.equals("tmodnext")) { this.modSel = (this.modSel + 1) % 6; return ""; }
  if (a.equals("kcraft")) return @PKG@.ShCore.craft(this.me, this.kSel, invOf(ref, st));   // crafting is personal (no shard needed)
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
  // 0.2: the totem clicks (the page is filled first, so tIsl / tpad / pCi / modSel are what the player saw)
  if (a.startsWith("tplace") || a.startsWith("tmod") || a.equals("tboost") || a.equals("trange") || a.equals("tup") || a.equals("tpick")) {
    @IC@[] cs = invOf(ref, st);
    fill(k, cs);
    if (a.startsWith("tplace")) {
      int r = a.length() > 6 ? (int) (a.charAt(6) - '0') : -1;
      if (r < 0 || r >= this.pN) return "-That totem is not in your inventory any more.";
      return @PKG@.ShCore.placeTotem(u, k, this.tIsl, this.pCi[r], this.pSi[r], cs);
    }
    if (!this.dHas) return "-Pick a totem first.";
    if (a.equals("tmodadd")) return @PKG@.ShCore.addMod(u, k, this.tIsl, this.tpad, this.modSel, cs);
    if (a.equals("tmodrem1")) return @PKG@.ShCore.removeMod(u, k, this.tIsl, this.tpad, 1, cs);
    if (a.equals("tmodrem2")) return @PKG@.ShCore.removeMod(u, k, this.tIsl, this.tpad, 2, cs);
    if (a.equals("tboost")) return @PKG@.ShCore.addBooster(u, k, this.tIsl, this.tpad, cs);
    if (a.equals("trange")) return @PKG@.ShCore.showRange(k, this.tIsl, this.tpad);
    if (a.equals("tup")) { if (this.testMode) return "=test: anvil"; return @PKG@.ShCore.upgrade(u); }
    long now = System.currentTimeMillis();
    if (now - this.tpickArm > 10000L) { this.tpickArm = now; return "=Click Pick up again to take this totem into your inventory (tier, modifiers and booster stay with it)."; }
    this.tpickArm = 0L;
    return @PKG@.ShCore.pickTotem(u, k, this.tIsl, this.tpad, cs);
  }
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
# fix3: true = another mod's page took the screen (Upgrade -> SkyyGear's Anvil opened): no rebuild() and no close() afterwards
M(page, r"""
public static boolean handedOff(String a, String r) {
  return "tup".equals(a) && r != null && r.startsWith("+");
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
    if (handedOff(a, r)) return;   // fix3: the Anvil page replaced this one - never update a page that is gone
    rebuild();
  }
}""")
pfn = mk("ShPageFn", None, ("java.util.function.Function",))
F(pfn, "public boolean totem;")
C(pfn, "public ShPageFn() { this.totem = false; }")
C(pfn, "public ShPageFn(boolean t) { this.totem = t; }")
M(pfn, "public Object apply(Object o) { @PKG@.ShPage pg = new @PKG@.ShPage((@PR@) o); if (this.totem) { pg.fromTotem = true; pg.near = true; pg.tab = 3; } return pg; }")

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

# ================= /shardadmin (skyyshards.admin): give <player> | info <player> | unplace <player> | unload <player> | totem <player> <type> [tier] =================
adm = mk("ShAdmin")
M(adm, r"""
public static String keyOfName(String name) {
  @PR@ t = @UNI@.get().getPlayerByUsername(name, com.hypixel.hytale.server.core.NameMatching.EXACT_IGNORE_CASE);
  return t == null ? null : @PKG@.ShCfg.pkey(t.getUuid());
}""")
# fix3: an inventory is touched only on its own world thread (/shardadmin give / totem for a player in another world = refused)
F(adm, "public static volatile java.util.function.Function THREAD_TEST = null;")
M(adm, r"""
public static boolean sameThread(@REF@ r) {
  try {
    java.util.function.Function f = THREAD_TEST;
    if (f != null) return Boolean.TRUE.equals(f.apply(r));
    @ST@ st = r.getStore();
    return st != null && st.isInThread();
  } catch (Throwable t) { return false; }
}""")
# fix3 + fix4: /shardadmin give / totem touch an inventory only on its own world thread and never while the target switches profile
# (PROFILES-CONTRACT rule 5); null = go on
M(adm, r"""
public static String giveGate(java.util.UUID u, String name, @REF@ r) {
  if (!sameThread(r)) return "-" + name + " is in another world - run this from their world (or bring them here).";
  if (@PKG@.ShCore.busy(u)) return "-" + name + " is switching profile - try again in a moment.";
  return null;
}""")
M(adm, r"""
public static java.util.ArrayList run(String args) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] a = args == null ? new String[0] : args.trim().split("\\s+");
  if (a.length < 2) { out.add("-Usage: /shardadmin give <player> | info <player> | unplace <player> | unload <player> | totem <player> <type> [tier]"); return out; }
  String cmd = a[0].toLowerCase();
  @PR@ t = @UNI@.get().getPlayerByUsername(a[1], com.hypixel.hytale.server.core.NameMatching.EXACT_IGNORE_CASE);
  if (t == null || !t.isValid()) { out.add("-That player is not online."); return out; }
  String k = @PKG@.ShCfg.pkey(t.getUuid());
  if (cmd.equals("give")) {
    @REF@ r = t.getReference();
    if (r == null || !r.isValid()) { out.add("-That player is not in a world."); return out; }
    String gg = giveGate(t.getUuid(), t.getUsername(), r);   // fix3 + fix4
    if (gg != null) { out.add(gg); return out; }
    long got = @PKG@.ShInv.give(@PKG@.ShInv.containers(r.getStore(), r), @PKG@.ShCore.SHARD, 1L);
    out.add(got > 0L ? "+Gave a Farming Shard to " + t.getUsername() + "." : "-Their inventory is full.");
    if (got > 0L) @PKG@.ShSay.to(t, "[Shards] You got a Farming Shard. Place it on your island, then right-click it.", "#39f493");
    return out;
  }
  if (cmd.equals("totem")) {   // 0.2: any totem at any tier (testing the tiers before SkyyGear's Anvil exists)
    if (a.length < 3) { out.add("-Usage: /shardadmin totem <player> <type> [tier 1-5]. Types: " + String.join(", ", @PKG@.ShTotem.KEYS)); return out; }
    int ti = @PKG@.ShTotem.idx(a[2].toLowerCase());
    if (ti < 0) { out.add("-Unknown totem type " + a[2] + ". Types: " + String.join(", ", @PKG@.ShTotem.KEYS)); return out; }
    int tier = a.length > 3 ? @PKG@.ShTotem.tierOf(a[3]) : 1;
    @REF@ r = t.getReference();
    if (r == null || !r.isValid()) { out.add("-That player is not in a world."); return out; }
    String gg = giveGate(t.getUuid(), t.getUsername(), r);   // fix3 + fix4
    if (gg != null) { out.add(gg); return out; }
    String[] f = new String[] { @PKG@.ShTotem.KEYS[ti], String.valueOf(tier), "", "", "0", @PKG@.ShTotem.newUid() };
    boolean ok = @PKG@.ShInv.giveStack(@PKG@.ShInv.containers(r.getStore(), r), @PKG@.ShTotem.stack(f, @PKG@.ShCore.now()));
    if (ok) @PKG@.ShCore.tlog("admin give " + t.getUsername() + " " + @PKG@.ShTotem.fmt(f));
    out.add(ok ? "+Gave " + @PKG@.ShTotem.name(f) + " to " + t.getUsername() + "." : "-Their inventory is full.");
    return out;
  }
  java.util.Properties p = @PKG@.ShStore.get(k);
  if (cmd.equals("info")) {
    if (p == null) { out.add("-The shard file of " + t.getUsername() + " could not be read."); return out; }
    @PKG@.ShTotem.moonBlade(k);   // fix4: outside the lock
    @PKG@.ShStore.LOCK.lock(); try {
      @PKG@.ShMath.settleAll(p, @PKG@.ShCore.now());
      out.add("=" + t.getUsername() + " (" + k + "): placed " + @PKG@.ShStore.str(p, @PKG@.ShMath.K + ".placed") + ", storage tier " + @PKG@.ShMath.storageTier(p) + ", world " + @PKG@.ShWorlds.name(k) + (@PKG@.ShWorlds.loaded().contains(@PKG@.ShWorlds.name(k)) ? " (loaded)" : " (unloaded)"));
      for (int i = 0; i < @PKG@.ShMath.SLOTS; i++) if (@PKG@.ShMath.hasIsland(p, i)) out.add("=  slot " + (i + 1) + ": wheat size " + @PKG@.ShMath.size(p, i) + ", stored " + @PKG@.ShMath.stored(p, i) + " / " + @PKG@.ShMath.capOf(p, i) + " (+" + @PKG@.ShMath.ench(p, i) + " Enchanted), " + @PKG@.ShCfg.dec(@PKG@.ShMath.rate(p, i, @PKG@.ShCore.now())) + " / min, totems " + @PKG@.ShStore.str(p, @PKG@.ShMath.ik(i, "totems")));
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
  out.add("-Unknown: " + cmd + ". Usage: /shardadmin give <player> | info <player> | unplace <player> | unload <player> | totem <player> <type> [tier]");
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
  super("(admin) give <player> | info <player> | unplace <player> | unload <player> | totem <player> <type> [tier]");
  requirePermission("skyyshards.admin");
  this.argsArg = withRequiredArg("args", "give <player>, info <player>, unplace <player>, unload <player> or totem <player> <type> [tier]", @ATY@.GREEDY_STRING);
}""")
M(admv, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try { @PKG@.ShAdmin.send(pr, @PKG@.ShAdmin.run(String.valueOf(ctx.get(this.argsArg)))); }
  catch (Throwable t) { @PKG@.ShCfg.warn("/shardadmin failed: " + t); }
}""")
admc = mk("ShAdminCmd", T["APC"])
C(admc, r"""
public ShAdminCmd() {
  super("shardadmin", "(admin) Shards: give <player> | info <player> | unplace <player> | unload <player> | totem <player> <type> [tier]");
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
  b.put("shard:fn:totem", new @PKG@.ShTotemFn());   // 0.2: SkyyGear's Anvil tier-up (cost / up / describe / key)
  b.put("shard:version", "@VERSION@");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@PAGEID@", new @PKG@.ShPageFn());
  @OCU@.registerSimple(this, @PKG@.SkyyShardsPlugin.class, "@TPAGEID@", new @PKG@.ShPageFn(true));   // 0.2: right-click a totem
  getEntityStoreRegistry().registerSystem(new @PKG@.ShPlace());
  getCommandRegistry().registerCommand(new @PKG@.ShAdminCmd());
  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.ShTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyShards] @VERSION@ ready (@KITID@) - Farming Shard (Skyy_Shard_Farming portal, menu page @PAGEID@), one shard world per profile (skyy-shard-<pkey>, Farming region at x @RX@), hub + 6 slots, Wheat island Small / Medium / Large, TOTEMS (" + @PKG@.ShTotem.KEYS.length + " types, tiers I-V, 2 modifier slots, booster, Harvest Moon, menu Place / Pick up / Craft, totem page @TPAGEID@), lazy production + storage + Collect; shard crafting from rebirth " + @PKG@.ShCfg.SHARD_RB + "; guards via SkyyIslands 0.5.8 (shard:fn:allowed" + (@PKG@.ShRole.guarded() ? ", island:shardguard seen" : ", island:shardguard not seen yet") + "); bridge shard:fn:allowed / open / world / totem; " + c + "; data in " + dir);
}""".replace("@KITID@", KIT_ID).replace("@TPAGEID@", TOTEM_PAGE_ID).replace("@PAGEID@", PAGE_ID).replace("@RX@", str(REGION_X)))
M(pl, r"""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  java.util.Map b = @PKG@.ShCfg.bridge();
  try { b.remove("shard:fn:allowed"); b.remove("shard:fn:open"); b.remove("shard:fn:world"); b.remove("shard:fn:totem"); b.remove("shard:version"); } catch (Throwable t) { }
  super.shutdown();
}""")

ALLC = [cfg, st, tot, tfn, mth, geo, fill, wld, op, say, role, gate, inv, pay, core, w2, hop, tick, rng, sweep, part, place, chk, page, pfn, bfn, adm, admv, admc, pl]
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
# ---- 0.2 totems: item (in hand = the vanilla Healing Totem projectile model + our texture), block (the statue model, our texture; Rain =
# the folded MoreTotems Water Totem), modifiers. Textures / icons are recoloured from vanilla at BUILD time (never committed).
def _ramp(hexes):
    return tuple(tuple(int(h_[k_:k_ + 2], 16) for k_ in (1, 3, 5)) for h_ in hexes)


GEN = {}          # jar path -> bytes (written after assemble)
_vtex = AZ.read(TOTEM_TEX_SRC)
_vicon = AZ.read(TOTEM_ICON_SRC)
TOTEM_JSON = {}
for _i, _t in enumerate(TOTEMS):
    _tex_path = "Blocks/SkyyShards/Totem_%s.png" % _t[1]
    _icon_path = "Icons/ItemsGenerated/%s.png" % TOTEM_ITEM[_i]
    _model = TOTEM_MODEL
    _hand_model = "Items/Deployables/Healing_Totem/Healing_Totem_Projectile.blockymodel"
    if _t[0] == "rain" and len(MT) == 3:          # the MoreTotems Water Totem fold (MIT, credit Nagatwin)
        _model = "Blocks/SkyyShards/Totem_Rain.blockymodel"
        _hand_model = _model
        GEN["Common/" + _model] = MT["model"]
        GEN["Common/" + _tex_path] = MT["tex"]
        GEN["Common/" + _icon_path] = MT["icon"]
    else:
        GEN["Common/" + _tex_path] = SA.recolor(_vtex, _ramp(_t[6]), rank=0.4)
        GEN["Common/" + _icon_path] = SA.recolor(_vicon, _ramp(_t[6]), rank=0.4)
    _farm = KIND in _t[4]
    TOTEM_JSON["Server/Item/Items/SkyyShards/Totems/%s.json" % TOTEM_ITEM[_i]] = {
        "TranslationProperties": {"Name": "server.items.%s.name" % TOTEM_ITEM[_i], "Description": "server.items.%s.description" % TOTEM_ITEM[_i]},
        "Icon": _icon_path, "Categories": ["Items.Utility"], "MaxStack": 1, "Quality": "Uncommon", "PlayerAnimationsId": "Item",
        "Model": _hand_model, "Texture": _tex_path, "Scale": 0.305,
        "IconProperties": {"Rotation": [22.5, 45, 22.5], "Scale": 0.305, "Translation": [0, -39.6]}}
    TOTEM_JSON["Server/Item/Items/SkyyShards/Totems/%s.json" % TOTEM_BLOCK[_i]] = {
        "TranslationProperties": {"Name": "server.items.%s.name" % TOTEM_ITEM[_i]}, "Icon": _icon_path, "MaxStack": 1,
        "BlockType": {"DrawType": "Model", "Material": "Solid", "Opacity": "Transparent", "CustomModel": _model,
                      "CustomModelTexture": [{"Texture": _tex_path, "Weight": 1}], "CustomModelScale": 1,
                      "BlockParticleSetId": "Stone", "BlockSoundSetId": "Stone", "PhysicalMaterialId": "Stone", "VariantRotation": "NESW",
                      "Gathering": {"Breaking": {"GatherType": "Unbreakable"}},
                      "Interactions": {"Use": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": TOTEM_PAGE_ID}}]}}}}
_micon = AZ.read(MOD_ICON_SRC)
_MOD_RAMPS = [("#0d2f5c", "#2f7fd6", "#bfe6ff"), ("#6b3a00", "#f0a020", "#fff2a0"), ("#2f4a12", "#7fbf3a", "#e4ffb0"),   # ui-data: texture ramp (not UI)
              ("#22180c", "#5c4a2a", "#b0a070"), ("#3a2a1a", "#9a7a5a", "#f0e0c8"), ("#4a1a5c", "#d070e0", "#ffe0ff")]   # ui-data: texture ramp (not UI)
for _i, _m in enumerate(MODS):
    _icon_path = "Icons/ItemsGenerated/%s.png" % MOD_ITEM[_i]
    GEN["Common/" + _icon_path] = SA.recolor(_micon, _ramp(_MOD_RAMPS[_i]), rank=0.4)
    TOTEM_JSON["Server/Item/Items/SkyyShards/Totems/%s.json" % MOD_ITEM[_i]] = {
        "TranslationProperties": {"Name": "server.items.%s.name" % MOD_ITEM[_i], "Description": "server.items.%s.description" % MOD_ITEM[_i]},
        "Icon": _icon_path, "Categories": ["Items.Utility"], "MaxStack": 16, "Quality": "Uncommon", "PlayerAnimationsId": "Item"}
for pre in ("", "server."):
    for _i, _t in enumerate(TOTEMS):
        _farm = KIND in _t[4]
        _what = ("A worker totem: it harvests the crops in its range." if _t[3] else "A support totem: more crops for its island.")
        LANG.append("%sitems.%s.name=%s" % (pre, TOTEM_ITEM[_i], _t[2]))
        LANG.append("%sitems.%s.description=%s %s Place it from your shard menu (Totems tab)." % (pre, TOTEM_ITEM[_i], _what,
                    "" if _farm else "Works in the %s Shard (a later update)." % _t[4][0]))
    for _i, _m in enumerate(MODS):
        LANG.append("%sitems.%s.name=%s Modifier" % (pre, MOD_ITEM[_i], _m[2]))
        LANG.append("%sitems.%s.description=A totem modifier: %s. Add it in the shard menu (Totems tab)." % (pre, MOD_ITEM[_i], _m[3]))
# fix3: the MIT notice travels with the copied model / texture / icon (the jar ships no LICENSE file; its manifest names the author
# "Nagatwin" and the repo, which answered 404 on 2026-10-14 - the copyright line names the manifest's author; Skyy to confirm)
CREDITS = ("SkyyShards uses the Water Totem model, texture and icon from MoreTotems by Nagatwin\n"
           "(https://github.com/poiuytrezaur/Nagatwin.MoreTotemsPlugin), MIT licence, for its Rain Totem.\n"
           "Copied at build time from the installed MoreTotemsPlugin jar. Those files are used under this licence:\n\n"
           "MIT License\n\n"
           "Copyright (c) Nagatwin\n\n"
           "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
           "of this software and associated documentation files (the \"Software\"), to deal\n"
           "in the Software without restriction, including without limitation the rights\n"
           "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
           "copies of the Software, and to permit persons to whom the Software is\n"
           "furnished to do so, subject to the following conditions:\n\n"
           "The above copyright notice and this permission notice shall be included in all\n"
           "copies or substantial portions of the Software.\n\n"
           "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
           "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
           "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
           "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
           "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
           "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
           "SOFTWARE.\n")
files = {
    "Server/Instances/SkyyShard/instance.bson": json.dumps(template, indent=2) + "\n",
    "Server/Instances/SkyyShard/resources/InstanceData.json": '{\n  "HadPlayer": false\n}\n',
    "Server/Item/Items/SkyyShards/%s.json" % SHARD_ITEM: json.dumps(item, indent=2),
    "Server/Languages/en-US/server.lang": "\n".join(LANG) + "\n",
}
for _p, _j in TOTEM_JSON.items():
    files[_p] = json.dumps(_j, indent=2)
if len(MT) == 3:
    files["CREDITS-MoreTotems.txt"] = CREDITS
jar = os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)
man = B.manifest("SkyyShards", VERSION, "SkyWynn Shards: the Farming Shard - a portal block you place on your island that opens your own private shard world (one per profile): a hub island with 6 fixed slots, a Wheat island that grows Small / Medium / Large in place, shard storage, Collect (Farming XP + collections are paid when you collect) and the shard menu. 0.2: totems (20 types, tiers I-V with their own item document, 2 modifier slots, an optional booster, Harvest Moon Enchanted crops, crafted / placed / picked up in the menu; the Rain Totem uses the Water Totem of MoreTotems by Nagatwin, MIT) and shard crafting from rebirth 2. Protected by SkyyIslands 0.5.8. Server Setup: Shards.", PKG + ".SkyyShardsPlugin")
man["IncludesAssetPack"] = True
B.assemble(jar, man, OUT, extra_files=files)
with zipfile.ZipFile(jar, "a") as _jz:
    _jz.writestr("Common/" + TEX_PATH, _tex)
    _jz.writestr("Common/" + ICON_PATH, _icon)
    for _p, _b in GEN.items():          # 0.2: the generated totem / modifier textures and icons (+ the MoreTotems fold)
        _jz.writestr(_p, _b)
with zipfile.ZipFile(jar) as _jz:
    _bad = [n for n in _jz.namelist() if n.lower().endswith(".ui")]
    if _bad:
        raise SystemExit("SkyyShards jar must not ship .ui files (inline pages only): %s" % _bad)
print("assembled", jar, os.path.getsize(jar), "bytes (with the generated gold portal texture + the icon)")
if "--deploy" in sys.argv:
    raise SystemExit("SkyyShards: --deploy is not supported here - deploys go through tools/deploy_set.py")
