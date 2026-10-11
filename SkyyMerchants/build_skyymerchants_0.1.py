"""SkyyMerchants 0.1 - build script (javassist via jpype, tools/skyybuild.py). NEW standalone mod: ROAMING MERCHANTS.
Owner: Skyy (they/them). Run:  python SkyyMerchants/build_skyymerchants_0.1.py   -> SkyyMerchants/SkyyMerchants-0.1.jar
(no --deploy on purpose: tools/deploy_set.py installs the set once the round is ready). Test: python SkyyMerchants/test_skyymerchants_0.1.py

WHY (Skyy's own words, docs/answered/economy.md 2026-10-09): "this one has wandering traders, and some mounts. could be good for special
shops to get pets and weapons. (have them constantly move around each zone so you have to find them" + "yes, build our own roaming
merchants" + popup batch 9: move "Every 20 min (Recommended)", finding "Rumours in chat (Recommended)", stock "Special weapons
(Recommended),Mounts,Pet eggs later". Plan: research/Mods-Folder-Survey.md (Bio's Kobolds section); engine route:
research/Server-Setup-Research.md section 3 (NPCPlugin.spawnNPC + UseEntityEvent$Pre). Market wall (economy.md 2026-10-08): Mythic + UT +
Sets are never bought or sold - and gear.md 2026-10-08: UNTIERED is NEVER sold in NPC shops.

NO ASSET SHIPPED: the jar holds classes only (IncludesAssetPack false - nothing for the engine's asset validators to refuse). The look is a
VANILLA NPC role picked by name (default Temple_Klops: Variant of Template_Temple = Invulnerable, MotionStatic, Klops_Merchant look, no
InteractionInstruction = no vanilla barter shop; checked against Assets.zip at every build), the vanilla Use root every NPC gets (*UseNPC)
and the vanilla hint key server.interactionHints.trade ("Press [F] to trade").

1. ROAMING MERCHANTS - one merchant per ZONE (Server Setup table merchant.zones: zone id -> World ; Area ; Levels). Defaults zone1..zone4
   in world "default": Area = the vanilla environment ids Env_Zone1..Env_Zone4 (prefixes, "!" = except, "*" = any; the same env ids the
   SkyyMobs bands use), Levels = the SkyyMobs zone bands 1-20 / 20-30 / 30-45 / 45-60 (a spot counts only when SkyyMobs' mob:fn:levelAt
   lowest level lies in the band; no SkyyMobs / no level there = the Area alone decides). A merchant appears ONLY in loaded chunks: once a
   second per world (HytaleServer scheduler -> World.execute, the world thread; worlds without players are skipped) up to 6 random columns
   48-192 blocks from a random player of that world are tried (merchant.ringMin / ringMax; never within merchant.playerGap 24 of any
   player): heightmap top = natural ground (merchant.ground prefixes, never a built shape: _Half _Stairs _Roof _Wall _Beam _Brick _Cobble
   _Pillar _Smooth _Decorative _Ornate _Corner _Fence _Path _Quarter _Tilled), the 2 blocks above air or short wild plants, no fluid, the
   environment there matches the zone's Area and the level its Levels. No valid spot / no loaded area = it waits (tries again in 5 s).
   Spawn = NPCPlugin.spawnNPC(store, role, null, pos, rot) (vanilla SpawnNpcEffect call shape) + Nameplate / DisplayName / PersistentDisplayName
   "Traveling Merchant" + Interactable + the Use root + hint. Every merchant.moveSeconds (1200 = 20 min, live, shown in seconds) it MOVES:
   the new one is spawned first, the registry line is saved (a failed save removes the new one again - nothing unsaved stays in the
   world), then the old one is removed (if its chunk is not loaded it becomes a GHOST: removed the moment it loads - see 5).
2. RUMOURS - when a merchant appears or moves, every player in that world gets one chat line (rumour.enabled, rumour.text): place = the
   environment there in plain words (Env_Zone1_Plains -> plains), where = a distance band + 8-way compass direction from the world spawn
   ("close to spawn" < 150 blocks, "a short walk north-east of spawn" < 500, "a fair way" < 1200, "far to the" < 2500, else "very far to
   the"), zone = "Zone 1", region = the vanilla zone name (Emerald Wilds ...). Never coordinates. /merchants (every player) repeats the
   latest rumour of each merchant in your world and when it moves on.
3. SHOP - Use (F) on a merchant: our UseEntityEvent$Pre system (fired on the player) cancels the vanilla use for OUR merchant UUIDs only and
   opens the vanilla-look shop page next tick (World.execute, never from inside the ECS handler). Tabs Weapons / Mounts / Pet eggs. Stock
   per zone from three key-family tables (merchant.weapons / mounts / pets: item id -> Zones ; Price ; Stock): on every move the merchant
   RESTOCKS: up to merchant.offers (4) random weapons of its zone + every mount / pet egg of its zone, each with its table Stock, the
   price frozen for that visit. A row shows only ids the server knows (Item asset map) - a pack mod that is not installed hides its rows.
   BUY: first click arms, second click (10 s) buys: part on, the merchant still the one the page opened (else "has moved on"), you stand
   within merchant.useRange (8) blocks, the id is not walled, stock left, profile not busy (profile:busy:<uuid>), purse >= price, a free
   inventory slot (storage, hotbar, backpack) - all BEFORE any coin moves; then stock reserved -> coins:fn:take -> the item given storage
   first (counted before / after, never trusting the transaction) -> nothing arrived = coins refunded (coins:fn:add) + stock back; a
   failed refund is logged REFUND-FAILED in sales.log and told to the player. Never coins lost without the item, never an item unpaid.
   THE WALL: never sold (also refused when an admin adds it to a table, check= hook): ids matching merchant.neverSell (exact or Prefix*;
   default = every boss special of research/Pack-Armor-Plan.md 3.3, the 6 developer bows, Weapon_Longsword_Flame, the Crystal staffs,
   Debug_*), every Skyy_Sack_* bag, and whatever SkyyGear's gear:fn:rarity answers mythic / untiered / set for (the UT/Mythic round makes
   SkyyGear answer that; today it answers normal for every plain id).
4. ADMIN - /merchantadmin list | move <zone> | spawn <zone> | remove <zone> (op only: requirePermission skyymerchants.admin + no permission
   groups on the command and both usage variants). remove = the merchant leaves and stays away (held) until spawn / move. Requests for a
   zone in another world run on that world's next second (needs a player there); the admin gets the result in chat. Server Setup tab
   "Merchants" (tools/skyycfg.py kit 1.1, KEEP=10): Merchants (on/off, move seconds, name, role, ring, gaps, offers, ground), Rumours,
   Zones, Stock (the three tables + the never-sell list).
5. SAVED DATA + RESTARTS - Skyy_SkyyMerchants/config.properties (the kit) + merchants/<world>.tsv (one line per zone: zone uuid x y z
   placedAt visit held stock ghosts env rumour; atomic tmp + move; an unreadable file is NEVER overwritten - that world's merchants
   pause until it reads; unparsable lines: the whole file is first copied to <world>-<ms>.tsv.bad) + sales.log. Restart: the registry
   is read again; when the merchant's chunk is loaded its entity is re-attached by UUID (name + Use re-applied); still missing 15 s
   after its chunk loaded = it was not saved by the engine -> re-spawned AT THE SAME SPOT with the same stock (old UUID kept as a ghost).
   NO DUPLICATES / ORPHANS: a RefSystem on NPCEntity sees every NPC that is added (spawn or chunk load): a GHOST UUID, or an NPC with
   our role AND our nameplate that is not a current merchant, is removed at once (CommandBuffer.tryRemoveEntity). Ghosts are also
   retried every second and forgotten after 7 days. Switching the part off removes every merchant where loaded (the rest as ghosts)
   and keeps the lines, so they come back when switched on.
ENGINE SEAM: every call that needs a live world (chunk / block / fluid / environment / height, players, spawn point, NPC spawn / find /
remove, chat, the player's containers / position, world list + World.execute) goes through MerchEng's static wrappers; the harness sets
MerchEng.API to a stand-in world. Everything else (config, registry, spot rules, rumours, restock, the buy flow on REAL ItemContainers,
coins + gear bridges, commands, the page, the ECS handlers on stand-in stores) runs for real in the harness.
"""
import sys, os, json, zipfile, re, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI
import skyycfg as CFG

