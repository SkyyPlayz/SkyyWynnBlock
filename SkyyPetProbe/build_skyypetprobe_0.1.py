"""SkyyPetProbe 0.1 - build script (javassist via jpype). NEW throwaway probe mod for research/cloud/Pet-Core-Spec.md section 8, probes
P1-P10 (they gate SkyyPets 0.2 visible pets, 0.4 summon fights, 0.5 mounts). Skyy 2026-10-08/09: "we should make a pet for every nutral
mob in the game ... i want all the pets of them to be similar just a little smaller and cuter. (keep the mounts near the same size or
bigger, but like a skeleton pet would be about fox size." Admin-only, pinned for ONE test session, then removed from the SET (like
SkyyMonkProbe / SkyyReelProbe / SkyyTownProbe). Probe mods have no patch chain: this is a plain build script.
Run:   python SkyyPetProbe/build_skyypetprobe_0.1.py   -> SkyyPetProbe/SkyyPetProbe-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyPetProbe/test_skyypetprobe_0.1.py    (-Xverify:all, every code path executed on engine stand-ins, the vanilla models
       through the engine's own ModelAsset codec, permissions, start twice on a scratch copy of live data, engine-access audit;
       scratch tools/dev/scratch/petprobe/)

NO ASSET SHIPPED (the 2026-10-08 SkyyArmory lesson): the jar holds classes only (IncludesAssetPack false) - nothing for the engine's asset
validators to refuse. Every pet is a VANILLA role spawned with a VANILLA model by id at our own scale (Model.createScaledModel ->
NPCPlugin.spawnEntity(store, role, pos, rot, model, preAdd, null)); nothing vanilla is copied. Our own role FILE (SkyyPet_Follow as a
Variant) is NOT probed here (it needs an asset pack round of its own); P2 probes the engine half of it: does a role keep the Model we
pass, or does its Appearance win? Every vanilla id the probe names is checked against Assets.zip at build time.

THE COMMAND  /petprobe (alias /pprobe); op only: requirePermission skyypetprobe.admin + no permission groups (lint perm_group_leaks).
Every result is a "[SkyyPetProbe] RESULT P<n> PASS|FAIL|LOOK: ..." line in the server log (LOOK = Skyy must look and say), the same line
in chat, and a line in <server>/mods/Skyy_SkyyPetProbe/probe.log (the only file the probe writes).
  /petprobe [help]       the list
  /petprobe all          the safe ones in rows ahead of you: p1 (row 4 ahead), p2 (8), p4 (12), p8 (15)
  /petprobe p1 [air|water]  small scales + walk "skating": Test_Pet role (invulnerable, follows the nearest player, teleports when far)
                         with Skeleton_Fighter x0.6 (Fox size), Fox x0.8, Wolf_Black x0.75, Eye_Void x0.35, Rex_Cave x0.3,
                         Whale_Humpback x0.2 and a mount at full size (Horse x1.0). air = Owl / Bat with their own flying roles + a
                         walking owl; water = Bluegill / Jellyfish / tiny whale with swimming roles (stand in water). Read back after
                         1 s: model id + scale kept, hitbox (BoundingBox component vs the scaled model box), nameplate; after 20 s a
                         follow summary (distance, teleports) - Skyy looks at legs (skating), nameplates, can you hit the tiny ones.
  /petprobe p2           role vs passed model: Test_Pet(Corgi) + Fox x0.8, Risen_Knight(Skeleton_Knight) + Skeleton_Fighter x0.6,
                         Tamed_Horse(Horse) + Bison x1.0, Empty_Role(Mannequin) + Corgi x1.0 - read back at 1 s and 6 s.
  /petprobe p3 [own]     follow + teleport when far: Test_Pet + Fox x0.8 (vanilla Seek + Teleport); 'own' = Empty_Role + Fox x0.8
                         moved by OUR code every tick (step toward you, stop at 3). Both: our fallback teleport when > 24 blocks for
                         2 s. Per second distance; 'vanilla teleport seen' = moved > 8 blocks in 1 s without ours; summary every 10 s,
                         verdict at 60 s (PASS = within 8 blocks 80 % of the time).
  /petprobe p4           scale change at runtime on Test_Pet + Fox x0.4: 4 s new ModelComponent x0.8, 8 s NPCEntity.setAppearance at
                         initial scale 1.0, 12 s EntityScaleComponent 1.5, 16 s setAppearance(Wolf_Black) = a baby -> adult style
                         model swap; each step read back at the next one; Skyy says which ones visibly changed.
  /petprobe p5           not saved with the chunk: A = Fox x0.8 WITH NonSerialized, B = Corgi WITHOUT (the control). Go 300+ blocks
                         away, wait 10 s, come back, run /petprobe p5 again -> report (A should be gone, B reloaded). After a server
                         restart the probe log's SPAWN-without-GONE uuids are removed when their chunk loads (the ghost sweep).
  /petprobe p6           flock from data: Risen_Knight (Template_Summoned_Ally: joins the nearest player's flock) + Skeleton_Fighter
                         x0.6; at 2 s and 5 s FlockPlugin.getFlockReference(pet) == (you)? Vanilla despawn timer 300 s is watched.
                         Assist / defend: the first hit any non-P7 probe pet deals is a "P6 LOOK: ATTACK: <pet> hit <target>" line.
  /petprobe p7 [credit]  a fighting summon: Risen_Knight + Skeleton_Fighter x0.6 and a target Pig ahead. Hit the pig once; the knight
                         should join in. Every hit by a probe pet is logged (target, amount, health, lethal). 'credit' toggles: the
                         pet's hits ON THE P7 PIG ONLY are rewritten to YOUR entity in the damage filter (Damage.setSource) - kill it
                         with credit on and off and say whether Combat XP / collections counted. Each p7 run removes the last run's
                         fighter + pig first; credit resets on clear / stop.
  /petprobe p8           SkyyMobs ignores pets: every probe pet is asked through mob:fn:info 3 s after it spawns (null = no level =
                         PASS); p8 also spawns a CONTROL Fox x0.8 with the vanilla hostile Fox role (expected: SkyyMobs DOES level it).
  /petprobe p9           lethal hit -> DOWN: Pig role + Skeleton_Fighter x0.6, not invulnerable. Hit it; the lethal hit is cancelled
                         in the damage filter and the pet is removed with no death / no drop (PASS) - a death = FAIL.
  /petprobe p10 [ride|big]  mounts: Tamed_Horse + Horse x1.0, Tamed_Horse + Horse x1.3 (bigger), Tamed_Horse + Bison x1.0 (a candidate
                         mount), Tamed_Horse + Horse x0.5 (pet size, "mount pets pet-size in slot 1"), Tamed_Camel + Camel, Tamed_Ram +
                         Ram (spec phase 5 "Horse, Camel, Ram first"). Press F on each (vanilla mount) or /petprobe p10 ride (OUR code
                         mount on the nearest one: the ActionMount steps - NPCMountComponent owner + anchor = the role's MountAnchorY x
                         scale, role -> Empty_Role, movement 'Mount'; if you are not riding it 3 s later your movement is reset).
                         Riding is read every second (Player.getMountEntityId == the pet's NetworkId). 'big' = just the x1.3 one.
  /petprobe list | clear | nosave on|off   list the probe pets / remove every probe pet (dismounts you first) / NonSerialized on
                         new spawns (default ON, so a crash leaves nothing; P5 B and 'nosave off' spawns are the saved ones).
                         list + clear end with the GHOST LIST: pets not loaded when something tried to remove them (they may sit in
                         a saved chunk) with their last known spot. "0 probe ghosts" = safe to remove the mod; otherwise stand
                         within 16 blocks of each spot for 5 s (found = removed, not found = confirmed gone).
LIFECYCLE (spec 2.2, logged as RESULT LIFE ...): logout (PlayerDisconnectEvent) -> your pets removed on their world thread; changing
world -> pets in the old world removed; profile switch (profile:epoch:<uuid> changes) -> removed; you die -> removed. Server stop ->
every pet queued for removal; whatever a saved chunk still holds is removed at the next start (probe log ghost sweep, P5). Fix round:
a ghost never expires by run count - only its chunk loading it or its spot seen loaded without it (PpLife.sweep) clears it.
SAVED DATA: only <server>/mods/Skyy_SkyyPetProbe/probe.log (SPAWN / WHERE / GONE / START / RESULT lines). A start with no probe folder
writes nothing.
ENGINE SEAM: the calls that need the NPC plugin / asset stores / a live world (role index, model asset, scaled model, spawn, uuid -> ref,
the world's store, flock ref, role change, the Mount movement config, dismount, setAppearance) go through PpEng's static wrappers; the
harness swaps them for stand-ins (PpEng.API) and checks the real lines by bytecode against the vanilla code they copy (ActionMount,
NPCPlugin, BodyMotionTeleport, EntitySpawnPage) + the access audit. Everything else runs for real in the harness.
"""
import sys, os, json, zipfile, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI

