"""SkyyTownProbe 0.1 - build script (javassist via jpype). NEW throwaway probe mod: the T0 probe round of research/Zone-1-Town-Build-Plan.md
section 9 (Skyy 2026-10-08: "yes plan the zone 1 town while i test", "keep v2, its hub enough", "1. yes 2. keep all 3. yes 4. yes 5. yes
6. yes" - docs/answered/world.md). Admin-only, pinned for ONE test session, then removed from the SET (like SkyyMonkProbe / SkyyReelProbe).
Run:   python SkyyTownProbe/build_skyytownprobe_0.1.py   -> SkyyTownProbe/SkyyTownProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyTownProbe/test_skyytownprobe_0.1.py    (-Xverify:all, every code path executed on engine stand-ins, permissions,
       start twice on a scratch copy of live data, engine-access audit; scratch tools/dev/scratch/townprobe01/)

NO ASSET SHIPPED (the 2026-10-08 SkyyArmory lesson): the jar holds classes only (IncludesAssetPack false). The NPC uses the vanilla role
Temple_Kweebec_Static (Variant of Template_Temple: Invulnerable, MotionStatic, greets, NO InteractionInstruction = no barter shop), the
vanilla Use root every NPC gets ("*UseNPC", RoleBuilderSystem) and the vanilla hint key server.interactionHints.trade; the page opens
from our UseEntityEvent$Pre system (no RootInteraction / role / lang asset needed). Every vanilla id / path is checked against Assets.zip
at build time.

THE COMMAND  /townprobe (alias /tprobe); op only: requirePermission skyytownprobe.admin + no permission groups (lint perm_group_leaks).
World-changing actions only run in the Zone 1 test island world (skywynn_z1, SkyyWorldGen 0.1); anywhere else they refuse (harmless).
Every action writes clear "[SkyyTownProbe] ..." INFO lines (anchor offset, box, ms taken, what spawned) - Skyy sends them back.
  /townprobe [help]          the command list
  /townprobe temple [0-3]    pastes the vanilla spawn temple (Grasslands_Spawn) a few blocks in front of you; 0 = ROTATION_0 (door
                             south, to the sea), 1 / 2 / 3 = ROTATION_90 / 180 / 270. Append e (0e) = WITH the prefab's entities
                             (default OFF: the Earth Crystal Golem spawn marker etc. are skipped; when ON each one gets a UUID through
                             the paste's entity consumer and undo removes them). Steps (vanilla PrefabPasteAction):
                             load the paste region (PrefabUtil.loadPasteRegionAsync), SNAPSHOT it (vanilla PrefabSnapshotUtil.createSnapshot
                             logic, written into OUR data folder, not the world's snapshots dir), register the undo record (memory),
                             paste (PrefabUtil.paste, FORCE) - a paste that throws partway keeps its record, so undo still restores -
                             then the .lpf is written and only after it lands the .properties (TpIoDone). A job that arrives after the
                             60 s busy escape is dropped (ticket).
                             Logs: prefab anchor + buffer box (raw and rotated), the target block, the world box, where the door / causeway
                             foot landed, child prefabs + Prefab_Spawner_Block count after the paste, prefab entities skipped, ms per step.
  /townprobe undo            the newest probe change is put back: the snapshot is pasted back with FORCE (vanilla PrefabRemoveAction),
                             spawned probe entities are removed, its files are deleted. Undo is a stack (newest first, at most 20).
  /townprobe lane            a 40-block cobble lane (S-curve, 3 wide) ahead of you that follows the ground: heights are smoothed to at
                             most 1 block per step, a Rock_Stone_Cobble_Stairs block on every step, stone fill under raised parts,
                             3 blocks of air cleared above. Pasted through the same snapshot pipeline (undo restores it exactly).
  /townprobe piece <prefab path | alias> [rot]   any vanilla prefab under Server/Prefabs (with or without .prefab.json, / or . separated),
                             entities OFF unless the rot ends in e; refused when the rotated box is over MAX_CELLS (300 000). Aliases: stall, cottage, softwood, cabin, plains, lighthouse, tower,
                             well, pool, path.
  /townprobe npc             spawns "Mossby" (vanilla Temple_Kweebec_Static) 3 blocks ahead, facing you; F (Use) opens the SkyyBazaar
                             page through its registered page id "SkyyBazaar" (OpenCustomUIInteraction.PAGE_CODEC -> CustomPageSupplier;
                             SkyyBazaar is read only, never edited); hint "Press [F] to trade"; a bark in chat within 8 blocks (once per
                             player per 60 s). Running it again while Mossby exists counts the probe NPCs at that spot (pass = 1 after a
                             restart, never 2) instead of spawning another.
  /townprobe pebble          the vanilla Rubble_Stone_Mossy projectile model, scaled x5, as an NPC (role Temple_Kweebec_Static); logs
                             whether the role kept the rock model or replaced it (then the rock is forced back and that is logged too).
  /townprobe zone [all|off]  a 9-corner polygon (about 20 blocks across) around you, in MEMORY only: break / damage / place / use blocks
                             inside are refused for non-admins (zone all: for everyone, admins too - so Skyy can test it alone);
                             outside stays allowed; enter / leave lines in chat; every refusal logged. zone off removes it.
  /townprobe sign            places a vanilla Furniture_Village_Sign 2 blocks ahead (snapshot + undo). The engine has NO sign text (no
                             text state / component in HytaleServer.jar or Assets.zip - build-time desk check below), so it shows the
                             fallback: a floating nameplate "Waiting Square" on a tiny mossy pebble prop on the sign (Nameplate +
                             PropComponent + Intangible, the vanilla prefab-marker component set).
SAVED DATA: only what undo needs, in <server>/mods/Skyy_SkyyTownProbe/undo/ (<n>.properties + <n>.lpf snapshot); undo deletes them and
the folders once empty; a start deletes broken / orphan undo files (lost snapshot, unreadable record, lone .lpf / .tmp). An NPC record
whose area is not loaded is never 'forgotten' by undo (that would leave the entity in the world). The zone, barks and per-player state are memory only.
ENGINE SEAM: the calls that need a live world / chunk store / NPC plugin (find + load a prefab, load a paste region, paste, chunk height
+ block id, the entity store, uuid -> ref, role index, spawn) go through TpEng's static wrappers; the harness swaps them for stand-ins
(TpEng.API) and checks the real lines by bytecode (same call shapes as vanilla PrefabPasteAction / PrefabRemoveAction / SpawnNpcEffect)
+ the access audit. Everything else (snapshot building from a PasteRegion, lane / sign buffers, snapshot file IO, records, the page
open, NPC components, guards, barks) runs for real in the harness.
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI

if "--deploy" in sys.argv:
    raise SystemExit("SkyyTownProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyytownprobe.admin"
WORLD = "skywynn_z1"                       # SkyyWorldGen 0.1's Zone 1 test island
MAX_RECS = 20
MAX_CELLS = 300000                         # /townprobe piece refuses a (rotated) box bigger than this (the temple is 42 000 cells)
TEMPLE = "Monuments/Unique/Temple/Portal/Grasslands_Spawn/Unique_Portal_Grasslands_Monuments_Unique_Portal_Grasslands_001.prefab.json"
ALIASES = [
    ("stall", "Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001.prefab.json"),
    ("cottage", "Monuments/Incidental/Quartzite/Cottage/Incidental_Quartzite_001.prefab.json"),
    ("softwood", "Monuments/Incidental/Softwood/Cottage/Incidental_Softwood_001.prefab.json"),
    ("cabin", "Monuments/Incidental/Grasslands/Hunting/Cabins/Incidental_Grasslands_Cabins_Incidentals_Grasslands_Hunting_Cabins_001.prefab.json"),
    ("plains", "Monuments/Incidental/Grasslands/Houses/Plains/Incidental_Grasslands_Plains_Incidentals_Grasslands_Houses_Plains_001.prefab.json"),
    ("lighthouse", "Monuments/Incidental/Grasslands/Houses/Towers/Lighthouses/Incidental_Grasslands_Lighthouses_Incidentals_Grasslands_Towers_Lighthouses_001.prefab.json"),
    ("tower", "Npc/Kweebec/Oak/Guard_Towers/Kweebec_Oak_Guard_Towers_001.prefab.json"),
    ("well", "Npc/Kweebec/Oak/Well/Kweebec_Oak_Well_001.prefab.json"),
    ("pool", "Npc/Kweebec/Oak/Water_Pool/Kweebec_Oak_Water_Pool_001.prefab.json"),
    ("path", "Spawn/Pathways/Spawn_Zone1_Pathway_001.prefab.json"),
]
ROLE = "Temple_Kweebec_Static"             # vanilla: Invulnerable, MotionStatic, no InteractionInstruction (no barter shop)
ROCK = "Rubble_Stone_Mossy"                # Server/Models/Projectiles/Items/Rubble/Rubble_Stone_Mossy.json
ROCK_SCALE, HOLO_SCALE = 5.0, 0.35
PAGE = "SkyyBazaar"                        # SkyyBazaar 0.1.5 OpenCustomUIInteraction.registerSimple(..., "SkyyBazaar", ...)
HINT = "server.interactionHints.trade"     # vanilla lang: "Press [{key}] to trade" (Kweebec_Merchant's own hint)
USE_ROOT = "*UseNPC"                       # RoleBuilderSystem.onEntityAdd: every NPC's Use root
SIGN = "Furniture_Village_Sign"
LANE_TOP, LANE_STAIR, LANE_FILL = "Rock_Stone_Cobble", "Rock_Stone_Cobble_Stairs", "Rock_Stone"
LANE_LEN, LANE_AMP, LANE_HALF = 40, 5, 1
BARK_R, BARK_MS = 8.0, 60000
POLY_R = [10, 8, 11, 9, 10, 7, 11, 9, 8]   # the zone's 9 corner radii (about 20 blocks across, irregular on purpose)
NPC_NAME, PEBBLE_NAME, HOLO_TEXT = "Mossby (town probe)", "Pebble (town probe)", "Waiting Square"
BARK_NPC = "[Mossby] Welcome to the Department of Arrivals! Press F to open the Bazaar."
BARK_PEBBLE = "[Pebble] ...the mossy rock wobbles. (Pebble has nothing to say yet.)"
SUI.verify()
COL_OK, COL_ERR, COL_INFO, COL_BARK = SUI.COLOR["success"], SUI.COLOR["error"], SUI.COLOR["info"], SUI.COLOR["gold"]

# ================= build-time desk checks (Assets.zip, read only) =================
az = zipfile.ZipFile(ASSETS)
AZ_NAMES = set(az.namelist())


def vanilla_json(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


for _k in [TEMPLE] + [p for _, p in ALIASES]:
    if "Server/Prefabs/" + _k not in AZ_NAMES:
        raise SystemExit("prefab %s not in Assets.zip" % _k)
_t = vanilla_json("Server/Prefabs/" + TEMPLE)
if (_t.get("anchorX"), _t.get("anchorY"), _t.get("anchorZ")) != (6, 13, 6):
    raise SystemExit("the temple's anchor changed: %r - re-check the placement notes" % ((_t.get("anchorX"), _t.get("anchorY"), _t.get("anchorZ")),))
def _cells(d):
    xs, ys, zs = [b["x"] for b in d["blocks"]], [b["y"] for b in d["blocks"]], [b["z"] for b in d["blocks"]]
    return (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1) * (max(zs) - min(zs) + 1)
PIECE_CELLS = dict((_k, _cells(vanilla_json("Server/Prefabs/" + _k))) for _k in [TEMPLE] + [p for _, p in ALIASES])
if max(PIECE_CELLS.values()) > MAX_CELLS:
    raise SystemExit("a named prefab is bigger than MAX_CELLS %d: %r" % (MAX_CELLS, PIECE_CELLS))
TEMPLE_SPAWNERS = sum(1 for b in _t["blocks"] if b.get("name") == "Prefab_Spawner_Block")
TEMPLE_ENTS = len(_t.get("entities") or [])
_roles = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
if ROLE not in _roles:
    raise SystemExit("vanilla role %s missing" % ROLE)
_r = vanilla_json(_roles[ROLE])
if _r.get("Type") != "Variant" or _r.get("Reference") != "Template_Temple" or (_r.get("Modify") or {}).get("MotionStatic") is not True:
    raise SystemExit("%s changed: %r" % (ROLE, _r))
_tt = vanilla_json(_roles["Template_Temple"])
if _tt.get("Invulnerable") is not True or "InteractionInstruction" in _tt or "InteractionInstruction" in _r:
    raise SystemExit("Template_Temple changed (Invulnerable %r, InteractionInstruction present?) - the probe NPC must stay shop-less" % _tt.get("Invulnerable"))
if "Server/Models/Projectiles/Items/Rubble/%s.json" % ROCK not in AZ_NAMES:
    raise SystemExit("rock model %s missing" % ROCK)
_lang = az.read("Server/Languages/en-US/server.lang").decode("utf-8")
if not re.search(r"(?m)^interactionHints\.trade\s*=", _lang):
    raise SystemExit("vanilla hint interactionHints.trade missing")
_items = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))
for _b in (SIGN, LANE_TOP, LANE_STAIR, LANE_FILL):
    if _b not in _items or "BlockType" not in vanilla_json(_items[_b]):
        raise SystemExit("block %s missing in Assets.zip" % _b)
_sign = vanilla_json(_items[SIGN])
_sign_txt = json.dumps(_sign)
SIGN_HAS_TEXT = any(k in _sign_txt for k in ('"State"', '"Text"', '"SignText"', '"BlockEntity"'))
if SIGN_HAS_TEXT:
    raise SystemExit("Furniture_Village_Sign now carries a text / state key - re-check the sign probe (text may be supported)")
_stairs = vanilla_json(_items[LANE_STAIR])["BlockType"]
if _stairs.get("VariantRotation") != "UpDownNESW" or "North" not in (_stairs.get("Supporting") or {}):
    raise SystemExit("%s changed shape (VariantRotation / Supporting North): %r" % (LANE_STAIR, _stairs.get("VariantRotation")))
print("desk: temple %d Prefab_Spawner_Block, %d prefab entities, %d cells; role %s shop-less; rock %s; sign has no text state; %d aliases (largest %d cells, cap %d)"
      % (TEMPLE_SPAWNERS, TEMPLE_ENTS, PIECE_CELLS[TEMPLE], ROLE, ROCK, len(ALIASES), max(PIECE_CELLS[p] for _, p in ALIASES), MAX_CELLS))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.townprobe"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "WORLD": WORLD,
    "COLOK": COL_OK, "COLERR": COL_ERR, "COLINF": COL_INFO, "COLBRK": COL_BARK,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "ICE": "com.hypixel.hytale.component.system.ICancellableEcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "ARCH": "com.hypixel.hytale.component.Archetype",
    "HOL": "com.hypixel.hytale.component.Holder",
    "RR": "com.hypixel.hytale.component.RemoveReason",
    "ADR": "com.hypixel.hytale.component.AddReason",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "HR": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "V3I": "org.joml.Vector3i",
    "V3IC": "org.joml.Vector3ic",
    "V3D": "org.joml.Vector3d",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "PU": "com.hypixel.hytale.server.core.util.PrefabUtil",
    "PBU": "com.hypixel.hytale.server.core.prefab.selection.buffer.PrefabBufferUtil",
    "PS": "com.hypixel.hytale.server.core.prefab.PrefabStore",
    "IPB": "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.IPrefabBuffer",
    "PBF": "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.PrefabBuffer",
    "PBB": "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.PrefabBuffer$Builder",
    "PBE": "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.PrefabBufferBlockEntry",
    "CHP": "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.PrefabBuffer$ChildPrefab",
    "ENC": "com.hypixel.hytale.server.core.prefab.selection.buffer.impl.IPrefabBuffer$EntityConsumer",
    "PREG": "com.hypixel.hytale.server.core.util.PrefabUtil$PasteRegion",
    "PSEC": "com.hypixel.hytale.server.core.util.PrefabUtil$PasteRegion$Section",
    "PROT": "com.hypixel.hytale.server.core.prefab.PrefabRotation",
    "ROT": "com.hypixel.hytale.server.core.asset.type.blocktype.config.Rotation",
    "RTUP": "com.hypixel.hytale.server.core.asset.type.blocktype.config.RotationTuple",
    "BT": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BTAM": "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "WCH": "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "FR": "com.hypixel.hytale.math.util.FastRandom",
    "CF": "java.util.concurrent.CompletableFuture",
    "NPCP": "com.hypixel.hytale.server.npc.NPCPlugin",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "MDL": "com.hypixel.hytale.server.core.asset.type.model.config.Model",
    "MDA": "com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset",
    "MC": "com.hypixel.hytale.server.core.modules.entity.component.ModelComponent",
    "PM": "com.hypixel.hytale.server.core.modules.entity.component.PersistentModel",
    "UUC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "ITB": "com.hypixel.hytale.server.core.modules.entity.component.Interactable",
    "ITS": "com.hypixel.hytale.server.core.modules.interaction.Interactions",
    "ITY": "com.hypixel.hytale.protocol.InteractionType",
    "NPL": "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "DNC": "com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent",
    "PDN": "com.hypixel.hytale.server.core.modules.entity.component.PersistentDisplayName",
    "INT": "com.hypixel.hytale.server.core.modules.entity.component.Intangible",
    "PROP": "com.hypixel.hytale.server.core.modules.entity.component.PropComponent",
    "UEPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre",
    "BBE": "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
    "PLBE": "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent",
    "DBE": "com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent",
    "UBPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre",
    "OCU": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction",
    "CPS": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction$CustomPageSupplier",
    "CODEC": "com.hypixel.hytale.codec.Codec",
    "EEI": "com.hypixel.hytale.codec.EmptyExtraInfo",
    "CUP": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "PAIR": "it.unimi.dsi.fastutil.Pair",
    "PATH": "java.nio.file.Path",
}
PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "hasPermission"), (T["PR"], "getComponentType"), (T["MSG"], "raw"), (T["MSG"], "color"),
             (T["PLA"], "getComponentType"), (T["PLA"], "getPageManager"), (T["WLD"], "getName"), (T["WLD"], "getEntityStore"),
             (T["WLD"], "getChunkIfLoaded"), (T["EST"], "getStore"), (T["EST"], "getRefFromUUID"), (T["EST"], "REGISTRY"),
             (T["TC"], "getPosition"), (T["TC"], "getRotation"), (T["HR"], "getHorizontalAxisDirection"),
             (T["PU"], "loadPasteRegionAsync"), (T["PU"], "paste"), (T["PU"], "NOOP_BLOCK_ENTITY_CONSUMER"), (T["PU"], "NOOP_ENTITY_CONSUMER"),
             (T["PBU"], "getCached"), (T["PBU"], "writeToFileAsync"), (T["PBU"], "readFromFileAsync"), (T["PS"], "get"),
             (T["PS"], "findAssetPrefabPath"), (T["IPB"], "getMinX"), (T["IPB"], "getMaxY"), (T["IPB"], "getAnchorY"),
             (T["IPB"], "getChildPrefabs"), (T["IPB"], "forEachEntity"), (T["PBF"], "newBuilder"), (T["PBF"], "newAccess"),
             (T["PBB"], "addColumn"), (T["PBB"], "build"), (T["PREG"], "isFullyLoaded"), (T["PREG"], "getSectionAtBlock"),
             (T["PSEC"], "getBlock"), (T["PSEC"], "getState"), (T["PSEC"], "getFluid"), (T["PSEC"], "getFluidLevel"),
             (T["PSEC"], "getSupport"), (T["PSEC"], "getRotation"), (T["PSEC"], "getFiller"), (T["PROT"], "VALUES"), (T["PROT"], "rotate"),
             (T["PROT"], "getRotation"), (T["ROT"], "rotateYaw"), (T["RTUP"], "index"), (T["BT"], "getAssetMap"), (T["BTAM"], "getIndex"),
             (T["CHU"], "indexBlock"), (T["CHU"], "indexChunkFromBlock"), (T["WCH"], "getHeight"), (T["WCH"], "getBlock"),
             (T["NPCP"], "get"), (T["NPCP"], "getIndex"), (T["NPCP"], "spawnNPC"), (T["NPCP"], "spawnEntity"), (T["NPC"], "getRoleName"),
             (T["MDA"], "getAssetMap"), (T["MDL"], "createStaticScaledModel"), (T["MDL"], "getModelAssetId"), (T["MDL"], "toReference"),
             (T["MC"], "getModel"), (T["UUC"], "getUuid"), (T["ITB"], "getComponentType"), (T["ITS"], "setInteractionHint"),
             (T["ITS"], "getInteractionId"), (T["ITS"], "setInteractionId"), (T["NPL"], "getComponentType"), (T["INT"], "INSTANCE"),
             (T["PROP"], "get"), (T["UEPRE"], "getTargetEntity"), (T["UEPRE"], "setCancelled"), (T["BBE"], "getTargetBlock"),
             (T["PLBE"], "getTargetBlock"), (T["DBE"], "getTargetBlock"), (T["UBPRE"], "getTargetBlock"), (T["OCU"], "PAGE_CODEC"),
             (T["CPS"], "tryCreate"), (T["EEI"], "EMPTY"), (T["ST"], "ensureComponent"), (T["ST"], "putComponent"),
             (T["ST"], "removeEntity"), (T["ST"], "addEntity"), (T["HOL"], "addComponent"), (T["HOL"], "ensureComponent"),
             ("com.hypixel.hytale.codec.lookup.ACodecMapCodec", "getCodecFor"), ("com.hypixel.hytale.codec.lookup.ACodecMapCodec", "getRegisteredIds"),
             (PB_, "getCommandRegistry"), (PB_, "getEntityStoreRegistry"), (PB_, "getLogger"), (PB_, "getDataDirectory"), (PB_, "shutdown")):
    B.probe(pool, c, m)

TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:3000]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs)


def jint(xs):
    return "new int[] { %s }" % ", ".join(str(int(x)) for x in xs)


# =====================================================================================================================
# TpLog: server log + chat. SINK (harness hook, null in game) also receives every chat line as "<colour>|<text>".
# =====================================================================================================================
log = mk("TpLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
F(log, "public static java.util.List LINES;")      # harness hook: every INFO / WARN line
M(log, r"""
public static void info(String msg) {
  try { if (LINES != null) LINES.add("INFO " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyTownProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LINES != null) LINES.add("WARN " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyTownProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s, String col) {
  info((pr == null ? "" : "to " + pr.getUsername() + ": ") + s);
  try { if (SINK != null) SINK.add((col == null ? "" : col) + "|" + s); } catch (Throwable t) { }
  try {
    if (pr != null) {
      @MSG@ m = @MSG@.raw(s);
      if (col != null) m = m.color(col);
      pr.sendMessage(m);
    }
  } catch (Throwable t) { }
}""")

# =====================================================================================================================
# TpLogic: pure functions (no engine objects) - the harness calls them on plain data
# =====================================================================================================================
lg = mk("TpLogic")
F(lg, "public static final String TEMPLE = %s;" % json.dumps(TEMPLE))
F(lg, "public static final String[] ALIAS = %s;" % jarr([a for a, _ in ALIASES]))
F(lg, "public static final String[] ALIAS_PATH = %s;" % jarr([p for _, p in ALIASES]))
F(lg, "public static final int[] POLY_R = %s;" % jint(POLY_R))
F(lg, "public static final int LANE_LEN = %d;" % LANE_LEN)
F(lg, "public static final int LANE_AMP = %d;" % LANE_AMP)
F(lg, "public static final int LANE_HALF = %d;" % LANE_HALF)
F(lg, "public static final int MAX_RECS = %d;" % MAX_RECS)
F(lg, "public static final long MAX_CELLS = %dL;" % MAX_CELLS)
# "0".."3" (optionally + "e" = with entities) -> 0..3; null / empty -> 0; anything else -1
M(lg, r"""
public static int parseRot(String s) {
  if (s == null) return 0;
  String t = s.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.length() == 0) return 0;
  if (t.endsWith("e")) t = t.substring(0, t.length() - 1);
  if (t.length() != 1) return -1;
  char c = t.charAt(0);
  if (c < '0' || c > '3') return -1;
  return c - '0';
}""")
M(lg, r"""
public static boolean wantsEntities(String s) {
  if (s == null) return false;
  String t = s.trim().toLowerCase(java.util.Locale.ROOT);
  return t.length() == 2 && t.endsWith("e") && parseRot(t) >= 0;
}""")
# a prefab path relative to Server/Prefabs/ ending in .prefab.json; an alias; dotted form (Npc.Kweebec.Oak.Shops.X); null = refused
M(lg, r"""
public static String prefabKey(String raw) {
  if (raw == null) return null;
  String s = raw.trim().replace('\\', '/');
  if (s.length() == 0) return null;
  String low = s.toLowerCase(java.util.Locale.ROOT);
  for (int i = 0; i < ALIAS.length; i++) if (ALIAS[i].equals(low)) return ALIAS_PATH[i];
  if (low.equals("temple")) return TEMPLE;
  if (s.startsWith("Server/Prefabs/")) s = s.substring(15);
  while (s.startsWith("/")) s = s.substring(1);
  if (s.endsWith(".prefab.json")) s = s.substring(0, s.length() - 12);
  else if (s.endsWith(".json")) s = s.substring(0, s.length() - 5);
  if (s.indexOf('/') < 0 && s.indexOf('.') > 0) s = s.replace('.', '/');
  if (s.length() == 0 || s.indexOf("..") >= 0 || s.indexOf(':') >= 0 || s.indexOf('*') >= 0 || s.endsWith("/")) return null;
  return s + ".prefab.json";
}""")
M(lg, r"""
public static String dirName(int fx, int fz) {
  if (fz < 0) return "north";
  if (fz > 0) return "south";
  if (fx > 0) return "east";
  if (fx < 0) return "west";
  return "?";
}""")
# where the anchor goes so the (rotated) box starts 'gap' blocks in front of the player, centred on the facing line
M(lg, r"""
public static int[] placeOrigin(int px, int pz, int fx, int fz, int minX, int maxX, int minZ, int maxZ, int gap) {
  int ox; int oz;
  if (fz > 0) { ox = px - (minX + maxX) / 2; oz = pz + gap - minZ; }
  else if (fz < 0) { ox = px - (minX + maxX) / 2; oz = pz - gap - maxZ; }
  else if (fx > 0) { ox = px + gap - minX; oz = pz - (minZ + maxZ) / 2; }
  else { ox = px - gap - maxX; oz = pz - (minZ + maxZ) / 2; }
  return new int[] { ox, oz };
}""")
M(lg, r"""
public static double[] polyX(double cx) {
  double[] r = new double[POLY_R.length];
  for (int i = 0; i < POLY_R.length; i++) r[i] = cx + POLY_R[i] * Math.cos(2.0 * Math.PI * i / POLY_R.length);
  return r;
}""")
M(lg, r"""
public static double[] polyZ(double cz) {
  double[] r = new double[POLY_R.length];
  for (int i = 0; i < POLY_R.length; i++) r[i] = cz + POLY_R[i] * Math.sin(2.0 * Math.PI * i / POLY_R.length);
  return r;
}""")
# point in polygon (even-odd ray cast on x / z)
M(lg, r"""
public static boolean inPoly(double[] xs, double[] zs, double x, double z) {
  if (xs == null || zs == null || xs.length < 3 || xs.length != zs.length) return false;
  boolean in = false;
  int n = xs.length;
  int j = n - 1;
  for (int i = 0; i < n; i++) {
    if (((zs[i] > z) != (zs[j] > z)) && (x < (xs[j] - xs[i]) * (z - zs[i]) / (zs[j] - zs[i]) + xs[i])) in = !in;
    j = i;
  }
  return in;
}""")
M(lg, r"""
public static String polyText(double[] xs, double[] zs) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < xs.length; i++) {
    if (i > 0) sb.append(" ");
    sb.append("(").append(Math.round(xs[i])).append(", ").append(Math.round(zs[i])).append(")");
  }
  return sb.toString();
}""")
# the lane's sideways offset at step i (S-curve, at most 1 block per step for amplitude 5 over 40 steps)
M(lg, r"""
public static int lat(int i) {
  return (int) Math.round(LANE_AMP * Math.sin(2.0 * Math.PI * i / LANE_LEN));
}""")
# target heights: start at g[0], then follow g but change at most 1 block per step
M(lg, r"""
public static int[] smooth(int[] g) {
  int[] t = new int[g.length];
  if (g.length == 0) return t;
  t[0] = g[0];
  for (int i = 1; i < g.length; i++) {
    int v = g[i];
    if (v > t[i - 1] + 1) v = t[i - 1] + 1;
    if (v < t[i - 1] - 1) v = t[i - 1] - 1;
    t[i] = v;
  }
  return t;
}""")
M(lg, r"""
public static boolean isGround(String key) {
  if (key == null) return false;
  if (key.indexOf("Stairs") >= 0 || key.indexOf("Leaves") >= 0) return false;
  return key.startsWith("Soil_") || key.startsWith("Rock_") || key.startsWith("Sand") || key.startsWith("Gravel") || key.startsWith("Snow") || key.startsWith("Clay");
}""")
M(lg, r"""
public static String ms(long nanos) {
  long t = nanos / 100000L;
  return (t / 10L) + "." + (t % 10L) + " ms";
}""")
M(lg, r"""
public static String xyz(int x, int y, int z) {
  return x + " " + y + " " + z;
}""")
M(lg, r"""
public static String rotName(int r) {
  if (r == 1) return "ROTATION_90";
  if (r == 2) return "ROTATION_180";
  if (r == 3) return "ROTATION_270";
  return "ROTATION_0";
}""")
M(lg, r"""
public static long cells(int minX, int maxX, int minY, int maxY, int minZ, int maxZ) {
  return (long) (maxX - minX + 1) * (long) (maxY - minY + 1) * (long) (maxZ - minZ + 1);
}""")
# the yaw (radians) that faces direction (dx, dz): yaw 0 faces -z (Transform.getDirection(0, 0) = (0, 0, -1), SkyyWorldGen 0.1 note)
M(lg, r"""
public static float yawToward(double dx, double dz) {
  if (dx == 0.0 && dz == 0.0) return 0.0f;
  return (float) Math.atan2(-dx, -dz);
}""")
M(lg, r"""
public static boolean near(double ax, double ay, double az, double bx, double by, double bz, double r) {
  double dx = ax - bx; double dy = ay - by; double dz = az - bz;
  return dx * dx + dy * dy + dz * dz <= r * r;
}""")

# =====================================================================================================================
# TpRec: one undo record (newest last). Saved as undo/<seq>.properties (+ undo/<seq>.lpf = the snapshot when there is one).
# =====================================================================================================================
rec = mk("TpRec")
for f in ("public int seq;", "public String kind;", "public String world;", "public int ox;", "public int oy;", "public int oz;",
          "public String snap;", "public String uuids;", "public String what;", "public long time;", "public Object buf;",
          "public long dropAsk;", "public double nx;", "public double ny;", "public double nz;"):
    F(rec, f)
C(rec, r"""public TpRec() { this.kind = ""; this.world = ""; this.snap = ""; this.uuids = ""; this.what = ""; this.time = 0L; this.dropAsk = 0L; }""")
M(rec, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('\n', ' ').replace('\r', ' ');
}""")
M(rec, r"""
public String toText() {
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyTownProbe undo record - deleted by /townprobe undo\n");
  sb.append("seq=").append(this.seq).append("\n");
  sb.append("kind=").append(clean(this.kind)).append("\n");
  sb.append("world=").append(clean(this.world)).append("\n");
  sb.append("ox=").append(this.ox).append("\noy=").append(this.oy).append("\noz=").append(this.oz).append("\n");
  sb.append("snap=").append(clean(this.snap)).append("\n");
  sb.append("uuids=").append(clean(this.uuids)).append("\n");
  sb.append("nx=").append(this.nx).append("\nny=").append(this.ny).append("\nnz=").append(this.nz).append("\n");
  sb.append("what=").append(clean(this.what)).append("\n");
  sb.append("time=").append(this.time).append("\n");
  return sb.toString();
}""")
M(rec, r"""
public static @PKG@.TpRec parse(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  @PKG@.TpRec r = new @PKG@.TpRec();
  try {
    r.seq = Integer.parseInt(p.getProperty("seq", "").trim());
    r.ox = Integer.parseInt(p.getProperty("ox", "0").trim());
    r.oy = Integer.parseInt(p.getProperty("oy", "0").trim());
    r.oz = Integer.parseInt(p.getProperty("oz", "0").trim());
    r.nx = Double.parseDouble(p.getProperty("nx", "0").trim());
    r.ny = Double.parseDouble(p.getProperty("ny", "0").trim());
    r.nz = Double.parseDouble(p.getProperty("nz", "0").trim());
    r.time = Long.parseLong(p.getProperty("time", "0").trim());
  } catch (Throwable t) { return null; }
  r.kind = p.getProperty("kind", "").trim();
  r.world = p.getProperty("world", "").trim();
  r.snap = p.getProperty("snap", "").trim();
  r.uuids = p.getProperty("uuids", "").trim();
  r.what = p.getProperty("what", "").trim();
  if (r.kind.length() == 0 || r.world.length() == 0 || r.seq <= 0) return null;
  if (r.snap.length() > 0 && !r.snap.equals(r.seq + ".lpf")) return null;
  return r;
}""")
M(rec, r"""
public String[] uuidList() {
  if (this.uuids == null || this.uuids.length() == 0) return new String[0];
  return this.uuids.split(",");
}""")