if "--deploy" in sys.argv:
    raise SystemExit("SkyyMerchants: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
MOD = "SkyyMerchants"
NODE = "skyymerchants.admin"
PKG = "com.skyy.merchants"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
CFG_FILE = "Skyy_SkyyMerchants/config.properties"
SUI.verify()
KIT_ID = SUI.kit_id()
COL = SUI.COLOR
COL_RUMOUR, COL_OK, COL_ERR, COL_INFO = COL["gold"], COL["success"], COL["error"], COL["info"]

ROLE = "Temple_Klops"                      # vanilla: Variant of Template_Temple (Invulnerable), MotionStatic, Klops_Merchant look
HINT = "server.interactionHints.trade"     # vanilla lang "Press [{key}] to trade" (Kweebec_Merchant's own hint)
USE_ROOT = "*UseNPC"                       # RoleBuilderSystem.onEntityAdd: every NPC's Use root
NAME = "Traveling Merchant"
GROUND = "Soil_Grass,Soil_Dirt,Soil_Sand,Soil_Snow,Soil_Gravel,Soil_Mud,Soil_Needles,Soil_Ash,Soil_Pebbles,Rock_Stone,Rock_Sandstone"
RUMOUR = "[Merchants] A traveling merchant was seen near the {place} in {zone} ({region}), {where}."
GRACE_MS = 15000                           # a merchant missing this long after its chunk loaded is re-spawned at its spot
RETRY_MS = 5000                            # no spot found: try again after this long
SPOT_TRIES = 16                            # random columns per spot search (each = a height + 3 block reads; stops at the first good one)
GHOST_DAYS = 7
ZONES = [("zone1", "default", "Env_Zone1", "1-20"), ("zone2", "default", "Env_Zone2", "20-30"),
         ("zone3", "default", "Env_Zone3", "30-45"), ("zone4", "default", "Env_Zone4", "45-60")]
REGION_KEYS = {1: "Emerald_Wilds", 2: "Howling_Sands", 3: "Whisperfrost_Frontiers", 4: "Devastated_Lands"}
# the plain words of the environment suffixes the rumours name (Env_ZoneN_<suffix>); anything else = the suffix in lower case
PLACE_WORDS = {"Plains": "plains", "Forests": "forests", "Autumn": "autumn woods", "Azure": "azure forest", "Swamps": "swamps",
               "Mountains": "mountains", "Shores": "shore", "Kweebec": "Kweebec woods", "Trork": "Trork lands", "Savanna": "savanna",
               "Scrub": "scrublands", "Plateaus": "plateaus", "Deserts": "desert", "Oasis": "oasis", "Feran": "Feran lands",
               "Scarak": "Scarak lands", "Tundra": "tundra", "Glacial": "glaciers", "Outlander": "Outlander lands", "Wastes": "wastes",
               "Crucible": "crucible", "Volcanoes": "volcanoes", "Jungles": "jungle", "Villages": "villages", "Encounters": "wilds",
               "Graveyard": "graveyard", "Mage_Towers": "mage towers", "Spawn": "spawn lands"}
# Special weapons per zone (Skyy: "Special weapons"; level-banded per zone). None of the boss specials of research/Pack-Armor-Plan.md 3.3
# nor the Armory "specials" of docs/answered/gear.md 2026-10-08 (flails / whips = the Berserker specials of the plan's fairness table,
# Antique shields = listed among the specials),
# no developer / UT bow, no Crystal staff (vanilla "Work in Progress"). source: "vanilla" = Assets.zip, else the installed pack archive.
WEAPONS = [
    # zone 1 (Lv 1-20): The Armory Lv 15-20 + vanilla elemental shortbows (Lv 20)
    ("Sword_Iron_Green", "1", 2500, 1, "TheArmoryMod"), ("Weapon_Battleaxe_Iron_Blue", "1", 2500, 1, "TheArmoryMod"),
    ("Weapon_Shield_Iron_Red_Pat", "1", 2000, 1, "TheArmoryMod"),
    ("Longsword_Iron_Red", "1", 3000, 1, "TheArmoryMod"), ("Dagger_Iron_Purple", "1", 3000, 1, "TheArmoryMod"),
    ("Mace_Iron_Cyan", "1", 3000, 1, "TheArmoryMod"), ("Weapon_Shortbow_Frost", "1", 2000, 1, "vanilla"),
    ("Weapon_Shortbow_Flame", "1", 2000, 1, "vanilla"),
    # every zone: one Mage / Priest / Monk row from our own SkyyArmory ladder (fair share per class, docs/answered/gear.md 2026-10-08),
    # metal by the zone band (Iron 15-23, Thorium 20-28, Adamantite 35-43, Onyxium = Lv 50 like the vanilla Onyxium rows)
    ("Weapon_Wand_Iron", "1", 2500, 1, "SkyyArmory"), ("Weapon_Spellbook_Iron", "1", 2500, 1, "SkyyArmory"),
    ("Weapon_Bo_Iron", "1", 2500, 1, "SkyyArmory"),
    # zone 2 (Lv 20-30): vanilla Rare Lv 25-30 + Armory Thorium colours + More Crossbow Tiers Thorium
    ("Weapon_Axe_Bone", "2", 6000, 1, "vanilla"), ("Weapon_Daggers_Claw_Bone", "2", 6000, 1, "vanilla"),
    ("Weapon_Sword_Frost", "2", 7500, 1, "vanilla"), ("Weapon_Daggers_Fang_Doomed", "2", 7500, 1, "vanilla"),
    ("Weapon_Crossbow_Ancient_Steel", "2", 7500, 1, "vanilla"), ("Sword_Thorium_Magenta", "2", 7500, 1, "TheArmoryMod"),
    ("Mace_Thorium_Yellow", "2", 7500, 1, "TheArmoryMod"), ("Weapon_Battleaxe_Thorium_Red", "2", 7500, 1, "TheArmoryMod"),
    ("Weapon_Crossbow_Thorium", "2", 7500, 1, "More_Crossbow_Tiers"),
    ("Weapon_Wand_Thorium", "2", 7000, 1, "SkyyArmory"), ("Weapon_Spellbook_Thorium", "2", 7000, 1, "SkyyArmory"),
    ("Weapon_Bo_Thorium", "2", 7000, 1, "SkyyArmory"),
    # zone 3 (Lv 30-45): vanilla Saurian Lv 40 + Armory Cobalt / Adamantite colours + More Crossbow Tiers Cobalt / Adamantite
    ("Weapon_Spear_Adamantite_Saurian", "3", 18000, 1, "vanilla"), ("Weapon_Daggers_Adamantite_Saurian", "3", 18000, 1, "vanilla"),
    ("Weapon_Longsword_Adamantite_Saurian", "3", 18000, 1, "vanilla"), ("Longsword_Cobalt_Purple", "3", 15000, 1, "TheArmoryMod"),
    ("Sword_Cobalt_Cyan", "3", 15000, 1, "TheArmoryMod"), ("Dagger_Cobalt_Red", "3", 15000, 1, "TheArmoryMod"),
    ("Weapon_Battleaxe_Adamantite_Green", "3", 18000, 1, "TheArmoryMod"), ("Weapon_Crossbow_Cobalt", "3", 15000, 1, "More_Crossbow_Tiers"),
    ("Weapon_Crossbow_Adamantite", "3", 18000, 1, "More_Crossbow_Tiers"),
    ("Weapon_Wand_Adamantite", "3", 18000, 1, "SkyyArmory"), ("Weapon_Spellbook_Adamantite", "3", 18000, 1, "SkyyArmory"),
    ("Weapon_Bo_Adamantite", "3", 18000, 1, "SkyyArmory"),
    # zones 3 + 4: Mithril (band 40-49 straddles zone 3 Lv 30-45 and zone 4 Lv 45-60)
    ("Weapon_Longsword_Mithril", "3,4", 40000, 1, "vanilla"), ("Weapon_Mace_Mithril", "3,4", 40000, 1, "vanilla"),
    ("Weapon_Crossbow_Mithril", "3,4", 40000, 1, "More_Crossbow_Tiers"),
    # zone 4 (Lv 45-60): vanilla Epic Onyxium Lv 50 + SkyyArmory Onyxium (Kunai: zone 4 has no Armory dagger)
    ("Weapon_Sword_Onyxium", "4", 45000, 1, "vanilla"), ("Weapon_Spear_Onyxium", "4", 45000, 1, "vanilla"),
    ("Weapon_Wand_Onyxium", "4", 45000, 1, "SkyyArmory"), ("Weapon_Spellbook_Onyxium", "4", 45000, 1, "SkyyArmory"),
    ("Weapon_Bo_Onyxium", "4", 45000, 1, "SkyyArmory"), ("Weapon_Kunai_Onyxium", "4", 45000, 1, "SkyyArmory"),
]
# Mounts: no rideable mount is sold as an ITEM by vanilla or by an enabled pack mod (checked: Assets.zip has no mount / saddle / whistle /
# mount egg item; the mount mods in Mods - Kazzy, More Mounts, Traveling Mounts, Ancient Riders, Bio's Kobolds - are not in the pack).
MOUNTS = []
PETS = []                                  # filled when pets ship (Skyy: "Pet eggs later")
NEVER = ("Weapon_Elemental_*,RuneBlade*,DualRuneBlade,LahatChereb,Hepta_Axe,GhostSword,Zweihander,Fist,Weapon_Dualswords_*,"
         "Weapon_Shortbow_Combat,Weapon_Shortbow_Bomb,Weapon_Shortbow_Pull,Weapon_Shortbow_Ricochet,Weapon_Shortbow_Vampire,"
         "Weapon_Shortbow_Test_Zoom,Weapon_Longsword_Flame,Weapon_Staff_Crystal_*,Skyy_Sack_*,Debug_*,FireWhip,ScorpianFlail,"
         "Antique_Shield,AntiqueShield*")

# ================= build-time desk checks (Assets.zip + the installed pack archives, read only) =================
az = zipfile.ZipFile(ASSETS)
AZ = set(az.namelist())


def vjson(path):
    return json.loads(az.read(path).decode("utf-8-sig"))


_roles = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
_r = vjson(_roles[ROLE])
_tt = vjson(_roles["Template_Temple"])
if (_r.get("Type") != "Variant" or _r.get("Reference") != "Template_Temple" or (_r.get("Modify") or {}).get("MotionStatic") is not True
        or _tt.get("Invulnerable") is not True or "InteractionInstruction" in json.dumps(_r) or "InteractionInstruction" in json.dumps(_tt)):
    raise SystemExit("%s changed (must stay a static, invulnerable, shop-less Template_Temple variant): %r" % (ROLE, _r))
LANG = {}
for _l in az.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines():
    if "=" in _l and not _l.lstrip().startswith("#"):
        _k, _v = _l.split("=", 1)
        LANG[_k.strip()] = _v.strip()
if "interactionHints.trade" not in LANG:
    raise SystemExit("vanilla hint interactionHints.trade missing")
REGION = {}
for _n, _k in REGION_KEYS.items():
    REGION[_n] = LANG["map.zone." + _k]
ENV_IDS = set(n.rsplit("/", 1)[1][:-5] for n in AZ if "/Environments/" in n and n.endswith(".json"))
for _z in ZONES:
    if _z[2] not in ENV_IDS or not any(e.startswith(_z[2] + "_") for e in ENV_IDS):
        raise SystemExit("environment %s missing in Assets.zip" % _z[2])
ITEM_IDS = set(n.rsplit("/", 1)[1][:-5] for n in AZ if n.startswith("Server/Item/Items/") and n.endswith(".json"))
NAMES = {}
PACK_SEEN = {}
COLOURS = {"Black", "Blue", "Cyan", "Gray", "Green", "Magenta", "Purple", "Red", "Rusty", "White", "Yellow"}


def pack_items(stem):
    """item id -> en-US name of an installed pack archive (read only); None when the archive is not installed"""
    if stem in PACK_SEEN:
        return PACK_SEEN[stem]
    out = None
    if os.path.isdir(B.MODS_DIR):
        for f in sorted(os.listdir(B.MODS_DIR)):
            if f.startswith(stem) and (f.endswith(".jar") or f.endswith(".zip")):
                with zipfile.ZipFile(os.path.join(B.MODS_DIR, f)) as z:
                    ids = set(n.rsplit("/", 1)[1][:-5] for n in z.namelist() if "/Item/Items/" in n and n.endswith(".json"))
                    lang = {}
                    for n in z.namelist():
                        if n.endswith("en-US/server.lang"):
                            for l in z.read(n).decode("utf-8", "replace").splitlines():
                                if "=" in l:
                                    a, b = l.split("=", 1)
                                    lang[a.strip()] = b.strip()
                    out = {}
                    for n in z.namelist():
                        if "/Item/Items/" not in n or not n.endswith(".json"):
                            continue
                        i = n.rsplit("/", 1)[1][:-5]
                        try:
                            k = (json.loads(z.read(n).decode("utf-8-sig")).get("TranslationProperties") or {}).get("Name") or ""
                        except Exception:
                            k = ""
                        k = k[7:] if k.startswith("server.") else k
                        nm = lang.get("items.%s.name" % i) or lang.get(k) or LANG.get(k) or ""
                        tail = i.rsplit("_", 1)[-1]
                        if nm and not lang.get("items.%s.name" % i) and tail in COLOURS:
                            nm = "%s (%s)" % (nm, tail)
                        out[i] = nm
                break
    PACK_SEEN[stem] = out
    return out


_never = [p.strip() for p in NEVER.split(",") if p.strip()]


def walled(i):
    return any((i.startswith(p[:-1]) if p.endswith("*") else i == p) for p in _never) or i.startswith("Skyy_Sack_")


NOT_INSTALLED = []
for _id, _zn, _pr, _st, _src in WEAPONS + MOUNTS + PETS:
    if walled(_id):
        raise SystemExit("default stock %s is on the never-sell list" % _id)
    if _src == "vanilla":
        if _id not in ITEM_IDS:
            raise SystemExit("vanilla item %s missing in Assets.zip" % _id)
        NAMES[_id] = LANG.get("items.%s.name" % _id, "")
    else:
        _pk = pack_items(_src)
        if _pk is None:
            NOT_INSTALLED.append(_id)
        elif _id not in _pk:
            raise SystemExit("%s is not an item of the installed %s" % (_id, _src))
        else:
            NAMES[_id] = _pk[_id]
for _k in list(NAMES):
    if not NAMES[_k]:
        del NAMES[_k]
print("desk: role %s shop-less; %d zones (%s); %d weapons (%d named, not installed here: %s); mounts %d; pet eggs %d"
      % (ROLE, len(ZONES), ", ".join(REGION[n] for n in sorted(REGION)), len(WEAPONS), len(NAMES), NOT_INSTALLED or "none",
         len(MOUNTS), len(PETS)))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "KITID": KIT_ID,
    "COLRUM": COL_RUMOUR, "COLOK": COL_OK, "COLERR": COL_ERR, "COLINF": COL_INFO,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CAC": "com.hypixel.hytale.component.ComponentAccessor",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "ARCH": "com.hypixel.hytale.component.Archetype",
    "EV": "com.hypixel.hytale.component.system.EcsEvent",
    "EES": "com.hypixel.hytale.component.system.EntityEventSystem",
    "RSYS": "com.hypixel.hytale.component.system.RefSystem",
    "ADR": "com.hypixel.hytale.component.AddReason",
    "RR": "com.hypixel.hytale.component.RemoveReason",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "CHS": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
    "WCH": "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BCH": "com.hypixel.hytale.server.core.universe.world.chunk.BlockChunk",
    "ENVA": "com.hypixel.hytale.server.core.asset.type.environment.config.Environment",
    "SPP": "com.hypixel.hytale.server.core.universe.world.spawn.ISpawnProvider",
    "TRF": "com.hypixel.hytale.math.vector.Transform",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3D": "org.joml.Vector3d",
    "R3F": "com.hypixel.hytale.math.vector.Rotation3f",
    "NPCP": "com.hypixel.hytale.server.npc.NPCPlugin",
    "NPC": "com.hypixel.hytale.server.npc.entities.NPCEntity",
    "UUC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
    "ITB": "com.hypixel.hytale.server.core.modules.entity.component.Interactable",
    "ITS": "com.hypixel.hytale.server.core.modules.interaction.Interactions",
    "ITY": "com.hypixel.hytale.protocol.InteractionType",
    "NPL": "com.hypixel.hytale.server.core.entity.nameplate.Nameplate",
    "DNC": "com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent",
    "PDN": "com.hypixel.hytale.server.core.modules.entity.component.PersistentDisplayName",
    "PAIR": "it.unimi.dsi.fastutil.Pair",
    "UEPRE": "com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BT": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
}
AC = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
PB_ = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["NPCP"], "get"), (T["NPCP"], "spawnNPC"), (T["NPCP"], "hasRoleName"), (T["NPC"], "getRoleName"), (T["NPC"], "getComponentType"),
             (T["UUC"], "getUuid"), (T["UUC"], "getComponentType"), (T["ITB"], "getComponentType"), (T["ITS"], "setInteractionHint"), (T["ITS"], "getInteractionHint"),
             (T["ITS"], "getInteractionId"), (T["ITS"], "setInteractionId"), (T["ITS"], "getComponentType"), (T["ITY"], "Use"),
             (T["NPL"], "getComponentType"), (T["NPL"], "getText"), (T["DNC"], "getComponentType"), (T["DNC"], "getDisplayName"),
             (T["PDN"], "getComponentType"), (T["PAIR"], "first"), (T["UEPRE"], "getTargetEntity"), (T["UEPRE"], "setCancelled"),
             (T["UEPRE"], "isCancelled"), (T["RSYS"], "onEntityAdded"), (T["RSYS"], "onEntityRemove"), (T["CB"], "tryRemoveEntity"),
             (T["RR"], "REMOVE"), (T["ST"], "removeEntity"), (T["ST"], "getComponent"), (T["ST"], "putComponent"),
             (T["ST"], "ensureComponent"), (T["ST"], "getExternalData"), (T["ACH"], "getReferenceTo"), (T["ARCH"], "empty"),
             (T["EST"], "getStore"), (T["EST"], "getRefFromUUID"), (T["EST"], "getWorld"), (T["WLD"], "getName"), (T["WLD"], "execute"),
             (T["WLD"], "getEntityStore"), (T["WLD"], "getChunkStore"), (T["WLD"], "getChunkIfLoaded"), (T["WLD"], "getPlayerRefs"),
             (T["WLD"], "getWorldConfig"), (T["CHS"], "getChunkComponent"), (T["WCH"], "getBlockType"), (T["WCH"], "getHeight"),
             (T["WCH"], "getFluidId"), (T["BTY"], "getId"), (T["BCH"], "getEnvironment"), (T["BCH"], "getComponentType"),
             (T["ENVA"], "getAssetMap"), (T["ENVA"], "getId"), (T["CHU"], "indexChunkFromBlock"), (T["SPP"], "getSpawnPoints"),
             (T["TRF"], "getPosition"), (T["UNI"], "get"), (T["UNI"], "getWorld"), (T["UNI"], "getWorlds"), (T["UNI"], "getPlayer"),
             (T["HSV"], "SCHEDULED_EXECUTOR"), (T["MSG"], "raw"), (T["MSG"], "color"), (T["MSG"], "getRawText"),
             (T["PLA"], "getComponentType"), (T["PLA"], "getPageManager"), (T["PLA"], "getInventory"), (T["INV"], "getStorage"),
             (T["INV"], "getHotbar"), (T["INV"], "getBackpack"), (T["IC"], "getCapacity"), (T["IC"], "getItemStack"),
             (T["IC"], "addItemStack"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"), (T["ITM"], "getAssetMap"),
             (T["ITM"], "getMaxStack"), (T["ITM"], "getTranslationKey"), (T["I18N"], "get"), (T["I18N"], "getMessage"),
             (T["TC"], "getComponentType"), (T["TC"], "getPosition"), (T["PR"], "getUuid"), (T["PR"], "getUsername"),
             (T["PR"], "sendMessage"), (T["PR"], "getTransform"), (T["PR"], "getComponentType"), (T["PR"], "hasPermission"),
             (T["PAGE"], "rebuild"), (T["PAGE"], "close"), (T["EVD"], "of"), (T["EVD"], "append"), (T["UEB"], "addEventBinding"),
             (T["UCB"], "set"), (T["UCB"], "appendInline"), (T["R3F"], "setYaw"), (AC, "requirePermission"), (AC, "setPermissionGroups"),
             (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "addAliases"), (T["CTX"], "get"), (T["ATY"], "STRING"),
             (PB_, "getCommandRegistry"), (PB_, "getEntityStoreRegistry"), (PB_, "getLogger"), (PB_, "getDataDirectory"),
             (PB_, "shutdown"), ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem")):
    B.probe(pool, c, m)
# the exact call shapes (a drift stops the build): spawnNPC(Store, String role, String flock, Vector3dc, Rotation3fc) - NPCPlugin.spawnNPC
# passes arg 2 to getIndex (bytecode 2026-10-09); WorldChunk getHeight (II)S / getFluidId (III)I; BlockChunk.getEnvironment (III)I
_sig = lambda cls, name: [str(m.getSignature()) for m in pool.get(cls).getDeclaredMethods() if str(m.getName()) == name]
assert "(Lcom/hypixel/hytale/component/Store;Ljava/lang/String;Ljava/lang/String;Lorg/joml/Vector3dc;Lcom/hypixel/hytale/math/vector/Rotation3fc;)Lit/unimi/dsi/fastutil/Pair;" in _sig(T["NPCP"], "spawnNPC"), _sig(T["NPCP"], "spawnNPC")
assert "(II)S" in _sig(T["WCH"], "getHeight") and "(III)I" in _sig(T["WCH"], "getFluidId"), "WorldChunk changed"
assert "(III)I" in _sig(T["BCH"], "getEnvironment"), "BlockChunk.getEnvironment(int, int, int) changed"
assert "(Ljava/util/UUID;)Lcom/hypixel/hytale/component/Ref;" in _sig(T["EST"], "getRefFromUUID"), "EntityStore.getRefFromUUID changed"

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


def jstr(s):
    return json.dumps(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs) if xs else "new String[0]"


ALL = []


def cls(name, sup=None):
    c = mk(name, sup)
    ALL.append(c)
    return c


# =====================================================================================================================
# MerchLog: server log (+ LINES, a harness hook: every INFO / WARN line; null in game)
# =====================================================================================================================
log = cls("MerchLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List LINES;")
F(log, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(log, r"""
public static void info(String msg) {
  try { if (LINES != null) LINES.add("INFO " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyMerchants] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LINES != null) LINES.add("WARN " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyMerchants] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warnOnce(String key, String msg) {
  if (ONCE.size() > 2000) ONCE.clear();
  if (ONCE.putIfAbsent(key, Boolean.TRUE) == null) warn(msg);
}""")
M(log, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(log, r"""
public static java.util.function.Function fn(String key) {
  try { Object o = bridge().get(key); return o instanceof java.util.function.Function ? (java.util.function.Function) o : null; } catch (Throwable t) { return null; }
}""")
M(log, r"""
public static String grp(long n) {
  String s = String.valueOf(Math.abs(n));
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < s.length(); i++) {
    if (i > 0 && (s.length() - i) % 3 == 0) b.append(',');
    b.append(s.charAt(i));
  }
  return (n < 0L ? "-" : "") + b.toString();
}""")
M(log, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
}""")

# =====================================================================================================================
# MerchApi (interface) + MerchEng: the engine seam (header). API == null in game = the real calls.
# =====================================================================================================================
api = pool.makeInterface(PKG + ".MerchApi")
ALL.append(api)
for sig in ("public abstract String[] worlds();",
            "public abstract boolean exec(String wn, Runnable r);",
            "public abstract int height(String wn, int x, int z);",
            "public abstract String block(String wn, int x, int y, int z);",
            "public abstract boolean fluid(String wn, int x, int y, int z);",
            "public abstract String env(String wn, int x, int y, int z);",
            "public abstract double[] players(String wn);",
            "public abstract double[] spawnPoint(String wn);",
            "public abstract boolean roleOk(String role);",
            "public abstract String spawn(String wn, String role, double x, double y, double z, float yaw, String name);",
            "public abstract int present(String wn, String uuid, int x, int z, String name);",
            "public abstract int remove(String wn, String uuid);",
            "public abstract void tell(String wn, String text, String color);",
            "public abstract void tellPlayer(java.util.UUID u, String text, String color);",
            "public abstract @IC@[] conts(Object player);",
            "public abstract double[] pos(@REF@ ref, @ST@ st);",
            "public abstract boolean open(@REF@ ref, @PR@ pr, @PAGE@ page);"):
    M(api, sig)

eng = cls("MerchEng")
F(eng, "public static volatile @PKG@.MerchApi API = null;")
F(eng, "public static final String HINT = %s;" % jstr(HINT))
F(eng, "public static final String USE_ROOT = %s;" % jstr(USE_ROOT))
M(eng, r"""
public static @WLD@ world(String wn) {
  if (wn == null) return null;
  try { @UNI@ u = @UNI@.get(); return u == null ? null : u.getWorld(wn); } catch (Throwable t) { return null; }
}""")
# worlds with at least one player (the scheduler only wakes those)
M(eng, r"""
public static String[] worlds() {
  if (API != null) return API.worlds();
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    @UNI@ u = @UNI@.get();
    if (u == null) return new String[0];
    java.util.Iterator it = u.getWorlds().values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @WLD@)) continue;
      @WLD@ w = (@WLD@) o;
      java.util.Collection c = w.getPlayerRefs();
      if (c != null && !c.isEmpty()) out.add(w.getName());
    }
  } catch (Throwable t) { }
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
M(eng, r"""
public static boolean exec(String wn, Runnable r) {
  if (API != null) return API.exec(wn, r);
  @WLD@ w = world(wn);
  if (w == null) return false;
  w.execute(r);
  return true;
}""")
M(eng, r"""
public static @WCH@ chunk(@WLD@ w, int x, int z) {
  if (w == null) return null;
  return w.getChunkIfLoaded(@CHU@.indexChunkFromBlock(x, z));
}""")
# -1 = the chunk is not loaded (never loads one)
M(eng, r"""
public static int height(String wn, int x, int z) {
  if (API != null) return API.height(wn, x, z);
  @WCH@ c = chunk(world(wn), x, z);
  if (c == null) return -1;
  return c.getHeight(x, z);
}""")
# block id; null = not loaded
M(eng, r"""
public static String block(String wn, int x, int y, int z) {
  if (API != null) return API.block(wn, x, y, z);
  if (y < 0 || y >= 320) return "Empty";
  @WCH@ c = chunk(world(wn), x, z);
  if (c == null) return null;
  @BTY@ t = c.getBlockType(x, y, z);
  if (t == null) return "Empty";
  Object oid = t.getId();
  return oid == null ? "?" : oid.toString();
}""")
M(eng, r"""
public static boolean fluid(String wn, int x, int y, int z) {
  if (API != null) return API.fluid(wn, x, y, z);
  if (y < 0 || y >= 320) return false;
  @WCH@ c = chunk(world(wn), x, z);
  if (c == null) return true;
  return c.getFluidId(x, y, z) != 0;
}""")
# the environment id at a block (BlockChunk 3D environment, SkyyMobs MobLevel.blockEnv); null = not loaded / none
M(eng, r"""
public static String env(String wn, int x, int y, int z) {
  if (API != null) return API.env(wn, x, y, z);
  @WLD@ w = world(wn);
  if (w == null || chunk(w, x, z) == null) return null;
  try {
    Object c = w.getChunkStore().getChunkComponent(@CHU@.indexChunkFromBlock(x, z), @BCH@.getComponentType());
    if (!(c instanceof @BCH@)) return null;
    int idx = ((@BCH@) c).getEnvironment(x, y, z);
    if (idx < 0) return null;
    Object a = @ENVA@.getAssetMap().getAsset(idx);
    return a instanceof @ENVA@ ? ((@ENVA@) a).getId() : null;
  } catch (Throwable t) { return null; }
}""")
# x, z of every player in the world (flattened pairs)
M(eng, r"""
public static double[] players(String wn) {
  if (API != null) return API.players(wn);
  @WLD@ w = world(wn);
  if (w == null) return new double[0];
  java.util.ArrayList l = new java.util.ArrayList();
  try {
    java.util.Iterator it = w.getPlayerRefs().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      @TRF@ t = ((@PR@) o).getTransform();
      if (t == null || t.getPosition() == null) continue;
      l.add(t.getPosition());
    }
  } catch (Throwable t) { }
  double[] a = new double[l.size() * 2];
  for (int i = 0; i < l.size(); i++) { @V3D@ p = (@V3D@) l.get(i); a[2 * i] = p.x; a[2 * i + 1] = p.z; }
  return a;
}""")
M(eng, r"""
public static double[] spawnPoint(String wn) {
  if (API != null) return API.spawnPoint(wn);
  @WLD@ w = world(wn);
  try {
    @SPP@ sp = w.getWorldConfig().getSpawnProvider();
    @TRF@[] ts = null;
    if (sp != null) ts = sp.getSpawnPoints();
    if (ts != null && ts.length > 0 && ts[0] != null && ts[0].getPosition() != null) return new double[] { ts[0].getPosition().x, ts[0].getPosition().z };
  } catch (Throwable t) { }
  return new double[] { 0.0, 0.0 };
}""")
M(eng, r"""
public static boolean roleOk(String role) {
  if (role == null || role.trim().length() == 0) return false;
  if (API != null) return API.roleOk(role);
  try { @NPCP@ p = @NPCP@.get(); return p == null || p.hasRoleName(role.trim()); } catch (Throwable t) { return true; }
}""")
M(eng, r"""
public static java.util.UUID uuidOf(@ST@ st, @REF@ r) {
  try {
    @UUC@ u = (@UUC@) st.getComponent(r, @UUC@.getComponentType());
    return u == null ? null : u.getUuid();
  } catch (Throwable t) { return null; }
}""")
# the merchant's look: name over its head (Nameplate + DisplayName + PersistentDisplayName, the vanilla EntityNameplateCommand set) +
# F works (Interactable + a Use root, vanilla EntityMakeInteractableCommand / RoleBuilderSystem) + the trade hint. Only what is missing.
M(eng, r"""
public static int prepare(@ST@ st, @REF@ r, String name) {
  int n = 0;
  @NPL@ pl = (@NPL@) st.getComponent(r, @NPL@.getComponentType());
  if (pl == null || pl.getText() == null || !pl.getText().equals(name)) {
    @MSG@ m = @MSG@.raw(name);
    st.putComponent(r, @DNC@.getComponentType(), new @DNC@(m));
    st.putComponent(r, @PDN@.getComponentType(), new @PDN@(m));
    st.putComponent(r, @NPL@.getComponentType(), new @NPL@(name));
    n++;
  }
  if (st.getComponent(r, @ITB@.getComponentType()) == null) { st.ensureComponent(r, @ITB@.getComponentType()); n++; }
  @ITS@ its = (@ITS@) st.getComponent(r, @ITS@.getComponentType());
  if (its == null) { its = new @ITS@(); st.putComponent(r, @ITS@.getComponentType(), its); n++; }
  if (its.getInteractionId(@ITY@.Use) == null) { its.setInteractionId(@ITY@.Use, USE_ROOT); n++; }
  if (its.getInteractionHint() == null || !HINT.equals(its.getInteractionHint())) { its.setInteractionHint(HINT); n++; }
  return n;
}""")
# spawn one merchant (World.execute / a command: never inside a system's processing); answers its UUID or null
M(eng, r"""
public static String spawn(String wn, String role, double x, double y, double z, float yaw, String name) {
  if (API != null) return API.spawn(wn, role, x, y, z, yaw, name);
  @WLD@ w = world(wn);
  if (w == null) return null;
  @ST@ st = w.getEntityStore().getStore();
  @R3F@ rot = new @R3F@();
  rot.setYaw(yaw);
  @PAIR@ p = @NPCP@.get().spawnNPC(st, role, (String) null, new @V3D@(x, y, z), rot);
  @REF@ e = p == null ? null : (@REF@) p.first();
  if (e == null || !e.isValid()) return null;
  prepare(st, e, name);
  java.util.UUID u = uuidOf(st, e);
  if (u == null) { st.removeEntity(e, @RR@.REMOVE); return null; }
  return u.toString();
}""")
# 1 = the entity is here (its look re-applied when missing), 0 = its chunk is loaded but no entity, -1 = the chunk is not loaded
M(eng, r"""
public static int present(String wn, String uuid, int x, int z, String name) {
  if (API != null) return API.present(wn, uuid, x, z, name);
  @WLD@ w = world(wn);
  if (w == null) return -1;
  try {
    @REF@ r = w.getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    if (r != null && r.isValid()) { prepare(w.getEntityStore().getStore(), r, name); return 1; }
  } catch (Throwable t) { }
  return chunk(w, x, z) == null ? -1 : 0;
}""")
# 1 = removed, 0 = not found (not loaded, or gone)
M(eng, r"""
public static int remove(String wn, String uuid) {
  if (API != null) return API.remove(wn, uuid);
  @WLD@ w = world(wn);
  if (w == null) return 0;
  try {
    @REF@ r = w.getEntityStore().getRefFromUUID(java.util.UUID.fromString(uuid));
    if (r == null || !r.isValid()) return 0;
    w.getEntityStore().getStore().removeEntity(r, @RR@.REMOVE);
    return 1;
  } catch (Throwable t) { @PKG@.MerchLog.warnOnce("rm:" + t.getClass().getName(), "removing merchant " + uuid + " failed: " + t); return 0; }
}""")
M(eng, r"""
public static void say(@PR@ pr, String text, String color) {
  try { @MSG@ m = @MSG@.raw(text); if (color != null) m = m.color(color); pr.sendMessage(m); } catch (Throwable t) { }
}""")
M(eng, r"""
public static void tell(String wn, String text, String color) {
  if (API != null) { API.tell(wn, text, color); return; }
  @WLD@ w = world(wn);
  if (w == null) return;
  try {
    Object[] a = w.getPlayerRefs().toArray();
    for (int i = 0; i < a.length; i++) if (a[i] instanceof @PR@) say((@PR@) a[i], text, color);
  } catch (Throwable t) { }
}""")
M(eng, r"""
public static void tellPlayer(java.util.UUID u, String text, String color) {
  if (u == null) return;
  if (API != null) { API.tellPlayer(u, text, color); return; }
  try { @PR@ pr = @UNI@.get().getPlayer(u); if (pr != null) say(pr, text, color); } catch (Throwable t) { }
}""")
# the containers a purchase goes into, storage first (Bazaar Inv.conts order)
M(eng, r"""
public static @IC@[] conts(Object player) {
  if (API != null) return API.conts(player);
  if (!(player instanceof @PLA@)) return new @IC@[0];
  @INV@ inv = ((@PLA@) player).getInventory();
  if (inv == null) return new @IC@[0];
  return new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
}""")
M(eng, r"""
public static double[] pos(@REF@ ref, @ST@ st) {
  if (API != null) return API.pos(ref, st);
  try {
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) return null;
    return new double[] { tc.getPosition().x, tc.getPosition().y, tc.getPosition().z };
  } catch (Throwable t) { return null; }
}""")
M(eng, r"""
public static boolean open(@REF@ ref, @PR@ pr, @PAGE@ page) {
  if (API != null) return API.open(ref, pr, page);
  if (ref == null || !ref.isValid()) return false;
  @ST@ st = ref.getStore();
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  if (p == null) return false;
  p.getPageManager().openCustomPage(ref, st, page);
  return true;
}""")
M(eng, r"""
public static boolean itemOk(String id) {
  if (id == null || id.length() == 0) return false;
  try { return @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { return false; }
}""")
M(eng, r"""
public static int maxStack(String id) {
  try { @ITM@ it = (@ITM@) @ITM@.getAssetMap().getAsset(id); return it == null ? 0 : it.getMaxStack(); } catch (Throwable t) { return 0; }
}""")
M(eng, r"""
public static String tr(String id) {
  try {
    @ITM@ it = (@ITM@) @ITM@.getAssetMap().getAsset(id);
    if (it == null || it.getTranslationKey() == null) return null;
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    String k = it.getTranslationKey();
    String s = m.getMessage("en-US", k);
    if ((s == null || s.equals(k)) && k.startsWith("server.")) s = m.getMessage("en-US", k.substring(7));
    if (s == null || s.trim().length() == 0 || s.equals(k)) return null;
    return s;
  } catch (Throwable t) { return null; }
}""")
M(eng, r"""
public static String worldOf(@ST@ st) {
  try { Object e = st.getExternalData(); if (e instanceof @EST@) { @WLD@ w = ((@EST@) e).getWorld(); return w == null ? null : w.getName(); } } catch (Throwable t) { }
  return null;
}""")
M(eng, r"""
public static String plateOf(@ST@ st, @REF@ r) {
  try {
    @NPL@ p = (@NPL@) st.getComponent(r, @NPL@.getComponentType());
    if (p != null && p.getText() != null) return p.getText();
    @DNC@ d = (@DNC@) st.getComponent(r, @DNC@.getComponentType());
    if (d != null && d.getDisplayName() != null) return d.getDisplayName().getRawText();
  } catch (Throwable t) { }
  return null;
}""")
M(eng, r"""
public static String roleOf(@ST@ st, @REF@ r) {
  try { Object e = st.getComponent(r, @NPC@.getComponentType()); return e instanceof @NPC@ ? ((@NPC@) e).getRoleName() : null; } catch (Throwable t) { return null; }
}""")