if "--deploy" in sys.argv:
    raise SystemExit("SkyyPetProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyypetprobe.admin"
MAX_PETS = 40
TELE_FAR = 24.0          # spec row pets.follow.teleport
STOP = 3.0               # spec row pets.follow.stop
OWN_SPEED = 5.0          # blocks / s for the 'own steering' probe
JUMP = 8.0               # a move this long within one second (without our teleport) = the role teleported it

# (role, model, scale, label) rows - every id checked against Assets.zip below
P1 = [("Test_Pet", "Skeleton_Fighter", 0.6, "Skeleton x0.6 (Fox size)"), ("Test_Pet", "Fox", 0.8, "Fox x0.8"),
      ("Test_Pet", "Wolf_Black", 0.75, "Wolf x0.75"), ("Test_Pet", "Eye_Void", 0.35, "Void Eye x0.35"),
      ("Test_Pet", "Rex_Cave", 0.3, "Cave Rex x0.3"), ("Test_Pet", "Whale_Humpback", 0.2, "Whale x0.2"),
      ("Test_Pet", "Horse", 1.0, "Horse x1.0 (mount size)")]
P1_AIR = [("Owl_Brown", "Owl_Brown", 1.0, "Owl (flying role)"), ("Bat", "Bat", 1.0, "Bat (flying role)"),
          ("Test_Pet", "Owl_Brown", 1.0, "Owl (walking role)")]
P1_WATER = [("Bluegill", "Bluegill", 0.8, "Bluegill x0.8"), ("Jellyfish_Blue", "Jellyfish_Blue", 0.8, "Jellyfish x0.8"),
            ("Bluegill", "Whale_Humpback", 0.2, "Whale x0.2 (fish role)")]
P2 = [("Test_Pet", "Fox", 0.8, "Fox on Test_Pet(Corgi)"), ("Risen_Knight", "Skeleton_Fighter", 0.6, "Skeleton on Risen_Knight"),
      ("Tamed_Horse", "Bison", 1.0, "Bison on Tamed_Horse"), ("Empty_Role", "Corgi", 1.0, "Corgi on Empty_Role(Mannequin)")]
P3 = [("Test_Pet", "Fox", 0.8, "P3 Fox (vanilla follow)")]
P3_OWN = [("Empty_Role", "Fox", 0.8, "P3 Fox (our steering)")]
P4 = [("Test_Pet", "Fox", 0.4, "P4 Fox x0.4 (grows)")]
P4_ADULT = "Wolf_Black"
P5 = [("Test_Pet", "Fox", 0.8, "P5 A Fox (NonSerialized)"), ("Test_Pet", "Corgi", 1.0, "P5 B Corgi (saved control)")]
P6 = [("Risen_Knight", "Skeleton_Fighter", 0.6, "P6 Skeleton (summon flock)")]
P7 = [("Risen_Knight", "Skeleton_Fighter", 0.6, "P7 Skeleton fighter")]
P7_TARGET = [("Pig", "Pig", 1.0, "P7 target - hit me once")]
P8 = [("Fox", "Fox", 0.8, "P8 control Fox (vanilla hostile role)")]
P9 = [("Pig", "Skeleton_Fighter", 0.6, "P9 Skeleton - hit me (DOWN test)")]
# fix round: + a pet-size Horse x0.5 (docs/answered/pets.md "mount pets pet-size in slot 1") and the other vanilla mount roles, Camel
# (tallest, 2.65) and Ram (spec phase 5 "Horse, Camel, Ram first"); each mount's anchor comes from ITS role (MOUNT_Y below)
P10 = [("Tamed_Horse", "Horse", 1.0, "P10 Horse x1.0"), ("Tamed_Horse", "Horse", 1.3, "P10 Horse x1.3 (bigger)"),
       ("Tamed_Horse", "Bison", 1.0, "P10 Bison x1.0 (candidate)"), ("Tamed_Horse", "Horse", 0.5, "P10 Horse x0.5 (pet size)"),
       ("Tamed_Camel", "Camel", 1.0, "P10 Camel x1.0"), ("Tamed_Ram", "Ram", 1.0, "P10 Ram x1.0")]
P10_BIG = [("Tamed_Horse", "Horse", 1.3, "P10 Horse x1.3 (bigger)")]
ROW_GAP = {"P10": 3.5}   # sideways gap per row (default 2.5); mounts are wide
MOUNT_ANCHOR_Y = 1.6     # Tamed_Horse MountAnchorY (checked below)
EMPTY_ROLE = "Empty_Role"
MOUNT_MOVE = "Mount"     # ActionMount's default movement config id
SUI.verify()
COL_OK, COL_ERR, COL_INFO, COL_LOOK = SUI.COLOR["success"], SUI.COLOR["error"], SUI.COLOR["info"], SUI.COLOR["gold"]

ROWS = {"P1": P1, "P1_AIR": P1_AIR, "P1_WATER": P1_WATER, "P2": P2, "P3": P3, "P3_OWN": P3_OWN, "P4": P4, "P5": P5, "P6": P6, "P7": P7,
        "P7_TARGET": P7_TARGET, "P8": P8, "P9": P9, "P10": P10, "P10_BIG": P10_BIG}

# ================= build-time desk checks (Assets.zip, read only) =================
az = zipfile.ZipFile(ASSETS)
AZ_NAMES = az.namelist()


def vanilla_json(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


ROLE_FILES = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
MODEL_FILES = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/Models/") and n.endswith(".json"))
for _k, _rows in ROWS.items():
    for _role, _model, _scale, _label in _rows:
        if _role not in ROLE_FILES:
            raise SystemExit("%s: vanilla role %s missing in Assets.zip" % (_k, _role))
        if _model not in MODEL_FILES:
            raise SystemExit("%s: vanilla model %s missing in Assets.zip" % (_k, _model))
        if not (0.1 <= _scale <= 2.0):
            raise SystemExit("%s: scale %s out of range" % (_k, _scale))
for _m in (P4_ADULT,):
    if _m not in MODEL_FILES:
        raise SystemExit("model %s missing" % _m)
for _r in (EMPTY_ROLE,):
    if _r not in ROLE_FILES:
        raise SystemExit("role %s missing" % _r)
_tp = vanilla_json(ROLE_FILES["Test_Pet"])
if _tp.get("Invulnerable") is not True or '"Teleport"' not in json.dumps(_tp) or _tp.get("Appearance") != "Corgi":
    raise SystemExit("Test_Pet changed (Invulnerable / Teleport body motion / Corgi appearance) - re-check P1-P5")
_rk = vanilla_json(ROLE_FILES["Risen_Knight"])
if _rk.get("Reference") != "Template_Summoned_Ally":
    raise SystemExit("Risen_Knight is no longer a Template_Summoned_Ally variant - re-check P6 / P7")
_tsa = vanilla_json(ROLE_FILES["Template_Summoned_Ally"])
SUMMON_DESPAWN = int((_tsa.get("Parameters") or {}).get("DespawnTimer", {}).get("Value", -1))
if '"JoinFlock"' not in json.dumps(_tsa) or SUMMON_DESPAWN <= 0:
    raise SystemExit("Template_Summoned_Ally no longer joins a flock / has no DespawnTimer - re-check P6")
_th = vanilla_json(ROLE_FILES["Tamed_Horse"])["Modify"]
if _th.get("IsMountable") is not True or float(_th.get("MountAnchorY", -1)) != MOUNT_ANCHOR_Y:
    raise SystemExit("Tamed_Horse mount data changed: %r" % ((_th.get("IsMountable"), _th.get("MountAnchorY")),))
MOUNT_Y = {}             # mount role -> its vanilla MountAnchorY (PpMount.anchorOf; our code mount scales it by the pet's scale)
for _role, _model, _scale, _label in P10 + P10_BIG:
    _md = vanilla_json(ROLE_FILES[_role]).get("Modify") or {}
    if _md.get("IsMountable") is not True or float(_md.get("MountAnchorY", -1)) <= 0:
        raise SystemExit("P10: %s is not a mountable role with a MountAnchorY" % _role)
    MOUNT_Y[_role] = float(_md["MountAnchorY"])
_er = vanilla_json(ROLE_FILES[EMPTY_ROLE])
if _er.get("Instructions") != [{}]:
    raise SystemExit("Empty_Role is no longer instruction-free - re-check P3 own / P10 ride")
_mv = [n for n in AZ_NAMES if re.search(r"/MovementConfig[s]?/.*\b%s\.json$" % MOUNT_MOVE, n) or n.endswith("/%s.json" % MOUNT_MOVE) and "Movement" in n]
if not _mv:
    raise SystemExit("movement config '%s' not found in Assets.zip" % MOUNT_MOVE)


def model_box(mid):
    """the vanilla hitbox (w, h, d) of a model id, following Parent; None when no HitBox anywhere up the chain"""
    seen = 0
    while mid and seen < 8:
        d = vanilla_json(MODEL_FILES[mid])
        hb = d.get("HitBox") or d.get("BoundingBox")
        if hb:
            mn, mx = hb["Min"], hb["Max"]
            return (mx["X"] - mn["X"], mx["Y"] - mn["Y"], mx["Z"] - mn["Z"])
        mid = d.get("Parent")
        seen += 1
    return None


VBOX = {}
for _rows in ROWS.values():
    for _role, _model, _scale, _label in _rows:
        VBOX[_model] = model_box(_model)
print("desk: %d probe rows, %d roles, %d models; Test_Pet invulnerable + teleport; Risen_Knight = Template_Summoned_Ally (DespawnTimer %d s); "
      "Tamed_Horse anchor %.1f; movement config %s (%s)" % (sum(len(r) for r in ROWS.values()), len(set(r[0] for rs in ROWS.values() for r in rs)),
                                                          len(VBOX), SUMMON_DESPAWN, MOUNT_ANCHOR_Y, MOUNT_MOVE, _mv[0]))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
PKG = "com.skyy.petprobe"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE,
    "COLOK": COL_OK, "COLERR": COL_ERR, "COLINF": COL_INFO, "COLLOOK": COL_LOOK,
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
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "HOL": "com.hypixel.hytale.component.Holder",
    "RR": "com.hypixel.hytale.component.RemoveReason",
    "ADR": "com.hypixel.hytale.component.AddReason",
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "SG": "com.hypixel.hytale.component.SystemGroup",
    "NSER": "com.hypixel.hytale.component.NonSerialized",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "HR": "com.hypixel.hytale.server.core.modules.entity.component.HeadRotation",
    "V3I": "org.joml.Vector3i",
    "V3D": "org.joml.Vector3d",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "BOX": "com.hypixel.hytale.math.shape.Box",
    "NPCP": "com.hypixel.hytale.server.npc.NPCPlugin",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "ROLE": "com.hypixel.hytale.server.npc.role.Role",
    "RCS": "com.hypixel.hytale.server.npc.systems.RoleChangeSystem",
    "MDL": "com.hypixel.hytale.server.core.asset.type.model.config.Model",
    "MDA": "com.hypixel.hytale.server.core.asset.type.model.config.ModelAsset",
    "MC": "com.hypixel.hytale.server.core.modules.entity.component.ModelComponent",
    "PM": "com.hypixel.hytale.server.core.modules.entity.component.PersistentModel",
    "ESC": "com.hypixel.hytale.server.core.modules.entity.component.EntityScaleComponent",
    "BBX": "com.hypixel.hytale.server.core.modules.entity.component.BoundingBox",
    "INV": "com.hypixel.hytale.server.core.modules.entity.component.Invulnerable",
    "UUC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "NPL": "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "DNC": "com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent",
    "PDN": "com.hypixel.hytale.server.core.modules.entity.component.PersistentDisplayName",
    "NID": "com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId",
    "TEL": "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "TRI": "com.hypixel.hytale.function.consumer.TriConsumer",
    "PAIR": "it.unimi.dsi.fastutil.Pair",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "ESV": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.DamageEventSystem",
    "DMOD": "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DSRC": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$Source",
    "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
    "DTH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "FLP": "com.hypixel.hytale.server.flock.FlockPlugin",
    "FLM": "com.hypixel.hytale.server.flock.FlockMembership",
    "MNT": "com.hypixel.hytale.builtin.mounts.NPCMountComponent",
    "MTP": "com.hypixel.hytale.builtin.mounts.MountPlugin",
    "MVM": "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager",
    "MVC": "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementConfig",
    "PHV": "com.hypixel.hytale.server.core.modules.physics.component.PhysicsValues",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
    "PATH": "java.nio.file.Path",
}
PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getReference"), (T["PR"], "getPacketHandler"), (T["PR"], "getComponentType"),
             (T["MSG"], "raw"), (T["MSG"], "color"), (T["PLA"], "getComponentType"), (T["PLA"], "getMountEntityId"), (T["PLA"], "getGameMode"),
             (T["WLD"], "getName"), (T["WLD"], "getEntityStore"), (T["WLD"], "execute"), (T["EST"], "getStore"), (T["EST"], "getRefFromUUID"),
             (T["EST"], "getWorld"), (T["EST"], "REGISTRY"), ("com.hypixel.hytale.component.ComponentRegistry", "getNonSerializedComponentType"),
             (T["NSER"], "get"), (T["TC"], "getPosition"), (T["HR"], "getHorizontalAxisDirection"), (T["NPCP"], "get"),
             (T["NPCP"], "getIndex"), (T["NPCP"], "spawnEntity"), (T["NPC"], "getRoleName"), (T["NPC"], "getRole"), (T["NPC"], "setAppearance"),
             (T["NPC"], "setInitialModelScale"), (T["MDA"], "getAssetMap"), (T["MDL"], "createScaledModel"), (T["MDL"], "getModelAssetId"),
             (T["MDL"], "getScale"), (T["MDL"], "getBoundingBox"), (T["MDL"], "toReference"), (T["MC"], "getModel"), (T["BOX"], "width"),
             (T["BOX"], "height"), (T["BOX"], "depth"), (T["BBX"], "getBoundingBox"), (T["ESC"], "getScale"), (T["INV"], "getComponentType"),
             (T["UUC"], "getUuid"), (T["NPL"], "getText"), (T["NID"], "getId"), (T["TEL"], "createExact"), (T["ESM"], "get"),
             (T["ESV"], "get"), (T["DST"], "getHealth"), (T["DMOD"], "getFilterDamageGroup"), (T["DMOD"], "getInspectDamageGroup"),
             (T["DMG"], "getSource"), (T["DMG"], "setSource"), (T["DMG"], "getAmount"), (T["DMG"], "setAmount"), (T["DMG"], "setCancelled"),
             (T["DMG"], "isCancelled"), (T["DENT"], "getRef"), (T["DTH"], "getComponentType"), (T["FLP"], "getFlockReference"),
             (T["FLM"], "getMembershipType"), (T["MNT"], "setOwnerPlayerRef"), (T["MNT"], "setAnchor"), (T["MNT"], "setOriginalRoleIndex"),
             (T["MNT"], "getOwnerPlayerRef"), (T["MNT"], "getAnchorY"), (T["MTP"], "checkDismountNpc"), (T["RCS"], "requestRoleChange"),
             (T["MVM"], "setDefaultSettings"), (T["MVM"], "applyDefaultSettings"), (T["MVM"], "update"), (T["MVM"], "resetDefaultsAndUpdate"), (T["MVC"], "getAssetMap"),
             (T["PDE"], "getPlayerRef"), (T["ST"], "putComponent"), (T["ST"], "removeEntity"), (T["CB"], "removeEntity"), (T["CB"], "putComponent"),
             (T["HOL"], "addComponent"), (T["HOL"], "ensureComponent"), (PB_, "getCommandRegistry"), (PB_, "getEntityStoreRegistry"),
             (PB_, "getEventRegistry"), (PB_, "getLogger"), (PB_, "getDataDirectory"), (PB_, "shutdown"), (PB_, "start"),
             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):
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


def jflt(xs):
    return "new float[] { %s }" % ", ".join("%sf" % repr(float(x)) for x in xs)


def vbox_text(mid, s):
    b = VBOX.get(mid)
    if not b:
        return "none (no HitBox in the model chain)"
    return "%.2f x %.2f x %.2f" % (b[0] * s, b[1] * s, b[2] * s)