# =====================================================================================================================
# TpZone: the in-memory probe zone (world, polygon, admins too?)
# =====================================================================================================================
zone = mk("TpZone")
for f in ("public String world;", "public double[] xs;", "public double[] zs;", "public boolean all;", "public double cx;", "public double cz;"):
    F(zone, f)
C(zone, "public TpZone(String w, double cx, double cz, boolean all) { this.world = w; this.cx = cx; this.cz = cz; this.all = all; this.xs = @PKG@.TpLogic.polyX(cx); this.zs = @PKG@.TpLogic.polyZ(cz); }")
M(zone, r"""
public boolean contains(String w, double x, double z) {
  if (w == null || !w.equals(this.world)) return false;
  return @PKG@.TpLogic.inPoly(this.xs, this.zs, x, z);
}""")

# =====================================================================================================================
# TpStore: records (memory + undo/ folder), the probe NPC table, the zone, the busy flag
# =====================================================================================================================
sto = mk("TpStore")
F(sto, "public static java.nio.file.Path DIR;")                                  # <server>/mods/Skyy_SkyyTownProbe
F(sto, "public static final java.util.ArrayList RECS = new java.util.ArrayList();")
F(sto, "public static final java.util.concurrent.ConcurrentHashMap NPCS = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> TpRec
F(sto, "public static final java.util.concurrent.ConcurrentHashMap LIVE = new java.util.concurrent.ConcurrentHashMap();")  # seq -> TRUE while the record exists (snapshot writes check it)
F(sto, "public static volatile @PKG@.TpZone ZONE;")
F(sto, "public static int SEQ = 0;")
F(sto, "public static volatile boolean BUSY = false;")
F(sto, "public static volatile long BUSY_SINCE = 0L;")
F(sto, "public static volatile int TICKET = 0;")      # the current region job; a job whose ticket is not current is dropped (TpPaste.step)
M(sto, r"""
public static java.nio.file.Path undoDir() {
  return DIR == null ? null : DIR.resolve("undo");
}""")
M(sto, r"""
public static boolean busy() {
  if (BUSY && System.currentTimeMillis() - BUSY_SINCE > 60000L) { TICKET = TICKET + 1; @PKG@.TpLog.warn("a probe job never finished (60 s) - busy flag cleared, that job is dropped if it ever arrives"); BUSY = false; }
  return BUSY;
}""")
M(sto, r"""
public static void setBusy(boolean b) {
  BUSY = b;
  BUSY_SINCE = b ? System.currentTimeMillis() : 0L;
}""")
# a new region job: busy + a fresh ticket
M(sto, r"""
public static int begin() {
  TICKET = TICKET + 1;
  setBusy(true);
  return TICKET;
}""")
M(sto, r"""
public static int nextSeq() {
  SEQ = SEQ + 1;
  return SEQ;
}""")
M(sto, r"""
public static @PKG@.TpRec last() {
  if (RECS.isEmpty()) return null;
  return (@PKG@.TpRec) RECS.get(RECS.size() - 1);
}""")
M(sto, r"""
public static boolean isEntityKind(String k) {
  return "npc".equals(k) || "pebble".equals(k) || "sign".equals(k);
}""")
M(sto, r"""
public static void indexNpcs(@PKG@.TpRec r) {
  if (r == null || !isEntityKind(r.kind)) return;
  String[] us = r.uuidList();
  for (int i = 0; i < us.length; i++) if (us[i].length() > 0) NPCS.put(us[i], r);
}""")
# the first record of this kind in this world (npc: one Mossby at a time)
M(sto, r"""
public static @PKG@.TpRec find(String kind, String world) {
  for (int i = 0; i < RECS.size(); i++) {
    @PKG@.TpRec r = (@PKG@.TpRec) RECS.get(i);
    if (r.kind.equals(kind) && r.world.equals(world)) return r;
  }
  return null;
}""")
M(sto, r"""
public static boolean writeText(java.nio.file.Path p, String text) {
  try {
    java.nio.file.Files.createDirectories(p.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = p.resolveSibling(p.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, p, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    return true;
  } catch (Throwable t) { @PKG@.TpLog.warn("could not write " + p + ": " + t); return false; }
}""")
M(sto, r"""
public static boolean saveRec(@PKG@.TpRec r) {
  java.nio.file.Path d = undoDir();
  if (d == null) { @PKG@.TpLog.warn("no data folder - undo record " + r.seq + " kept in memory only"); return false; }
  return writeText(d.resolve(r.seq + ".properties"), r.toText());
}""")
# write = false: memory only for now (a paste record: its .properties is written by TpIoDone once the .lpf snapshot is on disk)
M(sto, r"""
public static boolean add(@PKG@.TpRec r, boolean write) {
  RECS.add(r);
  LIVE.put(String.valueOf(r.seq), Boolean.TRUE);
  indexNpcs(r);
  if (!write) return true;
  return saveRec(r);
}""")
M(sto, r"""
public static boolean add(@PKG@.TpRec r) {
  return add(r, true);
}""")
M(sto, r"""
public static void deleteQuiet(java.nio.file.Path p) {
  try { if (p != null) java.nio.file.Files.deleteIfExists(p); } catch (Throwable t) { @PKG@.TpLog.warn("could not delete " + p + ": " + t); }
}""")
M(sto, r"""
public static boolean isEmptyDir(java.nio.file.Path d) {
  if (d == null || !java.nio.file.Files.isDirectory(d, new java.nio.file.LinkOption[0])) return false;
  java.util.stream.Stream s = null;
  try {
    s = java.nio.file.Files.list(d);
    boolean e = !s.iterator().hasNext();
    s.close();
    return e;
  } catch (Throwable t) { try { if (s != null) s.close(); } catch (Throwable t2) { } return false; }
}""")
M(sto, r"""
public static void cleanDirs() {
  java.nio.file.Path d = undoDir();
  if (d != null && isEmptyDir(d)) deleteQuiet(d);
  if (DIR != null && isEmptyDir(DIR)) deleteQuiet(DIR);
}""")
# drop a record: memory, NPC index, its files; empty folders go too (no saved data left once everything is undone)
M(sto, r"""
public static void remove(@PKG@.TpRec r) {
  RECS.remove(r);
  LIVE.remove(String.valueOf(r.seq));
  String[] us = r.uuidList();
  for (int i = 0; i < us.length; i++) NPCS.remove(us[i]);
  java.nio.file.Path d = undoDir();
  if (d == null) return;
  deleteQuiet(d.resolve(r.seq + ".properties"));
  if (r.snap.length() > 0) deleteQuiet(d.resolve(r.snap));
  if (RECS.isEmpty()) cleanDirs();
}""")
M(sto, r"""
public static java.nio.file.Path snapPath(@PKG@.TpRec r) {
  java.nio.file.Path d = undoDir();
  return d == null || r.snap.length() == 0 ? null : d.resolve(r.snap);
}""")
# start: read undo/*.properties (oldest first), index probe NPCs. Writes nothing; deletes only broken / orphan undo files of its own
# (a record that lost its snapshot, an unreadable record, a snapshot or .tmp with no record) so removing the pin leaves no files.
M(sto, r"""
public static int load() {
  RECS.clear();
  NPCS.clear();
  LIVE.clear();
  ZONE = null;
  SEQ = 0;
  setBusy(false);
  java.nio.file.Path d = undoDir();
  if (d == null || !java.nio.file.Files.isDirectory(d, new java.nio.file.LinkOption[0])) return 0;
  java.util.ArrayList found = new java.util.ArrayList();
  java.util.ArrayList junk = new java.util.ArrayList();
  java.util.HashSet keep = new java.util.HashSet();
  java.util.stream.Stream s = null;
  try {
    s = java.nio.file.Files.list(d);
    java.util.Iterator it = s.iterator();
    while (it.hasNext()) {
      java.nio.file.Path p = (java.nio.file.Path) it.next();
      String n = p.getFileName().toString();
      if (!n.endsWith(".properties")) continue;
      String text = new String(java.nio.file.Files.readAllBytes(p), "UTF-8");
      @PKG@.TpRec r = @PKG@.TpRec.parse(text);
      if (r == null || !n.equals(r.seq + ".properties")) { @PKG@.TpLog.warn("ignored unreadable undo record " + n + " - deleted"); junk.add(p); continue; }
      if (r.snap.length() > 0 && !java.nio.file.Files.exists(d.resolve(r.snap), new java.nio.file.LinkOption[0])) { @PKG@.TpLog.warn("undo record " + n + " lost its snapshot " + r.snap + " - ignored and deleted"); junk.add(p); continue; }
      found.add(r);
      if (r.snap.length() > 0) keep.add(r.snap);
    }
    s.close();
    s = java.nio.file.Files.list(d);
    it = s.iterator();
    while (it.hasNext()) {
      java.nio.file.Path p = (java.nio.file.Path) it.next();
      String n = p.getFileName().toString();
      if (n.endsWith(".properties") || keep.contains(n)) continue;
      if (n.endsWith(".lpf") || n.endsWith(".tmp")) { @PKG@.TpLog.warn("orphan undo file " + n + " (no record) - deleted"); junk.add(p); }
    }
    s.close();
  } catch (Throwable t) { try { if (s != null) s.close(); } catch (Throwable t2) { } @PKG@.TpLog.warn("reading " + d + " failed: " + t); }
  for (int i = 0; i < junk.size(); i++) deleteQuiet((java.nio.file.Path) junk.get(i));
  while (!found.isEmpty()) {
    int bi = 0;
    for (int i = 1; i < found.size(); i++) if (((@PKG@.TpRec) found.get(i)).seq < ((@PKG@.TpRec) found.get(bi)).seq) bi = i;
    @PKG@.TpRec r = (@PKG@.TpRec) found.remove(bi);
    RECS.add(r);
    LIVE.put(String.valueOf(r.seq), Boolean.TRUE);
    indexNpcs(r);
    if (r.seq > SEQ) SEQ = r.seq;
  }
  if (RECS.isEmpty() && !junk.isEmpty()) cleanDirs();
  return RECS.size();
}""")

# =====================================================================================================================
# TpEngApi (interface) + TpEng: the engine seam (see the header). API == null in game = the real calls.
# =====================================================================================================================
api = pool.makeInterface(PKG + ".TpEngApi")
# javassist: abstract interface methods via CtNewMethod.make on an interface take a body-less declaration
for sig in ("public abstract Object findPrefab(String key);",
            "public abstract Object buffer(Object path);",
            "public abstract @CF@ loadRegion(@IPB@ b, @WLD@ w, @V3I@ o, @PROT@ r);",
            "public abstract void paste(@IPB@ b, @WLD@ w, @V3I@ o, @ROT@ rot, int flags, @PREG@ reg, @ST@ st, java.util.function.Consumer ents);",
            "public abstract int height(@WLD@ w, int x, int z);",
            "public abstract String key(@WLD@ w, int x, int y, int z);",
            "public abstract @ST@ store(@WLD@ w);",
            "public abstract @REF@ refOf(@WLD@ w, java.util.UUID u);",
            "public abstract int roleIndex(String role);",
            "public abstract @PAIR@ spawnNpc(@ST@ st, String role, @V3D@ pos, @R3F@ rot);",
            "public abstract @PAIR@ spawnModel(@ST@ st, int role, @V3D@ pos, @R3F@ rot, @MDL@ m);",
            "public abstract @HOL@ newHolder();"):
    M(api, sig)

eng = mk("TpEng")
F(eng, "public static @PKG@.TpEngApi API;")
F(eng, "public static final int NO_HEIGHT = -1000000;")
M(eng, r"""
public static @PATH@ findPrefab(String key) {
  if (API != null) return (@PATH@) API.findPrefab(key);
  return @PS@.get().findAssetPrefabPath(key);
}""")
M(eng, r"""
public static @IPB@ buffer(@PATH@ p) {
  if (API != null) return (@IPB@) API.buffer(p);
  return @PBU@.getCached(p);
}""")
# vanilla PrefabRemoveAction passes 4 as the last argument (PrefabPasteAction uses loadPasteRegionIfInMemory)
M(eng, r"""
public static @CF@ loadRegion(@IPB@ b, @WLD@ w, @V3I@ o, @PROT@ r) {
  if (API != null) return API.loadRegion(b, w, o, r);
  return @PU@.loadPasteRegionAsync(b, w, (@V3IC@) o, r, 4);
}""")
# the vanilla PrefabPasteAction / PrefabRemoveAction$RemoveOp call shape: paste(buffer, world, origin, Rotation, Random, flags, 0, region,
# NOOP block-entity consumer, the entity consumer, the entity store). 'ents' (TpEntGrab, or null = NOOP) sees every prefab entity's Holder
# right before PrefabUtil adds it (PrefabUtil.lambda$paste$1: Consumer.accept(holder) then ComponentAccessor.addEntity(holder, LOAD)).
M(eng, r"""
public static void paste(@IPB@ b, @WLD@ w, @V3I@ o, @ROT@ rot, int flags, @PREG@ reg, @ST@ st, java.util.function.Consumer ents) {
  if (API != null) { API.paste(b, w, o, rot, flags, reg, st, ents); return; }
  @PU@.paste(b, w, o, rot, new @FR@(), flags, 0, reg, @PU@.NOOP_BLOCK_ENTITY_CONSUMER, ents == null ? @PU@.NOOP_ENTITY_CONSUMER : ents, (@CAC@) st);
}""")
M(eng, r"""
public static int height(@WLD@ w, int x, int z) {
  if (API != null) return API.height(w, x, z);
  @WCH@ c = w.getChunkIfLoaded(@CHU@.indexChunkFromBlock(x, z));
  if (c == null) return NO_HEIGHT;
  return c.getHeight(x, z);
}""")
M(eng, r"""
public static String key(@WLD@ w, int x, int y, int z) {
  if (API != null) return API.key(w, x, y, z);
  @WCH@ c = w.getChunkIfLoaded(@CHU@.indexChunkFromBlock(x, z));
  if (c == null) return null;
  int id = c.getBlock(x, y, z);
  @BT@ t = (@BT@) @BT@.getAssetMap().getAsset(id);
  return t == null ? null : t.getId();
}""")
M(eng, r"""
public static @ST@ store(@WLD@ w) {
  if (API != null) return API.store(w);
  return w.getEntityStore().getStore();
}""")
M(eng, r"""
public static @REF@ refOf(@WLD@ w, java.util.UUID u) {
  if (API != null) return API.refOf(w, u);
  return w.getEntityStore().getRefFromUUID(u);
}""")
M(eng, r"""
public static int roleIndex(String role) {
  if (API != null) return API.roleIndex(role);
  return @NPCP@.get().getIndex(role);
}""")
M(eng, r"""
public static @PAIR@ spawnNpc(@ST@ st, String role, @V3D@ pos, @R3F@ rot) {
  if (API != null) return API.spawnNpc(st, role, pos, rot);
  return @NPCP@.get().spawnNPC(st, role, (String) null, pos, rot);
}""")
M(eng, r"""
public static @HOL@ newHolder() {
  if (API != null) return API.newHolder();
  return @EST@.REGISTRY.newHolder();
}""")
M(eng, r"""
public static @PAIR@ spawnModel(@ST@ st, int role, @V3D@ pos, @R3F@ rot, @MDL@ m) {
  if (API != null) return API.spawnModel(st, role, pos, rot, m);
  return @NPCP@.get().spawnEntity(st, role, pos, rot, m, null);
}""")

# =====================================================================================================================
# TpSnap: the snapshot (vanilla PrefabSnapshotUtil.createSnapshot's loop, without its write into the world's snapshots dir)
# + the block counter used after a paste. World thread, region fully loaded.
# =====================================================================================================================
snp = mk("TpSnap")
M(snp, r"""
public static @PBF@ create(@PREG@ region, @IPB@ buf, @V3I@ o, @PROT@ rot) {
  int minY = o.y + buf.getMinY();
  int maxY = o.y + buf.getMaxY();
  int h = 1 + maxY - minY;
  int minX = o.x + buf.getMinX(rot);
  int minZ = o.z + buf.getMinZ(rot);
  int maxX = o.x + buf.getMaxX(rot);
  int maxZ = o.z + buf.getMaxZ(rot);
  @PBB@ b = @PBF@.newBuilder();
  @BTAM@ map = @BT@.getAssetMap();
  for (int z = minZ; z <= maxZ; z++) {
    for (int x = minX; x <= maxX; x++) {
      @PBE@[] col = new @PBE@[h];
      int k = 0;
      for (int y = minY; y <= maxY; y++) {
        @PSEC@ s = region.getSectionAtBlock(x, y, z);
        int idx = @CHU@.indexBlock(x, y, z);
        int id = s.getBlock(idx);
        @BT@ t = (@BT@) map.getAsset(id);
        if (t == null) col[k] = new @PBE@(y - o.y, 0, "Empty");
        else col[k] = new @PBE@(y - o.y, id, t.getId(), 1.0f, s.getState(idx), s.getFluid(idx), s.getFluidLevel(idx), s.getSupport(idx), s.getRotation(idx), s.getFiller(idx));
        k++;
      }
      b.addColumn(x - o.x, z - o.z, col, null);
    }
  }
  return b.build();
}""")
# block id 'id' in the box [x0..x1] x [y0..y1] x [z0..z1]: the count + the first 8 positions (after a paste: Prefab_Spawner_Block)
M(snp, r"""
public static String count(@PREG@ region, int id, int x0, int y0, int z0, int x1, int y1, int z1) {
  if (id < 0) return "0 (id not loaded)";
  int n = 0;
  StringBuilder at = new StringBuilder();
  for (int z = z0; z <= z1; z++) for (int x = x0; x <= x1; x++) for (int y = y0; y <= y1; y++) {
    @PSEC@ s = region.getSectionAtBlock(x, y, z);
    if (s.getBlock(@CHU@.indexBlock(x, y, z)) != id) continue;
    n++;
    if (n <= 8) at.append(n == 1 ? " at " : ", ").append(@PKG@.TpLogic.xyz(x, y, z));
  }
  return n + at.toString();
}""")

# TpEntCount: IPrefabBuffer.forEachEntity consumer - counts the prefab's own entities (spawn markers) so the log can say what was skipped
ec = mk("TpEntCount")
ec.addInterface(pool.get(T["ENC"]))
F(ec, "public int n;")
C(ec, "public TpEntCount() { this.n = 0; }")
M(ec, r"""
public void accept(int x, int z, @HOL@[] ents, Object o) {
  if (ents != null) this.n = this.n + ents.length;
}""")

# TpEntGrab: the paste's entity consumer when entities are ON - gives each prefab entity a UUID (vanilla NPCPlugin.spawnEntity does the
# same ensureComponent) and remembers it, so undo removes what the paste spawned
grab = mk("TpEntGrab")
grab.addInterface(pool.get("java.util.function.Consumer"))
F(grab, "public StringBuilder ids;")
F(grab, "public int n;")
C(grab, "public TpEntGrab() { this.ids = new StringBuilder(); this.n = 0; }")
M(grab, r"""
public void accept(Object o) {
  try {
    if (!(o instanceof @HOL@)) return;
    @HOL@ h = (@HOL@) o;
    h.ensureComponent(@UUC@.getComponentType());
    @UUC@ u = (@UUC@) h.getComponent(@UUC@.getComponentType());
    if (u == null || u.getUuid() == null) return;
    if (this.ids.length() > 0) this.ids.append(",");
    this.ids.append(u.getUuid().toString());
    this.n = this.n + 1;
  } catch (Throwable t) { @PKG@.TpLog.warn("prefab entity not tracked: " + t); }
}""")

# =====================================================================================================================
# TpBuild: our own small buffers (lane, sign) - built with the vanilla PrefabBuffer builder, pasted like a prefab (snapshot + undo)
# =====================================================================================================================
bld = mk("TpBuild")
F(bld, "public static final String TOP = %s;" % json.dumps(LANE_TOP))
F(bld, "public static final String STAIR = %s;" % json.dumps(LANE_STAIR))
F(bld, "public static final String FILL = %s;" % json.dumps(LANE_FILL))
F(bld, "public static final String SIGN = %s;" % json.dumps(SIGN))
M(bld, r"""
public static int idOf(String key) {
  try { return @BT@.getAssetMap().getIndex(key); } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
# the Rotation whose yaw turns north (0, 0, -1) into (fx, fz) - engine maths (Rotation.rotateYaw); null = none matches
M(bld, r"""
public static @ROT@ yawFor(int fx, int fz) {
  @ROT@[] all = @ROT@.values();
  for (int i = 0; i < all.length; i++) {
    @V3I@ out = all[i].rotateYaw(new @V3I@(0, 0, -1), new @V3I@());
    if (out.x == fx && out.z == fz) return all[i];
  }
  return null;
}""")
M(bld, r"""
public static int rotIndex(@ROT@ yaw) {
  if (yaw == null) return 0;
  return @RTUP@.index(yaw, @ROT@.None, @ROT@.None);
}""")
M(bld, r"""
public static @PBE@ entry(int y, String key, int rot) {
  int id = idOf(key);
  if (id == Integer.MIN_VALUE || id < 0) throw new IllegalStateException("block " + key + " is not loaded");
  if (rot == 0) return new @PBE@(y, id, key);
  return new @PBE@(y, id, key, 1.0f, null, 0, (byte) 0, (byte) 0, rot, 0);
}""")
# one column (ascending y): fill FILL from gy+1 .. top-1 (raised), TOP at 'top' (or a stair at top+1 when 'stair' >= 0), air above up to
# max(gy, top) + 3. Coordinates relative to oy.
M(bld, r"""
public static @PBE@[] laneColumn(int oy, int gy, int top, int stairRot, boolean stair) {
  int hi = Math.max(gy, top) + 3;
  int lo = Math.min(gy + 1, top);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int y = lo; y <= hi; y++) {
    if (y < top) l.add(entry(y - oy, FILL, 0));
    else if (y == top) l.add(entry(y - oy, TOP, 0));
    else if (y == top + 1 && stair) l.add(entry(y - oy, STAIR, stairRot));
    else l.add(entry(y - oy, "Empty", 0));
  }
  @PBE@[] a = new @PBE@[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = (@PBE@) l.get(i);
  return a;
}""")

# =====================================================================================================================
# TpJob + TpStep (BiFunction for CompletableFuture.handleAsync on the world executor) + TpPaste: load region -> snapshot -> paste
# (or, for undo: load region -> paste the snapshot back with FORCE -> remove entities -> delete files)
# =====================================================================================================================
job = mk("TpJob")
for f in ("public @PR@ pr;", "public @WLD@ w;", "public @IPB@ buf;", "public @V3I@ o;", "public @PROT@ prot;", "public int flags;",
          "public String kind;", "public String what;", "public long t0;", "public long tLoad;", "public boolean undo;",
          "public @PKG@.TpRec rec;", "public String note;", "public int ents;", "public int children;", "public double hx;",
          "public double hy;", "public double hz;", "public String report;", "public int ticket;"):
    F(job, f)
C(job, r"""public TpJob() { this.note = ""; this.report = ""; this.flags = 0; this.ents = -1; this.children = 0; }""")

stp = mk("TpStep")
stp.addInterface(pool.get("java.util.function.BiFunction"))
F(stp, "public @PKG@.TpJob job;")
F(stp, "public int phase;")      # 0 = the paste region arrived; 1 = the snapshot file was read (undo after a restart)
C(stp, "public TpStep(@PKG@.TpJob j, int phase) { this.job = j; this.phase = phase; }")

iod = mk("TpIoDone")
iod.addInterface(pool.get("java.util.function.BiFunction"))
F(iod, "public java.nio.file.Path path;")
F(iod, "public @PKG@.TpRec rec;")
C(iod, "public TpIoDone(java.nio.file.Path p, @PKG@.TpRec r) { this.path = p; this.rec = r; }")
M(iod, r"""
public void dropFiles() {
  @PKG@.TpStore.deleteQuiet(this.path);
  java.nio.file.Path d = @PKG@.TpStore.undoDir();
  if (d != null && this.rec != null) @PKG@.TpStore.deleteQuiet(d.resolve(this.rec.seq + ".properties"));
  if (@PKG@.TpStore.LIVE.isEmpty()) @PKG@.TpStore.cleanDirs();
}""")
# the .lpf is on disk -> NOW the record's .properties is written (a crash in between leaves only an orphan .lpf, which load() deletes).
# A write that finishes after its record was undone deletes its files again (no orphan, folders cleaned).
M(iod, r"""
public Object apply(Object v, Object err) {
  String k = this.rec == null ? "" : String.valueOf(this.rec.seq);
  if (err != null) {
    @PKG@.TpLog.warn("snapshot file " + this.path + " NOT written: " + err + " (undo still works until a restart; no record file written)");
    @PKG@.TpStore.deleteQuiet(this.path);
    return null;
  }
  if (!@PKG@.TpStore.LIVE.containsKey(k)) { dropFiles(); return null; }
  @PKG@.TpStore.saveRec(this.rec);
  if (!@PKG@.TpStore.LIVE.containsKey(k)) dropFiles();
  return null;
}""")


# =====================================================================================================================
# TpNpc: the probe NPCs (Mossby, Pebble), the sign's nameplate prop, finding / counting / removing them
# =====================================================================================================================
npc = mk("TpNpc")
F(npc, "public static final String ROLE = %s;" % json.dumps(ROLE))
F(npc, "public static final String ROCK = %s;" % json.dumps(ROCK))
F(npc, "public static final float ROCK_SCALE = %sf;" % ROCK_SCALE)
F(npc, "public static final float HOLO_SCALE = %sf;" % HOLO_SCALE)
F(npc, "public static final String HINT = %s;" % json.dumps(HINT))
F(npc, "public static final String USE_ROOT = %s;" % json.dumps(USE_ROOT))
F(npc, "public static final String NPC_NAME = %s;" % json.dumps(NPC_NAME))
F(npc, "public static final String PEBBLE_NAME = %s;" % json.dumps(PEBBLE_NAME))
F(npc, "public static final String HOLO_TEXT = %s;" % json.dumps(HOLO_TEXT))
M(npc, r"""
public static @MDL@ model(String id, float scale) {
  try {
    @MDA@ a = (@MDA@) @MDA@.getAssetMap().getAsset(id);
    return a == null ? null : @MDL@.createStaticScaledModel(a, scale);
  } catch (Throwable t) { @PKG@.TpLog.warn("model " + id + " failed: " + t); return null; }
}""")
M(npc, r"""
public static java.util.UUID uuidOf(@ST@ st, @REF@ r) {
  try {
    @UUC@ u = (@UUC@) st.getComponent(r, @UUC@.getComponentType());
    return u == null ? null : u.getUuid();
  } catch (Throwable t) { return null; }
}""")
M(npc, r"""
public static String modelId(@ST@ st, @REF@ r) {
  try {
    @MC@ m = (@MC@) st.getComponent(r, @MC@.getComponentType());
    if (m == null || m.getModel() == null) return "none";
    return m.getModel().getModelAssetId() + " x" + m.getModel().getScale();
  } catch (Throwable t) { return "? (" + t + ")"; }
}""")
M(npc, r"""
public static void name(@ST@ st, @REF@ r, String n) {
  @MSG@ m = @MSG@.raw(n);
  st.putComponent(r, @DNC@.getComponentType(), new @DNC@(m));
  st.putComponent(r, @PDN@.getComponentType(), new @PDN@(m));
  st.putComponent(r, @NPL@.getComponentType(), new @NPL@(n));
}""")
# F on the NPC: the client needs Interactable (vanilla EntityMakeInteractableCommand / StateSupport.setInteractable) + a Use root
# (RoleBuilderSystem gives every NPC *UseNPC; our UseEntityEvent$Pre system cancels it and opens the page instead)
M(npc, r"""
public static String makeUsable(@ST@ st, @REF@ r) {
  st.ensureComponent(r, @ITB@.getComponentType());
  @ITS@ its = (@ITS@) st.getComponent(r, @ITS@.getComponentType());
  if (its == null) { its = new @ITS@(); st.putComponent(r, @ITS@.getComponentType(), its); }
  if (its.getInteractionId(@ITY@.Use) == null) its.setInteractionId(@ITY@.Use, USE_ROOT);
  its.setInteractionHint(HINT);
  return "Use = " + its.getInteractionId(@ITY@.Use) + ", hint " + HINT + ", Interactable on";
}""")
M(npc, r"""
public static @R3F@ facing(double fromX, double fromZ, double toX, double toZ) {
  @R3F@ r = new @R3F@();
  r.setYaw(@PKG@.TpLogic.yawToward(toX - fromX, toZ - fromZ));
  return r;
}""")
# how many NPCs with our role stand within 3 blocks of (x, y, z) - the "once, not twice after a restart" count
M(npc, r"""
public static int countNear(@ST@ st, double x, double y, double z) {
  int n = 0;
  try {
    java.util.List l = com.hypixel.hytale.server.core.util.TargetUtil.getAllEntitiesInSphere(new @V3D@(x, y, z), 3.0, (@CAC@) st);
    for (int i = 0; l != null && i < l.size(); i++) {
      @REF@ r = (@REF@) l.get(i);
      if (r == null || !r.isValid()) continue;
      Object e = st.getComponent(r, @NPC@.getComponentType());
      if (e instanceof @NPC@ && ROLE.equals(((@NPC@) e).getRoleName())) n++;
    }
  } catch (Throwable t) { @PKG@.TpLog.warn("count near failed: " + t); return -1; }
  return n;
}""")
M(npc, r"""
public static @REF@ find(@WLD@ w, String uuid) {
  try {
    @REF@ r = @PKG@.TpEng.refOf(w, java.util.UUID.fromString(uuid));
    return r != null && r.isValid() ? r : null;
  } catch (Throwable t) { return null; }
}""")
# remove every entity of a record; answers a log text ("" = none). Missing ones are named (not loaded / already gone).
M(npc, r"""
public static String removeAll(@WLD@ w, @ST@ st, @PKG@.TpRec r) {
  String[] us = r.uuidList();
  if (us.length == 0) return "";
  int gone = 0;
  StringBuilder miss = new StringBuilder();
  for (int i = 0; i < us.length; i++) {
    @REF@ e = find(w, us[i]);
    if (e == null) { miss.append(miss.length() == 0 ? "" : ", ").append(us[i]); continue; }
    try { st.removeEntity(e, @RR@.REMOVE); gone++; } catch (Throwable t) { miss.append(miss.length() == 0 ? "" : ", ").append(us[i] + " (" + t + ")"); }
  }
  return "entities removed " + gone + "/" + us.length + (miss.length() > 0 ? " - not found: " + miss : "");
}""")
# the sign's fallback text: a tiny mossy pebble prop on the sign with a Nameplate (vanilla prefab-marker component set)
M(npc, r"""
public static String holo(@PKG@.TpJob j, @ST@ st, @PKG@.TpRec r) {
  try {
    @MDL@ m = model(ROCK, HOLO_SCALE);
    @HOL@ h = @PKG@.TpEng.newHolder();
    @V3D@ pos = new @V3D@(j.hx, j.hy, j.hz);
    h.addComponent(@TC@.getComponentType(), new @TC@(pos, new @R3F@()));
    h.ensureComponent(@UUC@.getComponentType());
    h.addComponent(@NPL@.getComponentType(), new @NPL@(HOLO_TEXT));
    h.addComponent(@INT@.getComponentType(), @INT@.INSTANCE);
    h.addComponent(@PROP@.getComponentType(), @PROP@.get());
    if (m != null) {
      h.addComponent(@MC@.getComponentType(), new @MC@(m));
      h.addComponent(@PM@.getComponentType(), new @PM@(m.toReference()));
    }
    @REF@ e = st.addEntity(h, @ADR@.SPAWN);
    java.util.UUID u = ((@UUC@) h.getComponent(@UUC@.getComponentType())).getUuid();
    if (e != null && e.isValid()) { java.util.UUID u2 = uuidOf(st, e); if (u2 != null) u = u2; }
    r.uuids = u.toString();
    r.nx = j.hx; r.ny = j.hy; r.nz = j.hz;
    return "sign text: NOT supported by this server (no text state on " + @PKG@.TpBuild.SIGN + "); fallback nameplate prop '" + HOLO_TEXT + "' spawned at " + j.hx + " " + j.hy + " " + j.hz + " (entity " + u + ", model " + (m == null ? "none" : ROCK + " x" + HOLO_SCALE) + ")";
  } catch (Throwable t) { return "sign nameplate prop FAILED: " + t; }
}""")

pst = mk("TpPaste")
F(pst, "public static final int FORCE = 1;")
F(pst, "public static final int NO_ENTITIES = 8;")
F(pst, "public static final String OK = \"@COLOK@\";")
F(pst, "public static final String ERR = \"@COLERR@\";")
M(pst, r"""
public static void fail(@PKG@.TpJob j, String why) {
  @PKG@.TpStore.setBusy(false);
  @PKG@.TpLog.warn((j.undo ? "UNDO " : j.kind.toUpperCase(java.util.Locale.ROOT) + " ") + "failed: " + why);
  @PKG@.TpLog.tell(j.pr, (j.undo ? "Undo" : "The " + j.kind) + " failed: " + why, ERR);
}""")
# phase 0 (world thread): kick off the region load
M(pst, r"""
public static void start(@PKG@.TpJob j) {
  j.ticket = @PKG@.TpStore.begin();
  try {
    @CF@ f = @PKG@.TpEng.loadRegion(j.buf, j.w, j.o, j.prot);
    if (f == null) { fail(j, "no paste region"); return; }
    f.orTimeout(30L, java.util.concurrent.TimeUnit.SECONDS).handleAsync(new @PKG@.TpStep(j, 0), j.w);
  } catch (Throwable t) { fail(j, "could not load the area: " + t); }
}""")
M(pst, r"""
public static int[] box(@IPB@ b, @V3I@ o, @PROT@ r) {
  return new int[] { o.x + b.getMinX(r), o.y + b.getMinY(), o.z + b.getMinZ(r), o.x + b.getMaxX(r), o.y + b.getMaxY(), o.z + b.getMaxZ(r) };
}""")
M(pst, r"""
public static String boxText(int[] bx) {
  return "x " + bx[0] + ".." + bx[3] + ", y " + bx[1] + ".." + bx[4] + ", z " + bx[2] + ".." + bx[5] + " (" + (bx[3] - bx[0] + 1) + " x " + (bx[4] - bx[1] + 1) + " x " + (bx[5] - bx[2] + 1) + ")";
}""")
M(pst, r"""
public static void writeSnap(@PBF@ snap, @PATH@ p, @PKG@.TpRec r) {
  if (p == null) { @PKG@.TpStore.saveRec(r); return; }
  try {
    java.nio.file.Files.createDirectories(p.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    @PBU@.writeToFileAsync(snap, p).handle(new @PKG@.TpIoDone(p, r));
  } catch (Throwable t) { @PKG@.TpLog.warn("snapshot write " + p + " failed: " + t + " (undo still works until a restart)"); }
}""")
# the paste itself (region loaded, world thread). The undo record (with the snapshot in memory) is registered BEFORE the paste, so a
# paste that throws partway still leaves something /townprobe undo can put back; the snapshot file + record file are written after.
M(pst, r"""
public static void doPaste(@PKG@.TpJob j, @PREG@ region) {
  @ST@ st = @PKG@.TpEng.store(j.w);
  long t1 = System.nanoTime();
  @PBF@ snap = @PKG@.TpSnap.create(region, j.buf, j.o, j.prot);
  long t2 = System.nanoTime();
  @PKG@.TpRec r = new @PKG@.TpRec();
  r.seq = @PKG@.TpStore.nextSeq();
  r.kind = j.kind;
  r.world = j.w.getName();
  r.ox = j.o.x; r.oy = j.o.y; r.oz = j.o.z;
  r.snap = r.seq + ".lpf";
  r.what = j.what;
  r.time = System.currentTimeMillis();
  r.buf = snap;
  @PKG@.TpStore.add(r, false);
  boolean grabbing = (j.flags & NO_ENTITIES) == 0 && ("temple".equals(j.kind) || "piece".equals(j.kind));
  @PKG@.TpEntGrab grab = grabbing ? new @PKG@.TpEntGrab() : null;
  String err = null;
  try { @PKG@.TpEng.paste(j.buf, j.w, j.o, j.prot.getRotation(), j.flags, region, st, grab); } catch (Throwable t) { err = t.toString(); }
  long t3 = System.nanoTime();
  if (grab != null) r.uuids = grab.ids.toString();
  int[] bx = box(j.buf, j.o, j.prot);
  String spawners = "";
  String extra = "";
  if (err == null) {
    try { if ("temple".equals(j.kind) || "piece".equals(j.kind)) spawners = @PKG@.TpSnap.count(region, @PKG@.TpBuild.idOf("Prefab_Spawner_Block"), bx[0], bx[1], bx[2], bx[3], bx[4], bx[5]); } catch (Throwable t) { spawners = "count failed: " + t; }
    if ("sign".equals(j.kind)) extra = @PKG@.TpNpc.holo(j, st, r);
  }
  @PKG@.TpStore.indexNpcs(r);
  writeSnap(snap, @PKG@.TpStore.snapPath(r), r);
  @PKG@.TpStore.setBusy(false);
  String head = j.kind.toUpperCase(java.util.Locale.ROOT) + (err == null ? " done (" : " FAILED PARTWAY (") + j.what + "): ";
  if (err != null) {
    @PKG@.TpLog.warn(head + "the paste threw after " + @PKG@.TpLogic.ms(t3 - t2) + ": " + err + " - the ground snapshot was taken first, undo record " + r.seq + " kept (world box " + boxText(bx) + ")" + (grab != null ? "; prefab entities spawned before the error: " + grab.n : ""));
    @PKG@.TpLog.tell(j.pr, "The " + j.kind + " failed partway: " + err + ". The ground was saved first - /townprobe undo puts it back.", ERR);
    return;
  }
  @PKG@.TpLog.info(head + "region load " + @PKG@.TpLogic.ms(t1 - j.t0) + ", snapshot " + @PKG@.TpLogic.ms(t2 - t1) + ", paste " + @PKG@.TpLogic.ms(t3 - t2) + ", total " + @PKG@.TpLogic.ms(t3 - j.t0) + " (+ prefab load " + @PKG@.TpLogic.ms(j.tLoad) + ")");
  @PKG@.TpLog.info(head + "world box " + boxText(bx) + ", undo record " + r.seq);
  if (spawners.length() > 0) @PKG@.TpLog.info(head + "Prefab_Spawner_Block in the box after the paste: " + spawners + "; child prefabs in the buffer: " + j.children);
  if (j.ents >= 0) @PKG@.TpLog.info(head + "prefab entities: " + j.ents + ((j.flags & NO_ENTITIES) != 0 ? " SKIPPED (entities off)" : " pasted (entities on); " + (grab == null ? 0 : grab.n) + " spawned and tracked - undo removes them" + (grab != null && grab.n > 0 ? " (" + r.uuids + ")" : "")));
  if (j.report.length() > 0) @PKG@.TpLog.info(head + j.report);
  if (extra.length() > 0) @PKG@.TpLog.info(head + extra);
  @PKG@.TpLog.tell(j.pr, "Done: " + j.what + " in " + @PKG@.TpLogic.ms(t3 - j.t0) + ". /townprobe undo puts the ground back" + (grab != null && grab.n > 0 ? " and removes its " + grab.n + " entities." : "."), OK);
}""")
M(pst, r"""
public static void doUndo(@PKG@.TpJob j, @PREG@ region) {
  @ST@ st = @PKG@.TpEng.store(j.w);
  long t1 = System.nanoTime();
  @PKG@.TpEng.paste(j.buf, j.w, j.o, @ROT@.None, FORCE, region, st, null);
  long t2 = System.nanoTime();
  String gone = @PKG@.TpNpc.removeAll(j.w, st, j.rec);
  @PKG@.TpStore.remove(j.rec);
  @PKG@.TpStore.setBusy(false);
  @PKG@.TpLog.info("UNDO done: " + j.rec.kind + " record " + j.rec.seq + " (" + j.rec.what + ") - snapshot pasted back with FORCE at " + @PKG@.TpLogic.xyz(j.o.x, j.o.y, j.o.z) + " in " + @PKG@.TpLogic.ms(t2 - t1) + " (total " + @PKG@.TpLogic.ms(t2 - j.t0) + ")" + (gone.length() > 0 ? "; " + gone : "") + "; files deleted; " + @PKG@.TpStore.RECS.size() + " records left");
  @PKG@.TpLog.tell(j.pr, "Undone: " + j.rec.what + ". The ground is back as before (" + @PKG@.TpStore.RECS.size() + " more to undo).", OK);
}""")
M(pst, r"""
public static void step(@PKG@.TpJob j, Object value, Throwable err, int phase) {
  if (j.ticket != @PKG@.TpStore.TICKET) {
    @PKG@.TpLog.warn((j.undo ? "UNDO" : j.kind.toUpperCase(java.util.Locale.ROOT)) + " (" + j.what + ") arrived after its busy flag was cleared (job " + j.ticket + ", current " + @PKG@.TpStore.TICKET + ") - dropped, nothing changed");
    return;
  }
  try {
    if (phase == 1) {
      if (err != null || value == null) { fail(j, "the snapshot file could not be read: " + (err == null ? "empty" : err.toString())); return; }
      j.buf = ((@PBF@) value).newAccess();
      j.rec.buf = value;
      start(j);
      return;
    }
    if (err != null) { fail(j, "the area did not load: " + err); return; }
    @PREG@ region = (@PREG@) value;
    if (region == null || !region.isFullyLoaded()) { fail(j, "the area is not fully loaded - stand closer and try again"); return; }
    if (j.undo) doUndo(j, region); else doPaste(j, region);
  } catch (Throwable t) {
    fail(j, t.toString());
  }
}""")
M(stp, r"""
public Object apply(Object value, Object err) {
  @PKG@.TpPaste.step(this.job, value, (Throwable) err, this.phase);
  return null;
}""")
# =====================================================================================================================
# TpTick: once per second per player (world thread) - barks near the probe NPCs, zone enter / leave lines. Memory only.
# =====================================================================================================================
tick = mk("TpTick", T["ETS"])
F(tick, "public static final java.util.concurrent.ConcurrentHashMap ACC = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> double[1]
F(tick, "public static final java.util.concurrent.ConcurrentHashMap BARKED = new java.util.concurrent.ConcurrentHashMap();") # uuid|npc -> Long
F(tick, "public static final java.util.concurrent.ConcurrentHashMap IN = new java.util.concurrent.ConcurrentHashMap();")     # uuid -> Boolean
F(tick, "public static boolean FAILED_ONCE = false;")
F(tick, "public static final double BARK_R = %s;" % BARK_R)
F(tick, "public static final long BARK_MS = %dL;" % BARK_MS)
F(tick, "public static final String BARK_NPC = %s;" % json.dumps(BARK_NPC))
F(tick, "public static final String BARK_PEBBLE = %s;" % json.dumps(BARK_PEBBLE))
C(tick, "public TpTick() { super(); }")
M(tick, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(tick, r"""
public boolean isParallel(int a, int b) {
  return false;
}""")
# barks: every probe NPC record in this world within BARK_R of the player, once per BARK_MS per player (leaving range re-arms it)
M(tick, r"""
public static void barks(@PR@ pr, java.util.UUID u, String world, double x, double y, double z, long now) {
  java.util.Iterator it = @PKG@.TpStore.NPCS.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpRec r = (@PKG@.TpRec) it.next();
    if (!"npc".equals(r.kind) && !"pebble".equals(r.kind)) continue;
    if (!r.world.equals(world)) continue;
    String k = u + "|" + r.seq;
    if (!@PKG@.TpLogic.near(x, y, z, r.nx, r.ny, r.nz, BARK_R)) {
      Long t = (Long) BARKED.get(k);
      if (t != null && now - t.longValue() > 5000L) BARKED.remove(k);
      continue;
    }
    Long t = (Long) BARKED.get(k);
    if (t != null && now - t.longValue() < BARK_MS) continue;
    BARKED.put(k, Long.valueOf(now));
    @PKG@.TpLog.tell(pr, "npc".equals(r.kind) ? BARK_NPC : BARK_PEBBLE, "@COLBRK@");
    @PKG@.TpLog.info("BARK: " + r.kind + " record " + r.seq + " greeted " + pr.getUsername() + " at " + Math.round(Math.sqrt((x - r.nx) * (x - r.nx) + (y - r.ny) * (y - r.ny) + (z - r.nz) * (z - r.nz))) + " blocks");
  }
}""")
M(tick, r"""
public static void zoneLine(@PR@ pr, java.util.UUID u, String world, double x, double z) {
  @PKG@.TpZone zn = @PKG@.TpStore.ZONE;
  boolean in = zn != null && zn.contains(world, x, z);
  Boolean was = (Boolean) IN.get(u);
  if (was == null) { IN.put(u, Boolean.valueOf(in)); if (!in) return; }
  else if (was.booleanValue() == in) return;
  IN.put(u, Boolean.valueOf(in));
  @PKG@.TpLog.tell(pr, in ? "You entered the town probe zone (building refused for " + (zn.all ? "everyone" : "non-admins") + ")." : "You left the town probe zone.", "@COLINF@");
}""")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CB@ cb) {
  try {
    if (@PKG@.TpStore.NPCS.isEmpty() && @PKG@.TpStore.ZONE == null && IN.isEmpty()) return;
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PR@ pr = (@PR@) st.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    double[] acc = (double[]) ACC.get(u);
    if (acc == null) { acc = new double[1]; ACC.put(u, acc); }
    acc[0] = acc[0] + (double) dt;
    if (acc[0] < 1.0) return;
    acc[0] = 0.0;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) return;
    @V3D@ p = tc.getPosition();
    long now = System.currentTimeMillis();
    if (!@PKG@.TpStore.NPCS.isEmpty()) barks(pr, u, w.getName(), p.x, p.y, p.z, now);
    zoneLine(pr, u, w.getName(), p.x, p.z);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("probe tick failed (logged once): " + t); }
  }
}""")

# =====================================================================================================================
# TpCmds: what each /townprobe action does (world thread: AbstractPlayerCommand.execute)
# =====================================================================================================================
cmds = mk("TpCmds")
F(cmds, "public static final String OK = \"@COLOK@\";")
F(cmds, "public static final String ERR = \"@COLERR@\";")
F(cmds, "public static final String INF = \"@COLINF@\";")
F(cmds, "public static final String WORLD = \"@WORLD@\";")
F(cmds, "public static java.util.concurrent.atomic.AtomicLong NPC_SPAWNS = new java.util.concurrent.atomic.AtomicLong();")
M(cmds, r"""
public static void help(@PR@ pr) {
  @PKG@.TpLog.tell(pr, "Town probe (admin only, Zone 1 test island). Every action is logged as [SkyyTownProbe] lines in the server log.", INF);
  @PKG@.TpLog.tell(pr, "/townprobe temple [0-3] - paste the spawn temple in front of you (0 door south, 1 east, 2 north, 3 west; add e for its entities, e.g. 0e - undo removes them too)", null);
  @PKG@.TpLog.tell(pr, "/townprobe undo - put back the newest probe change (the ground as it was, probe NPCs removed; anything built inside the box since is overwritten)", null);
  @PKG@.TpLog.tell(pr, "/townprobe lane - a 40-block cobble lane ahead that follows the ground", null);
  @PKG@.TpLog.tell(pr, "/townprobe piece <prefab path or stall, cottage, softwood, cabin, plains, lighthouse, tower, well, pool, path> [0-3] - any vanilla prefab, entities off", null);
  @PKG@.TpLog.tell(pr, "/townprobe npc - Mossby: press F to open the Bazaar; he greets you within 8 blocks", null);
  @PKG@.TpLog.tell(pr, "/townprobe pebble - a mossy rock as an NPC", null);
  @PKG@.TpLog.tell(pr, "/townprobe zone [all, off] - a no-build zone around you (all = admins too, off = remove)", null);
  @PKG@.TpLog.tell(pr, "/townprobe sign - a village sign + the name fallback (signs have no text)", null);
  @PKG@.TpLog.tell(pr, @PKG@.TpStore.RECS.size() + " probe changes to undo; zone " + (@PKG@.TpStore.ZONE == null ? "off" : "on"), INF);
}""")
M(cmds, r"""
public static boolean worldOk(@PR@ pr, @WLD@ w) {
  if (w != null && WORLD.equals(w.getName())) return true;
  @PKG@.TpLog.tell(pr, "The town probe only builds on the Zone 1 test island (/zone 1). This world (" + (w == null ? "?" : w.getName()) + ") is left alone.", ERR);
  return false;
}""")
M(cmds, r"""
public static boolean canStart(@PR@ pr, @WLD@ w) {
  if (!worldOk(pr, w)) return false;
  if (@PKG@.TpStore.busy()) { @PKG@.TpLog.tell(pr, "Still working on the last probe action - try again in a moment.", ERR); return false; }
  if (@PKG@.TpStore.RECS.size() >= @PKG@.TpLogic.MAX_RECS) { @PKG@.TpLog.tell(pr, "There are already " + @PKG@.TpLogic.MAX_RECS + " probe changes - /townprobe undo some first.", ERR); return false; }
  return true;
}""")
# {feet x, y, z (block), facing x, z, yaw} of the player; null = unreadable
M(cmds, r"""
public static double[] where(@ST@ st, @REF@ ref) {
  try {
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) return null;
    @V3D@ p = tc.getPosition();
    int fx = 0; int fz = 1;
    @HR@ hr = (@HR@) st.getComponent(ref, @HR@.getComponentType());
    if (hr != null) {
      @V3I@ d = hr.getHorizontalAxisDirection();
      if (d != null && (d.x != 0 || d.z != 0)) { fx = d.x; fz = d.z; }
    }
    float yaw = tc.getRotation() == null ? 0.0f : tc.getRotation().yaw();
    return new double[] { Math.floor(p.x), Math.floor(p.y), Math.floor(p.z), (double) fx, (double) fz, (double) yaw, p.x, p.y, p.z };
  } catch (Throwable t) { @PKG@.TpLog.warn("position unreadable: " + t); return null; }
}""")
# the top ground block at (x, z), searching down from the height map; NO_HEIGHT = chunk not loaded
M(cmds, r"""
public static int ground(@WLD@ w, int x, int z) {
  int h = @PKG@.TpEng.height(w, x, z);
  if (h == @PKG@.TpEng.NO_HEIGHT) return h;
  int y = h;
  for (int k = 0; k < 40; k++) {
    if (@PKG@.TpLogic.isGround(@PKG@.TpEng.key(w, x, y, z))) return y;
    y--;
  }
  return h;
}""")
M(cmds, r"""
public static void pastePrefab(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String key, String rotTok, String kind) {
  if (!canStart(pr, w)) return;
  int rot = @PKG@.TpLogic.parseRot(rotTok);
  if (rot < 0) { @PKG@.TpLog.tell(pr, "Rotation must be 0, 1, 2 or 3 (add e for entities, like 1e).", ERR); return; }
  boolean ents = @PKG@.TpLogic.wantsEntities(rotTok);
  if (key == null) { @PKG@.TpLog.tell(pr, "That is not a prefab path (example: Npc/Kweebec/Oak/Shops/Kweebec_Oak_Shops_001, or an alias like stall).", ERR); return; }
  double[] me = where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  long t0 = System.nanoTime();
  @PATH@ path = null;
  try { path = @PKG@.TpEng.findPrefab(key); } catch (Throwable t) { path = null; }
  if (path == null) { @PKG@.TpLog.tell(pr, "No vanilla prefab at Server/Prefabs/" + key, ERR); @PKG@.TpLog.info(kind.toUpperCase(java.util.Locale.ROOT) + " refused: prefab " + key + " not found"); return; }
  @IPB@ b = null;
  try { b = @PKG@.TpEng.buffer(path); } catch (Throwable t) { @PKG@.TpLog.tell(pr, "The prefab could not be loaded: " + t, ERR); return; }
  if (b == null) { @PKG@.TpLog.tell(pr, "The prefab could not be loaded.", ERR); return; }
  long tLoad = System.nanoTime() - t0;
  @PROT@ prot = @PROT@.VALUES[rot];
  long cells = @PKG@.TpLogic.cells(b.getMinX(prot), b.getMaxX(prot), b.getMinY(), b.getMaxY(), b.getMinZ(prot), b.getMaxZ(prot));
  if (cells > @PKG@.TpLogic.MAX_CELLS) {
    @PKG@.TpLog.info(kind.toUpperCase(java.util.Locale.ROOT) + " refused: Server/Prefabs/" + key + " is " + (b.getMaxX(prot) - b.getMinX(prot) + 1) + " x " + (b.getMaxY() - b.getMinY() + 1) + " x " + (b.getMaxZ(prot) - b.getMinZ(prot) + 1) + " = " + cells + " cells, over the probe cap of " + @PKG@.TpLogic.MAX_CELLS);
    @PKG@.TpLog.tell(pr, "That prefab is too big for the probe (" + cells + " blocks in its box, the limit is " + @PKG@.TpLogic.MAX_CELLS + ").", ERR);
    return;
  }
  int px = (int) me[0]; int py = (int) me[1]; int pz = (int) me[2]; int fx = (int) me[3]; int fz = (int) me[4];
  int[] xz = @PKG@.TpLogic.placeOrigin(px, pz, fx, fz, b.getMinX(prot), b.getMaxX(prot), b.getMinZ(prot), b.getMaxZ(prot), 4);
  int gy = ground(w, xz[0], xz[1]);
  boolean guess = gy == @PKG@.TpEng.NO_HEIGHT;
  if (guess) gy = py - 1;
  @PKG@.TpJob j = new @PKG@.TpJob();
  j.pr = pr; j.w = w; j.buf = b; j.prot = prot; j.kind = kind;
  j.o = new @V3I@(xz[0], gy, xz[1]);
  j.flags = @PKG@.TpPaste.FORCE | (ents ? 0 : @PKG@.TpPaste.NO_ENTITIES);
  String name = key.lastIndexOf('/') >= 0 ? key.substring(key.lastIndexOf('/') + 1) : key;
  if (name.endsWith(".prefab.json")) name = name.substring(0, name.length() - 12);
  j.what = name + " " + @PKG@.TpLogic.rotName(rot) + (ents ? " with entities" : "") + " at " + @PKG@.TpLogic.xyz(j.o.x, j.o.y, j.o.z);
  j.t0 = System.nanoTime();
  j.tLoad = tLoad;
  try { @PKG@.TpEntCount c = new @PKG@.TpEntCount(); b.forEachEntity(c, null); j.ents = c.n; } catch (Throwable t) { j.ents = -1; }
  try { Object[] ch = b.getChildPrefabs(); j.children = ch == null ? 0 : ch.length; } catch (Throwable t) { j.children = -1; }
  @V3I@ door = new @V3I@(0, 0, 1);
  prot.rotate(door);
  @V3I@ foot = new @V3I@(0, 0, 11);
  prot.rotate(foot);
  String up = kind.toUpperCase(java.util.Locale.ROOT);
  @PKG@.TpLog.info(up + " start: Server/Prefabs/" + key + " " + @PKG@.TpLogic.rotName(rot) + ", entities " + (ents ? "ON" : "OFF") + ", you at " + @PKG@.TpLogic.xyz(px, py, pz) + " facing " + @PKG@.TpLogic.dirName(fx, fz));
  @PKG@.TpLog.info(up + " anchor offset: prefab anchor (" + b.getAnchorX() + ", " + b.getAnchorY() + ", " + b.getAnchorZ() + ") is placed on block " + @PKG@.TpLogic.xyz(j.o.x, j.o.y, j.o.z) + " (ground top " + (guess ? "UNKNOWN - chunk not loaded, used your feet - 1" : "found") + "); buffer box relative to the anchor x " + b.getMinX(prot) + ".." + b.getMaxX(prot) + ", y " + b.getMinY() + ".." + b.getMaxY() + ", z " + b.getMinZ(prot) + ".." + b.getMaxZ(prot) + " (unrotated x " + b.getMinX() + ".." + b.getMaxX() + ", z " + b.getMinZ() + ".." + b.getMaxZ() + ")");
  if ("temple".equals(kind)) {
    j.report = "temple door side faces " + @PKG@.TpLogic.dirName(door.x, door.z) + " (+z of the prefab rotated); causeway foot / spawn spot about " + @PKG@.TpLogic.xyz(j.o.x + foot.x, j.o.y + 1, j.o.z + foot.z) + " (anchor + (0, 1, 11) rotated) - stand there and send /zone info";
  }
  @PKG@.TpLog.tell(pr, "Placing " + j.what + " (" + (ents ? "with" : "without") + " prefab entities)..." + ("temple".equals(kind) ? " Its door faces " + @PKG@.TpLogic.dirName(door.x, door.z) + "." : ""), INF);
  @PKG@.TpPaste.start(j);
}""")
# the lane: 40 steps along your facing, sideways S-curve, 3 wide; ground read now (loaded chunks), pasted as one buffer
M(cmds, r"""
public static void lane(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w) {
  if (!canStart(pr, w)) return;
  double[] me = where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  long t0 = System.nanoTime();
  int px = (int) me[0]; int py = (int) me[1]; int pz = (int) me[2]; int fx = (int) me[3]; int fz = (int) me[4];
  int sx = -fz; int sz = fx;
  int n = @PKG@.TpLogic.LANE_LEN;
  int half = @PKG@.TpLogic.LANE_HALF;
  int[] g = new int[n];
  for (int i = 0; i < n; i++) {
    int a = i + 3; int l = @PKG@.TpLogic.lat(i);
    g[i] = ground(w, px + fx * a + sx * l, pz + fz * a + sz * l);
    if (g[i] == @PKG@.TpEng.NO_HEIGHT) { @PKG@.TpLog.tell(pr, "Part of the lane is not loaded yet - look along open ground closer by.", ERR); return; }
  }
  int[] t = @PKG@.TpLogic.smooth(g);
  @ROT@ up = @PKG@.TpBuild.yawFor(fx, fz);
  @ROT@ down = @PKG@.TpBuild.yawFor(-fx, -fz);
  int rUp = @PKG@.TpBuild.rotIndex(up); int rDown = @PKG@.TpBuild.rotIndex(down);
  com.hypixel.hytale.server.core.prefab.selection.buffer.impl.PrefabBuffer$Builder b = @PBF@.newBuilder();
  int steps = 0; int raised = 0; int cut = 0; int lo = Integer.MAX_VALUE; int hi = Integer.MIN_VALUE;
  for (int i = 0; i < n; i++) {
    int a = i + 3; int l = @PKG@.TpLogic.lat(i);
    boolean stepUp = i + 1 < n && t[i + 1] > t[i];
    boolean stepDown = i > 0 && t[i - 1] > t[i];
    if (stepUp || stepDown) steps++;
    for (int s = -half; s <= half; s++) {
      int x = px + fx * a + sx * (l + s); int z = pz + fz * a + sz * (l + s);
      int gc = ground(w, x, z);
      if (gc == @PKG@.TpEng.NO_HEIGHT) gc = t[i];
      if (gc < t[i]) raised++;
      if (gc > t[i]) cut++;
      if (t[i] < lo) lo = t[i];
      if (t[i] > hi) hi = t[i];
      b.addColumn(x - px, z - pz, @PKG@.TpBuild.laneColumn(py, gc, t[i], stepUp ? rUp : rDown, stepUp || stepDown), null);
    }
  }
  @PKG@.TpJob j = new @PKG@.TpJob();
  j.pr = pr; j.w = w; j.kind = "lane";
  j.buf = b.build().newAccess();
  j.prot = @PROT@.ROTATION_0;
  j.o = new @V3I@(px, py, pz);
  j.flags = @PKG@.TpPaste.FORCE;
  j.what = "lane of " + n + " steps from " + @PKG@.TpLogic.xyz(px + fx * 3, t[0], pz + fz * 3) + " heading " + @PKG@.TpLogic.dirName(fx, fz);
  j.tLoad = System.nanoTime() - t0;
  j.t0 = System.nanoTime();
  j.report = "lane: " + steps + " step cells (stairs " + @PKG@.TpBuild.STAIR + " yaw up " + up + " / down " + down + "), " + raised + " columns raised (stone fill), " + cut + " columns cut, path height " + lo + ".." + hi + ", ground read " + @PKG@.TpLogic.ms(j.tLoad);
  @PKG@.TpLog.info("LANE start: you at " + @PKG@.TpLogic.xyz(px, py, pz) + " facing " + @PKG@.TpLogic.dirName(fx, fz) + "; ground " + java.util.Arrays.toString(g) + " -> path " + java.util.Arrays.toString(t));
  @PKG@.TpLog.tell(pr, "Laying a " + n + "-block cobble lane ahead...", INF);
  @PKG@.TpPaste.start(j);
}""")
M(cmds, r"""
public static void sign(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w) {
  if (!canStart(pr, w)) return;
  double[] me = where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  int px = (int) me[0]; int py = (int) me[1]; int pz = (int) me[2]; int fx = (int) me[3]; int fz = (int) me[4];
  int x = px + fx * 2; int z = pz + fz * 2;
  int gy = ground(w, x, z);
  if (gy == @PKG@.TpEng.NO_HEIGHT) gy = py - 1;
  @ROT@ face = @PKG@.TpBuild.yawFor(-fx, -fz);
  com.hypixel.hytale.server.core.prefab.selection.buffer.impl.PrefabBuffer$Builder b = @PBF@.newBuilder();
  b.addColumn(0, 0, new @PBE@[] { @PKG@.TpBuild.entry(0, @PKG@.TpBuild.SIGN, @PKG@.TpBuild.rotIndex(face)) }, null);
  @PKG@.TpJob j = new @PKG@.TpJob();
  j.pr = pr; j.w = w; j.kind = "sign";
  j.buf = b.build().newAccess();
  j.prot = @PROT@.ROTATION_0;
  j.o = new @V3I@(x, gy + 1, z);
  j.flags = @PKG@.TpPaste.FORCE;
  j.hx = x + 0.5; j.hy = gy + 2.05; j.hz = z + 0.5;
  j.what = "village sign at " + @PKG@.TpLogic.xyz(x, gy + 1, z);
  j.report = "sign block " + @PKG@.TpBuild.SIGN + " yaw " + face + " (rotation index " + @PKG@.TpBuild.rotIndex(face) + ", meant to face you)";
  j.t0 = System.nanoTime();
  @PKG@.TpLog.info("SIGN start: you at " + @PKG@.TpLogic.xyz(px, py, pz) + " facing " + @PKG@.TpLogic.dirName(fx, fz) + "; desk check: Furniture_Village_Sign has no text state in Assets.zip and the server has no sign text component");
  @PKG@.TpLog.tell(pr, "Signs cannot hold text on this server - placing a sign with a floating name above it instead...", INF);
  @PKG@.TpPaste.start(j);
}""")
M(cmds, r"""
public static void npc(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, boolean pebble) {
  if (!worldOk(pr, w)) return;
  String kind = pebble ? "pebble" : "npc";
  String up = kind.toUpperCase(java.util.Locale.ROOT);
  @PKG@.TpRec old = @PKG@.TpStore.find(kind, w.getName());
  if (old != null) {
    @REF@ e = old.uuids.length() == 0 ? null : @PKG@.TpNpc.find(w, old.uuidList()[0]);
    int n = @PKG@.TpNpc.countNear(st, old.nx, old.ny, old.nz);
    @PKG@.TpLog.info(up + " check: the probe " + kind + " from record " + old.seq + " (entity " + old.uuids + ") is " + (e != null ? "PRESENT" : "NOT FOUND (unloaded or gone)") + "; " + n + " " + @PKG@.TpNpc.ROLE + " NPCs within 3 blocks of " + old.nx + " " + old.ny + " " + old.nz + " (pass = 1)");
    @PKG@.TpLog.tell(pr, (pebble ? "Pebble" : "Mossby") + " is already placed (" + (e != null ? "found" : "not found right now") + "; " + n + " at that spot - 1 is right). Not spawning another. /townprobe undo removes it.", e != null && n == 1 ? OK : ERR);
    return;
  }
  if (!canStart(pr, w)) return;
  double[] me = where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  long t0 = System.nanoTime();
  int fx = (int) me[3]; int fz = (int) me[4];
  int bx = (int) me[0] + fx * 3; int bz = (int) me[2] + fz * 3;
  int gy = ground(w, bx, bz);
  if (gy == @PKG@.TpEng.NO_HEIGHT) gy = (int) me[1] - 1;
  @V3D@ pos = new @V3D@(bx + 0.5, gy + 1.0, bz + 0.5);
  @R3F@ rot = @PKG@.TpNpc.facing(pos.x, pos.z, me[6], me[8]);
  @PAIR@ p = null;
  String modelNote = "";
  try {
    if (!pebble) p = @PKG@.TpEng.spawnNpc(st, @PKG@.TpNpc.ROLE, pos, rot);
    else {
      int ri = @PKG@.TpEng.roleIndex(@PKG@.TpNpc.ROLE);
      @MDL@ m = @PKG@.TpNpc.model(@PKG@.TpNpc.ROCK, @PKG@.TpNpc.ROCK_SCALE);
      if (ri < 0 || m == null) { @PKG@.TpLog.tell(pr, "Pebble needs the vanilla role " + @PKG@.TpNpc.ROLE + " (" + ri + ") and the model " + @PKG@.TpNpc.ROCK + " (" + (m != null) + ").", ERR); return; }
      p = @PKG@.TpEng.spawnModel(st, ri, pos, rot, m);
    }
  } catch (Throwable t) { @PKG@.TpLog.warn(up + " spawn threw: " + t); p = null; }
  @REF@ e = p == null ? null : (@REF@) p.first();
  if (e == null || !e.isValid()) { @PKG@.TpLog.tell(pr, "The " + kind + " did not spawn (see the server log).", ERR); @PKG@.TpLog.info(up + " FAILED: spawn returned nothing for role " + @PKG@.TpNpc.ROLE); return; }
  if (pebble) {
    String got = @PKG@.TpNpc.modelId(st, e);
    boolean kept = got.startsWith(@PKG@.TpNpc.ROCK + " ");
    modelNote = "model after spawn: " + got + (kept ? " (the role KEPT our rock model)" : " (the role REPLACED our rock model)");
    if (!kept) {
      @MDL@ m2 = @PKG@.TpNpc.model(@PKG@.TpNpc.ROCK, @PKG@.TpNpc.ROCK_SCALE);
      st.putComponent(e, @MC@.getComponentType(), new @MC@(m2));
      st.putComponent(e, @PM@.getComponentType(), new @PM@(m2.toReference()));
      modelNote = modelNote + "; forced the rock back: now " + @PKG@.TpNpc.modelId(st, e);
    }
  }
  @PKG@.TpNpc.name(st, e, pebble ? @PKG@.TpNpc.PEBBLE_NAME : @PKG@.TpNpc.NPC_NAME);
  String use = pebble ? "" : @PKG@.TpNpc.makeUsable(st, e);
  java.util.UUID u = @PKG@.TpNpc.uuidOf(st, e);
  @PKG@.TpRec r = new @PKG@.TpRec();
  r.seq = @PKG@.TpStore.nextSeq();
  r.kind = kind; r.world = w.getName();
  r.ox = bx; r.oy = gy + 1; r.oz = bz;
  r.nx = pos.x; r.ny = pos.y; r.nz = pos.z;
  r.uuids = u == null ? "" : u.toString();
  r.what = (pebble ? "Pebble" : "Mossby") + " at " + @PKG@.TpLogic.xyz(bx, gy + 1, bz);
  r.time = System.currentTimeMillis();
  @PKG@.TpStore.add(r);
  NPC_SPAWNS.incrementAndGet();
  long dt = System.nanoTime() - t0;
  @PKG@.TpLog.info(up + " spawned: role " + @PKG@.TpNpc.ROLE + ", entity " + r.uuids + ", at " + pos.x + " " + pos.y + " " + pos.z + " facing you, in " + @PKG@.TpLogic.ms(dt) + (use.length() > 0 ? "; " + use : "") + (modelNote.length() > 0 ? "; " + modelNote : "") + "; model " + @PKG@.TpNpc.modelId(st, e) + "; undo record " + r.seq);
  if (pebble) @PKG@.TpLog.tell(pr, "Pebble is here. Does a mossy rock stand there (or a Kweebec)? " + modelNote, OK);
  else @PKG@.TpLog.tell(pr, "Mossby is here. Press F on him - the Bazaar should open. Walk away and back for his greeting.", OK);
}""")
M(cmds, r"""
public static void zone(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String opt) {
  String o = opt == null ? "" : opt.trim().toLowerCase(java.util.Locale.ROOT);
  if (o.equals("off")) {
    boolean had = @PKG@.TpStore.ZONE != null;
    @PKG@.TpStore.ZONE = null;
    @PKG@.TpTick.IN.clear();
    @PKG@.TpLog.info("ZONE off (" + (had ? "was on" : "was already off") + ")");
    @PKG@.TpLog.tell(pr, had ? "The probe zone is gone." : "There was no probe zone.", OK);
    return;
  }
  if (o.length() > 0 && !o.equals("all")) { @PKG@.TpLog.tell(pr, "Use /townprobe zone, /townprobe zone all or /townprobe zone off.", ERR); return; }
  if (!worldOk(pr, w)) return;
  double[] me = where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  @PKG@.TpZone z = new @PKG@.TpZone(w.getName(), me[0] + 0.5, me[2] + 0.5, o.equals("all"));
  @PKG@.TpStore.ZONE = z;
  @PKG@.TpTick.IN.clear();
  @PKG@.TpLog.info("ZONE on (" + (z.all ? "everyone refused, admins too" : "non-admins refused") + ", memory only) centre " + me[0] + " " + me[2] + " corners " + @PKG@.TpLogic.polyText(z.xs, z.zs));
  @PKG@.TpLog.tell(pr, "Probe zone on around you (about 20 blocks across, an odd 9-corner shape): breaking, placing and using blocks inside is refused for " + (z.all ? "everyone, admins too" : "non-admins") + ". Outside is normal. /townprobe zone off removes it.", OK);
}""")
M(cmds, r"""
public static void undo(@PR@ pr, @WLD@ w) {
  @PKG@.TpRec r = @PKG@.TpStore.last();
  if (r == null) { @PKG@.TpLog.tell(pr, "Nothing to undo.", INF); return; }
  if (w == null || !r.world.equals(w.getName())) { @PKG@.TpLog.tell(pr, "The newest probe change (" + r.what + ") is in world " + r.world + " - go there to undo it.", ERR); return; }
  if (@PKG@.TpStore.busy()) { @PKG@.TpLog.tell(pr, "Still working on the last probe action - try again in a moment.", ERR); return; }
  long t0 = System.nanoTime();
  if (r.snap.length() == 0) {
    @ST@ st = @PKG@.TpEng.store(w);
    String[] us = r.uuidList();
    @REF@ e = us.length == 0 ? null : @PKG@.TpNpc.find(w, us[0]);
    long now = System.currentTimeMillis();
    if (e == null && us.length > 0 && @PKG@.TpEng.height(w, (int) Math.floor(r.nx), (int) Math.floor(r.nz)) == @PKG@.TpEng.NO_HEIGHT) {
      r.dropAsk = 0L;
      @PKG@.TpLog.info("UNDO: " + r.what + " (entity " + r.uuids + ") is in an unloaded area around " + Math.round(r.nx) + " " + Math.round(r.nz) + " - kept (forgetting it now would leave it in the world)");
      @PKG@.TpLog.tell(pr, r.what + " is in an area that is not loaded. Go near it (" + Math.round(r.nx) + ", " + Math.round(r.nz) + ") and run /townprobe undo again.", ERR);
      return;
    }
    if (e == null && us.length > 0 && now - r.dropAsk > 30000L) {
      r.dropAsk = now;
      @PKG@.TpLog.info("UNDO: " + r.what + " (entity " + r.uuids + ") not found although its area is loaded - already gone; asked to confirm");
      @PKG@.TpLog.tell(pr, r.what + " is not there any more (its area is loaded but the entity is gone). Run /townprobe undo again within 30 s to forget it.", ERR);
      return;
    }
    String gone = @PKG@.TpNpc.removeAll(w, st, r);
    @PKG@.TpStore.remove(r);
    @PKG@.TpLog.info("UNDO done: " + r.kind + " record " + r.seq + " (" + r.what + ") - " + gone + " in " + @PKG@.TpLogic.ms(System.nanoTime() - t0) + "; files deleted; " + @PKG@.TpStore.RECS.size() + " records left");
    @PKG@.TpLog.tell(pr, "Undone: " + r.what + " (" + @PKG@.TpStore.RECS.size() + " more to undo).", OK);
    return;
  }
  @PKG@.TpJob j = new @PKG@.TpJob();
  j.pr = pr; j.w = w; j.undo = true; j.rec = r; j.kind = r.kind; j.what = r.what;
  j.o = new @V3I@(r.ox, r.oy, r.oz);
  j.prot = @PROT@.ROTATION_0;
  j.flags = @PKG@.TpPaste.FORCE;
  j.t0 = t0;
  @PKG@.TpLog.tell(pr, "Putting back: " + r.what + "...", INF);
  if (r.buf != null) {
    j.buf = ((@PBF@) r.buf).newAccess();
    @PKG@.TpPaste.start(j);
    return;
  }
  @PATH@ p = @PKG@.TpStore.snapPath(r);
  j.ticket = @PKG@.TpStore.begin();
  try {
    @PBU@.readFromFileAsync(p).orTimeout(30L, java.util.concurrent.TimeUnit.SECONDS).handleAsync(new @PKG@.TpStep(j, 1), w);
  } catch (Throwable t) { @PKG@.TpPaste.fail(j, "the snapshot file could not be read: " + t); }
}""")
# one entry point: args = the tokens after /townprobe (0 - 3 of them)
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String a, String b, String c) {
  String t = a == null ? "" : a.trim().toLowerCase(java.util.Locale.ROOT);
  @PKG@.TpLog.info(pr.getUsername() + " ran /townprobe " + t + (b == null ? "" : " " + b) + (c == null ? "" : " " + c) + " in " + (w == null ? "?" : w.getName()));
  if (t.length() == 0 || t.equals("help")) { help(pr); return; }
  if (t.equals("temple")) { if (c != null) { help(pr); return; } pastePrefab(pr, st, ref, w, @PKG@.TpLogic.TEMPLE, b, "temple"); return; }
  if (t.equals("piece")) { if (b == null) { @PKG@.TpLog.tell(pr, "Usage: /townprobe piece <prefab path or alias> [0-3]", ERR); return; } pastePrefab(pr, st, ref, w, @PKG@.TpLogic.prefabKey(b), c, "piece"); return; }
  if (b != null) { @PKG@.TpLog.tell(pr, "Too many words after /townprobe " + t + ".", ERR); help(pr); return; }
  if (t.equals("undo")) { undo(pr, w); return; }
  if (t.equals("lane")) { lane(pr, st, ref, w); return; }
  if (t.equals("npc")) { npc(pr, st, ref, w, false); return; }
  if (t.equals("pebble")) { npc(pr, st, ref, w, true); return; }
  if (t.equals("sign")) { sign(pr, st, ref, w); return; }
  if (t.equals("zone")) { zone(pr, st, ref, w, c); return; }
  @PKG@.TpLog.tell(pr, "Unknown option '" + a.trim() + "'.", ERR);
  help(pr);
}""")
# /townprobe zone all|off arrive as 2 tokens: route them here (run() only lets 'temple' / 'piece' take more than one)
M(cmds, r"""
public static void run2(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String a, String b) {
  String t = a == null ? "" : a.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("zone")) { @PKG@.TpLog.info(pr.getUsername() + " ran /townprobe zone " + b + " in " + (w == null ? "?" : w.getName())); zone(pr, st, ref, w, b); return; }
  run(ref, st, pr, w, a, b, null);
}""")

# =====================================================================================================================
# TpUseSys: F (Use) on a probe NPC -> open the SkyyBazaar page by its registered page id (or Pebble says a line). Cancels the
# vanilla *UseNPC for our NPCs only. The event is invoked on the PLAYER (UseEntityInteraction.firstRun: invoke(context.getEntity(), ...)).
# =====================================================================================================================
use = mk("TpUseSys", T["EES"])
F(use, "public static boolean FAILED_ONCE = false;")
F(use, "public static final String PAGE = %s;" % json.dumps(PAGE))
F(use, "public static java.util.concurrent.atomic.AtomicLong OPENS = new java.util.concurrent.atomic.AtomicLong();")
C(use, "public TpUseSys() { super(@UEPRE@.class); }")
M(use, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
# answers "" when opened, else why not
M(use, r"""
public static String openPage(@REF@ r, @ST@ st, @CAC@ acc, @PR@ pr) {
  @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
  if (p == null) return "no Player component";
  if (!@OCU@.PAGE_CODEC.getRegisteredIds().contains(PAGE)) return "page id " + PAGE + " is not registered (is SkyyBazaar installed and enabled?)";
  @CODEC@ c = @OCU@.PAGE_CODEC.getCodecFor((Object) PAGE);
  if (c == null) return "no codec for page id " + PAGE;
  Object s = c.decode(new org.bson.BsonDocument(), @EEI@.EMPTY);
  if (!(s instanceof @CPS@)) return "page id " + PAGE + " decoded to " + s;
  @CUP@ page = ((@CPS@) s).tryCreate(r, acc, pr, null);
  if (page == null) return "the " + PAGE + " page supplier returned no page";
  p.getPageManager().openCustomPage(r, st, page);
  return "";
}""")
M(use, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (@PKG@.TpStore.NPCS.isEmpty()) return;
    if (!(ev instanceof @UEPRE@)) return;
    @UEPRE@ e = (@UEPRE@) ev;
    @REF@ t = e.getTargetEntity();
    if (t == null || !t.isValid()) return;
    java.util.UUID u = @PKG@.TpNpc.uuidOf(st, t);
    if (u == null) return;
    @PKG@.TpRec rec = (@PKG@.TpRec) @PKG@.TpStore.NPCS.get(u.toString());
    if (rec == null) return;
    e.setCancelled(true);
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (!"npc".equals(rec.kind)) { @PKG@.TpLog.tell(pr, "[Pebble] ...the rock looks back at you.", "@COLBRK@"); @PKG@.TpLog.info("USE: " + pr.getUsername() + " used " + rec.kind + " " + u); return; }
    String why = openPage(r, st, (@CAC@) buf, pr);
    OPENS.incrementAndGet();
    if (why.length() == 0) @PKG@.TpLog.info("USE: " + pr.getUsername() + " pressed F on Mossby (" + u + ") -> " + PAGE + " page OPENED via its page id");
    else { @PKG@.TpLog.info("USE: " + pr.getUsername() + " pressed F on Mossby (" + u + ") -> page NOT opened: " + why); @PKG@.TpLog.tell(pr, "Mossby could not open the Bazaar: " + why, "@COLERR@"); }
  } catch (Throwable x) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("use hook failed (logged once): " + x); }
  }
}""")