# =====================================================================================================================
# MerchZone / MerchItem (table rows) + MerchCfg (settings; the kit binds the scalars, RELOAD re-reads the tables)
# =====================================================================================================================
zn = cls("MerchZone")
for _f in ("String key", "String name", "int num", "String world", "String area", "String[] inc", "String[] exc", "boolean any",
           "int lo", "int hi", "String region"):
    F(zn, "public %s;" % _f)
C(zn, "public MerchZone() { this.key = \"\"; this.name = \"\"; this.world = \"\"; this.area = \"\"; this.inc = new String[0]; this.exc = new String[0]; this.region = \"\"; }")
F(zn, "public static final String[] REGIONS = %s;" % jarr([""] + [REGION[n] for n in sorted(REGION)]))
# zone1 -> 1, "Zone 1"
M(zn, r"""
public static int numOf(String key) {
  if (key == null) return 0;
  String k = key.toLowerCase();
  if (!k.startsWith("zone") || k.length() < 5) return 0;
  try { return Integer.parseInt(k.substring(4)); } catch (Throwable t) { return 0; }
}""")
# "World|Area|Levels" (the kit's canonical value) or the file's "World/Area/Levels" -> a zone, null = bad
M(zn, r"""
public static @PKG@.MerchZone parse(String key, String value, String sep) {
  if (key == null || value == null) return null;
  String[] p = value.split(java.util.regex.Pattern.quote(sep), -1);
  if (p.length != 3) return null;
  @PKG@.MerchZone z = new @PKG@.MerchZone();
  z.key = key.trim();
  z.num = numOf(z.key);
  z.name = z.num > 0 ? "Zone " + z.num : z.key;
  z.region = z.num > 0 && z.num < REGIONS.length ? REGIONS[z.num] : "";
  z.world = p[0].trim();
  z.area = p[1].trim();
  if (z.world.length() == 0 || z.area.length() == 0) return null;
  java.util.ArrayList in = new java.util.ArrayList();
  java.util.ArrayList ex = new java.util.ArrayList();
  String[] a = z.area.split(",");
  for (int i = 0; i < a.length; i++) {
    String s = a[i].trim();
    if (s.length() == 0) continue;
    if (s.equals("*")) { z.any = true; continue; }
    if (s.startsWith("!")) { if (s.length() > 1) ex.add(s.substring(1)); }
    else in.add(s);
  }
  if (!z.any && in.isEmpty()) return null;
  z.inc = new String[in.size()];
  for (int i = 0; i < z.inc.length; i++) z.inc[i] = (String) in.get(i);
  z.exc = new String[ex.size()];
  for (int i = 0; i < z.exc.length; i++) z.exc[i] = (String) ex.get(i);
  String lv = p[2].trim();
  if (lv.length() == 0 || lv.equals("0")) { z.lo = 0; z.hi = 0; return z; }
  try {
    int d = lv.indexOf('-', 1);
    z.lo = Integer.parseInt((d < 0 ? lv : lv.substring(0, d)).trim());
    z.hi = d < 0 ? z.lo : Integer.parseInt(lv.substring(d + 1).trim());
  } catch (Throwable t) { return null; }
  if (z.lo < 0 || z.hi < z.lo || z.hi > 1000) return null;
  return z;
}""")
# the environment at a spot belongs to this zone (prefix match; "!" prefixes excluded; "*" = any, also an unknown environment)
M(zn, r"""
public boolean envOk(String env) {
  if (env == null) return this.any;
  for (int i = 0; i < this.exc.length; i++) if (env.startsWith(this.exc[i])) return false;
  if (this.any) return true;
  for (int i = 0; i < this.inc.length; i++) if (env.startsWith(this.inc[i])) return true;
  return false;
}""")
# a spot's lowest mob level lies in the band (lo <= L < hi; a one-level band = that level); no band = any
M(zn, r"""
public boolean levelOk(int L) {
  if (this.lo <= 0 && this.hi <= 0) return true;
  if (L < this.lo) return false;
  return L < this.hi || this.lo == this.hi && L == this.lo;
}""")
M(zn, "public String band() { return this.lo <= 0 ? \"any level\" : (this.lo == this.hi ? \"Lv \" + this.lo : \"Lv \" + this.lo + \"-\" + this.hi); }")

itm = cls("MerchItem")
for _f in ("String id", "String zones", "long price", "int stock", "int cat"):
    F(itm, "public %s;" % _f)
C(itm, "public MerchItem() { this.id = \"\"; this.zones = \"*\"; }")
M(itm, r"""
public static boolean zonesOk(String zones) {
  if (zones == null) return false;
  String z = zones.trim();
  if (z.equals("*")) return true;
  String[] a = z.split(",");
  int n = 0;
  for (int i = 0; i < a.length; i++) {
    String s = a[i].trim();
    if (s.length() == 0) continue;
    for (int k = 0; k < s.length(); k++) {
      char c = s.charAt(k);
      if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') && !(c >= '0' && c <= '9') && c != '_' && c != '-') return false;
    }
    n++;
  }
  return n > 0;
}""")
M(itm, r"""
public static @PKG@.MerchItem parse(String id, String value, String sep, int cat) {
  if (id == null || value == null) return null;
  String[] p = value.split(java.util.regex.Pattern.quote(sep), -1);
  if (p.length != 3) return null;
  @PKG@.MerchItem it = new @PKG@.MerchItem();
  it.id = id.trim();
  it.zones = p[0].trim();
  it.cat = cat;
  try { it.price = Long.parseLong(p[1].trim()); it.stock = Integer.parseInt(p[2].trim()); } catch (Throwable t) { return null; }
  if (it.id.length() == 0 || !zonesOk(it.zones) || it.price < 0L || it.price > 1000000000000L || it.stock < 0 || it.stock > 1000) return null;
  return it;
}""")
M(itm, r"""
public boolean inZone(@PKG@.MerchZone z) {
  if (z == null) return false;
  String s = this.zones.trim();
  if (s.equals("*")) return true;
  String[] a = s.split(",");
  for (int i = 0; i < a.length; i++) {
    String t = a[i].trim();
    if (t.length() == 0) continue;
    if (t.equalsIgnoreCase(z.key)) return true;
    if (z.num > 0 && t.equals(String.valueOf(z.num))) return true;
  }
  return false;
}""")

