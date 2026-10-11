"""SkyyTownProbe 0.2 - build script (javassist via jpype). Throwaway probe mod, Q0 PROBE ROUND: the 14 engine probes of
research/cloud/SkyyQuests-Zone1-Spec.md section 11 (+ Skyy's Pebble lock: "in every town, but he wears a different hat, and goes by a
different name ... pebble, rubble, rock things like that") appended to 0.1 (the T0 town probe, research/Zone-1-Town-Build-Plan.md 9).
Admin-only, pinned for ONE test session, then removed from the SET (like SkyyMonkProbe / SkyyReelProbe).
NO PATCH CHAIN: probe mods are rebuilt from a full copy of the previous build script (this file = build_skyytownprobe_0.1.py + the Q0
round); 0.1's script is never re-run for 0.2 and nothing reads a generated script.
Run:   python SkyyTownProbe/build_skyytownprobe_0.2.py   -> SkyyTownProbe/SkyyTownProbe-0.2.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyTownProbe/test_skyytownprobe_0.2.py    (-Xverify:all, every code path executed on engine stand-ins, the shipped
       assets through the engine's own codecs, permissions, start twice on a scratch copy of live data, engine-access audit;
       scratch tools/dev/scratch/q0probe/)

Q0 PROBES (all /townprobe sub-commands, admin only; the ones that spawn something only on the Zone 1 test island skywynn_z1). Every
result is ONE line "[SkyyTownProbe] Q0 #<n> <title>: PASS / FAIL / WAIT - <value>" in chat AND the server log, also appended to the
probe's own log file <server>/mods/Skyy_SkyyTownProbe/q0-results.log (the only new saved data besides the claim ledger, see #17).
  /townprobe all        sets the whole round up in one go (Fennel + Pebble NPCs, event listener, kill log, board, stamps, poll,
                        copper) and prints the numbered things to do; /townprobe report = every probe's latest result; /townprobe q0
                        = the Q0 command list
  #1  talk              "Fennel" (vanilla Temple_Kweebec_Static, no shop) 3 ahead / 2 left. F -> our UseEntityEvent$Pre system
                        cancels the vanilla use -> calls the bridge function townprobe:fn:talk (the exact quest:fn:talk shape:
                        Function(Object[] {UUID, String npcId}) -> Boolean) -> World.execute -> the dialogue page opens NEXT tick.
                        Counts presses / bridge calls / opens; a second Use event from the same player within 250 ms is counted
                        and suppressed. PASS = one page per press. Pebble (both models) goes the same way.
  #2  pebblem           Pebble with OUR art (art/pebble, shipped in the jar under NPC/SkyyTownProbe/Pebble, ModelAsset
                        SkyyTownProbe_Pebble: Idle / Walk / Talk / Wave / Hurt / Death) as an NPC (role Temple_Kweebec_Static +
                        NPCPlugin.spawnEntity with our model); logs kept / replaced (forced back); Wave on spawn, Talk on F
                        (NPCEntity.playAnimation, slot Action). The nameplate node is the client's business (Skyy looks).
  #3  hint              cycles the F prompt on Fennel / Pebble: 1 our lang key server.skyytownprobe.talkHint ("Press [F] to talk",
                        shipped in Server/Languages/en-US/server.lang - merged per key), 2 vanilla interactionHints.generic, 3 a raw
                        text. Desk check (build): vanilla has NO talk hint key (the list is printed and logged).
  #4  marker [off]      cycles the ! / ? over Fennel and Pebble: 1 nameplate prefix, 2 a floating "!" nameplate prop (undo record),
                        3 the vanilla emote particles Alerted (!) / Question (?) every 3 s sent to YOU only (ParticleUtil with a
                        player list), 0 off.
  #5  hooks             a SECOND UseEntityEvent$Pre system (TpUseSys2, registered after TpUseSys) counts what reaches it. Desk
                        (build + harness bytecode): EventSystem.shouldProcessEvent skips a cancelled ICancellableEcsEvent, so a
                        cancelled Use never reaches a later system -> only one mod (SkyyTowns) may own the town NPC Use hook.
  #6  poll [s]          for 30 s (or s, 5-120) the 1 s tick times a reach check of 20 players x 3 objectives (20 real
                        TransformComponent reads + 60 distance checks) on the world thread; PASS = average under 0.5 ms.
  #7  move / move check moves the Pebble NPC between its spot A and a spot B in front of you (Teleport component, the vanilla
                        TeleportSystems$MoveSystem) and saves the spot in its undo record; after a restart "move check" counts Pebble
                        models at both spots: PASS = exactly one, at the saved spot.
  #8  (dialogue page)   two portraits on the page: an ItemIcon (Rock_Stone, the control) and the Pebble icon png shipped in the jar
                        (Common/UI/Custom/SkyyTownProbe/Pebble.png as a Group Background). Pebble has no item, so an ItemIcon of
                        Pebble itself would need an item asset - left out on purpose. Skyy says which shows.
  #9  stamp [off]       3 stamp points 8 / 16 / 24 blocks ahead (memory only, owner = you); a WorldMapManager marker provider
                        shows them on the map to the owner only; walking within 3 blocks stamps each (reach). PASS (reach) at 3/3.
  #10 event [off]       registers quest:fn:event in the skyy.bridge map ONLY if nobody owns it (never replaced; removed on off /
                        shutdown only if it is still ours), self-test round trip, then logs every real call (none expected until
                        SkyyBank / SkyyBazaar / SkyyGear add the one-line call).
  #11 kills / golem     logs every NPC death a player causes (role id + killer) while on; a Golem_Crystal_Earth kill = PASS (the
                        Zone 1 guardian, by role id - an OnDeathSystem like SkyyCollections' CollKillSys). /townprobe golem spawns
                        one 10 blocks ahead (undo record; it fights back).
  #12 board             the daily anchor: day = floor((now - anchor) / 86400 s), seed = FNV-1a(pkey | day), 3 of the 12 placeholder
                        jobs of spec 3.1 by java.util.Random(seed). Each run appends a BOARD line to q0-results.log and compares
                        with earlier lines of the same profile + day: PASS across a restart / a world change, FAIL if they differ.
  #13 copper [check]    gives the 4 Copper armour pieces (Armor_Copper_Head / Hands / Legs / Chest) with OUR metadata key
                        SkyyTownProbe = {set: copper_quest, grant: <pkey>:copper:<n>} (never the SkyyGear doc key); "copper check"
                        counts pieces carrying set=copper_quest in bags + armour (also notes a SkyyGear doc) -> run it after a
                        death, a Vault deposit / withdraw and a Wardrobe swap.
  #14 (dialogue page)   the reward preview = an ItemGrid of new ItemGridSlot(new ItemStack(id, 1)) for the 4 Copper pieces (no
                        metadata, the kit's java_grid_fill); PASS when the player is still connected 5 s after that page.
  #15 hat               cycles Pebble's town disguise: alias Pebble / Rubble / Cobble / Gravel / Flint / Shale + a vanilla cosmetic
                        hat as a ModelAttachment added to a copy of the live Model (ModelComponent replaced, PersistentModel NOT
                        touched - after a restart the hat is gone again, the probe says so); Fennel gets the same hats as the
                        vanilla-rig control. Nameplate + DisplayName swapped at runtime.
  #16 (dialogue page)   open / Next / Close button / Esc (onDismiss) counted; PASS when both closes were seen.
  #17 copper / claim    the claim ledger (spec section 6): the 4 rewards become 4 claim lines in ONE atomic write
                        (Skyy_SkyyTownProbe/claims.properties), then paid one at a time storage-first with a count before / after;
                        a claim whose grant id is already on an item in the bags is removed without a second item (dupe guard); a
                        full bag keeps the claim ("/townprobe claim" pays later). The ledger file is deleted when empty.
                        FIX ROUND (q0probefix): claim pays ONLY the caller's own lines (grant starts with pkey + ":"; other
                        players' / profiles' lines stay, not counted as waiting); every grant ever written stays as an
                        "issued=<grant>" line, so copper never issues a set twice (pieces in the Vault / Wardrobe / dropped on
                        death count as issued) until "/townprobe copper reset" (clears the caller's own claim + issued lines).
                        Every ledger read-change-write runs inside ONE static synchronized TpClaims method (pay / issue / reset).
FIX ROUND (q0probefix) also: a result line for a NON-admin (a kill, a quest:fn:event, F on a probe NPC) goes to the server log only (no
chat, no q0-results.log line); a repeated #10 / #11 WAIT is server log only too (no file line per kill); /townprobe report falls back
to the newest q0-results.log line for a probe that has no result since the last start (so the report survives a restart); the first
dialogue line no longer says "probe clerk" (Fennel and Pebble share it).
ASSETS SHIPPED (0.2; 0.1 shipped none): only our own files - the Pebble art from art/pebble (model, texture, 6 animations, model icon,
the UI icon copy), the ModelAsset JSON Server/Models/SkyyTownProbe/SkyyTownProbe_Pebble.json and one lang key. Every vanilla path they
name is checked against Assets.zip at build time; the harness decodes the ModelAsset JSON through the engine's own ModelAsset codec
(validation results checked) and loads it; the smoke test boots a real server on a scratch world copy (the engine's asset validators).
Ids / paths are all SkyyTownProbe-prefixed, so they can never clash with a later SkyyTowns jar.

0.1 (unchanged unless noted):
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
                             0.2: F on this Pebble opens the Q0 dialogue page (probe #1) instead of the 0.1 chat line.
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
0.2 adds q0-results.log (the probe's own result log, appended by every Q0 probe; the board probe reads it back) and claims.properties
(the claim ledger of #17, deleted when empty). The Q0 NPCs (Fennel, Pebble model, the golem, the floating "!") are undo records like
Mossby; stamps, poll, event listener, kill log, marker mode and hat choice are memory only. A start writes nothing.
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

VERSION = "0.2"
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

# ================= Q0 round (0.2): constants + desk checks (Assets.zip read only; our own art from art/pebble) =================
ART = os.path.join(os.path.dirname(HERE), "art", "pebble", "Common")
PEB_MODEL = "SkyyTownProbe_Pebble"                    # our ModelAsset id (Server/Models/SkyyTownProbe/SkyyTownProbe_Pebble.json)
PEB_DIR = "NPC/SkyyTownProbe/Pebble"                  # under Common/ (art/pebble ships it as NPC/SkyyTowns/Pebble: renamed here so a
                                                      # later SkyyTowns jar never shares a path with this probe)
PEB_ANIMS = [("Idle", "Default/Idle", True), ("Walk", "Default/Walk", True), ("Talk", "Default/Talk", True), ("Wave", "Default/Wave", False),
             ("Hurt", "Damage/Hurt", False), ("Death", "Damage/Death", False)]
PEB_ICON = "Icons/ModelsGenerated/SkyyTownProbe_Pebble.png"
PEB_UI_ICON = "SkyyTownProbe/Pebble.png"              # under Common/UI/Custom/ (the dialogue portrait, probe #8)
TALKER_NAME, PEBM_NAME, GOLEM_NAME = "Fennel (Q0 probe)", "Pebble", "Earth Golem (Q0 probe)"
GOLEM = "Golem_Crystal_Earth"                         # the Zone 1 guardian ("Earthen Golem") - the temple's Earth Crystal Golem
PORTRAIT_ITEM = LANE_FILL                             # ItemIcon control portrait (a vanilla block item, checked above)
TALK_KEY = "skyytownprobe.talkHint"                   # our one lang key (server.lang is merged per key - research/SkyyArmory-Spec.md)
HINTS = ["server." + TALK_KEY, "server.interactionHints.generic", "Press F to talk"]
DISGUISES = [("Pebble", None, None),
             ("Rubble", "Cosmetics/Head/MossyHat.blockymodel", "Cosmetics/Head/MossyHat_Textures/MossyHat_Texture.png"),
             ("Cobble", "Cosmetics/Head/CowboyHat.blockymodel", "Cosmetics/Head/CowboyHat_Leather.png"),
             ("Gravel", "Cosmetics/Head/BowlerHat.blockymodel", "Cosmetics/Head/BowlerHat_Turquoise.png"),
             ("Flint", "Cosmetics/Head/Merchant_Hat.blockymodel", "Cosmetics/Head/Merchant_Hat_Textures/Merchant_Hat_Orange.png"),
             ("Shale", "Cosmetics/Head/Savanna_Explorer_Hat.blockymodel", "Cosmetics/Head/Savanna_Explorer_Hat_Texture.png")]
MARK_BANG, MARK_ASK = "Alerted", "Question"           # vanilla NPC emote particle systems (LifeSpan 1 s / 3 s: nothing stays)
COPPER = ["Armor_Copper_Head", "Armor_Copper_Hands", "Armor_Copper_Legs", "Armor_Copper_Chest"]
META_KEY, SET_ID = "SkyyTownProbe", "copper_quest"    # OUR metadata key on the probe's copper pieces (never SkyyGear's "SkyyGear")
GEAR_DOC_KEY = "SkyyGear"                             # read only: /townprobe copper check notes whether SkyyGear put its doc there too
TALK_FN, EVENT_KEY = "townprobe:fn:talk", "quest:fn:event"
JOBS = ["hunt.plains", "hunt.trork", "hunt.azure", "gather.logs", "gather.copper", "gather.wheat", "deliver.parcel", "craft.workbench",
        "craft.torches", "explore.outpost", "explore.headland", "hunt.elite"]          # spec 3.1, placeholders
BOARD_JOBS, BOARD_DAY_S, BOARD_ANCHOR_S = 3, 86400, 0
POLL_PLAYERS, POLL_OBJ, POLL_LIMIT_NS, POLL_DEFAULT_S = 20, 3, 500000, 30
STAMP_DIST, STAMP_R = [8, 16, 24], 3.0
STAMP_OPEN, STAMP_DONE = "Coordinate.png", "Home.png"  # vanilla map marker images (Common/UI/WorldMap/MapMarkers/)
DUP_MS, SLOT_OK_MS, MARK_EVERY_MS = 250, 5000, 3000
Q0_TITLES = ["", "NPC Use -> bridge -> dialogue page next tick", "Pebble model as an NPC (Idle / Talk / nameplate)", "Talk hint key",
             "! / ? over the head", "Two Use hooks (cancelled-early return)", "1 s reach poll (20 players x 3 objectives)",
             "Move one NPC between two spots (restart)", "Dialogue portrait (icon)", "Stamp points + map markers (owner only)",
             "quest:fn:event calls", "Boss kill by role id", "Daily board anchor (restart / world change)",
             "Copper set field survives death / Vault / Wardrobe", "ItemGridSlot plain stack in the reward preview",
             "Pebble alias + hat per town (runtime swap)", "Dialogue page open / close", "Give item + claim ledger"]
DLG_LINES = ["Oh! A visitor. Press Next to hear more, or Close to leave.",
             "Every town has a Pebble. Same rock, different hat, different name. Do not tell the others.",
             "Here is what a reward would look like. The four Copper pieces below are only a preview."]

for _r in (GOLEM,):
    if _r not in _roles:
        raise SystemExit("vanilla role %s missing (probe #11)" % _r)
for _c in COPPER:
    if _c not in _items:
        raise SystemExit("vanilla item %s missing (probe #13)" % _c)
if "BlockType" not in vanilla_json(_items[PORTRAIT_ITEM]):
    raise SystemExit("portrait item %s is not a block item" % PORTRAIT_ITEM)
for _a, _hm, _ht in DISGUISES:
    for _p in (_hm, _ht):
        if _p is not None and "Common/" + _p not in AZ_NAMES:
            raise SystemExit("hat file Common/%s missing (probe #15)" % _p)
_parts = dict((n.rsplit("/", 1)[1], n) for n in AZ_NAMES if n.endswith(".particlesystem"))
for _ps in (MARK_BANG, MARK_ASK):
    if _ps + ".particlesystem" not in _parts:
        raise SystemExit("particle system %s missing (probe #4)" % _ps)
    _pj = json.loads(az.read(_parts[_ps + ".particlesystem"]).decode("utf-8-sig"))
    if not isinstance(_pj.get("LifeSpan"), (int, float)) or _pj["LifeSpan"] > 5:
        raise SystemExit("particle system %s has no short LifeSpan (%r) - it could stay in the sky" % (_ps, _pj.get("LifeSpan")))
for _mk in (STAMP_OPEN, STAMP_DONE):
    if "Common/UI/WorldMap/MapMarkers/" + _mk not in AZ_NAMES:
        raise SystemExit("map marker image %s missing (probe #9)" % _mk)
HINT_KEYS = sorted(m.group(1) for m in re.finditer(r"(?m)^(interactionHints\.\w+)\s*=", _lang))
if any("talk" in k.lower() for k in HINT_KEYS):
    raise SystemExit("vanilla now HAS a talk hint key %r - use it (probe #3)" % [k for k in HINT_KEYS if "talk" in k.lower()])
if not re.search(r"(?m)^interactionHints\.generic\s*=", _lang):
    raise SystemExit("vanilla hint interactionHints.generic missing (probe #3)")
if re.search(r"(?m)^" + re.escape(TALK_KEY) + r"\s*=", _lang):
    raise SystemExit("vanilla server.lang already has %s" % TALK_KEY)
# our own art (art/pebble, committed; original) -> the jar, renamed under NPC/SkyyTownProbe/Pebble
PEB_FILES = {}
PEB_FILES["Common/%s/Pebble.blockymodel" % PEB_DIR] = open(os.path.join(ART, "NPC", "SkyyTowns", "Pebble", "Pebble.blockymodel"), "rb").read()
PEB_FILES["Common/%s/Pebble_Texture.png" % PEB_DIR] = open(os.path.join(ART, "NPC", "SkyyTowns", "Pebble", "Pebble_Texture.png"), "rb").read()
for _n, _rel, _loop in PEB_ANIMS:
    PEB_FILES["Common/%s/Animations/%s.blockyanim" % (PEB_DIR, _rel)] = open(os.path.join(ART, "NPC", "SkyyTowns", "Pebble", "Animations", *(_rel + ".blockyanim").split("/")), "rb").read()
_icon = open(os.path.join(ART, "Icons", "ModelsGenerated", "Pebble.png"), "rb").read()
PEB_FILES["Common/" + PEB_ICON] = _icon
PEB_FILES["Common/UI/Custom/" + PEB_UI_ICON] = _icon
_bm = json.loads(PEB_FILES["Common/%s/Pebble.blockymodel" % PEB_DIR].decode("utf-8"))
def _names(nodes, out):
    for _nd in nodes:
        out.append(_nd.get("name"))
        _names(_nd.get("children") or [], out)
    return out
PEB_NODES = _names(_bm.get("nodes") or [], [])
if "Head" not in PEB_NODES or "Origin" not in PEB_NODES:
    raise SystemExit("Pebble.blockymodel lost its Head / Origin node: %r" % PEB_NODES[:8])
for _k, _v in PEB_FILES.items():
    if _k.endswith(".png") and _v[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("%s is not a PNG" % _k)
    if _k.endswith(".blockyanim"):
        _a = json.loads(_v.decode("utf-8"))
        if "nodeAnimations" not in _a or not isinstance(_a.get("duration"), (int, float)):
            raise SystemExit("%s is not a blockyanim" % _k)
        _bad = [nn for nn in _a["nodeAnimations"] if nn not in PEB_NODES]
        if _bad:
            raise SystemExit("%s animates nodes the model does not have: %r" % (_k, _bad))
# the ModelAsset JSON: the vanilla Kweebec_Sapling.json keys only (Model, Texture, EyeHeight, HitBox, AnimationSets, Icon)
_kw = vanilla_json("Server/Models/Intelligent/Kweebec/Kweebec_Sapling.json")
for _k in ("Model", "Texture", "EyeHeight", "HitBox", "AnimationSets", "Icon"):
    if _k not in _kw:
        raise SystemExit("vanilla Kweebec_Sapling.json lost key %s - re-check the Pebble ModelAsset shape" % _k)
PEB_ASSET = {
    "Model": "%s/Pebble.blockymodel" % PEB_DIR,
    "Texture": "%s/Pebble_Texture.png" % PEB_DIR,
    "EyeHeight": 0.7,
    "HitBox": {"Max": {"X": 0.45, "Y": 1.0, "Z": 0.35}, "Min": {"X": -0.45, "Y": 0, "Z": -0.35}},
    "AnimationSets": dict((_n, {"Animations": [dict([("Animation", "%s/Animations/%s.blockyanim" % (PEB_DIR, _rel))] + ([] if _loop else [("Looping", False)]))]})
                          for _n, _rel, _loop in PEB_ANIMS),
    "Icon": PEB_ICON,
}
for _p in [PEB_ASSET["Model"], PEB_ASSET["Texture"], PEB_ASSET["Icon"]] + [s_["Animations"][0]["Animation"] for s_ in PEB_ASSET["AnimationSets"].values()]:
    if "Common/" + _p not in PEB_FILES:
        raise SystemExit("the Pebble ModelAsset names %s which the jar does not ship" % _p)
ASSET_FILES = dict(PEB_FILES)
ASSET_FILES["Server/Models/SkyyTownProbe/%s.json" % PEB_MODEL] = json.dumps(PEB_ASSET, indent=2) + "\n"
ASSET_FILES["Server/Languages/en-US/server.lang"] = "%s = Press [{key}] to talk\n" % TALK_KEY
print("desk Q0: no vanilla talk hint (%d hint keys: %s); golem %s; copper %s; %d disguises; particles %s / %s; Pebble art %d files, %d nodes"
      % (len(HINT_KEYS), ", ".join(k.split(".", 1)[1] for k in HINT_KEYS), GOLEM, "/".join(c.rsplit("_", 1)[1] for c in COPPER), len(DISGUISES),
         MARK_BANG, MARK_ASK, len(PEB_FILES), len(PEB_NODES)))

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
    # ---- 0.2 (Q0 round)
    "PTU": "com.hypixel.hytale.server.core.universe.world.ParticleUtil",
    "TP": "com.hypixel.hytale.server.core.modules.entity.teleport.Teleport",
    "R3C": "com.hypixel.hytale.math.vector.Rotation3fc",
    "V3DC": "org.joml.Vector3dc",
    "ASL": "com.hypixel.hytale.protocol.AnimationSlot",
    "WMM": "com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager",
    "MPV": "com.hypixel.hytale.server.core.universe.world.worldmap.WorldMapManager$MarkerProvider",
    "MKC": "com.hypixel.hytale.server.core.universe.world.worldmap.markers.MarkersCollector",
    "MMB": "com.hypixel.hytale.server.core.universe.world.worldmap.markers.MapMarkerBuilder",
    "TRF": "com.hypixel.hytale.math.vector.Transform",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "ODS": "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem",
    "DTH": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
    "DES": "com.hypixel.hytale.server.core.modules.entity.damage.Damage.EntitySource",   # javassist source name (dotted nested)
    "CMP": "com.hypixel.hytale.component.Component",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "BD": "org.bson.BsonDocument",
    "BSTR": "org.bson.BsonString",
    "BV": "org.bson.BsonValue",
    "MA": "com.hypixel.hytale.server.core.asset.type.model.config.ModelAttachment",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "CEB": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "IGS": "com.hypixel.hytale.server.core.ui.ItemGridSlot",
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
# 0.2 (Q0 round): every engine member the new probes use (API drift stops the build) + the exact call shapes
for c, m in ((T["PTU"], "spawnParticleEffect"), (T["TP"], "getComponentType"), (T["ASL"], "Action"), (T["ASL"], "valueOf"),
             (T["NPC"], "playAnimation"), (T["WLD"], "getWorldMapManager"), (T["WLD"], "execute"), (T["WMM"], "addMarkerProvider"),
             (T["WMM"], "getMarkerProviders"), (T["MPV"], "update"), (T["MKC"], "add"), (T["MMB"], "withCustomName"), (T["MMB"], "build"),
             (T["UNI"], "get"), (T["UNI"], "getPlayer"), (T["UNI"], "getWorld"), (T["PR"], "getReference"), (T["PR"], "getWorldUuid"),
             (T["PLA"], "getPlayerRef"), (T["PLA"], "getInventory"), (T["REF"], "getStore"), (T["ODS"], "onComponentAdded"),
             (T["DTH"], "getDeathInfo"), (T["DMG"], "getSource"), ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource", "getRef"),
             (T["INV"], "getStorage"), (T["INV"], "getHotbar"), (T["INV"], "getBackpack"), (T["INV"], "getArmor"), (T["IC"], "getCapacity"),
             (T["IC"], "getItemStack"), (T["IC"], "addItemStack"), (T["IS"], "withMetadata"), (T["IS"], "getMetadata"), (T["IS"], "getItemId"),
             (T["IS"], "isEmpty"), (T["BD"], "getString"), (T["BD"], "containsKey"), (T["MDL"], "getAttachments"), (T["MDL"], "getRandomAttachmentIds"),
             (T["MDL"], "getBoundingBox"), (T["MDL"], "getAnimationSetMap"), (T["MDL"], "getPhobiaModelAssetId"), (T["MA"], "getModel"),
             (T["MA"], "getTexture"), (T["NPL"], "getText"), (T["ITS"], "getInteractionHint"), (T["CUP"], "onDismiss"), (T["CUP"], "rebuild"),
             (T["CUP"], "close"), (T["UCB"], "appendInline"), (T["UCB"], "set"), (T["UEB"], "addEventBinding"), (T["EVD"], "of"),
             (T["EVD"], "append"), (T["CEB"], "Activating"), (T["LIFE"], "CanDismiss"), (T["IGS"], "setName"),
             ("com.hypixel.hytale.component.system.EventSystem", "shouldProcessEvent")):
    B.probe(pool, c, m)
_sig = lambda cls, name: [str(x.getSignature()) for x in pool.get(cls).getDeclaredMethods() if str(x.getName()) == name]
_csig = lambda cls: [str(x.getSignature()) for x in pool.get(cls).getDeclaredConstructors()]
if "(Ljava/lang/String;Lorg/joml/Vector3dc;Ljava/util/List;Lcom/hypixel/hytale/component/ComponentAccessor;)V" not in _sig(T["PTU"], "spawnParticleEffect"):
    raise SystemExit("ParticleUtil.spawnParticleEffect(String, Vector3dc, List, ComponentAccessor) changed")
if "(Lcom/hypixel/hytale/component/Ref;Lcom/hypixel/hytale/protocol/AnimationSlot;Ljava/lang/String;Lcom/hypixel/hytale/component/ComponentAccessor;)V" not in _sig(T["NPC"], "playAnimation"):
    raise SystemExit("NPCEntity.playAnimation(Ref, AnimationSlot, String, ComponentAccessor) changed")
if "(Lorg/joml/Vector3dc;Lcom/hypixel/hytale/math/vector/Rotation3fc;)V" not in _csig(T["TP"]):
    raise SystemExit("new Teleport(Vector3dc, Rotation3fc) changed")
if "(Ljava/lang/String;Ljava/lang/String;Lcom/hypixel/hytale/math/vector/Transform;)V" not in _csig(T["MMB"]):
    raise SystemExit("new MapMarkerBuilder(String id, String image, Transform) changed")
if "(Lcom/hypixel/hytale/server/core/universe/world/World;Lcom/hypixel/hytale/server/core/entity/entities/Player;Lcom/hypixel/hytale/server/core/universe/world/worldmap/markers/MarkersCollector;)V" not in _sig(T["MPV"], "update"):
    raise SystemExit("WorldMapManager$MarkerProvider.update(World, Player, MarkersCollector) changed")
_MCT = ("(Ljava/lang/String;FLjava/util/Map;[Lcom/hypixel/hytale/server/core/asset/type/model/config/ModelAttachment;Lcom/hypixel/hytale/math/shape/Box;"
        "Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;FFFFLjava/util/Map;Lcom/hypixel/hytale/server/core/asset/type/model/config/camera/CameraSettings;"
        "Lcom/hypixel/hytale/protocol/ColorLight;[Lcom/hypixel/hytale/server/core/asset/type/model/config/ModelParticle;[Lcom/hypixel/hytale/protocol/ModelTrail;"
        "Lcom/hypixel/hytale/server/core/modules/physics/component/PhysicsValues;Ljava/util/Map;Lcom/hypixel/hytale/protocol/Phobia;Ljava/lang/String;)V")
if _MCT not in _csig(T["MDL"]):
    raise SystemExit("the full Model constructor changed - re-check TpQ0.withHat (field order checked by bytecode 2026-10-09)")
if "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;D)V" not in _csig(T["MA"]):
    raise SystemExit("new ModelAttachment(model, texture, gradientSet, gradientId, weight) changed")
# probe #5 desk check: a cancelled ICancellableEcsEvent is never handed to a later EntityEventSystem (EventSystem.shouldProcessEvent)
_ev = pool.get("com.hypixel.hytale.component.system.EventSystem").getDeclaredMethod("shouldProcessEvent").getMethodInfo()
_evb = bytes(bytearray((x & 0xff) for x in _ev.getCodeAttribute().getCode()))
_evc = _ev.getConstPool()
_ev_refs = [str(_evc.getClassInfo(i)) for i in range(1, _evc.getSize()) if _evc.getTag(i) == 7]
_ev_meth = [str(_evc.getInterfaceMethodrefName(i)) for i in range(1, _evc.getSize()) if _evc.getTag(i) == 11]
if "com.hypixel.hytale.component.system.ICancellableEcsEvent" not in _ev_refs or "isCancelled" not in _ev_meth or 0xc1 not in _evb:
    raise SystemExit("EventSystem.shouldProcessEvent no longer skips cancelled events (%r %r) - re-check probe #5" % (_ev_refs, _ev_meth))
_hd = pool.get("com.hypixel.hytale.component.system.EntityEventSystem").getDeclaredMethod("handleInternal").getMethodInfo()
_hdc = _hd.getConstPool()
if "shouldProcessEvent" not in [str(_hdc.getMethodrefName(i)) for i in range(1, _hdc.getSize()) if _hdc.getTag(i) == 10]:
    raise SystemExit("EntityEventSystem.handleInternal no longer asks shouldProcessEvent - re-check probe #5")
HOOKS_DESK = "EventSystem.shouldProcessEvent returns false for a cancelled ICancellableEcsEvent and EntityEventSystem.handleInternal asks it first"
print("desk Q0 #5: " + HOOKS_DESK)

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
public static void chat(@PR@ pr, String s, String col) {
  try { if (SINK != null) SINK.add((col == null ? "" : col) + "|" + s); } catch (Throwable t) { }
  try {
    if (pr != null) {
      @MSG@ m = @MSG@.raw(s);
      if (col != null) m = m.color(col);
      pr.sendMessage(m);
    }
  } catch (Throwable t) { }
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
# ---- 0.2 (Q0 round): the board anchor maths (#12) - plain data, the same answer in every JVM
F(lg, "public static final String[] JOBS = %s;" % jarr(JOBS))
F(lg, "public static final int BOARD_JOBS = %d;" % BOARD_JOBS)
F(lg, "public static final long DAY_S = %dL;" % BOARD_DAY_S)
F(lg, "public static final long ANCHOR_S = %dL;" % BOARD_ANCHOR_S)
# FNV-1a 64 over the UTF-16 chars (stable across JVMs; String.hashCode is too, but 32 bits only)
M(lg, r"""
public static long fnv(String s) {
  long h = 0xcbf29ce484222325L;
  if (s == null) return h;
  for (int i = 0; i < s.length(); i++) { h = h ^ (long) s.charAt(i); h = h * 0x100000001b3L; }
  return h;
}""")
M(lg, r"""
public static long boardDay(long nowMs, long anchorS, long dayS) {
  return Math.floorDiv(nowMs / 1000L - anchorS, dayS);
}""")
M(lg, r"""
public static long boardLeftS(long nowMs, long anchorS, long dayS) {
  long t = nowMs / 1000L - anchorS;
  return dayS - Math.floorMod(t, dayS);
}""")
M(lg, r"""
public static long boardSeed(String pkey, long day) {
  return fnv(pkey + "|" + day);
}""")
# 'n' distinct job indexes: a Fisher-Yates shuffle of 0..JOBS-1 with java.util.Random(seed) (its algorithm is fixed by the JLS docs)
M(lg, r"""
public static int[] pickJobs(long seed, int n) {
  int[] all = new int[JOBS.length];
  for (int i = 0; i < all.length; i++) all[i] = i;
  java.util.Random r = new java.util.Random(seed);
  for (int i = all.length - 1; i > 0; i--) { int j = r.nextInt(i + 1); int t = all[i]; all[i] = all[j]; all[j] = t; }
  int k = Math.max(0, Math.min(n, all.length));
  int[] out = new int[k];
  for (int i = 0; i < k; i++) out[i] = all[i];
  return out;
}""")
M(lg, r"""
public static String jobText(int[] js) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < js.length; i++) { if (i > 0) sb.append(","); sb.append(JOBS[js[i]]); }
  return sb.toString();
}""")
M(lg, r"""
public static String hms(long s) {
  if (s < 0L) s = 0L;
  return (s / 3600L) + " h " + ((s / 60L) % 60L) + " m";
}""")
# 'reach' in x / z only (a stamp post is a column)
M(lg, r"""
public static boolean nearXZ(double ax, double az, double bx, double bz, double r) {
  double dx = ax - bx; double dz = az - bz;
  return dx * dx + dz * dz <= r * r;
}""")
# the next / previous entry of a cycle of n (n > 0)
M(lg, r"""
public static int cycle(int i, int n) {
  if (n <= 0) return 0;
  int k = (i + 1) % n;
  return k < 0 ? 0 : k;
}""")

# =====================================================================================================================
# TpRec: one undo record (newest last). Saved as undo/<seq>.properties (+ undo/<seq>.lpf = the snapshot when there is one).
# =====================================================================================================================
rec = mk("TpRec")
for f in ("public int seq;", "public String kind;", "public String world;", "public int ox;", "public int oy;", "public int oz;",
          "public String snap;", "public String uuids;", "public String what;", "public long time;", "public Object buf;",
          "public long dropAsk;", "public double nx;", "public double ny;", "public double nz;",
          "public double bx;", "public double by;", "public double bz;", "public String at;"):      # 0.2: spot B + where it stands (#7)
    F(rec, f)
C(rec, r"""public TpRec() { this.kind = ""; this.world = ""; this.snap = ""; this.uuids = ""; this.what = ""; this.time = 0L; this.dropAsk = 0L; this.at = ""; }""")
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
  if (this.at != null && this.at.length() > 0) sb.append("bx=").append(this.bx).append("\nby=").append(this.by).append("\nbz=").append(this.bz).append("\nat=").append(clean(this.at)).append("\n");
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
    r.bx = Double.parseDouble(p.getProperty("bx", "0").trim());
    r.by = Double.parseDouble(p.getProperty("by", "0").trim());
    r.bz = Double.parseDouble(p.getProperty("bz", "0").trim());
  } catch (Throwable t) { return null; }
  r.at = p.getProperty("at", "").trim();
  if (!r.at.equals("") && !r.at.equals("A") && !r.at.equals("B")) return null;
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
  return "npc".equals(k) || "pebble".equals(k) || "sign".equals(k) || "talker".equals(k) || "pebblem".equals(k) || "golem".equals(k) || "mark".equals(k);
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
            "public abstract @HOL@ newHolder();",
            # 0.2 (Q0 round)
            "public abstract @PR@ playerOf(java.util.UUID u);",
            "public abstract @WLD@ worldOf(@PR@ pr);",
            "public abstract void particle(String id, @V3D@ pos, java.util.List players, @ST@ st);",
            "public abstract void anim(@ST@ st, @REF@ r, String slot, String id);",
            "public abstract void teleport(@ST@ st, @REF@ r, @V3D@ pos, @R3F@ rot);",
            "public abstract void addMarkers(@WLD@ w, String key, Object provider);",
            "public abstract void removeMarkers(@WLD@ w, String key);",
            "public abstract @IC@[] conts(Object player, boolean armor);"):
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
# ---- 0.2 (Q0 round) engine lines
M(eng, r"""
public static @PR@ playerOf(java.util.UUID u) {
  if (API != null) return API.playerOf(u);
  return @UNI@.get().getPlayer(u);
}""")
M(eng, r"""
public static @WLD@ worldOf(@PR@ pr) {
  if (API != null) return API.worldOf(pr);
  java.util.UUID w = pr.getWorldUuid();
  return w == null ? null : @UNI@.get().getWorld(w);
}""")
# vanilla ParticleUtil overload with a player list: only those players get the effect (probe #4, "per player")
M(eng, r"""
public static void particle(String id, @V3D@ pos, java.util.List players, @ST@ st) {
  if (API != null) { API.particle(id, pos, players, st); return; }
  @PTU@.spawnParticleEffect(id, (@V3DC@) pos, players, (@CAC@) st);
}""")
# the vanilla NPC action route (ActionPlayAnimation.execute: NPCEntity.playAnimation(ref, slot, id, accessor))
M(eng, r"""
public static void anim(@ST@ st, @REF@ r, String slot, String id) {
  if (API != null) { API.anim(st, r, slot, id); return; }
  @NPC@ n = (@NPC@) st.getComponent(r, @NPC@.getComponentType());
  if (n == null) throw new IllegalStateException("not an NPC");
  n.playAnimation(r, @ASL@.valueOf(slot), id, (@CAC@) st);
}""")
# a Teleport component on a non-player entity = vanilla TeleportSystems$MoveSystem.onComponentAdded moves it (teleportPosition)
M(eng, r"""
public static void teleport(@ST@ st, @REF@ r, @V3D@ pos, @R3F@ rot) {
  if (API != null) { API.teleport(st, r, pos, rot); return; }
  st.putComponent(r, @TP@.getComponentType(), new @TP@((@V3DC@) pos, (@R3C@) rot));
}""")
M(eng, r"""
public static void addMarkers(@WLD@ w, String key, Object provider) {
  if (API != null) { API.addMarkers(w, key, provider); return; }
  w.getWorldMapManager().addMarkerProvider(key, (@MPV@) provider);
}""")
M(eng, r"""
public static void removeMarkers(@WLD@ w, String key) {
  if (API != null) { API.removeMarkers(w, key); return; }
  w.getWorldMapManager().getMarkerProviders().remove(key);
}""")
# storage first (the give order), then hotbar, backpack (+ armour for counting)
M(eng, r"""
public static @IC@[] conts(Object player, boolean armor) {
  if (API != null) return API.conts(player, armor);
  if (!(player instanceof @PLA@)) return new @IC@[0];
  @INV@ inv = ((@PLA@) player).getInventory();
  if (inv == null) return new @IC@[0];
  if (armor) return new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack(), inv.getArmor() };
  return new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
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
# 0.2 Q0 ROUND (research/cloud/SkyyQuests-Zone1-Spec.md section 11). TpQ0 = the shared state + the result lines; TpDlgPage = the
# dialogue page; TpOpenDlg / TpTalkFn = Use -> bridge -> next tick -> page; TpEventFn = the quest:fn:event listener; TpMarkers =
# the map markers; TpClaims = the claim ledger. The commands are in TpQ0Cmds (after TpCmds' helpers).
# =====================================================================================================================
q0 = mk("TpQ0")
F(q0, "public static final String[] TITLE = %s;" % jarr(Q0_TITLES))
F(q0, "public static final String[] STATE = new String[%d];" % len(Q0_TITLES))
F(q0, "public static final String[] DETAIL = new String[%d];" % len(Q0_TITLES))
F(q0, "public static final long BOOT = System.currentTimeMillis();")
F(q0, "public static final String TALK_FN = %s;" % json.dumps(TALK_FN))
F(q0, "public static final String EVENT_KEY = %s;" % json.dumps(EVENT_KEY))
F(q0, "public static final String PEB_MODEL = %s;" % json.dumps(PEB_MODEL))
F(q0, "public static final String TALKER_NAME = %s;" % json.dumps(TALKER_NAME))
F(q0, "public static final String GOLEM = %s;" % json.dumps(GOLEM))
F(q0, "public static final String GOLEM_NAME = %s;" % json.dumps(GOLEM_NAME))
F(q0, "public static final String PORTRAIT = %s;" % json.dumps(PORTRAIT_ITEM))
F(q0, "public static final String[] HINTS = %s;" % jarr(HINTS))
F(q0, "public static final String HINT_KEYS = %s;" % json.dumps(", ".join(HINT_KEYS)))
F(q0, "public static final String HOOKS_DESK = %s;" % json.dumps(HOOKS_DESK))
F(q0, "public static final String[] DIS_ALIAS = %s;" % jarr([d[0] for d in DISGUISES]))
F(q0, "public static final String[] DIS_HAT = %s;" % jarr([d[1] or "" for d in DISGUISES]))
F(q0, "public static final String[] DIS_TEX = %s;" % jarr([d[2] or "" for d in DISGUISES]))
F(q0, "public static final String MARK_BANG = %s;" % json.dumps(MARK_BANG))
F(q0, "public static final String MARK_ASK = %s;" % json.dumps(MARK_ASK))
F(q0, "public static final String[] COPPER = %s;" % jarr(COPPER))
F(q0, "public static final String META_KEY = %s;" % json.dumps(META_KEY))
F(q0, "public static final String SET_ID = %s;" % json.dumps(SET_ID))
F(q0, "public static final String GEAR_DOC_KEY = %s;" % json.dumps(GEAR_DOC_KEY))
F(q0, "public static final int POLL_PLAYERS = %d;" % POLL_PLAYERS)
F(q0, "public static final int POLL_OBJ = %d;" % POLL_OBJ)
F(q0, "public static final long POLL_LIMIT_NS = %dL;" % POLL_LIMIT_NS)
F(q0, "public static final int[] STAMP_DIST = %s;" % jint(STAMP_DIST))
F(q0, "public static final double STAMP_R = %s;" % STAMP_R)
F(q0, "public static final String STAMP_OPEN = %s;" % json.dumps(STAMP_OPEN))
F(q0, "public static final String STAMP_DONE = %s;" % json.dumps(STAMP_DONE))
F(q0, "public static final String MAP_KEY = \"skyytownprobe\";")
F(q0, "public static final long DUP_MS = %dL;" % DUP_MS)
F(q0, "public static final long SLOT_OK_MS = %dL;" % SLOT_OK_MS)
F(q0, "public static final long MARK_EVERY_MS = %dL;" % MARK_EVERY_MS)
for _f in ("PRESSES", "DUPS", "CALLS", "OPENS", "CANCELLED", "HOOK2_OURS", "HOOK2_OTHER", "KILLS", "EVENTS", "SELFTEST", "SHOWN", "HIDDEN",
           "CLOSES", "DISMISSES", "PAID", "ALREADY"):
    F(q0, "public static final java.util.concurrent.atomic.AtomicLong %s = new java.util.concurrent.atomic.AtomicLong();" % _f)