# =====================================================================================================================
# Guards: ONE registerSystem per class - TpGuard base (EntityEventSystem on the acting player, Archetype.empty() like SkyyIslands' guards)
# =====================================================================================================================
guard = mk("TpGuard", T["EES"])
F(guard, "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();")
F(guard, "public static volatile long LAST_OUT = 0L;")
F(guard, "public static volatile long LAST_ADMIN = 0L;")
F(guard, "public static boolean FAILED_ONCE = false;")
F(guard, "public static java.util.concurrent.atomic.AtomicLong REFUSED = new java.util.concurrent.atomic.AtomicLong();")
C(guard, "public TpGuard(Class cls) { super(cls); }")
M(guard, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
M(guard, "public @V3I@ target(@EV@ ev) { return null; }")
M(guard, "public String action() { return \"?\"; }")
M(guard, r"""
public static boolean isAdmin(@PR@ pr) {
  try { return pr != null && pr.hasPermission("@NODE@"); } catch (Throwable t) { return false; }
}""")
# the decision (no side effects): 1 = refuse, 0 = allow inside (admin), -1 = outside / no zone
M(guard, r"""
public static int decide(@PKG@.TpZone z, String world, int x, int z2, boolean admin) {
  if (z == null || !z.contains(world, x + 0.5, z2 + 0.5)) return -1;
  if (z.all || !admin) return 1;
  return 0;
}""")
M(guard, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    @PKG@.TpZone z = @PKG@.TpStore.ZONE;
    if (z == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null || !z.world.equals(w.getName())) return;
    @V3I@ b = target(ev);
    if (b == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    int d = decide(z, w.getName(), b.x, b.z, isAdmin(pr));
    long now = System.currentTimeMillis();
    if (d < 0) {
      if (now - LAST_OUT > 3000L) { LAST_OUT = now; @PKG@.TpLog.info("ZONE: " + action() + " by " + pr.getUsername() + " at " + @PKG@.TpLogic.xyz(b.x, b.y, b.z) + " is OUTSIDE the zone - allowed"); }
      return;
    }
    if (d == 0) {
      if (now - LAST_ADMIN > 3000L) { LAST_ADMIN = now; @PKG@.TpLog.info("ZONE: " + action() + " by admin " + pr.getUsername() + " at " + @PKG@.TpLogic.xyz(b.x, b.y, b.z) + " inside the zone - allowed (admins pass; /townprobe zone all refuses admins too)"); }
      return;
    }
    if (ev instanceof @ICE@) ((@ICE@) ev).setCancelled(true);
    REFUSED.incrementAndGet();
    Long last = (Long) WARNED.get(pr.getUuid());
    if (last == null || now - last.longValue() > 3000L) {
      WARNED.put(pr.getUuid(), Long.valueOf(now));
      @PKG@.TpLog.info("ZONE: REFUSED " + action() + " by " + pr.getUsername() + " at " + @PKG@.TpLogic.xyz(b.x, b.y, b.z));
      @PKG@.TpLog.tell(pr, "Town probe zone: you can't " + action() + " here.", "@COLERR@");
    }
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("zone guard failed (logged once): " + t); }
  }
}""")
GUARDS = [("TpGuardBreak", "BBE", "break blocks"), ("TpGuardDamage", "DBE", "dig blocks"), ("TpGuardPlace", "PLBE", "place blocks"),
          ("TpGuardUse", "UBPRE", "use blocks")]
gcls = []
for gname, gev, gact in GUARDS:
    gc = mk(gname, PKG + ".TpGuard")
    C(gc, "public %s() { super(@%s@.class); }" % (gname, gev))
    M(gc, r"""