cfgc = cls("MerchCfg")
SCALARS = [
    # key, label, cat, type, default, min, max, opts, unit, flags, help, FIELD, java type
    ("part.merchants", "Roaming merchants", "merch", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = every merchant leaves (removed where loaded) and none appear. On again = they come back.", "ON", "boolean"),
    ("merchant.moveSeconds", "Move every", "merch", "int", "1200", "60", "604800", "", "s", "live",
     "A merchant moves to a new random spot in its zone this often (and restocks).", "MOVE_S", "int"),
    ("merchant.name", "Name over its head", "merch", "text", NAME, "1", "40", "", "", "live",
     "The name players see. Changing it renames every merchant within a second.", "NAME", "java.lang.String"),
    ("merchant.role", "NPC look (vanilla role)", "merch", "text", ROLE, "1", "80", "", "", "new",
     "A vanilla NPC role id. Applies when a merchant next moves. Default Temple_Klops.", "ROLE", "java.lang.String"),
    ("merchant.ringMin", "Spot distance from players, min", "merch", "int", "48", "8", "512", "", "blocks", "live,adv",
     "New spots are looked for this far from a random player in the world, at least.", "RING_MIN", "int"),
    ("merchant.ringMax", "Spot distance from players, max", "merch", "int", "192", "16", "1024", "", "blocks", "live,adv",
     "...and at most this far (only loaded chunks are ever used).", "RING_MAX", "int"),
    ("merchant.playerGap", "Never closer to a player than", "merch", "int", "24", "0", "256", "", "blocks", "live,adv",
     "A merchant never appears this close to any player (so nobody sees it pop in).", "GAP", "int"),
    ("merchant.useRange", "Buying distance", "merch", "int", "8", "2", "64", "", "blocks", "live,adv",
     "Buying needs you this close to the merchant.", "USE_RANGE", "int"),
    ("merchant.offers", "Weapons per visit", "merch", "int", "4", "1", "30", "", "", "live",
     "How many weapons of its zone list a merchant brings each visit (picked at random).", "OFFERS", "int"),
    ("merchant.ground", "Ground it may stand on", "merch", "text", GROUND, "1", "2000", "", "", "live,adv",
     "Block id prefixes, comma separated. Built shapes (stairs, slabs, bricks...) never count.", "GROUND", "java.lang.String"),
    ("rumour.enabled", "Rumours in chat", "rumour", "bool", "true", "", "", "", "", "live",
     "On = when a merchant moves, everyone in that world gets a vague hint where.", "RUMOUR_ON", "boolean"),
    ("rumour.text", "Rumour text", "rumour", "text", RUMOUR, "1", "200", "", "", "live",
     "Placeholders {place} {where} {dir} {dist} {zone} {region} {name}. Never coordinates.", "RUMOUR", "java.lang.String"),
    ("merchant.neverSell", "Never sold (ids or Prefix*)", "stock", "text", NEVER, "1", "2000", "", "", "live",
     "Never sold, whatever the tables say. Mythic, Untiered, Set and Magic Bags are never sold anyway.", "NEVER", "java.lang.String"),
]
TABLES = [
    ("merchant.zones", "Zones", "zones", "table", "", "", "400", "text|text|text;type;World|Area|Levels", "", "live",
     "Area: env id prefixes (! = except, * = any). Levels: SkyyMobs band, 0 = any. One merchant each.", "zone."),
    ("merchant.weapons", "Special weapons", "stock", "table", "", "0", "1000000000", "text|int|int;both;Zones|Price|Stock", "coins", "new",
     "Zones: 1,2 or zone keys or *. Price in coins. Stock per visit. Applies from the next move.", "weapon."),
    ("merchant.mounts", "Mounts", "stock", "table", "", "0", "1000000000", "text|int|int;both;Zones|Price|Stock", "coins", "new",
     "Mount items (eggs, whistles) by zone. Empty: no mount item exists in the pack yet.", "mount."),
    ("merchant.pets", "Pet eggs", "stock", "table", "", "0", "1000000000", "text|int|int;both;Zones|Price|Stock", "coins", "new",
     "Pet eggs by zone - filled when pets ship.", "pet."),
]
for _r in SCALARS + TABLES:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, (_r[0], len(_r[1]), len(_r[10]))
_chk = {"merchant.role": "MerchCfg.checkRole", "rumour.text": "MerchCfg.checkRumour", "merchant.ringMin": "MerchCfg.checkRing",
        "merchant.ringMax": "MerchCfg.checkRing", "merchant.neverSell": "MerchCfg.checkNever"}
CFG_ROWS = [r[:11] + ("field:MerchCfg.%s" % r[11] + (";check=%s" % _chk[r[0]] if r[0] in _chk else ""),) for r in SCALARS]
CFG_ROWS += [r[:11] + ("reload@%s:%s;sep=/;check=MerchCfg.%s" % (CFG_FILE, r[11], "checkZone" if r[0] == "merchant.zones" else "checkStock")
                       + ("" if r[0] == "merchant.zones" else ";entry=item"),) for r in TABLES]
CFG_CATS = [("merch", "Merchants"), ("rumour", "Rumours"), ("zones", "Zones"), ("stock", "Stock")]
CFG_NOTE = "Chat: /merchantadmin list | move | spawn | remove <zone> (admins), /merchants (players)."
_d = ["# SkyyMerchants %s - roaming merchants. Also in game: SkyWynn Menu > Server Setup > Merchants (admins). Times in seconds." % VERSION,
      "# Hand edits: Server Setup > Merchants > Reload (or restart).", ""]
for _r in SCALARS:
    _d.append("# %s - %s" % (_r[1], _r[10]))
    _d.append("%s=%s" % (_r[0], _r[4]))
_d += ["", "# Zones: zone.<id>=World/Area/Levels - one merchant per line. Area = environment id prefixes (comma separated, ! = except,",
       "# * = any), Levels = the SkyyMobs level band a spot must have (0 = any). Rumours call zone<N> 'Zone N'."]
for _z in ZONES:
    _d.append("zone.%s=%s/%s/%s" % _z)
_d += ["", "# Special weapons: weapon.<item id>=Zones/Price/Stock (Zones = 1,2 / zone ids / *; Stock = per visit). Ids the server does",
       "# not know (a pack mod that is not installed) are skipped."]
for _w in WEAPONS:
    _d.append("weapon.%s=%s/%d/%d" % _w[:4])
_d += ["", "# Mounts: mount.<item id>=Zones/Price/Stock - no mount item exists in vanilla or the enabled pack mods yet."]
for _w in MOUNTS:
    _d.append("mount.%s=%s/%d/%d" % _w[:4])
_d += ["", "# Pet eggs: pet.<item id>=Zones/Price/Stock - filled when pets ship."]
for _w in PETS:
    _d.append("pet.%s=%s/%d/%d" % _w[:4])
_d.append("")
DEFAULT_TEXT = "\n".join(_d)
_dp = CFG.parse_props(DEFAULT_TEXT)
for _r in SCALARS:
    assert _dp.get(_r[0]) == _r[4], _r[0]

for r in SCALARS:
    jt, fld, dv = r[12], r[11], r[4]
    if jt == "boolean":
        F(cfgc, "public static volatile boolean %s = %s;" % (fld, dv))
    elif jt == "int":
        F(cfgc, "public static volatile int %s = %d;" % (fld, int(dv)))
    else:
        F(cfgc, "public static volatile String %s = %s;" % (fld, jstr(dv)))
F(cfgc, "public static volatile @PKG@.MerchZone[] ZONES = new @PKG@.MerchZone[0];")
F(cfgc, "public static volatile @PKG@.MerchItem[] ITEMS = new @PKG@.MerchItem[0];")
F(cfgc, "public static java.nio.file.Path FILE;")
F(cfgc, "public static volatile long LOADS = 0L;")
F(cfgc, "public static final String DEFAULT_TEXT = %s;" % jstr(DEFAULT_TEXT))
F(cfgc, "public static final String DEFAULT_ROLE = %s;" % jstr(ROLE))
F(cfgc, "public static final String[] CATS = new String[] { \"weapon.\", \"mount.\", \"pet.\" };")
# every name / role a merchant was given this run (the orphan rule: our role + one of our names = ours)
F(cfgc, "public static final java.util.Set NAMES = java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap());")
F(cfgc, "public static final java.util.Set ROLES = java.util.Collections.newSetFromMap(new java.util.concurrent.ConcurrentHashMap());")

# MerchWall: what is never sold (fields of MerchCfg exist now)
wall = cls("MerchWall")
M(wall, r"""
public static boolean listed(String id, String list) {
  if (id == null || list == null) return false;
  String[] a = list.split(",");
  for (int i = 0; i < a.length; i++) {
    String p = a[i].trim();
    if (p.length() == 0) continue;
    if (p.endsWith("*")) { if (p.length() > 1 && id.startsWith(p.substring(0, p.length() - 1))) return true; }
    else if (id.equals(p)) return true;
  }
  return false;
}""")
# SkyyGear's rarity of a plain id (gear:fn:rarity, Object[]{ id } -> "normal" ... "mythic" / "set" / "untiered" or null)
M(wall, r"""
public static String gearRarity(String id) {
  java.util.function.Function f = @PKG@.MerchLog.fn("gear:fn:rarity");
  if (f == null) return null;
  try { Object r = f.apply(new Object[] { id }); return r instanceof String ? ((String) r).trim().toLowerCase() : null; } catch (Throwable t) { return null; }
}""")
# null = may be sold, else why not
M(wall, r"""
public static String why(String id) {
  if (id == null || id.length() == 0) return "no item";
  if (id.startsWith("Skyy_Sack_")) return "Magic Bags are never sold";
  if (listed(id, @PKG@.MerchCfg.NEVER)) return "it is on the never-sell list";
  String r = gearRarity(id);
  if (r != null && (r.equals("mythic") || r.equals("untiered") || r.equals("set"))) return "Mythic, Untiered and Set gear is never sold";
  return null;
}""")

M(cfgc, r"""
public static boolean bv(java.util.Properties p, String k, boolean d) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null) return d;
  s = s.trim().toLowerCase();
  if (s.equals("true") || s.equals("on") || s.equals("yes") || s.equals("1")) return true;
  if (s.equals("false") || s.equals("off") || s.equals("no") || s.equals("0")) return false;
  return d;
}""")
M(cfgc, r"""
public static int iv(java.util.Properties p, String k, int d, int lo, int hi) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null) return d;
  try { int v = Integer.parseInt(s.trim()); return v < lo ? lo : (v > hi ? hi : v); } catch (Throwable t) { return d; }
}""")
M(cfgc, r"""
public static String sv(java.util.Properties p, String k, String d) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null || s.trim().length() == 0) return d;
  return s.trim();
}""")
_ap = ["public static void applyScalars(java.util.Properties p) {"]
for r in SCALARS:
    k, jt, fld, dv = r[0], r[12], r[11], r[4]
    if jt == "boolean":
        _ap.append('  %s = bv(p, %s, %s);' % (fld, jstr(k), dv))
    elif jt == "int":
        _ap.append('  %s = iv(p, %s, %d, %d, %d);' % (fld, jstr(k), int(dv), int(r[5]), int(r[6])))
    else:
        _ap.append('  %s = sv(p, %s, %s);' % (fld, jstr(k), jstr(dv)))
_ap.append("}")
M(cfgc, "\n".join(_ap))
M(cfgc, r"""
public static void applyTables(java.util.Properties p) {
  java.util.ArrayList zs = new java.util.ArrayList();
  java.util.ArrayList its = new java.util.ArrayList();
  if (p != null) {
    java.util.ArrayList keys = new java.util.ArrayList(p.stringPropertyNames());
    java.util.Collections.sort(keys);
    for (int i = 0; i < keys.size(); i++) {
      String k = (String) keys.get(i);
      String v = p.getProperty(k);
      if (k.startsWith("zone.")) {
        @PKG@.MerchZone z = @PKG@.MerchZone.parse(k.substring(5), v, "/");
        if (z == null) { @PKG@.MerchLog.warnOnce("zone:" + k + "=" + v, k + "=" + v + " is not 'World/Area/Levels' - that zone has no merchant until it is fixed"); continue; }
        zs.add(z);
        continue;
      }
      for (int c = 0; c < CATS.length; c++) {
        if (!k.startsWith(CATS[c])) continue;
        @PKG@.MerchItem it = @PKG@.MerchItem.parse(k.substring(CATS[c].length()), v, "/", c);
        if (it == null) { @PKG@.MerchLog.warnOnce("item:" + k + "=" + v, k + "=" + v + " is not 'Zones/Price/Stock' - skipped"); break; }
        String w = @PKG@.MerchWall.why(it.id);
        if (w != null) { @PKG@.MerchLog.warnOnce("wall:" + k, k + " is never sold (" + w + ") - skipped"); break; }
        its.add(it);
        break;
      }
    }
  }
  @PKG@.MerchZone[] za = new @PKG@.MerchZone[zs.size()];
  for (int i = 0; i < za.length; i++) za[i] = (@PKG@.MerchZone) zs.get(i);
  @PKG@.MerchItem[] ia = new @PKG@.MerchItem[its.size()];
  for (int i = 0; i < ia.length; i++) ia[i] = (@PKG@.MerchItem) its.get(i);
  ZONES = za;
  ITEMS = ia;
}""")
M(cfgc, r"""
public static java.util.Properties props(String text) {
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { }
  return p;
}""")
M(cfgc, r"""
public static java.util.Properties read(java.nio.file.Path f) {
  if (f == null) return null;
  java.io.InputStream in = null;
  try {
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
    in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    java.util.Properties p = new java.util.Properties();
    p.load(in);
    return p;
  } catch (Throwable t) {
    @PKG@.MerchLog.warn("could not read " + f + ": " + t + " - using the built-in defaults");
    return null;
  } finally {
    try { if (in != null) in.close(); } catch (Throwable t2) { }
  }
}""")
M(cfgc, r"""
public static void seed(java.nio.file.Path f) {
  if (f == null) return;
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return;
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
    java.nio.file.Files.write(tmp, DEFAULT_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    @PKG@.MerchLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.MerchLog.warn("could not write the default " + f + ": " + t); }
}""")
M(cfgc, r"""
public static void applyAll(java.util.Properties p) {
  java.util.Properties q = p != null ? p : props(DEFAULT_TEXT);
  applyScalars(q);
  applyTables(q);
  NAMES.add(NAME);
  ROLES.add(ROLE);
  ROLES.add(DEFAULT_ROLE);
  LOADS = LOADS + 1L;
}""")
# the kit's RELOAD routine (a table edit, a hand edit + Reload) and the start: the file, or the defaults when it cannot be read
M(cfgc, r"""
public static void reloadAll() {
  java.util.Properties p = read(FILE);
  applyAll(p);
}""")
M(cfgc, r"""
public static void load(java.nio.file.Path modsDir) {
  FILE = modsDir == null ? null : modsDir.resolve("Skyy_SkyyMerchants").resolve("config.properties");
  seed(FILE);
  reloadAll();
}""")
M(cfgc, r"""
public static @PKG@.MerchZone zone(String key) {
  @PKG@.MerchZone[] a = ZONES;
  for (int i = 0; i < a.length; i++) if (a[i].key.equals(key)) return a[i];
  return null;
}""")
M(cfgc, r"""
public static boolean worldHasZone(String wn) {
  @PKG@.MerchZone[] a = ZONES;
  for (int i = 0; wn != null && i < a.length; i++) if (a[i].world.equals(wn)) return true;
  return false;
}""")
M(cfgc, r"""
public static @PKG@.MerchItem item(int cat, String id) {
  @PKG@.MerchItem[] a = ITEMS;
  for (int i = 0; i < a.length; i++) if (a[i].cat == cat && a[i].id.equals(id)) return a[i];
  return null;
}""")
# ---- the kit's check= hooks (null = fine, text = refused)
M(cfgc, r"""
public static String checkRole(String key, String value) {
  if (value == null) return null;
  if (!@PKG@.MerchEng.roleOk(value.trim())) return "There is no NPC role called " + value.trim() + " on this server.";
  return null;
}""")
M(cfgc, r"""
public static String checkRumour(String key, String value) {
  if (value == null) return null;
  if (value.indexOf("{where}") < 0 && value.indexOf("{place}") < 0 && value.indexOf("{dir}") < 0) return "Put {where}, {place} or {dir} in the text so players get a hint.";
  return null;
}""")
M(cfgc, r"""
public static String checkRing(String key, String value) {
  if (value == null) return null;
  int v = 0;
  try { v = Integer.parseInt(value.trim()); } catch (Throwable t) { return null; }
  if (key.endsWith("ringMin") && v > RING_MAX) return "The minimum must not be above the maximum (" + RING_MAX + ").";
  if (key.endsWith("ringMax") && v < RING_MIN) return "The maximum must not be below the minimum (" + RING_MIN + ").";
  return null;
}""")
M(cfgc, r"""
public static String checkNever(String key, String value) {
  if (value == null) return null;
  String[] a = value.split(",");
  for (int i = 0; i < a.length; i++) { String s = a[i].trim(); if (s.equals("*")) return "A lone * would wall every item."; }
  return null;
}""")
# tables pass "tableKey[entry]" and the canonical columns joined by '|' (null = a removal: always fine)
M(cfgc, r"""
public static String entryOf(String key) {
  if (key == null) return "";
  int a = key.indexOf('['), b = key.lastIndexOf(']');
  return a >= 0 && b > a ? key.substring(a + 1, b) : key;
}""")
M(cfgc, r"""
public static String checkZone(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  if (@PKG@.MerchZone.parse(e, value, "|") == null) return "Use World | Area | Levels, e.g. default | Env_Zone1 | 1-20 (Area: env prefixes, ! = except, * = any; Levels lo-hi or 0).";
  if (value.indexOf('/') >= 0) return "No / in a zone line.";
  return null;
}""")
M(cfgc, r"""
public static String checkStock(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  String w = @PKG@.MerchWall.why(e);
  if (w != null) return e + " can never be sold here: " + w + ".";
  if (@PKG@.MerchItem.parse(e, value, "|", 0) == null) return "Use Zones | Price | Stock, e.g. 1,2 | 2500 | 1 (Zones: zone numbers, zone ids or *).";
  if (value.indexOf('/') >= 0) return "No / in a stock line.";
  return null;
}""")

# ---------------------------------------------------------------- the config kit (Server Setup > Merchants): MerchCfg's fields exist now
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Merchants", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS, FILES=[CFG_FILE], NOTE=CFG_NOTE,
               RELOAD="MerchCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": DEFAULT_TEXT})

# =====================================================================================================================
# MerchSite: one registry line (a zone's merchant in one world)
# =====================================================================================================================
site = cls("MerchSite")
for _f in ("String zone", "String uuid", "int x", "int y", "int z", "long placedAt", "long visit", "boolean held", "String stock",
           "String ghosts", "String env", "String rumour",
           # memory only
           "long missingSince", "long nextTry", "String req", "java.util.UUID reqBy", "long seen"):
    F(site, "public %s;" % _f)
C(site, 'public MerchSite() { this.zone = ""; this.uuid = ""; this.stock = ""; this.ghosts = ""; this.env = ""; this.rumour = ""; this.req = ""; }')
M(site, r"""
public String line() {
  return @PKG@.MerchLog.clean(this.zone) + "\t" + this.uuid + "\t" + this.x + "\t" + this.y + "\t" + this.z + "\t" + this.placedAt + "\t" + this.visit + "\t" + (this.held ? "1" : "0")
    + "\t" + @PKG@.MerchLog.clean(this.stock) + "\t" + @PKG@.MerchLog.clean(this.ghosts) + "\t" + @PKG@.MerchLog.clean(this.env) + "\t" + @PKG@.MerchLog.clean(this.rumour);
}""")
M(site, r"""
public static boolean uuidOk(String s) {
  if (s == null) return false;
  if (s.length() == 0) return true;
  try { java.util.UUID.fromString(s); return true; } catch (Throwable t) { return false; }
}""")
M(site, r"""
public static @PKG@.MerchSite parse(String line) {
  if (line == null) return null;
  String t = line.trim();
  if (t.length() == 0 || t.startsWith("#")) return null;
  String[] p = line.split("\t", -1);
  if (p.length < 12) return null;
  try {
    @PKG@.MerchSite s = new @PKG@.MerchSite();
    s.zone = p[0].trim(); s.uuid = p[1].trim();
    s.x = Integer.parseInt(p[2].trim()); s.y = Integer.parseInt(p[3].trim()); s.z = Integer.parseInt(p[4].trim());
    s.placedAt = Long.parseLong(p[5].trim()); s.visit = Long.parseLong(p[6].trim()); s.held = p[7].trim().equals("1");
    s.stock = p[8]; s.ghosts = p[9].trim(); s.env = p[10]; s.rumour = p[11];
    if (s.zone.length() == 0 || !uuidOk(s.uuid) || s.y < -64 || s.y > 400) return null;
    return s;
  } catch (Throwable e) { return null; }
}""")
# ghosts: "uuid@ms;uuid@ms" - old merchants not seen removed yet (forgotten after GHOST_DAYS)
M(site, r"""
public String[] ghostList() {
  if (this.ghosts == null || this.ghosts.length() == 0) return new String[0];
  java.util.ArrayList l = new java.util.ArrayList();
  String[] a = this.ghosts.split(";");
  for (int i = 0; i < a.length; i++) { int at = a[i].indexOf('@'); String u = at < 0 ? a[i] : a[i].substring(0, at); if (u.trim().length() > 0) l.add(u.trim()); }
  String[] r = new String[l.size()];
  for (int i = 0; i < r.length; i++) r[i] = (String) l.get(i);
  return r;
}""")
M(site, r"""
public boolean hasGhost(String u) {
  String[] g = ghostList();
  for (int i = 0; i < g.length; i++) if (g[i].equals(u)) return true;
  return false;
}""")
M(site, r"""
public void addGhost(String u, long now) {
  if (u == null || u.length() == 0 || hasGhost(u)) return;
  String[] a = this.ghosts == null || this.ghosts.length() == 0 ? new String[0] : this.ghosts.split(";");
  StringBuilder b = new StringBuilder();
  int start = a.length >= 16 ? a.length - 15 : 0;
  for (int i = start; i < a.length; i++) { if (a[i].length() == 0) continue; if (b.length() > 0) b.append(';'); b.append(a[i]); }
  if (b.length() > 0) b.append(';');
  b.append(u).append('@').append(now);
  this.ghosts = b.toString();
}""")
M(site, r"""
public boolean dropGhost(String u) {
  if (this.ghosts == null || this.ghosts.length() == 0) return false;
  String[] a = this.ghosts.split(";");
  StringBuilder b = new StringBuilder();
  boolean hit = false;
  for (int i = 0; i < a.length; i++) {
    int at = a[i].indexOf('@');
    String g = at < 0 ? a[i] : a[i].substring(0, at);
    if (g.equals(u)) { hit = true; continue; }
    if (a[i].length() == 0) continue;
    if (b.length() > 0) b.append(';');
    b.append(a[i]);
  }
  this.ghosts = b.toString();
  return hit;
}""")
M(site, r"""
public boolean expireGhosts(long now, long keepMs) {
  if (this.ghosts == null || this.ghosts.length() == 0) return false;
  String[] a = this.ghosts.split(";");
  StringBuilder b = new StringBuilder();
  boolean hit = false;
  for (int i = 0; i < a.length; i++) {
    int at = a[i].indexOf('@');
    long t = 0L;
    try { t = at < 0 ? 0L : Long.parseLong(a[i].substring(at + 1)); } catch (Throwable e) { t = 0L; }
    if (a[i].length() == 0) continue;
    if (now - t > keepMs) { hit = true; continue; }
    if (b.length() > 0) b.append(';');
    b.append(a[i]);
  }
  this.ghosts = b.toString();
  return hit;
}""")