for _f in ("LASTUSE", "SLOT_SENT", "MAP_WORLDS"):
    F(q0, "public static final java.util.concurrent.ConcurrentHashMap %s = new java.util.concurrent.ConcurrentHashMap();" % _f)
for _f in ("public static volatile boolean KILLS_ON = false;", "public static volatile int HINT_I = -1;", "public static volatile int MARK_MODE = 0;",
           "public static volatile int DIS_I = 0;", "public static volatile java.util.UUID MARK_OWNER;", "public static volatile long MARK_NEXT = 0L;",
           "public static volatile java.util.UUID POLL_OWNER;", "public static volatile long POLL_UNTIL = 0L;", "public static long POLL_N = 0L;",
           "public static long POLL_SUM = 0L;", "public static long POLL_MAX = 0L;", "public static long POLL_SINK = 0L;", "public static int POLL_S = 0;",
           "public static volatile java.util.UUID STAMP_OWNER;", "public static volatile String STAMP_WORLD;", "public static volatile double[] STAMP_X;",
           "public static volatile double[] STAMP_Y;", "public static volatile double[] STAMP_Z;", "public static volatile boolean[] STAMP_HIT;",
           "public static volatile Object EVENT_FN;", "public static volatile Object TALK_OBJ;", "public static volatile boolean CLOSED_BTN = false;",
           "public static volatile boolean CLOSED_ESC = false;", "public static volatile boolean DISMISS_AFTER_CLOSE = false;",
           "public static boolean FAILED_ONCE = false;"):
    F(q0, _f)