public @V3I@ target(@EV@ ev) {
  if (!(ev instanceof @XEV@)) return null;
  return ((@XEV@) ev).getTargetBlock();
}""".replace("@XEV@", "@%s@" % gev))
    M(gc, "public String action() { return %s; }" % json.dumps(gact))
    gcls.append(gc)

# =====================================================================================================================
# the commands: /townprobe (alias /tprobe) + usage variants for 1, 2 and 3 tokens (HANDOFF COMMAND RULES 2)
# =====================================================================================================================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
c1 = mk("TownProbeArgCmd", T["APC"])
F(c1, "public @RA@ aArg;")
C(c1, r"""
public TownProbeArgCmd() {
  super("(admin) /townprobe <temple, undo, lane, npc, pebble, zone, sign, help>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("action", "temple, undo, lane, piece, npc, pebble, zone, sign or help", @ATY@.STRING);
}""")
M(c1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.aArg)); } catch (Throwable t) { @PKG@.TpCmds.help(pr); return; }
  @PKG@.TpCmds.run(ref, store, pr, world, a, null, null);
}""")
c2 = mk("TownProbeArg2Cmd", T["APC"])
F(c2, "public @RA@ aArg;")
F(c2, "public @RA@ bArg;")
C(c2, r"""
public TownProbeArg2Cmd() {
  super("(admin) /townprobe temple <0-3>, /townprobe piece <prefab path>, /townprobe zone <all, off>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("action", "temple, piece or zone", @ATY@.STRING);
  this.bArg = withRequiredArg("value", "a rotation 0-3 (add e for entities), a prefab path / alias, or all / off", @ATY@.STRING);
}""")
M(c2, EXEC + r""" {
  String a = null; String b = null;
  try { a = String.valueOf(ctx.get(this.aArg)); b = String.valueOf(ctx.get(this.bArg)); } catch (Throwable t) { @PKG@.TpCmds.help(pr); return; }
  @PKG@.TpCmds.run2(ref, store, pr, world, a, b);
}""")
c3 = mk("TownProbeArg3Cmd", T["APC"])
F(c3, "public @RA@ aArg;")
F(c3, "public @RA@ bArg;")
F(c3, "public @RA@ cArg;")
C(c3, r"""
public TownProbeArg3Cmd() {
  super("(admin) /townprobe piece <prefab path or alias> <0-3>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("action", "piece", @ATY@.STRING);
  this.bArg = withRequiredArg("prefab", "a prefab path under Server/Prefabs or an alias (stall, cottage, softwood, cabin, plains, lighthouse, tower, well, pool, path)", @ATY@.STRING);
  this.cArg = withRequiredArg("rotation", "0-3, add e for the prefab's entities (e.g. 2e)", @ATY@.STRING);
}""")
M(c3, EXEC + r""" {
  String a = null; String b = null; String c = null;
  try { a = String.valueOf(ctx.get(this.aArg)); b = String.valueOf(ctx.get(this.bArg)); c = String.valueOf(ctx.get(this.cArg)); } catch (Throwable t) { @PKG@.TpCmds.help(pr); return; }
  @PKG@.TpCmds.run(ref, store, pr, world, a, b, c);
}""")
cmd = mk("TownProbeCmd", T["APC"])
C(cmd, r"""
public TownProbeCmd() {
  super("townprobe", "(admin) Zone 1 town probe (throwaway dev pack): /townprobe lists the actions");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "tprobe" });
  addUsageVariant(new @PKG@.TownProbeArgCmd());
  addUsageVariant(new @PKG@.TownProbeArg2Cmd());
  addUsageVariant(new @PKG@.TownProbeArg3Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.TpCmds.run(ref, store, pr, world, null, null, null);
}""")