# =====================================================================================================================
# PpFile: the probe log (the ONLY file the probe writes) + the ghost list read from it at start
# =====================================================================================================================
fil = mk("PpFile")
F(fil, "public static java.nio.file.Path DIR;")
F(fil, "public static final String NAME = \"probe.log\";")
F(fil, "public static volatile String LAST_ERR = \"\";")
F(fil, "public static final java.util.concurrent.ConcurrentHashMap GHOSTS = new java.util.concurrent.ConcurrentHashMap();")      # uuid -> info
F(fil, "public static final java.util.concurrent.ConcurrentHashMap GHOST_NONSER = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> Boolean
M(fil, r"""
public static java.nio.file.Path file() {
  return DIR == null ? null : DIR.resolve(NAME);
}""")
M(fil, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('\n', ' ').replace('\r', ' ');
}""")
M(fil, r"""
public static boolean append(String line) {
  java.nio.file.Path p = file();
  if (p == null) return false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    String l = java.time.Instant.now().toString() + " " + clean(line) + "\n";
    java.nio.file.Files.write(p, l.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
    return true;
  } catch (Throwable t) { LAST_ERR = String.valueOf(t); return false; }
}""")
F(fil, "public static final java.util.concurrent.ConcurrentHashMap GHOST_AT = new java.util.concurrent.ConcurrentHashMap();")    # uuid -> "world,x,z" (last known spot)
F(fil, "public static final java.util.concurrent.ConcurrentHashMap GHOST_NEAR = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> int[1] seconds a player stood at the spot
F(fil, "public static final double NEAR = 16.0;")   # a player this close (x / z) to the spot = its chunk is loaded
F(fil, "public static final int NEAR_SECS = 5;")     # ... for this many seconds without the entity = confirmed gone
M(fil, r"""
public static String wname(String n) {
  return n == null ? "?" : n.replace(' ', '_').replace(',', '_');
}""")
M(fil, r"""
public static String at(String world, double x, double z) {
  return wname(world) + "," + (Math.round(x * 10.0) / 10.0) + "," + (Math.round(z * 10.0) / 10.0);
}""")
M(fil, r"""
public static void clearGhosts() {
  GHOSTS.clear();
  GHOST_NONSER.clear();
  GHOST_AT.clear();
  GHOST_NEAR.clear();
}""")
M(fil, r"""
public static void removeGhost(String u) {
  if (u == null) return;
  GHOSTS.remove(u);
  GHOST_NONSER.remove(u);
  GHOST_AT.remove(u);
  GHOST_NEAR.remove(u);
}""")
# a pet that is not loaded now (clear / logout / stop could not reach it): it may sit in a saved chunk -> on the ghost list until a load
# removes it or its spot is seen loaded without it (PpLoadSys.sweep). The WHERE line carries its last known spot to the next start.
M(fil, r"""
public static void addGhost(String u, String info, boolean nonser, String at) {
  if (u == null) return;
  GHOSTS.put(u, info == null ? "" : info);
  GHOST_NONSER.put(u, Boolean.valueOf(nonser));
  if (at != null) { GHOST_AT.put(u, at); append("WHERE " + u + " " + at); }
}""")
# start: SPAWN lines with no GONE = entities that may still sit in a saved chunk -> GHOSTS, NonSerialized or not (fix round: no more
# expiry by run count - a ghost leaves the list only when its chunk loads it (PpLoadSys.added removes it) or its last known spot was
# loaded for NEAR_SECS without it (PpLoadSys.sweep)). SPAWN '... nonser=<b> at=<world,x,z> <tag> <label>'; WHERE '<uuid> <world,x,z>'
# moves the spot. No probe folder / no log -> nothing read, NOTHING written.
M(fil, r"""
public static int load() {
  clearGhosts();
  java.nio.file.Path p = file();
  if (p == null || !java.nio.file.Files.isRegularFile(p, new java.nio.file.LinkOption[0])) return 0;
  java.util.List ls;
  try { ls = java.nio.file.Files.readAllLines(p, java.nio.charset.StandardCharsets.UTF_8); } catch (Throwable t) { LAST_ERR = String.valueOf(t); return 0; }
  java.util.LinkedHashMap live = new java.util.LinkedHashMap();
  for (int i = 0; i < ls.size(); i++) {
    String l = (String) ls.get(i);
    String[] w = l.split(" ");
    if (w.length < 2) continue;
    if (w[1].equals("SPAWN") && w.length >= 4) {
      boolean hasAt = w.length >= 5 && w[4].startsWith("at=");
      String key = hasAt ? w[4] : w[3];
      int k = l.indexOf(key);
      String info = k < 0 ? w[2] : l.substring(k + key.length()).trim();
      live.put(w[2], new Object[] { info, Boolean.valueOf(w[3].equals("nonser=true")), hasAt ? w[4].substring(3) : null });
    } else if (w[1].equals("WHERE") && w.length >= 4) {
      Object[] v = (Object[]) live.get(w[2]);
      if (v != null) v[2] = w[3];
    } else if (w[1].equals("GONE") && w.length >= 3) {
      live.remove(w[2]);
    }
  }
  java.util.Iterator it2 = live.entrySet().iterator();
  while (it2.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it2.next();
    Object[] v = (Object[]) e.getValue();
    GHOSTS.put(e.getKey(), v[0]);
    GHOST_NONSER.put(e.getKey(), v[1]);
    if (v[2] != null) GHOST_AT.put(e.getKey(), v[2]);
  }
  append("START ghosts=" + GHOSTS.size());
  return GHOSTS.size();
}""")

# =====================================================================================================================
# PpLog: server log + chat + probe log. SINK (harness hook, null in game) gets every chat line as "<colour>|<text>".
# =====================================================================================================================
log = mk("PpLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List SINK;")
F(log, "public static final String COL_INF = \"@COLINF@\";")
F(log, "public static java.util.List LINES;")
F(log, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(log, r"""
public static void info(String msg) {
  try { if (LINES != null) LINES.add("INFO " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyPetProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LINES != null) LINES.add("WARN " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyPetProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warnOnce(String key, String msg) {
  if (ONCE.putIfAbsent(key, Boolean.TRUE) == null) warn(msg + " (logged once)");
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
# a probe result: v 1 = PASS, 0 = FAIL, -1 = LOOK (Skyy must look and say). Log + probe.log + chat (pr may be null).
M(log, r"""
public static String result(@PR@ pr, String probe, int v, String s) {
  String line = probe + " " + (v == 1 ? "PASS" : (v == 0 ? "FAIL" : "LOOK")) + ": " + s;
  info("RESULT " + line);
  @PKG@.PpFile.append("RESULT " + line);
  try { if (SINK != null && pr == null) SINK.add("-|" + line); } catch (Throwable t) { }
  if (pr != null) {
    try { if (SINK != null) SINK.add((v == 1 ? "@COLOK@" : (v == 0 ? "@COLERR@" : "@COLLOOK@")) + "|" + line); } catch (Throwable t) { }
    try {
      @MSG@ m = @MSG@.raw(line).color(v == 1 ? "@COLOK@" : (v == 0 ? "@COLERR@" : "@COLLOOK@"));
      pr.sendMessage(m);
    } catch (Throwable t) { }
  }
  return line;
}""")

# =====================================================================================================================
# PpLogic: pure functions (no engine objects) - the harness calls them on plain data
# =====================================================================================================================
lg = mk("PpLogic")
F(lg, "public static final double TELE_FAR = %s;" % TELE_FAR)
F(lg, "public static final double STOP = %s;" % STOP)
F(lg, "public static final double OWN_SPEED = %s;" % OWN_SPEED)
F(lg, "public static final double JUMP = %s;" % JUMP)
M(lg, r"""
public static String f1(double v) {
  long t = Math.round(v * 10.0);
  String s = t < 0L ? "-" : "";
  t = Math.abs(t);
  return s + (t / 10L) + "." + (t % 10L);
}""")
M(lg, r"""
public static String f2(double v) {
  long t = Math.round(v * 100.0);
  String s = t < 0L ? "-" : "";
  t = Math.abs(t);
  long c = t % 100L;
  return s + (t / 100L) + "." + (c < 10L ? "0" : "") + c;
}""")
M(lg, "public static String f1(float v) { return f1((double) v); }")
M(lg, "public static String f2(float v) { return f2((double) v); }")
M(lg, r"""
public static double dist(double ax, double ay, double az, double bx, double by, double bz) {
  double dx = ax - bx; double dy = ay - by; double dz = az - bz;
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}""")
# "p1".."p10" -> 1..10, "all" -> 0, else -1
M(lg, r"""
public static int probeNo(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("all")) return 0;
  if (t.length() < 2 || t.length() > 3 || t.charAt(0) != 'p') return -1;
  try {
    int n = Integer.parseInt(t.substring(1));
    return n >= 1 && n <= 10 ? n : -1;
  } catch (Throwable x) { return -1; }
}""")
# the yaw (radians) that faces (dx, dz): yaw 0 faces -z (SkyyWorldGen / SkyyTownProbe note)
M(lg, r"""
public static float yawToward(double dx, double dz) {
  if (dx == 0.0 && dz == 0.0) return 0.0f;
  return (float) Math.atan2(-dx, -dz);
}""")
# spot i of n in a row 'ahead' blocks in front (fx, fz = facing axis), 'gap' apart sideways: {x, z}
M(lg, r"""
public static double[] slot(int i, int n, double px, double pz, int fx, int fz, double ahead, double gap) {
  double side = (i - (n - 1) / 2.0) * gap;
  double sx = (double) -fz; double sz = (double) fx;
  return new double[] { px + fx * ahead + sx * side, pz + fz * ahead + sz * side };
}""")
# one steering step (x, z) toward (tx, tz): nothing inside 'stop'; never past 'stop'; at most 'maxStep'
M(lg, r"""
public static double[] step(double x, double z, double tx, double tz, double maxStep, double stop) {
  double dx = tx - x; double dz = tz - z;
  double d = Math.sqrt(dx * dx + dz * dz);
  if (d <= stop || d <= 0.0) return new double[] { x, z };
  double s = Math.min(maxStep, d - stop);
  return new double[] { x + dx / d * s, z + dz / d * s };
}""")
M(lg, r"""
public static double clamp(double v, double lo, double hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}""")
# P3 verdict: within 8 blocks at least 80 % of the sampled seconds
M(lg, r"""
public static boolean followOk(int near, int secs) {
  return secs > 0 && near * 5 >= secs * 4;
}""")
M(lg, r"""
public static boolean scaleIs(float a, float b) {
  return Math.abs(a - b) < 0.001f;
}""")
M(lg, r"""
public static String up(String tag) {
  return tag == null ? "?" : tag.toUpperCase(java.util.Locale.ROOT);
}""")
M(lg, r"""
public static String shortId(String u) {
  return u == null ? "?" : (u.length() > 8 ? u.substring(0, 8) : u);
}""")

# =====================================================================================================================
# PpPet: one probe entity (the throwaway view the spec describes; holds no saved data)
# =====================================================================================================================
pet = mk("PpPet")
for f in ("public String uuid;", "public @REF@ ref;", "public @WLD@ world;", "public String worldName;", "public java.util.UUID owner;",
          "public String ownerName;", "public @PR@ pr;", "public String tag;", "public String label;", "public String role;", "public int roleIdx;",
          "public String model;", "public float scale;", "public String vbox;", "public boolean nonser;", "public boolean invul;",
          "public int mode;", "public boolean fight;", "public boolean down;", "public boolean mount;", "public boolean codeMount;",
          "public boolean riding;", "public int netId;", "public long t0;", "public int stage;", "public boolean checked;",
          "public boolean mobChecked;", "public double lx;", "public double ly;", "public double lz;", "public boolean hasLast;",
          "public double maxD;", "public double sumD;", "public int secs;", "public int near;", "public int jumps;", "public int ours;",
          "public int far;", "public boolean justTele;", "public int steps;", "public int hitsDealt;", "public int hitsTaken;",
          "public int unloads;", "public int reloads;", "public int missing;", "public boolean gone;", "public boolean removing;",
          "public boolean queued;", "public String goneWhy;", "public String lastRead;", "public double kx;", "public double kz;",
          "public boolean hasK;", "public long moveAt;", "public float anchorY;"):
    F(pet, f)
C(pet, r"""public PpPet() { this.uuid = ""; this.worldName = ""; this.ownerName = ""; this.tag = ""; this.label = ""; this.role = ""; this.model = ""; this.vbox = ""; this.goneWhy = ""; this.lastRead = ""; }""")
M(pet, r"""
public String describe() {
  return this.label + " [" + this.tag + ", " + @PKG@.PpLogic.shortId(this.uuid) + ", role " + this.role + ", " + this.model + " x" + this.scale + (this.nonser ? ", not saved" : ", SAVED") + (this.invul ? ", invulnerable" : "") + "]";
}""")

# =====================================================================================================================
# PpReg: the live probe pets (memory) + flags
# =====================================================================================================================
reg = mk("PpReg")
F(reg, "public static final java.util.concurrent.ConcurrentHashMap PETS = new java.util.concurrent.ConcurrentHashMap();")    # uuid string -> PpPet
F(reg, "public static final java.util.concurrent.ConcurrentHashMap REWRITE = new java.util.concurrent.ConcurrentHashMap();")  # target uuid -> pet label (P7 credit)
F(reg, "public static final java.util.concurrent.ConcurrentHashMap EPOCH = new java.util.concurrent.ConcurrentHashMap();")    # owner uuid -> last epoch
F(reg, "public static final java.util.concurrent.ConcurrentHashMap DEAD = new java.util.concurrent.ConcurrentHashMap();")     # owner uuid -> TRUE while dead
F(reg, "public static volatile boolean CREDIT = false;")
F(reg, "public static volatile boolean NOSAVE = true;")
F(reg, "public static final int MAX = %d;" % MAX_PETS)
F(reg, "public static final int SUMMON_DESPAWN = %d;" % SUMMON_DESPAWN)
M(reg, r"""
public static java.util.UUID uuidOf(@CAC@ acc, @REF@ r) {
  try {
    if (r == null) return null;
    @UUC@ u = (@UUC@) acc.getComponent(r, @UUC@.getComponentType());
    return u == null ? null : u.getUuid();
  } catch (Throwable t) { return null; }
}""")
M(reg, r"""
public static @PKG@.PpPet petOf(@CAC@ acc, @REF@ r) {
  if (PETS.isEmpty() || r == null) return null;
  java.util.UUID u = uuidOf(acc, r);
  return u == null ? null : (@PKG@.PpPet) PETS.get(u.toString());
}""")
M(reg, r"""
public static java.util.List ofOwner(java.util.UUID o) {
  java.util.ArrayList l = new java.util.ArrayList();
  java.util.Iterator it = PETS.values().iterator();
  while (it.hasNext()) {
    @PKG@.PpPet p = (@PKG@.PpPet) it.next();
    if (o != null && o.equals(p.owner)) l.add(p);
  }
  return l;
}""")
M(reg, r"""
public static java.util.List all() {
  return new java.util.ArrayList(PETS.values());
}""")
# the pet is gone for good: memory + a GONE line (the ghost sweep never looks for it again)
M(reg, r"""
public static void forget(@PKG@.PpPet p, String why) {
  if (p == null || p.gone) return;
  p.gone = true;
  p.goneWhy = why;
  PETS.remove(p.uuid);
  @PKG@.PpFile.append("GONE " + p.uuid + " " + why);
  @PKG@.PpLog.info("GONE " + p.label + " (" + p.uuid + "): " + why);
}""")
# out of memory but NOT written GONE: its chunk may hold it -> the next start's ghost sweep removes it when the chunk loads
M(reg, r"""
public static void drop(@PKG@.PpPet p, String why) {
  if (p == null || p.gone) return;
  p.gone = true;
  p.goneWhy = why;
  PETS.remove(p.uuid);
  @PKG@.PpFile.addGhost(p.uuid, p.tag + " " + p.label, p.nonser, p.hasK ? @PKG@.PpFile.at(p.worldName, p.kx, p.kz) : null);
  @PKG@.PpLog.info("DROPPED " + p.label + " (" + p.uuid + "): " + why + " - not loaded now; on the ghost list until its chunk loads it (removed then) or its spot is seen loaded without it");
}""")

# =====================================================================================================================
# PpEngApi (interface) + PpEng: the engine seam (API == null in game = the real calls)
# =====================================================================================================================
api = pool.makeInterface(PKG + ".PpEngApi")
for sig in ("public abstract int roleIndex(String role);",
            "public abstract Object modelAsset(String id);",
            "public abstract @MDL@ scaled(Object asset, float scale);",
            "public abstract @PAIR@ spawn(@ST@ st, int role, @V3D@ pos, @R3F@ rot, @MDL@ m, @TRI@ pre);",
            "public abstract @REF@ refOf(@WLD@ w, java.util.UUID u);",
            "public abstract @ST@ store(@WLD@ w);",
            "public abstract @REF@ flockOf(@REF@ r, @CAC@ acc);",
            "public abstract void roleChange(@REF@ r, @ROLE@ role, int idx, @CAC@ acc);",
            "public abstract String mountMove(@REF@ pref, @PR@ pr, @CAC@ acc);",
            "public abstract void dismount(@CAC@ acc, @REF@ pref, @PLA@ p);",
            "public abstract void setAppearance(@NPC@ npc, @REF@ r, Object asset, @CAC@ acc);",
            "public abstract boolean resetMove(@REF@ pref, @CAC@ acc);"):
    M(api, sig)

eng = mk("PpEng")
F(eng, "public static @PKG@.PpEngApi API;")
M(eng, r"""
public static int roleIndex(String role) {
  if (API != null) return API.roleIndex(role);
  return @NPCP@.get().getIndex(role);
}""")
M(eng, r"""
public static Object modelAsset(String id) {
  if (API != null) return API.modelAsset(id);
  return @MDA@.getAssetMap().getAsset(id);
}""")
M(eng, r"""
public static @MDL@ scaled(Object asset, float scale) {
  if (API != null) return API.scaled(asset, scale);
  return @MDL@.createScaledModel((@MDA@) asset, scale);
}""")
# NPCPlugin.spawnEntity 7-argument form: the 6th argument is the PRE-add consumer (NPCEntity, Holder, Store), called before
# Store.addEntity (the 6-argument overload passes null there and its consumer runs AFTER the add)
M(eng, r"""
public static @PAIR@ spawn(@ST@ st, int role, @V3D@ pos, @R3F@ rot, @MDL@ m, @TRI@ pre) {
  if (API != null) return API.spawn(st, role, pos, rot, m, pre);
  return @NPCP@.get().spawnEntity(st, role, pos, rot, m, pre, null);
}""")
M(eng, r"""
public static @REF@ refOf(@WLD@ w, java.util.UUID u) {
  if (API != null) return API.refOf(w, u);
  return w.getEntityStore().getRefFromUUID(u);
}""")
M(eng, r"""
public static @ST@ store(@WLD@ w) {
  if (API != null) return API.store(w);
  return w.getEntityStore().getStore();
}""")
M(eng, r"""
public static @REF@ flockOf(@REF@ r, @CAC@ acc) {
  if (API != null) return API.flockOf(r, acc);
  return @FLP@.getFlockReference(r, acc);
}""")
# vanilla ActionMount.execute: RoleChangeSystem.requestRoleChange(ref, role, emptyRoleIndex, false, null, null, accessor)
M(eng, r"""
public static void roleChange(@REF@ r, @ROLE@ role, int idx, @CAC@ acc) {
  if (API != null) { API.roleChange(r, role, idx, acc); return; }
  @RCS@.requestRoleChange(r, role, idx, false, (String) null, (String) null, acc);
}""")
# vanilla ActionMount.execute: the rider's movement = MovementConfig "Mount" (setDefaultSettings + applyDefaultSettings + update)
M(eng, r"""
public static String mountMove(@REF@ pref, @PR@ pr, @CAC@ acc) {
  if (API != null) return API.mountMove(pref, pr, acc);
  @MVC@ cfg = (@MVC@) @MVC@.getAssetMap().getAsset("%s");
  if (cfg == null) return "no '%s' movement config";
  @MVM@ mm = (@MVM@) acc.getComponent(pref, @MVM@.getComponentType());
  @PHV@ pv = (@PHV@) acc.getComponent(pref, @PHV@.getComponentType());
  @PLA@ p = (@PLA@) acc.getComponent(pref, @PLA@.getComponentType());
  if (mm == null || p == null) return "no MovementManager / Player on you";
  mm.setDefaultSettings(cfg, pv, p.getGameMode());
  mm.applyDefaultSettings();
  mm.update(pr.getPacketHandler());
  return "";
}""" % (MOUNT_MOVE, MOUNT_MOVE))
# fix round: undo mountMove when the code mount never took (vanilla MountPlugin.resetOriginalPlayerMovementSettings ends in this same
# MovementManager.resetDefaultsAndUpdate(ref, accessor); we skip its DismountNPC packet - there is no mount to leave)
M(eng, r"""
public static boolean resetMove(@REF@ pref, @CAC@ acc) {
  if (API != null) return API.resetMove(pref, acc);
  @MVM@ mm = (@MVM@) acc.getComponent(pref, @MVM@.getComponentType());
  if (mm == null) return false;
  mm.resetDefaultsAndUpdate(pref, acc);
  return true;
}""")
M(eng, r"""
public static void dismount(@CAC@ acc, @REF@ pref, @PLA@ p) {
  if (API != null) { API.dismount(acc, pref, p); return; }
  @MTP@.checkDismountNpc(acc, pref, p);
}""")
M(eng, r"""
public static void setAppearance(@NPC@ npc, @REF@ r, Object asset, @CAC@ acc) {
  if (API != null) { API.setAppearance(npc, r, asset, acc); return; }
  npc.setAppearance(r, (@MDA@) asset, acc);
}""")

# =====================================================================================================================
# PpPre: NPCPlugin.spawnEntity's pre-add consumer (NPCEntity, Holder, Store): Invulnerable (ensure, like RoleBuilderSystem for an
# Invulnerable role) + NonSerialized (vanilla EntitySpawnPage preview: EntityStore.REGISTRY.getNonSerializedComponentType(), NonSerialized.get())
# =====================================================================================================================
pre = mk("PpPre")
pre.addInterface(pool.get(T["TRI"]))
F(pre, "public boolean invul;")
F(pre, "public boolean nonser;")
F(pre, "public int calls;")
C(pre, "public PpPre(boolean invul, boolean nonser) { this.invul = invul; this.nonser = nonser; this.calls = 0; }")
M(pre, r"""
public void accept(Object npc, Object holder, Object store) {
  this.calls = this.calls + 1;
  @HOL@ h = (@HOL@) holder;
  if (this.invul) h.ensureComponent(@INV@.getComponentType());
  if (this.nonser) h.addComponent(@EST@.REGISTRY.getNonSerializedComponentType(), @NSER@.get());
}""")

# =====================================================================================================================
# PpCheck: engine reads used by every probe (all guarded; "?" / -1 / null when unreadable)
# =====================================================================================================================
chk = mk("PpCheck")
M(chk, r"""
public static double[] pos(@CAC@ acc, @REF@ r) {
  try {
    if (r == null || !r.isValid()) return null;
    @TC@ tc = (@TC@) acc.getComponent(r, @TC@.getComponentType());
    if (tc == null) return null;
    @V3D@ p = tc.getPosition();
    return new double[] { p.x, p.y, p.z };
  } catch (Throwable t) { return null; }
}""")
M(chk, r"""
public static String modelText(@CAC@ acc, @REF@ r) {
  try {
    @MC@ m = (@MC@) acc.getComponent(r, @MC@.getComponentType());
    if (m == null || m.getModel() == null) return "none";
    return m.getModel().getModelAssetId() + " x" + m.getModel().getScale();
  } catch (Throwable t) { return "? (" + t + ")"; }
}""")
M(chk, r"""
public static boolean modelIs(@CAC@ acc, @REF@ r, String id, float s) {
  try {
    @MC@ m = (@MC@) acc.getComponent(r, @MC@.getComponentType());
    if (m == null || m.getModel() == null) return false;
    return id.equals(m.getModel().getModelAssetId()) && @PKG@.PpLogic.scaleIs(m.getModel().getScale(), s);
  } catch (Throwable t) { return false; }
}""")
M(chk, r"""
public static String boxText(@BOX@ b) {
  if (b == null) return "none";
  return @PKG@.PpLogic.f2(b.width()) + " x " + @PKG@.PpLogic.f2(b.height()) + " x " + @PKG@.PpLogic.f2(b.depth());
}""")
M(chk, r"""
public static String hitbox(@CAC@ acc, @REF@ r) {
  try {
    @BBX@ b = (@BBX@) acc.getComponent(r, @BBX@.getComponentType());
    return b == null ? "none" : boxText(b.getBoundingBox());
  } catch (Throwable t) { return "? (" + t + ")"; }
}""")
M(chk, r"""
public static float health(@CAC@ acc, @REF@ r) {
  try {
    @ESM@ m = (@ESM@) acc.getComponent(r, @ESM@.getComponentType());
    if (m == null) return -1.0f;
    @ESV@ v = m.get(@DST@.getHealth());
    return v == null ? -1.0f : v.get();
  } catch (Throwable t) { return -1.0f; }
}""")
M(chk, r"""
public static String roleOf(@CAC@ acc, @REF@ r) {
  try {
    Object e = acc.getComponent(r, @NPC@.getComponentType());
    if (e instanceof @NPC@) return ((@NPC@) e).getRoleName();
    if (acc.getComponent(r, @PR@.getComponentType()) != null) return "a player";
    return "?";
  } catch (Throwable t) { return "?"; }
}""")
M(chk, r"""
public static String nameplate(@CAC@ acc, @REF@ r) {
  try {
    @NPL@ n = (@NPL@) acc.getComponent(r, @NPL@.getComponentType());
    return n == null ? "none" : n.getText();
  } catch (Throwable t) { return "?"; }
}""")
M(chk, r"""
public static int netId(@CAC@ acc, @REF@ r) {
  try {
    @NID@ n = (@NID@) acc.getComponent(r, @NID@.getComponentType());
    return n == null ? 0 : n.getId();
  } catch (Throwable t) { return 0; }
}""")
M(chk, r"""
public static boolean invulnerable(@CAC@ acc, @REF@ r) {
  try { return acc.getComponent(r, @INV@.getComponentType()) != null; } catch (Throwable t) { return false; }
}""")
M(chk, r"""
public static Object bridge(String key) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (!(b instanceof java.util.Map)) return null;
    return ((java.util.Map) b).get(key);
  } catch (Throwable t) { return null; }
}""")
# SkyyMobs' mob:fn:info (Object[]{world, uuid} -> Object[]{level, ...} or null). "SKIP" when SkyyMobs is not on the bridge.
M(chk, r"""
public static String mobInfo(@PKG@.PpPet p) {
  Object f = bridge("mob:fn:info");
  if (!(f instanceof java.util.function.Function)) return "SKIP";
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { p.worldName, java.util.UUID.fromString(p.uuid) });
    if (r == null) return "";
    if (r instanceof Object[] && ((Object[]) r).length > 0) return "level " + ((Object[]) r)[0];
    return String.valueOf(r);
  } catch (Throwable t) { return "error " + t; }
}""")
M(chk, r"""
public static @WLD@ worldOf(@CAC@ acc) {
  try {
    if (!(acc instanceof @ST@)) return null;
    Object ext = ((@ST@) acc).getExternalData();
    return ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
  } catch (Throwable t) { return null; }
}""")
M(chk, r"""
public static @REF@ live(@PKG@.PpPet p) {
  if (p.ref != null && p.ref.isValid()) return p.ref;
  if (p.world == null) return null;
  try {
    @REF@ r = @PKG@.PpEng.refOf(p.world, java.util.UUID.fromString(p.uuid));
    if (r != null && r.isValid()) { p.ref = r; return r; }
  } catch (Throwable t) { }
  return null;
}""")
# {feet x, y, z, facing x, facing z} of the player (facing = HeadRotation's horizontal axis, south when unreadable)
M(chk, r"""
public static double[] where(@CAC@ acc, @REF@ ref) {
  try {
    @TC@ tc = (@TC@) acc.getComponent(ref, @TC@.getComponentType());
    if (tc == null) return null;
    @V3D@ p = tc.getPosition();
    int fx = 0; int fz = 1;
    @HR@ hr = (@HR@) acc.getComponent(ref, @HR@.getComponentType());
    if (hr != null) {
      @V3I@ d = hr.getHorizontalAxisDirection();
      if (d != null && (d.x != 0 || d.z != 0)) { fx = d.x; fz = d.z; }
    }
    return new double[] { p.x, p.y, p.z, (double) fx, (double) fz };
  } catch (Throwable t) { @PKG@.PpLog.warn("position unreadable: " + t); return null; }
}""")

# =====================================================================================================================
# PpSpawn: one probe pet = vanilla role + vanilla model by id at our scale; name + nameplate; tracked; SPAWN line
# =====================================================================================================================
spn = mk("PpSpawn")
F(spn, "public static final String ERR = \"@COLERR@\";")
M(spn, r"""
public static void name(@CAC@ acc, @REF@ r, String n) {
  @MSG@ m = @MSG@.raw(n);
  acc.putComponent(r, @DNC@.getComponentType(), new @DNC@(m));
  acc.putComponent(r, @PDN@.getComponentType(), new @PDN@(m));
  acc.putComponent(r, @NPL@.getComponentType(), new @NPL@(n));
}""")
M(spn, r"""
public static @PKG@.PpPet spawn(@ST@ st, @WLD@ w, @PR@ pr, String tag, String label, String role, String model, float scale, String vbox, double x, double y, double z, double fx, double fz, boolean invul, boolean nonser, int mode) {
  String P = @PKG@.PpLogic.up(tag);
  if (@PKG@.PpReg.PETS.size() >= @PKG@.PpReg.MAX) { @PKG@.PpLog.tell(pr, "Already " + @PKG@.PpReg.MAX + " probe pets - /petprobe clear first.", ERR); return null; }
  int ri = -1;
  try { ri = @PKG@.PpEng.roleIndex(role); } catch (Throwable t) { ri = -1; }
  if (ri < 0) { @PKG@.PpLog.result(pr, P, 0, label + ": role " + role + " is not spawnable on this server (NPCPlugin index " + ri + ")"); return null; }
  Object a = null;
  try { a = @PKG@.PpEng.modelAsset(model); } catch (Throwable t) { a = null; }
  if (a == null) { @PKG@.PpLog.result(pr, P, 0, label + ": model " + model + " is not loaded"); return null; }
  @MDL@ m = null;
  try { m = @PKG@.PpEng.scaled(a, scale); } catch (Throwable t) { @PKG@.PpLog.warn("scaled model " + model + " x" + scale + " failed: " + t); }
  if (m == null) { @PKG@.PpLog.result(pr, P, 0, label + ": Model.createScaledModel(" + model + ", " + scale + ") gave nothing"); return null; }
  @R3F@ rot = new @R3F@();
  rot.setYaw(@PKG@.PpLogic.yawToward(fx - x, fz - z));
  @PKG@.PpPre pc = new @PKG@.PpPre(invul, nonser);
  @PAIR@ pair = null;
  try { pair = @PKG@.PpEng.spawn(st, ri, new @V3D@(x, y, z), rot, m, pc); } catch (Throwable t) { @PKG@.PpLog.result(pr, P, 0, label + ": spawnEntity threw " + t); return null; }
  @REF@ r = pair == null ? null : (@REF@) pair.first();
  if (r == null || !r.isValid()) { @PKG@.PpLog.result(pr, P, 0, label + ": NPCPlugin.spawnEntity gave no entity (role " + role + ")"); return null; }
  java.util.UUID u = @PKG@.PpReg.uuidOf(st, r);
  if (u == null) {
    try { st.removeEntity(r, @RR@.REMOVE); } catch (Throwable t) { }
    @PKG@.PpLog.result(pr, P, 0, label + ": the spawned entity has no UUID - removed again");
    return null;
  }
  try { name(st, r, label); } catch (Throwable t) { @PKG@.PpLog.warn("naming " + label + " failed: " + t); }
  @PKG@.PpPet p = new @PKG@.PpPet();
  p.uuid = u.toString(); p.ref = r; p.world = w; p.worldName = w == null ? "?" : w.getName();
  p.owner = pr.getUuid(); p.ownerName = pr.getUsername(); p.pr = pr;
  p.tag = tag; p.label = label; p.role = role; p.roleIdx = ri; p.model = model; p.scale = scale;
  @BOX@ mb = null;
  try { mb = m.getBoundingBox(); } catch (Throwable t) { mb = null; }
  p.vbox = mb == null ? vbox : @PKG@.PpCheck.boxText(mb);
  p.nonser = nonser; p.invul = invul; p.mode = mode;
  p.netId = @PKG@.PpCheck.netId(st, r);
  p.t0 = System.currentTimeMillis();
  p.kx = x; p.kz = z; p.hasK = true;
  @PKG@.PpReg.PETS.put(p.uuid, p);
  @PKG@.PpFile.append("SPAWN " + p.uuid + " nonser=" + nonser + " at=" + @PKG@.PpFile.at(p.worldName, x, z) + " " + tag + " " + label);
  @PKG@.PpLog.info("SPAWN " + label + ": role " + role + " (index " + ri + "), model " + model + " x" + scale + " (scaled box " + p.vbox + "), invulnerable " + invul + ", NonSerialized " + nonser + ", pre-add consumer ran " + pc.calls + "x, at " + @PKG@.PpLogic.f1(x) + " " + @PKG@.PpLogic.f1(y) + " " + @PKG@.PpLogic.f1(z) + " in " + p.worldName + " (entity " + p.uuid + ")");
  return p;
}""")
# a row of pets ahead of the player: roles / models / scales / labels / vanilla boxes; answers how many spawned
M(spn, r"""
public static int row(@ST@ st, @WLD@ w, @PR@ pr, double[] wh, String tag, String[] roles, String[] models, float[] scales, String[] labels, String[] vbox, double ahead, double gap, boolean invul, boolean nonser, int mode, java.util.List out) {
  int n = 0;
  for (int i = 0; i < roles.length; i++) {
    double[] s = @PKG@.PpLogic.slot(i, roles.length, wh[0], wh[2], (int) wh[3], (int) wh[4], ahead, gap);
    @PKG@.PpPet p = spawn(st, w, pr, tag, labels[i], roles[i], models[i], scales[i], vbox[i], s[0], wh[1], s[1], wh[0], wh[2], invul, nonser, mode);
    if (p != null) { n++; if (out != null) out.add(p); }
  }
  return n;
}""")

# =====================================================================================================================
# PpRemove: remove one pet on ITS world thread (logout / world change / shutdown / clear in another world)
# =====================================================================================================================
rmv = mk("PpRemove")
rmv.addInterface(pool.get("java.lang.Runnable"))
F(rmv, "public @PKG@.PpPet p;")
F(rmv, "public String why;")
C(rmv, "public PpRemove(@PKG@.PpPet p, String why) { this.p = p; this.why = why; }")
# when the owner rides this pet, dismount first (MountPlugin.checkDismountNpc, what /dismount's NPC path ends in)
M(rmv, r"""
public static void unride(@ST@ st, @PKG@.PpPet p) {
  try {
    if (!p.mount || p.pr == null) return;
    @REF@ o = p.pr.getReference();
    if (o == null || !o.isValid()) return;
    @PLA@ pl = (@PLA@) st.getComponent(o, @PLA@.getComponentType());
    if (pl != null && p.netId != 0 && pl.getMountEntityId() == p.netId) { p.moveAt = 0L; @PKG@.PpEng.dismount(st, o, pl); @PKG@.PpLog.info("dismounted " + p.ownerName + " from " + p.label + " before removing it"); }
    else if (p.moveAt > 0L) { p.moveAt = 0L; boolean ok = @PKG@.PpEng.resetMove(o, st); @PKG@.PpLog.info("the code mount on " + p.label + " never took: " + p.ownerName + "'s movement reset to normal (" + ok + ")"); }
  } catch (Throwable t) { @PKG@.PpLog.warn("dismount before removing " + p.label + " failed: " + t); }
}""")
M(rmv, r"""
public static boolean now(@ST@ st, @PKG@.PpPet p, String why) {
  if (p == null || p.gone) return false;
  unride(st, p);
  @REF@ r = @PKG@.PpCheck.live(p);
  if (r == null) { @PKG@.PpReg.drop(p, why); return false; }
  p.removing = true;
  try { st.removeEntity(r, @RR@.REMOVE); } catch (Throwable t) { p.removing = false; @PKG@.PpLog.warn("removing " + p.label + " failed: " + t); @PKG@.PpReg.drop(p, why + " (remove failed)"); return false; }
  @PKG@.PpReg.forget(p, why);
  return true;
}""")
M(rmv, r"""
public void run() {
  try {
    if (this.p == null || this.p.gone) return;
    @ST@ st = this.p.world == null ? null : @PKG@.PpEng.store(this.p.world);
    if (st == null) { @PKG@.PpReg.drop(this.p, this.why + " (no world store)"); return; }
    now(st, this.p, this.why);
  } catch (Throwable t) { @PKG@.PpLog.warn("removal job for " + (this.p == null ? "?" : this.p.label) + " failed: " + t); }
}""")
# queue a removal on the pet's world thread (World.execute); a pet with no world is dropped (memory only)
M(rmv, r"""
public static boolean queue(@PKG@.PpPet p, String why) {
  if (p == null || p.gone || p.queued) return false;
  p.queued = true;
  if (p.world == null) { @PKG@.PpReg.drop(p, why + " (no world)"); return false; }
  try { p.world.execute(new @PKG@.PpRemove(p, why)); return true; }
  catch (Throwable t) { @PKG@.PpReg.drop(p, why + " (world would not take the job: " + t + ")"); return false; }
}""")
# in a ticking / event system: removal through the CommandBuffer (store is processing)
M(rmv, r"""
public static boolean viaBuffer(@CB@ cb, @PKG@.PpPet p, String why) {
  if (p == null || p.gone) return false;
  @REF@ r = @PKG@.PpCheck.live(p);
  if (r == null) { @PKG@.PpReg.drop(p, why); return false; }
  p.removing = true;
  try { cb.removeEntity(r, @RR@.REMOVE); } catch (Throwable t) { p.removing = false; @PKG@.PpLog.warn("removing " + p.label + " failed: " + t); return false; }
  @PKG@.PpReg.forget(p, why);
  return true;
}""")

# =====================================================================================================================
# PpFollow: per-second follow sampling (P1 / P3), our fallback teleport (> 24 blocks for 2 s), our own steering (P3 own, every tick)
# =====================================================================================================================
fol = mk("PpFollow")
# the vanilla BodyMotionTeleport way: accessor.<add/put>Component(ref, Teleport, Teleport.createExact(pos, rot))
M(fol, r"""
public static void teleport(@CAC@ acc, @REF@ r, double x, double y, double z, float yaw) {
  @R3F@ rot = new @R3F@();
  rot.setYaw(yaw);
  acc.putComponent(r, @TEL@.getComponentType(), @TEL@.createExact(new @V3D@(x, y, z), rot));
}""")
M(fol, r"""
public static void sample(@CAC@ acc, @PKG@.PpPet p, @REF@ r, double[] pp, double[] op, @PR@ pr) {
  double d = @PKG@.PpLogic.dist(pp[0], pp[1], pp[2], op[0], op[1], op[2]);
  p.secs = p.secs + 1;
  p.sumD = p.sumD + d;
  if (d <= 8.0) p.near = p.near + 1;
  if (d > p.maxD) p.maxD = d;
  if (p.hasLast) {
    double mv = @PKG@.PpLogic.dist(pp[0], pp[1], pp[2], p.lx, p.ly, p.lz);
    if (mv > @PKG@.PpLogic.JUMP && !p.justTele) {
      p.jumps = p.jumps + 1;
      @PKG@.PpLog.result(pr, @PKG@.PpLogic.up(p.tag), -1, p.label + ": the role TELEPORTED it (" + @PKG@.PpLogic.f1(mv) + " blocks in 1 s, now " + @PKG@.PpLogic.f1(d) + " from you) - vanilla teleport-when-far works");
    }
  }
  p.justTele = false;
  p.lx = pp[0]; p.ly = pp[1]; p.lz = pp[2]; p.hasLast = true;
  if (p.mode >= 1 && d > @PKG@.PpLogic.TELE_FAR) {
    p.far = p.far + 1;
    if (p.far >= 2 || p.mode == 2) {
      teleport(acc, r, op[0] + 1.5, op[1], op[2] + 1.5, @PKG@.PpLogic.yawToward(-1.5, -1.5));
      p.ours = p.ours + 1; p.justTele = true; p.far = 0;
      @PKG@.PpLog.info("FOLLOW " + p.label + ": " + @PKG@.PpLogic.f1(d) + " blocks away for 2 s -> OUR teleport next to " + p.ownerName + " (#" + p.ours + ")");
    }
  } else p.far = 0;
}""")
# P3 own: one step per tick toward the owner (stop at 3), yaw facing the owner, height eased toward the owner's
M(fol, r"""
public static boolean steer(@CAC@ acc, @PKG@.PpPet p, double[] op, float dt) {
  @REF@ r = @PKG@.PpCheck.live(p);
  if (r == null) return false;
  double[] pp = @PKG@.PpCheck.pos(acc, r);
  if (pp == null) return false;
  double d = @PKG@.PpLogic.dist(pp[0], 0.0, pp[2], op[0], 0.0, op[2]);
  if (d > @PKG@.PpLogic.TELE_FAR || d <= @PKG@.PpLogic.STOP) return false;
  double mx = @PKG@.PpLogic.OWN_SPEED * (double) dt;
  double[] s = @PKG@.PpLogic.step(pp[0], pp[2], op[0], op[2], mx, @PKG@.PpLogic.STOP);
  double ny = pp[1] + @PKG@.PpLogic.clamp(op[1] - pp[1], -mx, mx);
  teleport(acc, r, s[0], ny, s[1], @PKG@.PpLogic.yawToward(op[0] - s[0], op[2] - s[1]));
  p.steps = p.steps + 1;
  return true;
}""")
M(fol, r"""
public static String summary(@PKG@.PpPet p) {
  double avg = p.secs == 0 ? 0.0 : p.sumD / p.secs;
  return p.label + ": " + p.secs + " s sampled, average " + @PKG@.PpLogic.f1(avg) + " blocks from you, max " + @PKG@.PpLogic.f1(p.maxD) + ", within 8 blocks " + p.near + "/" + p.secs + " s, role teleports seen " + p.jumps + ", our teleports " + p.ours + (p.mode == 2 ? ", our steering steps " + p.steps : "");
}""")

# =====================================================================================================================
# PpMount: P10 - riding read back every second; OUR code mount (the vanilla ActionMount steps)
# =====================================================================================================================
mnt = mk("PpMount")
M(mnt, r"""
public static String mountInfo(@CAC@ acc, @REF@ r) {
  try {
    @MNT@ c = (@MNT@) acc.getComponent(r, @MNT@.getComponentType());
    if (c == null) return "no NPCMountComponent";
    @PR@ o = c.getOwnerPlayerRef();
    return "NPCMountComponent owner " + (o == null ? "none" : o.getUsername()) + ", anchor " + @PKG@.PpLogic.f2(c.getAnchorX()) + " " + @PKG@.PpLogic.f2(c.getAnchorY()) + " " + @PKG@.PpLogic.f2(c.getAnchorZ()) + ", original role index " + c.getOriginalRoleIndex();
  } catch (Throwable t) { return "? (" + t + ")"; }
}""")
# the mount role's vanilla MountAnchorY (desk-checked per P10 role at build time; 1.6 = Tamed_Horse for anything else)
M(mnt, r"""
public static float anchorOf(String role) {
%s
  return %sf;
}""" % (chr(10).join('  if ("%s".equals(role)) return %sf;' % (k, repr(v)) for k, v in sorted(MOUNT_Y.items())), repr(MOUNT_ANCHOR_Y)))
F(mnt, "public static final long MOVE_WAIT = 3000L;")
M(mnt, r"""
public static void watch(@CAC@ acc, @REF@ pref, @PR@ pr, @PKG@.PpPet p, @REF@ r) {
  @PLA@ pl = (@PLA@) acc.getComponent(pref, @PLA@.getComponentType());
  if (pl == null) return;
  if (p.netId == 0) p.netId = @PKG@.PpCheck.netId(acc, r);
  int mid = pl.getMountEntityId();
  boolean riding = mid != 0 && mid == p.netId;
  if (riding) p.moveAt = 0L;
  else if (p.moveAt > 0L && System.currentTimeMillis() - p.moveAt >= MOVE_WAIT) {
    p.moveAt = 0L;
    boolean ok = @PKG@.PpEng.resetMove(pref, acc);
    @PKG@.PpLog.result(pr, "P10", 0, "our code mount on " + p.label + " did not take within 3 s (you are not riding it) - your movement was reset to normal (" + ok + "); " + mountInfo(acc, r));
  }
  if (riding == p.riding) return;
  p.riding = riding;
  if (riding) @PKG@.PpLog.result(pr, "P10", 1, "you RIDE " + p.label + " (scale " + p.scale + ", via " + (p.codeMount ? "our code mount" : "F = the vanilla mount") + "); " + mountInfo(acc, r) + " - LOOK: does the seat sit right at this size?");
  else @PKG@.PpLog.result(pr, "P10", -1, "you got off " + p.label + " (mount entity id now " + mid + "); " + mountInfo(acc, r));
}""")
# the vanilla ActionMount.execute steps on the nearest probe mount within 8 blocks: NPCMountComponent (owner, anchor 1.6 x scale, original
# role index) put in ONE go (NPCMountSystems$OnAdd reads the owner when it sends MountNPC), role -> Empty_Role, movement 'Mount'
M(mnt, r"""
public static String ride(@ST@ st, @REF@ pref, @PR@ pr) {
  double[] op = @PKG@.PpCheck.pos(st, pref);
  if (op == null) return "your position is unreadable";
  @PKG@.PpPet best = null; double bd = 8.0; @REF@ br = null;
  java.util.List l = @PKG@.PpReg.ofOwner(pr.getUuid());
  for (int i = 0; i < l.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) l.get(i);
    if (!p.mount || p.riding) continue;
    @REF@ r = @PKG@.PpCheck.live(p);
    double[] pp = @PKG@.PpCheck.pos(st, r);
    if (pp == null) continue;
    double d = @PKG@.PpLogic.dist(pp[0], pp[1], pp[2], op[0], op[1], op[2]);
    if (d <= bd) { bd = d; best = p; br = r; }
  }
  if (best == null) return "no probe mount within 8 blocks - /petprobe p10 first, then stand next to one";
  if (st.getComponent(br, @MNT@.getComponentType()) != null) return best.label + " already has an NPCMountComponent (someone rides it?)";
  @NPC@ npc = (@NPC@) st.getComponent(br, @NPC@.getComponentType());
  if (npc == null) return best.label + " has no NPCEntity";
  int empty = @PKG@.PpEng.roleIndex("%s");
  @MNT@ c = new @MNT@();
  c.setOriginalRoleIndex(@PKG@.PpEng.roleIndex(npc.getRoleName()));
  c.setOwnerPlayerRef(pr);
  float ay = anchorOf(best.role) * best.scale;
  best.anchorY = ay;
  c.setAnchor(0.0f, ay, 0.0f);
  st.putComponent(br, @MNT@.getComponentType(), c);
  @PKG@.PpEng.roleChange(br, npc.getRole(), empty, st);
  String mv = @PKG@.PpEng.mountMove(pref, pr, st);
  best.codeMount = true;
  if (mv.length() == 0) best.moveAt = System.currentTimeMillis();
  return "+code mount sent on " + best.label + " (" + @PKG@.PpLogic.f1(bd) + " blocks): NPCMountComponent owner " + pr.getUsername() + ", anchor Y " + @PKG@.PpLogic.f2(ay) + " (" + best.role + " " + anchorOf(best.role) + " x " + best.scale + "), role -> Empty_Role (index " + empty + "), movement " + (mv.length() == 0 ? "'Mount' applied (reset again if you do not ride it within 3 s)" : "NOT applied: " + mv) + " - the next second says whether you ride it";
}""" % (EMPTY_ROLE,))

# =====================================================================================================================
# PpProbe: the per-second steps of every probe pet (owner's world thread, from PpTick)
# =====================================================================================================================
prb = mk("PpProbe")
F(prb, "public static final String P4_ADULT = %s;" % json.dumps(P4_ADULT))
# spawn check (1 s): did the entity keep OUR model + scale? hitbox, nameplate, invulnerable
M(prb, r"""
public static void firstCheck(@CAC@ acc, @PR@ pr, @PKG@.PpPet p, @REF@ r) {
  boolean ok = @PKG@.PpCheck.modelIs(acc, r, p.model, p.scale);
  String probe = p.tag.equals("p2") ? "P2" : (p.tag.equals("p1") ? "P1" : @PKG@.PpLogic.up(p.tag) + " spawn");
  p.lastRead = @PKG@.PpCheck.modelText(acc, r);
  @PKG@.PpLog.result(pr, probe, ok ? 1 : 0, p.label + ": model now " + p.lastRead + " (asked " + p.model + " x" + p.scale + ", role " + p.role + "), hitbox " + @PKG@.PpCheck.hitbox(acc, r) + " (scaled model box " + p.vbox + "), nameplate '" + @PKG@.PpCheck.nameplate(acc, r) + "', invulnerable " + @PKG@.PpCheck.invulnerable(acc, r) + ", health " + @PKG@.PpLogic.f1(@PKG@.PpCheck.health(acc, r)));
}""")
# P8 (3 s after every spawn): SkyyMobs must give probe pets no level; the p8 control (vanilla hostile Fox role) is expected levelled
M(prb, r"""
public static void mobCheck(@PR@ pr, @PKG@.PpPet p) {
  String mi = @PKG@.PpCheck.mobInfo(p);
  if (mi.equals("SKIP")) { if (p.tag.equals("p8")) @PKG@.PpLog.result(pr, "P8", -1, "SkyyMobs is not on this server (no mob:fn:info) - nothing to test"); return; }
  if (p.tag.equals("p8")) { @PKG@.PpLog.result(pr, "P8", -1, "CONTROL " + p.label + ": " + (mi.length() == 0 ? "NOT levelled by SkyyMobs" : "SkyyMobs gave it " + mi + " - a pet on a vanilla hostile role gets levelled, so SkyyPets needs its own roles (or a SkyyMobs exclude)")); return; }
  @PKG@.PpLog.result(pr, "P8", mi.length() == 0 ? 1 : 0, p.label + " (role " + p.role + "): " + (mi.length() == 0 ? "no SkyyMobs level" : "SkyyMobs gave it " + mi));
}""")
# P4 steps (4 / 8 / 12 / 16 / 20 s): each step reads back the one before
M(prb, r"""
public static void growStep(@CAC@ acc, @PR@ pr, @PKG@.PpPet p, @REF@ r, int st) {
  String before = @PKG@.PpCheck.modelText(acc, r);
  Object e = acc.getComponent(r, @NPC@.getComponentType());
  @NPC@ npc = e instanceof @NPC@ ? (@NPC@) e : null;
  if (st == 0) {
    @MDL@ m = @PKG@.PpEng.scaled(@PKG@.PpEng.modelAsset(p.model), 0.8f);
    acc.putComponent(r, @MC@.getComponentType(), new @MC@(m));
    acc.putComponent(r, @PM@.getComponentType(), new @PM@(m.toReference()));
    @PKG@.PpLog.result(pr, "P4", -1, "step A (new ModelComponent x0.8, was " + before + "): did the fox DOUBLE in size just now?");
  } else if (st == 1) {
    @PKG@.PpLog.result(pr, "P4", @PKG@.PpCheck.modelIs(acc, r, p.model, 0.8f) ? 1 : 0, "step A read back: " + before + " (want " + p.model + " x0.8)");
    if (npc == null) { @PKG@.PpLog.result(pr, "P4", 0, "step B: no NPCEntity"); return; }
    npc.setInitialModelScale(1.0f);
    @PKG@.PpEng.setAppearance(npc, r, @PKG@.PpEng.modelAsset(p.model), acc);
    @PKG@.PpLog.result(pr, "P4", -1, "step B (NPCEntity.setAppearance at initial scale 1.0): did it grow to full fox size?");
  } else if (st == 2) {
    @PKG@.PpLog.result(pr, "P4", -1, "step B read back: " + before + " (setAppearance uses the entity's initial scale: want x1.0)");
    acc.putComponent(r, @ESC@.getComponentType(), new @ESC@(1.5f));
    @PKG@.PpLog.result(pr, "P4", -1, "step C (EntityScaleComponent 1.5 on top): did it get BIGGER again (x1.5)?");
  } else if (st == 3) {
    @ESC@ sc = (@ESC@) acc.getComponent(r, @ESC@.getComponentType());
    @PKG@.PpLog.result(pr, "P4", -1, "step C read back: EntityScaleComponent " + (sc == null ? "none" : String.valueOf(sc.getScale())) + ", model " + before);
    if (npc == null) return;
    @PKG@.PpEng.setAppearance(npc, r, @PKG@.PpEng.modelAsset(P4_ADULT), acc);
    @PKG@.PpLog.result(pr, "P4", -1, "step D (setAppearance(" + P4_ADULT + ") = a baby -> adult style model swap): is it a wolf now?");
  } else if (st == 4) {
    @PKG@.PpLog.result(pr, "P4", -1, "step D read back: " + before + ". Done - tell us which steps (A, B, C, D) visibly changed it");
  }
}""")
# P6: is the pet in YOUR flock (FlockPlugin.getFlockReference of both)?
M(prb, r"""
public static void flockCheck(@CAC@ acc, @REF@ pref, @PR@ pr, @PKG@.PpPet p, @REF@ r, boolean last) {
  @REF@ pf = null; @REF@ of = null;
  try { pf = @PKG@.PpEng.flockOf(r, acc); } catch (Throwable t) { pf = null; }
  try { of = @PKG@.PpEng.flockOf(pref, acc); } catch (Throwable t) { of = null; }
  String mt = "?";
  try { @FLM@ fm = (@FLM@) acc.getComponent(r, @FLM@.getComponentType()); mt = fm == null ? "no FlockMembership" : String.valueOf(fm.getMembershipType()); } catch (Throwable t) { mt = "? " + t; }
  boolean ok = pf != null && pf.equals(of);
  if (ok || last) @PKG@.PpLog.result(pr, "P6", ok ? 1 : 0, p.label + (ok ? " is in YOUR flock" : " is NOT in your flock") + " after " + ((System.currentTimeMillis() - p.t0) / 1000L) + " s (pet flock " + (pf == null ? "none" : "set") + ", your flock " + (of == null ? "none" : "set") + ", membership " + mt + "; the role despawns it after " + @PKG@.PpReg.SUMMON_DESPAWN + " s)");
}""")
M(prb, r"""
public static void second(@CAC@ acc, @REF@ pref, @PR@ pr, @PKG@.PpPet p, double[] op) {
  long el = System.currentTimeMillis() - p.t0;
  @REF@ r = @PKG@.PpCheck.live(p);
  double[] pp = @PKG@.PpCheck.pos(acc, r);
  if (pp == null) {
    p.missing = p.missing + 1;
    if (p.missing == 3) @PKG@.PpLog.result(pr, @PKG@.PpLogic.up(p.tag), -1, p.label + " is not loaded / not found for 3 s (" + (el / 1000L) + " s after spawn; unloaded chunk, or the game removed it)");
    return;
  }
  p.missing = 0;
  p.kx = pp[0]; p.kz = pp[2]; p.hasK = true;
  if (p.mode >= 1 && op != null) @PKG@.PpFollow.sample(acc, p, r, pp, op, pr);
  if (!p.checked && el >= 1000L) { p.checked = true; firstCheck(acc, pr, p, r); }
  if (!p.mobChecked && el >= 3000L) { p.mobChecked = true; mobCheck(pr, p); }
  if (p.tag.equals("p2") && p.stage == 0 && el >= 6000L) {
    p.stage = 1;
    boolean ok = @PKG@.PpCheck.modelIs(acc, r, p.model, p.scale);
    @PKG@.PpLog.result(pr, "P2", ok ? 1 : 0, p.label + " after 6 s: model " + @PKG@.PpCheck.modelText(acc, r) + (ok ? " - the role KEPT the model we passed" : " - the role REPLACED our model"));
  }
  if (p.tag.equals("p1") && p.stage == 0 && el >= 20000L) { p.stage = 1; @PKG@.PpLog.result(pr, "P1", -1, @PKG@.PpFollow.summary(p) + " - LOOK: legs skating? nameplate readable? can you hit it?"); }
  if (p.tag.equals("p3") && p.stage < 6 && el >= (p.stage + 1) * 10000L) {
    p.stage = p.stage + 1;
    if (p.stage < 6) @PKG@.PpLog.info("P3 " + @PKG@.PpFollow.summary(p));
    else @PKG@.PpLog.result(pr, "P3", @PKG@.PpLogic.followOk(p.near, p.secs) ? 1 : 0, @PKG@.PpFollow.summary(p) + " (PASS = within 8 blocks 80 % of the time)");
  }
  if (p.tag.equals("p4") && p.stage < 5 && el >= (p.stage + 1) * 4000L) { growStep(acc, pr, p, r, p.stage); p.stage = p.stage + 1; }
  if (p.tag.equals("p6") && p.stage == 0 && el >= 2000L) { p.stage = 1; flockCheck(acc, pref, pr, p, r, false); }
  if (p.tag.equals("p6") && p.stage == 1 && el >= 5000L) { p.stage = 2; flockCheck(acc, pref, pr, p, r, true); }
  if (p.mount) @PKG@.PpMount.watch(acc, pref, pr, p, r);
}""")

# =====================================================================================================================
# PpLife: spec 2.2 lifecycle rows (owner died, profile switch, world change); logout is PpQuit
# =====================================================================================================================
life = mk("PpLife")
M(life, r"""
public static int removeHere(@CB@ cb, java.util.List l, @WLD@ w, String why) {
  int n = 0;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) l.get(i);
    if (p.gone) continue;
    if (p.world == w) { if (@PKG@.PpRemove.viaBuffer(cb, p, why)) n++; }
    else if (@PKG@.PpRemove.queue(p, why)) n++;
  }
  return n;
}""")
# true = this owner's pets were just removed (the caller stops)
M(life, r"""
public static boolean check(@CAC@ acc, @CB@ cb, @REF@ pref, @PR@ pr, @WLD@ w, java.util.List mine) {
  java.util.UUID o = pr.getUuid();
  boolean dead = false;
  try { dead = acc.getComponent(pref, @DTH@.getComponentType()) != null; } catch (Throwable t) { dead = false; }
  if (dead) {
    if (@PKG@.PpReg.DEAD.putIfAbsent(o, Boolean.TRUE) == null) {
      int n = removeHere(cb, mine, w, "owner died");
      @PKG@.PpLog.result(pr, "LIFE", -1, "you died: " + n + " probe pets removed (the spec hides pets while the owner is dead) - did they vanish?");
    }
    return true;
  }
  @PKG@.PpReg.DEAD.remove(o);
  Object e = @PKG@.PpCheck.bridge("profile:epoch:" + o);
  if (e != null) {
    Object last = @PKG@.PpReg.EPOCH.put(o, e);
    if (last != null && !last.equals(e)) {
      int n = removeHere(cb, mine, w, "profile switch");
      @PKG@.PpLog.result(pr, "LIFE", -1, "profile switch seen (epoch " + last + " -> " + e + "): " + n + " probe pets removed - did they vanish?");
      return true;
    }
  }
  int moved = 0;
  for (int i = 0; i < mine.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) mine.get(i);
    if (p.gone || p.queued || p.world == null || p.world == w) continue;
    if (@PKG@.PpRemove.queue(p, "owner left world " + p.worldName)) moved++;
  }
  if (moved > 0) @PKG@.PpLog.result(pr, "LIFE", -1, "you changed world (now " + (w == null ? "?" : w.getName()) + "): " + moved + " probe pets in the old world queued for removal on that world's thread - go back: are they gone?");
  return false;
}""")

# once a second per player while ghosts are listed: a ghost whose last known spot (same world) is within NEAR blocks of the player for
# NEAR_SECS seconds has its chunk loaded -> found = removed now; not found = confirmed gone (GONE line). A ghost with no known spot
# leaves only when its chunk loads it (added above).
M(life, r"""
public static int sweep(@CAC@ acc, @CB@ cb, @PR@ pr, @WLD@ w, double[] op) {
  if (@PKG@.PpFile.GHOSTS.isEmpty() || op == null || w == null) return 0;
  String wn = @PKG@.PpFile.wname(w.getName());
  int done = 0;
  java.util.Iterator it = new java.util.ArrayList(@PKG@.PpFile.GHOST_AT.entrySet()).iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String k = (String) e.getKey();
    String[] a = String.valueOf(e.getValue()).split(",");
    if (a.length != 3 || !a[0].equals(wn) || !@PKG@.PpFile.GHOSTS.containsKey(k)) continue;
    double x = 0.0; double z = 0.0;
    try { x = Double.parseDouble(a[1]); z = Double.parseDouble(a[2]); } catch (Throwable t) { continue; }
    int[] c = (int[]) @PKG@.PpFile.GHOST_NEAR.get(k);
    if (c == null) { c = new int[1]; @PKG@.PpFile.GHOST_NEAR.put(k, c); }
    if (Math.abs(op[0] - x) > @PKG@.PpFile.NEAR || Math.abs(op[2] - z) > @PKG@.PpFile.NEAR) { c[0] = 0; continue; }
    c[0] = c[0] + 1;
    if (c[0] < @PKG@.PpFile.NEAR_SECS) continue;
    Object info = @PKG@.PpFile.GHOSTS.get(k);
    @REF@ r = null;
    try { r = @PKG@.PpEng.refOf(w, java.util.UUID.fromString(k)); } catch (Throwable t) { r = null; }
    @PKG@.PpFile.removeGhost(k);
    if (r != null && r.isValid()) {
      cb.removeEntity(r, @RR@.REMOVE);
      @PKG@.PpFile.append("GONE " + k + " ghost found at its spot and removed");
      @PKG@.PpLog.tell(pr, "Probe ghost FOUND at " + e.getValue() + " and removed: " + info, @PKG@.PpLog.COL_INF);
    } else {
      @PKG@.PpFile.append("GONE " + k + " confirmed gone (its spot was loaded for " + @PKG@.PpFile.NEAR_SECS + " s without it)");
      @PKG@.PpLog.tell(pr, "Probe ghost confirmed gone (its spot " + e.getValue() + " was loaded without it): " + info, @PKG@.PpLog.COL_INF);
    }
    done++;
  }
  if (done > 0) @PKG@.PpLog.tell(pr, @PKG@.PpFile.GHOSTS.isEmpty() ? "No probe ghosts left - nothing of the probe is in a saved chunk; the mod is safe to remove once you are done." : @PKG@.PpFile.GHOSTS.size() + " probe ghosts left (/petprobe list shows where).", @PKG@.PpLog.COL_INF);
  return done;
}""")

# =====================================================================================================================
# PpTick: per player, every tick (world thread): own steering each tick; once a second lifecycle + every probe step
# =====================================================================================================================
tick = mk("PpTick", T["ETS"])
F(tick, "public static final java.util.concurrent.ConcurrentHashMap ACC = new java.util.concurrent.ConcurrentHashMap();")   # owner uuid -> double[1]
C(tick, "public PpTick() { super(); }")
M(tick, r"""
public @QRY@ getQuery() {
  return (@QRY@) @PLA@.getComponentType();
}""")
M(tick, r"""
public boolean isParallel(int a, int b) {
  return false;
}""")
M(tick, r"""
public static void run(float dt, @REF@ pref, @ST@ st, @CB@ cb) {
  if (pref == null || (@PKG@.PpReg.PETS.isEmpty() && @PKG@.PpFile.GHOSTS.isEmpty())) return;
  @PR@ pr = (@PR@) st.getComponent(pref, @PR@.getComponentType());
  if (pr == null) return;
  java.util.UUID o = pr.getUuid();
  java.util.List mine = @PKG@.PpReg.ofOwner(o);
  if (mine.isEmpty() && @PKG@.PpFile.GHOSTS.isEmpty()) return;
  @WLD@ w = @PKG@.PpCheck.worldOf(st);
  double[] op = @PKG@.PpCheck.pos(st, pref);
  if (op != null) {
    for (int i = 0; i < mine.size(); i++) {
      @PKG@.PpPet p = (@PKG@.PpPet) mine.get(i);
      if (p.mode == 2 && !p.gone && p.world == w) @PKG@.PpFollow.steer(cb, p, op, dt);
    }
  }
  double[] acc = (double[]) ACC.get(o);
  if (acc == null) { acc = new double[1]; ACC.put(o, acc); }
  acc[0] = acc[0] + dt;
  if (acc[0] < 1.0) return;
  acc[0] = 0.0;
  if (!@PKG@.PpFile.GHOSTS.isEmpty()) {
    try { @PKG@.PpLife.sweep(st, cb, pr, w, op); } catch (Throwable t) { @PKG@.PpLog.warnOnce("sweep:" + t.getClass().getName(), "ghost sweep failed: " + t); }
  }
  if (mine.isEmpty()) return;
  if (@PKG@.PpLife.check(st, cb, pref, pr, w, mine)) return;
  for (int i = 0; i < mine.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) mine.get(i);
    if (p.gone || p.world != w) continue;
    try { @PKG@.PpProbe.second(cb, pref, pr, p, op); }
    catch (Throwable t) { @PKG@.PpLog.warnOnce("probe:" + p.tag + ":" + t.getClass().getName(), "probe step " + p.tag + " failed: " + t); }
  }
}""")
M(tick, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CB@ cb) {
  try {
    if (@PKG@.PpReg.PETS.isEmpty() && @PKG@.PpFile.GHOSTS.isEmpty()) return;
    run(dt, chunk.getReferenceTo(idx), st, cb);
  } catch (Throwable t) { @PKG@.PpLog.warnOnce("tick:" + t.getClass().getName(), "probe tick failed: " + t); }
}""")

# =====================================================================================================================
# Damage: PpDmgFilter (filter group: P9 DOWN instead of death, P7 credit rewrite - fix round: ONLY on the P7 target pig ("p7t"), never a
# real mob / player; CREDIT resets on clear / stop). PpDmgInspect: P6 (and any non-P7 probe pet) - its first hit is a LOOK line naming
# the target (assist / defend) + PpDmgInspect (inspect group: every hit by or on a
# probe pet - P7 hits / kills, aggro on pets). ONE registerSystem per class.
# =====================================================================================================================
dflt = mk("PpDmgFilter", T["DES"])
C(dflt, "public PpDmgFilter() { super(); }")
M(dflt, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(dflt, "public @SG@ getGroup() { return @DMOD@.get().getFilterDamageGroup(); }")
M(dflt, r"""
public static @PKG@.PpPet attacker(@CAC@ acc, @DMG@ d) {
  @DSRC@ s = d.getSource();
  if (!(s instanceof @DENT@)) return null;
  return @PKG@.PpReg.petOf(acc, ((@DENT@) s).getRef());
}""")
M(dflt, r"""
public static void filter(@REF@ target, @ST@ st, @CB@ cb, @DMG@ d) {
  if (d.isCancelled()) return;
  @PKG@.PpPet tp = @PKG@.PpReg.petOf(st, target);
  if (tp != null && tp.down) {
    float hp = @PKG@.PpCheck.health(st, target);
    float amt = d.getAmount();
    if (hp >= 0.0f && amt >= hp) {
      d.setCancelled(true);
      d.setAmount(0.0f);
      boolean gone = @PKG@.PpRemove.viaBuffer(cb, tp, "DOWN (lethal hit cancelled)");
      @PKG@.PpLog.result(tp.pr, "P9", gone ? 1 : 0, tp.label + ": the lethal hit (" + @PKG@.PpLogic.f1(amt) + " vs " + @PKG@.PpLogic.f1(hp) + " health) was CANCELLED in the damage filter and the pet went DOWN (removed: " + gone + ") - no death animation, no drop? (LOOK)");
      return;
    }
    @PKG@.PpLog.result(tp.pr, "P9", -1, tp.label + " took a hit: " + @PKG@.PpLogic.f1(amt) + " damage, health " + @PKG@.PpLogic.f1(hp) + " -> " + @PKG@.PpLogic.f1(hp - amt) + " (not lethal yet - keep hitting)");
  }
  if (!@PKG@.PpReg.CREDIT) return;
  if (tp == null || !"p7t".equals(tp.tag)) return;
  @PKG@.PpPet ap = attacker(st, d);
  if (ap == null || !ap.fight || ap.pr == null) return;
  @REF@ o = ap.pr.getReference();
  if (o == null || !o.isValid()) return;
  d.setSource(new @DENT@(o));
  java.util.UUID tu = @PKG@.PpReg.uuidOf(st, target);
  if (tu != null) @PKG@.PpReg.REWRITE.put(tu.toString(), ap.label);
}""")
M(dflt, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ cb, @EV@ ev) {
  try {
    if (@PKG@.PpReg.PETS.isEmpty() || !(ev instanceof @DMG@)) return;
    filter(chunk.getReferenceTo(idx), st, cb, (@DMG@) ev);
  } catch (Throwable t) { @PKG@.PpLog.warnOnce("filter:" + t.getClass().getName(), "damage filter failed: " + t); }
}""")
dins = mk("PpDmgInspect", T["DES"])
C(dins, "public PpDmgInspect() { super(); }")
M(dins, "public @QRY@ getQuery() { return @QRY@.any(); }")
M(dins, "public @SG@ getGroup() { return @DMOD@.get().getInspectDamageGroup(); }")
M(dins, r"""
public static void inspect(@REF@ target, @ST@ st, @DMG@ d) {
  @PKG@.PpPet tp = @PKG@.PpReg.petOf(st, target);
  @DSRC@ s = d.getSource();
  @REF@ ar = s instanceof @DENT@ ? ((@DENT@) s).getRef() : null;
  if (tp != null) {
    tp.hitsTaken = tp.hitsTaken + 1;
    if (tp.hitsTaken <= 5 || tp.hitsTaken % 20 == 0) @PKG@.PpLog.info("HIT ON PET " + tp.label + " #" + tp.hitsTaken + ": " + @PKG@.PpLogic.f1(d.getAmount()) + " from " + (ar == null ? "no entity" : @PKG@.PpCheck.roleOf(st, ar)) + ", cancelled " + d.isCancelled() + ", invulnerable " + tp.invul);
  }
  java.util.UUID tu = @PKG@.PpReg.uuidOf(st, target);
  String rw = tu == null ? null : (String) @PKG@.PpReg.REWRITE.remove(tu.toString());
  @PKG@.PpPet ap = @PKG@.PpReg.petOf(st, ar);
  if (ap == null && rw == null) return;
  if (d.isCancelled()) return;
  float hp = @PKG@.PpCheck.health(st, target);
  boolean lethal = hp >= 0.0f && d.getAmount() >= hp;
  String who = ap != null ? ap.label : rw + " (source rewritten to " + @PKG@.PpCheck.roleOf(st, ar) + ")";
  if (ap != null) ap.hitsDealt = ap.hitsDealt + 1;
  @PR@ pr = ap != null ? ap.pr : null;
  if (pr == null && ar != null) { try { pr = (@PR@) st.getComponent(ar, @PR@.getComponentType()); } catch (Throwable t) { pr = null; } }
  String line = who + " hit " + @PKG@.PpCheck.roleOf(st, target) + " for " + @PKG@.PpLogic.f1(d.getAmount()) + " (health " + @PKG@.PpLogic.f1(hp) + ")";
  String probe = (ap == null || "p7".equals(ap.tag)) ? "P7" : @PKG@.PpLogic.up(ap.tag);
  if (!probe.equals("P7")) {
    if (ap.hitsDealt == 1 || lethal) @PKG@.PpLog.result(pr, probe, -1, (lethal ? "KILL: " : "ATTACK: ") + line + " - your summon picked this target by itself: was it hitting you / did you hit it first (defend / assist)?");
    else @PKG@.PpLog.info(probe + " HIT: " + line);
    return;
  }
  if (lethal) @PKG@.PpLog.result(pr, "P7", rw != null ? 1 : -1, "KILL: " + line + " - the killing blow's source is " + (rw != null ? "YOU (credit on): did you get Combat XP / the collection?" : "the PET (credit off): did you get Combat XP? (expected no)"));
  else @PKG@.PpLog.info("P7 HIT: " + line);
}""")
M(dins, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ cb, @EV@ ev) {
  try {
    if (@PKG@.PpReg.PETS.isEmpty() || !(ev instanceof @DMG@)) return;
    inspect(chunk.getReferenceTo(idx), st, (@DMG@) ev);
  } catch (Throwable t) { @PKG@.PpLog.warnOnce("inspect:" + t.getClass().getName(), "damage inspect failed: " + t); }
}""")

# =====================================================================================================================
# PpLoadSys: RefSystem on NPC entities - the ghost sweep (probe-log uuids removed when their chunk loads) + P5 unload / reload facts
# =====================================================================================================================
lds = mk("PpLoadSys", T["RSYS"])
C(lds, "public PpLoadSys() { super(); }")
M(lds, r"""
public @QRY@ getQuery() {
  return (@QRY@) @NPC@.getComponentType();
}""")
M(lds, r"""
public static void added(@REF@ ref, @ADR@ reason, @ST@ st, @CB@ cb) {
  if (@PKG@.PpReg.PETS.isEmpty() && @PKG@.PpFile.GHOSTS.isEmpty()) return;
  java.util.UUID u = @PKG@.PpReg.uuidOf(st, ref);
  if (u == null) return;
  String k = u.toString();
  Object g = @PKG@.PpFile.GHOSTS.get(k);
  if (g != null) {
    boolean ns = Boolean.TRUE.equals(@PKG@.PpFile.GHOST_NONSER.get(k));
    @PKG@.PpFile.removeGhost(k);
    cb.removeEntity(ref, @RR@.REMOVE);
    @PKG@.PpFile.append("GONE " + k + " ghost removed when its chunk loaded");
    @PKG@.PpLog.result(null, "P5", ns ? 0 : 1, "a probe pet that was not loaded (restart / clear / logout) came back: " + (ns ? "a NonSerialized one (" + g + ") - it WAS saved" : "the saved one, as expected (" + g + ")") + " -> removed now (the ghost sweep works; " + @PKG@.PpFile.GHOSTS.size() + " ghosts left)");
    return;
  }
  @PKG@.PpPet p = (@PKG@.PpPet) @PKG@.PpReg.PETS.get(k);
  if (p != null && reason == @ADR@.LOAD) {
    p.ref = ref;
    p.reloads = p.reloads + 1;
    @PKG@.PpLog.result(p.pr, "P5", p.nonser ? 0 : -1, p.label + " was LOADED back from its chunk" + (p.nonser ? " although it has NonSerialized - it WAS saved" : " (the saved control - expected)"));
  }
}""")
M(lds, r"""
public static void removed(@REF@ ref, @RR@ reason, @ST@ st) {
  if (@PKG@.PpReg.PETS.isEmpty()) return;
  @PKG@.PpPet p = @PKG@.PpReg.petOf(st, ref);
  if (p == null || p.gone || p.removing) return;
  long s = (System.currentTimeMillis() - p.t0) / 1000L;
  if (reason == @RR@.UNLOAD) {
    p.unloads = p.unloads + 1;
    double[] at = @PKG@.PpCheck.pos(st, ref);
    if (at != null) { p.kx = at[0]; p.kz = at[2]; p.hasK = true; }
    if (p.hasK) @PKG@.PpFile.append("WHERE " + p.uuid + " " + @PKG@.PpFile.at(p.worldName, p.kx, p.kz));
    @PKG@.PpLog.info("UNLOAD " + p.label + " left memory with its chunk after " + s + " s (NonSerialized " + p.nonser + ")");
    return;
  }
  @PKG@.PpLog.result(p.pr, @PKG@.PpLogic.up(p.tag), -1, p.label + " was removed BY THE GAME after " + s + " s (" + reason + ": role despawn timer, death or another mod)" + (p.role.startsWith("Risen_") ? " - Template_Summoned_Ally despawns after " + @PKG@.PpReg.SUMMON_DESPAWN + " s or when it leaves your flock" : ""));
  @PKG@.PpReg.forget(p, "removed by the game (" + reason + ")");
}""")
M(lds, r"""
public void onEntityAdded(@REF@ ref, @ADR@ reason, @ST@ st, @CB@ cb) {
  try { added(ref, reason, st, cb); } catch (Throwable t) { @PKG@.PpLog.warnOnce("load:" + t.getClass().getName(), "load hook failed: " + t); }
}""")
M(lds, r"""
public void onEntityRemove(@REF@ ref, @RR@ reason, @ST@ st, @CB@ cb) {
  try { removed(ref, reason, st); } catch (Throwable t) { @PKG@.PpLog.warnOnce("unload:" + t.getClass().getName(), "remove hook failed: " + t); }
}""")

# =====================================================================================================================
# PpQuit: PlayerDisconnectEvent -> the owner's pets removed on their world threads (spec 2.2 "auto-store on logout")
# =====================================================================================================================
quit_ = mk("PpQuit")
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public PpQuit() { }")
M(quit_, r"""
public static int leave(java.util.UUID o, String name) {
  if (o == null) return 0;
  @PKG@.PpTick.ACC.remove(o);
  @PKG@.PpReg.EPOCH.remove(o);
  @PKG@.PpReg.DEAD.remove(o);
  java.util.List l = @PKG@.PpReg.ofOwner(o);
  int n = 0;
  for (int i = 0; i < l.size(); i++) if (@PKG@.PpRemove.queue((@PKG@.PpPet) l.get(i), "owner logged out")) n++;
  if (l.size() > 0) @PKG@.PpLog.result(null, "LIFE", -1, name + " logged out: " + n + " of " + l.size() + " probe pets queued for removal on their world threads (the GONE lines follow; log back in - nothing of the probe should be left)");
  return n;
}""")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr != null) leave(pr.getUuid(), pr.getUsername());
  } catch (Throwable t) { @PKG@.PpLog.warnOnce("quit:" + t.getClass().getName(), "logout handler failed: " + t); }
}""")

# =====================================================================================================================
# PpCmds: what each /petprobe action does (world thread: AbstractPlayerCommand.execute)
# =====================================================================================================================
cmds = mk("PpCmds")
F(cmds, "public static final String OK = \"@COLOK@\";")
F(cmds, "public static final String ERR = \"@COLERR@\";")
F(cmds, "public static final String INF = \"@COLINF@\";")
for key, rows in ROWS.items():
    F(cmds, "public static final String[] %s_ROLE = %s;" % (key, jarr([r[0] for r in rows])))
    F(cmds, "public static final String[] %s_MODEL = %s;" % (key, jarr([r[1] for r in rows])))
    F(cmds, "public static final float[] %s_SCALE = %s;" % (key, jflt([r[2] for r in rows])))
    F(cmds, "public static final String[] %s_LABEL = %s;" % (key, jarr([r[3] for r in rows])))
    F(cmds, "public static final String[] %s_VBOX = %s;" % (key, jarr([vbox_text(r[1], r[2]) for r in rows])))
HELP = [
    "Pet probe (admin only). Results are [SkyyPetProbe] RESULT lines in the server log + mods/Skyy_SkyyPetProbe/probe.log.",
    "/petprobe all - p1, p2, p4 and p8 in rows ahead of you",
    "/petprobe p1 [air, water] - small pets: walk with them, look at legs / nameplates / hitting the tiny ones",
    "/petprobe p2 - does a role keep the model we pass? (read back at 1 s and 6 s)",
    "/petprobe p3 [own] - follow + teleport when far: run / fly away 30+ blocks for a minute",
    "/petprobe p4 - grows a fox in 4 steps (4 s apart): say which steps changed it",
    "/petprobe p5 - saved or not: go 300+ blocks away, come back, run /petprobe p5 again",
    "/petprobe p6 - a summon joins your flock? does it attack what hits you / what you hit?",
    "/petprobe p7 [credit] - a fighting summon + a pig: hit the pig once (credit = its kills of THAT pig count as yours)",
    "/petprobe p8 - SkyyMobs ignores pets? (+ a control fox that it should level)",
    "/petprobe p9 - hit the skeleton until it would die: it must go DOWN instead",
    "/petprobe p10 [ride, big] - mounts (horse x0.5 / x1.0 / x1.3, bison, camel, ram): press F on each, or /petprobe p10 ride",
    "/petprobe list, /petprobe clear (both show the ghost list: 0 ghosts = safe to remove the mod), /petprobe nosave on|off",
]
F(cmds, "public static final String[] HELP = %s;" % jarr(HELP))
M(cmds, r"""
public static void help(@PR@ pr) {
  for (int i = 0; i < HELP.length; i++) @PKG@.PpLog.tell(pr, HELP[i], i == 0 ? INF : null);
  @PKG@.PpLog.tell(pr, @PKG@.PpReg.PETS.size() + " probe pets out; NonSerialized on new spawns " + (@PKG@.PpReg.NOSAVE ? "ON" : "OFF") + "; P7 credit " + (@PKG@.PpReg.CREDIT ? "ON" : "OFF") + "; " + @PKG@.PpFile.GHOSTS.size() + " ghosts from earlier runs still to find", INF);
}""")
# one row by its table name (the constants above)
for key in ROWS:
    M(cmds, r"""
public static int row%s(@ST@ st, @WLD@ w, @PR@ pr, double[] wh, String tag, double ahead, boolean invul, boolean nonser, int mode, java.util.List out) {
  return @PKG@.PpSpawn.row(st, w, pr, wh, tag, %s_ROLE, %s_MODEL, %s_SCALE, %s_LABEL, %s_VBOX, ahead, %s, invul, nonser, mode, out);
}""" % (key, key, key, key, key, key, repr(float(ROW_GAP.get(key, 2.5)))))
M(cmds, r"""
public static void said(@PR@ pr, String probe, int n, int want, String what) {
  @PKG@.PpLog.tell(pr, probe + ": " + n + "/" + want + " spawned - " + what, n == want ? OK : ERR);
}""")
M(cmds, r"""
public static void p1(@ST@ st, @WLD@ w, @PR@ pr, double[] wh, String opt, double ahead) {
  boolean ns = @PKG@.PpReg.NOSAVE;
  if ("air".equals(opt)) { said(pr, "P1 air", rowP1_AIR(st, w, pr, wh, "p1", ahead, true, ns, 0, null), P1_AIR_ROLE.length, "two flying roles + a walking owl: do they fly near you, flee, or wander off?"); return; }
  if ("water".equals(opt)) { said(pr, "P1 water", rowP1_WATER(st, w, pr, wh, "p1", ahead, true, ns, 0, null), P1_WATER_ROLE.length, "stand IN water: do they swim, and how do they look out of water?"); return; }
  said(pr, "P1", rowP1(st, w, pr, wh, "p1", ahead, true, ns, 1, null), P1_ROLE.length, "walk around 20 s: legs skating? nameplates? hit the tiny whale / rex");
}""")
M(cmds, r"""
public static void p5(@ST@ st, @WLD@ w, @PR@ pr, double[] wh) {
  java.util.List l = @PKG@.PpReg.ofOwner(pr.getUuid());
  java.util.ArrayList five = new java.util.ArrayList();
  for (int i = 0; i < l.size(); i++) if ("p5".equals(((@PKG@.PpPet) l.get(i)).tag)) five.add(l.get(i));
  if (five.isEmpty()) {
    double ahead = 4.0;
    double[] a = @PKG@.PpLogic.slot(0, 2, wh[0], wh[2], (int) wh[3], (int) wh[4], ahead, 2.5);
    double[] b = @PKG@.PpLogic.slot(1, 2, wh[0], wh[2], (int) wh[3], (int) wh[4], ahead, 2.5);
    int n = 0;
    if (@PKG@.PpSpawn.spawn(st, w, pr, "p5", P5_LABEL[0], P5_ROLE[0], P5_MODEL[0], P5_SCALE[0], P5_VBOX[0], a[0], wh[1], a[1], wh[0], wh[2], true, true, 0) != null) n++;
    if (@PKG@.PpSpawn.spawn(st, w, pr, "p5", P5_LABEL[1], P5_ROLE[1], P5_MODEL[1], P5_SCALE[1], P5_VBOX[1], b[0], wh[1], b[1], wh[0], wh[2], true, false, 0) != null) n++;
    said(pr, "P5", n, 2, "A has NonSerialized, B not. Go 300+ blocks away (or /tp), wait 10 s, come back here, run /petprobe p5 again");
    return;
  }
  for (int i = 0; i < five.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) five.get(i);
    @REF@ r = @PKG@.PpCheck.live(p);
    boolean here = r != null;
    String facts = " (chunk unloads seen " + p.unloads + ", reloads seen " + p.reloads + ")";
    if (p.nonser) {
      if (!here && p.unloads > 0) @PKG@.PpLog.result(pr, "P5", 1, p.label + " is GONE after its chunk unloaded - NonSerialized entities are not saved" + facts);
      else if (here && p.reloads > 0) @PKG@.PpLog.result(pr, "P5", 0, p.label + " came back from the chunk - NonSerialized did NOT stop the save" + facts);
      else @PKG@.PpLog.result(pr, "P5", -1, p.label + (here ? " is still here and its chunk never unloaded - go further away / wait longer" : " is not found but no unload was seen") + facts);
    } else {
      if (here && p.reloads > 0) @PKG@.PpLog.result(pr, "P5", 1, p.label + " (no NonSerialized) was saved and LOADED back - the control works, so SkyyPets needs NonSerialized or the ghost sweep" + facts);
      else @PKG@.PpLog.result(pr, "P5", -1, p.label + (here ? " is here, its chunk never unloaded" : " is not found") + facts);
    }
  }
  if (!@PKG@.PpFile.GHOSTS.isEmpty()) @PKG@.PpLog.tell(pr, @PKG@.PpFile.GHOSTS.size() + " probe pets from before the last restart were not seen yet (their chunks did not load).", INF);
}""")
# the ghost list: pets that were not loaded when clear / logout / stop tried to remove them (may sit in a saved chunk). The mod must
# stay installed until this is 0 (critic fix): it is the only thing that can remove them.
M(cmds, r"""
public static int ghosts(@PR@ pr) {
  int n = @PKG@.PpFile.GHOSTS.size();
  if (n == 0) { @PKG@.PpLog.tell(pr, "0 probe ghosts: nothing of the probe can sit in a saved chunk - safe to remove the mod once you are done.", OK); return 0; }
  @PKG@.PpLog.tell(pr, n + " probe ghosts (pets that were not loaded, they may sit in a saved chunk) - do NOT remove the mod yet. Stand within 16 blocks of each spot for 5 s:", ERR);
  java.util.Iterator it = new java.util.ArrayList(@PKG@.PpFile.GHOSTS.keySet()).iterator();
  int k = 0;
  while (it.hasNext()) {
    String u = (String) it.next();
    k++;
    if (k > 8) continue;
    Object at = @PKG@.PpFile.GHOST_AT.get(u);
    @PKG@.PpLog.tell(pr, "  " + @PKG@.PpFile.GHOSTS.get(u) + " (" + @PKG@.PpLogic.shortId(u) + ") at " + (at == null ? "an unknown spot (only its chunk loading clears it)" : String.valueOf(at).replace(',', ' ')), null);
  }
  if (k > 8) @PKG@.PpLog.tell(pr, "  ... and " + (k - 8) + " more", null);
  return n;
}""")
M(cmds, r"""
public static void list(@ST@ st, @PR@ pr) {
  java.util.List l = @PKG@.PpReg.all();
  double[] op = null;
  try { op = @PKG@.PpCheck.pos(st, pr.getReference()); } catch (Throwable t) { op = null; }
  @PKG@.PpLog.tell(pr, l.size() + " probe pets (max " + @PKG@.PpReg.MAX + "):", INF);
  for (int i = 0; i < l.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) l.get(i);
    @REF@ r = @PKG@.PpCheck.live(p);
    double[] pp = @PKG@.PpCheck.pos(st, r);
    String d = (pp == null || op == null) ? (r == null ? "not loaded" : "other world") : @PKG@.PpLogic.f1(@PKG@.PpLogic.dist(pp[0], pp[1], pp[2], op[0], op[1], op[2])) + " blocks";
    @PKG@.PpLog.tell(pr, p.describe() + " in " + p.worldName + ", " + d + ", owner " + p.ownerName, null);
  }
  ghosts(pr);
}""")
# remove every probe pet: this world now (dismounting you first), other worlds through their world thread
M(cmds, r"""
public static int clear(@ST@ st, @WLD@ w, @PR@ pr) {
  java.util.List l = @PKG@.PpReg.all();
  int now = 0; int queued = 0; int missing = 0;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) l.get(i);
    if (p.world == w) { if (@PKG@.PpRemove.now(st, p, "/petprobe clear")) now++; else missing++; }
    else if (@PKG@.PpRemove.queue(p, "/petprobe clear (other world)")) queued++;
  }
  @PKG@.PpReg.REWRITE.clear();
  @PKG@.PpReg.CREDIT = false;
  @PKG@.PpLog.tell(pr, "Cleared: " + now + " removed here, " + queued + " queued in other worlds, " + missing + " not loaded (kept on the ghost list until found or confirmed gone). P7 credit OFF.", OK);
  ghosts(pr);
  return now + queued;
}""")
M(cmds, r"""
public static void run(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String a, String b) {
  String t = a == null ? "" : a.trim().toLowerCase(java.util.Locale.ROOT);
  String o = b == null ? "" : b.trim().toLowerCase(java.util.Locale.ROOT);
  @PKG@.PpLog.info(pr.getUsername() + " ran /petprobe " + t + (b == null ? "" : " " + b) + " in " + (w == null ? "?" : w.getName()));
  if (t.length() == 0 || t.equals("help")) { help(pr); return; }
  if (t.equals("list")) { list(st, pr); return; }
  if (t.equals("clear")) { clear(st, w, pr); return; }
  if (t.equals("nosave")) {
    if (o.equals("on")) @PKG@.PpReg.NOSAVE = true; else if (o.equals("off")) @PKG@.PpReg.NOSAVE = false;
    else { @PKG@.PpLog.tell(pr, "Usage: /petprobe nosave on|off (now " + (@PKG@.PpReg.NOSAVE ? "on" : "off") + ")", ERR); return; }
    @PKG@.PpLog.tell(pr, "NonSerialized on new probe pets: " + (@PKG@.PpReg.NOSAVE ? "ON (not saved with the chunk)" : "OFF (saved; the next start's ghost sweep removes leftovers)"), OK);
    return;
  }
  int n = @PKG@.PpLogic.probeNo(t);
  if (n < 0) { @PKG@.PpLog.tell(pr, "Unknown option '" + a.trim() + "'.", ERR); help(pr); return; }
  double[] wh = @PKG@.PpCheck.where(st, ref);
  if (wh == null) { @PKG@.PpLog.tell(pr, "Your position is unreadable.", ERR); return; }
  boolean ns = @PKG@.PpReg.NOSAVE;
  if (n == 1 && (o.length() == 0 || o.equals("air") || o.equals("water"))) { p1(st, w, pr, wh, o, 4.0); return; }
  if (n == 3 && (o.length() == 0 || o.equals("own"))) {
    if (o.equals("own")) said(pr, "P3 own", rowP3_OWN(st, w, pr, wh, "p3", 4.0, true, ns, 2, null), 1, "OUR code walks it after you (every tick). Run / fly 30+ blocks away for a minute");
    else said(pr, "P3", rowP3(st, w, pr, wh, "p3", 4.0, true, ns, 1, null), 1, "vanilla Test_Pet follow + teleport. Run / fly 30+ blocks away for a minute");
    return;
  }
  if (n == 7 && o.equals("credit")) { @PKG@.PpReg.CREDIT = !@PKG@.PpReg.CREDIT; @PKG@.PpLog.tell(pr, "P7 credit " + (@PKG@.PpReg.CREDIT ? "ON: the P7 fighter's hits ON THE P7 PIG count as YOURS (source rewritten; nothing else; any XP you get is real and stays; /petprobe clear turns it off)" : "OFF: hits stay the pet's"), OK); return; }
  if (n == 10 && o.equals("ride")) {
    String res = @PKG@.PpMount.ride(st, ref, pr);
    if (res.startsWith("+")) @PKG@.PpLog.result(pr, "P10", -1, res.substring(1));
    else @PKG@.PpLog.tell(pr, "P10 ride: " + res, ERR);
    return;
  }
  if (n == 10 && (o.length() == 0 || o.equals("big"))) {
    java.util.ArrayList got = new java.util.ArrayList();
    int k = o.equals("big") ? rowP10_BIG(st, w, pr, wh, "p10", 5.0, true, ns, 0, got) : rowP10(st, w, pr, wh, "p10", 5.0, true, ns, 0, got);
    for (int i = 0; i < got.size(); i++) { @PKG@.PpPet q = (@PKG@.PpPet) got.get(i); q.mount = true; q.anchorY = @PKG@.PpMount.anchorOf(q.role) * q.scale; }
    said(pr, "P10", k, o.equals("big") ? P10_BIG_ROLE.length : P10_ROLE.length, "press F on each to ride (vanilla) and note the seat, or stand next to one: /petprobe p10 ride (our code)");
    return;
  }
  if (o.length() > 0) { @PKG@.PpLog.tell(pr, "/petprobe " + t + " takes no '" + b.trim() + "'.", ERR); return; }
  if (n == 0) {
    p1(st, w, pr, wh, "", 4.0);
    said(pr, "P2", rowP2(st, w, pr, wh, "p2", 8.0, true, ns, 0, null), P2_ROLE.length, "read back at 1 s and 6 s");
    said(pr, "P4", rowP4(st, w, pr, wh, "p4", 12.0, true, ns, 0, null), 1, "grows in 4 steps, 4 s apart");
    said(pr, "P8", rowP8(st, w, pr, wh, "p8", 15.0, true, ns, 0, null), 1, "every pet is asked at 3 s; the control fox may bite (invulnerable pets only)");
    return;
  }
  if (n == 2) { said(pr, "P2", rowP2(st, w, pr, wh, "p2", 4.0, true, ns, 0, null), P2_ROLE.length, "read back at 1 s and 6 s"); return; }
  if (n == 4) { said(pr, "P4", rowP4(st, w, pr, wh, "p4", 4.0, true, ns, 0, null), 1, "grows in 4 steps, 4 s apart: say which steps changed it"); return; }
  if (n == 5) { p5(st, w, pr, wh); return; }
  if (n == 6) { said(pr, "P6", rowP6(st, w, pr, wh, "p6", 3.0, true, ns, 0, null), 1, "flock checked at 2 s and 5 s; it despawns by itself after " + @PKG@.PpReg.SUMMON_DESPAWN + " s"); return; }
  if (n == 7) {
    int old = 0;
    java.util.List mine = @PKG@.PpReg.ofOwner(pr.getUuid());
    for (int i = 0; i < mine.size(); i++) {
      @PKG@.PpPet q = (@PKG@.PpPet) mine.get(i);
      if (!"p7".equals(q.tag) && !"p7t".equals(q.tag)) continue;
      if (q.world == w ? @PKG@.PpRemove.now(st, q, "a new /petprobe p7 run") : @PKG@.PpRemove.queue(q, "a new /petprobe p7 run")) old++;
    }
    @PKG@.PpReg.REWRITE.clear();
    if (old > 0) @PKG@.PpLog.tell(pr, "P7: removed the " + old + " pets of the last P7 run first (one fighter + one pig per run).", INF);
    java.util.ArrayList got = new java.util.ArrayList();
    int k = rowP7(st, w, pr, wh, "p7", 3.0, false, ns, 0, got);
    for (int i = 0; i < got.size(); i++) ((@PKG@.PpPet) got.get(i)).fight = true;
    int k2 = rowP7_TARGET(st, w, pr, wh, "p7t", 7.0, false, ns, 0, null);
    said(pr, "P7", k + k2, 2, "with ONLY the pig nearby: hit the pig ONCE, let the skeleton finish it (credit " + (@PKG@.PpReg.CREDIT ? "ON" : "OFF") + ", toggle: /petprobe p7 credit)");
    return;
  }
  if (n == 8) { said(pr, "P8", rowP8(st, w, pr, wh, "p8", 4.0, true, ns, 0, null), 1, "every probe pet is asked at 3 s; this control fox has the vanilla hostile role (invulnerable, may bite)"); return; }
  if (n == 9) {
    java.util.ArrayList got = new java.util.ArrayList();
    int k = rowP9(st, w, pr, wh, "p9", 3.0, false, ns, 0, got);
    for (int i = 0; i < got.size(); i++) ((@PKG@.PpPet) got.get(i)).down = true;
    said(pr, "P9", k, 1, "hit it until it would die: it must vanish with NO death animation and NO drop");
    return;
  }
  @PKG@.PpLog.tell(pr, "/petprobe " + t + " takes no '" + b + "'.", ERR);
}""")

# =====================================================================================================================
# the commands: /petprobe (alias /pprobe) + usage variants for 1 and 2 tokens (HANDOFF COMMAND RULES 2); admin only
# =====================================================================================================================
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
c1 = mk("PetProbeArgCmd", T["APC"])
F(c1, "public @RA@ aArg;")
C(c1, r"""
public PetProbeArgCmd() {
  super("(admin) /petprobe <all, p1-p10, list, clear, help>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("probe", "all, p1 .. p10, list, clear or help", @ATY@.STRING);
}""")
M(c1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.aArg)); } catch (Throwable t) { @PKG@.PpCmds.help(pr); return; }
  @PKG@.PpCmds.run(ref, store, pr, world, a, null);
}""")
c2 = mk("PetProbeArg2Cmd", T["APC"])
F(c2, "public @RA@ aArg;")
F(c2, "public @RA@ bArg;")
C(c2, r"""
public PetProbeArg2Cmd() {
  super("(admin) /petprobe p1 <air, water>, p3 own, p7 credit, p10 <ride, big>, nosave <on, off>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("probe", "p1, p3, p7, p10 or nosave", @ATY@.STRING);
  this.bArg = withRequiredArg("option", "air / water (p1), own (p3), credit (p7), ride / big (p10), on / off (nosave)", @ATY@.STRING);
}""")
M(c2, EXEC + r""" {
  String a = null; String b = null;
  try { a = String.valueOf(ctx.get(this.aArg)); b = String.valueOf(ctx.get(this.bArg)); } catch (Throwable t) { @PKG@.PpCmds.help(pr); return; }
  @PKG@.PpCmds.run(ref, store, pr, world, a, b);
}""")
cmd = mk("PetProbeCmd", T["APC"])
C(cmd, r"""
public PetProbeCmd() {
  super("petprobe", "(admin) pet engine probes P1-P10 (throwaway dev pack): /petprobe lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "pprobe" });
  addUsageVariant(new @PKG@.PetProbeArgCmd());
  addUsageVariant(new @PKG@.PetProbeArg2Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.PpCmds.run(ref, store, pr, world, null, null);
}""")

# ---- the plugin
pl = mk("SkyyPetProbePlugin", T["JP"])
F(pl, "public static final String[] ROLES = %s;" % jarr(sorted(set(r[0] for rs in ROWS.values() for r in rs) | {EMPTY_ROLE})))
F(pl, "public static final String[] MODELS = %s;" % jarr(sorted(set(r[1] for rs in ROWS.values() for r in rs) | {P4_ADULT})))
C(pl, "public SkyyPetProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.PpLog.LOG = getLogger();
  try { @PKG@.PpFile.DIR = getDataDirectory().resolveSibling("Skyy_SkyyPetProbe"); } catch (Throwable t) { @PKG@.PpFile.DIR = null; @PKG@.PpLog.warn("no data folder: " + t); }
  int g = @PKG@.PpFile.load();
  getCommandRegistry().registerCommand(new @PKG@.PetProbeCmd());
  getEntityStoreRegistry().registerSystem(new @PKG@.PpTick());
  getEntityStoreRegistry().registerSystem(new @PKG@.PpDmgFilter());
  getEntityStoreRegistry().registerSystem(new @PKG@.PpDmgInspect());
  getEntityStoreRegistry().registerSystem(new @PKG@.PpLoadSys());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.PpQuit());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyPetProbe] @VERSION@ ready - /petprobe (admin): pet engine probes P1-P10; " + g + " probe pets from earlier runs to sweep when their chunks load (throwaway dev pack, remove after the test session)");
}""")
# start: every role / model the probe uses, as the live server sees them (logged; the probe refuses missing ones with a FAIL line)
M(pl, r"""
public static String census() {
  StringBuilder sb = new StringBuilder();
  int bad = 0;
  for (int i = 0; i < ROLES.length; i++) {
    int ix = -1;
    try { ix = @PKG@.PpEng.roleIndex(ROLES[i]); } catch (Throwable t) { ix = -2; }
    if (ix < 0) bad++;
    sb.append(i == 0 ? "" : ", ").append(ROLES[i]).append("=").append(ix);
  }
  int miss = 0;
  StringBuilder ms = new StringBuilder();
  for (int i = 0; i < MODELS.length; i++) {
    Object a = null;
    try { a = @PKG@.PpEng.modelAsset(MODELS[i]); } catch (Throwable t) { a = null; }
    if (a == null) { miss++; ms.append(ms.length() == 0 ? "" : ", ").append(MODELS[i]); }
  }
  return "roles " + sb + " (" + bad + " not spawnable); models " + (MODELS.length - miss) + "/" + MODELS.length + " loaded" + (miss > 0 ? " - missing " + ms : "");
}""")
M(pl, r"""
protected void start() {
  try { @PKG@.PpLog.info("census at start: " + census()); } catch (Throwable t) { @PKG@.PpLog.warn("census failed: " + t); }
}""")
# stop: every pet queued for removal on its world thread (best effort - a world that is already stopping keeps it in its chunk; the
# next start's ghost sweep removes it). Memory cleared.
M(pl, r"""
protected void shutdown() {
  java.util.List l = @PKG@.PpReg.all();
  int q = 0;
  for (int i = 0; i < l.size(); i++) {
    @PKG@.PpPet p = (@PKG@.PpPet) l.get(i);
    if (p.hasK) @PKG@.PpFile.append("WHERE " + p.uuid + " " + @PKG@.PpFile.at(p.worldName, p.kx, p.kz));
    if (@PKG@.PpRemove.queue(p, "server stop")) q++;
  }
  if (l.size() > 0) @PKG@.PpLog.info("stop: " + q + " of " + l.size() + " probe pets queued for removal; anything a saved chunk still holds is removed at the next start");
  @PKG@.PpReg.PETS.clear();
  @PKG@.PpReg.REWRITE.clear();
  @PKG@.PpReg.EPOCH.clear();
  @PKG@.PpReg.DEAD.clear();
  @PKG@.PpTick.ACC.clear();
  @PKG@.PpReg.CREDIT = false;
  @PKG@.PpFile.clearGhosts();
  super.shutdown();
}""")

ALL = [fil, log, lg, pet, reg, api, eng, pre, chk, spn, rmv, fol, mnt, prb, life, tick, dflt, dins, lds, quit_, cmds, c1, c2, cmd, pl]
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyPetProbe-%s.jar" % VERSION)
man = B.manifest("SkyyPetProbe", VERSION, "SkyWynn THROWAWAY dev pack: pet engine probes P1-P10 (/petprobe, admin only) - shrunk vanilla pets, follow / teleport, growth, saving, flock, fight credit, SkyyMobs, DOWN, mounts. Pinned for one test session, then removed.", PKG + ".SkyyPetProbePlugin")
man["IncludesAssetPack"] = False   # class-only jar (no asset = nothing for the engine's asset validators to refuse)
B.assemble(jar, man, OUT, {})
print("[SkyyPetProbe] %s ready (build) - %d classes" % (VERSION, len(ALL)))