M(q0, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(q0, r"""
public static java.util.function.Function fn(String key) {
  try { Object o = bridge().get(key); return o instanceof java.util.function.Function ? (java.util.function.Function) o : null; } catch (Throwable t) { return null; }
}""")
# tools/PROFILES-CONTRACT.md pkey (profile 1 / no SkyyProfiles = the UUID)
M(q0, r"""
public static String pkey(java.util.UUID u) {
  try {
    java.util.function.Function f = fn("profile:fn:key");
    if (f != null) {
      Object r = f.apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(q0, r"""
public static java.nio.file.Path logFile() {
  return @PKG@.TpStore.DIR == null ? null : @PKG@.TpStore.DIR.resolve("q0-results.log");
}""")
# the probe's own result log (append only; the board probe reads it back)
M(q0, r"""
public static void append(String line) {
  try {
    java.nio.file.Path p = logFile();
    if (p == null) return;
    java.nio.file.Files.createDirectories(p.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String t = java.time.LocalDateTime.now().withNano(0).toString() + " " + @PKG@.TpRec.clean(line) + "\n";
    java.nio.file.Files.write(p, t.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable e) { @PKG@.TpLog.warn("could not write q0-results.log: " + e); }
}""")
M(q0, r"""
public static java.util.List readLog() {
  try {
    java.nio.file.Path p = logFile();
    if (p == null || !java.nio.file.Files.isRegularFile(p, new java.nio.file.LinkOption[0])) return new java.util.ArrayList();
    return java.nio.file.Files.readAllLines(p, java.nio.charset.StandardCharsets.UTF_8);
  } catch (Throwable e) { @PKG@.TpLog.warn("could not read q0-results.log: " + e); return new java.util.ArrayList(); }
}""")
M(q0, r"""
public static String colOf(String state) {
  if ("PASS".equals(state)) return "@COLOK@";
  if ("FAIL".equals(state)) return "@COLERR@";
  return "@COLINF@";
}""")
M(q0, r"""
public static boolean admin(@PR@ pr) {
  try { return pr != null && pr.hasPermission("@NODE@"); } catch (Throwable t) { return false; }
}""")
# ONE result line: server log + chat + q0-results.log. The same state + text again = server log only (no chat spam, no file line).
# FIX: a NON-admin (kill / event / F on a probe NPC) = server log only; a repeated #10 / #11 WAIT (detail = a running count) = server log only.
M(q0, r"""
public static void res(@PR@ pr, int n, String state, String detail) {
  if (n <= 0 || n >= TITLE.length) return;
  String line = "Q0 #" + n + " " + TITLE[n] + ": " + state + " - " + detail;
  boolean same = state.equals(STATE[n]) && detail.equals(DETAIL[n]);
  boolean rep = (n == 10 || n == 11) && "WAIT".equals(state) && "WAIT".equals(STATE[n]);
  STATE[n] = state;
  DETAIL[n] = detail;
  boolean adm = admin(pr);
  @PKG@.TpLog.info(line + (adm ? "" : " (non-admin " + (pr == null ? "?" : pr.getUsername()) + ": server log only)"));
  if (same || rep || !adm) return;
  append(line);
  @PKG@.TpLog.chat(pr, "#" + n + " " + TITLE[n] + ": " + state + " - " + detail, colOf(state));
}""")
# report fallback: the newest q0-results.log line of probe n -> {state, detail, time} (null = none); the log line is
# "<time> Q0 #n <title>: <STATE> - <detail>" (TpQ0.append)
M(q0, r"""
public static String[] fromLog(java.util.List lg, int n) {
  if (lg == null) return null;
  String p = @PKG@.TpRec.clean("Q0 #" + n + " " + TITLE[n] + ": ");
  for (int i = lg.size() - 1; i >= 0; i--) {
    String x = (String) lg.get(i);
    int k = x == null ? -1 : x.indexOf(p);
    if (k < 0) continue;
    String rest = x.substring(k + p.length());
    int dash = rest.indexOf(" - ");
    if (dash <= 0) continue;
    String st = rest.substring(0, dash);
    if (!st.equals("PASS") && !st.equals("FAIL") && !st.equals("WAIT")) continue;
    return new String[] { st, rest.substring(dash + 3), x.substring(0, k).trim() };
  }
  return null;
}""")
M(q0, r"""
public static void report(@PR@ pr) {
  @PKG@.TpLog.tell(pr, "Q0 probe results (every line is also in the server log as [SkyyTownProbe] Q0 #n ...):", "@COLINF@");
  int pass = 0; int fail = 0; int wait = 0; int none = 0; int old = 0;
  java.util.List lg = null;
  for (int n = 1; n < TITLE.length; n++) {
    String s = STATE[n];
    String d = DETAIL[n];
    String src = "";
    if (s == null) {
      if (lg == null) lg = readLog();
      String[] f = fromLog(lg, n);
      if (f != null) { s = f[0]; d = f[1]; src = " (from q0-results.log, " + f[2] + ")"; old++; }
    }
    if (s == null) { none++; @PKG@.TpLog.tell(pr, "#" + n + " " + TITLE[n] + ": not run yet", null); continue; }
    if (s.equals("PASS")) pass++; else if (s.equals("FAIL")) fail++; else wait++;
    @PKG@.TpLog.tell(pr, "#" + n + " " + TITLE[n] + ": " + s + " - " + d + src, colOf(s));
  }
  @PKG@.TpLog.info("Q0 REPORT: " + pass + " PASS, " + fail + " FAIL, " + wait + " WAIT (Skyy's eyes / more steps), " + none + " not run; " + old + " read back from q0-results.log (no result since this start)");
}""")
M(q0, r"""
public static boolean active() {
  return POLL_OWNER != null || STAMP_OWNER != null || (MARK_MODE == 3 && MARK_OWNER != null) || !SLOT_SENT.isEmpty();
}""")
M(q0, r"""
public static boolean isTalker(String k) {
  return "talker".equals(k) || "pebble".equals(k) || "pebblem".equals(k);
}""")
M(q0, r"""
public static boolean isPebble(String k) {
  return "pebble".equals(k) || "pebblem".equals(k);
}""")
M(q0, r"""
public static String alias() {
  int i = DIS_I;
  if (i < 0 || i >= DIS_ALIAS.length) i = 0;
  return DIS_ALIAS[i];
}""")
# the name an NPC shows now (alias for Pebble, marker prefix in marker mode 1)
M(q0, r"""
public static String nameOf(@PKG@.TpRec r) {
  String base;
  if ("talker".equals(r.kind)) base = TALKER_NAME;
  else if ("golem".equals(r.kind)) base = GOLEM_NAME;
  else if (isPebble(r.kind)) base = alias();
  else base = r.kind;
  if (MARK_MODE == 1 && isTalker(r.kind)) return ("talker".equals(r.kind) ? "? " : "! ") + base;
  return base;
}""")
M(q0, r"""
public static @PKG@.TpRec findRec(String key) {
  java.util.Iterator it = @PKG@.TpStore.NPCS.values().iterator();
  while (it.hasNext()) {
    @PKG@.TpRec r = (@PKG@.TpRec) it.next();
    if ((r.kind + ":" + r.seq).equals(key)) return r;
  }
  return null;
}""")
# the records of these kinds in this world, oldest first
M(q0, r"""
public static java.util.ArrayList recs(String world, String[] kinds) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.TpStore.RECS.size(); i++) {
    @PKG@.TpRec r = (@PKG@.TpRec) @PKG@.TpStore.RECS.get(i);
    if (!r.world.equals(world)) continue;
    for (int k = 0; k < kinds.length; k++) if (kinds[k].equals(r.kind)) { out.add(r); break; }
  }
  return out;
}""")
M(q0, r"""
public static @REF@ refOf(@WLD@ w, @PKG@.TpRec r) {
  String[] us = r.uuidList();
  return us.length == 0 ? null : @PKG@.TpNpc.find(w, us[0]);
}""")
M(q0, r"""
public static boolean isProbeHat(String model) {
  if (model == null) return false;
  for (int i = 0; i < DIS_HAT.length; i++) if (DIS_HAT[i].length() > 0 && DIS_HAT[i].equals(model)) return true;
  return false;
}""")
# a COPY of the live Model with our hat attachment swapped (every other field as it was; the field order of the full constructor is
# checked against the bytecode at build time). PersistentModel is not touched: after a restart the asset's own look comes back.
M(q0, r"""
public static @MDL@ withHat(@MDL@ m, String hat, String tex) {
  @MA@[] old = m.getAttachments();
  java.util.ArrayList keep = new java.util.ArrayList();
  for (int i = 0; old != null && i < old.length; i++) if (old[i] != null && !isProbeHat(old[i].getModel())) keep.add(old[i]);
  if (hat != null && hat.length() > 0) keep.add(new @MA@(hat, tex, (String) null, (String) null, 1.0));
  @MA@[] a = new @MA@[keep.size()];
  for (int i = 0; i < a.length; i++) a[i] = (@MA@) keep.get(i);
  return new @MDL@(m.getModelAssetId(), m.getScale(), m.getRandomAttachmentIds(), a, m.getBoundingBox(), m.getModel(), m.getTexture(),
      m.getGradientSet(), m.getGradientId(), m.getEyeHeight(), m.getCrouchOffset(), m.getSittingOffset(), m.getSleepingOffset(),
      m.getAnimationSetMap(), m.getCamera(), m.getLight(), m.getParticles(), m.getTrails(), m.getPhysicsValues(), m.getDetailBoxes(),
      m.getPhobia(), m.getPhobiaModelAssetId());
}""")
M(q0, r"""
public static String attText(@MDL@ m) {
  if (m == null) return "no model";
  @MA@[] a = m.getAttachments();
  StringBuilder sb = new StringBuilder();
  sb.append(a == null ? 0 : a.length).append(" attachments");
  for (int i = 0; a != null && i < a.length; i++) {
    String p = a[i] == null || a[i].getModel() == null ? "?" : a[i].getModel();
    if (p.lastIndexOf('/') >= 0) p = p.substring(p.lastIndexOf('/') + 1);
    sb.append(i == 0 ? ": " : ", ").append(p);
  }
  return sb.toString();
}""")
# NPCs of our Pebble models within r of (x, y, z) (the 'one Pebble, not two' count of #7)
M(q0, r"""
public static int countPebbles(@ST@ st, double x, double y, double z, double r) {
  int n = 0;
  try {
    java.util.List l = com.hypixel.hytale.server.core.util.TargetUtil.getAllEntitiesInSphere(new @V3D@(x, y, z), r, (@CAC@) st);
    for (int i = 0; l != null && i < l.size(); i++) {
      @REF@ e = (@REF@) l.get(i);
      if (e == null || !e.isValid()) continue;
      if (st.getComponent(e, @NPC@.getComponentType()) == null) continue;
      String id = @PKG@.TpNpc.modelId(st, e);
      if (id.startsWith(PEB_MODEL + " ") || id.startsWith(@PKG@.TpNpc.ROCK + " ")) n++;
    }
  } catch (Throwable t) { @PKG@.TpLog.warn("pebble count failed: " + t); return -1; }
  return n;
}""")
# our Pebble as an ANIMATED model: Model.createScaledModel(asset, 1) (createStaticScaledModel = isStatic true = no animation sets,
# fine for the 0.1 rock prop, wrong for Pebble - harness E2 checks both)
M(q0, r"""
public static @MDL@ pebbleModel() {
  try {
    @MDA@ a = (@MDA@) @MDA@.getAssetMap().getAsset(PEB_MODEL);
    return a == null ? null : @MDL@.createScaledModel(a, 1.0f);
  } catch (Throwable t) { @PKG@.TpLog.warn("model " + PEB_MODEL + " failed: " + t); return null; }
}""")
M(q0, r"""
public static String us(long nanos) {
  long t = nanos / 100L;
  return (t / 10L) + "." + (t % 10L) + " us";
}""")

# ---- the dialogue page (#1 / #8 / #14 / #16): the vanilla kit look, inline, built from tools/skyyui.py
dlg = mk("TpDlgPage", T["CUP"])
DPW, DPH = 900, 600
DSH = SUI.page_shell("SkyyTpDlg", DPW, DPH, SUI.J("this.name", "Fennel"), body_id="SkyyTpDlgBody")
DIW = DSH.inner_w
D_TOP_H, D_SEC_H, D_STATUS_H, D_FOOT_H = 116, 30, 30, SUI.BTN_H + 8
D_PORT = 104
D_GRID_H = SUI.GRID_SLOT + 2 * SUI.GRID_WELL_PAD
D_LEFT = DSH.fit([D_TOP_H, 12, D_SEC_H, D_GRID_H, 12, D_STATUS_H, D_FOOT_H], "dialogue page")
DLG_TEXT_W = DIW - 2 * D_PORT - 2 * 12


def dlg_java():
    ap = SUI.Appends()
    ap.add(DSH.body, SUI.group("SkyyTpDlgTop", "Left", h=D_TOP_H))
    ap.add("SkyyTpDlgTop", SUI.item_frame("SkyyTpDlgP1", size=D_PORT, item=PORTRAIT_ITEM))
    ap.add("SkyyTpDlgTop", SUI.spacer(w=12))
    # probe #8: OUR icon png from the jar (Common/UI/Custom/SkyyTownProbe/Pebble.png) as a Group Background - UNVERIFIED on purpose
    ap.add("SkyyTpDlgTop", 'Group #SkyyTpDlgP2 { Anchor: (Width: %d, Height: %d); Background: "%s"; }' % (D_PORT, D_PORT, PEB_UI_ICON))  # ui-data (probe #8)
    ap.add("SkyyTpDlgTop", SUI.spacer(w=12))
    ap.text("SkyyTpDlgTop", "SkyyTpDlgLine", SUI.J("line", DLG_LINES[0]), "default", w=DLG_TEXT_W, h=D_TOP_H, wrap=True, max_lines=4)
    ap.add(DSH.body, SUI.spacer(h=12))
    ap.text(DSH.body, "SkyyTpDlgSec", "Reward preview", "section", h=D_SEC_H)
    ap.add(DSH.body, SUI.item_grid("SkyyTpDlgGrid", 4, 1, tooltips=False))
    ap.add(DSH.body, SUI.spacer(h=12))
    ap.add(DSH.body, SUI.status_line("SkyyTpDlgStatus", h=D_STATUS_H))
    used = 3 * SUI.BTN_MIN_W + 2 * 6
    ap.add(DSH.body, SUI.button_row("SkyyTpDlgFoot", align="right", used=used, avail=DIW))
    ap.add("SkyyTpDlgFoot", SUI.button("SkyyTpDlgNext", "Next", "primary"))
    ap.add("SkyyTpDlgFoot", SUI.button("SkyyTpDlgAccept", "Accept", "secondary", anchor={"left": 6}))
    ap.add("SkyyTpDlgFoot", SUI.button("SkyyTpDlgClose", "Close", "secondary", sound="cancel", anchor={"left": 6}))
    grid = SUI.java_grid_fill("SkyyTpDlgGrid", [(c, 1) for c in COPPER], var="rewardSlots")
    return DSH.java("b") + "\n" + ap.java("b") + "\n" + grid


DLG_JAVA = dlg_java()
if not SUI.item_grid_java_is_safe(DLG_JAVA):
    raise SystemExit("the dialogue page's ItemGridSlot Java is not new ItemGridSlot(new ItemStack(id, qty))")
for _f in ("public String key;", "public String name;", "public int step;", "public String info;", "public boolean closing;",
           "public static final java.util.concurrent.atomic.AtomicLong BUILDS = new java.util.concurrent.atomic.AtomicLong();",
           "public static final java.util.concurrent.atomic.AtomicLong CLICKS = new java.util.concurrent.atomic.AtomicLong();"):
    F(dlg, _f)
F(dlg, "public static final String[] LINES = %s;" % jarr(DLG_LINES))
C(dlg, r"""
public TpDlgPage(@PR@ pr, String key, String name) {
  super(pr, @LIFE@.CanDismiss);
  this.key = key; this.name = name; this.step = 0; this.info = ""; this.closing = false;
}""")
for _l in SUI.java_status_methods():
    M(dlg, _l)
M(dlg, r"""
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
  while (i < data.length() && sb.length() < 100) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(dlg, "public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {\n"
       "  BUILDS.incrementAndGet();\n"
       "  String line = LINES[Math.max(0, Math.min(this.step, LINES.length - 1))];\n"
       + "\n".join("  " + l for l in DLG_JAVA.split("\n")) + "\n"
       "  b.set(\"#SkyyTpDlgStatus.Text\", textOf(this.info));\n"
       "  ev.addEventBinding(@CEB@.Activating, \"#SkyyTpDlgNext\", @EVD@.of(\"a\", \"next\"));\n"
       "  ev.addEventBinding(@CEB@.Activating, \"#SkyyTpDlgAccept\", @EVD@.of(\"a\", \"accept\"));\n"
       "  ev.addEventBinding(@CEB@.Activating, \"#SkyyTpDlgClose\", @EVD@.of(\"a\", \"close\"));\n"
       "}")
# Close button vs Esc (onDismiss) for #16; onDismiss after our own close() is noted, not counted as Esc
M(q0, r"""
public static void closed(@PR@ pr, boolean button) {
  if (button) { CLOSED_BTN = true; CLOSES.incrementAndGet(); } else { CLOSED_ESC = true; DISMISSES.incrementAndGet(); }
  String d = "Close button " + CLOSES.get() + "x, Esc " + DISMISSES.get() + "x" + (DISMISS_AFTER_CLOSE ? " (onDismiss also runs after the page closes itself)" : "");
  if (CLOSED_BTN && CLOSED_ESC) res(pr, 16, "PASS", "the page closes both ways: " + d);
  else res(pr, 16, "WAIT", d + " - now close it the " + (CLOSED_BTN ? "Esc" : "Close button") + " way (F on Fennel / Pebble again)");
}""")
M(dlg, r"""
public void onDismiss(@REF@ ref, @ST@ st) {
  if (this.closing) { @PKG@.TpQ0.DISMISS_AFTER_CLOSE = true; @PKG@.TpLog.info("Q0 dialogue: onDismiss after the Close button (close() calls it too)"); return; }
  @PKG@.TpLog.info("Q0 dialogue: " + this.playerRef.getUsername() + " closed the page with Esc (onDismiss)");
  @PKG@.TpQ0.closed(this.playerRef, false);
}""")
M(dlg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  CLICKS.incrementAndGet();
  String a = jsonStr(data, "a");
  try {
    if (a.equals("close")) {
      @PKG@.TpLog.info("Q0 dialogue: " + this.playerRef.getUsername() + " pressed Close");
      this.closing = true;
      @PKG@.TpQ0.closed(this.playerRef, true);
      close();
      return;
    }
    if (a.equals("next")) { this.step = (this.step + 1) % LINES.length; this.info = "=Line " + (this.step + 1) + " of " + LINES.length + "."; }
    else if (a.equals("accept")) { this.info = "+Accepted. (A probe - nothing is saved.)"; @PKG@.TpLog.info("Q0 dialogue: " + this.playerRef.getUsername() + " pressed Accept on " + this.key); }
    else this.info = "";
  } catch (Throwable t) { @PKG@.TpLog.warn("dialogue click " + a + " failed: " + t); this.info = "-Something went wrong (server log)."; }
  rebuild();
}""")
# ---- #1: opens the page (the next tick: World.execute from the bridge function)
opn = mk("TpOpenDlg")
opn.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public String key;", "public long t0;"):
    F(opn, _f)
C(opn, "public TpOpenDlg(@PR@ pr, String key, long t0) { this.pr = pr; this.key = key; this.t0 = t0; }")
M(opn, r"""
public void run() {
  try {
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) { @PKG@.TpQ0.res(this.pr, 1, "FAIL", "the player was gone on the next tick"); return; }
    @ST@ st = r.getStore();
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) { @PKG@.TpQ0.res(this.pr, 1, "FAIL", "no Player component on the next tick"); return; }
    @PKG@.TpRec rec = @PKG@.TpQ0.findRec(this.key);
    String nm = rec == null ? "?" : @PKG@.TpQ0.nameOf(rec);
    p.getPageManager().openCustomPage(r, st, new @PKG@.TpDlgPage(this.pr, this.key, nm));
    long opens = @PKG@.TpQ0.OPENS.incrementAndGet();
    @PKG@.TpQ0.SLOT_SENT.put(this.pr.getUuid(), Long.valueOf(System.currentTimeMillis()));
    long presses = @PKG@.TpQ0.PRESSES.get() - @PKG@.TpQ0.DUPS.get();
    String d = "the page opened on the next tick (" + @PKG@.TpLogic.ms(System.nanoTime() - this.t0) + " after the bridge call) for " + nm + "; F presses " + presses
        + " (+ " + @PKG@.TpQ0.DUPS.get() + " duplicate Use events suppressed), bridge calls " + @PKG@.TpQ0.CALLS.get() + ", pages opened " + opens + " - and no vanilla trade window? (Skyy)";
    @PKG@.TpQ0.res(this.pr, 1, opens == presses ? "PASS" : "FAIL", d);
    @PKG@.TpQ0.res(this.pr, 8, "WAIT", "two portraits on the page: LEFT = an ItemIcon of " + @PKG@.TpQ0.PORTRAIT + " (the control), RIGHT = the Pebble icon png from this jar - which ones show?");
    @PKG@.TpQ0.res(this.pr, 14, "WAIT", "the reward row holds 4 plain Copper stacks (no metadata) - PASS comes by itself if you are still connected 5 s later");
    if (!(@PKG@.TpQ0.CLOSED_BTN && @PKG@.TpQ0.CLOSED_ESC)) @PKG@.TpQ0.res(this.pr, 16, "WAIT", "page open - press Next, then Close; next time close it with Esc");
  } catch (Throwable t) { @PKG@.TpQ0.res(this.pr, 1, "FAIL", "the page did not open: " + t); }
}""")
# ---- the bridge function townprobe:fn:talk = the quest:fn:talk shape: Function(Object[] {UUID, String npcId}) -> Boolean
tfn = mk("TpTalkFn")
tfn.addInterface(pool.get("java.util.function.Function"))
C(tfn, "public TpTalkFn() { }")
M(tfn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || a[1] == null) return Boolean.FALSE;
    @PR@ pr = @PKG@.TpEng.playerOf((java.util.UUID) a[0]);
    if (pr == null) return Boolean.FALSE;
    @WLD@ w = @PKG@.TpEng.worldOf(pr);
    if (w == null) return Boolean.FALSE;
    @PKG@.TpQ0.CALLS.incrementAndGet();
    w.execute(new @PKG@.TpOpenDlg(pr, String.valueOf(a[1]), System.nanoTime()));
    return Boolean.TRUE;
  } catch (Throwable t) { @PKG@.TpLog.warn("townprobe:fn:talk failed: " + t); return Boolean.FALSE; }
}""")
# ---- #10: the quest:fn:event listener (only while nobody else owns the key)
efn = mk("TpEventFn")
efn.addInterface(pool.get("java.util.function.Function"))
C(efn, "public TpEventFn() { }")
M(efn, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof Object[])) { @PKG@.TpLog.info("Q0 #10: quest:fn:event called with " + o + " (not Object[])"); return Boolean.FALSE; }
    Object[] a = (Object[]) o;
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < a.length; i++) sb.append(i == 0 ? "" : ", ").append(String.valueOf(a[i]));
    String kind = a.length > 1 ? String.valueOf(a[1]) : "";
    if (kind.equals("townprobe:selftest")) { @PKG@.TpQ0.SELFTEST.incrementAndGet(); return Boolean.TRUE; }
    long n = @PKG@.TpQ0.EVENTS.incrementAndGet();
    @PR@ pr = a.length > 0 && a[0] instanceof java.util.UUID ? @PKG@.TpEng.playerOf((java.util.UUID) a[0]) : null;
    @PKG@.TpQ0.res(pr, 10, a.length >= 4 ? "PASS" : "FAIL", "event " + n + " reached the quest bridge: {" + sb + "}" + (a.length >= 4 ? "" : " - fewer than the 4 values {UUID, kind, key, amount}"));
    return Boolean.TRUE;
  } catch (Throwable t) { @PKG@.TpLog.warn("quest:fn:event listener failed: " + t); return Boolean.FALSE; }
}""")
# ---- #9: the map markers (WorldMapManager thread): the 3 stamp points for their owner only
mpv = mk("TpMarkers")
mpv.addInterface(pool.get(T["MPV"]))
F(mpv, "public static boolean FAILED_ONCE = false;")
C(mpv, "public TpMarkers() { }")
M(mpv, r"""
public void update(@WLD@ world, @PLA@ player, @MKC@ col) {
  try {
    java.util.UUID own = @PKG@.TpQ0.STAMP_OWNER;
    double[] xs = @PKG@.TpQ0.STAMP_X; double[] ys = @PKG@.TpQ0.STAMP_Y; double[] zs = @PKG@.TpQ0.STAMP_Z; boolean[] hit = @PKG@.TpQ0.STAMP_HIT;
    if (own == null || xs == null || ys == null || zs == null || hit == null || world == null || player == null) return;
    if (!world.getName().equals(@PKG@.TpQ0.STAMP_WORLD)) return;
    @PR@ pr = player.getPlayerRef();
    if (pr == null || !own.equals(pr.getUuid())) { @PKG@.TpQ0.HIDDEN.incrementAndGet(); return; }
    for (int i = 0; i < xs.length; i++) {
      @TRF@ t = new @TRF@((@V3DC@) new @V3D@(xs[i], ys[i], zs[i]));
      col.add(new @MMB@("SkyyTownProbeStamp" + i, hit[i] ? @PKG@.TpQ0.STAMP_DONE : @PKG@.TpQ0.STAMP_OPEN, t).withCustomName("Stamp " + (i + 1) + (hit[i] ? " (stamped)" : "")).build());
    }
    @PKG@.TpQ0.SHOWN.incrementAndGet();
  } catch (Throwable t) { if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("map markers failed (logged once): " + t); } }
}""")
# ---- #13 / #17: the claim ledger (Skyy_SkyyTownProbe/claims.properties: one "claim=<itemId>|<grantId>" line per owed item + one
# "issued=<grantId>" line per grant ever written, so a set is never issued twice; grant = <pkey>:copper:<n>)
clm = mk("TpClaims")
M(clm, r"""
public static java.nio.file.Path file() {
  return @PKG@.TpStore.DIR == null ? null : @PKG@.TpStore.DIR.resolve("claims.properties");
}""")
M(clm, r"""
public static java.util.ArrayList readKey(String key, boolean bar) {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.nio.file.Path p = file();
    if (p == null || !java.nio.file.Files.isRegularFile(p, new java.nio.file.LinkOption[0])) return out;
    java.util.List l = java.nio.file.Files.readAllLines(p, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < l.size(); i++) {
      String s = ((String) l.get(i)).trim();
      if (!s.startsWith(key)) continue;
      String v = s.substring(key.length());
      if (bar ? v.indexOf('|') > 0 : (v.length() > 0 && v.indexOf('|') < 0)) out.add(v);
    }
  } catch (Throwable t) { @PKG@.TpLog.warn("could not read claims.properties: " + t); }
  return out;
}""")
M(clm, r"""
public static java.util.ArrayList read() {
  return readKey("claim=", true);
}""")
M(clm, r"""
public static java.util.ArrayList readIssued() {
  return readKey("issued=", false);
}""")
# ONE atomic write of the whole ledger (tmp + move); an empty ledger deletes the file (and the probe folder when nothing else is left)
M(clm, r"""
public static boolean write2(java.util.ArrayList l, java.util.ArrayList iss) {
  java.nio.file.Path p = file();
  if (p == null) return false;
  if (l.isEmpty() && iss.isEmpty()) { @PKG@.TpStore.deleteQuiet(p); if (@PKG@.TpStore.DIR != null && @PKG@.TpStore.isEmptyDir(@PKG@.TpStore.DIR)) @PKG@.TpStore.deleteQuiet(@PKG@.TpStore.DIR); return true; }
  StringBuilder sb = new StringBuilder("# SkyyTownProbe Q0 claim ledger (probe #17): one claim line per owed item (/townprobe claim pays the caller's own) + one issued line per grant ever written (/townprobe copper reset clears yours)\n");
  for (int i = 0; i < l.size(); i++) sb.append("claim=").append(@PKG@.TpRec.clean((String) l.get(i))).append("\n");
  for (int i = 0; i < iss.size(); i++) sb.append("issued=").append(@PKG@.TpRec.clean((String) iss.get(i))).append("\n");
  return @PKG@.TpStore.writeText(p, sb.toString());
}""")
# the claim lines only; the issued= lines on disk are kept as they are
M(clm, r"""
public static boolean write(java.util.ArrayList l) {
  if (file() == null) return false;
  return write2(l, readIssued());
}""")
M(clm, r"""
public static @BD@ doc(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return null;
    @BD@ m = s.getMetadata();
    if (m == null || !m.containsKey(@PKG@.TpQ0.META_KEY)) return null;
    return m.getDocument(@PKG@.TpQ0.META_KEY);
  } catch (Throwable t) { return null; }
}""")
M(clm, r"""
public static String field(@BD@ d, String k) {
  try { return d == null || !d.containsKey(k) ? "" : d.getString(k).getValue(); } catch (Throwable t) { return ""; }
}""")
M(clm, r"""
public static int countGrant(@IC@ c, String grant) {
  if (c == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (grant.equals(field(doc(it), "grant"))) n += it.getQuantity();
  }
  return n;
}""")
M(clm, r"""
public static int countGrantAll(Object player, String grant) {
  @IC@[] cs = @PKG@.TpEng.conts(player, true);
  int n = 0;
  for (int i = 0; i < cs.length; i++) n += countGrant(cs[i], grant);
  return n;
}""")
M(clm, r"""
public static @IS@ stack(String id, String grant) {
  @BD@ d = new @BD@();
  d.put("set", new @BSTR@(@PKG@.TpQ0.SET_ID));
  d.put("grant", new @BSTR@(grant));
  return new @IS@(id, 1).withMetadata(@PKG@.TpQ0.META_KEY, (@BV@) d);
}""")
# one item, storage first, every add measured by re-counting that container (never trusting the transaction)
M(clm, r"""
public static int give(Object player, String id, String grant) {
  @IC@[] cs = @PKG@.TpEng.conts(player, false);
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    int before = countGrant(cs[c], grant);
    try { cs[c].addItemStack(stack(id, grant)); } catch (Throwable t) { @PKG@.TpLog.warn("addItemStack " + id + " failed: " + t); continue; }
    if (countGrant(cs[c], grant) > before) return 1;
  }
  return 0;
}""")
M(clm, r"""
public static boolean mine(String v, String pk) {
  return v != null && pk != null && v.indexOf('|') > 0 && v.substring(v.indexOf('|') + 1).startsWith(pk + ":");
}""")
M(clm, r"""
public static int countMine(java.util.ArrayList l, int from, String pk) {
  int n = 0;
  for (int i = from; i < l.size(); i++) if (mine((String) l.get(i), pk)) n++;
  return n;
}""")
# pays the CALLER's own ledger lines (grant starts with pkey + ":") in order; answers {paid, kept, already, others}. Other players' /
# profiles' lines stay in the ledger untouched and are not counted as waiting. A grant already on an item = removed without a
# second item (dupe guard). static synchronized: every ledger read-change-write (pay / issue / reset) holds the TpClaims class lock.
M(clm, r"""
public static synchronized int[] pay(Object player, String pk) {
  java.util.ArrayList l = read();
  int paid = 0; int kept = 0; int already = 0;
  int others = l.size() - countMine(l, 0, pk);
  int i = 0;
  while (i < l.size()) {
    String v = (String) l.get(i);
    if (!mine(v, pk)) { i++; continue; }
    String id = v.substring(0, v.indexOf('|'));
    String grant = v.substring(v.indexOf('|') + 1);
    if (countGrantAll(player, grant) > 0) {
      l.remove(i); write(l); already++; @PKG@.TpQ0.ALREADY.incrementAndGet();
      @PKG@.TpLog.info("Q0 #17 claim " + grant + " (" + id + "): already granted (the item is in the bags) - line removed, NO second item");
      continue;
    }
    if (give(player, id, grant) == 1) {
      l.remove(i); write(l); paid++; @PKG@.TpQ0.PAID.incrementAndGet();
      @PKG@.TpLog.info("Q0 #17 claim " + grant + " (" + id + "): PAID (count before / after +1), line removed");
      continue;
    }
    kept = countMine(l, i, pk);
    @PKG@.TpLog.info("Q0 #17 claim " + grant + " (" + id + "): bag full - claim KEPT (" + kept + " waiting)");
    break;
  }
  if (others > 0) @PKG@.TpLog.info("Q0 #17: " + others + " ledger lines belong to another player / profile - left alone");
  return new int[] { paid, kept, already, others };
}""")
# writes the caller's missing Copper claims in ONE atomic write; answers {added, have, refused, ok, older}. A grant that was ever
# issued (issued= line) is never written again (pieces in the Vault / Wardrobe / dropped on death) until /townprobe copper reset.
M(clm, r"""
public static synchronized int[] issue(Object player, String pk) {
  java.util.ArrayList l = read();
  java.util.ArrayList iss = readIssued();
  int added = 0; int have = 0; int refused = 0; boolean dirty = false;
  for (int i = 0; i < @PKG@.TpQ0.COPPER.length; i++) {
    String g = pk + ":copper:" + (i + 1);
    boolean listed = false;
    for (int k = 0; k < l.size(); k++) if (((String) l.get(k)).endsWith("|" + g)) listed = true;
    if (listed) { if (!iss.contains(g)) { iss.add(g); dirty = true; } continue; }
    if (countGrantAll(player, g) > 0) { have++; if (!iss.contains(g)) { iss.add(g); dirty = true; } continue; }
    if (iss.contains(g)) { refused++; continue; }
    l.add(@PKG@.TpQ0.COPPER[i] + "|" + g);
    iss.add(g);
    added++; dirty = true;
  }
  boolean ok = !dirty || write2(l, iss);
  return new int[] { added, have, refused, ok ? 1 : 0, l.size() - added };
}""")
# /townprobe copper reset: removes the caller's own claim + issued lines (others' stay); answers {claims, issued} removed
M(clm, r"""
public static synchronized int[] reset(String pk) {
  java.util.ArrayList l = read();
  java.util.ArrayList iss = readIssued();
  int a = 0; int b = 0;
  for (int i = l.size() - 1; i >= 0; i--) if (mine((String) l.get(i), pk)) { l.remove(i); a++; }
  for (int i = iss.size() - 1; i >= 0; i--) if (((String) iss.get(i)).startsWith(pk + ":")) { iss.remove(i); b++; }
  if (a + b > 0) write2(l, iss);
  return new int[] { a, b };
}""")
# ---- the per-second part of TpTick for the Q0 probes (#14 still connected, #6 poll, #9 stamps, #4 particles)
M(q0, r"""
public static void pollStep(@PR@ pr, @REF@ ref, @ST@ st, long now) {
  long t0 = System.nanoTime();
  long hits = 0L;
  for (int p = 0; p < POLL_PLAYERS; p++) {
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null) continue;
    @V3D@ pos = tc.getPosition();
    for (int o = 0; o < POLL_OBJ; o++) {
      double ox = pos.x + 10.0 * (o + 1) + p; double oz = pos.z - 7.0 * o;
      if (@PKG@.TpLogic.near(pos.x, pos.y, pos.z, ox, pos.y, oz, 3.0)) hits++;
    }
  }
  long dt = System.nanoTime() - t0;
  POLL_SINK = POLL_SINK + hits;
  POLL_N = POLL_N + 1L;
  POLL_SUM = POLL_SUM + dt;
  if (dt > POLL_MAX) POLL_MAX = dt;
  if (now < POLL_UNTIL) return;
  long avg = POLL_N == 0L ? 0L : POLL_SUM / POLL_N;
  POLL_OWNER = null;
  res(pr, 6, avg < POLL_LIMIT_NS ? "PASS" : "FAIL", "average " + us(avg) + ", max " + us(POLL_MAX) + " per 1 s poll over " + POLL_N + " polls in " + POLL_S + " s (" + POLL_PLAYERS + " players x " + POLL_OBJ + " reach objectives on the world thread; limit 500 us)");
}""")
M(q0, r"""
public static void stampStep(@PR@ pr, double x, double z) {
  double[] xs = STAMP_X; double[] zs = STAMP_Z; boolean[] hit = STAMP_HIT;
  if (xs == null || zs == null || hit == null) return;
  for (int i = 0; i < xs.length; i++) {
    if (hit[i] || !@PKG@.TpLogic.nearXZ(x, z, xs[i], zs[i], STAMP_R)) continue;
    hit[i] = true;
    int n = 0;
    for (int k = 0; k < hit.length; k++) if (hit[k]) n++;
    @PKG@.TpLog.tell(pr, "Stamp " + (i + 1) + " stamped (" + n + " of " + hit.length + ").", "@COLOK@");
    if (n == hit.length) res(pr, 9, "PASS", "all " + n + " stamp points reached by walking (reach, radius " + STAMP_R + "); the map markers went to you " + SHOWN.get() + "x and were held back from other players " + HIDDEN.get() + "x - did the 3 markers show on YOUR map only? (Skyy)");
    else res(pr, 9, "WAIT", n + " of " + hit.length + " stamp points reached - walk to the rest (map markers sent to you " + SHOWN.get() + "x)");
  }
}""")
M(q0, r"""
public static void markParticles(@PR@ pr, @REF@ ref, @WLD@ w, @ST@ st) {
  java.util.ArrayList rs = recs(w.getName(), new String[] { "talker", "pebble", "pebblem" });
  java.util.ArrayList to = new java.util.ArrayList();
  to.add(ref);
  for (int i = 0; i < rs.size(); i++) {
    @PKG@.TpRec r = (@PKG@.TpRec) rs.get(i);
    @REF@ e = refOf(w, r);
    if (e == null) continue;
    @TC@ tc = (@TC@) st.getComponent(e, @TC@.getComponentType());
    if (tc == null) continue;
    @V3D@ p = tc.getPosition();
    boolean ask = "talker".equals(r.kind);
    try { @PKG@.TpEng.particle(ask ? MARK_ASK : MARK_BANG, new @V3D@(p.x, p.y + (ask ? 1.7 : 1.3), p.z), to, st); }
    catch (Throwable t) { if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("marker particle failed (logged once): " + t); } }
  }
}""")
M(q0, r"""
public static void tick(@PR@ pr, java.util.UUID u, @WLD@ w, @REF@ ref, @ST@ st, double x, double y, double z, long now) {
  Long sent = (Long) SLOT_SENT.get(u);
  if (sent != null && now - sent.longValue() >= SLOT_OK_MS) {
    SLOT_SENT.remove(u);
    res(pr, 14, "PASS", "still connected " + ((now - sent.longValue()) / 1000L) + " s after the page with 4 plain Copper ItemGridSlots (new ItemStack(id, 1), no metadata)");
  }
  if (u.equals(POLL_OWNER)) pollStep(pr, ref, st, now);
  if (u.equals(STAMP_OWNER) && w.getName().equals(STAMP_WORLD)) stampStep(pr, x, z);
  if (MARK_MODE == 3 && u.equals(MARK_OWNER) && now >= MARK_NEXT) { MARK_NEXT = now + MARK_EVERY_MS; markParticles(pr, ref, w, st); }
}""")
# ---- #1: F on a probe talker (TpUseSys, after it cancelled the vanilla use): duplicate guard, animation, the bridge call
M(q0, r"""
public static void useTalk(@REF@ player, @ST@ st, @PR@ pr, @REF@ target, @PKG@.TpRec rec, java.util.UUID npc) {
  long now = System.currentTimeMillis();
  PRESSES.incrementAndGet();
  Long last = (Long) LASTUSE.get(pr.getUuid());
  LASTUSE.put(pr.getUuid(), Long.valueOf(now));
  if (last != null && now - last.longValue() < DUP_MS) {
    DUPS.incrementAndGet();
    @PKG@.TpLog.info("Q0 #1: a second Use event from " + pr.getUsername() + " " + (now - last.longValue()) + " ms after the first - suppressed (counted)");
    return;
  }
  String anim = isPebble(rec.kind) && "pebblem".equals(rec.kind) ? "Talk" : "Wave";
  String an;
  try { @PKG@.TpEng.anim(st, target, "Action", anim); an = "played " + anim + " (slot Action)"; } catch (Throwable t) { an = anim + " not played: " + t; }
  java.util.function.Function f = fn(TALK_FN);
  if (f == null) { res(pr, 1, "FAIL", "the bridge function " + TALK_FN + " is missing from skyy.bridge"); return; }
  Object ok = f.apply(new Object[] { pr.getUuid(), rec.kind + ":" + rec.seq });
  @PKG@.TpLog.info("Q0 #1: " + pr.getUsername() + " pressed F on " + nameOf(rec) + " (" + npc + ") -> vanilla use cancelled -> bridge " + TALK_FN + " returned " + ok + "; animation " + an);
  if (!Boolean.TRUE.equals(ok)) res(pr, 1, "FAIL", "the bridge call returned " + ok + " (no page)");
  if ("pebblem".equals(rec.kind)) res(pr, 2, "WAIT", "F on Pebble: " + an + " - does Pebble talk (mouth moves) and is the nameplate over his head?");
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
    if (@PKG@.TpStore.NPCS.isEmpty() && @PKG@.TpStore.ZONE == null && IN.isEmpty() && !@PKG@.TpQ0.active()) return;
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
    @PKG@.TpQ0.tick(pr, u, w, ref, st, p.x, p.y, p.z, now);
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
  @PKG@.TpLog.tell(pr, "Q0 quest probes (0.2): /townprobe all sets them up, /townprobe q0 lists them, /townprobe report shows the results", null);
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
# =====================================================================================================================
# 0.2 TpQ0Cmds: the Q0 sub-commands (world thread: AbstractPlayerCommand.execute). Uses TpCmds' helpers (worldOk / canStart /
# where / ground), so it is built here, before TpCmds.run dispatches to it.
# =====================================================================================================================
qc = mk("TpQ0Cmds")
F(qc, "public static final String OK = \"@COLOK@\";")
F(qc, "public static final String ERR = \"@COLERR@\";")
F(qc, "public static final String INF = \"@COLINF@\";")
M(qc, r"""
public static String nameFor(String kind) {
  if ("talker".equals(kind)) return "Fennel";
  if ("pebblem".equals(kind)) return "Pebble";
  if ("golem".equals(kind)) return "The Earth Golem";
  return kind;
}""")
M(qc, r"""
public static void q0help(@PR@ pr) {
  @PKG@.TpLog.tell(pr, "Q0 quest probes (admin, Zone 1 test island). Each answer is a [SkyyTownProbe] Q0 #n line in chat and the server log.", INF);
  @PKG@.TpLog.tell(pr, "/townprobe all - set everything up and list what to do; /townprobe report - every result so far", null);
  @PKG@.TpLog.tell(pr, "/townprobe talk (Fennel), pebblem (Pebble with our model), golem - NPCs; F on Fennel / Pebble opens the dialogue page", null);
  @PKG@.TpLog.tell(pr, "/townprobe hint, marker [off], hat - cycle the F prompt, the ! / ? markers, Pebble's alias + hat", null);
  @PKG@.TpLog.tell(pr, "/townprobe hooks, poll [5-120], board, event [off], kills - the engine checks", null);
  @PKG@.TpLog.tell(pr, "/townprobe move / move check, stamp [off], copper / copper check / copper reset, claim - the longer tests", null);
}""")
# a floating nameplate prop (a tiny mossy pebble + Nameplate + Intangible + PropComponent: the 0.1 sign fallback set)
M(qc, r"""
public static String prop(@ST@ st, double x, double y, double z, String text) {
  @MDL@ m = @PKG@.TpNpc.model(@PKG@.TpNpc.ROCK, 0.2f);
  @HOL@ h = @PKG@.TpEng.newHolder();
  h.addComponent(@TC@.getComponentType(), new @TC@(new @V3D@(x, y, z), new @R3F@()));
  h.ensureComponent(@UUC@.getComponentType());
  h.addComponent(@NPL@.getComponentType(), new @NPL@(text));
  h.addComponent(@INT@.getComponentType(), @INT@.INSTANCE);
  h.addComponent(@PROP@.getComponentType(), @PROP@.get());
  if (m != null) {
    h.addComponent(@MC@.getComponentType(), new @MC@(m));
    h.addComponent(@PM@.getComponentType(), new @PM@(m.toReference()));
  }
  @REF@ e = st.addEntity(h, @ADR@.SPAWN);
  java.util.UUID u = ((@UUC@) h.getComponent(@UUC@.getComponentType())).getUuid();
  if (e != null && e.isValid()) { java.util.UUID u2 = @PKG@.TpNpc.uuidOf(st, e); if (u2 != null) u = u2; }
  return u.toString();
}""")
# spawn one Q0 NPC (talker / pebblem / golem); an existing one is answered, never doubled. quiet = no 'already here' line when found.
M(qc, r"""
public static @REF@ spawnQ(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String kind, boolean quiet) {
  if (!@PKG@.TpCmds.worldOk(pr, w)) return null;
  @PKG@.TpRec old = @PKG@.TpStore.find(kind, w.getName());
  if (old != null) {
    @REF@ e0 = @PKG@.TpQ0.refOf(w, old);
    if (!quiet || e0 == null) @PKG@.TpLog.tell(pr, nameFor(kind) + " is already placed (" + (e0 != null ? "found" : "not loaded right now") + ") - /townprobe undo removes the newest probe change.", e0 != null ? OK : ERR);
    return e0;
  }
  if (!@PKG@.TpCmds.canStart(pr, w)) return null;
  double[] me = @PKG@.TpCmds.where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return null; }
  long t0 = System.nanoTime();
  int fx = (int) me[3]; int fz = (int) me[4]; int sx = -fz; int sz = fx;
  int ahead = "golem".equals(kind) ? 10 : 3;
  int side = "talker".equals(kind) ? -2 : ("pebblem".equals(kind) ? 2 : 0);
  int bx = (int) me[0] + fx * ahead + sx * side; int bz = (int) me[2] + fz * ahead + sz * side;
  int gy = @PKG@.TpCmds.ground(w, bx, bz);
  if (gy == @PKG@.TpEng.NO_HEIGHT) gy = (int) me[1] - 1;
  @V3D@ pos = new @V3D@(bx + 0.5, gy + 1.0, bz + 0.5);
  @R3F@ rot = @PKG@.TpNpc.facing(pos.x, pos.z, me[6], me[8]);
  String up = kind.toUpperCase(java.util.Locale.ROOT);
  @PAIR@ p = null;
  String note = "";
  try {
    if ("pebblem".equals(kind)) {
      int ri = @PKG@.TpEng.roleIndex(@PKG@.TpNpc.ROLE);
      @MDL@ m = @PKG@.TpQ0.pebbleModel();
      if (ri < 0 || m == null) {
        @PKG@.TpLog.tell(pr, "Pebble needs the vanilla role " + @PKG@.TpNpc.ROLE + " (" + ri + ") and this jar's model " + @PKG@.TpQ0.PEB_MODEL + " (" + (m != null ? "loaded" : "NOT loaded") + ").", ERR);
        @PKG@.TpQ0.res(pr, 2, "FAIL", "our ModelAsset " + @PKG@.TpQ0.PEB_MODEL + " is " + (m != null ? "loaded" : "NOT loaded (the jar's asset pack did not load it)") + ", role index " + ri);
        return null;
      }
      p = @PKG@.TpEng.spawnModel(st, ri, pos, rot, m);
    } else p = @PKG@.TpEng.spawnNpc(st, "golem".equals(kind) ? @PKG@.TpQ0.GOLEM : @PKG@.TpNpc.ROLE, pos, rot);
  } catch (Throwable t) { @PKG@.TpLog.warn(up + " spawn threw: " + t); p = null; }
  @REF@ e = p == null ? null : (@REF@) p.first();
  if (e == null || !e.isValid()) {
    @PKG@.TpLog.tell(pr, nameFor(kind) + " did not spawn (see the server log).", ERR);
    @PKG@.TpLog.info(up + " FAILED: spawn returned nothing");
    if ("pebblem".equals(kind)) @PKG@.TpQ0.res(pr, 2, "FAIL", "NPCPlugin.spawnEntity with our model returned nothing");
    return null;
  }
  if ("pebblem".equals(kind)) {
    String got = @PKG@.TpNpc.modelId(st, e);
    boolean kept = got.startsWith(@PKG@.TpQ0.PEB_MODEL + " ");
    note = "model after spawn: " + got + (kept ? " (the role KEPT our Pebble model)" : " (the role REPLACED our Pebble model)");
    if (!kept) {
      @MDL@ m2 = @PKG@.TpQ0.pebbleModel();
      st.putComponent(e, @MC@.getComponentType(), new @MC@(m2));
      st.putComponent(e, @PM@.getComponentType(), new @PM@(m2.toReference()));
      note = note + "; forced it back: now " + @PKG@.TpNpc.modelId(st, e);
    }
    try { @PKG@.TpEng.anim(st, e, "Action", "Wave"); note = note + "; Wave played (slot Action)"; } catch (Throwable t) { note = note + "; Wave not played: " + t; }
  }
  java.util.UUID u = @PKG@.TpNpc.uuidOf(st, e);
  @PKG@.TpRec r = new @PKG@.TpRec();
  r.seq = @PKG@.TpStore.nextSeq();
  r.kind = kind; r.world = w.getName();
  r.ox = bx; r.oy = gy + 1; r.oz = bz;
  r.nx = pos.x; r.ny = pos.y; r.nz = pos.z;
  r.uuids = u == null ? "" : u.toString();
  r.what = nameFor(kind) + " at " + @PKG@.TpLogic.xyz(bx, gy + 1, bz);
  r.time = System.currentTimeMillis();
  @PKG@.TpNpc.name(st, e, @PKG@.TpQ0.nameOf(r));
  String use = "";
  if (!"golem".equals(kind)) {
    @PKG@.TpNpc.makeUsable(st, e);
    @ITS@ its = (@ITS@) st.getComponent(e, @ITS@.getComponentType());
    if (its != null) its.setInteractionHint(@PKG@.TpQ0.HINTS[0]);
    use = "Use = " + (its == null ? "?" : its.getInteractionId(@ITY@.Use)) + ", hint " + @PKG@.TpQ0.HINTS[0] + ", Interactable on";
  }
  @PKG@.TpStore.add(r);
  @PKG@.TpLog.info(up + " spawned: role " + ("golem".equals(kind) ? @PKG@.TpQ0.GOLEM : @PKG@.TpNpc.ROLE) + ", entity " + r.uuids + ", at " + pos.x + " " + pos.y + " " + pos.z + " in " + @PKG@.TpLogic.ms(System.nanoTime() - t0) + (use.length() > 0 ? "; " + use : "") + (note.length() > 0 ? "; " + note : "") + "; model " + @PKG@.TpNpc.modelId(st, e) + "; undo record " + r.seq);
  if ("pebblem".equals(kind)) @PKG@.TpQ0.res(pr, 2, "WAIT", "server side OK (asset loaded, spawned; " + note + ") - is it our rock with a face (not a Kweebec), does it wobble (Idle) and wave, and where is the nameplate?");
  else if ("talker".equals(kind)) @PKG@.TpLog.tell(pr, "Fennel is here (a Kweebec, no shop). Press F on him: the dialogue page should open.", OK);
  else { @PKG@.TpQ0.KILLS_ON = true; @PKG@.TpLog.tell(pr, "An Earth Golem (" + @PKG@.TpQ0.GOLEM + ") stands 10 blocks ahead - it fights back. Kill it for probe #11 (kill log is on), or /townprobe undo.", OK); }
  return e;
}""")
M(qc, r"""
public static void hint(@PR@ pr, @ST@ st, @WLD@ w) {
  java.util.ArrayList rs = @PKG@.TpQ0.recs(w == null ? "" : w.getName(), new String[] { "talker", "pebble", "pebblem" });
  if (rs.isEmpty()) { @PKG@.TpLog.tell(pr, "Spawn Fennel or Pebble first: /townprobe talk or /townprobe pebblem.", ERR); return; }
  int i = @PKG@.TpLogic.cycle(@PKG@.TpQ0.HINT_I, @PKG@.TpQ0.HINTS.length);
  @PKG@.TpQ0.HINT_I = i;
  int n = 0;
  for (int k = 0; k < rs.size(); k++) {
    @REF@ e = @PKG@.TpQ0.refOf(w, (@PKG@.TpRec) rs.get(k));
    if (e == null) continue;
    @ITS@ its = (@ITS@) st.getComponent(e, @ITS@.getComponentType());
    if (its == null) continue;
    its.setInteractionHint(@PKG@.TpQ0.HINTS[i]);
    n++;
  }
  String what = i == 0 ? "our lang key " + @PKG@.TpQ0.HINTS[0] + " (should read Press [F] to talk)" : (i == 1 ? "the vanilla " + @PKG@.TpQ0.HINTS[1] + " (Press [F] to interact)" : "a raw text '" + @PKG@.TpQ0.HINTS[2] + "' (not a key)");
  @PKG@.TpLog.info("Q0 #3 desk: vanilla interaction hint keys (none says talk): " + @PKG@.TpQ0.HINT_KEYS);
  @PKG@.TpQ0.res(pr, 3, "WAIT", "F prompt " + (i + 1) + " of 3 = " + what + " on " + n + " NPCs; vanilla has no talk hint key - look at Fennel / Pebble: what does the prompt say? (walk away and back if it did not change)");
}""")
M(qc, r"""
public static void marker(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String opt) {
  String o = opt == null ? "" : opt.trim().toLowerCase(java.util.Locale.ROOT);
  if (o.length() > 0 && !o.equals("off")) { @PKG@.TpLog.tell(pr, "Use /townprobe marker or /townprobe marker off.", ERR); return; }
  if (w == null) return;
  int mode = o.equals("off") ? 0 : @PKG@.TpLogic.cycle(@PKG@.TpQ0.MARK_MODE, 4);
  @PKG@.TpRec old = @PKG@.TpStore.find("mark", w.getName());
  if (old != null) { @PKG@.TpNpc.removeAll(w, st, old); @PKG@.TpStore.remove(old); }
  @PKG@.TpQ0.MARK_MODE = mode;
  @PKG@.TpQ0.MARK_OWNER = mode == 3 ? pr.getUuid() : null;
  @PKG@.TpQ0.MARK_NEXT = 0L;
  java.util.ArrayList rs = @PKG@.TpQ0.recs(w.getName(), new String[] { "talker", "pebble", "pebblem" });
  StringBuilder ids = new StringBuilder();
  double fx0 = 0.0; double fy0 = 0.0; double fz0 = 0.0;
  for (int k = 0; k < rs.size(); k++) {
    @PKG@.TpRec r = (@PKG@.TpRec) rs.get(k);
    @REF@ e = @PKG@.TpQ0.refOf(w, r);
    if (e == null) continue;
    @PKG@.TpNpc.name(st, e, @PKG@.TpQ0.nameOf(r));
    if (mode != 2) continue;
    @TC@ tc = (@TC@) st.getComponent(e, @TC@.getComponentType());
    if (tc == null) continue;
    @V3D@ p = tc.getPosition();
    boolean ask = "talker".equals(r.kind);
    String u = prop(st, p.x, p.y + (ask ? 2.3 : 1.8), p.z, ask ? "?" : "!");
    if (ids.length() == 0) { fx0 = p.x; fy0 = p.y; fz0 = p.z; } else ids.append(",");
    ids.append(u);
  }
  int props = 0;
  if (ids.length() > 0) {
    @PKG@.TpRec m = new @PKG@.TpRec();
    m.seq = @PKG@.TpStore.nextSeq(); m.kind = "mark"; m.world = w.getName(); m.uuids = ids.toString();
    m.nx = fx0; m.ny = fy0; m.nz = fz0; m.ox = (int) Math.floor(fx0); m.oy = (int) Math.floor(fy0); m.oz = (int) Math.floor(fz0);
    m.what = "the floating ? / ! markers"; m.time = System.currentTimeMillis();
    @PKG@.TpStore.add(m);
    props = m.uuidList().length;
  }
  String d = mode == 0 ? "off - names back, floating markers removed, particles stopped"
      : (mode == 1 ? "1 of 3: a '? ' / '! ' in front of the names (nameplate prefix, everyone sees it)"
      : (mode == 2 ? "2 of 3: a floating ? / ! nameplate over each head (" + props + " props, everyone sees them)"
      : "3 of 3: the vanilla emote particles Question (?) over Fennel and Alerted (!) over Pebble every 3 s, sent to YOU only"));
  if (rs.isEmpty()) d = d + " - but there is no Fennel / Pebble here yet (/townprobe talk, /townprobe pebblem)";
  @PKG@.TpQ0.res(pr, 4, "WAIT", "marker " + d + " - which can you see? (/townprobe marker again for the next one)");
}""")
M(qc, r"""
public static void hooks(@PR@ pr) {
  long c1 = @PKG@.TpQ0.CANCELLED.get(); long ours = @PKG@.TpQ0.HOOK2_OURS.get(); long other = @PKG@.TpQ0.HOOK2_OTHER.get();
  String desk = "desk: " + @PKG@.TpQ0.HOOKS_DESK;
  if (c1 == 0L) { @PKG@.TpQ0.res(pr, 5, "WAIT", desk + "; no F press on a probe NPC yet - press F on Fennel or Pebble, then /townprobe hooks"); return; }
  if (ours == 0L) @PKG@.TpQ0.res(pr, 5, "PASS", "system 1 cancelled " + c1 + " probe-NPC uses; system 2 (registered after it) received 0 of them and " + other + " uses of other things -> a cancelled Use never reaches a later system, so only ONE mod (SkyyTowns) may own the town NPC Use hook (" + desk + ")");
  else @PKG@.TpQ0.res(pr, 5, "FAIL", "system 2 still received " + ours + " of " + c1 + " cancelled probe-NPC uses (the order or the engine changed) - two mods on one NPC would BOTH act (" + desk + ")");
}""")
M(qc, r"""
public static void poll(@PR@ pr, String opt) {
  int s = 30;
  if (opt != null) { try { s = Integer.parseInt(opt.trim()); } catch (Throwable t) { @PKG@.TpLog.tell(pr, "Use /townprobe poll or /townprobe poll <5-120 seconds>.", ERR); return; } }
  if (s < 5) s = 5;
  if (s > 120) s = 120;
  @PKG@.TpQ0.POLL_N = 0L; @PKG@.TpQ0.POLL_SUM = 0L; @PKG@.TpQ0.POLL_MAX = 0L; @PKG@.TpQ0.POLL_S = s;
  @PKG@.TpQ0.POLL_UNTIL = System.currentTimeMillis() + s * 1000L;
  @PKG@.TpQ0.POLL_OWNER = pr.getUuid();
  @PKG@.TpQ0.res(pr, 6, "WAIT", "measuring for " + s + " s: every second " + @PKG@.TpQ0.POLL_PLAYERS + " players x " + @PKG@.TpQ0.POLL_OBJ + " reach checks on the world thread - just keep playing");
}""")
M(qc, r"""
public static void moveCheck(@PR@ pr, @ST@ st, @WLD@ w, @PKG@.TpRec r) {
  double ax = r.ox + 0.5; double ay = r.oy; double az = r.oz + 0.5;
  int na = @PKG@.TpQ0.countPebbles(st, ax, ay, az, 1.5);
  int nb = r.at.length() == 0 ? 0 : @PKG@.TpQ0.countPebbles(st, r.bx, r.by, r.bz, 1.5);
  @REF@ e = @PKG@.TpQ0.refOf(w, r);
  String where = "not found (unloaded or gone)";
  boolean atSaved = false;
  if (e != null) {
    @TC@ tc = (@TC@) st.getComponent(e, @TC@.getComponentType());
    if (tc != null) {
      @V3D@ p = tc.getPosition();
      atSaved = @PKG@.TpLogic.near(p.x, p.y, p.z, r.nx, r.ny, r.nz, 1.5);
      where = "at " + Math.round(p.x) + " " + Math.round(p.y) + " " + Math.round(p.z) + (atSaved ? " = the saved spot" : " - NOT the saved spot " + Math.round(r.nx) + " " + Math.round(r.ny) + " " + Math.round(r.nz));
    }
  }
  boolean restarted = r.time < @PKG@.TpQ0.BOOT;
  boolean one = na + nb == 1 && e != null && atSaved;
  String d = "Pebble models at spot A: " + na + ", at spot B: " + (r.at.length() == 0 ? "- (never moved)" : String.valueOf(nb)) + "; the record's Pebble is " + where + "; saved spot " + (r.at.length() == 0 ? "A" : r.at) + (restarted ? " (checked after a server restart)" : " (same session - restart the server, then check again)");
  @PKG@.TpQ0.res(pr, 7, !one ? "FAIL" : (restarted && r.at.length() > 0 ? "PASS" : "WAIT"), d);
}""")
M(qc, r"""
public static void move(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String opt) {
  if (w == null) return;
  String o = opt == null ? "" : opt.trim().toLowerCase(java.util.Locale.ROOT);
  if (o.length() > 0 && !o.equals("check")) { @PKG@.TpLog.tell(pr, "Use /townprobe move or /townprobe move check.", ERR); return; }
  @PKG@.TpRec r = @PKG@.TpStore.find("pebblem", w.getName());
  if (r == null) r = @PKG@.TpStore.find("pebble", w.getName());
  if (r == null) { @PKG@.TpLog.tell(pr, "Spawn Pebble first: /townprobe pebblem.", ERR); return; }
  if (o.equals("check")) { moveCheck(pr, st, w, r); return; }
  @REF@ e = @PKG@.TpQ0.refOf(w, r);
  if (e == null) { @PKG@.TpLog.tell(pr, "Pebble is not loaded - go near " + Math.round(r.nx) + ", " + Math.round(r.nz) + ".", ERR); return; }
  double[] me = @PKG@.TpCmds.where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  double tx; double ty; double tz;
  String nat;
  if (!"B".equals(r.at)) {
    int fx = (int) me[3]; int fz = (int) me[4];
    int ahead = 3;
    if (@PKG@.TpLogic.nearXZ((int) me[0] + fx * 3 + 0.5, (int) me[2] + fz * 3 + 0.5, r.ox + 0.5, r.oz + 0.5, 4.0)) ahead = 7;
    int bx = (int) me[0] + fx * ahead; int bz = (int) me[2] + fz * ahead;
    int gy = @PKG@.TpCmds.ground(w, bx, bz);
    if (gy == @PKG@.TpEng.NO_HEIGHT) gy = (int) me[1] - 1;
    tx = bx + 0.5; ty = gy + 1.0; tz = bz + 0.5;
    nat = "B";
  } else { tx = r.ox + 0.5; ty = r.oy; tz = r.oz + 0.5; nat = "A"; }
  @R3F@ rot = @PKG@.TpNpc.facing(tx, tz, me[6], me[8]);
  try { @PKG@.TpEng.teleport(st, e, new @V3D@(tx, ty, tz), rot); }
  catch (Throwable t) { @PKG@.TpQ0.res(pr, 7, "FAIL", "the Teleport component could not be put on Pebble: " + t); return; }
  if (nat.equals("B")) { r.bx = tx; r.by = ty; r.bz = tz; }
  r.at = nat;
  r.nx = tx; r.ny = ty; r.nz = tz; r.time = System.currentTimeMillis();
  @PKG@.TpStore.saveRec(r);
  @PKG@.TpQ0.res(pr, 7, "WAIT", "Pebble moved to spot " + r.at + " (" + Math.round(tx) + " " + Math.round(ty) + " " + Math.round(tz) + ") and the spot saved in record " + r.seq + " - restart the server, come back here and run /townprobe move check");
}""")
M(qc, r"""
public static void stamp(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w, String opt) {
  String o = opt == null ? "" : opt.trim().toLowerCase(java.util.Locale.ROOT);
  if (o.equals("off")) {
    @PKG@.TpQ0.STAMP_OWNER = null; @PKG@.TpQ0.STAMP_X = null; @PKG@.TpQ0.STAMP_Y = null; @PKG@.TpQ0.STAMP_Z = null; @PKG@.TpQ0.STAMP_HIT = null;
    @PKG@.TpLog.tell(pr, "Stamp points removed (the map markers go with them).", OK);
    return;
  }
  if (o.length() > 0) { @PKG@.TpLog.tell(pr, "Use /townprobe stamp or /townprobe stamp off.", ERR); return; }
  if (!@PKG@.TpCmds.worldOk(pr, w)) return;
  double[] me = @PKG@.TpCmds.where(st, ref);
  if (me == null) { @PKG@.TpLog.tell(pr, "Could not read your position.", ERR); return; }
  int fx = (int) me[3]; int fz = (int) me[4];
  int n = @PKG@.TpQ0.STAMP_DIST.length;
  double[] xs = new double[n]; double[] ys = new double[n]; double[] zs = new double[n];
  StringBuilder at = new StringBuilder();
  for (int i = 0; i < n; i++) {
    int x = (int) me[0] + fx * @PKG@.TpQ0.STAMP_DIST[i]; int z = (int) me[2] + fz * @PKG@.TpQ0.STAMP_DIST[i];
    int gy = @PKG@.TpCmds.ground(w, x, z);
    if (gy == @PKG@.TpEng.NO_HEIGHT) gy = (int) me[1] - 1;
    xs[i] = x + 0.5; ys[i] = gy + 1.0; zs[i] = z + 0.5;
    at.append(i == 0 ? "" : ", ").append(x).append(" ").append(z);
  }
  @PKG@.TpQ0.STAMP_HIT = new boolean[n];
  @PKG@.TpQ0.STAMP_X = xs; @PKG@.TpQ0.STAMP_Y = ys; @PKG@.TpQ0.STAMP_Z = zs;
  @PKG@.TpQ0.STAMP_WORLD = w.getName();
  @PKG@.TpQ0.STAMP_OWNER = pr.getUuid();
  String reg = "already registered";
  if (!@PKG@.TpQ0.MAP_WORLDS.containsKey(w.getName())) {
    try { @PKG@.TpEng.addMarkers(w, @PKG@.TpQ0.MAP_KEY, new @PKG@.TpMarkers()); @PKG@.TpQ0.MAP_WORLDS.put(w.getName(), w); reg = "registered"; }
    catch (Throwable t) { reg = "NOT registered: " + t; }
  }
  @PKG@.TpLog.info("Q0 #9: stamp points at " + at + " (owner " + pr.getUsername() + "); map marker provider " + @PKG@.TpQ0.MAP_KEY + " " + reg);
  @PKG@.TpQ0.res(pr, 9, "WAIT", n + " stamp points ahead at " + at + " (memory only, yours) - open the map (M): " + n + " markers for you only; then walk to each (within 3 blocks)");
}""")
M(qc, r"""
public static void event(@PR@ pr, String opt) {
  java.util.Map b = @PKG@.TpQ0.bridge();
  String o = opt == null ? "" : opt.trim().toLowerCase(java.util.Locale.ROOT);
  Object cur = b.get(@PKG@.TpQ0.EVENT_KEY);
  if (o.equals("off")) {
    boolean was = @PKG@.TpQ0.EVENT_FN != null && b.remove(@PKG@.TpQ0.EVENT_KEY, @PKG@.TpQ0.EVENT_FN);
    @PKG@.TpQ0.EVENT_FN = null;
    @PKG@.TpLog.tell(pr, was ? "quest:fn:event listener removed." : "The probe was not listening on quest:fn:event (left as it is).", OK);
    return;
  }
  if (o.length() > 0) { @PKG@.TpLog.tell(pr, "Use /townprobe event or /townprobe event off.", ERR); return; }
  if (cur != null && cur != @PKG@.TpQ0.EVENT_FN) {
    @PKG@.TpQ0.res(pr, 10, "WAIT", "quest:fn:event already belongs to another mod (" + cur.getClass().getName() + ") - left alone, not replaced");
    return;
  }
  if (cur == null) {
    @PKG@.TpEventFn f = new @PKG@.TpEventFn();
    Object prev = b.putIfAbsent(@PKG@.TpQ0.EVENT_KEY, f);
    if (prev != null) { @PKG@.TpQ0.res(pr, 10, "WAIT", "quest:fn:event was taken a moment ago by " + prev.getClass().getName() + " - left alone"); return; }
    @PKG@.TpQ0.EVENT_FN = f;
  }
  Object back = null;
  try { back = ((java.util.function.Function) b.get(@PKG@.TpQ0.EVENT_KEY)).apply(new Object[] { pr.getUuid(), "townprobe:selftest", "probe", Integer.valueOf(1) }); } catch (Throwable t) { back = t.toString(); }
  long n = @PKG@.TpQ0.EVENTS.get();
  if (n > 0L) { @PKG@.TpLog.tell(pr, "quest:fn:event: " + n + " real calls so far - see #10 in /townprobe report.", OK); return; }
  @PKG@.TpQ0.res(pr, 10, "WAIT", "listening on quest:fn:event (self-test round trip through skyy.bridge: " + back + "); no real call yet - SkyyBank / SkyyBazaar / SkyyGear add their one-line call in their next versions (a sell / identify / deposit then shows here as PASS)");
}""")
M(qc, r"""
public static void kills(@PR@ pr) {
  @PKG@.TpQ0.KILLS_ON = !@PKG@.TpQ0.KILLS_ON;
  if (!@PKG@.TpQ0.KILLS_ON) { @PKG@.TpLog.tell(pr, "Kill log off (a " + @PKG@.TpQ0.GOLEM + " kill is still logged).", OK); return; }
  @PKG@.TpQ0.res(pr, 11, "WAIT", "kill log on - kill any mob: its role id shows here; a " + @PKG@.TpQ0.GOLEM + " kill = PASS (/townprobe golem spawns one)");
}""")
M(qc, r"""
public static void board(@PR@ pr, @WLD@ w) {
  java.util.UUID u = pr.getUuid();
  String pk = @PKG@.TpQ0.pkey(u);
  long now = System.currentTimeMillis();
  long day = @PKG@.TpLogic.boardDay(now, @PKG@.TpLogic.ANCHOR_S, @PKG@.TpLogic.DAY_S);
  long seed = @PKG@.TpLogic.boardSeed(pk, day);
  String jobs = @PKG@.TpLogic.jobText(@PKG@.TpLogic.pickJobs(seed, @PKG@.TpLogic.BOARD_JOBS));
  String wn = w == null ? "?" : w.getName();
  String head = "BOARD pkey=" + pk + " day=" + day + " ";
  java.util.List l = @PKG@.TpQ0.readLog();
  int same = 0; int diff = 0; boolean restart = false; boolean world = false;
  for (int i = 0; i < l.size(); i++) {
    String s = (String) l.get(i);
    int k = s.indexOf(head);
    if (k < 0) continue;
    String[] t = s.substring(k).split(" ");
    String j = ""; String ow = ""; String ob = "";
    for (int q = 0; q < t.length; q++) {
      if (t[q].startsWith("jobs=")) j = t[q].substring(5);
      else if (t[q].startsWith("world=")) ow = t[q].substring(6);
      else if (t[q].startsWith("boot=")) ob = t[q].substring(5);
    }
    if (!j.equals(jobs)) { diff++; continue; }
    same++;
    if (!ob.equals(String.valueOf(@PKG@.TpQ0.BOOT))) restart = true;
    if (!ow.equals(wn)) world = true;
  }
  @PKG@.TpQ0.append(head + "seed=" + seed + " jobs=" + jobs + " world=" + wn + " boot=" + @PKG@.TpQ0.BOOT);
  String d = "profile " + pk + ", day " + day + " (next board in " + @PKG@.TpLogic.hms(@PKG@.TpLogic.boardLeftS(now, @PKG@.TpLogic.ANCHOR_S, @PKG@.TpLogic.DAY_S)) + "), seed " + seed + ", jobs " + jobs
      + "; earlier runs today: " + same + " same" + (diff > 0 ? ", " + diff + " DIFFERENT" : "") + " (after a restart: " + (restart ? "yes" : "not yet") + ", in another world: " + (world ? "yes" : "not yet") + ")";
  @PKG@.TpQ0.res(pr, 12, diff > 0 ? "FAIL" : (restart && world ? "PASS" : "WAIT"), d);
}""")
M(qc, r"""
public static void copperCheck(@PR@ pr, Object player) {
  @IC@[] cs = @PKG@.TpEng.conts(player, true);
  java.util.HashSet ids = new java.util.HashSet();
  int worn = 0; int bags = 0; int gear = 0; int lost = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      boolean copper = false;
      for (int k = 0; k < @PKG@.TpQ0.COPPER.length; k++) if (@PKG@.TpQ0.COPPER[k].equals(it.getItemId())) copper = true;
      if (!copper) continue;
      @BD@ d = @PKG@.TpClaims.doc(it);
      try { if (it.getMetadata() != null && it.getMetadata().containsKey(@PKG@.TpQ0.GEAR_DOC_KEY)) gear++; } catch (Throwable t) { }
      if (!@PKG@.TpQ0.SET_ID.equals(@PKG@.TpClaims.field(d, "set"))) { lost++; continue; }
      ids.add(it.getItemId());
      if (c == 3) worn++; else bags++;
    }
  }
  int n = ids.size();
  @PKG@.TpQ0.res(pr, 13, n == 4 ? "PASS" : "FAIL", "set=copper_quest on " + n + " of 4 pieces (worn " + worn + ", in bags " + bags + "); Copper pieces WITHOUT the field: " + lost + "; SkyyGear doc on " + gear
      + (n == 4 ? " - check again after a death, a Vault deposit + withdraw and a Wardrobe swap" : " - a piece is missing or lost its field (or never given: /townprobe copper)"));
}""")
M(qc, r"""
public static void claim(@PR@ pr, Object player) {
  int[] r = @PKG@.TpClaims.pay(player, @PKG@.TpQ0.pkey(pr.getUuid()));
  if (r[0] + r[1] + r[2] == 0) { @PKG@.TpLog.tell(pr, "No claims waiting.", OK); return; }
  @PKG@.TpQ0.res(pr, 17, r[1] == 0 ? "PASS" : "WAIT", "paid " + r[0] + ", already granted (no second item) " + r[2] + ", still waiting " + r[1] + (r[1] > 0 ? " - the bag is full: make room, then /townprobe claim" : " - the ledger is empty again"));
}""")
M(qc, r"""
public static void copper(@PR@ pr, @ST@ st, @REF@ ref, String opt) {
  Object player = st.getComponent(ref, @PLA@.getComponentType());
  if (player == null) { @PKG@.TpLog.tell(pr, "No Player component.", ERR); return; }
  String o = opt == null ? "" : opt.trim().toLowerCase(java.util.Locale.ROOT);
  if (o.equals("check")) { copperCheck(pr, player); return; }
  if (o.length() > 0 && !o.equals("reset")) { @PKG@.TpLog.tell(pr, "Use /townprobe copper, /townprobe copper check or /townprobe copper reset.", ERR); return; }
  if (@PKG@.TpStore.DIR == null) { @PKG@.TpLog.tell(pr, "No data folder - the claim ledger needs one.", ERR); return; }
  String pk = @PKG@.TpQ0.pkey(pr.getUuid());
  if (o.equals("reset")) {
    int[] z = @PKG@.TpClaims.reset(pk);
    @PKG@.TpLog.tell(pr, "Copper reset: " + z[0] + " waiting claims and " + z[1] + " issued marks of yours removed - /townprobe copper issues a new set (pieces you still have are not given twice).", OK);
    return;
  }
  int[] q = @PKG@.TpClaims.issue(player, pk);
  int added = q[0]; int have = q[1];
  if (q[3] == 0) { @PKG@.TpQ0.res(pr, 17, "FAIL", "the claim ledger could not be written - nothing given"); return; }
  @PKG@.TpLog.info("Q0 #17: " + added + " claim lines written in ONE atomic write (" + have + " pieces already in the bags, " + q[2] + " issued before and not in the bags - NOT issued again, " + q[4] + " older claims)");
  if (q[2] > 0) @PKG@.TpLog.tell(pr, q[2] + " Copper pieces were issued to you before and are not in your bags or armour (Vault, Wardrobe, dropped?) - not given again. /townprobe copper reset, then /townprobe copper, if you really want a new set.", INF);
  int[] r = @PKG@.TpClaims.pay(player, pk);
  @PKG@.TpQ0.res(pr, 17, r[1] == 0 ? "PASS" : "WAIT", added + " claims written in one atomic write, then paid one by one storage-first (count before / after): paid " + r[0] + ", already granted " + r[2] + ", waiting " + r[1] + (r[1] > 0 ? " (bag full - make room, /townprobe claim)" : "; the ledger file is gone again"));
  if (r[0] + have > 0) @PKG@.TpQ0.res(pr, 13, "WAIT", "the Copper pieces carry set=copper_quest - run /townprobe copper check now, then again after a death, a Vault deposit + withdraw and a Wardrobe swap");
}""")
M(qc, r"""
public static void hat(@PR@ pr, @ST@ st, @WLD@ w) {
  if (w == null) return;
  java.util.ArrayList rs = @PKG@.TpQ0.recs(w.getName(), new String[] { "talker", "pebble", "pebblem" });
  if (rs.isEmpty()) { @PKG@.TpLog.tell(pr, "Spawn Pebble first: /townprobe pebblem (Fennel gets the hats too: /townprobe talk).", ERR); return; }
  int i = @PKG@.TpLogic.cycle(@PKG@.TpQ0.DIS_I, @PKG@.TpQ0.DIS_ALIAS.length);
  @PKG@.TpQ0.DIS_I = i;
  String hat = @PKG@.TpQ0.DIS_HAT[i];
  String hn = hat.length() == 0 ? "no hat" : hat.substring(hat.lastIndexOf('/') + 1);
  int n = 0;
  StringBuilder log = new StringBuilder();
  for (int k = 0; k < rs.size(); k++) {
    @PKG@.TpRec r = (@PKG@.TpRec) rs.get(k);
    @REF@ e = @PKG@.TpQ0.refOf(w, r);
    if (e == null) continue;
    @MC@ mc = (@MC@) st.getComponent(e, @MC@.getComponentType());
    if (mc == null || mc.getModel() == null) continue;
    @MDL@ m2 = @PKG@.TpQ0.withHat(mc.getModel(), hat, @PKG@.TpQ0.DIS_TEX[i]);
    String before = @PKG@.TpQ0.attText(mc.getModel());
    st.putComponent(e, @MC@.getComponentType(), new @MC@(m2));
    @PKG@.TpNpc.name(st, e, @PKG@.TpQ0.nameOf(r));
    log.append(log.length() == 0 ? "" : "; ").append(@PKG@.TpQ0.nameOf(r)).append(": ").append(before).append(" -> ").append(@PKG@.TpQ0.attText(m2));
    n++;
  }
  @PKG@.TpLog.info("Q0 #15 disguise " + (i + 1) + ": " + log);
  @PKG@.TpQ0.res(pr, 15, n == 0 ? "FAIL" : "WAIT", "disguise " + (i + 1) + " of " + @PKG@.TpQ0.DIS_ALIAS.length + ": Pebble is now '" + @PKG@.TpQ0.alias() + "' wearing " + hn + " (Fennel wears it too, the vanilla-rig control); name + model swapped on " + n
      + " NPCs at runtime - do you see the new name and hat without walking away? (the hat is NOT saved: after a restart it is gone - SkyyTowns would put it back on load)");
}""")
M(qc, r"""
public static void all(@PR@ pr, @ST@ st, @REF@ ref, @WLD@ w) {
  if (!@PKG@.TpCmds.worldOk(pr, w)) return;
  @PKG@.TpLog.tell(pr, "Q0 probe round: setting everything up...", INF);
  spawnQ(pr, st, ref, w, "talker", true);
  spawnQ(pr, st, ref, w, "pebblem", true);
  if (@PKG@.TpQ0.EVENT_FN == null) event(pr, null);
  @PKG@.TpQ0.KILLS_ON = true;
  board(pr, w);
  stamp(pr, st, ref, w, null);
  poll(pr, null);
  copper(pr, st, ref, null);
  @PKG@.TpLog.tell(pr, "Now: 1) F on Fennel (the Kweebec): a page opens - press Next, then Close. F again and close it with Esc. 2) The same on Pebble.", INF);
  @PKG@.TpLog.tell(pr, "3) /townprobe hint x3, /townprobe marker x4, /townprobe hat x3 - say what you see each time. 4) /townprobe hooks.", INF);
  @PKG@.TpLog.tell(pr, "5) Open the map (M): 3 stamp markers ahead - walk to all 3. 6) Kill any mob (or /townprobe golem).", INF);
  @PKG@.TpLog.tell(pr, "7) /townprobe copper check, then die, check; Vault deposit + withdraw, check; Wardrobe swap, check.", INF);
  @PKG@.TpLog.tell(pr, "8) /townprobe report (screenshot), /townprobe move, restart the server, /townprobe move check + /townprobe board (also in another world). 9) /townprobe report again.", INF);
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
  if (t.equals("q0")) { @PKG@.TpQ0Cmds.q0help(pr); return; }
  if (t.equals("all")) { @PKG@.TpQ0Cmds.all(pr, st, ref, w); return; }
  if (t.equals("report")) { @PKG@.TpQ0.report(pr); return; }
  if (t.equals("talk")) { @PKG@.TpQ0Cmds.spawnQ(pr, st, ref, w, "talker", false); return; }
  if (t.equals("pebblem")) { @PKG@.TpQ0Cmds.spawnQ(pr, st, ref, w, "pebblem", false); return; }
  if (t.equals("golem")) { @PKG@.TpQ0Cmds.spawnQ(pr, st, ref, w, "golem", false); return; }
  if (t.equals("hint")) { @PKG@.TpQ0Cmds.hint(pr, st, w); return; }
  if (t.equals("marker")) { @PKG@.TpQ0Cmds.marker(pr, st, ref, w, null); return; }
  if (t.equals("hooks")) { @PKG@.TpQ0Cmds.hooks(pr); return; }
  if (t.equals("poll")) { @PKG@.TpQ0Cmds.poll(pr, null); return; }
  if (t.equals("move")) { @PKG@.TpQ0Cmds.move(pr, st, ref, w, null); return; }
  if (t.equals("stamp")) { @PKG@.TpQ0Cmds.stamp(pr, st, ref, w, null); return; }
  if (t.equals("event")) { @PKG@.TpQ0Cmds.event(pr, null); return; }
  if (t.equals("kills")) { @PKG@.TpQ0Cmds.kills(pr); return; }
  if (t.equals("board")) { @PKG@.TpQ0Cmds.board(pr, w); return; }
  if (t.equals("copper")) { @PKG@.TpQ0Cmds.copper(pr, st, ref, null); return; }
  if (t.equals("claim")) { Object pl = st.getComponent(ref, @PLA@.getComponentType()); if (pl == null) @PKG@.TpLog.tell(pr, "No Player component.", ERR); else @PKG@.TpQ0Cmds.claim(pr, pl); return; }
  if (t.equals("hat")) { @PKG@.TpQ0Cmds.hat(pr, st, w); return; }
  @PKG@.TpLog.tell(pr, "Unknown option '" + a.trim() + "'.", ERR);
  help(pr);
}""")
# /townprobe zone all|off arrive as 2 tokens: route them here (run() only lets 'temple' / 'piece' take more than one)
M(cmds, r"""
public static void run2(@REF@ ref, @ST@ st, @PR@ pr, @WLD@ w, String a, String b) {
  String t = a == null ? "" : a.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("zone")) { @PKG@.TpLog.info(pr.getUsername() + " ran /townprobe zone " + b + " in " + (w == null ? "?" : w.getName())); zone(pr, st, ref, w, b); return; }
  if (t.equals("marker") || t.equals("stamp") || t.equals("event") || t.equals("move") || t.equals("copper") || t.equals("poll")) {
    @PKG@.TpLog.info(pr.getUsername() + " ran /townprobe " + t + " " + b + " in " + (w == null ? "?" : w.getName()));
    if (t.equals("marker")) @PKG@.TpQ0Cmds.marker(pr, st, ref, w, b);
    else if (t.equals("stamp")) @PKG@.TpQ0Cmds.stamp(pr, st, ref, w, b);
    else if (t.equals("event")) @PKG@.TpQ0Cmds.event(pr, b);
    else if (t.equals("move")) @PKG@.TpQ0Cmds.move(pr, st, ref, w, b);
    else if (t.equals("copper")) @PKG@.TpQ0Cmds.copper(pr, st, ref, b);
    else @PKG@.TpQ0Cmds.poll(pr, b);
    return;
  }
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
    @PKG@.TpQ0.CANCELLED.incrementAndGet();
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (@PKG@.TpQ0.isTalker(rec.kind)) { @PKG@.TpQ0.useTalk(r, st, pr, t, rec, u); return; }
    if (!"npc".equals(rec.kind)) { @PKG@.TpLog.info("USE: " + pr.getUsername() + " used " + rec.kind + " " + u + " (nothing to open)"); return; }
    String why = openPage(r, st, (@CAC@) buf, pr);
    OPENS.incrementAndGet();
    if (why.length() == 0) @PKG@.TpLog.info("USE: " + pr.getUsername() + " pressed F on Mossby (" + u + ") -> " + PAGE + " page OPENED via its page id");
    else { @PKG@.TpLog.info("USE: " + pr.getUsername() + " pressed F on Mossby (" + u + ") -> page NOT opened: " + why); @PKG@.TpLog.tell(pr, "Mossby could not open the Bazaar: " + why, "@COLERR@"); }
  } catch (Throwable x) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("use hook failed (logged once): " + x); }
  }
}""")

# =====================================================================================================================
# 0.2 #5: TpUseSys2 - a SECOND UseEntityEvent$Pre system (registered after TpUseSys). It only counts; it never cancels or opens.
# 0.2 #11: TpKillSys - an OnDeathSystem (DeathComponent added on an NPC; killer = Damage$EntitySource), like SkyyCollections' CollKillSys
# =====================================================================================================================
use2 = mk("TpUseSys2", T["EES"])
F(use2, "public static boolean FAILED_ONCE = false;")
C(use2, "public TpUseSys2() { super(@UEPRE@.class); }")
M(use2, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
M(use2, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @UEPRE@)) return;
    @UEPRE@ e = (@UEPRE@) ev;
    @REF@ t = e.getTargetEntity();
    java.util.UUID u = t == null || !t.isValid() ? null : @PKG@.TpNpc.uuidOf(st, t);
    if (u != null && @PKG@.TpStore.NPCS.containsKey(u.toString())) {
      @PKG@.TpQ0.HOOK2_OURS.incrementAndGet();
      @PKG@.TpLog.info("Q0 #5: system 2 received a probe-NPC use (cancelled = " + e.isCancelled() + ")");
    } else @PKG@.TpQ0.HOOK2_OTHER.incrementAndGet();
  } catch (Throwable x) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("use hook 2 failed (logged once): " + x); }
  }
}""")
kil = mk("TpKillSys", T["ODS"])
F(kil, "public static boolean FAILED_ONCE = false;")
C(kil, "public TpKillSys() { super(); }")
M(kil, r"""
public @QRY@ getQuery() {
  return @ARCH@.empty();
}""")
M(kil, r"""
public void onComponentAdded(@REF@ r, @CMP@ c, @ST@ s, @CB@ b) {
  try {
    if (r == null || !(c instanceof @DTH@)) return;
    @NPC@ npc = (@NPC@) s.getComponent(r, @NPC@.getComponentType());
    if (npc == null) return;
    String role = npc.getRoleName();
    boolean boss = @PKG@.TpQ0.GOLEM.equals(role);
    if (!boss && !@PKG@.TpQ0.KILLS_ON) return;
    @PR@ pr = null;
    @DMG@ d = ((@DTH@) c).getDeathInfo();
    if (d != null) {
      Object src = d.getSource();
      if (src instanceof @DES@) {
        @REF@ k = ((@DES@) src).getRef();
        if (k != null && k.isValid() && k.getStore() == s) pr = (@PR@) s.getComponent(k, @PR@.getComponentType());
      }
    }
    if (pr == null) { @PKG@.TpLog.info("Q0 #11: " + role + " died (no player killer)"); return; }
    long n = @PKG@.TpQ0.KILLS.incrementAndGet();
    if (boss) @PKG@.TpQ0.res(pr, 11, "PASS", "boss kill: " + role + " killed by " + pr.getUsername() + " - it reached the probe by role id (DeathComponent on the NPC, killer = the Damage source)");
    else @PKG@.TpQ0.res(pr, 11, "WAIT", "the role-id route works: " + role + " killed by " + pr.getUsername() + " (" + n + " kills seen); the " + @PKG@.TpQ0.GOLEM + " is not killed yet");
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.TpLog.warn("kill hook failed (logged once): " + t); }
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
  super("(admin) /townprobe <temple, undo, lane, npc, pebble, zone, sign, help> or a Q0 probe <all, report, q0, talk, pebblem, golem, hint, marker, hooks, poll, move, stamp, event, kills, board, copper, claim, hat>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("action", "temple, undo, lane, piece, npc, pebble, zone, sign, help, or a Q0 probe (all, report, q0 lists them)", @ATY@.STRING);
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
  super("(admin) /townprobe temple <0-3>, piece <prefab path>, zone <all, off>, marker / stamp / event off, move / copper check, copper reset, poll <seconds>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.aArg = withRequiredArg("action", "temple, piece, zone, marker, stamp, event, move, copper or poll", @ATY@.STRING);
  this.bArg = withRequiredArg("value", "a rotation 0-3 (add e for entities), a prefab path / alias, all / off, check, or seconds", @ATY@.STRING);
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
  super("townprobe", "(admin) Zone 1 town + Q0 quest probe (throwaway dev pack): /townprobe lists the actions");
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

# ---- 0.2: the Q0 shutdown (only OUR bridge entries are removed; the marker providers go; memory state cleared)
M(q0, r"""
public static void shutdown() {
  try {
    java.util.Map b = bridge();
    if (TALK_OBJ != null) b.remove(TALK_FN, TALK_OBJ);
    if (EVENT_FN != null) b.remove(EVENT_KEY, EVENT_FN);
  } catch (Throwable t) { }
  TALK_OBJ = null; EVENT_FN = null;
  java.util.Iterator it = MAP_WORLDS.values().iterator();
  while (it.hasNext()) { try { @PKG@.TpEng.removeMarkers((@WLD@) it.next(), MAP_KEY); } catch (Throwable t) { } }
  MAP_WORLDS.clear();
  STAMP_OWNER = null; STAMP_X = null; STAMP_Y = null; STAMP_Z = null; STAMP_HIT = null;
  POLL_OWNER = null; MARK_OWNER = null; MARK_MODE = 0; KILLS_ON = false;
  LASTUSE.clear(); SLOT_SENT.clear();
}""")
M(q0, r"""
public static void publish() {
  @PKG@.TpTalkFn f = new @PKG@.TpTalkFn();
  bridge().put(TALK_FN, f);
  TALK_OBJ = f;
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
  getEntityStoreRegistry().registerSystem(new @PKG@.TpUseSys2());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardBreak());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardDamage());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardPlace());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpGuardUse());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpTick());
  getEntityStoreRegistry().registerSystem(new @PKG@.TpKillSys());
  @PKG@.TpQ0.publish();
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyTownProbe] @VERSION@ ready - /townprobe (admin, Zone 1 test island @WORLD@ only): " + n + " undo records, " + @PKG@.TpStore.NPCS.size() + " probe entities known; Q0 quest probes on (/townprobe q0) (throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  @PKG@.TpStore.ZONE = null;
  @PKG@.TpTick.ACC.clear();
  @PKG@.TpTick.BARKED.clear();
  @PKG@.TpTick.IN.clear();
  @PKG@.TpGuard.WARNED.clear();
  @PKG@.TpQ0.shutdown();
  super.shutdown();
}""")

ALL = ([log, lg, rec, zone, sto, api, eng, snp, ec, grab, bld, job, stp, pst, iod, npc, q0, dlg, opn, tfn, efn, mpv, clm, cmds, qc, use, use2, kil, guard]
       + gcls + [tick, c1, c2, c3, cmd, pl])
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d" % len(ALL))

jar = os.path.join(HERE, "SkyyTownProbe-%s.jar" % VERSION)
man = B.manifest("SkyyTownProbe", VERSION, "SkyWynn THROWAWAY dev pack: the Zone 1 town T0 probe + the Q0 quest probes (/townprobe, admin only, Zone 1 test island) - temple paste + undo, lane, prefab pieces, Bazaar NPC, Pebble, no-build zone, sign; NPC Use -> dialogue, Pebble model + hats, markers, hooks, poll, move, stamps, events, boss kill, board, copper set + claim ledger. Pinned for one test session, then removed.", PKG + ".SkyyTownProbePlugin")
man["IncludesAssetPack"] = True    # 0.2 ships our own Pebble model / animations / icons, one ModelAsset and one lang key (ASSET_FILES)
B.assemble(jar, man, OUT, ASSET_FILES)