# =====================================================================================================================
# MerchReg: per world, the lines (loaded on first use from merchants/<wf>.tsv), atomic writes; an unreadable file is never overwritten
# =====================================================================================================================
reg = cls("MerchReg")
F(reg, "public static java.nio.file.Path DIR;")
F(reg, "public static final java.util.concurrent.ConcurrentHashMap W = new java.util.concurrent.ConcurrentHashMap();")
F(reg, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")
F(reg, "public static final java.util.concurrent.atomic.AtomicLong SAVE_FAILS = new java.util.concurrent.atomic.AtomicLong();")
F(reg, "public static volatile boolean STOPPING = false;")
# world file -> no registry file there (cached so the NPC add hook never stats the disk per mob; cleared when save() writes the file)
F(reg, "public static final java.util.concurrent.ConcurrentHashMap NOFILE = new java.util.concurrent.ConcurrentHashMap();")
M(reg, r"""
public static String wf(String wn) {
  if (wn == null) return "_";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < wn.length() && b.length() < 120; i++) {
    char c = wn.charAt(i);
    b.append((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-' || c == '_' || c == '.' ? c : '_');
  }
  return b.length() == 0 ? "_" : b.toString();
}""")
M(reg, "public static java.nio.file.Path file(String wf) { return DIR == null ? null : DIR.resolve(wf + \".tsv\"); }")
M(reg, "public static synchronized void add(java.util.ArrayList l, @PKG@.MerchSite s) { if (l != null && s != null) l.add(s); }")
M(reg, "public static synchronized boolean remove(java.util.ArrayList l, @PKG@.MerchSite s) { return l != null && l.remove(s); }")
M(reg, "public static synchronized Object[] snap(java.util.ArrayList l) { if (l == null) return new Object[0]; return l.toArray(); }")
M(reg, r"""
public static java.util.ArrayList sites(String wn) {
  String wf = wf(wn);
  Object o = W.get(wf);
  if (o instanceof java.util.ArrayList) return (java.util.ArrayList) o;
  java.util.ArrayList l = new java.util.ArrayList();
  java.nio.file.Path f = file(wf);
  int bad = 0;
  try {
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
      for (int i = 0; i < ls.size(); i++) {
        String ln = (String) ls.get(i);
        if (ln.trim().length() == 0 || ln.startsWith("#")) continue;
        @PKG@.MerchSite s = @PKG@.MerchSite.parse(ln);
        if (s == null) bad++; else l.add(s);
      }
    }
  } catch (Throwable t) {
    @PKG@.MerchLog.warnOnce("read|" + wf + "|" + (System.currentTimeMillis() / 60000L), "could not read " + f + " (" + t + ") - the merchants of world " + wn + " pause until it reads; the file is never overwritten");
    return null;
  }
  if (bad > 0) {
    java.nio.file.Path bk = DIR.resolve(wf + "-" + System.currentTimeMillis() + ".tsv.bad");
    try { java.nio.file.Files.copy(f, bk, new java.nio.file.CopyOption[0]); }
    catch (Throwable t) {
      @PKG@.MerchLog.warnOnce("bak|" + wf + "|" + (System.currentTimeMillis() / 60000L), "could not back up " + f + " (" + t + ") - the merchants of world " + wn + " pause until it can");
      return null;
    }
    @PKG@.MerchLog.warn("skipped " + bad + " unreadable line(s) in " + f + " - the whole file was copied to " + bk.getFileName() + " first");
  }
  Object prev = W.putIfAbsent(wf, l);
  NAMES.put(wf, wn);
  return prev instanceof java.util.ArrayList ? (java.util.ArrayList) prev : l;
}""")
M(reg, r"""
public static void moveRetry(java.nio.file.Path tmp, java.nio.file.Path f) throws java.lang.Exception {
  for (int i = 0; ; i++) {
    try {
      try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      catch (java.nio.file.AtomicMoveNotSupportedException a) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      return;
    } catch (java.nio.file.FileSystemException e) {
      if (i >= 4) throw e;
      try { Thread.sleep(20L); } catch (Throwable t) { }
    }
  }
}""")
M(reg, r"""
public static boolean save(String wn) {
  String wf = wf(wn);
  java.util.ArrayList l = (java.util.ArrayList) W.get(wf);
  if (l == null || DIR == null) return false;
  StringBuilder sb = new StringBuilder("# SkyyMerchants roaming merchants - world " + @PKG@.MerchLog.clean(wn) + ": zone uuid x y z placedAt visit held stock ghosts env rumour\n");
  Object[] arr = snap(l);
  for (int i = 0; i < arr.length; i++) sb.append(((@PKG@.MerchSite) arr[i]).line()).append('\n');
  try {
    java.nio.file.Path f = file(wf);
    if (arr.length == 0 && !java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;   // nothing to keep: no empty file
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(wf + ".tsv.tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[0]);
    moveRetry(tmp, f);
    NOFILE.remove(wf);
    return true;
  } catch (Throwable t) {
    SAVE_FAILS.incrementAndGet();
    @PKG@.MerchLog.warnOnce("save|" + wf + "|" + (System.currentTimeMillis() / 60000L), "could not save the merchants of world " + wn + ": " + t + " - nothing moves until it saves");
    return false;
  }
}""")
M(reg, r"""
public static @PKG@.MerchSite find(java.util.ArrayList l, String zone) {
  Object[] arr = snap(l);
  for (int i = 0; i < arr.length; i++) if (((@PKG@.MerchSite) arr[i]).zone.equals(zone)) return (@PKG@.MerchSite) arr[i];
  return null;
}""")
M(reg, r"""
public static boolean known(String wn) {
  String wf = wf(wn);
  if (W.containsKey(wf)) return true;
  if (NOFILE.containsKey(wf)) return false;
  java.nio.file.Path f = file(wf);
  boolean e = false;
  try { e = f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]); } catch (Throwable t) { e = false; }
  if (!e && f != null) NOFILE.put(wf, Boolean.TRUE);
  return e;
}""")
M(reg, r"""
public static void flushAll() {
  java.util.Iterator it = NAMES.values().iterator();
  while (it.hasNext()) { try { save((String) it.next()); } catch (Throwable t) { } }
}""")

# =====================================================================================================================
# MerchCoins: the SkyyCoins bridge (the SkyyBazaar 0.1.5 wrappers: never throw out of a half-done trade)
# =====================================================================================================================
coins = cls("MerchCoins")
M(coins, r"""
public static boolean ready() {
  return @PKG@.MerchLog.fn("coins:fn:get") != null && @PKG@.MerchLog.fn("coins:fn:add") != null && @PKG@.MerchLog.fn("coins:fn:take") != null;
}""")
# balance, or -1 = the bridge threw / answered garbage / missing
M(coins, r"""
public static long get(java.util.UUID u) {
  java.util.function.Function f = @PKG@.MerchLog.fn("coins:fn:get");
  if (f == null || u == null) return -1L;
  Object r = null;
  try { r = f.apply(u); } catch (Throwable t) { @PKG@.MerchLog.warn("coins:fn:get threw for " + u + ": " + t); return -1L; }
  return r instanceof Number ? ((Number) r).longValue() : -1L;
}""")
# 1 = taken, 0 = refused / missing, -1 = threw (outcome unknown)
M(coins, r"""
public static int take(java.util.UUID u, long n) {
  if (n <= 0L) return 1;
  java.util.function.Function f = @PKG@.MerchLog.fn("coins:fn:take");
  if (f == null) return 0;
  Object r = null;
  try { r = f.apply(new Object[] { u, Long.valueOf(n) }); } catch (Throwable t) { @PKG@.MerchLog.warn("coins:fn:take threw for " + u + " (" + n + " coins): " + t); return -1; }
  return (r instanceof Boolean && ((Boolean) r).booleanValue()) ? 1 : 0;
}""")
M(coins, r"""
public static int add(java.util.UUID u, long n) {
  if (n <= 0L) return 1;
  java.util.function.Function f = @PKG@.MerchLog.fn("coins:fn:add");
  if (f == null) return 0;
  Object r = null;
  try { r = f.apply(new Object[] { u, Long.valueOf(n) }); } catch (Throwable t) { @PKG@.MerchLog.warn("coins:fn:add threw for " + u + " (" + n + " coins): " + t); return -1; }
  return r instanceof Number ? 1 : 0;
}""")
M(coins, r"""
public static boolean busy(java.util.UUID u) {
  if (u == null) return false;
  try { return @PKG@.MerchLog.bridge().get("profile:busy:" + u) != null; } catch (Throwable t) { return false; }
}""")

# =====================================================================================================================
# MerchSpot: a valid surface spot of a zone near a random player (loaded chunks only)
# =====================================================================================================================
spot = cls("MerchSpot")
F(spot, "public static final java.util.Random RNG = new java.security.SecureRandom();")
F(spot, 'public static final String[] BUILT = new String[] { "_Half", "_Stairs", "_Roof", "_Wall", "_Beam", "_Brick", "_Cobble", "_Pillar", "_Smooth", "_Decorative", "_Ornate", "_Corner", "_Fence", "_Stalactite", "_Path", "_Quarter", "_Tilled" };')
F(spot, "public static volatile String LAST_ENV = null;")
F(spot, "public static volatile String LAST_WHY = \"\";")
M(spot, r"""
public static boolean ground(String id) {
  if (id == null || id.startsWith("Soil_Dirt_Tilled") || id.startsWith("Soil_Pathway")) return false;
  for (int i = 0; i < BUILT.length; i++) if (id.indexOf(BUILT[i]) >= 0) return false;
  String[] ps = @PKG@.MerchCfg.GROUND == null ? new String[0] : @PKG@.MerchCfg.GROUND.split(",");
  for (int i = 0; i < ps.length; i++) { String p = ps[i].trim(); if (p.length() > 0 && id.startsWith(p)) return true; }
  return false;
}""")
M(spot, r"""
public static boolean soft(String id) {
  if (id == null) return false;
  if (id.equals("Empty")) return true;
  if (id.startsWith("Plant_Grass_") || id.startsWith("Plant_Petals_") || id.startsWith("Plant_Moss_Short_") || id.startsWith("Plant_Moss_Rug_")) return true;
  return id.equals("Plant_Fern") || id.equals("Plant_Fern_Arid") || id.equals("Plant_Fern_Forest") || id.equals("Plant_Fern_Wet") || id.equals("Plant_Fern_Winter");
}""")
M(spot, r"""
public static boolean nearPlayer(double[] ps, double x, double z, double gap) {
  if (ps == null || gap <= 0.0) return false;
  for (int i = 0; i + 1 < ps.length; i += 2) {
    double dx = ps[i] - x, dz = ps[i + 1] - z;
    if (dx * dx + dz * dz < gap * gap) return true;
  }
  return false;
}""")
# SkyyMobs' level at the spot (mob:fn:levelAt -> Object[]{ Integer lo, Integer hi, ... }); -1 = no answer (no SkyyMobs / no level there)
M(spot, r"""
public static int levelAt(String wn, int x, int y, int z) {
  java.util.function.Function f = @PKG@.MerchLog.fn("mob:fn:levelAt");
  if (f == null) return -1;
  try {
    Object r = f.apply(new Object[] { wn, Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) });
    if (r instanceof Object[] && ((Object[]) r).length >= 1 && ((Object[]) r)[0] instanceof Integer) return ((Integer) ((Object[]) r)[0]).intValue();
  } catch (Throwable t) { }
  return -1;
}""")
# one column: the y the merchant stands at, or -1 (LAST_WHY says why - the admin list and the harness read it)
M(spot, r"""
public static int column(String wn, @PKG@.MerchZone z, int x, int cz, double[] ps) {
  if (nearPlayer(ps, (double) x + 0.5, (double) cz + 0.5, (double) @PKG@.MerchCfg.GAP)) { LAST_WHY = "near a player"; return -1; }
  int h = @PKG@.MerchEng.height(wn, x, cz);
  if (h < 1 || h > 316) { LAST_WHY = h < 0 ? "not loaded" : "no ground"; return -1; }
  if (!ground(@PKG@.MerchEng.block(wn, x, h, cz))) { LAST_WHY = "not natural ground"; return -1; }
  if (!soft(@PKG@.MerchEng.block(wn, x, h + 1, cz)) || !soft(@PKG@.MerchEng.block(wn, x, h + 2, cz))) { LAST_WHY = "no room above"; return -1; }
  if (@PKG@.MerchEng.fluid(wn, x, h + 1, cz) || @PKG@.MerchEng.fluid(wn, x, h + 2, cz)) { LAST_WHY = "water"; return -1; }
  String env = @PKG@.MerchEng.env(wn, x, h + 1, cz);
  if (!z.envOk(env)) { LAST_WHY = "outside the zone (" + env + ")"; return -1; }
  int L = levelAt(wn, x, h + 1, cz);
  if (L > 0 && !z.levelOk(L)) { LAST_WHY = "level " + L + " is outside " + z.band(); return -1; }
  LAST_ENV = env;
  LAST_WHY = "";
  return h + 1;
}""")
# up to `tries` random columns in the ring around random players of the world; int[]{ x, y, z } or null
M(spot, r"""
public static int[] find(String wn, @PKG@.MerchZone z, int tries) {
  double[] ps = @PKG@.MerchEng.players(wn);
  if (ps == null || ps.length < 2) { LAST_WHY = "no player in the world"; return null; }
  double rmin = (double) @PKG@.MerchCfg.RING_MIN, rmax = (double) @PKG@.MerchCfg.RING_MAX;
  if (rmax < rmin) rmax = rmin;
  for (int k = 0; k < tries; k++) {
    int pi = RNG.nextInt(ps.length / 2);
    double a = RNG.nextDouble() * Math.PI * 2.0;
    double d = rmin + RNG.nextDouble() * (rmax - rmin);
    int x = (int) Math.floor(ps[2 * pi] + Math.cos(a) * d);
    int cz = (int) Math.floor(ps[2 * pi + 1] + Math.sin(a) * d);
    int y = column(wn, z, x, cz, ps);
    if (y >= 0) return new int[] { x, y, cz };
  }
  return null;
}""")

# =====================================================================================================================
# MerchRumour: the vague hint (no coordinates)
# =====================================================================================================================
rum = cls("MerchRumour")
_pw = sorted(PLACE_WORDS.items())
F(rum, "public static final String[] PK = %s;" % jarr([k for k, _ in _pw]))
F(rum, "public static final String[] PW = %s;" % jarr([v for _, v in _pw]))
F(rum, 'public static final String[] DIRS = new String[] { "north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west" };')
# north = -Z, east = +X (the 8-way compass sector of the offset from spawn)
M(rum, r"""
public static String dir(double dx, double dz) {
  double a = Math.toDegrees(Math.atan2(dx, -dz));
  if (a < 0.0) a = a + 360.0;
  int i = (int) Math.floor((a + 22.5) / 45.0) % 8;
  return DIRS[i];
}""")
M(rum, r"""
public static String dist(double d) {
  if (d < 150.0) return "close to";
  if (d < 500.0) return "a short walk";
  if (d < 1200.0) return "a fair way";
  if (d < 2500.0) return "far to the";
  return "very far to the";
}""")
M(rum, r"""
public static String where(double dx, double dz) {
  double d = Math.sqrt(dx * dx + dz * dz);
  if (d < 150.0) return "close to spawn";
  return dist(d) + " " + dir(dx, dz) + " of spawn";
}""")
# Env_Zone1_Plains -> plains; Env_Zone1 -> wilds; unknown -> wilds
M(rum, r"""
public static String place(String env) {
  if (env == null || !env.startsWith("Env_")) return "wilds";
  String s = env.substring(4);
  int u = s.indexOf('_');
  if (s.startsWith("Zone")) { if (u < 0) return "wilds"; s = s.substring(u + 1); }
  for (int i = 0; i < PK.length; i++) if (s.equals(PK[i]) || s.startsWith(PK[i] + "_")) return PW[i];
  String t = s.replace('_', ' ').trim().toLowerCase();
  return t.length() == 0 ? "wilds" : t;
}""")
M(rum, r"""
public static String text(String tpl, @PKG@.MerchZone z, String env, double dx, double dz, String name) {
  double d = Math.sqrt(dx * dx + dz * dz);
  String s = tpl == null ? "" : tpl;
  s = s.replace("{place}", place(env));
  s = s.replace("{where}", where(dx, dz));
  s = s.replace("{dir}", d < 150.0 ? "near" : dir(dx, dz));
  s = s.replace("{dist}", dist(d));
  s = s.replace("{zone}", z == null ? "" : z.name);
  s = s.replace("{region}", z == null || z.region.length() == 0 ? (z == null ? "" : z.name) : z.region);
  s = s.replace("{name}", name == null ? "" : name);
  return s;
}""")
M(rum, r"""
public static String forSite(String wn, @PKG@.MerchZone z, @PKG@.MerchSite s) {
  double[] sp = @PKG@.MerchEng.spawnPoint(wn);
  if (sp == null || sp.length < 2) sp = new double[] { 0.0, 0.0 };
  return text(@PKG@.MerchCfg.RUMOUR, z, s.env, (double) s.x + 0.5 - sp[0], (double) s.z + 0.5 - sp[1], @PKG@.MerchCfg.NAME);
}""")

# =====================================================================================================================
# MerchShop: restock, the offers, names, the buy flow
# =====================================================================================================================
shop = cls("MerchShop")
F(shop, "public static final java.util.Random RNG = new java.security.SecureRandom();")
F(shop, "public static java.nio.file.Path LOGF;")
F(shop, "public static final java.util.concurrent.atomic.AtomicLong SALES = new java.util.concurrent.atomic.AtomicLong();")
F(shop, "public static final java.util.concurrent.atomic.AtomicLong COINS = new java.util.concurrent.atomic.AtomicLong();")
F(shop, "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();")
_nm = sorted(NAMES.items())
F(shop, "public static final String[] NK = %s;" % jarr([k for k, _ in _nm]))
F(shop, "public static final String[] NV = %s;" % jarr([v for _, v in _nm]))
F(shop, 'public static final String[] CAT_NAME = new String[] { "Weapons", "Mounts", "Pet eggs" };')
# a readable name: the build-time names of the default ids, else the server's en-US text, else the id in words
M(shop, r"""
public static String label(String id) {
  if (id == null) return "";
  String s = id;
  if (s.startsWith("Weapon_")) s = s.substring(7);
  s = s.replace('_', ' ').trim();
  return s.length() == 0 ? id : s;
}""")
M(shop, r"""
public static String name(String id) {
  if (id == null) return "";
  Object c = NAMES.get(id);
  if (c instanceof String) return (String) c;
  String n = null;
  for (int i = 0; i < NK.length; i++) if (NK[i].equals(id)) { n = NV[i]; break; }
  if (n == null) n = @PKG@.MerchEng.tr(id);
  if (n == null) n = label(id);
  if (NAMES.size() < 5000) NAMES.put(id, n);
  return n;
}""")
# the stock of one visit: "cat:id:price:left" comma separated (prices frozen for the visit)
M(shop, r"""
public static String restock(@PKG@.MerchZone z) {
  @PKG@.MerchItem[] all = @PKG@.MerchCfg.ITEMS;
  java.util.ArrayList w = new java.util.ArrayList();
  java.util.ArrayList rest = new java.util.ArrayList();
  for (int i = 0; i < all.length; i++) {
    @PKG@.MerchItem it = all[i];
    if (it.stock <= 0 || !it.inZone(z) || !@PKG@.MerchEng.itemOk(it.id) || @PKG@.MerchWall.why(it.id) != null) continue;
    if (it.cat == 0) w.add(it); else rest.add(it);
  }
  java.util.Collections.shuffle(w, RNG);
  int n = Math.min(w.size(), Math.max(1, @PKG@.MerchCfg.OFFERS));
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < n; i++) {
    @PKG@.MerchItem it = (@PKG@.MerchItem) w.get(i);
    if (b.length() > 0) b.append(',');
    b.append(it.cat).append(':').append(it.id).append(':').append(it.price).append(':').append(it.stock);
  }
  for (int i = 0; i < rest.size(); i++) {
    @PKG@.MerchItem it = (@PKG@.MerchItem) rest.get(i);
    if (b.length() > 0) b.append(',');
    b.append(it.cat).append(':').append(it.id).append(':').append(it.price).append(':').append(it.stock);
  }
  return b.toString();
}""")
# the offers of a category: String[][]{ ids, prices, lefts } (as text)
M(shop, r"""
public static String[][] offers(@PKG@.MerchSite s, int cat) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList ps = new java.util.ArrayList();
  java.util.ArrayList ls = new java.util.ArrayList();
  String st = s == null ? "" : s.stock;
  if (st != null && st.length() > 0) {
    String[] a = st.split(",");
    for (int i = 0; i < a.length; i++) {
      String[] p = a[i].split(":");
      if (p.length != 4) continue;
      if (!p[0].equals(String.valueOf(cat))) continue;
      if (!@PKG@.MerchEng.itemOk(p[1]) || @PKG@.MerchWall.why(p[1]) != null) continue;   // hidden (the saved line stays): unknown / walled since the restock
      ids.add(p[1]); ps.add(p[2]); ls.add(p[3]);
    }
  }
  String[][] r = new String[3][ids.size()];
  for (int i = 0; i < ids.size(); i++) { r[0][i] = (String) ids.get(i); r[1][i] = (String) ps.get(i); r[2][i] = (String) ls.get(i); }
  return r;
}""")
# change the left count of one offer by `by` (synchronized: one site, one change at a time); answers the new count or -1 (none / not enough)
M(shop, r"""
public static synchronized int adjust(@PKG@.MerchSite s, int cat, String id, int by) {
  if (s == null || s.stock == null) return -1;
  String[] a = s.stock.split(",");
  StringBuilder b = new StringBuilder();
  int res = -1;
  for (int i = 0; i < a.length; i++) {
    String[] p = a[i].split(":");
    String e = a[i];
    if (res < 0 && p.length == 4 && p[0].equals(String.valueOf(cat)) && p[1].equals(id)) {
      int left = 0;
      try { left = Integer.parseInt(p[3]); } catch (Throwable t) { left = 0; }
      if (left + by >= 0) { left = left + by; res = left; e = p[0] + ":" + p[1] + ":" + p[2] + ":" + left; }
    }
    if (b.length() > 0) b.append(',');
    b.append(e);
  }
  if (res >= 0) s.stock = b.toString();
  return res;
}""")
M(shop, r"""
public static void sale(String line) {
  try {
    if (LOGF == null) return;
    java.nio.file.Files.createDirectories(LOGF.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    String t = java.time.LocalDateTime.now().withNano(0).toString() + "\t" + @PKG@.MerchLog.clean(line) + "\n";
    java.nio.file.Files.write(LOGF, t.getBytes(java.nio.charset.StandardCharsets.UTF_8), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable e) { @PKG@.MerchLog.warnOnce("salelog", "could not write sales.log: " + e); }
}""")
M(shop, r"""
public static int countIn(@IC@ c, String id) {
  if (c == null) return 0;
  int n = 0;
  short cap = c.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = c.getItemStack(s);
    if (it != null && !it.isEmpty() && id.equals(it.getItemId())) n += it.getQuantity();
  }
  return n;
}""")
M(shop, r"""
public static int count(Object player, String id) {
  @IC@[] cs = @PKG@.MerchEng.conts(player);
  int n = 0;
  for (int i = 0; i < cs.length; i++) n += countIn(cs[i], id);
  return n;
}""")
# free room for ONE of id: an empty slot, or a partial stack of the same item below its max (max unknown / 1 = only an empty slot)
M(shop, r"""
public static boolean room(Object player, String id) {
  @IC@[] cs = @PKG@.MerchEng.conts(player);
  int max = @PKG@.MerchEng.maxStack(id);
  for (int c = 0; c < cs.length; c++) {
    @IC@ cont = cs[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ st = cont.getItemStack(s);
      if (st == null || st.isEmpty()) return true;
      if (max > 1 && id.equals(st.getItemId()) && st.getQuantity() < max) return true;
    }
  }
  return false;
}""")
# one item into the containers storage first; every add measured by re-counting the container (never trusting the transaction)
M(shop, r"""
public static int give(Object player, String id) {
  @IC@[] cs = @PKG@.MerchEng.conts(player);
  for (int c = 0; c < cs.length; c++) {
    @IC@ cont = cs[c];
    if (cont == null) continue;
    int before = countIn(cont, id);
    try { cont.addItemStack(new @IS@(id, 1)); } catch (Throwable t) { @PKG@.MerchLog.warn("addItemStack " + id + " failed: " + t); continue; }
    int got = countIn(cont, id) - before;
    if (got > 0) return got;
  }
  return 0;
}""")
# the purchase (the player's world thread). Answers the page / chat line: "+..." bought, "-..." refused, "=..." nothing changed
M(shop, r"""
public static String buy(java.util.UUID u, String who, Object player, double[] pos, String wn, String zone, String npc, int cat, String id) {
  if (!@PKG@.MerchCfg.ON) return "-The merchants are away (switched off on this server).";
  java.util.ArrayList sites = @PKG@.MerchReg.sites(wn);
  @PKG@.MerchSite s = sites == null ? null : @PKG@.MerchReg.find(sites, zone);
  if (s == null || s.uuid.length() == 0 || !s.uuid.equals(npc)) return "-The merchant has moved on - listen for the next rumour.";
  if (pos == null || pos.length < 3) return "-Walk back to the merchant to buy (within " + @PKG@.MerchCfg.USE_RANGE + " blocks).";
  double dx = pos[0] - ((double) s.x + 0.5), dz = pos[2] - ((double) s.z + 0.5), dy = pos[1] - (double) s.y;
  double r = (double) @PKG@.MerchCfg.USE_RANGE;
  if (dx * dx + dz * dz > r * r || dy > r + 3.0 || dy < -(r + 3.0)) return "-Walk back to the merchant to buy (within " + @PKG@.MerchCfg.USE_RANGE + " blocks).";
  String w = @PKG@.MerchWall.why(id);
  if (w != null) return "-" + name(id) + " cannot be sold: " + w + ".";
  if (!@PKG@.MerchEng.itemOk(id)) return "-This server does not know that item any more.";
  String[][] of = offers(s, cat);
  long price = -1L;
  int left = 0;
  for (int i = 0; i < of[0].length; i++) {
    if (!of[0][i].equals(id)) continue;
    try { price = Long.parseLong(of[1][i]); left = Integer.parseInt(of[2][i]); } catch (Throwable t) { price = -1L; }
    break;
  }
  if (price < 0L) return "-The merchant does not sell that this visit.";
  if (left <= 0) return "-Sold out - the merchant restocks when it moves.";
  if (@PKG@.MerchCoins.busy(u)) return "-Your profile is still loading - try again in a moment.";
  if (!@PKG@.MerchCoins.ready()) return "-The coin bank (SkyyCoins) is not running - nothing was bought.";
  long purse = @PKG@.MerchCoins.get(u);
  if (purse < 0L) return "-The coin bank did not answer - nothing was bought, try again.";
  if (purse < price) return "-You need " + @PKG@.MerchLog.grp(price) + " coins - you have " + @PKG@.MerchLog.grp(purse) + ".";
  if (!room(player, id)) return "-Your inventory is full - make room first. Nothing was taken.";
  if (adjust(s, cat, id, -1) < 0) return "-Sold out - the merchant restocks when it moves.";
  int before = count(player, id);
  int tk = @PKG@.MerchCoins.take(u, price);
  if (tk != 1) {
    adjust(s, cat, id, 1);
    if (tk < 0) {
      sale("TAKE-ERROR " + who + " " + u + " " + id + " " + price);
      return "-The coin bank failed while taking " + @PKG@.MerchLog.grp(price) + " coins - nothing was given. If your purse went down tell an admin (it is logged).";
    }
    return "-Not enough coins - nothing was bought.";
  }
  int got = 0;
  try { got = give(player, id); } catch (Throwable t) { @PKG@.MerchLog.warn("giving " + id + " to " + who + " failed: " + t); got = 0; }
  int real = count(player, id) - before;
  if (real < got) real = got;
  if (real <= 0) {
    adjust(s, cat, id, 1);
    int ad = @PKG@.MerchCoins.add(u, price);
    if (ad != 1) {
      sale("REFUND-FAILED " + who + " " + u + " " + id + " owed " + price);
      @PKG@.MerchLog.warn("REFUND FAILED: " + who + " " + u + " is owed " + price + " coins (" + id + ")");
      return "-The item could not be given and the refund of " + @PKG@.MerchLog.grp(price) + " coins FAILED - tell an admin (it is logged).";
    }
    sale("REFUND " + who + " " + u + " " + id + " " + price);
    return "-The item could not be given - your " + @PKG@.MerchLog.grp(price) + " coins were refunded.";
  }
  if (!@PKG@.MerchReg.save(wn)) {
    sale("SAVE-FAILED " + who + " " + u + " " + wn + " " + zone + " " + id + " (stock not saved: a restart may restock this offer)");
    @PKG@.MerchLog.warn("the sale of " + id + " to " + who + " was not saved to disk - a restart may restock this offer");
  }
  SALES.incrementAndGet();
  COINS.addAndGet(price);
  sale("BUY " + who + " " + u + " " + wn + " " + zone + " " + id + " " + price);
  @PKG@.MerchLog.info(who + " bought " + id + " for " + price + " coins from the " + zone + " merchant");
  return "+Bought " + name(id) + " for " + @PKG@.MerchLog.grp(price) + " coins.";
}""")

# =====================================================================================================================
# MerchCore: the per-world second (world thread), admin requests, the add hook verdict, lookups
# =====================================================================================================================
core = cls("MerchCore")
F(core, "public static final java.util.concurrent.ConcurrentHashMap KNOWN = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> "world\tzone"
F(core, "public static final java.util.concurrent.ConcurrentHashMap GHOSTS = new java.util.concurrent.ConcurrentHashMap();")  # uuid -> world
F(core, "public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();")
F(core, "public static final java.util.concurrent.ConcurrentHashMap REQ = new java.util.concurrent.ConcurrentHashMap();")    # zone -> "kind\tuuid"
F(core, "public static final long GRACE_MS = %dL;" % GRACE_MS)
F(core, "public static final long RETRY_MS = %dL;" % RETRY_MS)
F(core, "public static final int SPOT_TRIES = %d;" % SPOT_TRIES)
F(core, "public static final long GHOST_MS = %dL;" % (GHOST_DAYS * 86400000))
# 0 spawned, 1 moved, 2 respawned at its spot, 3 removed (ghost cleared), 4 orphans removed by the add hook, 5 rumours, 6 no spot,
# 7 spawn refused, 8 save refused (new one removed again), 9 page opens, 10 retired (part off / zone gone)
F(core, "public static final long[] N = new long[11];")
M(core, "public static synchronized void count(int i) { if (i >= 0 && i < N.length) N[i] = N[i] + 1L; }")
M(core, r"""
public static void reindex(String wn, java.util.ArrayList sites) {
  java.util.Iterator it = KNOWN.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); if (String.valueOf(e.getValue()).startsWith(wn + "\t")) it.remove(); }
  java.util.Iterator it2 = GHOSTS.entrySet().iterator();
  while (it2.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it2.next(); if (wn.equals(e.getValue())) it2.remove(); }
  Object[] arr = @PKG@.MerchReg.snap(sites);
  for (int i = 0; i < arr.length; i++) {
    @PKG@.MerchSite s = (@PKG@.MerchSite) arr[i];
    if (s.uuid.length() > 0) KNOWN.put(s.uuid, wn + "\t" + s.zone);
    String[] g = s.ghostList();
    for (int k = 0; k < g.length; k++) GHOSTS.put(g[k], wn);
  }
}""")
M(core, r"""
public static void commit(String wn, java.util.ArrayList sites) {
  if (@PKG@.MerchReg.save(wn)) DIRTY.remove(wn);
  else DIRTY.put(wn, Boolean.TRUE);
  reindex(wn, sites);
}""")
# remove the merchant (and every ghost) of a line: true when the line changed
M(core, r"""
public static boolean ghostSweep(String wn, @PKG@.MerchSite s, long now) {
  boolean ch = s.expireGhosts(now, GHOST_MS);
  String[] g = s.ghostList();
  for (int i = 0; i < g.length; i++) {
    if (@PKG@.MerchEng.remove(wn, g[i]) == 1) { s.dropGhost(g[i]); count(3); ch = true; @PKG@.MerchLog.info("an old merchant (" + g[i] + ") of " + s.zone + " in " + wn + " was removed"); }
  }
  return ch;
}""")
# part off, zone gone, zone moved to another world: the merchant leaves (removed when loaded, else a ghost); the line is dropped once nothing
# of it is left in the world and the zone is gone from this world (part off keeps it: the merchants come back)
M(core, r"""
public static boolean retire(String wn, java.util.ArrayList sites, @PKG@.MerchSite s, boolean drop) {
  boolean ch = false;
  if (s.uuid.length() > 0) {
    if (@PKG@.MerchEng.remove(wn, s.uuid) != 1) s.addGhost(s.uuid, System.currentTimeMillis());
    s.uuid = "";
    s.missingSince = 0L;
    count(10);
    ch = true;
  }
  if (drop && s.ghosts.length() == 0) { @PKG@.MerchReg.remove(sites, s); ch = true; }
  return ch;
}""")
M(core, r"""
public static void reply(@PKG@.MerchSite s, String text, boolean ok) {
  if (s.reqBy != null) @PKG@.MerchEng.tellPlayer(s.reqBy, "[Merchants] " + text, ok ? "@COLOK@" : "@COLERR@");
  s.reqBy = null;
}""")
# find a spot + spawn + restock + save + remove the old one + rumour; false = nothing changed (no spot, refused, unsaved)
M(core, r"""
public static boolean relocate(String wn, java.util.ArrayList sites, @PKG@.MerchZone z, @PKG@.MerchSite s, long now, String why) {
  int[] p = @PKG@.MerchSpot.find(wn, z, SPOT_TRIES);
  if (p == null) { count(6); return false; }
  String env = @PKG@.MerchSpot.LAST_ENV;
  String role = @PKG@.MerchCfg.ROLE;
  if (!@PKG@.MerchEng.roleOk(role)) { @PKG@.MerchLog.warnOnce("role:" + role, "the NPC role " + role + " does not exist - using " + @PKG@.MerchCfg.DEFAULT_ROLE); role = @PKG@.MerchCfg.DEFAULT_ROLE; }
  String name = @PKG@.MerchCfg.NAME;
  @PKG@.MerchCfg.NAMES.add(name);
  @PKG@.MerchCfg.ROLES.add(role);
  String u = null;
  try { u = @PKG@.MerchEng.spawn(wn, role, (double) p[0] + 0.5, (double) p[1], (double) p[2] + 0.5, (float) (@PKG@.MerchSpot.RNG.nextDouble() * Math.PI * 2.0), name); }
  catch (Throwable t) { @PKG@.MerchLog.warnOnce("spawn:" + t.getClass().getName(), "spawning a merchant failed: " + t); u = null; }
  if (u == null) { count(7); @PKG@.MerchLog.warnOnce("spawnnull:" + wn + ":" + z.key, "the " + z.key + " merchant could not be spawned in " + wn + " (role " + role + ") - trying again in 5 s"); return false; }
  String oU = s.uuid, oS = s.stock, oG = s.ghosts, oE = s.env, oR = s.rumour;
  int oX = s.x, oY = s.y, oZ = s.z;
  long oP = s.placedAt, oV = s.visit;
  boolean oH = s.held, isNew = @PKG@.MerchReg.find(sites, z.key) == null;
  if (isNew) @PKG@.MerchReg.add(sites, s);
  if (oU.length() > 0) s.addGhost(oU, now);
  s.uuid = u; s.x = p[0]; s.y = p[1]; s.z = p[2]; s.placedAt = now; s.visit = s.visit + 1L; s.held = false; s.missingSince = 0L;
  s.env = env == null ? "" : env;
  s.stock = @PKG@.MerchShop.restock(z);
  s.rumour = @PKG@.MerchRumour.forSite(wn, z, s);
  if (!@PKG@.MerchReg.save(wn)) {
    @PKG@.MerchEng.remove(wn, u);
    s.uuid = oU; s.stock = oS; s.ghosts = oG; s.env = oE; s.rumour = oR; s.x = oX; s.y = oY; s.z = oZ; s.placedAt = oP; s.visit = oV; s.held = oH;
    if (isNew) @PKG@.MerchReg.remove(sites, s);
    count(8);
    return false;
  }
  if (oU.length() > 0 && @PKG@.MerchEng.remove(wn, oU) == 1) { s.dropGhost(oU); @PKG@.MerchReg.save(wn); }
  reindex(wn, sites);
  count(oU.length() > 0 ? 1 : 0);
  @PKG@.MerchLog.info("the " + z.key + " merchant " + why + " in " + wn + " at " + p[0] + " " + p[1] + " " + p[2] + " (" + s.env + ", visit " + s.visit + ", uuid " + u + ", stock " + s.stock + ")");
  if (@PKG@.MerchCfg.RUMOUR_ON && s.rumour.length() > 0) { @PKG@.MerchEng.tell(wn, s.rumour, "@COLRUM@"); count(5); }
  reply(s, "The " + z.name + " merchant " + why + " at " + p[0] + " " + p[1] + " " + p[2] + " (" + s.env + ").", true);
  return true;
}""")
# the merchant's chunk is loaded but the entity is gone (not saved by the engine, killed, despawned): back at the same spot, same stock
M(core, r"""
public static boolean respawnSame(String wn, java.util.ArrayList sites, @PKG@.MerchZone z, @PKG@.MerchSite s, long now) {
  String role = @PKG@.MerchCfg.ROLE;
  if (!@PKG@.MerchEng.roleOk(role)) role = @PKG@.MerchCfg.DEFAULT_ROLE;
  String u = null;
  try { u = @PKG@.MerchEng.spawn(wn, role, (double) s.x + 0.5, (double) s.y, (double) s.z + 0.5, 0.0f, @PKG@.MerchCfg.NAME); } catch (Throwable t) { u = null; }
  String old = s.uuid;
  s.addGhost(old, now);
  s.uuid = u == null ? "" : u;
  s.missingSince = 0L;
  if (!@PKG@.MerchReg.save(wn)) {
    if (u != null) @PKG@.MerchEng.remove(wn, u);
    s.uuid = old; s.dropGhost(old);
    count(8);
    return false;
  }
  reindex(wn, sites);
  count(2);
  @PKG@.MerchLog.info("the " + z.key + " merchant of " + wn + " was gone from its loaded spot " + s.x + " " + s.y + " " + s.z + " - " + (u == null ? "it moves on instead" : "back there now (uuid " + u + ")"));
  return true;
}""")
M(core, r"""
public static void request(String zone, String kind, java.util.UUID by) {
  REQ.put(zone, kind + "\t" + (by == null ? "" : by.toString()));
}""")
M(core, r"""
public static boolean takeRequest(@PKG@.MerchSite s) {
  Object o = REQ.remove(s.zone);
  if (o == null) return false;
  String[] p = String.valueOf(o).split("\t", -1);
  s.req = p[0];
  try { s.reqBy = p.length > 1 && p[1].length() > 0 ? java.util.UUID.fromString(p[1]) : null; } catch (Throwable t) { s.reqBy = null; }
  return true;
}""")
# one zone, one second (its world's thread); true = the line changed
M(core, r"""
public static boolean zoneSecond(String wn, java.util.ArrayList sites, @PKG@.MerchZone z, @PKG@.MerchSite s, long now) {
  boolean ch = false;
  if (takeRequest(s)) {
    String k = s.req;
    s.req = "";
    if (k.equals("remove")) {
      if (s.uuid.length() > 0 && @PKG@.MerchEng.remove(wn, s.uuid) != 1) s.addGhost(s.uuid, now);
      boolean had = s.uuid.length() > 0;
      s.uuid = ""; s.held = true; s.missingSince = 0L;
      if (@PKG@.MerchReg.find(sites, z.key) == null) @PKG@.MerchReg.add(sites, s);
      reply(s, "The " + z.name + " merchant " + (had ? "left" : "stays away") + " and stays away until /merchantadmin spawn " + z.key + ".", true);
      return true;
    }
    if (k.equals("spawn") && s.uuid.length() > 0) { reply(s, "The " + z.name + " merchant is already out at " + s.x + " " + s.y + " " + s.z + " - use /merchantadmin move " + z.key + ".", false); }
    else if (k.equals("spawn") || k.equals("move")) {
      s.held = false; s.nextTry = 0L;
      if (s.uuid.length() > 0) s.placedAt = 0L;
      if (!relocate(wn, sites, z, s, now, s.uuid.length() > 0 ? "moved" : "appeared")) {
        reply(s, "No spot for the " + z.name + " merchant yet (" + @PKG@.MerchSpot.LAST_WHY + ") - it keeps trying every 5 s while players are in " + wn + ".", false);
        s.nextTry = now + RETRY_MS;
        return ch;
      }
      return true;
    }
  }
  if (s.held) return ch;
  if (s.uuid.length() == 0) {
    if (now < s.nextTry) return ch;
    if (relocate(wn, sites, z, s, now, "appeared")) return true;
    s.nextTry = now + RETRY_MS;
    return ch;
  }
  int st = @PKG@.MerchEng.present(wn, s.uuid, s.x, s.z, @PKG@.MerchCfg.NAME);
  if (st == 1) { s.missingSince = 0L; s.seen = now; }
  else if (st == 0) {
    if (s.missingSince == 0L) s.missingSince = now;
    else if (now - s.missingSince >= GRACE_MS) {
      if (respawnSame(wn, sites, z, s, now)) ch = true;
      return ch;
    }
  } else s.missingSince = 0L;
  if (now - s.placedAt >= (long) @PKG@.MerchCfg.MOVE_S * 1000L && now >= s.nextTry) {
    if (relocate(wn, sites, z, s, now, "moved")) return true;
    s.nextTry = now + RETRY_MS;
  }
  return ch;
}""")
# THE SECOND of one world (World.execute: its own thread; MerchWorldTask)
M(core, r"""
public static void second(String wn, long now) {
  java.util.ArrayList sites = @PKG@.MerchReg.sites(wn);
  if (sites == null) return;
  boolean ch = DIRTY.containsKey(wn);
  Object[] arr = @PKG@.MerchReg.snap(sites);
  for (int i = 0; i < arr.length; i++) {
    @PKG@.MerchSite s = (@PKG@.MerchSite) arr[i];
    if (ghostSweep(wn, s, now)) ch = true;
    @PKG@.MerchZone z = @PKG@.MerchCfg.zone(s.zone);
    boolean mine = z != null && z.world.equals(wn);
    if (!@PKG@.MerchCfg.ON || !mine) { if (retire(wn, sites, s, !mine)) ch = true; }
  }
  if (@PKG@.MerchCfg.ON) {
    @PKG@.MerchZone[] zs = @PKG@.MerchCfg.ZONES;
    for (int i = 0; i < zs.length; i++) {
      if (!zs[i].world.equals(wn)) continue;
      @PKG@.MerchSite s = @PKG@.MerchReg.find(sites, zs[i].key);
      if (s == null) { s = new @PKG@.MerchSite(); s.zone = zs[i].key; }
      try { if (zoneSecond(wn, sites, zs[i], s, now)) ch = true; }
      catch (Throwable t) { @PKG@.MerchLog.warnOnce("zone:" + zs[i].key + ":" + t.getClass().getName(), "the " + zs[i].key + " merchant failed this second: " + t); }
    }
  }
  if (ch) commit(wn, sites);
  else if (KNOWN.isEmpty() && GHOSTS.isEmpty() && arr.length > 0) reindex(wn, sites);
}""")
# the add hook (RefSystem.onEntityAdded on an NPC; the world thread, inside the store's processing): 0 keep, 1 remove it
M(core, r"""
public static int onAdded(String wn, String uuid, String role, String plate) {
  if (wn == null || uuid == null) return 0;
  if (KNOWN.containsKey(uuid)) return 0;
  java.util.ArrayList sites = @PKG@.MerchReg.sites(wn);
  if (sites == null) return 0;
  Object[] arr = @PKG@.MerchReg.snap(sites);
  for (int i = 0; i < arr.length; i++) {
    @PKG@.MerchSite s = (@PKG@.MerchSite) arr[i];
    if (s.uuid.equals(uuid)) { s.missingSince = 0L; KNOWN.put(uuid, wn + "\t" + s.zone); return 0; }
  }
  for (int i = 0; i < arr.length; i++) {
    @PKG@.MerchSite s = (@PKG@.MerchSite) arr[i];
    if (s.hasGhost(uuid)) {
      s.dropGhost(uuid);
      GHOSTS.remove(uuid);
      DIRTY.put(wn, Boolean.TRUE);
      count(4);
      @PKG@.MerchLog.info("an old " + s.zone + " merchant (" + uuid + ") loaded in " + wn + " - removed (no duplicates)");
      return 1;
    }
  }
  if (role != null && plate != null && @PKG@.MerchCfg.ROLES.contains(role) && (@PKG@.MerchCfg.NAMES.contains(plate) || plate.equals(@PKG@.MerchCfg.NAME))) {
    count(4);
    @PKG@.MerchLog.info("a merchant with no registry line (" + uuid + ", " + role + ", '" + plate + "') loaded in " + wn + " - removed (orphan)");
    return 1;
  }
  return 0;
}""")
M(core, r"""
public static @PKG@.MerchSite siteOf(String wn, String zone) {
  java.util.ArrayList sites = @PKG@.MerchReg.sites(wn);
  return sites == null ? null : @PKG@.MerchReg.find(sites, zone);
}""")
M(core, r"""
public static String mins(long ms) {
  long m = (ms + 59999L) / 60000L;
  if (m < 1L) m = 1L;
  return m + " min";
}""")
# /merchantadmin list
M(core, r"""
public static String listText(String here, long now) {
  StringBuilder b = new StringBuilder("Roaming merchants " + (@PKG@.MerchCfg.ON ? "ON" : "OFF") + ", move every " + @PKG@.MerchCfg.MOVE_S + " s, role " + @PKG@.MerchCfg.ROLE + ":");
  @PKG@.MerchZone[] zs = @PKG@.MerchCfg.ZONES;
  for (int i = 0; i < zs.length; i++) {
    @PKG@.MerchZone z = zs[i];
    @PKG@.MerchSite s = siteOf(z.world, z.key);
    b.append("\n").append(z.key).append(" (").append(z.name).append(", ").append(z.world).append(", ").append(z.area).append(", ").append(z.band()).append("): ");
    if (s == null) b.append("not out yet - waits for a player in its area");
    else if (s.held) b.append("removed by an admin - /merchantadmin spawn ").append(z.key);
    else if (s.uuid.length() == 0) b.append("not out - looking for a spot (").append(@PKG@.MerchSpot.LAST_WHY).append(")");
    else {
      long left = (long) @PKG@.MerchCfg.MOVE_S * 1000L - (now - s.placedAt);
      b.append("at ").append(s.x).append(" ").append(s.y).append(" ").append(s.z).append(" (").append(@PKG@.MerchRumour.place(s.env)).append("), visit ").append(s.visit)
       .append(", moves in ").append(left > 0L ? mins(left) : "a moment").append(", stock ").append(@PKG@.MerchShop.offers(s, 0)[0].length + @PKG@.MerchShop.offers(s, 1)[0].length + @PKG@.MerchShop.offers(s, 2)[0].length).append(" offers");
    }
    if (s != null && s.ghosts.length() > 0) b.append("; old ones waiting to be removed: ").append(s.ghostList().length);
    if (z.world.equals(here) && s == null) b.append("");
  }
  if (zs.length == 0) b.append("\nno zones - Server Setup > Merchants > Zones");
  b.append("\nsince start: appeared " + N[0] + ", moved " + N[1] + ", back at spot " + N[2] + ", old removed " + N[3] + ", duplicates / orphans removed " + N[4] + ", rumours " + N[5] + ", no spot " + N[6] + ", spawn refused " + N[7] + ", unsaved " + N[8] + ", shop opens " + N[9] + ", sales " + @PKG@.MerchShop.SALES.get() + " (" + @PKG@.MerchLog.grp(@PKG@.MerchShop.COINS.get()) + " coins)" + (@PKG@.MerchReg.SAVE_FAILS.get() > 0L ? ", SAVE FAILS " + @PKG@.MerchReg.SAVE_FAILS.get() : ""));
  return b.toString();
}""")
# /merchants: the latest rumour of each merchant in the player's world
M(core, r"""
public static String rumoursText(String wn, long now) {
  StringBuilder b = new StringBuilder();
  @PKG@.MerchZone[] zs = @PKG@.MerchCfg.ZONES;
  for (int i = 0; i < zs.length; i++) {
    if (!zs[i].world.equals(wn)) continue;
    @PKG@.MerchSite s = siteOf(wn, zs[i].key);
    if (b.length() > 0) b.append("\n");
    if (!@PKG@.MerchCfg.ON || s == null || s.held || s.uuid.length() == 0 || s.rumour.length() == 0) b.append(zs[i].name).append(": no word of a merchant yet.");
    else {
      long left = (long) @PKG@.MerchCfg.MOVE_S * 1000L - (now - s.placedAt);
      b.append(zs[i].name).append(": ").append(s.rumour).append(" (moves on in about ").append(left > 0L ? mins(left) : "a moment").append(")");
    }
  }
  if (b.length() == 0) return "No traveling merchants roam this world.";
  return b.toString();
}""")
M(core, r"""
public static void flush() {
  try { @PKG@.MerchReg.flushAll(); } catch (Throwable t) { }
}""")

# =====================================================================================================================
# MerchPage: the shop (one inline page, tabs rebuilt on click; the vanilla kit look)
# =====================================================================================================================
PAGEC = cls("MerchPage", T["PAGE"])
PW, PH = 900, 720
SH = SUI.page_shell("SkyyMc", PW, PH, "Traveling Merchant", body_id="SkyyMcBody")
IW = SH.inner_w
TAB_IDS = ["SkyyMcTab0", "SkyyMcTab1", "SkyyMcTab2"]
TAB_NAMES = ["Weapons", "Mounts", "Pet eggs"]
TABS_H = SUI.BTN_H + 2 * SUI.TAB_MARGIN
HINT_H, HINT_M = 24, 6
STATUS_H, STATUS_M = 30, 6
FOOT_H = SUI.BTN_H + 8
LIST_H = SH.inner_h - TABS_H - (HINT_H + HINT_M) - (STATUS_H + STATUS_M) - FOOT_H
assert SH.fit([TABS_H, HINT_H + HINT_M, LIST_H, STATUS_H + STATUS_M, FOOT_H]) == 0, "the shop page body must be filled exactly"
assert LIST_H >= 360, LIST_H
LIST_IN = IW - 2 * SUI.WELL_LIST_PAD - 12
J_ = SUI.J


def jl(parent, mkup, root=True):
    return SUI.java_append(parent, mkup, page_root=root)


def jsets(mkup):
    return "\n".join(SUI.java_set(i, p, v) for i, p, v in getattr(mkup, "sets", []))


def page_java():
    ap = SUI.Appends()
    ap.add(SH.body, SUI.label("SkyyMcHint", "", "default", h=HINT_H, anchor={"bottom": HINT_M}))
    hint_java = ap.java("b")
    tabs = [SUI.tab_row(SH.body, "SkyyMcTabs", TAB_IDS, TAB_NAMES, i).java("b") for i in range(3)]
    lst = jl(SH.body, SUI.scroll_list("SkyyMcList", h=LIST_H, well=True))
    rkw = dict(icon=J_("ic", "Weapon_Sword_Frost"), name=J_("nm", "Frost Sword"), sub=J_("sb", "1 left this visit"),
               tag=J_("tg", "7,500 coins"), tag_col=J_("tc", COL["gold"]), tag_w=200, action="Buy")
    r_on = SUI.static_row("SkyyMcR" + J_("i", "0"), LIST_IN, action_on=True, **rkw)
    r_off = SUI.static_row("SkyyMcR" + J_("i", "0"), LIST_IN, action_on=False, **rkw)
    assert [s[0] for s in r_on.sets] == [s[0] for s in r_off.sets]
    row = jl("SkyyMcList", SUI.choose(J_("left > 0"), r_on, r_off), False) + "\n" + jsets(r_on)
    ap2 = SUI.Appends()
    ap2.text("SkyyMcList", "SkyyMcEmpty", J_("empty", "Nothing for sale here this visit."), "caption", h=48, wrap=True, max_lines=2)
    empty = ap2.java("b", page_root=False)
    status = jl(SH.body, SUI.status_line("SkyyMcStatus", anchor={"top": STATUS_M}))
    close_btn = SUI.button("SkyyMcClose", "Close", "secondary", sound="cancel")
    foot = jl(SH.body, SUI.button_row("SkyyMcFoot", align="right", used=SUI.BTN_MIN_W, avail=IW)) + "\n" + jl("SkyyMcFoot", close_btn, False)
    return dict(shell=SH.java("b"), hint=hint_java, t0=tabs[0], t1=tabs[1], t2=tabs[2], lst=lst, row=row, empty=empty, status=status, foot=foot)


PJ = page_java()


def ind(s, n=2):
    return "\n".join((" " * n) + l for l in s.split("\n"))


for _f in ("public String wn;", "public String zone;", "public String npc;", "public int tab;", "public String info;", "public String tok;",
           "public long base;", "public long seq;", "public String[] ids;", "public int armI;", "public String armId;", "public long armUntil;",
           "public static volatile long BUILDS = 0L;", "public static volatile long CLICKS = 0L;", "public static volatile long STALE = 0L;"):
    F(PAGEC, _f)
C(PAGEC, r"""
public MerchPage(@PR@ pr, String wn, String zone, String npc) {
  super(pr, @LIFE@.CanDismiss);
  this.wn = wn; this.zone = zone; this.npc = npc; this.tab = 0; this.info = ""; this.tok = "0";
  this.base = System.nanoTime() & 0xffffffL; this.seq = 0L; this.ids = new String[0]; this.armI = -1; this.armId = ""; this.armUntil = 0L;
}""")
for _l in SUI.java_status_methods():
    M(PAGEC, _l)
M(PAGEC, r"""
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
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
M(PAGEC, r"""
public static int toInt(String s) {
  try { return Integer.parseInt(s.trim()); } catch (Throwable t) { return -1; }
}""")
M(PAGEC, r"""
public String hintText(long now) {
  @PKG@.MerchZone z = @PKG@.MerchCfg.zone(this.zone);
  @PKG@.MerchSite s = @PKG@.MerchCore.siteOf(this.wn, this.zone);
  if (!@PKG@.MerchCfg.ON || z == null || s == null || !this.npc.equals(s.uuid)) return "This merchant has moved on - listen for the next rumour.";
  long left = (long) @PKG@.MerchCfg.MOVE_S * 1000L - (now - s.placedAt);
  long purse = @PKG@.MerchCoins.get(this.playerRef.getUuid());
  return z.name + " merchant - " + z.band() + " - moves on in " + (left > 0L ? @PKG@.MerchCore.mins(left) : "a moment") + (purse >= 0L ? " - your purse " + @PKG@.MerchLog.grp(purse) + " coins" : "");
}""")
BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  BUILDS = BUILDS + 1L;
  long now = System.currentTimeMillis();
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  String hint = hintText(now);
  @PKG@.MerchSite s = @PKG@.MerchCore.siteOf(this.wn, this.zone);
  boolean here = @PKG@.MerchCfg.ON && s != null && this.npc.equals(s.uuid);
@SHELL@
  if (this.tab == 0) {
@T0@
  } else if (this.tab == 1) {
@T1@
  } else {
@T2@
  }
@HINT@
  b.set("#SkyyMcHint.Text", hint);
@LST@
  String[][] of = here ? @PKG@.MerchShop.offers(s, this.tab) : new String[3][0];
  this.ids = of[0];
  for (int i = 0; i < of[0].length; i++) {
    String ic = of[0][i];
    String nm = @PKG@.MerchShop.name(ic);
    int left = toInt(of[2][i]);
    long price = 0L;
    try { price = Long.parseLong(of[1][i]); } catch (Throwable t) { price = 0L; }
    String sb = left > 0 ? left + " left this visit" : "Sold out - restocks when it moves";
    String tg = @PKG@.MerchLog.grp(price) + " coins";
    String tc = left > 0 ? "@GOLD@" : "@DISABLED@";
@ROW@
    if (left > 0) ev.addEventBinding(@BT@.Activating, "#SkyyMcR" + i + "Act", @EVD@.of("a", "buy").append("i", String.valueOf(i)).append("t", this.tok));
  }
  if (of[0].length == 0) {
    String empty = !here ? "The merchant has moved on." : (this.tab == 0 ? "No weapons left this visit - the merchant restocks when it moves." : (this.tab == 1 ? "Mounts are coming soon - none for sale yet." : "Pet eggs are coming soon - they arrive when pets come to the world."));
@EMPTY@
  }
@STATUS@
  b.set("#SkyyMcStatus.Text", textOf(this.info));
@FOOT@
  ev.addEventBinding(@BT@.Activating, "#SkyyMcTab0", @EVD@.of("a", "tab").append("i", "0"));
  ev.addEventBinding(@BT@.Activating, "#SkyyMcTab1", @EVD@.of("a", "tab").append("i", "1"));
  ev.addEventBinding(@BT@.Activating, "#SkyyMcTab2", @EVD@.of("a", "tab").append("i", "2"));
  ev.addEventBinding(@BT@.Activating, "#SkyyMcClose", @EVD@.of("a", "close"));
}"""
_rep = {"@SHELL@": ind(PJ["shell"]), "@T0@": ind(PJ["t0"], 4), "@T1@": ind(PJ["t1"], 4), "@T2@": ind(PJ["t2"], 4), "@HINT@": ind(PJ["hint"]),
        "@LST@": ind(PJ["lst"]), "@ROW@": ind(PJ["row"], 4), "@EMPTY@": ind(PJ["empty"], 4), "@STATUS@": ind(PJ["status"]),
        "@FOOT@": ind(PJ["foot"]), "@GOLD@": COL["gold"], "@DISABLED@": COL["disabled"]}
for _k, _v in _rep.items():
    assert _k in BUILD_SRC, _k
    BUILD_SRC = BUILD_SRC.replace(_k, _v)
M(PAGEC, BUILD_SRC)
PAGE_ID = hashlib.sha256(BUILD_SRC.encode("utf-8")).hexdigest()[:12]
M(PAGEC, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  CLICKS = CLICKS + 1L;
  String a = jsonStr(data, "a");
  int i = toInt(jsonStr(data, "i"));
  try {
    if (a.equals("close")) { close(); return; }
    if (a.equals("tab")) {
      if (i >= 0 && i <= 2) this.tab = i;
      this.info = "";
      this.armI = -1;
      rebuild();
      return;
    }
    if (!jsonStr(data, "t").equals(this.tok)) { STALE = STALE + 1L; this.info = "=The page changed - here it is again."; rebuild(); return; }
    if (a.equals("buy")) {
      long now = System.currentTimeMillis();
      if (i < 0 || i >= this.ids.length) this.info = "-That offer is gone.";
      else {
        String id = this.ids[i];
        boolean armed = this.armI == i && this.armId.equals(id) && now <= this.armUntil;
        if (!armed) {
          this.armI = i; this.armId = id; this.armUntil = now + 10000L;
          String[][] of = @PKG@.MerchShop.offers(@PKG@.MerchCore.siteOf(this.wn, this.zone), this.tab);
          String price = "?";
          for (int k = 0; k < of[0].length; k++) if (of[0][k].equals(id)) price = @PKG@.MerchLog.grp(Long.parseLong(of[1][k]));
          this.info = "=Buy " + @PKG@.MerchShop.name(id) + " for " + price + " coins? Click BUY again to confirm.";
        } else {
          this.armI = -1;
          java.util.UUID u = this.playerRef.getUuid();
          Object player = null;
          try { player = st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable tp) { player = null; }
          this.info = @PKG@.MerchShop.buy(u, this.playerRef.getUsername(), player, @PKG@.MerchEng.pos(ref, st), this.wn, this.zone, this.npc, this.tab, id);
        }
      }
    } else this.info = "";
  } catch (Throwable t) {
    @PKG@.MerchLog.warn("shop click " + a + " failed: " + t);
    this.info = "-Something went wrong - check your inventory and purse. The server log has the details.";
  }
  rebuild();
}""")

# =====================================================================================================================
# MerchOpen: opens the page next tick (World.execute) - never from inside the ECS handler; MerchCore.use is added here
# =====================================================================================================================
opn = cls("MerchOpen")
opn.addInterface(pool.get("java.lang.Runnable"))
for _f in ("@REF@ ref", "@PR@ pr", "String wn", "String zone", "String npc"):
    F(opn, "public %s;" % _f)
C(opn, "public MerchOpen(@REF@ ref, @PR@ pr, String wn, String zone, String npc) { this.ref = ref; this.pr = pr; this.wn = wn; this.zone = zone; this.npc = npc; }")
M(opn, r"""
public void run() {
  try {
    if (!@PKG@.MerchCfg.ON) { @PKG@.MerchEng.say(this.pr, "[Merchants] The merchants are away.", "@COLERR@"); return; }
    if (@PKG@.MerchEng.open(this.ref, this.pr, new @PKG@.MerchPage(this.pr, this.wn, this.zone, this.npc))) @PKG@.MerchCore.count(9);
  } catch (Throwable t) { @PKG@.MerchLog.warnOnce("open:" + t.getClass().getName(), "the shop page could not open: " + t); }
}""")
# F on an NPC (the use system): our merchant -> the page next tick; an old one (ghost) -> a line. Answers true when the use was ours.
M(core, r"""
public static boolean use(String wn, String uuid, @REF@ ref, @PR@ pr) {
  if (uuid == null) return false;
  Object k = KNOWN.get(uuid);
  if (k == null) {
    if (GHOSTS.containsKey(uuid)) { @PKG@.MerchEng.say(pr, "[Merchants] This merchant is packing up - listen for the next rumour.", "@COLINF@"); return true; }
    return false;
  }
  String[] p = String.valueOf(k).split("\t", -1);
  if (p.length < 2) return false;
  @PKG@.MerchOpen o = new @PKG@.MerchOpen(ref, pr, p[0], p[1], uuid);
  if (!@PKG@.MerchEng.exec(p[0], o)) o.run();
  return true;
}""")

# =====================================================================================================================
# ECS: MerchUseSys (UseEntityEvent$Pre, fired on the PLAYER - UseEntityInteraction.firstRun) + MerchAddSys (RefSystem on NPCs)
# =====================================================================================================================
usys = cls("MerchUseSys", T["EES"])
F(usys, "public static boolean FAILED_ONCE = false;")
F(usys, "public static final java.util.concurrent.atomic.AtomicLong HITS = new java.util.concurrent.atomic.AtomicLong();")
C(usys, "public MerchUseSys() { super(@UEPRE@.class); }")
M(usys, "public @QRY@ getQuery() { return @ARCH@.empty(); }")
M(usys, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (@PKG@.MerchCore.KNOWN.isEmpty() && @PKG@.MerchCore.GHOSTS.isEmpty()) return;
    if (!(ev instanceof @UEPRE@)) return;
    @UEPRE@ e = (@UEPRE@) ev;
    if (e.isCancelled()) return;
    @REF@ t = e.getTargetEntity();
    if (t == null || !t.isValid()) return;
    java.util.UUID u = @PKG@.MerchEng.uuidOf(st, t);
    if (u == null) return;
    String us = u.toString();
    if (!@PKG@.MerchCore.KNOWN.containsKey(us) && !@PKG@.MerchCore.GHOSTS.containsKey(us)) return;
    e.setCancelled(true);
    HITS.incrementAndGet();
    @REF@ r = chunk.getReferenceTo(idx);
    @PR@ pr = r == null ? null : (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.MerchCore.use(@PKG@.MerchEng.worldOf(st), us, r, pr);
  } catch (Throwable x) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MerchLog.warn("use hook failed (logged once): " + x); }
  }
}""")
asys = cls("MerchAddSys", T["RSYS"])
F(asys, "public static boolean FAILED_ONCE = false;")
F(asys, "public @QRY@ query;")
C(asys, "public MerchAddSys() { super(); }")
M(asys, r"""
public @QRY@ getQuery() {
  if (this.query == null) this.query = (@QRY@) @NPC@.getComponentType();
  return this.query;
}""")
M(asys, r"""
public void onEntityAdded(@REF@ ref, @ADR@ why, @ST@ st, @CB@ cb) {
  try {
    if (@PKG@.MerchReg.DIR == null) return;
    String wn = @PKG@.MerchEng.worldOf(st);
    if (wn == null || !(@PKG@.MerchCfg.worldHasZone(wn) || @PKG@.MerchReg.known(wn))) return;
    java.util.UUID u = @PKG@.MerchEng.uuidOf(st, ref);
    if (u == null) return;
    if (@PKG@.MerchCore.onAdded(wn, u.toString(), @PKG@.MerchEng.roleOf(st, ref), @PKG@.MerchEng.plateOf(st, ref)) == 1) cb.tryRemoveEntity(ref, @RR@.REMOVE);
  } catch (Throwable x) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.MerchLog.warn("add hook failed (logged once): " + x); }
  }
}""")
M(asys, "public void onEntityRemove(@REF@ ref, @RR@ why, @ST@ st, @CB@ cb) { }")

# =====================================================================================================================
# MerchWorldTask (World.execute) + MerchTimer (HytaleServer scheduler, 1 s)
# =====================================================================================================================
wtask = cls("MerchWorldTask")
wtask.addInterface(pool.get("java.lang.Runnable"))
F(wtask, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")
F(wtask, "public String wn;")
C(wtask, "public MerchWorldTask(String wn) { this.wn = wn; }")
M(wtask, r"""
public void run() {
  try { @PKG@.MerchCore.second(this.wn, System.currentTimeMillis()); }
  catch (Throwable t) { @PKG@.MerchLog.warnOnce("second:" + t.getClass().getName(), "the merchant second of world " + this.wn + " failed: " + t); }
  finally { PENDING.remove(this.wn); }
}""")
timer = cls("MerchTimer")
timer.addInterface(pool.get("java.lang.Runnable"))
F(timer, "public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();")
C(timer, "public MerchTimer() { }")
M(timer, r"""
public void run() {
  try {
    RUNS.incrementAndGet();
    String[] ws = @PKG@.MerchEng.worlds();
    for (int i = 0; i < ws.length; i++) {
      String wn = ws[i];
      if (wn == null) continue;
      if (!@PKG@.MerchCfg.worldHasZone(wn) && !@PKG@.MerchReg.known(wn)) continue;
      if (@PKG@.MerchWorldTask.PENDING.putIfAbsent(wn, Boolean.TRUE) != null) continue;
      boolean ok = false;
      try { ok = @PKG@.MerchEng.exec(wn, new @PKG@.MerchWorldTask(wn)); } catch (Throwable t) { ok = false; }
      if (!ok) @PKG@.MerchWorldTask.PENDING.remove(wn);
    }
  } catch (Throwable t) { @PKG@.MerchLog.warnOnce("timer:" + t.getClass().getName(), "the merchant timer failed: " + t); }
}""")

# =====================================================================================================================
# Commands: /merchants (every player) + /merchantadmin list | move | spawn | remove <zone> (op only)
# =====================================================================================================================
cmds = cls("MerchCmds")
M(cmds, r"""
public static String admin(@PR@ pr, String wn, String verb, String zone) {
  long now = System.currentTimeMillis();
  String v = verb == null ? "" : verb.trim().toLowerCase();
  if (v.length() == 0 || v.equals("help")) return "=/merchantadmin list | move <zone> | spawn <zone> | remove <zone>";
  if (v.equals("list")) return "=" + @PKG@.MerchCore.listText(wn, now);
  if (!v.equals("move") && !v.equals("spawn") && !v.equals("remove")) return "-Unknown option " + verb + ". Use list, move, spawn or remove.";
  if (zone == null || zone.trim().length() == 0) return "-Which zone? /merchantadmin " + v + " <zone> (zone ids: /merchantadmin list).";
  @PKG@.MerchZone z = @PKG@.MerchCfg.zone(zone.trim());
  if (z == null) return "-No zone " + zone.trim() + " (Server Setup > Merchants > Zones).";
  if (!@PKG@.MerchCfg.ON && !v.equals("remove")) return "-Roaming merchants are switched off (Server Setup > Merchants).";
  @PKG@.MerchCore.request(z.key, v, pr == null ? null : pr.getUuid());
  @PKG@.MerchLog.info((pr == null ? "console" : pr.getUsername()) + " asked: " + v + " " + z.key);
  if (z.world.equals(wn) && @PKG@.MerchWorldTask.PENDING.putIfAbsent(wn, Boolean.TRUE) == null) {
    boolean ok = false;
    try { ok = @PKG@.MerchEng.exec(wn, new @PKG@.MerchWorldTask(wn)); } catch (Throwable t) { ok = false; }
    if (!ok) @PKG@.MerchWorldTask.PENDING.remove(wn);
    return ok ? "" : "=Queued: " + v + " " + z.key + " happens within a second.";
  }
  return "=Queued: " + v + " " + z.key + " happens on the next second of world " + z.world + " (it needs a player there). You get a line when it is done.";
}""")
M(cmds, r"""
public static void reply(@PR@ pr, String res) {
  if (res == null || res.length() == 0) return;
  char c = res.charAt(0);
  String col = c == '+' ? "@COLOK@" : (c == '-' ? "@COLERR@" : "@COLINF@");
  String t = (c == '+' || c == '-' || c == '=') ? res.substring(1) : res;
  String[] ls = t.split("\n");
  for (int i = 0; i < ls.length; i++) @PKG@.MerchEng.say(pr, (i == 0 ? "[Merchants] " : "  ") + ls[i], col);
}""")
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
pcmd = cls("MerchantsCmd", T["APC"])
C(pcmd, r"""
public MerchantsCmd() {
  super("merchants", "Rumours: where the traveling merchants of this world were last seen");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addAliases(new String[] { "rumours", "rumors" });
}""")
M(pcmd, EXEC + r""" {
  @PKG@.MerchCmds.reply(pr, "=" + @PKG@.MerchCore.rumoursText(world == null ? "" : world.getName(), System.currentTimeMillis()));
}""")
acmd1 = cls("MerchAdminArgCmd", T["APC"])
F(acmd1, "public @RA@ verbArg;")
C(acmd1, r"""
public MerchAdminArgCmd() {
  super("(admin) /merchantadmin list");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.verbArg = withRequiredArg("option", "list", @ATY@.STRING);
}""")
M(acmd1, EXEC + r""" {
  String a = "";
  try { a = String.valueOf(ctx.get(this.verbArg)); } catch (Throwable t) { a = ""; }
  @PKG@.MerchCmds.reply(pr, @PKG@.MerchCmds.admin(pr, world == null ? "" : world.getName(), a, null));
}""")
acmd2 = cls("MerchAdminArg2Cmd", T["APC"])
F(acmd2, "public @RA@ verbArg;")
F(acmd2, "public @RA@ zoneArg;")
C(acmd2, r"""
public MerchAdminArg2Cmd() {
  super("(admin) /merchantadmin move | spawn | remove <zone>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.verbArg = withRequiredArg("option", "move, spawn or remove", @ATY@.STRING);
  this.zoneArg = withRequiredArg("zone", "a zone id from /merchantadmin list (zone1 ...)", @ATY@.STRING);
}""")
M(acmd2, EXEC + r""" {
  String a = "", z = "";
  try { a = String.valueOf(ctx.get(this.verbArg)); z = String.valueOf(ctx.get(this.zoneArg)); } catch (Throwable t) { a = ""; }
  @PKG@.MerchCmds.reply(pr, @PKG@.MerchCmds.admin(pr, world == null ? "" : world.getName(), a, z));
}""")
acmd = cls("MerchAdminCmd", T["APC"])
C(acmd, r"""
public MerchAdminCmd() {
  super("merchantadmin", "(admin) Roaming merchants: /merchantadmin list | move <zone> | spawn <zone> | remove <zone>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addUsageVariant(new @PKG@.MerchAdminArgCmd());
  addUsageVariant(new @PKG@.MerchAdminArg2Cmd());
}""")
M(acmd, EXEC + " { @PKG@.MerchCmds.reply(pr, @PKG@.MerchCmds.admin(pr, world == null ? \"\" : world.getName(), \"help\", null)); }")

# =====================================================================================================================
# the plugin
# =====================================================================================================================
plug = cls("SkyyMerchantsPlugin", T["JP"])
F(plug, "public static volatile Object TIMER = null;")
C(plug, "public SkyyMerchantsPlugin(@JPI@ init) { super(init); }")
M(plug, r"""
public void setup() {
  @PKG@.MerchLog.LOG = getLogger();
  java.nio.file.Path mods = getDataDirectory().getParent();
  @PKG@.MerchCfg.load(mods);
  java.nio.file.Path dir = mods.resolve("Skyy_SkyyMerchants");
  @PKG@.MerchReg.DIR = dir.resolve("merchants");
  @PKG@.MerchShop.LOGF = dir.resolve("sales.log");
  @PKG@.CfgPub.start(mods, getLogger());
  getCommandRegistry().registerCommand(new @PKG@.MerchantsCmd());
  getCommandRegistry().registerCommand(new @PKG@.MerchAdminCmd());
  try { getEntityStoreRegistry().registerSystem(new @PKG@.MerchUseSys()); }
  catch (Throwable t) { @PKG@.MerchLog.warn("MerchUseSys could not be registered: " + t + " - F on a merchant does nothing"); }
  try { getEntityStoreRegistry().registerSystem(new @PKG@.MerchAddSys()); }
  catch (Throwable t2) { @PKG@.MerchLog.warn("MerchAddSys could not be registered: " + t2 + " - old merchants that load after a move are removed by the per-second ghost sweep only"); }
  try { TIMER = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.MerchTimer(), 3L, 1L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t3) { @PKG@.MerchLog.warn("the merchant timer could not start: " + t3 + " - no merchant appears or moves"); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyMerchants] @VERSION@ ready - " + @PKG@.MerchCfg.ZONES.length + " zones, " + @PKG@.MerchCfg.ITEMS.length + " stock lines, role " + @PKG@.MerchCfg.ROLE + ", move every " + @PKG@.MerchCfg.MOVE_S + " s, " + (@PKG@.MerchCfg.ON ? "ON" : "OFF") + "; /merchants, /merchantadmin; kit @KITID@, page @PAGEID@");
}""".replace("@PAGEID@", PAGE_ID))
M(plug, r"""
protected void shutdown() {
  try { if (TIMER instanceof java.util.concurrent.Future) ((java.util.concurrent.Future) TIMER).cancel(false); } catch (Throwable t) { }
  try { @PKG@.MerchReg.STOPPING = true; @PKG@.MerchCore.flush(); } catch (Throwable t2) { @PKG@.MerchLog.warn("the last merchant save failed: " + t2); }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t4) { }
  super.shutdown();
}""")

# ================================================================= write + assemble
kit.write(OUT)
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d (+ the config kit's 7); shop page id %s" % (len(ALL), PAGE_ID))
jar = os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)
man = B.manifest(MOD, VERSION, "SkyWynn roaming merchants: one merchant per zone moves to a new spot every 20 min, rumours in chat, a shop "
                 "for special weapons (mounts and pet eggs later), coins through SkyyCoins.", PKG + ".SkyyMerchantsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