# ---- the plugin
pl = mk("SkyyTownProbePlugin", T["JP"])
C(pl, "public SkyyTownProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.TpLog.LOG = getLogger();
  try { @PKG@.TpStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyTownProbe"); } catch (Throwable t) { @PKG@.TpStore.DIR = null; @PKG@.TpLog.warn("no data folder: " + t); }
  int n = @PKG@.TpStore.load();
  getCommandRegistry().registerCommand(new @PKG@.TownProbeCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpUseSys());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardBreak());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardDamage());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardPlace());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardUse());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpTick());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyTownProbe] @VERSION@ ready - /townprobe (admin, Zone 1 test island @WORLD@ only): " + n + " undo records, " + @PKG@.TpStore.NPCS.size() + " probe entities known (throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.TpStore.ZONE = null;
  @PKG@.TpTick.ACC.clear();
  @PKG@.TpTick.BARKED.clear();
  @PKG@.TpTick.IN.clear();
  @PKG@.TpGuard.WARNED.clear();
  super.shutdown();
}""")

ALL = [log, lg, rec, zone, sto, api, eng, snp, ec, grab, bld, job, stp, pst, iod, npc, cmds, use, guard] + gcls + [tick, c1, c2, c3, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyTownProbe-%s.jar" % VERSION)
man = B.manifest("SkyyTownProbe", VERSION, "SkyWynn THROWAWAY dev pack: the Zone 1 town T0 probe (/townprobe, admin only, Zone 1 test island) - temple paste + undo, lane, prefab pieces, Bazaar NPC, Pebble, no-build zone, sign. Pinned for one test session, then removed.", PKG + ".SkyyTownProbePlugin")
man["IncludesAssetPack"] = False   # class-only jar (no asset = nothing for the engine's asset validators to refuse)
B.assemble(jar, man, OUT, {})
