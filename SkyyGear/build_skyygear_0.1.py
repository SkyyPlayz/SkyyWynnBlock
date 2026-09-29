"""SkyyGear 0.1 - build script (javassist via jpype). NEW mod: rarity, level and modifiers on every weapon and armor piece.
Spec: research/SkyyGear-Stage1-Spec.md (the spec wins over this script; section numbers below point into it). Design docs (read only):
SkyyGear-Plan.md, SkyyGear-Stat-Catalog.md. SkyyGear REPLACES SkyyRolls (same /reforge command; deploy: SkyyRolls goes into
tools/deploy_set.py RETIRED - main-session work, spec 8.3).
Run:   python SkyyGear/build_skyygear_0.1.py            -> SkyyGear/SkyyGear-0.1.jar   (never pass --deploy from a builder agent)

THIS FILE IS BUILT IN TWO PARTS (Skyy / RESUME step 4). PART A = this build. PART B = a second builder adds its classes at the
"PART B PLUGS IN HERE" markers below without rewriting PART A:
  PART A (built here): the gear document on the ItemStack with its GATE SKILL (spec 1), the Wynn rarity ladder + 7 quality assets
    (2.1), the level table (3.1-3.2), the gate check + level cache used by tooltips / bridge (3.3; enforcement is PART B), the modifier
    pool + rolling by rarity with the level-scaled strength (2.2-2.3, 4.2), crafted-gear rolls on the vanilla benches (GearCraftSys,
    5.1) + the gear:fn:roll bridge for SkyySacks /craft (5.2, 7.3.3), smithing rarity odds (5.3), /reforge (5.4, vanilla look 5.8),
    SkyyRolls migration (1.6, migrate.by=stats default, migrate.maxRarity), SkyBlock-style tooltips (6), the legacy stamp + the
    drop stamp GearThrowSys (1.5), bridge functions (7.1; GearTick publishes gear:stats:<uuid> = the active totals, gear:fn:stats
    reads it), Server Setup rows via tools/skyycfg.py kit 1.1 with KEEP=10 (9), player
    switches (9.3), admin /gear commands (8.1), gear.log (8.2), the SkyyRolls cost import (1.6) and the SkyyRolls-still-loaded
    warning (8.4).
  PART B (NOT built here): unidentified drops from mobs (GearDeathMark + GearDropSys, 5.5) and world chests (GearChestMark +
    GearChestTag, 5.5), the /identify page + command (5.7; the cost table cost.identify, the identify roll GearRoll.identify and
    the admin /gear identify already exist), live stat effects (GearHitSys / GearArmorSys / GearTrueSys / GearLeechSys, the
    GearTick regen / stamina / armor-lock / speed parts; 4.3, 3.5) and level enforcement (weapon block + popup
    3.4 through GearGate.popup, inactive armor 3.5). Hooks ready for PART B: PARTB_CLASSES, PARTB_SETUP, PARTB_TICK (Python lists /
    string below), GearStats.totals / statsString (active totals), GearGate.check / have / popup, GearRoll.unidDoc / identify,
    GearData.put, GearCfg.costIdentify, the settings gear.blockedPopup / gear.armorWarn (registered here).

Commands (spec 8.1):
  /reforge                 player (hytale:Adventurer): the Reforge page (vanilla item-repair look): pick a weapon or armor piece,
                           pay coins (cost.reforge by rarity + level), its modifiers are re-rolled for its rarity and level; the
                           rarity never changes; Smithing XP through skill:fn:addxp (xp.reforge).
  /gear                    player: the held item's gear lines, your active totals, your Smithing rarity.
  /gear give <item> [--rarity <id>] [--unid true] | read | reroll | clear | rarity <id> | unid | identify | level <n|clear> |
        gate <skill|class> | migrate [player]
                           ADMIN: requirePermission("skyygear.admin") + setPermissionGroups(new String[0]) on every sub-command
                           (lint perm_group_leaks); the root /gear lists hytale:Adventurer.
Data: <world>/mods/Skyy_SkyyGear/ (getDataDirectory().resolveSibling): config.properties (the kit's rows), config-changes.log +
  config-history/ (kit, KEEP 10), players/<pkey>.properties (noticeShown), gear.log (rotated at 5 MB).
UI rules: inline pages only, no underscores in ids, root anchor Width/Height only, TextButton / Button + EventData, no periodic
  updates, never close-then-open, no ItemGridSlot at all (icons are ItemIcon { ItemId } = metadata free).
Vanilla look (spec 5.8, AGENT-BRIEF "UI LOOK"): the values in VANILLA below are copied from Assets.zip Common/UI/Custom/Common.ui,
  Sounds.ui and Pages/ItemRepairPage.ui / ItemRepairElement.ui (checked by this build). They are meant for the shared vanilla style
  helper of RESUME step 5 - move them there when it exists. Server Setup switch ui.frames (adv) turns the textures and sounds off
  (flat vanilla colours) as a safety valve if a texture path does not resolve in an inline page (UNVERIFIED in game).
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J0 = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J0["pool"], J0["CtField"], J0["CtNewMethod"], J0["CtNewConstructor"]
OUT = B.class_out(HERE)
AZ_PATH = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
AZ = zipfile.ZipFile(AZ_PATH)
AZ_NAMES = set(AZ.namelist())

# ================================================================= engine classes (probed below)
JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
GM  = "com.hypixel.hytale.protocol.GameMode"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
BD  = "org.bson.BsonDocument"
BV  = "org.bson.BsonValue"
BA  = "org.bson.BsonArray"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IDM = "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata"
IQ  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality"
IWP = "com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon"
IAR = "com.hypixel.hytale.server.core.asset.type.item.config.ItemArmor"
DBD = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown"
DBE = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown$Entry"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
EST2 = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
DCS = "com.hypixel.hytale.server.core.modules.entity.damage.DamageCause"
I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
PCOL = "com.hypixel.hytale.protocol.Color"
TXN = "com.hypixel.hytale.server.core.inventory.transaction.Transaction"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
PAGE = "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE = "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
CMGR = "com.hypixel.hytale.server.core.command.system.CommandManager"
NTU = "com.hypixel.hytale.server.core.util.NotificationUtil"
NST = "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle"
IWM = "com.hypixel.hytale.protocol.ItemWithAllMetadata"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
ARC = "com.hypixel.hytale.component.Archetype"
ICE = "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent"
DIE = "com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$Drop"      # '$' form for the class literal (SkyySkills CREP)
CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CREP = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"
PERM = "com.hypixel.hytale.server.core.permissions.PermissionsModule"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"

for c, m in ((IS, "withMetadata"), (IS, "getMetadata"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItemId"),
             (IS, "getQuantity"), (IS, "getDurability"), (IS, "getMaxDurability"), (IS, "isEmpty"), (IS, "getItem"),
             (IS, "getFromMetadataOrNull"), (IS, "CODEC"), (IS, "toPacket"), (ITM, "getItemLevel"), (ITM, "getAssetMap"),
             (ITM, "getWeapon"), (ITM, "getArmor"), (ITM, "getTranslationKey"), (ITM, "getTranslationMessage"),
             (ITM, "getDescriptionTranslationKey"), (ITM, "getDescriptionTranslationMessage"), (ITM, "getMaxStack"),
             (IAR, "getStatModifiers"), (IAR, "getDamageResistanceValues"), (SMO, "getAmount"), (SMO, "getCalculationType"),
             (CAL, "MULTIPLICATIVE"), (EST2, "getAssetMap"), (DCS, "getId"),
             (IWP, "getBasicDamageBreakdown"), (IWP, "getUltimateDamageBreakdown"), (DBD, "entries"), (DBE, "min"), (DBE, "max"),
             (IQ, "getAssetMap"), (IQ, "getTextColor"), (IQ, "getId"), (IQ, "getLocalizationKey"), (PCOL, "red"),
             (IDM, "KEYED_CODEC"), (IDM, "KEY"), (I18N, "get"), (I18N, "getMessage"), (MSG, "raw"), (MSG, "color"), (MSG, "insert"),
             (MSG, "empty"), (INV, "getHotbar"), (INV, "getStorage"), (INV, "getBackpack"), (INV, "getArmor"), (INV, "getUtility"),
             (INV, "getTools"), (INV, "usingToolsItem"), (INV, "getActiveToolsSlot"), (INV, "getActiveHotbarSlot"),
             (IC, "getItemStack"), (IC, "setItemStackForSlot"), (IC, "getCapacity"), (IC, "addItemStack"), (TXN, "succeeded"),
             (PLA, "getInventory"), (PLA, "getPageManager"), (PLA, "getGameMode"), (PLA, "isWaitingForClientReady"), (GM, "Creative"),
             (PR, "getUuid"), (PR, "getUsername"), (PR, "getReference"), (PR, "getWorldUuid"), (PR, "isValid"), (PR, "sendMessage"),
             (PR, "getPacketHandler"), (PR, "hasPermission"), (PR, "getComponentType"), (PRE, "getPlayerRef"), (UNI, "get"),
             (UNI, "getWorld"), (UNI, "getPlayers"), (WLD, "execute"), (REF, "isValid"), (REF, "getStore"), (ST, "getComponent"),
             (ST, "getExternalData"), (EST, "getWorld"), (HSV, "SCHEDULED_EXECUTOR"), (ACH, "getReferenceTo"),
             (ICE, "getTransaction"), (DIE, "getItemStack"), (DIE, "setItemStack"), (DIE, "isCancelled"), (CRE, "getCraftedRecipe"),
             (CRE, "getQuantity"), (CRR, "getPrimaryOutput"), (CRR, "getTimeSeconds"), (CRR, "getId"), (MQ, "getItemId"),
             (MQ, "getQuantity"), (MQ, "getMetadata"), (PAGE, "rebuild"), (PAGE, "close"), (PAGE, "build"), (PAGE, "handleDataEvent"),
             (LIFE, "CanDismiss"), ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (UCB, "appendInline"), (UCB, "set"), (UEB, "addEventBinding"), (EVD, "of"), (BT, "Activating"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "setAllowsExtraArguments"),
             (CTX, "getInputString"), (CTX, "provided"), (CTX, "get"), (AC, "withOptionalArg"), (ATY, "STRING"), (ATY, "BOOLEAN"), (CMGR, "get"), (CMGR, "handleCommand"), (NTU, "sendNotification"), (NST, "Warning"),
             (JP, "getDataDirectory"), (JP, "getEntityStoreRegistry"), (JP, "getEventRegistry"), (JP, "getCommandRegistry"),
             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal"), (PERM, "get"), (PERM, "hasPermission"),
             (BD, "append"), (BD, "clone"), (BD, "remove"), (BD, "containsKey"), (BD, "toJson"), (BA, "add"), (BV, "asDocument"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset")):
    B.probe(pool, c, m)
# spec 11.1 #2 probes that belong to PART B (kept here so a missing API fails the build early, before PART B is written)
for c, m in (("com.hypixel.hytale.server.core.modules.entity.damage.DamageSystems$ArmorDamageReduction", "getResistanceModifiers"),
             ("com.hypixel.hytale.server.core.modules.entity.item.ItemComponent", "setItemStack"),
             ("com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility", "getActiveItem"),
             ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap", "putModifier")):
    B.probe(pool, c, m)
for c in ("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems",
          "com.hypixel.hytale.builtin.adventure.stash.StashPlugin$StashSystem"):
    try:
        pool.get(c)
    except Exception:
        # PART B targets; a missing class only matters to PART B (it registers unordered + WARN then)
        print("note: PART B target class not in the pool:", c)

PKG = "com.skyy.gear"
T = {"PKG": PKG, "IS": IS, "BD": BD, "BV": BV, "BA": BA, "MSG": MSG, "ITM": ITM, "IQ": IQ, "IWP": IWP, "IAR": IAR, "DBD": DBD,
     "DBE": DBE, "INV": INV, "IC": IC, "SIC": SIC, "PLA": PLA, "PR": PR, "REF": REF, "ST": ST, "WLD": WLD, "EST": EST, "CTX": CTX,
     "TXN": TXN, "PAGE": PAGE, "LIFE": LIFE, "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT, "IDM": IDM, "I18N": I18N,
     "PCOL": PCOL, "HSV": HSV, "UNI": UNI, "LOG": LOG, "GM": GM, "CRR": CRR, "MQ": MQ, "SMO": SMO, "CAL": CAL, "ESTT": EST2,
     "DCS": DCS, "CMGR": CMGR, "NTU": NTU, "NST": NST, "IWM": IWM, "ACH": ACH, "CB": CB, "EV": EV, "QRY": QRY, "ARC": ARC,
     "ICE": ICE, "DIE": DIE, "CRE": CRE, "CREP": CREP, "PRE": PRE, "APC": APC, "PERM": PERM, "JPI": JPI, "ATY": ATY, "OA": OA}


def J(src):
    for k in sorted(T, key=len, reverse=True):
        src = src.replace("@" + k + "@", T[k])
    left = re.findall(r"@[A-Z]+@", src)
    assert not left, "unresolved placeholder(s): %s" % left
    return src


def _mk(c, src):
    try:
        c.addMethod(CtNewMethod.make(J(src), c))
    except Exception as e:
        raise SystemExit("compile error in %s: %s\n%s" % (c.getName(), e, J(src)[:1500]))


def M(c, src):
    _mk(c, src)


def F(c, src):
    c.addField(CtField.make(J(src), c))


def C(c, src):
    try:
        c.addConstructor(CtNewConstructor.make(J(src), c))
    except Exception as e:
        raise SystemExit("constructor compile error in %s: %s\n%s" % (c.getName(), e, J(src)[:1200]))


def jstr(s):
    assert all(32 <= ord(ch) < 127 for ch in s), repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def jarr(xs):
    return "new String[] { " + ", ".join(jstr(x) for x in xs) + " }" if xs else "new String[0]"


def jints(xs):
    return "new int[] { " + ", ".join(str(int(x)) for x in xs) + " }" if xs else "new int[0]"


def jlit(txt):
    return '"' + txt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


# ================================================================= spec 2.1: the rarity ladder (LOCKED names + colours)
# (id, Name, hex (tooltip + quality TextColor), page hex (vanilla panel, spec 5.8: Mythic readable variant = SkyySacks' choice),
#  frame art: tooltip + arrow texture quality, slot texture quality, drop particle)
RARITIES = [
    ("normal", "Normal", "#FFFFFF", "#FFFFFF", "Common", "Common", "Drop_Common"),
    ("unique", "Unique", "#FFFF55", "#FFFF55", "Legendary", "Legendary", "Drop_Legendary"),
    ("rare", "Rare", "#FF55FF", "#FF55FF", "Epic", "Epic", "Drop_Epic"),
    ("legendary", "Legendary", "#55FFFF", "#55FFFF", "Rare", "Rare", "Drop_Rare"),
    ("fabled", "Fabled", "#FF5555", "#FF5555", "Common", "Developer", "Drop_Legendary"),
    ("mythic", "Mythic", "#AA00AA", "#CC66CC", "Epic", "Epic", "Drop_Epic"),
    ("set", "Set", "#55FF55", "#55FF55", "Uncommon", "Uncommon", "Drop_Uncommon"),
]
NR = len(RARITIES)
R_IDS = [r[0] for r in RARITIES]
R_NAMES = [r[1] for r in RARITIES]
QUAL_IDS = ["Skyy_Gear_" + r[1] for r in RARITIES]
assert R_IDS == ["normal", "unique", "rare", "legendary", "fabled", "mythic", "set"]
LADDER = R_IDS[:6]          # stepping order for Smithing (never to Set)

# spec 2.2 rarity table (PLACEHOLDER): modifiers | low % | high %
RARITY_DEF = {"normal": (1, 30, 60), "unique": (2, 35, 70), "rare": (3, 40, 80), "legendary": (4, 45, 95),
              "fabled": (5, 50, 110), "mythic": (6, 60, 130), "set": (3, 45, 95)}
# spec 5.3 / 5.5 odds (PLACEHOLDER weights): craft | mob | chest
ODDS_DEF = {"normal": (60, 50, 45), "unique": (25, 30, 30), "rare": (10, 13, 15), "legendary": (4, 5, 7), "fabled": (1, 1.5, 2.4),
            "mythic": (0, 0.5, 0.6), "set": (0, 0, 0)}
# spec 5.4 reforge cost (base | per level), 5.7 identify cost, 5.4 Smithing XP per reforge (all PLACEHOLDER)
COST_R_DEF = {"normal": (250, 0), "unique": (500, 0), "rare": (1000, 0), "legendary": (2500, 0), "fabled": (5000, 0),
              "mythic": (10000, 0), "set": (2500, 0)}
COST_I_DEF = {"normal": (50, 5), "unique": (100, 10), "rare": (250, 20), "legendary": (500, 40), "fabled": (1000, 80),
              "mythic": (2500, 150), "set": (500, 40)}
XP_R_DEF = {"normal": 5, "unique": 10, "rare": 20, "legendary": 40, "fabled": 80, "mythic": 160, "set": 40}
# spec 1.6 migration score table (PLACEHOLDER): min score % per rarity (anything lower = normal)
MIG_DEF = {"unique": 25, "rare": 50, "legendary": 75, "fabled": 90}
MIG_IDS = ["unique", "rare", "legendary", "fabled"]
# SkyyRolls quality -> SkyyGear rarity (the cost import 1.6 and migrate.by=item)
ROLLS_QMAP = [("Junk", "normal"), ("Common", "normal"), ("Uncommon", "unique"), ("Rare", "rare"), ("Epic", "legendary"),
              ("Legendary", "fabled")]
for _r in R_IDS:
    assert _r in RARITY_DEF and _r in ODDS_DEF and _r in COST_R_DEF and _r in COST_I_DEF and _r in XP_R_DEF
    lo, hi = RARITY_DEF[_r][1], RARITY_DEF[_r][2]
    assert 0 <= lo <= hi <= 1000

# ================================================================= spec 4.2: the modifier pool (Keep rows only)
# key, label, slots (w = any gear weapon, s = spell weapon only, a = armor), unit ("%" or ""), max @100 % (PLACEHOLDER),
# weight (PLACEHOLDER), live (1 = 0.1 applies it - PART B code; 0 = "(coming later)"), suffix kind
STATS = [
    ("dmg", "Damage", "w", "%", 30, 10, 1, ""),
    ("str", "Strength", "wa", "", 25, 10, 1, ""),
    ("mp", "Magical Power", "sa", "", 25, 10, 1, "spells"),
    ("cc", "Crit Chance", "wa", "%", 15, 10, 1, ""),
    ("cd", "Crit Damage", "wa", "%", 30, 10, 1, ""),
    ("tdmg", "True Damage", "w", "", 5, 5, 1, ""),
    ("fEarth", "Earth Damage", "w", "", 6, 4, 1, ""),
    ("fThunder", "Thunder Damage", "w", "", 6, 4, 1, ""),
    ("fWater", "Water Damage", "w", "", 6, 4, 1, ""),
    ("fFire", "Fire Damage", "w", "", 6, 4, 1, ""),
    ("fAir", "Air Damage", "w", "", 6, 4, 1, ""),
    ("rThunder", "Raw Thunder Damage", "w", "", 6, 3, 1, ""),
    ("rWater", "Raw Water Damage", "w", "", 6, 3, 1, ""),
    ("rElem", "Raw Elemental Damage", "w", "", 3, 3, 1, "elem"),
    ("msteal", "Mana Steal", "s", "", 3, 5, 1, "steal"),
    ("lsteal", "Life Steal", "wa", "%", 5, 5, 1, "steal"),
    ("hpr", "Raw Health Regen", "wa", "", 2, 5, 1, "regen"),
    ("hprp", "Health Regen", "wa", "%", 20, 5, 1, "hprp"),
    ("def", "Defense", "a", "", 25, 10, 1, ""),
    ("spd", "Speed", "a", "", 5, 10, 1, ""),
    ("stam", "Stamina Regen", "a", "", 2, 5, 1, "regen"),
    ("as", "Attack Speed", "wa", "%", 10, 5, 0, ""),
    ("fer", "Ferocity", "wa", "", 10, 5, 0, ""),
    ("thorns", "Thorns", "a", "%", 10, 5, 0, ""),
    ("expl", "Exploding", "w", "%", 10, 5, 0, ""),
    ("poison", "Poison", "w", "", 20, 5, 0, ""),
    ("kb", "Knockback", "w", "%", 20, 5, 0, ""),
    ("slow", "Slow Enemy", "w", "%", 10, 5, 0, ""),
    ("weak", "Weaken Enemy", "w", "%", 10, 5, 0, ""),
    ("dEarth", "Earth Defence", "a", "", 10, 3, 0, ""),
    ("dThunder", "Thunder Defence", "a", "", 10, 3, 0, ""),
    ("dWater", "Water Defence", "a", "", 10, 3, 0, ""),
    ("dFire", "Fire Defence", "a", "", 10, 3, 0, ""),
    ("dAir", "Air Defence", "a", "", 10, 3, 0, ""),
    ("cwis", "Combat Wisdom", "wa", "%", 10, 5, 0, ""),
]
NS = len(STATS)
S_KEYS = [s[0] for s in STATS]
assert len(set(S_KEYS)) == NS, "duplicate stat key"
SPEC_KEYS = ("dmg str mp cc cd tdmg fEarth fThunder fWater fFire fAir rThunder rWater rElem msteal lsteal hpr hprp def spd stam "
             "as fer thorns expl poison kb slow weak dEarth dThunder dWater dFire dAir cwis").split()
assert S_KEYS == SPEC_KEYS, "the stat table must match spec 4.2 (keys + display order)"
for _s in STATS:
    assert re.match(r"^[a-z][a-zA-Z]*$", _s[0]) and _s[2] in ("w", "s", "a", "wa", "sa") and _s[3] in ("", "%"), _s
    assert _s[4] > 0 and _s[5] >= 0 and _s[6] in (0, 1) and _s[7] in ("", "spells", "elem", "steal", "regen", "hprp"), _s
    assert '"' not in _s[1] and "|" not in _s[1], _s
assert [s[0] for s in STATS if s[6] == 1] == SPEC_KEYS[:21], "live stats = spec 4.2 LIVE rows"

# ================================================================= spec 3.3: the gate skill per gear kind (LOCKED)
GATE_BY_KIND = [("combat", "class"), ("mining", "Mining"), ("foraging", "Foraging"), ("farming", "Farming"), ("tool", ""),
                ("equipment", "class"), ("accessory", "")]
ENFORCED_KINDS = ["combat"]
# spec 1.6 tool families of SkyyRolls-rolled tools (VERIFIED families in Assets.zip); every other Tool_* -> kind "tool", no gate
TOOL_FAMILIES = [("Tool_Pickaxe_", "mining"), ("Tool_Hatchet_", "foraging"), ("Tool_Hoe_", "farming"), ("Tool_Sickle_", "farming"),
                 ("Tool_Shovel_", "mining")]
_gk = dict(GATE_BY_KIND)
assert _gk["combat"] == "class" and _gk["mining"] == "Mining" and _gk["foraging"] == "Foraging" and _gk["farming"] == "Farming"
for _p, _k in TOOL_FAMILIES:
    assert _k in _gk, _p
    assert any(n.startswith("Server/Item/Items/") and os.path.basename(n).startswith(_p) for n in AZ_NAMES), "no Assets item " + _p
# spec 3.3: SkyyGear's own class -> weapon skill copy (tooltip text only, when SkyyClasses is absent)
CLASS_SKILLS = [("Archer", "Archery"), ("Warrior", "Swordsmanship"), ("Mage", "Sorcery"), ("Berserker", "Fury"),
                ("Priest", "Divinity"), ("Assassin", "Assassination")]
# spec 1.3: weapon prefixes that are not gear (config row gear.exclude) + the SkyyRolls AMMO tokens (code rule)
EXCLUDE_DEF = ",".join(["Weapon_Shield_", "Weapon_Bomb", "Weapon_Gun", "Weapon_Deployable_", "Weapon_Dart_", "Weapon_Claws_",
                        "Weapon_Blowgun_", "Weapon_Assault_Rifle", "Weapon_Handgun", "Weapon_Grenade_", "Weapon_Test_"])
AMMO = ["arrow", "arrows", "bolt", "bolts", "bomb", "bombs", "dart", "darts", "grenade", "grenades", "ammo", "bullet", "bullets",
        "shell", "shells", "shuriken", "shurikens", "thrown"]
SPELL_PREFIXES = ["Weapon_Staff_", "Weapon_Wand_", "Weapon_Spellbook_"]
# spec 3.2 default material table (PLACEHOLDER)
MATERIALS = [("Crude", 0), ("Wood", 0), ("Copper", 10), ("Bronze", 15), ("Iron", 20), ("Thorium", 30), ("Cobalt", 35),
             ("Adamantite", 40), ("Mithril", 50), ("Onyxium", 50)]
REFORGE_NAMES_DEF = "Sharp,Heroic,Spicy,Gentle,Odd,Fast,Epic,Withered"
for _n in REFORGE_NAMES_DEF.split(","):
    assert _n.lower() not in [x.lower() for x in R_NAMES], "reforge name is a rarity name: " + _n
PENDING_MAX_MS = 1000       # spec 1.5: a technical constant, not a balance number
SCAN_GAP_MS = 250           # spec 1.5: one coalesced stamp scan at most every 250 ms per player
VIEW_V = 1                  # spec 6.4

# ---- Assets.zip build checks (spec 11.1 #2)
AZ_ITEMS = set(os.path.basename(n)[:-5] for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))
for _tok, _lv in MATERIALS:
    assert any(("_" + _tok + "_") in ("_" + i + "_") for i in AZ_ITEMS if i.startswith(("Weapon_", "Armor_"))), "no item for " + _tok
for _kit in ("Weapon_Shortbow_Crude", "Weapon_Sword_Crude", "Weapon_Battleaxe_Crude", "Weapon_Daggers_Crude", "Weapon_Staff_Wood",
             "Weapon_Wand_Wood"):
    assert _kit in AZ_ITEMS, _kit
    _tok = next(t for t in _kit.split("_") if t in dict(MATERIALS))
    assert dict(MATERIALS)[_tok] == 0, "class kit weapon %s must resolve to level 0" % _kit


def az_texture(path):
    """a UI texture path as the client resolves it (relative to Common/UI/Custom/ or Common/, @2x variants count)"""
    for base in ("Common/UI/Custom/", "Common/"):
        p = base + path
        if p in AZ_NAMES or p[:-4] + "@2x.png" in AZ_NAMES:
            return True
    return False


for _r in RARITIES:
    for _q in (_r[4], _r[5]):
        assert ("Server/Item/Qualities/%s.json" % _q) in AZ_NAMES, _q
    assert any(n.endswith("/" + _r[6] + ".particlesystem") for n in AZ_NAMES), "no particle system " + _r[6]

# ================================================================= spec 5.8: vanilla look (values copied from Assets.zip)
# FOR THE SHARED VANILLA STYLE HELPER (RESUME step 5): move this dict there when it exists. Every entry is checked against the
# vanilla text below (Common.ui / Sounds.ui) so a game update that changes them fails the build instead of drifting silently.
# (read-only build checks against the game's own UI documents; nothing here is shipped - every page is built inline. The folder
#  and the document names are kept apart so tools/ci/lint.py's ".ui file" rule never mistakes these reads for a shipped file.)
_VDIR = "Common/" + "UI/Custom/"
_VDOC = dict(common="Common", sounds="Sounds", page="Pages/ItemRepairPage", element="Pages/ItemRepairElement")


def vdoc(k):
    return AZ.read(_VDIR + _VDOC[k] + ".u" + "i").decode("utf-8", "replace")


COMMON_UI = vdoc("common")
SOUNDS_UI = vdoc("sounds")
REPAIR_UI = vdoc("page")
REPAIR_EL = vdoc("element")
VANILLA = {
    "ColorDefault": "#ffffff", "ColorDefaultLabel": "#96a9be", "ColorGoldHighlight": "#E8A93B", "ColorGrayCaption": "#878e9c",
    "ColorDisabled": "#797b7c", "ColorButtonText": "#bfcdd5",
}
for _k, _v in VANILLA.items():
    assert ("@%s = %s;" % (_k, _v)) in COMMON_UI, "Common.ui no longer has @%s = %s" % (_k, _v)
V_TITLE_COLOR = "#b4c8c9"         # @TitleStyle TextColor (FontSize 15, Secondary font, bold, uppercase)
V_SECOND_BTN = "#bdcbd3"          # @SecondaryButtonLabelStyle TextColor
V_PANEL_TITLE = "#afc2c3"         # @PanelTitle label TextColor, line #393426(0.5)
V_SEPARATOR = "#2b3542"           # @ContentSeparator
V_ROW_HOVER = "#000000(0.2)"      # ItemRepairElement.ui row hover
V_ROW_SUB = "#ffffff(0.6)"        # ItemRepairElement.ui #Durability + the 2 px divider
for _needle in ("TextColor: #b4c8c9", "TextColor: #bdcbd3", "TextColor: #afc2c3", "Background: #393426(0.5)", "Color: #2b3542",
                "@TitleHeight = 38;", "\"Common/ContainerHeader.png\", HorizontalBorder: 50, VerticalBorder: 0",
                "\"Common/ContainerPatch.png\", Border: 23", "Anchor: (Width: 236, Height: 11, Top: -12)",
                "Anchor: (Width: 236, Height: 11, Bottom: -6)", "@ButtonBorder = 12;", "@PrimaryButtonHeight = 44;",
                "\"Common/Buttons/Primary.png\", VerticalBorder: @ButtonBorder, HorizontalBorder: 80",
                "\"Common/Buttons/Secondary.png\", Border: @ButtonBorder", "\"Common/Buttons/Destructive.png\", Border: @ButtonBorder",
                "\"Common/Scrollbar.png\", Border: 3", "\"Common/ScrollbarHandle.png\", Border: 3",
                "\"Common/ContainerVerticalSeparator.png\"", "FontSize: 17,", "RenderUppercase: true,"):
    assert _needle in COMMON_UI, "Common.ui changed: " + _needle
for _needle in ('@ButtonsLightActivate = "Sounds/ButtonsLightActivate.ogg";', '@ButtonsLightHover = "Sounds/ButtonsLightHover.ogg";',
                '@ButtonsCancelActivate = "Sounds/ButtonsCancelActivate.ogg";'):
    assert _needle in SOUNDS_UI, "Sounds.ui changed: " + _needle
assert "$C.@DecoratedContainer" in REPAIR_UI and "TopScrolling" in REPAIR_UI and "@DefaultScrollbarStyle" in REPAIR_UI
assert "Background: #000000(0.2)" in REPAIR_EL and "TextColor: #ffffff(0.6)" in REPAIR_EL and "Anchor: (Width: 32, Height: 32)" in REPAIR_EL
V_TEXTURES = ["Common/ContainerHeader.png", "Common/ContainerPatch.png", "Common/ContainerDecorationTop.png",
              "Common/ContainerDecorationBottom.png", "Common/ContainerVerticalSeparator.png", "Common/Buttons/Primary.png",
              "Common/Buttons/Primary_Hovered.png", "Common/Buttons/Primary_Pressed.png", "Common/Buttons/Disabled.png",
              "Common/Buttons/Secondary.png", "Common/Buttons/Secondary_Hovered.png", "Common/Buttons/Secondary_Pressed.png",
              "Common/Buttons/Destructive.png", "Common/Buttons/Destructive_Hovered.png", "Common/Buttons/Destructive_Pressed.png",
              "Common/Scrollbar.png", "Common/ScrollbarHandle.png", "Common/ScrollbarHandleHovered.png",
              "Common/ScrollbarHandleDragged.png"]
for _t in V_TEXTURES:
    assert az_texture(_t), "vanilla texture missing in Assets.zip: " + _t
for _snd in ("Sounds/ButtonsLightActivate.ogg", "Sounds/ButtonsLightHover.ogg", "Sounds/ButtonsCancelActivate.ogg"):
    assert ("Common/UI/Custom/" + _snd) in AZ_NAMES, _snd

# ================================================================= spec 2.1: the 7 quality assets + lang lines (jar asset pack)
EXTRA = {}
LANG = []
for _i, (_rid, _nm, _hex, _phex, _tt, _slot, _part) in enumerate(RARITIES):
    _q = {
        "QualityValue": _i + 1,
        "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % _tt,
        "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % _tt,
        "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
        "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
        "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % _slot,
        "TextColor": _hex.lower(),
        "LocalizationKey": "server.general.qualities.%s" % QUAL_IDS[_i],
        "VisibleQualityLabel": True,
        "RenderSpecialSlot": True,
        "ItemEntityConfig": {"ParticleSystemId": _part},
    }
    _vanilla_fields = set(json.loads(AZ.read("Server/Item/Qualities/Common.json").decode("utf-8")).keys())
    assert set(_q.keys()) == _vanilla_fields, "quality field set differs from vanilla Common.json: %s" % (set(_q) ^ _vanilla_fields)
    for _k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture"):
        assert az_texture(_q[_k]), "texture missing: " + _q[_k]
    EXTRA["Server/Item/Qualities/%s.json" % QUAL_IDS[_i]] = json.dumps(_q, indent=2)
    LANG.append("general.qualities.%s = %s" % (QUAL_IDS[_i], _nm))
EXTRA["Server/Languages/en-US/server.lang"] = "\n".join(LANG) + "\n"
assert "general.qualities.Common = Common" in AZ.read("Server/Languages/en-US/server.lang").decode("utf-8-sig")

# ================================================================= spec 9: config rows (tools/skyycfg.py kit 1.1) + the default file
CFG_FILE = "Skyy_SkyyGear/config.properties"
CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("stats", "Stats"), ("costs", "Costs"),
            ("drops", "Drops + craft"), ("combat", "Combat"), ("migrate", "Migration")]
PH = " Placeholder - Skyy tunes this."
_rch = ",".join("%s|%s" % (r[0], r[1]) for r in RARITIES[:6])
_mch = ",".join("%s|%s" % (r[0], r[1]) for r in RARITIES[:5])
CFG_ROWS = [
    # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("part.gate", "Level requirement check", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear above your level blocks hits and gives no stats. Off = every level passes.", "field:GearCfg.PART_GATE"),
    ("part.stats", "Gear stats in combat", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear modifiers change damage, defence, regen and speed. Off = they are only shown.", "field:GearCfg.PART_STATS"),
    ("part.craft", "Roll crafted gear", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Crafted weapons and armor roll a rarity and modifiers. Off = crafted gear is Normal.", "field:GearCfg.PART_CRAFT"),
    ("part.drops", "Unidentified mob drops", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear dropped by mobs is unidentified with a rarity. Off = mob gear drops Normal.", "field:GearCfg.PART_DROPS"),
    ("part.chests", "Unidentified chest loot", "general", "bool", "true", "", "", "", "", "live,part,danger",
     "Gear in fresh world loot chests is unidentified. Off = chest gear is Normal.", "field:GearCfg.PART_CHESTS"),
    ("identify.command", "/identify command", "general", "bool", "true", "", "", "", "", "live",
     "Players open the Identify page with /identify (switch off when an NPC does it).", "field:GearCfg.IDENTIFY_CMD"),
    ("gear.exclude", "Weapon prefixes that are not gear", "general", "text", EXCLUDE_DEF, "0", "2000", "", "", "live,adv",
     "Comma list of Weapon_ id prefixes that never get rarity or level (shields, bombs, guns ...).",
     "field:GearCfg.EXCLUDE"),
    ("ui.frames", "Vanilla frames on gear pages", "general", "bool", "true", "", "", "", "", "live,adv",
     "Reforge and Identify use the game's own frame textures and sounds. Off = flat colours.", "field:GearCfg.UI_FRAMES"),
    ("pool.later", "Roll coming-later stats", "stats", "bool", "true", "", "", "", "", "live",
     "Stats that do nothing yet (Ferocity, Thorns ...) may roll, shown grey (coming later).", "field:GearCfg.POOL_LATER"),
    ("rarity", "Modifiers and roll power by rarity", "rarity", "table", "", "0", "1000", "int;none;Mods|Low %|High %", "",
     "live,danger", "Modifier count per rarity and roll power in % of the stat max." + PH,
     "reload@%s:rarity.;check=GearCfg.checkRarity" % CFG_FILE),
    ("stat", "Stat max and weight", "stats", "table", "", "0", "100000", "int;none;Max at 100%|Weight", "", "live,danger",
     "Value at 100 % power on full-level gear, and roll weight (0 = never)." + PH,
     "reload@%s:stats.;check=GearCfg.checkStat" % CFG_FILE),
    ("stat.levelFloor", "Modifier power at item level 0", "stats", "int", "25", "1", "100", "", "%", "live,danger",
     "Level-0 gear rolls at this % of full power (100 = no level scaling)." + PH, "field:GearCfg.LEVEL_FLOOR"),
    ("stat.levelFull", "Item level with full modifier power", "stats", "int", "50", "1", "100", "", "", "live,danger",
     "Gear of this level or higher rolls at full power." + PH, "field:GearCfg.LEVEL_FULL"),
    ("odds", "Rarity odds (weights)", "drops", "table", "", "0", "1000000", "dec;none;Craft|Mob|Chest", "", "live,danger",
     "Weights per rarity for crafted gear, mob drops and loot chests." + PH,
     "reload@%s:odds.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("smith.perLevel", "Smithing rarity per level", "drops", "dec", "0.5", "0", "100", "", "%", "live,danger",
     "Chance per Smithing level that a crafted item steps up one rarity." + PH, "field:GearCfg.SMITH_PER"),
    ("smith.cap", "Smithing rarity cap", "drops", "dec", "50", "0", "100", "", "%", "live,danger",
     "The Smithing step-up chance never goes above this." + PH, "field:GearCfg.SMITH_CAP"),
    ("craft.maxRarity", "Best rarity from crafting", "drops", "choice", "fabled", "", "", _rch, "", "live,danger",
     "Crafting (Smithing included) never makes a better rarity than this.", "field:GearCfg.CRAFT_MAX"),
    ("level.material", "Level by material", "levels", "table", "", "0", "100", "int;type;Level", "", "live",
     "Level for gear of this material (first matching word of the id)." + PH,
     "reload@%s:level.material." % CFG_FILE),
    ("level.item", "Level by item", "levels", "table", "", "0", "100", "int;held;Level", "", "live",
     "Level needed for one exact item (hold it to add). Wins over the material table.",
     "reload@%s:level.item.;entry=item" % CFG_FILE),
    ("level.vanilla", "Use Hytale item level otherwise", "levels", "bool", "true", "", "", "", "", "live",
     "Gear without a table entry uses the game's own item level (0-100).", "field:GearCfg.LEVEL_VANILLA"),
    ("level.default", "Level when nothing matches", "levels", "int", "0", "0", "100", "", "", "live",
     "Level for gear that matches no table and has no Hytale level.", "field:GearCfg.LEVEL_DEFAULT"),
    ("level.noSkills", "Without SkyySkills", "levels", "choice", "pass", "", "", "pass|Allow all,block|Block", "", "live",
     "When SkyySkills is missing the level cannot be checked: allow all gear or block it.", "field:GearCfg.NO_SKILLS"),
    ("level.armorNative", "Under-level armor loses Hytale stats", "levels", "bool", "true", "", "", "", "", "live",
     "Armor above your level also loses its own Health and protection (off = only SkyyGear stats).",
     "field:GearCfg.ARMOR_NATIVE"),
    ("cost.reforge", "Reforge cost", "costs", "table", "", "0", "1000000000000", "int;none;Base|Per level", "coins",
     "live,danger", "Coins per reforge by rarity: base + per level x item level." + PH,
     "reload@%s:cost.reforge.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("cost.identify", "Identify cost", "costs", "table", "", "0", "1000000000000", "int;none;Base|Per level", "coins",
     "live,danger", "Coins per identify by rarity: base + per level x item level." + PH,
     "reload@%s:cost.identify.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("xp.reforge", "Smithing XP per reforge", "costs", "table", "", "0", "100000", "int;none;XP", "", "live,danger",
     "Smithing XP a reforge gives, by rarity (SkyySkills caps apply)." + PH,
     "reload@%s:xp.reforge.;check=GearCfg.checkRarityKey" % CFG_FILE),
    ("reforge.names", "Reforge names", "costs", "text", REFORGE_NAMES_DEF, "0", "2000", "", "", "live",
     "Comma list of cosmetic reforge prefixes. Never a rarity name.", "field:GearCfg.NAMES;check=GearCfg.checkNames"),
    ("combat.strPer", "Damage per Strength", "combat", "dec", "1", "0", "100", "", "%", "live,danger",
     "Each Strength point adds this % to physical hits." + PH, "field:GearCfg.STR_PER"),
    ("combat.mpPer", "Spell damage per Magical Power", "combat", "dec", "1", "0", "100", "", "%", "live,danger",
     "Each Magical Power point adds this % to spell hits." + PH, "field:GearCfg.MP_PER"),
    ("combat.defScale", "Defense curve (100 = SkyBlock)", "combat", "int", "100", "1", "100000", "", "", "live,danger",
     "Damage taken x scale / (scale + Defense)." + PH, "field:GearCfg.DEF_SCALE"),
    ("crit.base", "Base Crit Chance", "combat", "dec", "0", "0", "1000", "", "%", "live,danger",
     "Crit Chance every player has without gear." + PH, "field:GearCfg.CRIT_BASE"),
    ("crit.baseDamage", "Base Crit Damage", "combat", "dec", "0", "0", "10000", "", "%", "live,danger",
     "Crit Damage every player has without gear (a crit doubles first)." + PH, "field:GearCfg.CRIT_BASE_DMG"),
    ("steal.windowS", "Life / Mana Steal window", "combat", "int", "3", "1", "60", "", "s", "live",
     "Life Steal and Mana Steal pay out at most once per this many seconds.", "field:GearCfg.STEAL_S"),
    ("regen.periodMs", "Regen tick", "combat", "int", "2000", "250", "60000", "", "ms", "live",
     "Health Regen and Stamina Regen from gear apply once per this many ms.", "field:GearCfg.REGEN_MS"),
    ("speed.per", "Speed per point", "combat", "dec", "1", "0", "100", "", "%", "live,danger",
     "Each Speed point adds this % of the default walk speed." + PH, "field:GearCfg.SPEED_PER"),
    ("migrate.by", "Old SkyyRolls rarity from", "migrate", "choice", "stats", "", "",
     "stats|Roll strength,roll|Roll quality,item|Item colour", "", "new,danger",
     "How an old SkyyRolls item gets its rarity on the move (stats = how strong its rolls are).",
     "field:GearCfg.MIGRATE_BY"),
    ("migrate.map", "Score needed per rarity", "migrate", "table", "", "0", "100", "int;none;Min score %", "", "new,danger",
     "Old SkyyRolls score (0-100) needed for each rarity; lower = Normal." + PH,
     "reload@%s:migrate.map.;check=GearCfg.checkMigKey" % CFG_FILE),
    ("migrate.maxRarity", "Best rarity for old SkyyRolls items", "migrate", "choice", "fabled", "", "", _mch, "", "new,danger",
     "An old SkyyRolls item never moves over better than this (never Mythic or Set).", "field:GearCfg.MIGRATE_MAX"),
]
_bad = ["%s help %d" % (_r[0], len(_r[10])) for _r in CFG_ROWS if len(_r[10]) > 100] +        ["%s label %d" % (_r[0], len(_r[1])) for _r in CFG_ROWS if len(_r[1]) > 40]
assert not _bad, "config row text too long: %s" % _bad
# spec 9.2: every row on the LOCKED confirm list carries danger (money, rates, caps, curves, part switches)
_DANGER = {"part.gate", "part.stats", "part.craft", "part.drops", "part.chests", "rarity", "stat", "stat.levelFloor", "stat.levelFull",
           "odds", "smith.perLevel", "smith.cap", "craft.maxRarity", "cost.reforge", "cost.identify", "xp.reforge", "combat.strPer",
           "combat.mpPer", "combat.defScale", "crit.base", "crit.baseDamage", "speed.per", "migrate.by", "migrate.map",
           "migrate.maxRarity"}
for _r in CFG_ROWS:
    assert (("danger" in _r[9].split(",")) == (_r[0] in _DANGER)), "danger flag mismatch: " + _r[0]


def _dn(x):
    return str(int(x)) if float(x) == int(x) else repr(float(x))


def default_text():
    L = ["# SkyyGear %s - Server Setup -> Gear (SkyWynn Menu, /modconfig). Every number is a PLACEHOLDER Skyy tunes in game." % VERSION,
         "# Changed in game: only the changed line is rewritten, logged in config-changes.log and versioned in config-history/.",
         "# Hand edits apply on Reload in Server Setup or at the next start. Tables: <prefix><entry>=<col1>,<col2>,...", ""]
    rows = dict((r[0], r) for r in CFG_ROWS)
    def scal(k):
        L.append("# %s: %s" % (rows[k][1], rows[k][10]))
        L.append("%s=%s" % (k, rows[k][4]))
    L.append("# ---- general ----")
    for k in ("part.gate", "part.stats", "part.craft", "part.drops", "part.chests", "identify.command", "gear.exclude", "ui.frames"):
        scal(k)
    L += ["", "# ---- rarity: rarity.<id>=<modifiers>,<low %>,<high %> (spec 2.2) ----"]
    for r in R_IDS:
        L.append("rarity.%s=%d,%d,%d" % ((r,) + RARITY_DEF[r]))
    L += ["", "# ---- stats: stats.<key>=<max at 100 % power>,<weight> (spec 4.2; weight 0 = never rolls) ----"]
    for s in STATS:
        L.append("stats.%s=%d,%d" % (s[0], s[4], s[5]))
    for k in ("pool.later", "stat.levelFloor", "stat.levelFull"):
        scal(k)
    L += ["", "# ---- odds: odds.<id>=<craft>,<mob>,<chest> (weights, spec 5.3 / 5.5) ----"]
    for r in R_IDS:
        L.append("odds.%s=%s" % (r, ",".join(_dn(x) for x in ODDS_DEF[r])))
    for k in ("smith.perLevel", "smith.cap", "craft.maxRarity"):
        scal(k)
    L += ["", "# ---- levels (spec 3.1-3.2): level.material.<first matching id word>=<level>, level.item.<item id>=<level> ----"]
    for t, lv in MATERIALS:
        L.append("level.material.%s=%d" % (t, lv))
    for k in ("level.vanilla", "level.default", "level.noSkills", "level.armorNative"):
        scal(k)
    L += ["", "# ---- costs: cost.<reforge|identify>.<id>=<base coins>,<coins per item level>; xp.reforge.<id>=<Smithing XP> ----"]
    for r in R_IDS:
        L.append("cost.reforge.%s=%d,%d" % ((r,) + COST_R_DEF[r]))
    for r in R_IDS:
        L.append("cost.identify.%s=%d,%d" % ((r,) + COST_I_DEF[r]))
    for r in R_IDS:
        L.append("xp.reforge.%s=%d" % (r, XP_R_DEF[r]))
    scal("reforge.names")
    L += ["", "# ---- combat (PART B applies these; spec 4.3) ----"]
    for k in ("combat.strPer", "combat.mpPer", "combat.defScale", "crit.base", "crit.baseDamage", "steal.windowS", "regen.periodMs",
              "speed.per"):
        scal(k)
    L += ["", "# ---- migration of old SkyyRolls items (spec 1.6): migrate.map.<id>=<min score %> ----"]
    scal("migrate.by")
    for r in MIG_IDS:
        L.append("migrate.map.%s=%d" % (r, MIG_DEF[r]))
    scal("migrate.maxRarity")
    return "\n".join(L) + "\n"


DEFAULT_TEXT = default_text()
_dp = CFG.parse_props(DEFAULT_TEXT)
for _r in CFG_ROWS:
    if _r[3] != "table":
        assert _dp.get(_r[0]) == _r[4], "default file and row default differ: " + _r[0]

# ================================================================= classes (methods before callers; one registerSystem per class)
def mk(name, sup=None):
    return pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)


gu   = mk("Gear")            # util: log, bridge, busy, epoch, pkey, text helpers
gdf  = mk("GearDefs")        # tables generated from the Python lists above
gcf  = mk("GearCfg")         # config fields (kit-bound) + tables + loader + checks
glg  = mk("GearLog")         # gear.log (queued, rotated at 5 MB)
gdt  = mk("GearData")        # the gear document: id rules, read, migrate, write
glv  = mk("GearLevel")       # level lookup + level factor
grl  = mk("GearRoll")        # SecureRandom rolls: rarity, modifiers, reforge, identify, crafted gear
ggt  = mk("GearGate")        # gate skill + level cache + popup helper (PART B enforcement uses it)
gvw  = mk("GearView")        # tooltip (ItemDisplayMetadata) + plain lines + sigs
gst  = mk("GearStats")       # active totals (PART B applies them)
gnt  = mk("GearNotice")      # players/<pkey>.properties noticeShown
gsp  = mk("GearStamp")       # legacy stamp / migration / re-render scan + pending crafts
gspt = mk("GearStampTask")   # coalesced scan task (scheduler -> world thread)
gfg  = mk("GearForge")       # the reforge core (page + /gear reroll), write safety 1.7
gfn  = mk("GearFn")          # bridge functions (one class, a mode per key)
ginv = mk("GearInvSys", EES)     # InventoryChangeEvent -> dirty
gthr = mk("GearThrowSys", EES)   # DropItemEvent$Drop -> stamp the thrown stack (spec 1.5)
gcrs = mk("GearCraftSys", EES)   # CraftRecipeEvent$Post -> pending + roll task (spec 5.1)
gcrt = mk("GearCraftTask")
gtk  = mk("GearTick", ETS)       # 1 s per player: level re-read -> re-render; PART B stat effects plug in here
grft = mk("GearRefreshTask")     # PlayerReadyEvent refresh (waits out profile:busy, 15 tries)
grdy = mk("GearReady")
gui  = mk("GearUi")              # vanilla style snippets (for the shared helper, RESUME step 5)
rpg  = mk("ReforgePage", PAGE)
rfc  = mk("ReforgeCmd", APC)
gad  = mk("GearAdmin")           # /gear sub-command bodies
gcm  = mk("GearCmd", APC)
SUBS = [("give", "GearGiveCmd", "Give gear: /gear give <item> [--rarity <id>] [--unid true]", True),
        ("read", "GearReadCmd", "Show the gear document and raw metadata of the held item", False),
        ("reroll", "GearRerollCmd", "Free reforge of the held item", False),
        ("clear", "GearClearCmd", "Remove SkyyGear data from the held item (it becomes Normal again)", False),
        ("rarity", "GearRarityCmd", "Set the held item's rarity: /gear rarity <id>", True),
        ("unid", "GearUnidCmd", "Make the held item unidentified (keeps its rarity)", False),
        ("identify", "GearIdentifyCmd", "Identify the held item for free", False),
        ("level", "GearLevelCmd", "Set or clear the held item's level: /gear level <n|clear>", True),
        ("gate", "GearGateCmd", "Set the held item's gate skill: /gear gate <skill|class>", True),
        ("migrate", "GearMigrateCmd", "Run the stamp / migration scan now: /gear migrate [player]", True)]
subc = dict((s[0], mk(s[1], APC)) for s in SUBS)
pl   = mk("SkyyGearPlugin", JP)

# ---------------------------------------------------------------- PART B PLUGS IN HERE (1/4): its classes
# PART B appends (CtClass, "note") tuples here after creating them with mk(...) further down (or in its own section before the
# plugin is compiled); they are written with the rest. Planned names (spec Appendix A): GearShotTrack, GearHitSys, GearArmorSys,
# GearTrueSys, GearLeechSys, GearDeathMark, GearDropSys, GearChestMark, GearChestTag, IdentifyPage, IdentifyCmd.
PARTB_CLASSES = []
# ---------------------------------------------------------------- PART B PLUGS IN HERE (2/4): lines inside setup()
# Java statements (with @TOKENS@) PART B needs in SkyyGearPlugin.setup(), after SkyyGear's own systems and commands, before the
# bridge + kit publish: registerSystem calls (ordered with SystemDependency + unordered fallback + one WARN, spec 5.5), the
# /identify command (only when GearCfg.IDENTIFY_CMD at start), ...
PARTB_SETUP = []
# ---------------------------------------------------------------- PART B PLUGS IN HERE (3/4): GearTick body
# Java statements run once per second per player inside GearTick.tick after the level refresh. In scope: dt, idx, chunk, store,
# cb, ref (Ref), p (Player), pr (PlayerRef), u (UUID), w (World), inv (Inventory), ss (String: this second's active totals, already
# published as gear:stats:<uuid> by PART A). Spec 3.5 / 4.2: armor lock modifiers, regen, stamina, speed (skyymove).
PARTB_TICK = ""

# ================================================================= GearLog: gear.log (spec 8.2), queued, written on the scheduler
glg.addInterface(pool.get("java.lang.Runnable"))
F(glg, "public static final java.util.concurrent.ConcurrentLinkedQueue Q = new java.util.concurrent.ConcurrentLinkedQueue();")
F(glg, "public static volatile boolean SCHED = false;")
F(glg, "public static volatile java.nio.file.Path FILE;")
F(glg, "public static volatile boolean FAILED = false;")
C(glg, "public GearLog() { }")
M(glg, r"""
public static synchronized void flush() {
  SCHED = false;
  java.nio.file.Path f = FILE;
  if (f == null) { Q.clear(); return; }
  StringBuilder sb = new StringBuilder();
  Object o = Q.poll();
  while (o != null) { sb.append((String) o).append('\n'); o = Q.poll(); }
  if (sb.length() == 0) return;
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0]) && java.nio.file.Files.size(f) > 5242880L) {
      java.nio.file.Files.move(f, f.resolveSibling(f.getFileName().toString() + ".1"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    }
    java.nio.file.Files.write(f, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { if (!FAILED) { FAILED = true; System.err.println("[SkyyGear] could not write gear.log: " + t); } }
}""")
M(glg, "public void run() { flush(); }")
M(glg, r"""
public static synchronized void kick() {
  if (SCHED) return;
  SCHED = true;
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearLog(), 500L, java.util.concurrent.TimeUnit.MILLISECONDS); }
  catch (Throwable t) { SCHED = false; }
}""")
M(glg, r"""
public static void line(String s) {
  if (FILE == null || s == null) return;
  String ts = "";
  try { ts = java.time.LocalDateTime.now().withNano(0).toString(); } catch (Throwable t) { ts = String.valueOf(System.currentTimeMillis()); }
  Q.add(ts + " " + s.replace('\n', ' '));
  kick();
}""")

# ================================================================= Gear (util)
F(gu, "public static @LOG@ LOG;")
F(gu, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(gu, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyGear] " + msg); } catch (Throwable t) { }
  try { @PKG@.GearLog.line("WARN " + msg); } catch (Throwable t2) { }
}""")
M(gu, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyGear] " + msg); } catch (Throwable t) { }
}""")
M(gu, r"""
public static boolean once(String key) {
  if (key == null) return false;
  return ONCE.putIfAbsent(key, Boolean.TRUE) == null;
}""")
M(gu, r"""
public static void warnOnce(String key, String msg) {
  if (once(key)) warn(msg + " (logged once)");
}""")
M(gu, r"""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
M(gu, r"""
public static Object bget(String k) {
  try { return bridge().get(k); } catch (Throwable t) { return null; }
}""")
M(gu, r"""
public static java.util.function.Function fn(String k) {
  Object o = bget(k);
  return o instanceof java.util.function.Function ? (java.util.function.Function) o : null;
}""")
M(gu, r"""
public static boolean busy(java.util.UUID u) {
  return u != null && bget("profile:busy:" + u) != null;
}""")
M(gu, r"""
public static String epoch(java.util.UUID u) {
  Object e = u == null ? null : bget("profile:epoch:" + u);
  return e == null ? "" : String.valueOf(e);
}""")
# the contract's helper (tools/PROFILES-CONTRACT.md)
M(gu, r"""
public static String pkey(java.util.UUID u) {
  try {
    java.util.function.Function f = fn("profile:fn:key");
    if (f != null) {
      Object r = f.apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u == null ? "" : u.toString();
}""")
M(gu, r"""
public static String fmt(long n) {
  String s = String.valueOf(n < 0L ? -n : n);
  StringBuilder sb = new StringBuilder();
  int c = 0;
  for (int i = s.length() - 1; i >= 0; i--) {
    sb.append(s.charAt(i));
    c++;
    if (c % 3 == 0 && i > 0) sb.append(',');
  }
  if (n < 0L) sb.append('-');
  return sb.reverse().toString();
}""")
M(gu, r"""
public static String fnum(double f) {
  long r = Math.round(f);
  if (Math.abs(f - (double) r) < 0.05) return String.valueOf(r);
  return String.valueOf(Math.round(f * 10.0) / 10.0);
}""")
# en-US text of a translation key, null when missing (SkyyRolls tr)
M(gu, r"""
public static String tr(String key) {
  if (key == null) return null;
  try {
    @I18N@ m = @I18N@.get();
    if (m == null) return null;
    String s = m.getMessage("en-US", key);
    if (s == null || s.trim().length() == 0 || s.equals(key)) return null;
    return s;
  } catch (Throwable t) { return null; }
}""")
M(gu, r"""
public static @ITM@ item(String id) {
  if (id == null) return null;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    return o instanceof @ITM@ ? (@ITM@) o : null;
  } catch (Throwable t) { return null; }
}""")
M(gu, r"""
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id;
  if (s.startsWith("Weapon_")) s = s.substring(7);
  else if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Tool_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
M(gu, r"""
public static String itemName(String id) {
  String n = null;
  try { @ITM@ it = item(id); if (it != null) n = tr(it.getTranslationKey()); } catch (Throwable t) { n = null; }
  if (n != null && n.indexOf(123) < 0) return n;
  return pretty(id);
}""")
M(gu, r"""
public static String hex(@PCOL@ c) {
  if (c == null) return null;
  return "#" + Integer.toHexString(256 | (c.red & 255)).substring(1) + Integer.toHexString(256 | (c.green & 255)).substring(1)
    + Integer.toHexString(256 | (c.blue & 255)).substring(1);
}""")
M(gu, r"""
public static int quality(@IS@ s) {
  try { return s == null ? Integer.MIN_VALUE : s.getQualityIndex(); } catch (Throwable t) { return Integer.MIN_VALUE; }
}""")
M(gu, r"""
public static boolean admin(java.util.UUID u) {
  try { return u != null && @PERM@.get().hasPermission(u, "skyygear.admin"); } catch (Throwable t) { return false; }
}""")
# one string value out of the page event JSON (SkyyRolls ReforgePage.jsonStr)
M(gu, r"""
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
M(gu, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")

# ================================================================= GearDefs (generated tables)
F(gdf, "public static final String[] R_ID = %s;" % jarr(R_IDS))
F(gdf, "public static final String[] R_NAME = %s;" % jarr(R_NAMES))
F(gdf, "public static final String[] R_HEX = %s;" % jarr([r[2] for r in RARITIES]))
F(gdf, "public static final String[] R_PAGEHEX = %s;" % jarr([r[3] for r in RARITIES]))
F(gdf, "public static final String[] R_QID = %s;" % jarr(QUAL_IDS))
F(gdf, "public static final int NR = %d;" % NR)
F(gdf, "public static final int NS = %d;" % NS)
F(gdf, "public static final String[] S_KEY = %s;" % jarr(S_KEYS))
F(gdf, "public static final String[] S_LABEL = %s;" % jarr([s[1] for s in STATS]))
F(gdf, "public static final String[] S_SLOT = %s;" % jarr([s[2] for s in STATS]))
F(gdf, "public static final String[] S_UNIT = %s;" % jarr([s[3] for s in STATS]))
F(gdf, "public static final int[] S_MAXDEF = %s;" % jints([s[4] for s in STATS]))
F(gdf, "public static final int[] S_WDEF = %s;" % jints([s[5] for s in STATS]))
F(gdf, "public static final int[] S_LIVE = %s;" % jints([s[6] for s in STATS]))
F(gdf, "public static final String[] S_SUF = %s;" % jarr([s[7] for s in STATS]))
F(gdf, "public static final String[] KINDS = %s;" % jarr([k for k, g in GATE_BY_KIND]))
F(gdf, "public static final String[] KIND_GATE = %s;" % jarr([g for k, g in GATE_BY_KIND]))
F(gdf, "public static final String[] ENFORCED = %s;" % jarr(ENFORCED_KINDS))
F(gdf, "public static final String[] TF_PRE = %s;" % jarr([p for p, k in TOOL_FAMILIES]))
F(gdf, "public static final String[] TF_KIND = %s;" % jarr([k for p, k in TOOL_FAMILIES]))
F(gdf, "public static final String[] CL_NAME = %s;" % jarr([c for c, s in CLASS_SKILLS]))
F(gdf, "public static final String[] CL_SKILL = %s;" % jarr([s for c, s in CLASS_SKILLS]))
F(gdf, "public static final String[] AMMO = %s;" % jarr(AMMO))
F(gdf, "public static final String[] SPELL = %s;" % jarr(SPELL_PREFIXES))
F(gdf, "public static final String[] RQ_FROM = %s;" % jarr([a for a, b in ROLLS_QMAP]))
F(gdf, "public static final String[] RQ_TO = %s;" % jarr([b for a, b in ROLLS_QMAP]))
F(gdf, "public static final String[] MIG_ID = %s;" % jarr(MIG_IDS))
# spec 7.1 gear:gates = the combat + gathering kinds only (equipment / tool / accessory stay internal until their stages exist)
GATES_PUB = ",".join("%s:%s" % (k, g) for k, g in GATE_BY_KIND if k in ("combat", "mining", "foraging", "farming"))
assert GATES_PUB == "combat:class,mining:Mining,foraging:Foraging,farming:Farming", GATES_PUB
F(gdf, "public static final String GATES = %s;" % jstr(GATES_PUB))
F(gdf, "public static final String TIERS = %s;" % jstr(",".join("%s:%s:%s" % (r[0], r[1], r[2]) for r in RARITIES)))
F(gdf, "public static final int VIEW_V = %d;" % VIEW_V)
F(gdf, 'public static final String DOC_KEY = "SkyyGear";')
F(gdf, 'public static final String VIEW_KEY = "SkyyGearView";')
F(gdf, 'public static final String ROLLS_KEY = "SkyyRolls";')
F(gdf, 'public static final String ROLLS_VIEW = "SkyyRollsView";')
F(gdf, "public static final long PENDING_MAX_MS = %dL;" % PENDING_MAX_MS)
F(gdf, "public static final long SCAN_GAP_MS = %dL;" % SCAN_GAP_MS)
# vanilla palette (spec 5.8 / 6.4); FOR THE SHARED STYLE HELPER (RESUME step 5)
F(gdf, 'public static final String C_GRAY = "#878e9c";')      # @ColorGrayCaption: vanilla description, (coming later)
F(gdf, 'public static final String C_LABEL = "#96a9be";')     # @ColorDefaultLabel
F(gdf, 'public static final String C_GOLD = "#E8A93B";')      # @ColorGoldHighlight: costs
F(gdf, 'public static final String C_DIS = "#797b7c";')       # @ColorDisabled
F(gdf, 'public static final String C_OK = "#55FF55";')        # gate line green (Wynn) until step 5 names a vanilla success colour
F(gdf, 'public static final String C_BAD = "#FF5555";')       # gate line red (Wynn)
M(gdf, r"""
public static int rIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < R_ID.length; i++) if (R_ID[i].equalsIgnoreCase(id.trim())) return i;
  for (int i = 0; i < R_NAME.length; i++) if (R_NAME[i].equalsIgnoreCase(id.trim())) return i;
  return -1;
}""")
M(gdf, r"""
public static int sIndex(String key) {
  if (key == null) return -1;
  for (int i = 0; i < S_KEY.length; i++) if (S_KEY[i].equals(key)) return i;
  return -1;
}""")
M(gdf, r"""
public static String kindGate(String kind) {
  if (kind == null) return "class";
  for (int i = 0; i < KINDS.length; i++) if (KINDS[i].equals(kind)) return KIND_GATE[i];
  return "";
}""")
M(gdf, r"""
public static boolean enforcedKind(String kind) {
  if (kind == null) return true;
  for (int i = 0; i < ENFORCED.length; i++) if (ENFORCED[i].equals(kind)) return true;
  return false;
}""")
M(gdf, r"""
public static String classSkill(String cls) {
  if (cls == null) return null;
  for (int i = 0; i < CL_NAME.length; i++) if (CL_NAME[i].equalsIgnoreCase(cls)) return CL_SKILL[i];
  return null;
}""")
# quality asset index per rarity (resolved once; -1 = the plugin quality asset is not loaded -> fallback 2.1: name colour only)
F(gdf, "public static volatile int[] QIDX = null;")
F(gdf, "public static volatile long QMISS = 0L;")
M(gdf, r"""
public static int qIndex(int r) {
  int[] q = QIDX;
  if (q == null || (QMISS > 0L && System.currentTimeMillis() - QMISS > 60000L)) {
    q = new int[R_QID.length];
    boolean miss = false;
    for (int i = 0; i < R_QID.length; i++) {
      q[i] = -1;
      try {
        int ix = @IQ@.getAssetMap().getIndex(R_QID[i]);
        Object a = ix < 0 ? null : @IQ@.getAssetMap().getAsset(ix);
        if (a instanceof @IQ@ && R_QID[i].equals(((@IQ@) a).getId())) q[i] = ix;
      } catch (Throwable t) { q[i] = -1; }
      if (q[i] < 0) miss = true;
    }
    if (miss) @PKG@.Gear.warnOnce("qual", "the Skyy_Gear_* quality assets were not found - items keep their own quality frame and only the name takes the rarity colour (spec 2.1 fallback)");
    QMISS = miss ? System.currentTimeMillis() : 0L;
    QIDX = q;
  }
  if (r < 0 || r >= q.length) return -1;
  return q[r];
}""")

# ================================================================= GearCfg fields (kit-bound fields must exist before emit)
CFG_FIELDS = [("PART_GATE", "boolean", "true"), ("PART_STATS", "boolean", "true"), ("PART_CRAFT", "boolean", "true"),
              ("PART_DROPS", "boolean", "true"), ("PART_CHESTS", "boolean", "true"), ("IDENTIFY_CMD", "boolean", "true"),
              ("EXCLUDE", "String", jstr(EXCLUDE_DEF)), ("UI_FRAMES", "boolean", "true"), ("POOL_LATER", "boolean", "true"),
              ("LEVEL_FLOOR", "int", "25"), ("LEVEL_FULL", "int", "50"), ("SMITH_PER", "double", "0.5"),
              ("SMITH_CAP", "double", "50.0"), ("CRAFT_MAX", "String", '"fabled"'), ("LEVEL_VANILLA", "boolean", "true"),
              ("LEVEL_DEFAULT", "int", "0"), ("NO_SKILLS", "String", '"pass"'), ("ARMOR_NATIVE", "boolean", "true"),
              ("NAMES", "String", jstr(REFORGE_NAMES_DEF)), ("STR_PER", "double", "1.0"), ("MP_PER", "double", "1.0"),
              ("DEF_SCALE", "int", "100"), ("CRIT_BASE", "double", "0.0"), ("CRIT_BASE_DMG", "double", "0.0"),
              ("STEAL_S", "int", "3"), ("REGEN_MS", "int", "2000"), ("SPEED_PER", "double", "1.0"),
              ("MIGRATE_BY", "String", '"stats"'), ("MIGRATE_MAX", "String", '"fabled"')]
for _n, _t, _v in CFG_FIELDS:
    F(gcf, "public static volatile %s %s = %s;" % (_t, _n, _v))
# tables (set by load(); not kit fields)
F(gcf, "public static volatile int[] R_MODS = %s;" % jints([RARITY_DEF[r][0] for r in R_IDS]))
F(gcf, "public static volatile int[] R_LO = %s;" % jints([RARITY_DEF[r][1] for r in R_IDS]))
F(gcf, "public static volatile int[] R_HI = %s;" % jints([RARITY_DEF[r][2] for r in R_IDS]))
F(gcf, "public static volatile int[] S_MAX = %s;" % jints([s[4] for s in STATS]))
F(gcf, "public static volatile int[] S_W = %s;" % jints([s[5] for s in STATS]))
for _col, _nm in ((0, "O_CRAFT"), (1, "O_MOB"), (2, "O_CHEST")):
    F(gcf, "public static volatile double[] %s = new double[] { %s };" % (_nm, ", ".join(repr(float(ODDS_DEF[r][_col])) for r in R_IDS)))
F(gcf, "public static final double[] OD_CRAFT = new double[] { %s };" % ", ".join(repr(float(ODDS_DEF[r][0])) for r in R_IDS))
F(gcf, "public static final double[] OD_MOB = new double[] { %s };" % ", ".join(repr(float(ODDS_DEF[r][1])) for r in R_IDS))
F(gcf, "public static final double[] OD_CHEST = new double[] { %s };" % ", ".join(repr(float(ODDS_DEF[r][2])) for r in R_IDS))
for _nm, _tbl, _col in (("CR_BASE", COST_R_DEF, 0), ("CR_PER", COST_R_DEF, 1), ("CI_BASE", COST_I_DEF, 0), ("CI_PER", COST_I_DEF, 1)):
    F(gcf, "public static volatile long[] %s = new long[] { %s };" % (_nm, ", ".join("%dL" % _tbl[r][_col] for r in R_IDS)))
    F(gcf, "public static final long[] D%s = new long[] { %s };" % (_nm, ", ".join("%dL" % _tbl[r][_col] for r in R_IDS)))
F(gcf, "public static volatile long[] XPR = new long[] { %s };" % ", ".join("%dL" % XP_R_DEF[r] for r in R_IDS))
F(gcf, "public static final long[] DXPR = new long[] { %s };" % ", ".join("%dL" % XP_R_DEF[r] for r in R_IDS))
F(gcf, "public static volatile int[] MIG = %s;" % jints([MIG_DEF[r] for r in MIG_IDS]))
F(gcf, "public static final int[] DMIG = %s;" % jints([MIG_DEF[r] for r in MIG_IDS]))
F(gcf, "public static final int[] DR_MODS = %s;" % jints([RARITY_DEF[r][0] for r in R_IDS]))
F(gcf, "public static final int[] DR_LO = %s;" % jints([RARITY_DEF[r][1] for r in R_IDS]))
F(gcf, "public static final int[] DR_HI = %s;" % jints([RARITY_DEF[r][2] for r in R_IDS]))
F(gcf, "public static final String[] MAT_T = %s;" % jarr([t for t, l in MATERIALS]))
F(gcf, "public static final int[] MAT_L = %s;" % jints([l for t, l in MATERIALS]))
F(gcf, "public static volatile java.util.HashMap MAT = new java.util.HashMap();")
F(gcf, "public static volatile java.util.HashMap ITEMLVL = new java.util.HashMap();")
F(gcf, "public static volatile long EPOCH = 0L;")
F(gcf, "public static volatile java.nio.file.Path FILE;")
F(gcf, "public static volatile java.nio.file.Path DIR;")
F(gcf, "public static volatile String EXCL_SRC = null;")
F(gcf, "public static volatile String[] EXCL = new String[0];")
F(gcf, "public static volatile String NAMES_SRC = null;")
F(gcf, "public static volatile String[] RF = new String[0];")

kit = CFG.emit(pool, PKG, MOD="SkyyGear", TITLE="Gear", VERSION=VERSION, NODE="skyygear.admin", CATS=CFG_CATS, ROWS=CFG_ROWS,
               FILES=[CFG_FILE], NOTE="Every number is a placeholder. Tables apply at once; hand edits on Reload.",
               RELOAD="GearCfg.load", KEEP=10, DEFAULTS={CFG_FILE: DEFAULT_TEXT})

# ================================================================= Gear: settings registry helpers (research/Settings-Spec.md 1.3)
M(gu, r"""
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    java.util.function.Function f = fn("settings:fn:get");
    if (f != null) {
      Object r = f.apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
M(gu, r"""
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyGear", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")

# ================================================================= GearCfg: loader, SkyyRolls cost import, checks, costs
M(gcf, "public static String defaultsText() { return " + jlit(DEFAULT_TEXT) + "; }")
M(gcf, r"""
public static void writeAtomic(java.nio.file.Path dst, String text, boolean replace) throws Exception {
  java.nio.file.Files.createDirectories(dst.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dst.resolveSibling(dst.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, text.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
  Throwable last = null;
  int i = 0;
  while (i < 5) {
    try {
      if (replace) java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      else java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[0]);
      return;
    } catch (java.nio.file.FileAlreadyExistsException ae) {
      try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable d1) { }
      return;
    } catch (java.nio.file.FileSystemException fe) {
      last = fe;
      i++;
    } catch (Throwable t) {
      last = t;
      i = 5;
    }
    if (i < 5) { try { Thread.sleep(20L); } catch (Throwable ie) { } }
  }
  try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable d2) { }
  throw new java.io.IOException("could not write " + dst + ": " + last);
}""")
M(gcf, r"""
public static java.util.Properties read(java.nio.file.Path f) throws Exception {
  java.util.Properties p = new java.util.Properties();
  java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
  try { p.load(in); } finally { in.close(); }
  return p;
}""")
M(gcf, r"""
public static String clean(String v) {
  if (v == null) return null;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length(); i++) { char c = v.charAt(i); if (c != ',' && c != ' ' && c != '_' && c != '%') sb.append(c); }
  return sb.toString();
}""")
M(gcf, r"""
public static boolean pbool(java.util.Properties p, String k, boolean def) {
  String v = p.getProperty(k);
  if (v == null) return def;
  v = v.trim().toLowerCase();
  if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return false;
  @PKG@.Gear.warn("config.properties: " + k + "=" + v + " is not true/false - the default is used");
  return def;
}""")
M(gcf, r"""
public static long plong(java.util.Properties p, String k, long def, long lo, long hi) {
  String v = p.getProperty(k);
  if (v == null) return def;
  long n = def;
  try { n = (long) Math.floor(Double.parseDouble(clean(v.trim()))); }
  catch (Throwable t) { @PKG@.Gear.warn("config.properties: " + k + "=" + v + " is not a number - the default is used"); return def; }
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(gcf, r"""
public static double pdec(java.util.Properties p, String k, double def, double lo, double hi) {
  String v = p.getProperty(k);
  if (v == null) return def;
  double n = def;
  try { n = Double.parseDouble(clean(v.trim())); }
  catch (Throwable t) { @PKG@.Gear.warn("config.properties: " + k + "=" + v + " is not a number - the default is used"); return def; }
  if (Double.isNaN(n)) return def;
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
M(gcf, r"""
public static String ptext(java.util.Properties p, String k, String def) {
  String v = p.getProperty(k);
  if (v == null) return def;
  return v.trim();
}""")
# table cells "a,b,c" (the kit's sep=, file form; a hand edit with | is accepted too); null = missing or malformed
M(gcf, r"""
public static double[] cells(String v, int n) {
  if (v == null) return null;
  String s = v.trim().replace('|', ',');
  String[] ps = s.split(",");
  if (ps.length != n) return null;
  double[] out = new double[n];
  for (int i = 0; i < n; i++) {
    try { out[i] = Double.parseDouble(ps[i].trim().replace("_", "")); } catch (Throwable t) { return null; }
    if (Double.isNaN(out[i])) return null;
  }
  return out;
}""")
M(gcf, r"""
public static double clampd(double v, double lo, double hi) {
  if (v < lo) return lo;
  if (v > hi) return hi;
  return v;
}""")
M(gcf, r"""
public static int rchoice(String v, int maxIdx, int def) {
  int i = @PKG@.GearDefs.rIndex(v);
  if (i < 0 || i > maxIdx) return def;
  return i;
}""")
# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows
M(gcf, r"""
public static synchronized void apply(java.util.Properties p, boolean fromFile) {
  PART_GATE = pbool(p, "part.gate", true);
  PART_STATS = pbool(p, "part.stats", true);
  PART_CRAFT = pbool(p, "part.craft", true);
  PART_DROPS = pbool(p, "part.drops", true);
  PART_CHESTS = pbool(p, "part.chests", true);
  IDENTIFY_CMD = pbool(p, "identify.command", true);
  EXCLUDE = ptext(p, "gear.exclude", @EXCLDEF@);
  UI_FRAMES = pbool(p, "ui.frames", true);
  POOL_LATER = pbool(p, "pool.later", true);
  LEVEL_FLOOR = (int) plong(p, "stat.levelFloor", 25L, 1L, 100L);
  LEVEL_FULL = (int) plong(p, "stat.levelFull", 50L, 1L, 100L);
  SMITH_PER = pdec(p, "smith.perLevel", 0.5, 0.0, 100.0);
  SMITH_CAP = pdec(p, "smith.cap", 50.0, 0.0, 100.0);
  CRAFT_MAX = @PKG@.GearDefs.R_ID[rchoice(ptext(p, "craft.maxRarity", "fabled"), 5, 4)];
  LEVEL_VANILLA = pbool(p, "level.vanilla", true);
  LEVEL_DEFAULT = (int) plong(p, "level.default", 0L, 0L, 100L);
  NO_SKILLS = "block".equalsIgnoreCase(ptext(p, "level.noSkills", "pass")) ? "block" : "pass";
  ARMOR_NATIVE = pbool(p, "level.armorNative", true);
  NAMES = ptext(p, "reforge.names", @NAMESDEF@);
  STR_PER = pdec(p, "combat.strPer", 1.0, 0.0, 100.0);
  MP_PER = pdec(p, "combat.mpPer", 1.0, 0.0, 100.0);
  DEF_SCALE = (int) plong(p, "combat.defScale", 100L, 1L, 100000L);
  CRIT_BASE = pdec(p, "crit.base", 0.0, 0.0, 1000.0);
  CRIT_BASE_DMG = pdec(p, "crit.baseDamage", 0.0, 0.0, 10000.0);
  STEAL_S = (int) plong(p, "steal.windowS", 3L, 1L, 60L);
  REGEN_MS = (int) plong(p, "regen.periodMs", 2000L, 250L, 60000L);
  SPEED_PER = pdec(p, "speed.per", 1.0, 0.0, 100.0);
  String mb = ptext(p, "migrate.by", "stats").toLowerCase();
  MIGRATE_BY = (mb.equals("roll") || mb.equals("item")) ? mb : "stats";
  MIGRATE_MAX = @PKG@.GearDefs.R_ID[rchoice(ptext(p, "migrate.maxRarity", "fabled"), 4, 4)];
  int nr = @PKG@.GearDefs.NR;
  int[] rm = new int[nr];
  int[] rl = new int[nr];
  int[] rh = new int[nr];
  double[] oc = new double[nr];
  double[] om = new double[nr];
  double[] ox = new double[nr];
  long[] crb = new long[nr];
  long[] crp = new long[nr];
  long[] cib = new long[nr];
  long[] cip = new long[nr];
  long[] xp = new long[nr];
  for (int i = 0; i < nr; i++) {
    String rid = @PKG@.GearDefs.R_ID[i];
    double[] c = cells(p.getProperty("rarity." + rid), 3);
    if (c == null) {
      if (p.getProperty("rarity." + rid) != null) @PKG@.Gear.warn("config.properties: rarity." + rid + " must be <modifiers>,<low %>,<high %> - the default is used");
      rm[i] = DR_MODS[i]; rl[i] = DR_LO[i]; rh[i] = DR_HI[i];
    } else {
      rm[i] = (int) clampd(c[0], 0.0, 1000.0);
      rl[i] = (int) clampd(c[1], 0.0, 1000.0);
      rh[i] = (int) clampd(c[2], 0.0, 1000.0);
      if (rh[i] < rl[i]) { @PKG@.Gear.warn("config.properties: rarity." + rid + " high % is below low % - high = low"); rh[i] = rl[i]; }
    }
    double[] o = cells(p.getProperty("odds." + rid), 3);
    if (o == null) { oc[i] = OD_CRAFT[i]; om[i] = OD_MOB[i]; ox[i] = OD_CHEST[i]; }
    else { oc[i] = clampd(o[0], 0.0, 1000000.0); om[i] = clampd(o[1], 0.0, 1000000.0); ox[i] = clampd(o[2], 0.0, 1000000.0); }
    double[] cr = cells(p.getProperty("cost.reforge." + rid), 2);
    if (cr == null) { crb[i] = DCR_BASE[i]; crp[i] = DCR_PER[i]; }
    else { crb[i] = (long) clampd(cr[0], 0.0, 1.0E12); crp[i] = (long) clampd(cr[1], 0.0, 1.0E12); }
    double[] ci = cells(p.getProperty("cost.identify." + rid), 2);
    if (ci == null) { cib[i] = DCI_BASE[i]; cip[i] = DCI_PER[i]; }
    else { cib[i] = (long) clampd(ci[0], 0.0, 1.0E12); cip[i] = (long) clampd(ci[1], 0.0, 1.0E12); }
    double[] xr = cells(p.getProperty("xp.reforge." + rid), 1);
    xp[i] = xr == null ? DXPR[i] : (long) clampd(xr[0], 0.0, 100000.0);
  }
  int ns = @PKG@.GearDefs.NS;
  int[] sm = new int[ns];
  int[] sw = new int[ns];
  for (int i = 0; i < ns; i++) {
    String k = @PKG@.GearDefs.S_KEY[i];
    double[] c = cells(p.getProperty("stats." + k), 2);
    int d = @PKG@.GearDefs.S_MAXDEF[i];
    if (c == null) { sm[i] = d; sw[i] = @PKG@.GearDefs.S_WDEF[i]; }
    else {
      sm[i] = (int) clampd(c[0], 0.0, 100000.0);
      sw[i] = (int) clampd(c[1], 0.0, 100000.0);
      // spec 9.2 / review E10: the kit accepts a hand-edited line the check would ask about, so the loader warns instead
      if ((d > 0 && sm[i] > 4 * d) || (sm[i] == 0 && d > 0))
        @PKG@.Gear.warnOnce("stat4x:" + k + ":" + sm[i], "config.properties: stats." + k + " max " + sm[i] + " is far from the default " + d + " - every " + @PKG@.GearDefs.S_LABEL[i] + " roll on new items changes");
    }
  }
  int[] mg = new int[@PKG@.GearDefs.MIG_ID.length];
  for (int i = 0; i < mg.length; i++) {
    double[] c = cells(p.getProperty("migrate.map." + @PKG@.GearDefs.MIG_ID[i]), 1);
    mg[i] = c == null ? DMIG[i] : (int) clampd(c[0], 0.0, 100.0);
  }
  java.util.HashMap mat = new java.util.HashMap();
  java.util.HashMap il = new java.util.HashMap();
  java.util.Iterator it = p.stringPropertyNames().iterator();
  boolean anyMat = false;
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("level.material.") && k.length() > 15) {
      anyMat = true;
      double[] c = cells(p.getProperty(k), 1);
      if (c == null) { @PKG@.Gear.warn("config.properties: " + k + " is not a level - ignored"); continue; }
      mat.put(k.substring(15).toLowerCase(), Integer.valueOf((int) clampd(c[0], 0.0, 100.0)));
    } else if (k.startsWith("level.item.") && k.length() > 11) {
      double[] c = cells(p.getProperty(k), 1);
      if (c == null) { @PKG@.Gear.warn("config.properties: " + k + " is not a level - ignored"); continue; }
      il.put(k.substring(11), Integer.valueOf((int) clampd(c[0], 0.0, 100.0)));
    }
  }
  if (!fromFile && !anyMat) for (int i = 0; i < MAT_T.length; i++) mat.put(MAT_T[i].toLowerCase(), Integer.valueOf(MAT_L[i]));
  R_MODS = rm; R_LO = rl; R_HI = rh;
  O_CRAFT = oc; O_MOB = om; O_CHEST = ox;
  CR_BASE = crb; CR_PER = crp; CI_BASE = cib; CI_PER = cip; XPR = xp;
  S_MAX = sm; S_W = sw; MIG = mg; MAT = mat; ITEMLVL = il;
  EPOCH = EPOCH + 1L;
}""".replace("@EXCLDEF@", jstr(EXCLUDE_DEF)).replace("@NAMESDEF@", jstr(REFORGE_NAMES_DEF)))
# RELOAD of the kit (tools/CONFIG-CONTRACT.md) and the setup() loader: the first start writes the default file
M(gcf, r"""
public static synchronized void load() {
  java.util.Properties p = new java.util.Properties();
  boolean ok = false;
  try {
    java.nio.file.Path f = FILE;
    if (f != null) {
      if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) writeAtomic(f, defaultsText(), false);
      p = read(f);
      ok = true;
    }
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not read Skyy_SkyyGear/config.properties - the built-in defaults are used: " + t);
    p = new java.util.Properties();
    ok = false;
  }
  apply(p, ok);
}""")
M(gcf, r"""
public static boolean hasLine(String text, String prefix) {
  if (text == null) return false;
  String[] ls = text.split("\n");
  for (int i = 0; i < ls.length; i++) if (ls[i].trim().startsWith(prefix)) return true;
  return false;
}""")
# spec 1.6: one-time import of the SkyyRolls 0.1.5 reforge costs when config.properties has no cost.reforge. lines yet
M(gcf, r"""
public static void importRolls(java.nio.file.Path gearFile, java.nio.file.Path rollsFile) {
  try {
    if (gearFile == null || rollsFile == null || !java.nio.file.Files.exists(rollsFile, new java.nio.file.LinkOption[0])) return;
    String text = null;
    if (java.nio.file.Files.exists(gearFile, new java.nio.file.LinkOption[0])) {
      text = new String(java.nio.file.Files.readAllBytes(gearFile), "UTF-8");
      if (hasLine(text, "cost.reforge.")) return;
    }
    java.util.Properties rp = read(rollsFile);
    java.util.HashMap low = new java.util.HashMap();
    java.util.Iterator it = rp.stringPropertyNames().iterator();
    while (it.hasNext()) { String k = (String) it.next(); low.put(k.trim().toLowerCase(), rp.getProperty(k)); }
    int nr = @PKG@.GearDefs.NR;
    String[] lines = new String[nr];
    StringBuilder what = new StringBuilder();
    int n = 0;
    for (int i = 0; i < @PKG@.GearDefs.RQ_FROM.length; i++) {
      String from = @PKG@.GearDefs.RQ_FROM[i];
      if (from.equals("Junk")) continue;
      Object v = low.get("cost." + from.toLowerCase());
      if (v == null) continue;
      long c = 0L;
      try { c = (long) Math.floor(Double.parseDouble(clean(String.valueOf(v).trim()))); } catch (Throwable t) { continue; }
      if (c < 0L) c = 0L;
      if (c > 1000000000000L) c = 1000000000000L;
      int r = @PKG@.GearDefs.rIndex(@PKG@.GearDefs.RQ_TO[i]);
      if (r < 0) continue;
      lines[r] = "cost.reforge." + @PKG@.GearDefs.R_ID[r] + "=" + c + ",0";
      what.append(from).append(" -> ").append(@PKG@.GearDefs.R_NAME[r]).append(' ').append(c).append("; ");
      n++;
    }
    if (n == 0) return;
    String out;
    if (text == null) {
      String[] ls = defaultsText().split("\n");
      StringBuilder sb = new StringBuilder();
      for (int i = 0; i < ls.length; i++) {
        String l = ls[i];
        for (int r = 0; r < nr; r++) if (lines[r] != null && l.startsWith("cost.reforge." + @PKG@.GearDefs.R_ID[r] + "=")) l = lines[r];
        sb.append(l).append('\n');
      }
      out = sb.toString();
      writeAtomic(gearFile, out, false);
    } else {
      StringBuilder sb = new StringBuilder(text);
      if (!text.endsWith("\n")) sb.append('\n');
      sb.append("# imported once from Skyy_SkyyRolls/reforge.properties (spec 1.6)\n");
      for (int r = 0; r < nr; r++) {
        if (lines[r] != null) sb.append(lines[r]).append('\n');
        else sb.append("cost.reforge.").append(@PKG@.GearDefs.R_ID[r]).append('=').append(DCR_BASE[r]).append(',').append(DCR_PER[r]).append('\n');
      }
      writeAtomic(gearFile, sb.toString(), true);
    }
    @PKG@.Gear.info("imported the SkyyRolls reforge costs once (Mythic and Set keep their placeholders): " + what.toString());
    @PKG@.GearLog.line("IMPORT SkyyRolls reforge costs: " + what.toString());
  } catch (Throwable t) { @PKG@.Gear.warn("SkyyRolls cost import failed - the SkyyGear placeholders are used: " + t); }
}""")
M(gcf, r"""
public static String[] excl() {
  String s = EXCLUDE;
  if (s != EXCL_SRC) {
    java.util.ArrayList l = new java.util.ArrayList();
    if (s != null) {
      String[] ps = s.split(",");
      for (int i = 0; i < ps.length; i++) { String t = ps[i].trim(); if (t.length() > 0) l.add(t); }
    }
    String[] a = new String[l.size()];
    for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
    EXCL = a;
    EXCL_SRC = s;
  }
  return EXCL;
}""")
M(gcf, r"""
public static String[] names() {
  String s = NAMES;
  if (s != NAMES_SRC) {
    java.util.ArrayList l = new java.util.ArrayList();
    if (s != null) {
      String[] ps = s.split(",");
      for (int i = 0; i < ps.length; i++) {
        String t = ps[i].trim();
        if (t.length() > 0 && t.length() <= 24 && @PKG@.GearDefs.rIndex(t) < 0) l.add(t);
      }
    }
    String[] a = new String[l.size()];
    for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
    RF = a;
    NAMES_SRC = s;
  }
  return RF;
}""")
M(gcf, "public static int craftMax() { return rchoice(CRAFT_MAX, 5, 4); }")
M(gcf, "public static int migrateMax() { return rchoice(MIGRATE_MAX, 4, 4); }")
M(gcf, r"""
public static long cfgEpoch() {
  Object o = @PKG@.Gear.bget("config:epoch:SkyyGear");
  long k = o instanceof Number ? ((Number) o).longValue() : 0L;
  return EPOCH * 1000003L + k;
}""")
M(gcf, r"""
public static int ri(int r) {
  if (r < 0 || r >= @PKG@.GearDefs.NR) return 0;
  return r;
}""")
M(gcf, r"""
public static long costReforge(int r, int lvl) {
  int i = ri(r);
  long c = CR_BASE[i] + CR_PER[i] * (long) (lvl < 0 ? 0 : lvl);
  return c < 0L ? 0L : c;
}""")
M(gcf, r"""
public static long costIdentify(int r, int lvl) {
  int i = ri(r);
  long c = CI_BASE[i] + CI_PER[i] * (long) (lvl < 0 ? 0 : lvl);
  return c < 0L ? 0L : c;
}""")
M(gcf, "public static long xpReforge(int r) { return XPR[ri(r)]; }")
# ---- check= hooks (tools/CONFIG-CONTRACT.md: key = tableKey[entry], value = columns joined by |, null = removal)
M(gcf, r"""
public static String entryOf(String key) {
  if (key == null) return null;
  int a = key.indexOf('[');
  int z = key.lastIndexOf(']');
  if (a < 0 || z <= a + 1) return null;
  return key.substring(a + 1, z);
}""")
M(gcf, r"""
public static String checkRarityKey(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  int r = @PKG@.GearDefs.rIndex(e);
  if (r < 0 || !@PKG@.GearDefs.R_ID[r].equals(e)) return "Unknown rarity " + e + " - use normal, unique, rare, legendary, fabled, mythic or set (lower case).";
  return null;
}""")
M(gcf, r"""
public static String checkRarity(String key, String value) {
  String bad = checkRarityKey(key, value);
  if (bad != null || value == null) return bad;
  double[] c = cells(value, 3);
  if (c != null && c[2] < c[1]) return "High % must be at least Low % (the roll range gets wider and higher with rarity).";
  return null;
}""")
M(gcf, r"""
public static String checkMigKey(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  for (int i = 0; i < @PKG@.GearDefs.MIG_ID.length; i++) if (@PKG@.GearDefs.MIG_ID[i].equals(e)) return null;
  return "Old SkyyRolls items can only become unique, rare, legendary or fabled (anything lower is normal).";
}""")
M(gcf, r"""
public static String checkStat(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  int i = @PKG@.GearDefs.sIndex(e);
  if (i < 0) return "Unknown stat " + e + " - the stat keys are the ones listed in Server Setup (spec 4.2).";
  if (value == null) return null;
  double[] c = cells(value, 2);
  if (c == null) return null;
  long mx = (long) c[0];
  int d = @PKG@.GearDefs.S_MAXDEF[i];
  String lab = @PKG@.GearDefs.S_LABEL[i];
  if (d > 0 && mx == 0L) return "?" + lab + " max 0 means every " + lab + " roll on new items is 1. Save anyway?";
  if (d > 0 && mx > 4L * (long) d) return "?" + lab + " max " + mx + " is " + (mx / (long) d) + " x the default " + d + " - every " + lab + " roll on new items changes. Save anyway?";
  return null;
}""")
M(gcf, r"""
public static String checkNames(String key, String value) {
  if (value == null) return null;
  String[] ns = value.split(",");
  for (int i = 0; i < ns.length; i++) {
    String t = ns[i].trim();
    if (t.length() == 0) continue;
    if (@PKG@.GearDefs.rIndex(t) >= 0) return t + " is a rarity name - reforge names may not be rarity names.";
    if (t.length() > 24) return t + " is longer than 24 characters.";
  }
  return null;
}""")

# ================================================================= GearData (1/2): id rules + document read + migration (spec 1)
M(gdt, r"""
public static boolean skyyItem(String id) {
  if (id == null) return true;
  String low = id.toLowerCase();
  return low.startsWith("skyy") || low.indexOf("_skyy") >= 0;
}""")
M(gdt, r"""
public static boolean ammo(String id) {
  String[] parts = id.split("_");
  for (int i = 1; i < parts.length; i++) {
    String p = parts[i].toLowerCase();
    for (int j = 0; j < @PKG@.GearDefs.AMMO.length; j++) if (p.equals(@PKG@.GearDefs.AMMO[j])) return true;
  }
  return false;
}""")
# spec 1.3: gear = every Weapon_* (not ammo, not an excluded prefix) and every Armor_*; never Skyy_* and never Tool_*
M(gdt, r"""
public static boolean isGear(String id) {
  if (id == null || id.length() == 0 || skyyItem(id)) return false;
  if (id.startsWith("Armor_")) return true;
  if (!id.startsWith("Weapon_")) return false;
  if (ammo(id)) return false;
  String[] ex = @PKG@.GearCfg.excl();
  for (int i = 0; i < ex.length; i++) if (id.startsWith(ex[i])) return false;
  return true;
}""")
M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\"Tool_\") && !skyyItem(id); }")
M(gdt, r"""
public static boolean isSpell(String id) {
  if (id == null) return false;
  for (int i = 0; i < @PKG@.GearDefs.SPELL.length; i++) if (id.startsWith(@PKG@.GearDefs.SPELL[i])) return true;
  return false;
}""")
# 0 = weapon, 1 = spell weapon, 2 = armor, 3 = tool, -1 = not gear
M(gdt, r"""
public static int slotOf(String id) {
  if (isGear(id)) {
    if (id.startsWith("Armor_")) return 2;
    return isSpell(id) ? 1 : 0;
  }
  if (isTool(id)) return 3;
  return -1;
}""")
M(gdt, r"""
public static String toolKind(String id) {
  if (id == null) return "tool";
  for (int i = 0; i < @PKG@.GearDefs.TF_PRE.length; i++) if (id.startsWith(@PKG@.GearDefs.TF_PRE[i])) return @PKG@.GearDefs.TF_KIND[i];
  return "tool";
}""")
M(gdt, r"""
public static String kindFor(String id) {
  if (isTool(id)) return toolKind(id);
  return "combat";
}""")
M(gdt, r"""
public static @BV@ getv(@BD@ md, String k) {
  try { return md == null ? null : md.get(k); } catch (Throwable t) { return null; }
}""")
M(gdt, r"""
public static int num(@BD@ d, String k, int def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); } catch (Throwable t) { }
  return def;
}""")
M(gdt, r"""
public static long lnum(@BD@ d, String k, long def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isNumber()) return v.asNumber().longValue(); } catch (Throwable t) { }
  return def;
}""")
M(gdt, r"""
public static String str(@BD@ d, String k, String def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isString()) return v.asString().getValue(); } catch (Throwable t) { }
  return def;
}""")
M(gdt, r"""
public static boolean bool(@BD@ d, String k, boolean def) {
  try { @BV@ v = d == null ? null : d.get(k); if (v != null && v.isBoolean()) return v.asBoolean().getValue(); } catch (Throwable t) { }
  return def;
}""")
# 0 = no document, 1 = SkyyGear v1 document, 2 = only a SkyyRolls document, 3 = SkyyGear data that is not a document (unreadable),
# 4 = a newer SkyyGear schema (read only, never rewritten; spec 1.2)
M(gdt, r"""
public static int state(@BD@ md) {
  if (md == null) return 0;
  @BV@ g = getv(md, @PKG@.GearDefs.DOC_KEY);
  if (g != null && !g.isNull()) {
    if (!g.isDocument()) return 3;
    if (num(g.asDocument(), "v", 1) > 1) return 4;
    return 1;
  }
  @BV@ r = getv(md, @PKG@.GearDefs.ROLLS_KEY);
  if (r != null && r.isDocument()) return 2;
  return 0;
}""")
M(gdt, r"""
public static @BD@ gearDoc(@BD@ md) {
  @BV@ g = getv(md, @PKG@.GearDefs.DOC_KEY);
  return g != null && g.isDocument() ? g.asDocument() : null;
}""")
M(gdt, r"""
public static @BD@ rollsDoc(@BD@ md) {
  @BV@ g = getv(md, @PKG@.GearDefs.ROLLS_KEY);
  return g != null && g.isDocument() ? g.asDocument() : null;
}""")
M(gdt, r"""
public static boolean hasAnyDoc(@BD@ md) {
  if (md == null) return false;
  return md.containsKey(@PKG@.GearDefs.DOC_KEY) || md.containsKey(@PKG@.GearDefs.ROLLS_KEY);
}""")
# gear for every reader: a gear id, or a tool that carries a SkyyGear / SkyyRolls document (migrated SkyyRolls tools, spec 1.6)
M(gdt, r"""
public static boolean gearish(String id, @BD@ md) {
  return isGear(id) || (isTool(id) && hasAnyDoc(md));
}""")
M(gdt, r"""
public static int rarity(@BD@ d) {
  int r = @PKG@.GearDefs.rIndex(str(d, "r", "normal"));
  return r < 0 ? 0 : r;
}""")
M(gdt, "public static boolean identified(@BD@ d) { return bool(d, \"id\", true); }")
M(gdt, "public static String kind(@BD@ d) { return str(d, \"kind\", \"combat\"); }")
# spec 1.2 reading rule 1: a document without gate takes the kind table's gate
M(gdt, r"""
public static String gate(@BD@ d) {
  String g = str(d, "gate", null);
  if (g != null) return g;
  return @PKG@.GearDefs.kindGate(kind(d));
}""")
M(gdt, r"""
public static @BA@ mods(@BD@ d) {
  try { @BV@ v = d == null ? null : d.get("mods"); if (v != null && v.isArray()) return v.asArray(); } catch (Throwable t) { }
  return new @BA@();
}""")
M(gdt, r"""
public static @BD@ mod(String s, int v) {
  @BD@ m = new @BD@();
  m.append("s", new org.bson.BsonString(s));
  m.append("v", new org.bson.BsonInt32(v));
  return m;
}""")
M(gdt, r"""
public static @BD@ base(String kind, int r, boolean ident, String src) {
  @BD@ d = new @BD@();
  d.append("v", new org.bson.BsonInt32(1));
  d.append("kind", new org.bson.BsonString(kind));
  d.append("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[@PKG@.GearCfg.ri(r)]));
  d.append("id", new org.bson.BsonBoolean(ident));
  d.append("mods", new @BA@());
  d.append("src", new org.bson.BsonString(src));
  d.append("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  d.append("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kind)));
  return d;
}""")
# spec 1.5: the legacy stamp (gear a player already owns stays Normal with no modifiers, LOCKED)
M(gdt, "public static @BD@ legacy(String id) { return base(kindFor(id), 0, true, \"legacy\"); }")
M(gdt, r"""
public static String qualityIdOf(String id) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return "";
    Object q = @IQ@.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof @IQ@) { String s = ((@IQ@) q).getId(); if (s != null) return s; }
  } catch (Throwable t) { }
  return "";
}""")
# spec 1.6: rarity of an old SkyyRolls document. stats (default): score = average of dmg/30, str/25, crit/15 in % (SkyyRolls' maxima;
# a missing key = 0); roll: the old Roll Quality; item: the item's engine quality. Capped at migrate.maxRarity, never mythic / set.
M(gdt, r"""
public static int migrateRarity(String id, @BD@ rolls) {
  String by = @PKG@.GearCfg.MIGRATE_BY;
  int r = 0;
  if ("item".equals(by)) {
    String q = qualityIdOf(id);
    for (int i = 0; i < @PKG@.GearDefs.RQ_FROM.length; i++) if (@PKG@.GearDefs.RQ_FROM[i].equalsIgnoreCase(q)) r = @PKG@.GearDefs.rIndex(@PKG@.GearDefs.RQ_TO[i]);
  } else {
    double score;
    if ("roll".equals(by)) score = (double) num(rolls, "quality", 0);
    else {
      double a = (double) num(rolls, "dmg", 0) / 30.0;
      double b = (double) num(rolls, "str", 0) / 25.0;
      double c = (double) num(rolls, "crit", 0) / 15.0;
      score = (a + b + c) / 3.0 * 100.0;
    }
    int[] mg = @PKG@.GearCfg.MIG;
    if (score >= (double) mg[3]) r = 4;
    else if (score >= (double) mg[2]) r = 3;
    else if (score >= (double) mg[1]) r = 2;
    else if (score >= (double) mg[0]) r = 1;
    else r = 0;
  }
  if (r < 0) r = 0;
  int cap = @PKG@.GearCfg.migrateMax();
  if (r > cap) r = cap;
  if (r > 4) r = 4;
  return r;
}""")
M(gdt, r"""
public static @BD@ migrate(String id, @BD@ rolls) {
  String kind = kindFor(id);
  @BD@ d = base(kind, migrateRarity(id, rolls), true, "rolls");
  @BA@ ms = new @BA@();
  int vDmg = num(rolls, "dmg", 0);
  int vStr = num(rolls, "str", 0);
  int vCrit = num(rolls, "crit", 0);
  if (vDmg != 0) ms.add(mod("dmg", vDmg));
  if (vStr != 0) ms.add(mod("str", vStr));
  if (vCrit != 0) ms.add(mod("cc", vCrit));
  d.put("mods", ms);
  String rf = str(rolls, "reforge", null);
  if (rf != null && rf.trim().length() > 0 && !rf.equals("?") && @PKG@.GearDefs.rIndex(rf) < 0) d.append("rf", new org.bson.BsonString(rf.trim()));
  d.append("old", rolls.clone());
  return d;
}""")
# spec 1.2 reading rules 1 + 2 (the in-memory view every reader uses); null = unreadable / newer schema / not gear
M(gdt, r"""
public static @BD@ effective(String id, @BD@ md) {
  int st = state(md);
  if (st == 1) return gearDoc(md);
  if (st == 3 || st == 4) return null;
  if (st == 2) return (isGear(id) || isTool(id)) ? migrate(id, rollsDoc(md)) : null;
  if (isGear(id)) return legacy(id);
  return null;
}""")

# ================================================================= GearLevel (spec 3.1, 2.2 level factor)
M(glv, r"""
public static int clamp(int v) {
  if (v < 0) return 0;
  if (v > 100) return 100;
  return v;
}""")
M(glv, r"""
public static int level(String id, @BD@ d) {
  if (id == null) return 0;
  try {
    @BV@ v = d == null ? null : d.get("lvl");
    if (v != null && v.isNumber()) return clamp(v.asNumber().intValue());
  } catch (Throwable t) { }
  Object o = @PKG@.GearCfg.ITEMLVL.get(id);
  if (o instanceof Integer) return clamp(((Integer) o).intValue());
  java.util.HashMap mat = @PKG@.GearCfg.MAT;
  String[] tk = id.split("_");
  for (int i = 0; i < tk.length; i++) {
    Object m = mat.get(tk[i].toLowerCase());
    if (m instanceof Integer) return clamp(((Integer) m).intValue());
  }
  if (@PKG@.GearCfg.LEVEL_VANILLA) {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it != null) {
      int l = 0;
      try { l = it.getItemLevel(); } catch (Throwable t2) { l = 0; }
      if (l > 0) return clamp(l);
    }
  }
  return clamp(@PKG@.GearCfg.LEVEL_DEFAULT);
}""")
# f = floor + (100 - floor) x min(level, full) / full, in % (spec 2.2); floor 100 switches the scaling off
M(glv, r"""
public static double factor(int level) {
  int floor = @PKG@.GearCfg.LEVEL_FLOOR;
  int full = @PKG@.GearCfg.LEVEL_FULL;
  if (full < 1) full = 1;
  if (floor >= 100) return 100.0;
  int l = level < 0 ? 0 : level;
  if (l > full) l = full;
  return (double) floor + (100.0 - (double) floor) * (double) l / (double) full;
}""")

# ================================================================= GearGate (spec 3.3): gate skill + level cache (+ popup for PART B)
# cache per player: Object[] { String profileEpoch, String classSkill ("" = none), ConcurrentHashMap skill -> Integer level }.
# Every lookup compares profile:epoch + class:skill (two plain map reads) with the cached pair and starts over on a change (E2).
# Levels: >= 0 = the level; -1 = SkyySkills does not know that skill name; -2 = no SkyySkills (skill:fn:level missing).
F(ggt, "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();")
F(ggt, "public static final java.util.concurrent.ConcurrentHashMap POPPED = new java.util.concurrent.ConcurrentHashMap();")
M(ggt, r"""
public static String classSkillRaw(java.util.UUID u) {
  Object o = u == null ? null : @PKG@.Gear.bget("class:skill:" + u);
  return o instanceof String && ((String) o).length() > 0 ? (String) o : null;
}""")
M(ggt, "public static boolean classesOn() { return @PKG@.Gear.fn(\"class:fn:allowed\") != null; }")
M(ggt, "public static boolean skillsOn() { return @PKG@.Gear.fn(\"skill:fn:level\") != null; }")
M(ggt, r"""
public static int readLevel(java.util.UUID u, String skill) {
  java.util.function.Function f = @PKG@.Gear.fn("skill:fn:level");
  if (f == null) return -2;
  try {
    Object r = f.apply(new Object[] { u, skill });
    if (r instanceof Number) { int n = ((Number) r).intValue(); return n < 0 ? 0 : n; }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("skillfn", "skill:fn:level failed: " + t); }
  return -1;
}""")
M(ggt, r"""
public static Object[] entry(java.util.UUID u) {
  String ep = @PKG@.Gear.epoch(u);
  String cs = classSkillRaw(u);
  if (cs == null) cs = "";
  Object[] e = (Object[]) CACHE.get(u);
  if (e == null || !ep.equals(e[0]) || !cs.equals(e[1])) {
    e = new Object[] { ep, cs, new java.util.concurrent.ConcurrentHashMap() };
    CACHE.put(u, e);
  }
  return e;
}""")
M(ggt, r"""
public static int have(java.util.UUID u, String skill) {
  if (u == null || skill == null || skill.length() == 0) return -2;
  Object[] e = entry(u);
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) e[2];
  Object o = m.get(skill);
  if (o instanceof Integer) return ((Integer) o).intValue();
  int n = readLevel(u, skill);
  m.put(skill, Integer.valueOf(n));
  if (n == -1) @PKG@.Gear.warnOnce("skill:" + skill, "SkyySkills does not know the gate skill '" + skill + "' - it counts as level 0");
  return n;
}""")
# the SkyySkills skill a gate asks: "class" -> class:skill:<uuid>; SkyyClasses present but no class -> null (level 0, "pick a class");
# no SkyyClasses -> the pseudo-skill "Combat" (SkyySkills resolves it to the active class row)
M(ggt, r"""
public static String gateSkill(java.util.UUID u, String gate) {
  if (gate == null || gate.length() == 0) return null;
  if (!gate.equals("class")) return gate;
  String cs = classSkillRaw(u);
  if (cs != null) return cs;
  if (classesOn()) return null;
  return "Combat";
}""")
# display name of a gate for tooltips (SkyyGear's own class -> skill copy only when SkyyClasses is absent)
M(ggt, r"""
public static String gateLabel(java.util.UUID u, String gate) {
  if (gate == null || gate.length() == 0) return "";
  if (!gate.equals("class")) return gate;
  String cs = classSkillRaw(u);
  if (cs != null) return cs;
  Object pc = u == null ? null : @PKG@.Gear.bget("profile:class:" + u);
  String m = pc instanceof String ? @PKG@.GearDefs.classSkill((String) pc) : null;
  if (m != null) return m;
  return classesOn() ? "Class skill" : "Combat";
}""")
# GearTick (1 Hz) + the ready refresh: re-read every cached level; true = something the player can see may have changed
M(ggt, r"""
public static boolean refresh(java.util.UUID u) {
  if (u == null) return false;
  Object[] old = (Object[]) CACHE.get(u);
  Object[] e = entry(u);
  boolean changed = old != e;
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) e[2];
  String cs = gateSkill(u, "class");
  if (cs != null && !m.containsKey(cs)) { have(u, cs); changed = true; }
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    int n = readLevel(u, k);
    Object o = m.get(k);
    if (!(o instanceof Integer) || ((Integer) o).intValue() != n) { m.put(k, Integer.valueOf(n)); changed = true; }
  }
  return changed;
}""")
M(ggt, "public static void forget(java.util.UUID u) { if (u != null) { CACHE.remove(u); POPPED.remove(u); } }")
# Object[] { Boolean ok, String skill (label), Integer need, Integer have, Boolean enforced, Integer state }
# state: 0 evaluated, 1 SkyyClasses present but no class (level 0), 2 no SkyySkills, 3 no gate (kind without a skill),
#        4 no owner (neutral text), 5 part.gate off
M(ggt, r"""
public static Object[] check(java.util.UUID u, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  boolean enforced = @PKG@.GearDefs.enforcedKind(kind);
  String label = gateLabel(u, gate);
  if (gate.length() == 0) return new Object[] { Boolean.TRUE, "", Integer.valueOf(need), Integer.valueOf(-1), Boolean.FALSE, Integer.valueOf(3) };
  if (u == null) return new Object[] { Boolean.TRUE, label, Integer.valueOf(need), Integer.valueOf(-1), Boolean.valueOf(enforced), Integer.valueOf(4) };
  if (!@PKG@.GearCfg.PART_GATE) return new Object[] { Boolean.TRUE, label, Integer.valueOf(need), Integer.valueOf(-1), Boolean.FALSE, Integer.valueOf(5) };
  if (!skillsOn()) {
    boolean pass = !"block".equals(@PKG@.GearCfg.NO_SKILLS) || need <= 0;
    return new Object[] { Boolean.valueOf(pass), label, Integer.valueOf(need), Integer.valueOf(-2), Boolean.valueOf(enforced), Integer.valueOf(2) };
  }
  String sk = gateSkill(u, gate);
  if (sk == null) return new Object[] { Boolean.valueOf(need <= 0), label, Integer.valueOf(need), Integer.valueOf(0), Boolean.valueOf(enforced), Integer.valueOf(1) };
  int h = have(u, sk);
  if (h == -2) {
    boolean pass2 = !"block".equals(@PKG@.GearCfg.NO_SKILLS) || need <= 0;
    return new Object[] { Boolean.valueOf(pass2), label, Integer.valueOf(need), Integer.valueOf(-2), Boolean.valueOf(enforced), Integer.valueOf(2) };
  }
  if (h < 0) h = 0;
  return new Object[] { Boolean.valueOf(h >= need), label, Integer.valueOf(need), Integer.valueOf(h), Boolean.valueOf(enforced), Integer.valueOf(0) };
}""")
# PART B: the level / unidentified popup (spec 3.4, the SkyyClasses ClassRules.popup shape); throttled 1500 ms, gated by the
# player switch gear.blockedPopup (only the popup, never the block); the icon is a metadata-free new ItemStack(id, 1)
M(ggt, r"""
public static void popup(@PR@ pr, java.util.UUID u, String id, String title, String body) {
  try {
    if (!@PKG@.Gear.notifyOn(u, "gear.blockedPopup")) return;
    long now = System.currentTimeMillis();
    Long last = (Long) POPPED.get(u);
    if (last != null && now - last.longValue() < 1500L) return;
    POPPED.put(u, Long.valueOf(now));
    @MSG@ t = @MSG@.raw(title).color("#ff9d6b");
    @MSG@ b = @MSG@.raw(body);
    @IWM@ icon = null;
    try { if (id != null && id.length() > 0) icon = (@IWM@) new @IS@(id, 1).toPacket(); } catch (Throwable t0) { icon = null; }
    if (icon != null) @NTU@.sendNotification(pr.getPacketHandler(), t, b, icon, @NST@.Warning);
    else @NTU@.sendNotification(pr.getPacketHandler(), t, b, @NST@.Warning);
  } catch (Throwable x) { @PKG@.Gear.warnOnce("popup", "popup failed: " + x); }
}""")

# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded
F(grl, "public static final java.security.SecureRandom RNG = new java.security.SecureRandom();")
M(grl, r"""
public static int randInt(int a, int b) {
  if (b <= a) return a;
  return a + RNG.nextInt(b - a + 1);
}""")
M(grl, r"""
public static int pickWeighted(double[] w) {
  double total = 0.0;
  for (int i = 0; i < w.length; i++) if (w[i] > 0.0) total = total + w[i];
  if (total <= 0.0) return 0;
  double x = RNG.nextDouble() * total;
  int lastPos = 0;
  for (int i = 0; i < w.length; i++) {
    if (w[i] <= 0.0) continue;
    lastPos = i;
    x = x - w[i];
    if (x < 0.0) return i;
  }
  return lastPos;
}""")
# col 0 = craft, 1 = mob, 2 = chest (table odds)
M(grl, r"""
public static int pickRarity(int col) {
  double[] w = col == 1 ? @PKG@.GearCfg.O_MOB : (col == 2 ? @PKG@.GearCfg.O_CHEST : @PKG@.GearCfg.O_CRAFT);
  return pickWeighted(w);
}""")
# spec 5.3: Smithing rarity = skill:fn:level(uuid, "Smithing") x smith.perLevel %, capped by smith.cap (0 without SkyySkills)
M(grl, r"""
public static double smithChance(java.util.UUID u) {
  if (u == null) return 0.0;
  int lv = @PKG@.GearGate.have(u, "Smithing");
  if (lv <= 0) return 0.0;
  double c = (double) lv * @PKG@.GearCfg.SMITH_PER;
  if (c > @PKG@.GearCfg.SMITH_CAP) c = @PKG@.GearCfg.SMITH_CAP;
  return c < 0.0 ? 0.0 : c;
}""")
# base rarity from the craft odds, never above craft.maxRarity; with the Smithing chance it steps up one tier (never above the cap,
# never to Set; a rolled Set - weight 0 by default - stays Set)
M(grl, r"""
public static int craftRarity(java.util.UUID u, double[] smithOut) {
  int r = pickRarity(0);
  if (r == 6) return r;
  int max = @PKG@.GearCfg.craftMax();
  if (r > max) r = max;
  double c = smithChance(u);
  if (smithOut != null && smithOut.length > 0) smithOut[0] = c;
  if (c > 0.0 && r < max && r < 5 && RNG.nextDouble() * 100.0 < c) r = r + 1;
  return r;
}""")
M(grl, r"""
public static boolean allowed(int i, int slot) {
  String s = @PKG@.GearDefs.S_SLOT[i];
  if (slot == 2) return s.indexOf('a') >= 0;
  if (slot == 0) return s.indexOf('w') >= 0;
  if (slot == 1) return s.indexOf('w') >= 0 || s.indexOf('s') >= 0;
  return false;
}""")
M(grl, r"""
public static int[] pool(int slot) {
  int[] w = @PKG@.GearCfg.S_W;
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < @PKG@.GearDefs.NS; i++) {
    if (!allowed(i, slot) || w[i] <= 0) continue;
    if (@PKG@.GearDefs.S_LIVE[i] == 0 && !@PKG@.GearCfg.POOL_LATER) continue;
    l.add(Integer.valueOf(i));
  }
  int[] a = new int[l.size()];
  for (int i = 0; i < a.length; i++) a[i] = ((Integer) l.get(i)).intValue();
  return a;
}""")
# value bounds of stat i for rarity r at item level lvl: { lo, hi } = max(1, round(max x low/100 x f/100)) .. (high)
M(grl, r"""
public static int[] bounds(int i, int r, int lvl) {
  int rr = @PKG@.GearCfg.ri(r);
  double f = @PKG@.GearLevel.factor(lvl);
  double mx = (double) @PKG@.GearCfg.S_MAX[i];
  long lo = Math.round(mx * (double) @PKG@.GearCfg.R_LO[rr] / 100.0 * f / 100.0);
  long hi = Math.round(mx * (double) @PKG@.GearCfg.R_HI[rr] / 100.0 * f / 100.0);
  if (lo < 1L) lo = 1L;
  if (hi < 1L) hi = 1L;
  if (hi < lo) hi = lo;
  return new int[] { (int) lo, (int) hi };
}""")
# spec 2.3: pick count distinct stats (weighted, no repeats, capped by the pool), roll each value, display order = table order
M(grl, r"""
public static @BA@ rollMods(int slot, int r, int lvl) {
  @BA@ out = new @BA@();
  int[] p = pool(slot);
  if (p.length == 0) return out;
  int count = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(r)];
  if (count > p.length) count = p.length;
  int[] w = @PKG@.GearCfg.S_W;
  boolean[] used = new boolean[p.length];
  boolean[] pick = new boolean[@PKG@.GearDefs.NS];
  for (int k = 0; k < count; k++) {
    double total = 0.0;
    for (int j = 0; j < p.length; j++) if (!used[j]) total = total + (double) w[p[j]];
    if (total <= 0.0) break;
    double x = RNG.nextDouble() * total;
    int sel = -1;
    for (int j = 0; j < p.length; j++) {
      if (used[j]) continue;
      sel = j;
      x = x - (double) w[p[j]];
      if (x < 0.0) break;
    }
    if (sel < 0) break;
    used[sel] = true;
    pick[p[sel]] = true;
  }
  for (int i = 0; i < @PKG@.GearDefs.NS; i++) {
    if (!pick[i]) continue;
    int[] b = bounds(i, r, lvl);
    out.add(@PKG@.GearData.mod(@PKG@.GearDefs.S_KEY[i], randInt(b[0], b[1])));
  }
  return out;
}""")
M(grl, r"""
public static String pickName(String cur) {
  String[] ns = @PKG@.GearCfg.names();
  if (ns.length == 0) return null;
  if (ns.length == 1) return ns[0];
  for (int k = 0; k < 32; k++) {
    String n = ns[RNG.nextInt(ns.length)];
    if (cur == null || !n.equals(cur)) return n;
  }
  return ns[0].equals(cur) ? ns[1] : ns[0];
}""")
# a fresh document: rarity r, identified or not (unidentified = no modifiers stored; they roll at identify time, spec 5.6)
M(grl, r"""
public static @BD@ newDoc(String id, int r, boolean ident, String src) {
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), r, ident, src);
  if (ident) d.put("mods", rollMods(@PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  return d;
}""")
M(grl, "public static @BD@ craftDoc(String id, java.util.UUID u) { return newDoc(id, craftRarity(u, null), true, \"craft\"); }")
# PART B: the unidentified tag (col 1 = mob -> src drop, col 2 = chest -> src chest)
M(grl, "public static @BD@ unidDoc(String id, int col, String src) { return newDoc(id, pickRarity(col), false, src); }")
# spec 5.4: a reforge re-rolls the whole modifier set for the rarity + level, picks a new cosmetic name, rfN++; rarity, level, set,
# id and src never change; unknown fields are kept (clone, change, put back - reading rule 3)
M(grl, r"""
public static @BD@ reforge(String id, @BD@ doc) {
  @BD@ d = doc.clone();
  int r = @PKG@.GearData.rarity(d);
  d.put("mods", rollMods(@PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  String n = pickName(@PKG@.GearData.str(d, "rf", null));
  if (n != null) d.put("rf", new org.bson.BsonString(n));
  else d.remove("rf");
  d.put("rfN", new org.bson.BsonInt32(@PKG@.GearData.num(d, "rfN", 0) + 1));
  d.put("at", new org.bson.BsonInt64(System.currentTimeMillis()));
  return d;
}""")
# spec 5.7: identify rolls the modifiers for the item's rarity (PART B's page and the admin /gear identify call it)
M(grl, r"""
public static @BD@ identify(String id, @BD@ doc, java.util.UUID by) {
  @BD@ d = doc.clone();
  int r = @PKG@.GearData.rarity(d);
  long now = System.currentTimeMillis();
  d.put("mods", rollMods(@PKG@.GearData.slotOf(id), r, @PKG@.GearLevel.level(id, d)));
  d.put("id", new org.bson.BsonBoolean(true));
  d.put("idAt", new org.bson.BsonInt64(now));
  if (by != null) d.put("idBy", new org.bson.BsonString(by.toString()));
  d.put("at", new org.bson.BsonInt64(now));
  return d;
}""")

# ================================================================= GearView (spec 6): tooltip, plain lines, sigs
M(gvw, r"""
public static String slotWord(String id) {
  int s = @PKG@.GearData.slotOf(id);
  if (s == 2) return "ARMOR";
  if (s == 3) return "TOOL";
  return "WEAPON";
}""")
M(gvw, r"""
public static String suffix(int i) {
  if (@PKG@.GearDefs.S_LIVE[i] == 0) return " (coming later)";
  String s = @PKG@.GearDefs.S_SUF[i];
  if (s.equals("spells")) return " (spells)";
  if (s.equals("elem")) return " (each element)";
  if (s.equals("steal")) return " (every " + @PKG@.GearCfg.STEAL_S + "s)";
  if (s.equals("regen")) return " (every " + @PKG@.Gear.fnum((double) @PKG@.GearCfg.REGEN_MS / 1000.0) + "s)";
  if (s.equals("hprp")) return " (boosts Raw Health Regen)";
  return "";
}""")
M(gvw, r"""
public static String valText(String key, int v) {
  int i = @PKG@.GearDefs.sIndex(key);
  return (v >= 0 ? "+" : "") + v + (i >= 0 ? @PKG@.GearDefs.S_UNIT[i] : "");
}""")
# one modifier line ("Strength: +12", "Magical Power: +8 (spells)"); unknown stat keys are kept and shown by name (rule 3)
M(gvw, r"""
public static String modLine(String key, int v) {
  int i = @PKG@.GearDefs.sIndex(key);
  if (i < 0) return key + ": " + (v >= 0 ? "+" : "") + v;
  return @PKG@.GearDefs.S_LABEL[i] + ": " + valText(key, v) + suffix(i);
}""")
M(gvw, r"""
public static boolean later(String key) {
  int i = @PKG@.GearDefs.sIndex(key);
  return i >= 0 && @PKG@.GearDefs.S_LIVE[i] == 0;
}""")
# weapon base damage from the engine's own damage data (SkyyRolls 0.1.4 rangeOf / damageText, ItemWeapon basic breakdown)
M(gvw, r"""
public static float[] rangeOf(@DBD@ b) {
  if (b == null) return null;
  java.util.List es = b.entries();
  if (es == null || es.isEmpty()) return null;
  float lo = Float.MAX_VALUE;
  float hi = 0f;
  for (int i = 0; i < es.size(); i++) {
    Object o = es.get(i);
    if (!(o instanceof @DBE@)) continue;
    @DBE@ e = (@DBE@) o;
    float a = e.min();
    float z = e.max();
    if (z <= 0f) continue;
    if (a < 0f) a = 0f;
    if (a < lo) lo = a;
    if (z > hi) hi = z;
  }
  if (hi <= 0f) return null;
  if (lo == Float.MAX_VALUE || lo > hi) lo = hi;
  return new float[] { lo, hi };
}""")
M(gvw, r"""
public static String damageText(String id) {
  try {
    @ITM@ item = @PKG@.Gear.item(id);
    if (item == null) return null;
    @IWP@ w = item.getWeapon();
    if (w == null) return null;
    float[] r = rangeOf(w.getBasicDamageBreakdown());
    if (r == null) r = rangeOf(w.getUltimateDamageBreakdown());
    if (r == null) return null;
    String a = @PKG@.Gear.fnum((double) r[0]);
    String z = @PKG@.Gear.fnum((double) r[1]);
    return a.equals(z) ? a : a + "-" + z;
  } catch (Throwable t) { return null; }
}""")
M(gvw, r"""
public static String statName(int idx) {
  try {
    Object o = @ESTT@.getAssetMap().getAsset(idx);
    if (o instanceof @ESTT@) { String s = ((@ESTT@) o).getId(); if (s != null) return s; }
  } catch (Throwable t) { }
  return "Stat " + idx;
}""")
# armor base lines (native): "Health: 17", "Armor: 9% physical, 9% projectile" (spec 4.2 base lines, 6.1)
M(gvw, r"""
public static void armorLines(String id, java.util.ArrayList out) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return;
    @IAR@ a = it.getArmor();
    if (a == null) return;
    java.util.ArrayList st = new java.util.ArrayList();
    Object sm = a.getStatModifiers();
    if (sm instanceof java.util.Map) {
      java.util.Iterator e = ((java.util.Map) sm).entrySet().iterator();
      while (e.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(k instanceof Number) || !(v instanceof Object[])) continue;
        Object[] xs = (Object[]) v;
        double add = 0.0;
        double mul = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @SMO@)) continue;
          @SMO@ m = (@SMO@) xs[i];
          if (m.getCalculationType() == @CAL@.MULTIPLICATIVE) mul = mul + (double) m.getAmount();
          else add = add + (double) m.getAmount();
        }
        String nm = statName(((Number) k).intValue());
        if (add != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(add));
        if (mul != 0.0) st.add(nm + ": " + @PKG@.Gear.fnum(mul * 100.0) + "%");
      }
    }
    java.util.Collections.sort(st);
    for (int i = 0; i < st.size(); i++) out.add(st.get(i));
    Object dr = a.getDamageResistanceValues();
    if (dr instanceof java.util.Map && !((java.util.Map) dr).isEmpty()) {
      java.util.ArrayList parts = new java.util.ArrayList();
      java.util.Iterator e2 = ((java.util.Map) dr).entrySet().iterator();
      while (e2.hasNext()) {
        java.util.Map.Entry en = (java.util.Map.Entry) e2.next();
        Object k = en.getKey();
        Object v = en.getValue();
        if (!(v instanceof Object[])) continue;
        String cause = k instanceof @DCS@ ? ((@DCS@) k).getId() : String.valueOf(k);
        if (cause == null) cause = "?";
        Object[] xs = (Object[]) v;
        double add = 0.0;
        double mul = 0.0;
        for (int i = 0; i < xs.length; i++) {
          if (!(xs[i] instanceof @SMO@)) continue;
          @SMO@ m = (@SMO@) xs[i];
          if (m.getCalculationType() == @CAL@.MULTIPLICATIVE) mul = mul + (double) m.getAmount();
          else add = add + (double) m.getAmount();
        }
        String low = cause.toLowerCase();
        if (mul != 0.0) parts.add(@PKG@.Gear.fnum(mul * 100.0) + "% " + low);
        if (add != 0.0) parts.add(@PKG@.Gear.fnum(add) + " " + low);
      }
      java.util.Collections.sort(parts);
      if (!parts.isEmpty()) {
        StringBuilder sb = new StringBuilder("Armor: ");
        for (int i = 0; i < parts.size(); i++) { if (i > 0) sb.append(", "); sb.append((String) parts.get(i)); }
        out.add(sb.toString());
      }
    }
  } catch (Throwable t) { }
}""")
# the gate line for an owner: Object[] { String text, String colour, Boolean inactive, String label }
M(gvw, r"""
public static Object[] gateLine(java.util.UUID owner, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  if (!@PKG@.GearDefs.enforcedKind(kind)) {
    if (gate.length() == 0) return new Object[] { "", null, Boolean.FALSE, "" };
    return new Object[] { gate + " Lv. " + need + " (coming later: gathering gear)", @PKG@.GearDefs.C_GRAY, Boolean.FALSE, gate };
  }
  Object[] c = @PKG@.GearGate.check(owner, id, d, need);
  String label = (String) c[1];
  boolean ok = ((Boolean) c[0]).booleanValue();
  int have = ((Integer) c[3]).intValue();
  int st = ((Integer) c[5]).intValue();
  if (st == 4 || st == 5 || st == 3) return new Object[] { label + " Lv. " + need, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, label };
  if (st == 2) {
    if (ok) return new Object[] { "Level " + need, @PKG@.GearDefs.C_GRAY, Boolean.FALSE, "Level" };
    return new Object[] { "Level " + need + " (skills unavailable)", @PKG@.GearDefs.C_BAD, Boolean.TRUE, "Level" };
  }
  if (st == 1) {
    if (ok) return new Object[] { label + " Lv. " + need, @PKG@.GearDefs.C_OK, Boolean.FALSE, label };
    return new Object[] { label + " Lv. " + need + " (pick a class)", @PKG@.GearDefs.C_BAD, Boolean.TRUE, label };
  }
  if (ok) return new Object[] { label + " Lv. " + need, @PKG@.GearDefs.C_OK, Boolean.FALSE, label };
  return new Object[] { label + " Lv. " + need + " (you: " + (have < 0 ? 0 : have) + ")", @PKG@.GearDefs.C_BAD, Boolean.TRUE, label };
}""")
M(gvw, r"""
public static void add(java.util.ArrayList txt, java.util.ArrayList col, String t, String c) {
  txt.add(t == null ? "" : t);
  col.add(c);
}""")
# base value lines + modifier lines of an identified document (the tooltip body, the Reforge page's line columns)
M(gvw, r"""
public static void statLines(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int slot = @PKG@.GearData.slotOf(id);
  @BA@ ms = @PKG@.GearData.mods(d);
  boolean hasDmg = false;
  int dmg = 0;
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    if ("dmg".equals(@PKG@.GearData.str(m.asDocument(), "s", ""))) { hasDmg = true; dmg = @PKG@.GearData.num(m.asDocument(), "v", 0); }
  }
  boolean dmgShown = false;
  if (slot == 0 || slot == 1) {
    String b = damageText(id);
    if (b != null) {
      add(txt, col, "Damage: " + b + (hasDmg ? " (" + valText("dmg", dmg) + ")" : ""), null);
      dmgShown = hasDmg;
    }
  } else if (slot == 2) {
    java.util.ArrayList al = new java.util.ArrayList();
    armorLines(id, al);
    for (int i = 0; i < al.size(); i++) add(txt, col, (String) al.get(i), null);
  }
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    String k = @PKG@.GearData.str(m.asDocument(), "s", "?");
    if (k.equals("dmg") && dmgShown) continue;
    int v = @PKG@.GearData.num(m.asDocument(), "v", 0);
    add(txt, col, modLine(k, v), (later(k) || slot == 3) ? @PKG@.GearDefs.C_GRAY : null);
  }
}""")
# every tooltip line below the name (spec 6.1 identified, 6.2 unidentified), for the owner (null = neutral text)
M(gvw, r"""
public static void lines(String id, @BD@ d, java.util.UUID owner, java.util.ArrayList txt, java.util.ArrayList col) {
  int r = @PKG@.GearData.rarity(d);
  int need = @PKG@.GearLevel.level(id, d);
  int slot = @PKG@.GearData.slotOf(id);
  Object[] g = gateLine(owner, id, d, need);
  String gt = (String) g[0];
  String hex = @PKG@.GearDefs.R_HEX[r];
  if (!@PKG@.GearData.identified(d)) {
    add(txt, col, "Rarity: " + @PKG@.GearDefs.R_NAME[r], hex);
    if (gt.length() > 0) add(txt, col, gt, (String) g[1]);
    add(txt, col, "Unidentified - its modifiers appear when you identify it.", @PKG@.GearDefs.C_GRAY);
    add(txt, col, slot == 2 ? "Gives no stats until identified." : "Cannot be used until identified.", @PKG@.GearDefs.C_BAD);
    add(txt, col, "Identify: /identify - " + @PKG@.Gear.fmt(@PKG@.GearCfg.costIdentify(r, need)) + " coins", @PKG@.GearDefs.C_GOLD);
    return;
  }
  statLines(id, d, txt, col);
  add(txt, col, "", null);
  if (gt.length() > 0) add(txt, col, gt, (String) g[1]);
  if (slot == 2 && ((Boolean) g[2]).booleanValue()) add(txt, col, "Gives no stats until " + g[3] + " " + need, @PKG@.GearDefs.C_BAD);
  add(txt, col, @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + slotWord(id), hex);
  String rf = @PKG@.GearData.str(d, "rf", null);
  int rfn = @PKG@.GearData.num(d, "rfN", 0);
  if (rf != null && rf.length() > 0) add(txt, col, "Reforge: " + rf + (rfn > 0 ? " (" + rfn + "x)" : ""), null);
  if (slot == 3 && gt.indexOf("coming later") < 0) add(txt, col, "(coming later: gathering gear)", @PKG@.GearDefs.C_GRAY);
}""")
M(gvw, r"""
public static String nameText(String id, @BD@ d) {
  String base = @PKG@.Gear.itemName(id);
  if (!@PKG@.GearData.identified(d)) return "Unidentified " + base;
  String rf = @PKG@.GearData.str(d, "rf", null);
  return (rf != null && rf.length() > 0 ? rf + " " : "") + base;
}""")
# Name: one raw coloured line; if the en-US name is missing or has {params} the item's translation Message is inserted (SkyyRolls)
M(gvw, r"""
public static @MSG@ nameMsg(String id, @BD@ d, String col) {
  String base = null;
  @ITM@ it = @PKG@.Gear.item(id);
  try { if (it != null) base = @PKG@.Gear.tr(it.getTranslationKey()); } catch (Throwable t) { base = null; }
  if (base != null && base.indexOf(123) < 0) return @MSG@.raw(nameText(id, d).replace(@PKG@.Gear.itemName(id), base)).color(col);
  String pre = "";
  if (!@PKG@.GearData.identified(d)) pre = "Unidentified ";
  else { String rf = @PKG@.GearData.str(d, "rf", null); if (rf != null && rf.length() > 0) pre = rf + " "; }
  @MSG@ m = @MSG@.empty().color(col);
  if (pre.length() > 0) m.insert(@MSG@.raw(pre).color(col));
  try { m.insert(it.getTranslationMessage().color(col)); } catch (Throwable t) { m.insert(@MSG@.raw(@PKG@.Gear.pretty(id)).color(col)); }
  return m;
}""")
M(gvw, r"""
public static boolean hasDesc(String id) {
  try { @ITM@ it = @PKG@.Gear.item(id); return it != null && @PKG@.Gear.tr(it.getDescriptionTranslationKey()) != null; } catch (Throwable t) { return false; }
}""")
M(gvw, r"""
public static @MSG@ descMsg(String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  @MSG@ m = @MSG@.empty();
  if (@PKG@.GearData.identified(d) && hasDesc(id)) {
    try {
      m.insert(@PKG@.Gear.item(id).getDescriptionTranslationMessage().color(@PKG@.GearDefs.C_GRAY));
      m.insert(@MSG@.raw("\n\n"));
    } catch (Throwable t) { }
  }
  for (int i = 0; i < txt.size(); i++) {
    if (i > 0) m.insert(@MSG@.raw("\n"));
    String t = (String) txt.get(i);
    if (t.length() == 0) continue;
    String c = (String) col.get(i);
    m.insert(c == null ? @MSG@.raw(t) : @MSG@.raw(t).color(c));
  }
  return m;
}""")
# spec 6.3 sig: item id, stack quality, document JSON, resolved level, every rendered line (base values + the owner lines exactly as
# shown, colour and "(you: N)" included), config epoch - a change the player can see re-renders the item, nothing else does
M(gvw, r"""
public static String sig(String id, int quality, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < txt.size(); i++) sb.append((String) txt.get(i)).append('|').append(String.valueOf(col.get(i))).append('\n');
  return @PKG@.GearDefs.VIEW_V + ":" + id + ":" + quality + ":" + Integer.toHexString(d.toJson().hashCode()) + ":"
    + Integer.toHexString(sb.toString().hashCode()) + ":" + @PKG@.GearLevel.level(id, d) + ":" + @PKG@.GearCfg.cfgEpoch() + ":" + (hasDesc(id) ? 1 : 0);
}""")
# fingerprint of the stack's CURRENT ItemDisplay through the engine codec (SkyyRolls dispHash); null = none / unreadable
M(gvw, r"""
public static String dispHash(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return null;
    Object o = s.getFromMetadataOrNull(@IDM@.KEYED_CODEC);
    if (o == null) return null;
    @BD@ md = s.withMetadata(@IDM@.KEYED_CODEC, o).getMetadata();
    @BV@ v = md == null ? null : md.get(@IDM@.KEY);
    if (v == null || !v.isDocument()) return null;
    return Integer.toHexString(v.asDocument().toJson().hashCode());
  } catch (Throwable t) { return null; }
}""")
M(gvw, r"""
public static boolean ours(@IS@ s, @BD@ view) {
  if (view == null) return false;
  @BV@ h = view.get("disp");
  if (h == null || !h.isString()) return false;
  String now = dispHash(s);
  return now != null && now.equals(h.asString().getValue());
}""")
# the one writer (spec 1.1, 6.4): document + quality + ItemDisplayMetadata + our SkyyGearView marker {v, sig, disp, prev}. Returns
# the SAME object when nothing the player can see would change (callers compare with ==). prev = the display from before SkyyGear.
M(gvw, r"""
public static @IS@ apply(@IS@ s, @BD@ doc, java.util.UUID owner) {
  String id = "?";
  try {
    if (s == null || s.isEmpty() || doc == null) return s;
    id = s.getItemId();
    @BD@ md = s.getMetadata();
    int r = @PKG@.GearData.rarity(doc);
    int q = @PKG@.GearDefs.qIndex(r);
    int curQ = @PKG@.Gear.quality(s);
    int wantQ = q >= 0 ? q : curQ;
    java.util.ArrayList txt = new java.util.ArrayList();
    java.util.ArrayList col = new java.util.ArrayList();
    lines(id, doc, owner, txt, col);
    String sg = sig(id, wantQ, doc, txt, col);
    @BV@ cur = md == null ? null : md.get(@PKG@.GearDefs.DOC_KEY);
    boolean sameDoc = cur != null && cur.isDocument() && cur.asDocument().toJson().equals(doc.toJson());
    @BV@ view = md == null ? null : md.get(@PKG@.GearDefs.VIEW_KEY);
    if (sameDoc && wantQ == curQ && view != null && view.isDocument() && md.containsKey(@IDM@.KEY)) {
      @BV@ g = view.asDocument().get("sig");
      if (g != null && g.isString() && g.asString().getValue().equals(sg) && ours(s, view.asDocument())) return s;
    }
    @BV@ keep = null;
    @BV@ curD = md == null ? null : md.get(@IDM@.KEY);
    if (view != null && view.isDocument() && ours(s, view.asDocument())) {
      @BV@ p = view.asDocument().get("prev");
      if (p != null && !p.isNull()) keep = p;
    } else if (curD != null && !curD.isNull()) keep = curD;
    @IS@ out = s;
    if (!sameDoc) out = out.withMetadata(@PKG@.GearDefs.DOC_KEY, (@BV@) doc);
    if (q >= 0 && wantQ != curQ) out = out.withQuality(q);
    String hex = @PKG@.GearDefs.R_HEX[r];
    out = out.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(nameMsg(id, doc, hex), descMsg(id, doc, txt, col)));
    @BD@ nv = new @BD@();
    nv.append("v", new org.bson.BsonInt32(@PKG@.GearDefs.VIEW_V));
    nv.append("sig", new org.bson.BsonString(sg));
    String h = dispHash(out);
    if (h != null) nv.append("disp", new org.bson.BsonString(h));
    if (keep != null) nv.append("prev", keep);
    return out.withMetadata(@PKG@.GearDefs.VIEW_KEY, (@BV@) nv);
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("apply:" + id, "could not write the gear tooltip for " + id + ": " + t);
    return s;
  }
}""")
# plain lines (bridge gear:fn:describe, /gear, the page): name line first, neutral owner text when owner is null
M(gvw, r"""
public static String[] plain(String id, @BD@ d, java.util.UUID owner) {
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  txt.add(nameText(id, d));
  col.add(null);
  lines(id, d, owner, txt, col);
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < txt.size(); i++) { String t = (String) txt.get(i); if (t.length() > 0) out.add(t); }
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
# one line of the modifiers ("Strength +12 - Crit Chance +5%"); "" when none
M(gvw, r"""
public static String modSummary(@BD@ d) {
  @BA@ ms = @PKG@.GearData.mods(d);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    String k = @PKG@.GearData.str(m.asDocument(), "s", "?");
    int v = @PKG@.GearData.num(m.asDocument(), "v", 0);
    int si = @PKG@.GearDefs.sIndex(k);
    if (sb.length() > 0) sb.append(" - ");
    sb.append(si >= 0 ? @PKG@.GearDefs.S_LABEL[si] : k).append(' ').append(valText(k, v));
  }
  return sb.toString();
}""")
# spec 7.1 gear:fn:rollsLine: "Rare - Lv 20 - Strength +12 - Crit Chance +5%"; "" for a Normal with no modifiers
M(gvw, r"""
public static String rollsLine(String id, @BD@ d) {
  int r = @PKG@.GearData.rarity(d);
  int lv = @PKG@.GearLevel.level(id, d);
  if (!@PKG@.GearData.identified(d)) return "Unidentified (" + @PKG@.GearDefs.R_NAME[r] + ", Lv " + lv + ")";
  String ms = modSummary(d);
  if (r == 0 && ms.length() == 0) return "";
  return @PKG@.GearDefs.R_NAME[r] + " - Lv " + lv + (ms.length() > 0 ? " - " + ms : "");
}""")
# spec 7.1 gear:fn:sig: item id + stack quality + rarity + identify state + modifiers (review E4)
M(gvw, r"""
public static String bridgeSig(String id, int quality, @BD@ d) {
  String s = id + "|" + quality + "|" + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)] + "|" + @PKG@.GearData.identified(d) + "|" + @PKG@.GearData.mods(d).toString();
  return Integer.toHexString(s.hashCode()) + Integer.toHexString(s.length());
}""")

# ================================================================= GearData (2/2): writes (every rewrite goes through GearView.apply)
# drop the SkyyRolls keys of a stack being migrated; when the ItemDisplay on it is still SkyyRolls' tooltip, the display from before
# SkyyRolls comes back first, so GearView.apply stores THAT as prev (spec 1.6: view prev = the old SkyyRollsView.prev)
M(gdt, r"""
public static @IS@ dropRolls(@IS@ s) {
  @BD@ md = s.getMetadata();
  if (md == null) return s;
  @BD@ c = (@BD@) md.clone();
  c.remove(@PKG@.GearDefs.ROLLS_KEY);
  @BV@ rv = (@BV@) c.remove(@PKG@.GearDefs.ROLLS_VIEW);
  if (rv != null && rv.isDocument()) {
    @BV@ h = rv.asDocument().get("disp");
    String now = @PKG@.GearView.dispHash(s);
    if (h != null && h.isString() && now != null && now.equals(h.asString().getValue())) {
      @BV@ p = rv.asDocument().get("prev");
      if (p != null && !p.isNull()) c.put(@IDM@.KEY, p);
      else c.remove(@IDM@.KEY);
    }
  }
  if (c.isEmpty()) return s.withMetadata((@BD@) null);
  return s.withMetadata(c);
}""")
M(gdt, r"""
public static @IS@ put(@IS@ s, @BD@ doc, java.util.UUID owner) {
  if (s == null || s.isEmpty() || doc == null) return s;
  @IS@ x = s;
  @BD@ md = x.getMetadata();
  if (md != null && md.containsKey(@PKG@.GearDefs.ROLLS_KEY)) x = dropRolls(x);
  return @PKG@.GearView.apply(x, doc, owner);
}""")
# /gear clear: SkyyGear data and our tooltip go, the display from before SkyyGear comes back, the item's own quality returns
M(gdt, r"""
public static @IS@ clear(@IS@ s) {
  @BD@ md = s.getMetadata();
  @IS@ out = s;
  if (md != null) {
    @BD@ c = (@BD@) md.clone();
    c.remove(@PKG@.GearDefs.DOC_KEY);
    @BV@ view = (@BV@) c.remove(@PKG@.GearDefs.VIEW_KEY);
    if (view != null && view.isDocument() && @PKG@.GearView.ours(s, view.asDocument())) {
      @BV@ prev = view.asDocument().get("prev");
      if (prev != null && !prev.isNull()) c.put(@IDM@.KEY, prev);
      else c.remove(@IDM@.KEY);
    }
    out = c.isEmpty() ? s.withMetadata((@BD@) null) : s.withMetadata(c);
  }
  return out.withQuality(Integer.MIN_VALUE);
}""")

# ================================================================= GearStats: the player's active totals (PART B applies them)
# T = the main-hand weapon's modifiers + every active armor piece's (weapon-only stats only from the weapon; spec 4.3). Active =
# identified and the gate passes (3.4 / 3.5). World thread (reads the inventory).
M(gst, r"""
public static @IS@ hand(@INV@ inv) {
  try {
    if (inv.usingToolsItem()) {
      @IC@ t = inv.getTools();
      int ts = inv.getActiveToolsSlot();
      return t == null || ts < 0 || ts >= t.getCapacity() ? null : t.getItemStack((short) ts);
    }
    @IC@ h = inv.getHotbar();
    int hs = inv.getActiveHotbarSlot();
    return h == null || hs < 0 || hs >= h.getCapacity() ? null : h.getItemStack((short) hs);
  } catch (Throwable t) { return null; }
}""")
M(gst, r"""
public static boolean active(java.util.UUID u, String id, @BD@ d) {
  if (d == null || !@PKG@.GearData.identified(d)) return false;
  Object[] c = @PKG@.GearGate.check(u, id, d, @PKG@.GearLevel.level(id, d));
  return ((Boolean) c[0]).booleanValue();
}""")
M(gst, r"""
public static void addMods(int[] t, @BD@ d, boolean armor) {
  @BA@ ms = @PKG@.GearData.mods(d);
  for (int i = 0; i < ms.size(); i++) {
    @BV@ m = ms.get(i);
    if (m == null || !m.isDocument()) continue;
    int si = @PKG@.GearDefs.sIndex(@PKG@.GearData.str(m.asDocument(), "s", ""));
    if (si < 0) continue;
    if (armor && @PKG@.GearDefs.S_SLOT[si].indexOf('a') < 0) continue;
    t[si] = t[si] + @PKG@.GearData.num(m.asDocument(), "v", 0);
  }
}""")
M(gst, r"""
public static int[] totals(java.util.UUID u, @INV@ inv) {
  int[] t = new int[@PKG@.GearDefs.NS];
  if (inv == null) return t;
  @IS@ h = hand(inv);
  if (h != null && !h.isEmpty()) {
    String id = h.getItemId();
    int sl = @PKG@.GearData.slotOf(id);
    if (sl == 0 || sl == 1) {
      @BD@ d = @PKG@.GearData.effective(id, h.getMetadata());
      if (active(u, id, d)) addMods(t, d, false);
    }
  }
  @IC@ a = inv.getArmor();
  if (a != null) {
    for (int i = 0; i < a.getCapacity(); i++) {
      @IS@ s = a.getItemStack((short) i);
      if (s == null || s.isEmpty() || @PKG@.GearData.slotOf(s.getItemId()) != 2) continue;
      @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
      if (active(u, s.getItemId(), d)) addMods(t, d, true);
    }
  }
  return t;
}""")
M(gst, r"""
public static String statsString(int[] t) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < t.length && i < @PKG@.GearDefs.NS; i++) {
    if (t[i] == 0) continue;
    if (sb.length() > 0) sb.append(',');
    sb.append(@PKG@.GearDefs.S_KEY[i]).append(':').append(t[i]);
  }
  return sb.toString();
}""")

# ================================================================= GearNotice: players/<pkey>.properties noticeShown (spec 8.2)
gnt.addInterface(pool.get("java.lang.Runnable"))
F(gnt, "public static final java.util.concurrent.ConcurrentHashMap SHOWN = new java.util.concurrent.ConcurrentHashMap();")
F(gnt, "public String key;")
C(gnt, "public GearNotice(String key) { this.key = key; }")
M(gnt, r"""
public static java.nio.file.Path file(String pkey) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pkey == null || pkey.length() == 0) return null;
  return d.resolve("players").resolve(pkey.replace('/', '_').replace('\\', '_').replace(':', '_') + ".properties");
}""")
M(gnt, r"""
public static boolean shown(String pkey) {
  Object o = SHOWN.get(pkey);
  if (o instanceof Boolean) return ((Boolean) o).booleanValue();
  boolean v = false;
  try {
    java.nio.file.Path f = file(pkey);
    if (f != null && java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) v = "true".equalsIgnoreCase(@PKG@.GearCfg.read(f).getProperty("noticeShown", "false").trim());
  } catch (Throwable t) { v = false; }
  SHOWN.put(pkey, Boolean.valueOf(v));
  return v;
}""")
M(gnt, r"""
public void run() {
  try {
    java.nio.file.Path f = file(this.key);
    if (f != null) @PKG@.GearCfg.writeAtomic(f, "# SkyyGear player flags\nnoticeShown=true\n", true);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("notice", "could not write a players/ notice file: " + t); }
}""")
M(gnt, r"""
public static void mark(String pkey) {
  if (pkey == null) return;
  SHOWN.put(pkey, Boolean.TRUE);
  try { @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearNotice(pkey), 200L, java.util.concurrent.TimeUnit.MILLISECONDS); } catch (Throwable t) { }
}""")

# ================================================================= GearStamp (spec 1.5): legacy stamp, migration, re-render, pending crafts
F(gsp, "public static final int[] SCAN = new int[] { 0, 3, 5, 4, 1, 2 };")   # hotbar, armor, tools, utility, storage, backpack
F(gsp, 'public static final String[] SEC_NAME = new String[] { "Hotbar", "Inventory", "Backpack", "Armor", "Utility", "Tools" };')
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap PENDING = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> ConcurrentHashMap(id -> Long)
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap QUEUED = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(gsp, "public static final java.util.concurrent.ConcurrentHashMap RATE = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> long[]{windowStart, writes, pausedUntil}
M(gsp, r"""
public static @IC@ section(@INV@ inv, int s) {
  if (inv == null) return null;
  if (s == 0) return inv.getHotbar();
  if (s == 1) return inv.getStorage();
  if (s == 2) return inv.getBackpack();
  if (s == 3) return inv.getArmor();
  if (s == 4) return inv.getUtility();
  if (s == 5) return inv.getTools();
  return null;
}""")
M(gsp, r"""
public static @IS@ at(@INV@ inv, int s, int slot) {
  @IC@ c = section(inv, s);
  if (c == null || slot < 0 || slot >= c.getCapacity()) return null;
  return c.getItemStack((short) slot);
}""")
M(gsp, r"""
public static void pendingAdd(java.util.UUID u, String id) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) PENDING.get(u);
  if (m == null) { m = new java.util.concurrent.ConcurrentHashMap(); Object o = PENDING.putIfAbsent(u, m); if (o != null) m = (java.util.concurrent.ConcurrentHashMap) o; }
  m.put(id, Long.valueOf(System.currentTimeMillis()));
}""")
M(gsp, r"""
public static void pendingClear(java.util.UUID u, String id) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) PENDING.get(u);
  if (m != null) m.remove(id);
}""")
# true = stacks of this item id are held back from the stamp (a craft of it is pending and younger than PENDING_MAX_MS)
M(gsp, r"""
public static boolean held(java.util.UUID u, String id) {
  java.util.concurrent.ConcurrentHashMap m = (java.util.concurrent.ConcurrentHashMap) PENDING.get(u);
  if (m == null) return false;
  Object t = m.get(id);
  if (!(t instanceof Long)) return false;
  if (System.currentTimeMillis() - ((Long) t).longValue() < @PKG@.GearDefs.PENDING_MAX_MS) return true;
  m.remove(id);
  @PKG@.Gear.info("a pending craft of " + id + " expired unrolled - it is stamped Normal");
  return false;
}""")
# one stack -> the stack it should be (same object = nothing to do). cnt: [0] stamped Normal, [1] migrated, [2] re-rendered
M(gsp, r"""
public static @IS@ stampStack(@IS@ s, java.util.UUID owner, int[] cnt) {
  if (s == null || s.isEmpty()) return s;
  String id = s.getItemId();
  @BD@ md = s.getMetadata();
  int st = @PKG@.GearData.state(md);
  if (!@PKG@.GearData.gearish(id, md)) return s;
  if (st == 3 || st == 4) {
    @PKG@.Gear.warnOnce("unread:" + id + ":" + (md == null ? 0 : md.toJson().hashCode()), (st == 4 ? "gear data of a newer SkyyGear on " : "Gear data unreadable on ") + id + " - left untouched");
    return s;
  }
  if (st == 0 && !@PKG@.GearData.isGear(id)) return s;
  @BD@ doc;
  if (st == 1) doc = @PKG@.GearData.gearDoc(md);
  else if (st == 2) doc = @PKG@.GearData.migrate(id, @PKG@.GearData.rollsDoc(md));
  else doc = @PKG@.GearData.legacy(id);
  @IS@ out = @PKG@.GearData.put(s, doc, owner);
  if (out != s && cnt != null) {
    if (st == 0) cnt[0] = cnt[0] + 1;
    else if (st == 2) cnt[1] = cnt[1] + 1;
    else cnt[2] = cnt[2] + 1;
  }
  return out;
}""")
M(gsp, r"""
public static void notice(@PR@ pr, int migrated) {
  try {
    java.util.UUID u = pr.getUuid();
    String pk = @PKG@.Gear.pkey(u);
    if (@PKG@.GearNotice.shown(pk)) return;
    @PKG@.GearNotice.mark(pk);
    if (!@PKG@.Gear.notifyOn(u, "gear.notices")) return;
    pr.sendMessage(@MSG@.raw("[Gear] Your old rolled items moved to the new gear system: " + migrated + " item(s) kept their rolls and got a rarity from how strong they are. /gear shows the item in your hand.").color(@PKG@.GearDefs.C_LABEL));
  } catch (Throwable t) { }
}""")
# safety valve (not in the spec): more than 300 stack rewrites for one player within 10 s means something keeps undoing our writes
# (e.g. an engine path that normalises the quality we set) - the stamp pauses 30 s for that player instead of looping, one WARN
M(gsp, r"""
public static boolean paused(java.util.UUID u, int wrote) {
  long now = System.currentTimeMillis();
  long[] r = (long[]) RATE.get(u);
  if (r == null) { r = new long[] { now, 0L, 0L }; RATE.put(u, r); }
  if (r[2] > now) return true;
  if (now - r[0] > 10000L) { r[0] = now; r[1] = 0L; }
  r[1] = r[1] + (long) wrote;
  if (r[1] > 300L) {
    r[2] = now + 30000L;
    r[1] = 0L;
    @PKG@.Gear.warnOnce("rate:" + u, "the gear stamp rewrote more than 300 stacks of one player within 10 s - paused 30 s for that player (an engine path may be undoing the writes)");
    return true;
  }
  return false;
}""")
# the scan (world thread): the 6 sections in SkyyRolls' order; never while profile:busy; pending crafts hold back only undocumented
# stacks of their own item id (review E3)
M(gsp, r"""
public static int[] scan(@PR@ pr, @INV@ inv) {
  int[] cnt = new int[3];
  if (pr == null || inv == null) return cnt;
  java.util.UUID u = pr.getUuid();
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  if (@PKG@.Gear.busy(u) || paused(u, 0)) return cnt;
  for (int k = 0; k < SCAN.length; k++) {
    @IC@ c = section(inv, SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      if (@PKG@.GearData.state(s.getMetadata()) == 0 && held(u, s.getItemId())) continue;
      @IS@ ns = stampStack(s, u, cnt);
      if (ns == s) continue;
      try { c.setItemStackForSlot((short) i, ns); } catch (Throwable t) { @PKG@.Gear.warnOnce("scanset", "stamp write failed: " + t); }
    }
  }
  paused(u, cnt[0] + cnt[1] + cnt[2]);
  if (cnt[1] > 0) {
    notice(pr, cnt[1]);
    @PKG@.GearLog.line("MIGRATE " + pr.getUsername() + " " + u + " migrated=" + cnt[1] + " stamped=" + cnt[0]);
  }
  return cnt;
}""")
M(gsp, r"""
public static @INV@ invOf(@PR@ pr) {
  try {
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return null;
    @ST@ st = r.getStore();
    if (st == null) return null;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p == null ? null : p.getInventory();
  } catch (Throwable t) { return null; }
}""")
M(gsp, "public static void forget(java.util.UUID u) { if (u != null) { PENDING.remove(u); QUEUED.remove(u); LAST.remove(u); RATE.remove(u); } }")

# ================================================================= GearStampTask: one coalesced scan (<= every 250 ms per player)
gspt.addInterface(pool.get("java.lang.Runnable"))
F(gspt, "public @PR@ pr;")
F(gspt, "public boolean onWorld;")
F(gspt, "public java.util.UUID hop;")
C(gspt, "public GearStampTask(@PR@ pr, boolean onWorld, java.util.UUID hop) { this.pr = pr; this.onWorld = onWorld; this.hop = hop; }")
M(gspt, r"""
public void run() {
  java.util.UUID u = null;
  try {
    if (this.pr == null || !this.pr.isValid()) { if (this.pr != null) @PKG@.GearStamp.QUEUED.remove(this.pr.getUuid()); return; }
    u = this.pr.getUuid();
    if (!this.onWorld) {
      java.util.UUID wu = this.pr.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.GearStamp.QUEUED.remove(u); return; }
      this.onWorld = true;
      this.hop = wu;
      w.execute(this);
      return;
    }
    @PKG@.GearStamp.QUEUED.remove(u);
    java.util.UUID now = this.pr.getWorldUuid();
    if (this.hop != null && (now == null || !now.equals(this.hop))) return;
    @PKG@.GearStamp.scan(this.pr, @PKG@.GearStamp.invOf(this.pr));
  } catch (Throwable t) {
    if (u != null) @PKG@.GearStamp.QUEUED.remove(u);
    @PKG@.Gear.warnOnce("stamptask", "stamp scan failed: " + t);
  }
}""")
M(gsp, r"""
public static void dirty(@PR@ pr, @WLD@ w) {
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  if (QUEUED.putIfAbsent(u, Boolean.TRUE) != null) return;
  try {
    Object l = LAST.get(u);
    long wait = (l instanceof Long ? ((Long) l).longValue() : 0L) + @PKG@.GearDefs.SCAN_GAP_MS - System.currentTimeMillis();
    if (wait <= 0L && w != null) w.execute(new @PKG@.GearStampTask(pr, true, pr.getWorldUuid()));
    else @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GearStampTask(pr, false, null), wait < 1L ? 1L : wait, java.util.concurrent.TimeUnit.MILLISECONDS);
  } catch (Throwable t) { QUEUED.remove(u); }
}""")

# ================================================================= GearForge: the reforge core (spec 5.4 + write safety 1.7)
# what must still be in the slot for a click to go through: same id, quality, gear / rolls document and durability
M(gfg, r"""
public static String fp(@IS@ it) {
  if (it == null || it.isEmpty()) return "";
  @BD@ md = it.getMetadata();
  @BV@ g = @PKG@.GearData.getv(md, @PKG@.GearDefs.DOC_KEY);
  @BV@ r = @PKG@.GearData.getv(md, @PKG@.GearDefs.ROLLS_KEY);
  String dj = g != null && g.isDocument() ? g.asDocument().toJson() : (r != null && r.isDocument() ? "R" + r.asDocument().toJson() : "none");
  return it.getItemId() + "|" + @PKG@.Gear.quality(it) + "|" + Integer.toHexString(dj.hashCode()) + "|" + (long) it.getDurability();
}""")
M(gfg, r"""
public static boolean same(@IS@ it, String id, String f) {
  if (it == null || it.isEmpty() || id == null || f == null) return false;
  return id.equals(it.getItemId()) && f.equals(fp(it));
}""")
M(gfg, r"""
public static java.util.ArrayList rows(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });
    }
  }
  return out;
}""")
M(gfg, r"""
public static String where(int s, int slot) {
  if (s < 0 || s >= @PKG@.GearStamp.SEC_NAME.length) return "inventory";
  return @PKG@.GearStamp.SEC_NAME[s] + " " + (slot + 1);
}""")
# SkyyCoins 0.1.5 bridge (SkyyRolls Reforge.purse / take / refund): 1 taken, 0 not enough, -1 coins unavailable
M(gfg, r"""
public static long purse(java.util.UUID u) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("coins:fn:get");
    if (f == null) return -1L;
    Object r = f.apply(u);
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { @PKG@.Gear.warn("coins:fn:get failed: " + t); }
  return -1L;
}""")
M(gfg, r"""
public static int take(java.util.UUID u, long amt) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("coins:fn:take");
    if (f == null) return -1;
    Object r = f.apply(new Object[] { u, Long.valueOf(amt) });
    if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  } catch (Throwable t) { @PKG@.Gear.warn("coins:fn:take failed: " + t); }
  return -1;
}""")
M(gfg, r"""
public static boolean refund(java.util.UUID u, long amt) {
  try {
    java.util.function.Function f = @PKG@.Gear.fn("coins:fn:add");
    if (f == null) return false;
    Object r = f.apply(new Object[] { u, Long.valueOf(amt) });
    return r instanceof Number;
  } catch (Throwable t) { @PKG@.Gear.warn("coins:fn:add (refund) failed: " + t); }
  return false;
}""")
# why a stack cannot be reforged (null = it can); spec 5.4 "Which items"
M(gfg, r"""
public static String refuse(@IS@ it, @BD@ d) {
  if (it == null || it.isEmpty()) return "Pick a weapon or armor piece first.";
  String id = it.getItemId();
  if (@PKG@.GearData.isTool(id)) return "Tools get their own modifiers with gathering gear - they cannot be reforged yet.";
  if (!@PKG@.GearData.isGear(id)) return @PKG@.Gear.itemName(id) + " is not gear - only weapons and armor can be reforged.";
  int st = @PKG@.GearData.state(it.getMetadata());
  if (st == 3) return "The gear data on this item is unreadable - an admin can check it with /gear read.";
  if (st == 4) return "This item comes from a newer SkyyGear - it cannot be changed here.";
  if (d == null) return "The gear data on this item is unreadable.";
  if (!@PKG@.GearData.identified(d)) return "Identify it first: /identify";
  if (it.getQuantity() > 1) return "A reforge works on one item at a time - split this stack of " + it.getQuantity() + " first.";
  return null;
}""")
# Object[] { Integer code (1 done, 0 refused, -1 failed + refunded / not refunded), String message, IS newStack, BD before,
#            BD after, Long cost }. Coins TAKEN FIRST, REFUND on any failure; the new stack replaces the old one in the same slot.
M(gfg, r"""
public static Object[] reforge(@IC@ c, int slot, String expId, String expFp, java.util.UUID u, String who, boolean free) {
  @IS@ it = null;
  try { if (c != null && slot >= 0 && slot < c.getCapacity()) it = c.getItemStack((short) slot); } catch (Throwable t0) { it = null; }
  if (!same(it, expId, expFp)) return new Object[] { Integer.valueOf(0), "That item moved or changed - pick it again.", null, null, null, Long.valueOf(0L) };
  String id = it.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
  String why = refuse(it, d);
  if (why != null) return new Object[] { Integer.valueOf(0), why, null, null, null, Long.valueOf(0L) };
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  long cost = free ? 0L : @PKG@.GearCfg.costReforge(r, lvl);
  if (cost > 0L) {
    int t = take(u, cost);
    if (t < 0) return new Object[] { Integer.valueOf(0), "Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken.", null, null, null, Long.valueOf(0L) };
    if (t == 0) {
      long have = purse(u);
      return new Object[] { Integer.valueOf(0), "Not enough coins: this reforge costs " + @PKG@.Gear.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Gear.fmt(have) : "") + ".", null, null, null, Long.valueOf(0L) };
    }
    @PKG@.GearLog.line("TAKE " + who + " " + u + " " + cost + " reforge " + id);
  }
  @BD@ nd = null;
  @IS@ nu = null;
  Object tx = null;
  Throwable err = null;
  try {
    nd = @PKG@.GearRoll.reforge(id, d);
    nu = @PKG@.GearData.put(it, nd, u);
    tx = c.setItemStackForSlot((short) slot, nu);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && nu != null && nu != it && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Gear.warn("REFORGE FAILED for " + who + " (" + u + ") on " + id + ": " + what + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    if (cost > 0L) @PKG@.GearLog.line((back ? "REFUND " : "REFUND-FAILED ") + who + " " + u + " " + cost + " reforge " + id + ": " + what);
    return new Object[] { Integer.valueOf(-1), back ? "The reforge failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Gear.fmt(cost) + " coins were refunded." : ".") : "The reforge failed and the refund did not go through - an admin can find it in the server log.", null, d, null, Long.valueOf(cost) };
  }
  if (!free) {
    long xp = @PKG@.GearCfg.xpReforge(r);
    if (xp > 0L) {
      try {
        java.util.function.Function f = @PKG@.Gear.fn("skill:fn:addxp");
        if (f != null) f.apply(new Object[] { u, "Smithing", Long.valueOf(xp), "gear:reforge", @PKG@.Gear.pkey(u) });
      } catch (Throwable t) { @PKG@.Gear.warnOnce("addxp", "skill:fn:addxp failed: " + t); }
    }
  }
  @PKG@.GearLog.line("REFORGE " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r] + " lv" + lvl + " [" + @PKG@.GearView.modSummary(d) + "] -> [" + @PKG@.GearView.modSummary(nd) + "] cost " + cost + " rfN " + @PKG@.GearData.num(nd, "rfN", 0) + (free ? " (admin, free)" : ""));
  return new Object[] { Integer.valueOf(1), "Reforged!", nu, d, nd, Long.valueOf(cost) };
}""")

# ================================================================= GearFn: bridge functions (spec 7.1). Never throw, never touch ECS.
gfn.addInterface(pool.get("java.util.function.Function"))
F(gfn, "public int mode;")
C(gfn, "public GearFn(int mode) { this.mode = mode; }")
# X = an ItemStack or Object[]{String itemId, BsonDocument metadata} -> Object[]{ String id, BsonDocument md, Integer quality }
M(gfn, r"""
public static Object[] x(Object o) {
  if (o instanceof @IS@) {
    @IS@ s = (@IS@) o;
    if (s.isEmpty()) return null;
    return new Object[] { s.getItemId(), s.getMetadata(), Integer.valueOf(@PKG@.Gear.quality(s)) };
  }
  if (o instanceof Object[]) {
    Object[] a = (Object[]) o;
    if (a.length < 1 || !(a[0] instanceof String)) return null;
    @BD@ md = a.length > 1 && a[1] instanceof @BD@ ? (@BD@) a[1] : null;
    return new Object[] { a[0], md, Integer.valueOf(Integer.MIN_VALUE) };
  }
  return null;
}""")
M(gfn, r"""
public static @BD@ docOf(Object[] xs) {
  if (xs == null) return null;
  String id = (String) xs[0];
  @BD@ md = (@BD@) xs[1];
  if (!@PKG@.GearData.gearish(id, md)) return null;
  return @PKG@.GearData.effective(id, md);
}""")
M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 6) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 2) return null;
      Object[] a = (Object[]) o;
      java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
      Object[] xs = x(a[1]);
      @BD@ d = docOf(xs);
      if (d == null) return null;
      String id = (String) xs[0];
      Object[] c = @PKG@.GearGate.check(u, id, d, @PKG@.GearLevel.level(id, d));
      boolean enf = ((Boolean) c[4]).booleanValue() && @PKG@.GearCfg.PART_GATE;
      return new Object[] { c[0], c[1], c[2], c[3], Boolean.valueOf(enf) };
    }
    if (m == 7) {
      Object v = o instanceof java.util.UUID ? @PKG@.Gear.bget("gear:stats:" + o) : null;
      return v instanceof String ? v : "";
    }
    if (m == 8) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 4) return null;
      Object[] a = (Object[]) o;
      java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
      String id = a[1] instanceof String ? (String) a[1] : null;
      int n = a[2] instanceof Number ? ((Number) a[2]).intValue() : 1;
      String src = a[3] instanceof String ? (String) a[3] : "craft";
      if (id == null || !@PKG@.GearData.isGear(id) || !@PKG@.GearCfg.PART_CRAFT) return null;
      // never more stacks than were crafted (SkyySacks 0.7.7 refuses an answer above count); above 64 the caller gives the rest plain
      if (n < 1) return null;
      if (n > 64) n = 64;
      Object[] out = new Object[n];
      for (int i = 0; i < n; i++) {
        @BD@ d = "craft".equals(src) ? @PKG@.GearRoll.craftDoc(id, u) : @PKG@.GearRoll.newDoc(id, @PKG@.GearRoll.pickRarity(0), true, src);
        out[i] = @PKG@.GearData.put(new @IS@(id, 1), d, u);
      }
      @PKG@.GearLog.line("ROLL bridge " + src + " " + u + " " + id + " x" + n + (a.length > 4 && a[4] != null ? " recipe " + a[4] : ""));
      return out;
    }
    if (m == 9) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 2 || !(((Object[]) o)[0] instanceof @IS@)) return o instanceof Object[] && ((Object[]) o).length > 0 ? ((Object[]) o)[0] : null;
      Object[] a = (Object[]) o;
      @IS@ s = (@IS@) a[0];
      String src = a[1] instanceof String ? (String) a[1] : "";
      if (s.isEmpty() || !@PKG@.GearData.isGear(s.getItemId()) || @PKG@.GearData.hasAnyDoc(s.getMetadata())) return s;
      int col = "mob".equals(src) ? 1 : ("chest".equals(src) ? 2 : 0);
      if (col == 0) return s;
      if (col == 1 && !@PKG@.GearCfg.PART_DROPS) return s;
      if (col == 2 && !@PKG@.GearCfg.PART_CHESTS) return s;
      return @PKG@.GearData.put(s, @PKG@.GearRoll.unidDoc(s.getItemId(), col, col == 1 ? "drop" : "chest"), null);
    }
    Object[] xs = x(o);
    @BD@ d = docOf(xs);
    if (d == null) {
      if (m == 0 && xs != null && @PKG@.GearData.gearish((String) xs[0], (@BD@) xs[1])) {
        int st = @PKG@.GearData.state((@BD@) xs[1]);
        if (st == 3) return new String[] { @PKG@.Gear.itemName((String) xs[0]), "Gear data unreadable" };
        if (st == 4) return new String[] { @PKG@.Gear.itemName((String) xs[0]), "Gear data from a newer SkyyGear (read only)" };
      }
      return null;
    }
    String id = (String) xs[0];
    if (m == 0) return @PKG@.GearView.plain(id, d, null);
    if (m == 1) return @PKG@.GearView.rollsLine(id, d);
    if (m == 2) return @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)];
    if (m == 3) return Integer.valueOf(@PKG@.GearLevel.level(id, d));
    if (m == 4) return Boolean.valueOf(@PKG@.GearData.identified(d));
    if (m == 5) return @PKG@.GearView.bridgeSig(id, ((Integer) xs[2]).intValue(), d);
    return null;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("fn" + this.mode, "bridge function " + this.mode + " failed: " + t);
    return null;
  }
}""")

# ================================================================= systems (one registerSystem per class)
def event_system(cls, ctor, event_cls, query, body):
    C(cls, "public %s() { super(%s.class); }" % (ctor, event_cls))
    M(cls, "public @QRY@ getQuery() { return %s; }" % query)
    M(cls, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
%s
  } catch (Throwable t) { @PKG@.Gear.warnOnce("%s", "%s failed: " + t); }
}""" % (body, ctor, ctor))


PLAYER_Q = "(@QRY@) @PLA@.getComponentType()"
# spec 1.5: InventoryChangeEvent (the ECS event SkyySkills' SmeltSys uses) marks the player dirty; one coalesced scan <= 250 ms
event_system(ginv, "GearInvSys", ICE, PLAYER_Q, r"""
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
    @PKG@.GearStamp.dirty(pr, w);""")
# spec 1.5 GearThrowSys: ItemUtils.throwItem fires the cancellable DropItemEvent$Drop on the dropping entity, then spawns whatever stack
# the event holds (VERIFIED bytecode): a player-thrown undocumented gear stack is stamped here, before the item entity exists
event_system(gthr, "GearThrowSys", DIE, PLAYER_Q, r"""
    @DIE@ e = (@DIE@) ev;
    if (e.isCancelled()) return;
    @IS@ s = e.getItemStack();
    if (s == null || s.isEmpty() || !@PKG@.GearData.gearish(s.getItemId(), s.getMetadata())) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @IS@ ns = @PKG@.GearStamp.stampStack(s, pr.getUuid(), null);
    if (ns != s) e.setItemStack(ns);""")
# the roll task: stacks of that id that were not in the snapshot, carry no document and look exactly like a fresh output (metadata
# equal to the recipe output's, full durability; review E1), at most units x output quantity of them
gcrt.addInterface(pool.get("java.lang.Runnable"))
for _f in ("public @PR@ pr;", "public String id;", "public java.util.IdentityHashMap snap;", "public int cap;", "public @BD@ outMeta;",
           "public String recipe;"):
    F(gcrt, _f)
C(gcrt, r"""
public GearCraftTask(@PR@ pr, String id, java.util.IdentityHashMap snap, int cap, @BD@ outMeta, String recipe) {
  this.pr = pr; this.id = id; this.snap = snap; this.cap = cap; this.outMeta = outMeta; this.recipe = recipe;
}""")
# a stack that looks exactly like a fresh bench output: metadata equal to the recipe output's (normally none) and full durability
M(gcrt, r"""
public static boolean fresh(@IS@ s, @BD@ outMeta) {
  @BD@ md = s.getMetadata();
  boolean e1 = md == null || md.isEmpty();
  boolean e2 = outMeta == null || outMeta.isEmpty();
  if (e1 != e2) return false;
  if (!e1 && !md.equals(outMeta)) return false;
  return s.getDurability() >= s.getMaxDurability();
}""")
# the candidate rule over the containers in SCAN order (static so the bare-JVM harness runs it on plain containers): not in the
# pre-craft identity snapshot, no document, fresh; at most cap rolls. got collects the rolled rarity ids. Returns the roll count.
M(gcrt, r"""
public static int rollIn(@IC@[] cs, java.util.UUID u, String id, java.util.IdentityHashMap snap, int cap, @BD@ outMeta, StringBuilder got) {
  int n = 0;
  for (int k = 0; k < cs.length && n < cap; k++) {
    @IC@ c = cs[k];
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity() && n < cap; i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s == null || s.isEmpty() || !id.equals(s.getItemId())) continue;
      if (snap.containsKey(s) || @PKG@.GearData.hasAnyDoc(s.getMetadata()) || !fresh(s, outMeta)) continue;
      @BD@ d = @PKG@.GearRoll.craftDoc(id, u);
      @IS@ ns = @PKG@.GearData.put(s, d, u);
      if (ns == s) continue;
      c.setItemStackForSlot((short) i, ns);
      n++;
      if (got != null) got.append(' ').append(@PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)]);
    }
  }
  return n;
}""")
M(gcrt, r"""
public void run() {
  java.util.UUID u = null;
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    u = this.pr.getUuid();
    @INV@ inv = @PKG@.GearStamp.invOf(this.pr);
    if (inv == null || @PKG@.Gear.busy(u)) { @PKG@.GearStamp.pendingClear(u, this.id); return; }
    @IC@[] cs = new @IC@[@PKG@.GearStamp.SCAN.length];
    for (int k = 0; k < cs.length; k++) cs[k] = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    StringBuilder got = new StringBuilder();
    int n = rollIn(cs, u, this.id, this.snap, this.cap, this.outMeta, got);
    @PKG@.GearStamp.pendingClear(u, this.id);
    if (n > 0) @PKG@.GearLog.line("CRAFT " + this.pr.getUsername() + " " + u + " " + this.id + " x" + n + ":" + got.toString() + " recipe " + this.recipe + " smith " + @PKG@.Gear.fnum(@PKG@.GearRoll.smithChance(u)) + "%");
    if (n < this.cap) @PKG@.GearLog.line("CRAFT-MISS " + this.pr.getUsername() + " " + this.id + " rolled " + n + " of " + this.cap + " (output on the ground or changed) - the rest is stamped Normal");
  } catch (Throwable t) {
    if (u != null) @PKG@.GearStamp.pendingClear(u, this.id);
    @PKG@.Gear.warnOnce("crafttask", "crafted gear roll failed: " + t);
  }
}""")
# spec 5.1 GearCraftSys: CraftRecipeEvent$Post (before giveOutput) -> snapshot the identities of every stack of the output id, hold that id
# back from the stamp, and roll the new stacks in a world task that runs after giveOutput returned (same queue, FIFO)
event_system(gcrs, "GearCraftSys", CREP, "@ARC@.empty()", r"""
    @CRE@ e = (@CRE@) ev;
    if (e.isCancelled() || !@PKG@.GearCfg.PART_CRAFT) return;
    @CRR@ rc = e.getCraftedRecipe();
    if (rc == null) return;
    @MQ@ po = rc.getPrimaryOutput();
    if (po == null) return;
    String id = po.getItemId();
    if (id == null || !@PKG@.GearData.isGear(id)) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (pr == null || p == null || p.getInventory() == null) return;
    if (p.getGameMode() == @GM@.Creative) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    int units = rc.getTimeSeconds() > 0.0f ? 1 : Math.max(1, e.getQuantity());
    int cap = units * Math.max(1, po.getQuantity());
    if (cap > 64) cap = 64;
    java.util.IdentityHashMap snap = new java.util.IdentityHashMap();
    @INV@ inv = p.getInventory();
    for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
      @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
      if (c == null) continue;
      for (int i = 0; i < c.getCapacity(); i++) {
        @IS@ s = c.getItemStack((short) i);
        if (s != null && !s.isEmpty() && id.equals(s.getItemId())) snap.put(s, Boolean.TRUE);
      }
    }
    @PKG@.GearStamp.pendingAdd(pr.getUuid(), id);
    w.execute(new @PKG@.GearCraftTask(pr, id, snap, cap, po.getMetadata(), rc.getId()));""")
# GearTick: 1 s per player (world thread). Re-reads the gate levels (spec 3.3 / 3.6 / 6.3) and marks the player dirty when a level,
# the class skill, the profile or the config changed, so the scan re-renders exactly the items whose visible lines changed.
F(gtk, "public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();")
F(gtk, "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();")
F(gtk, "public static boolean FAILED_ONCE = false;")
C(gtk, "public GearTick() { super(); }")
M(gtk, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(gtk, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    float[] c = (float[]) CLOCK.get(u);
    if (c == null) { c = new float[] { 0.0f }; CLOCK.put(u, c); }
    c[0] = c[0] + dt;
    if (c[0] < 1.0f) return;
    c[0] = 0.0f;
    Object ext = store.getExternalData();
    @WLD@ w = ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null;
    @INV@ inv = p.getInventory();
    boolean dirty = @PKG@.GearGate.refresh(u);
    long ce = @PKG@.GearCfg.cfgEpoch();
    Object se = SEEN.get(u);
    if (!(se instanceof Long) || ((Long) se).longValue() != ce) { SEEN.put(u, Long.valueOf(ce)); dirty = true; }
    if (dirty) @PKG@.GearStamp.dirty(pr, w);
    // spec 7.1: gear:stats:<uuid> = the active totals (held weapon + worn armor that is identified and meets its gate), read by
    // gear:fn:stats; republished only when it changed. PART B applies these totals in combat; this only publishes them.
    String ss = @PKG@.GearStats.statsString(@PKG@.GearStats.totals(u, inv));
    if (!ss.equals(@PKG@.Gear.bget("gear:stats:" + u))) @PKG@.Gear.bridge().put("gear:stats:" + u, ss);
    // ---- PART B PLUGS IN HERE (4/4): stat effects (PARTB_TICK) ----
@PARTBTICK@
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.Gear.warn("gear tick failed (logged once): " + t); }
  }
}""".replace("@PARTBTICK@", PARTB_TICK))

# ================================================================= GearRefreshTask (PlayerReadyEvent, every world switch; idempotent)
grft.addInterface(pool.get("java.lang.Runnable"))
F(grft, "public @PR@ pr;")
F(grft, "public boolean onWorld;")
F(grft, "public int tries;")
F(grft, "public java.util.UUID hopWorld;")
C(grft, "public GearRefreshTask(@PR@ pr) { this.pr = pr; this.onWorld = false; this.tries = 0; this.hopWorld = null; }")
M(grft, r"""
public void later(long ms) {
  this.onWorld = false;
  @HSV@.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}""")
M(grft, r"""
public void again(String why) {
  this.tries = this.tries + 1;
  if (this.tries < 15) { later(2000L); return; }
  String who = "?";
  try { who = this.pr.getUsername(); } catch (Throwable t) { who = "?"; }
  @PKG@.Gear.warn("gear refresh gave up for " + who + " after " + this.tries + " tries (" + why + "); the next inventory change or relog tries again");
}""")
# spec 8.4: SkyyRolls still enabled next to SkyyGear -> one WARN and a line for admins at join
M(grft, r"""
public static void rollsWarn(@PR@ pr) {
  try {
    if (@PKG@.Gear.bget("config:def:SkyyRolls") == null) return;
    @PKG@.Gear.warnOnce("rolls", "SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED); both mods register /reforge");
    java.util.UUID u = pr.getUuid();
    if (@PKG@.Gear.admin(u) && @PKG@.Gear.once("rollswarn:" + u)) pr.sendMessage(@MSG@.raw("[Gear] SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED). SkyyGear replaces it.").color(@PKG@.GearDefs.C_GOLD));
  } catch (Throwable t) { }
}""")
M(grft, r"""
public void run() {
  try {
    if (this.pr == null || !this.pr.isValid()) return;
    if (!this.onWorld) {
      java.util.UUID wu = this.pr.getWorldUuid();
      if (wu == null) { again("player is in no world"); return; }
      @WLD@ w = @UNI@.get().getWorld(wu);
      if (w == null) { again("world " + wu + " is not loaded"); return; }
      this.onWorld = true;
      this.hopWorld = wu;
      w.execute(this);
      return;
    }
    java.util.UUID now = this.pr.getWorldUuid();
    if (now == null || !now.equals(this.hopWorld)) { again("player changed world"); return; }
    if (@PKG@.Gear.busy(this.pr.getUuid())) { again("SkyyProfiles profile:busy is still set"); return; }
    @INV@ inv = @PKG@.GearStamp.invOf(this.pr);
    if (inv == null) { again("player inventory not ready"); return; }
    @PKG@.GearGate.refresh(this.pr.getUuid());
    int[] cnt = @PKG@.GearStamp.scan(this.pr, inv);
    if (cnt[0] + cnt[1] + cnt[2] > 0) @PKG@.Gear.info("join refresh " + this.pr.getUsername() + ": stamped " + cnt[0] + ", migrated " + cnt[1] + ", re-rendered " + cnt[2]);
    rollsWarn(this.pr);
  } catch (Throwable t) { @PKG@.Gear.warn("gear refresh failed: " + t); }
}""")
grdy.addInterface(pool.get("java.util.function.Consumer"))
C(grdy, "public GearReady() { }")
M(grdy, r"""
public void accept(Object ev) {
  try {
    @PRE@ e = (@PRE@) ev;
    @REF@ r = e.getPlayerRef();
    if (r == null) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    new @PKG@.GearRefreshTask(pr).later(2000L);
  } catch (Throwable t) { @PKG@.Gear.warn("ready handler failed: " + t); }
}""")
PDE = "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent"
B.probe(pool, PDE, "getPlayerRef")
gbye = mk("GearBye")
gbye.addInterface(pool.get("java.util.function.Consumer"))
C(gbye, "public GearBye() { }")
M(gbye, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((%s) ev).getPlayerRef();
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    @PKG@.GearGate.forget(u);
    @PKG@.GearStamp.forget(u);
    @PKG@.GearTick.CLOCK.remove(u);
    @PKG@.GearTick.SEEN.remove(u);
    @PKG@.Gear.bridge().remove("gear:stats:" + u);
  } catch (Throwable t) { }
}""" % PDE)

# ================================================================= GearUi: vanilla styles (spec 5.8) - FOR THE SHARED HELPER (RESUME step 5)
# ui.frames ON (default) = the vanilla textures / sounds / scrolling list; OFF = flat vanilla colours, a paged list, no textures
# (only markup the live Skyy pages already use) - the in-game safety valve if an inline texture path does not resolve.
V_SND_LIGHT = ('Sounds: (Activate: (SoundPath: \\"Sounds/ButtonsLightActivate.ogg\\", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), '
               'MouseHover: (SoundPath: \\"Sounds/ButtonsLightHover.ogg\\", Volume: 6))')
V_SND_CANCEL = ('Sounds: (Activate: (SoundPath: \\"Sounds/ButtonsCancelActivate.ogg\\", MinPitch: -0.4, MaxPitch: 0.4, Volume: 6), '
                'MouseHover: (SoundPath: \\"Sounds/ButtonsLightHover.ogg\\", Volume: 6))')
M(gui, "public static boolean tex() { return @PKG@.GearCfg.UI_FRAMES; }")
M(gui, r"""
public static String lbl(String color) {
  return "LabelStyle: (FontSize: 17, TextColor: " + color + ", RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12)";
}""")
# kind 0 = @DefaultTextButtonStyle, 1 = @SecondaryTextButtonStyle, 2 = @CancelTextButtonStyle, 3 = the Disabled look
M(gui, r"""
public static String btn(int kind) {
  String col = kind == 1 ? "#bdcbd3" : (kind == 3 ? "#797b7c" : "#bfcdd5");
  String ls = lbl(col);
  if (!tex()) {
    String d = kind == 2 ? "#5a2a26" : (kind == 3 ? "#2a2f36" : (kind == 1 ? "#2b3542" : "#2c4a66"));
    String h = kind == 2 ? "#6e332e" : (kind == 3 ? "#2a2f36" : (kind == 1 ? "#34404f" : "#355a7c"));
    String p = kind == 2 ? "#44201d" : (kind == 3 ? "#2a2f36" : (kind == 1 ? "#222a35" : "#223a50"));
    return "Style: TextButtonStyle(Default: (Background: " + d + ", " + ls + "), Hovered: (Background: " + h + ", " + ls + "), Pressed: (Background: " + p + ", " + ls + "));";
  }
  String b1;
  String b2;
  String b3;
  if (kind == 0) {
    b1 = "PatchStyle(TexturePath: \"Common/Buttons/Primary.png\", VerticalBorder: 12, HorizontalBorder: 80)";
    b2 = "PatchStyle(TexturePath: \"Common/Buttons/Primary_Hovered.png\", VerticalBorder: 12, HorizontalBorder: 80)";
    b3 = "PatchStyle(TexturePath: \"Common/Buttons/Primary_Pressed.png\", VerticalBorder: 12, HorizontalBorder: 80)";
  } else if (kind == 3) {
    b1 = "PatchStyle(TexturePath: \"Common/Buttons/Disabled.png\", VerticalBorder: 12, HorizontalBorder: 80)";
    b2 = b1;
    b3 = b1;
  } else {
    String t = kind == 2 ? "Destructive" : "Secondary";
    b1 = "PatchStyle(TexturePath: \"Common/Buttons/" + t + ".png\", Border: 12)";
    b2 = "PatchStyle(TexturePath: \"Common/Buttons/" + t + "_Hovered.png\", Border: 12)";
    b3 = "PatchStyle(TexturePath: \"Common/Buttons/" + t + "_Pressed.png\", Border: 12)";
  }
  String snd = kind == 2 ? "@SNDCANCEL@" : "@SNDLIGHT@";
  return "Style: TextButtonStyle(Default: (Background: " + b1 + ", " + ls + "), Hovered: (Background: " + b2 + ", " + ls + "), Pressed: (Background: " + b3 + ", " + ls + "), " + snd + ");";
}""".replace("@SNDCANCEL@", V_SND_CANCEL).replace("@SNDLIGHT@", V_SND_LIGHT))
# the ItemRepairElement.ui row: hover #000000(0.2); the selected row keeps a darker Default background
M(gui, r"""
public static String rowStyle(boolean on) {
  if (on) return "Style: ButtonStyle(Default: (Background: #000000(0.35)), Hovered: (Background: #000000(0.35)), Pressed: (Background: #000000(0.4)));";
  return "Style: ButtonStyle(Default: (Background: #000000(0.05)), Hovered: (Background: #000000(0.2)), Pressed: (Background: #000000(0.3)));";
}""")
M(gui, r"""
public static String scroll() {
  return "ScrollbarStyle: (Spacing: 6, Size: 6, Background: (TexturePath: \"Common/Scrollbar.png\", Border: 3), Handle: (TexturePath: \"Common/ScrollbarHandle.png\", Border: 3), HoveredHandle: (TexturePath: \"Common/ScrollbarHandleHovered.png\", Border: 3), DraggedHandle: (TexturePath: \"Common/ScrollbarHandleDragged.png\", Border: 3));";
}""")
M(gui, r"""
public static String vsep() {
  if (tex()) return "Group { Anchor: (Width: 6); Background: (TexturePath: \"Common/ContainerVerticalSeparator.png\"); }";
  return "Group { Anchor: (Width: 2); Background: #2b3542; }";
}""")
# the @DecoratedContainer frame: ContainerHeader title bar with the @Title label, ContainerPatch body (#SkyyGBody, LayoutMode Top,
# padding 17), top + bottom decorations. The root Group only has Width / Height (HANDOFF section 2).
M(gui, r"""
public static void frame(@UCB@ b, String title, int w, int h) {
  boolean t = tex();
  b.appendInline((String) null, "Group #SkyyGRoot { Anchor: (Width: " + w + ", Height: " + h + "); }");
  String head = t ? "(TexturePath: \"Common/ContainerHeader.png\", HorizontalBorder: 50, VerticalBorder: 0)" : "#1b2533(0.98)";
  b.appendInline("#SkyyGRoot", "Group #SkyyGTitle { Anchor: (Height: 38, Top: 0); Padding: (Top: 7); Background: " + head + "; Label #SkyyGTitleTxt { Padding: (Horizontal: 19); Text: \"\"; Style: (FontSize: 15, VerticalAlignment: Center, HorizontalAlignment: Center, RenderUppercase: true, TextColor: #b4c8c9, FontName: \"Secondary\", RenderBold: true); } }");
  if (t) b.appendInline("#SkyyGTitle", "Group #SkyyGDecoTop { Anchor: (Width: 236, Height: 11, Top: -12); Background: \"Common/ContainerDecorationTop.png\"; }");
  String body = t ? "(TexturePath: \"Common/ContainerPatch.png\", Border: 23)" : "#0e1620(0.97)";
  b.appendInline("#SkyyGRoot", "Group #SkyyGBody { Anchor: (Top: 38); LayoutMode: Top; Padding: (Full: 17); Background: " + body + "; }");
  if (t) b.appendInline("#SkyyGRoot", "Group #SkyyGDecoBot { Anchor: (Width: 236, Height: 11, Bottom: -6); Background: \"Common/ContainerDecorationBottom.png\"; }");
  b.set("#SkyyGTitleTxt.Text", title);
}""")
# info line: "+" done (white), "-" refused / failed (vanilla gold highlight), "=" neutral (vanilla label colour)
M(gui, r"""
public static String infoColor(String res) {
  if (res == null || res.length() == 0) return @PKG@.GearDefs.C_LABEL;
  char c = res.charAt(0);
  if (c == '+') return "#ffffff";
  if (c == '-') return @PKG@.GearDefs.C_GOLD;
  return @PKG@.GearDefs.C_LABEL;
}""")
M(gui, r"""
public static String infoText(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")

# ================================================================= ReforgePage (spec 5.4 + 5.8): the vanilla item-repair page look
for _f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
           "public String selFp;", "public String info;", "public boolean fresh;", "public String epoch;", "public long lastForge;",
           "public @BD@ before;", "public @BD@ after;"):
    F(rpg, _f)
C(rpg, r"""
public ReforgePage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.pageNo = 0;
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null;
  this.info = ""; this.fresh = false; this.lastForge = 0L; this.before = null; this.after = null;
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
}""")
M(rpg, r"""
public void clearSel() {
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null; this.fresh = false; this.before = null; this.after = null;
}""")
# re-picking the item already on the anvil keeps the Before / After columns (same slot, fingerprint and profile epoch)
M(rpg, r"""
public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (it == null || it.isEmpty() || !@PKG@.GearData.isGear(it.getItemId())) return false;
  String ep = @PKG@.Gear.epoch(this.playerRef.getUuid());
  String f = @PKG@.GearForge.fp(it);
  if (s == this.selSec && slot == this.selSlot && f.equals(this.selFp) && ep.equals(this.epoch)) return true;
  this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = f;
  this.fresh = false; this.before = null; this.after = null;
  this.epoch = ep;
  this.info = "=" + @PKG@.Gear.itemName(it.getItemId()) + " is on the anvil.";
  return true;
}""")
M(rpg, r"""
public void preselect(@INV@ inv) {
  try {
    if (inv == null) return;
    if (inv.usingToolsItem()) pick(inv, 5, (int) inv.getActiveToolsSlot());
    else pick(inv, 0, (int) inv.getActiveHotbarSlot());
  } catch (Throwable t) { }
}""")
M(rpg, r"""
public static String rarHex(int r) { return @PKG@.GearDefs.R_PAGEHEX[@PKG@.GearCfg.ri(r)]; }""")
# one column of lines (the current roll, or Before / After) into a parent group
M(rpg, r"""
public static void column(@UCB@ b, String parent, String cid, String head, String headCol, String id, @BD@ d, int w) {
  b.appendInline(parent, "Group " + cid + " { Anchor: (Width: " + w + "); LayoutMode: Top; }");
  b.appendInline(cid, "Label " + cid + "H { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + headCol + ", VerticalAlignment: Center); }");
  b.set(cid + "H.Text", head);
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  if (d != null && @PKG@.GearData.identified(d)) @PKG@.GearView.statLines(id, d, txt, col);
  else if (d != null) { txt.add("Unidentified - identify it first (/identify)."); col.add(@PKG@.GearDefs.C_GRAY); }
  if (txt.isEmpty()) { txt.add("No modifiers yet - a reforge rolls them."); col.add(@PKG@.GearDefs.C_GRAY); }
  for (int i = 0; i < txt.size() && i < 12; i++) {
    String c = (String) col.get(i);
    b.appendInline(cid, "Label " + cid + "L" + i + " { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: " + (c == null ? "#ffffff" : c) + ", VerticalAlignment: Center); }");
    b.set(cid + "L" + i + ".Text", (String) txt.get(i));
  }
}""")
M(rpg, r"""
public void anvil(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel) {
  b.appendInline("#SkyyGMain", "Group #SkyyGAnvil { Anchor: (Width: 562); LayoutMode: Top; }");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGAnvilT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGAnvilT.Text", "Anvil");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGSel { Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 12); }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelIcon { Anchor: (Width: 72, Height: 72); Background: #000000(0.25); }");
  if (sel != null) b.appendInline("#SkyyGSelIcon", "ItemIcon { Anchor: (Width: 64, Height: 64, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(sel.getItemId()) + "\"; }");
  b.appendInline("#SkyyGSel", "Label { Anchor: (Width: 14, Height: 72); Text: \"\"; }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelTxt { Anchor: (Width: 470, Height: 76); LayoutMode: Top; }");
  if (sel == null) {
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGSelName.Text", "The anvil is empty");
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
    b.set("#SkyyGSelSub.Text", "Pick an item from Your gear - it stays in its own slot.");
    b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGCostH { Anchor: (Height: 32); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGCostH.Text", "Reforge cost by rarity");
    for (int r = 0; r < @PKG@.GearDefs.NR; r++) {
      b.appendInline("#SkyyGAnvil", "Label #SkyyGCost" + r + " { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
      long per = @PKG@.GearCfg.CR_PER[r];
      b.set("#SkyyGCost" + r + ".Text", @PKG@.GearDefs.R_NAME[r] + ": " + @PKG@.Gear.fmt(@PKG@.GearCfg.CR_BASE[r]) + " coins" + (per > 0L ? " + " + @PKG@.Gear.fmt(per) + " per item level" : ""));
    }
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow1 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow1.Text", "A reforge re-rolls every modifier for the item's rarity and level.");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow2 { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow2.Text", "Tip: hold the item when you type /reforge to put it on the anvil.");
    return;
  }
  String id = sel.getItemId();
  @BD@ d = @PKG@.GearData.effective(id, sel.getMetadata());
  int r = @PKG@.GearData.rarity(d);
  int lvl = @PKG@.GearLevel.level(id, d);
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelName.Text", d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
  Object[] g = null;
  if (d != null) g = @PKG@.GearView.gateLine(u, id, d, lvl);
  b.set("#SkyyGSelSub.Text", @PKG@.GearDefs.R_NAME[r].toUpperCase() + " " + @PKG@.GearView.slotWord(id) + "   -   " + (g == null || ((String) g[0]).length() == 0 ? "Level " + lvl : (String) g[0]));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelWhere { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  b.set("#SkyyGSelWhere.Text", "In your " + @PKG@.GearForge.where(this.selSec, this.selSlot) + " - it stays there while you reforge it.");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGCols { Anchor: (Height: 330); LayoutMode: Left; Padding: (Top: 6); }");
  if (this.fresh && this.before != null && this.after != null) {
    column(b, "#SkyyGCols", "#SkyyGColB", "Before", "#878e9c", id, this.before, 275);
    b.appendInline("#SkyyGCols", "Label { Anchor: (Width: 12); Text: \"\"; }");
    column(b, "#SkyyGCols", "#SkyyGColA", "After", "#ffffff", id, this.after, 275);
  } else {
    column(b, "#SkyyGCols", "#SkyyGColC", "Current modifiers", "#ffffff", id, d, 562);
  }
  long cost = @PKG@.GearCfg.costReforge(r, lvl);
  long have = @PKG@.GearForge.purse(u);
  String why = @PKG@.GearForge.refuse(sel, d);
  b.appendInline("#SkyyGAnvil", "Label #SkyyGCostTxt { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: #E8A93B, VerticalAlignment: Center); }");
  b.set("#SkyyGCostTxt.Text", cost > 0L ? "Cost: " + @PKG@.Gear.fmt(cost) + " coins (" + @PKG@.GearDefs.R_NAME[r] + ", level " + lvl + ")" : "Cost: free");
  b.appendInline("#SkyyGAnvil", "Label #SkyyGPurse { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGPurse.Text", have >= 0L ? "Your purse: " + @PKG@.Gear.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  boolean off = why != null || poor;
  // the button says only what happens (the gold cost line right above carries the number: inline button Text goes through safe(),
  // which would turn "1,000" into "1 000")
  String bt = why != null ? (d != null && !@PKG@.GearData.identified(d) ? "Identify it first" : "Cannot reforge") : (poor ? "Not enough coins" : "Reforge");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "Label { Anchor: (Width: 111, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnForge { Anchor: (Width: 340, Height: 44); Text: \"" + @PKG@.Gear.safe(bt) + "\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnForge", @EVD@.of("a", "forge"));
}""")
M(rpg, r"""
public void list(@UCB@ b, @UEB@ ev, @INV@ inv) {
  boolean t = @PKG@.GearUi.tex();
  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead { Anchor: (Height: 30); LayoutMode: Left; Padding: (Right: 15, Bottom: 5); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadItem { Anchor: (Width: 300); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadRar { Anchor: (Width: 150); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyGHeadItem.Text", "Your gear (" + this.rows.size() + ")");
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  int per = t ? 200 : 12;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (t) b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 634); LayoutMode: TopScrolling; " + @PKG@.GearUi.scroll() + " }");
  else b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 590); LayoutMode: Top; }");
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty1 { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty1.Text", "No weapons or armor on you.");
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty2 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty2.Text", "Carry one (hotbar, inventory, backpack or worn) and click Refresh.");
  }
  java.util.UUID u = this.playerRef.getUuid();
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    @BD@ d = @PKG@.GearData.effective(id, it.getMetadata());
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    int lvl = @PKG@.GearLevel.level(id, d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", (d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d)) + (on ? "  (on the anvil)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", (d == null ? "?" : @PKG@.GearDefs.R_NAME[r]) + " - Lv " + lvl);
    b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "sel:" + i));
  }
  if (!t && pages > 1) {
    b.appendInline("#SkyyGListBox", "Group #SkyyGNav { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGNav", "Label #SkyyGPageTxt { Anchor: (Width: 170, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "next"));
  }
}""")
M(rpg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  @IS@ sel = null;
  if (this.selSec >= 0) {
    sel = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
    if (!@PKG@.GearForge.same(sel, this.selId, this.selFp)) {
      sel = null;
      clearSel();
      if (this.info == null || this.info.length() == 0 || this.info.charAt(0) != '-') this.info = "-The item on the anvil moved or changed - pick it again.";
    }
  }
  this.rows = @PKG@.GearForge.rows(inv);
  @PKG@.GearUi.frame(b, "Reforge", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Pick a weapon or armor piece. A reforge re-rolls its modifiers for coins - the rarity never changes.");
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 680); LayoutMode: Left; Padding: (Top: 6); }");
  list(b, ev, inv);
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  b.appendInline("#SkyyGMain", @PKG@.GearUi.vsep());
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  anvil(b, ev, u, sel);
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
# the reforge click: guard -> profile:busy -> selection -> epoch -> GearForge.reforge (same item, refusals, coins first, refund)
M(rpg, r"""
public void forge(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastForge < 400L) return;
  this.lastForge = now;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was reforged. Try again in a moment."; return; }
  if (this.selSec < 0) { this.info = "-Pick an item from Your gear first."; return; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.epoch = ep; this.info = "-Your profile changed - pick the item again."; return; }
  @IC@ c = @PKG@.GearStamp.section(inv, this.selSec);
  String name = @PKG@.Gear.itemName(this.selId);
  Object[] res = @PKG@.GearForge.reforge(c, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername(), false);
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    this.selFp = @PKG@.GearForge.fp((@IS@) res[2]);
    this.before = (@BD@) res[3];
    this.after = (@BD@) res[4];
    this.fresh = true;
    long cost = ((Long) res[5]).longValue();
    this.info = "+Reforged! Your " + name + " rolled new modifiers" + (cost > 0L ? " (-" + @PKG@.Gear.fmt(cost) + " coins)." : ".");
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("That item moved")) clearSel();
  this.info = "-" + msg;
}""")
M(rpg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("refresh")) { this.info = ""; rebuild(); return; }
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t1) { }
      }
      close();
      return;
    }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv == null) return;
    if (a.startsWith("sel:")) {
      int i = -1;
      try { i = Integer.parseInt(a.substring(4)); } catch (Throwable t) { i = -1; }
      if (i < 0 || this.rows == null || i >= this.rows.size()) return;
      int[] r = (int[]) this.rows.get(i);
      if (!pick(inv, r[0], r[1])) this.info = "-That item is not there any more.";
      rebuild();
      return;
    }
    if (a.equals("forge")) { forge(inv); rebuild(); return; }
  } catch (Throwable t) { @PKG@.Gear.warn("reforge page click failed: " + t); }
}""")

# ================================================================= /reforge (player command, same name as SkyyRolls - spec 8.1)
C(rfc, r"""
public ReforgeCmd() {
  super("reforge", "Open the Reforge page: re-roll the modifiers of a weapon or armor piece for coins");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(rfc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Reforge] no player found")); return; }
    @PKG@.GearStamp.scan(pr, p.getInventory());
    @PKG@.ReforgePage page = new @PKG@.ReforgePage(pr);
    page.preselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/reforge failed: " + t);
    pr.sendMessage(@MSG@.raw("[Reforge] could not open the Reforge page - the server log has the details"));
  }
}""")

# ================================================================= GearAdmin: /gear bodies (world thread; admin writes are logged)
M(gad, r"""
public static void msg(@PR@ pr, String t) {
  try { pr.sendMessage(@MSG@.raw("[Gear] " + t)); } catch (Throwable x) { }
}""")
M(gad, r"""
public static @IC@ handC(@INV@ inv) {
  if (inv.usingToolsItem()) return inv.getTools();
  return inv.getHotbar();
}""")
M(gad, r"""
public static short handS(@INV@ inv) {
  if (inv.usingToolsItem()) return (short) inv.getActiveToolsSlot();
  return (short) inv.getActiveHotbarSlot();
}""")
M(gad, r"""
public static @IS@ hand(@INV@ inv) {
  @IC@ c = handC(inv);
  short s = handS(inv);
  if (c == null || s < 0 || s >= c.getCapacity()) return null;
  return c.getItemStack(s);
}""")
M(gad, r"""
public static String ok(Object tx) {
  if (tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) return "  (the inventory REFUSED the change)";
  return "";
}""")
# the words after the sub-command word ("gear give iron sword --rarity rare" -> "iron sword --rarity rare")
M(gad, r"""
public static String rest(@CTX@ ctx, String word) {
  String line = "";
  try { line = ctx.getInputString(); } catch (Throwable t) { line = ""; }
  if (line == null) return "";
  String[] tk = line.trim().split("\\s+");
  StringBuilder sb = new StringBuilder();
  boolean seen = false;
  for (int i = 0; i < tk.length; i++) {
    if (!seen) { if (tk[i].equalsIgnoreCase(word) || tk[i].equalsIgnoreCase("/" + word)) seen = true; continue; }
    if (sb.length() > 0) sb.append(' ');
    sb.append(tk[i]);
  }
  return sb.toString().trim();
}""")
# item name -> gear item id (or null + suggestions; SkyyRolls 0.1.2 resolve)
M(gad, r"""
public static String resolve(String q, StringBuilder sugg) {
  if (q == null) return null;
  String t = q.trim();
  if (t.length() == 0) return null;
  if (@PKG@.Gear.item(t) != null) return t;
  String norm = t.toLowerCase().replace(' ', '_');
  String[] words = t.toLowerCase().replace('_', ' ').trim().split(" ");
  java.util.ArrayList hits = new java.util.ArrayList();
  java.util.ArrayList good = new java.util.ArrayList();
  try {
    java.util.Iterator it = @ITM@.getAssetMap().getAssetMap().keySet().iterator();
    while (it.hasNext()) {
      String id = String.valueOf(it.next());
      if (id.length() == 0 || id.charAt(0) == '*') continue;
      String low = id.toLowerCase();
      if (low.equals(norm)) return id;
      boolean all = true;
      for (int i = 0; i < words.length; i++) { if (words[i].length() > 0 && low.indexOf(words[i]) < 0) { all = false; break; } }
      if (all) { hits.add(id); if (@PKG@.GearData.isGear(id)) good.add(id); }
    }
  } catch (Throwable e) { @PKG@.Gear.warn("item lookup failed: " + e); return null; }
  if (good.size() == 1) return (String) good.get(0);
  if (hits.size() == 1) return (String) hits.get(0);
  java.util.ArrayList show = good.size() > 0 ? good : hits;
  java.util.Collections.sort(show);
  for (int i = 0; i < show.size() && i < 8; i++) { if (sugg.length() > 0) sugg.append(", "); sugg.append((String) show.get(i)); }
  if (show.size() > 8) sugg.append(" ... (" + show.size() + " matches)");
  return null;
}""")
# storage first (engine rule), then hotbar, then backpack; true = it went in
M(gad, r"""
public static boolean give(@INV@ inv, @IS@ s) {
  @IC@[] cs = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int i = 0; i < cs.length; i++) {
    if (cs[i] == null) continue;
    try {
      Object tx = cs[i].addItemStack(s);
      if (!(tx instanceof @TXN@) || ((@TXN@) tx).succeeded()) return true;
    } catch (Throwable t) { }
  }
  return false;
}""")
M(gad, r"""
public static void giveCmd(@PR@ pr, @INV@ inv, String rest) {
  String[] tk = rest.length() == 0 ? new String[0] : rest.split("\\s+");
  StringBuilder q = new StringBuilder();
  String rar = null;
  boolean unid = false;
  for (int i = 0; i < tk.length; i++) {
    String w = tk[i];
    if (w.equalsIgnoreCase("--rarity") && i + 1 < tk.length) { rar = tk[i + 1]; i++; continue; }
    if (w.equalsIgnoreCase("--unid")) {
      if (i + 1 < tk.length && !tk[i + 1].startsWith("--")) { String v = tk[i + 1].toLowerCase(); unid = v.equals("true") || v.equals("yes") || v.equals("1") || v.equals("on"); i++; }
      else unid = true;
      continue;
    }
    if (q.length() > 0) q.append(' ');
    q.append(w);
  }
  if (q.length() == 0) { msg(pr, "usage: /gear give <item> [--rarity <id>] [--unid true]"); return; }
  StringBuilder sugg = new StringBuilder();
  String id = resolve(q.toString(), sugg);
  if (id == null) { msg(pr, "no item matches '" + q + "'" + (sugg.length() > 0 ? ". Did you mean: " + sugg : "")); return; }
  if (!@PKG@.GearData.isGear(id)) { msg(pr, id + " is not gear - only Weapon_* (not ammo, shields, bombs ...) and Armor_* items"); return; }
  int r;
  if (rar != null) {
    r = @PKG@.GearDefs.rIndex(rar);
    if (r < 0) { msg(pr, "unknown rarity '" + rar + "' - normal, unique, rare, legendary, fabled, mythic, set"); return; }
  } else r = @PKG@.GearRoll.pickRarity(0);
  java.util.UUID u = pr.getUuid();
  @BD@ d = @PKG@.GearRoll.newDoc(id, r, !unid, "admin");
  @IS@ s = @PKG@.GearData.put(new @IS@(id, 1), d, u);
  boolean in = give(inv, s);
  @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " give " + id + " " + @PKG@.GearDefs.R_ID[r] + (unid ? " unidentified" : " [" + @PKG@.GearView.modSummary(d) + "]") + (in ? "" : " (inventory full)"));
  msg(pr, (in ? "gave " : "NOT given (inventory full): ") + @PKG@.GearView.nameText(id, d) + " - " + @PKG@.GearDefs.R_NAME[r] + (unid ? ", unidentified" : (@PKG@.GearView.modSummary(d).length() > 0 ? " - " + @PKG@.GearView.modSummary(d) : "")));
}""")
# /gear migrate [player] on another player: hop to that player's world thread, scan there, report back
gmt = mk("GearMigrateTask")
gmt.addInterface(pool.get("java.lang.Runnable"))
F(gmt, "public @PR@ admin;")
F(gmt, "public @PR@ target;")
F(gmt, "public boolean onWorld;")
C(gmt, "public GearMigrateTask(@PR@ admin, @PR@ target) { this.admin = admin; this.target = target; this.onWorld = false; }")
M(gmt, r"""
public void run() {
  try {
    if (this.target == null || !this.target.isValid()) { @PKG@.GearAdmin.msg(this.admin, "that player left"); return; }
    if (!this.onWorld) {
      java.util.UUID wu = this.target.getWorldUuid();
      @WLD@ w = wu == null ? null : @UNI@.get().getWorld(wu);
      if (w == null) { @PKG@.GearAdmin.msg(this.admin, "that player's world is not loaded"); return; }
      this.onWorld = true;
      w.execute(this);
      return;
    }
    if (@PKG@.Gear.busy(this.target.getUuid())) { @PKG@.GearAdmin.msg(this.admin, this.target.getUsername() + "'s profile is loading (profile:busy) - try again in a moment"); return; }
    int[] c = @PKG@.GearStamp.scan(this.target, @PKG@.GearStamp.invOf(this.target));
    @PKG@.GearAdmin.msg(this.admin, "scan of " + this.target.getUsername() + ": stamped Normal " + c[0] + ", migrated from SkyyRolls " + c[1] + ", re-rendered " + c[2]);
    @PKG@.GearLog.line("ADMIN " + this.admin.getUsername() + " migrate " + this.target.getUsername() + " " + c[0] + "/" + c[1] + "/" + c[2]);
  } catch (Throwable t) { @PKG@.GearAdmin.msg(this.admin, "scan failed: " + t); }
}""")
M(gad, r"""
public static void migrateCmd(@PR@ pr, @INV@ inv, String rest) {
  if (rest.length() == 0) {
    if (@PKG@.Gear.busy(pr.getUuid())) { msg(pr, "your profile is loading (profile:busy) - try again in a moment"); return; }
    int[] c = @PKG@.GearStamp.scan(pr, inv);
    msg(pr, "scan: stamped Normal " + c[0] + ", migrated from SkyyRolls " + c[1] + ", re-rendered " + c[2]);
    @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " migrate self " + c[0] + "/" + c[1] + "/" + c[2]);
    return;
  }
  @PR@ target = null;
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(rest.trim())) { target = (@PR@) o; break; }
    }
  } catch (Throwable t) { target = null; }
  if (target == null) { msg(pr, "no online player called " + rest); return; }
  new @PKG@.GearMigrateTask(pr, target).run();
}""")
M(gad, r"""
public static void read(@PR@ pr, @IS@ h) {
  String id = h.getItemId();
  @BD@ md = h.getMetadata();
  int st = @PKG@.GearData.state(md);
  String[] sn = new String[] { "no document", "SkyyGear v1 document", "SkyyRolls document only (not migrated yet)", "unreadable SkyyGear data", "newer SkyyGear schema" };
  msg(pr, id + ": " + sn[st] + (@PKG@.GearData.gearish(id, md) ? "" : " - not gear"));
  @BD@ d = @PKG@.GearData.effective(id, md);
  if (d != null) {
    int lv = @PKG@.GearLevel.level(id, d);
    Object[] g = @PKG@.GearGate.check(pr.getUuid(), id, d, lv);
    msg(pr, (st == 1 ? "doc: " : "view (in memory): ") + d.toJson());
    msg(pr, "level " + lv + ", gate " + @PKG@.GearData.gate(d) + " -> " + g[1] + " (you: " + g[3] + ", ok " + g[0] + ", enforced " + g[4] + ")");
  }
  msg(pr, "raw: " + (md == null ? "null" : md.toJson()));
}""")
M(gad, r"""
public static void run(@ST@ store, @REF@ ref, @PR@ pr, String action, String rest) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.getInventory() == null) { msg(pr, "no player inventory"); return; }
    @INV@ inv = p.getInventory();
    java.util.UUID u = pr.getUuid();
    String who = pr.getUsername();
    // spec 1.7: no inventory write while SkyyProfiles is swapping this player's profile (read only reads; migrate checks its target)
    if (!action.equals("read") && !action.equals("migrate") && @PKG@.Gear.busy(u)) { msg(pr, "your profile is loading (profile:busy) - try again in a moment"); return; }
    if (action.equals("give")) { giveCmd(pr, inv, rest); return; }
    if (action.equals("migrate")) { migrateCmd(pr, inv, rest); return; }
    @IS@ h = hand(inv);
    if (h == null || h.isEmpty()) { msg(pr, "hold the item first"); return; }
    String id = h.getItemId();
    @BD@ md = h.getMetadata();
    if (action.equals("read")) { read(pr, h); return; }
    if (!@PKG@.GearData.gearish(id, md)) { msg(pr, @PKG@.Gear.itemName(id) + " is not gear"); return; }
    int st = @PKG@.GearData.state(md);
    if (action.equals("clear")) {
      if (md == null || (!md.containsKey(@PKG@.GearDefs.DOC_KEY) && !md.containsKey(@PKG@.GearDefs.VIEW_KEY))) { msg(pr, id + " has no SkyyGear data"); return; }
      Object tx = handC(inv).setItemStackForSlot(handS(inv), @PKG@.GearData.clear(h));
      @PKG@.GearLog.line("ADMIN " + who + " clear " + id);
      msg(pr, "cleared the SkyyGear data of " + id + " - it is stamped Normal again at the next inventory scan" + ok(tx));
      return;
    }
    if (st == 3 || st == 4) { msg(pr, "the gear data on this item is unreadable or from a newer SkyyGear - /gear read shows it; /gear clear removes it"); return; }
    @BD@ d = @PKG@.GearData.effective(id, md);
    if (d == null) { msg(pr, "no gear data"); return; }
    if (action.equals("reroll")) {
      Object[] res = @PKG@.GearForge.reforge(handC(inv), handS(inv), id, @PKG@.GearForge.fp(h), u, who, true);
      msg(pr, (String) res[1] + (((Integer) res[0]).intValue() == 1 ? " " + @PKG@.GearView.modSummary((@BD@) res[4]) : ""));
      return;
    }
    @BD@ nd = d.clone();
    String note = "";
    if (action.equals("rarity")) {
      int r = @PKG@.GearDefs.rIndex(rest.trim());
      if (r < 0) { msg(pr, "usage: /gear rarity <normal|unique|rare|legendary|fabled|mythic|set>"); return; }
      nd.put("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[r]));
      note = " (modifiers kept - /gear reroll rolls them for the new rarity)";
    } else if (action.equals("unid")) {
      nd.put("id", new org.bson.BsonBoolean(false));
      nd.put("mods", new @BA@());
    } else if (action.equals("identify")) {
      if (@PKG@.GearData.identified(d)) { msg(pr, "it is already identified"); return; }
      nd = @PKG@.GearRoll.identify(id, d, u);
    } else if (action.equals("level")) {
      String a = rest.trim().toLowerCase();
      if (a.equals("clear")) nd.remove("lvl");
      else {
        int lv = -1;
        try { lv = Integer.parseInt(a); } catch (Throwable t) { lv = -1; }
        if (lv < 0 || lv > 100) { msg(pr, "usage: /gear level <0-100 | clear>"); return; }
        nd.put("lvl", new org.bson.BsonInt32(lv));
      }
    } else if (action.equals("gate")) {
      String g = rest.trim();
      if (g.length() == 0 || g.indexOf(' ') >= 0) { msg(pr, "usage: /gear gate <class | a SkyySkills skill name, e.g. Mining>"); return; }
      if (g.equalsIgnoreCase("class")) g = "class";
      else if (@PKG@.GearGate.readLevel(u, g) == -1) note = " (SkyySkills does not know that skill - it counts as level 0)";
      nd.put("gate", new org.bson.BsonString(g));
    } else { msg(pr, "unknown action " + action); return; }
    nd.put("at", new org.bson.BsonInt64(System.currentTimeMillis()));
    @IS@ ns = @PKG@.GearData.put(h, nd, u);
    Object tx = handC(inv).setItemStackForSlot(handS(inv), ns);
    @PKG@.GearLog.line("ADMIN " + who + " " + action + " " + id + " " + rest + " -> " + @PKG@.GearView.rollsLine(id, nd));
    msg(pr, action + " done: " + @PKG@.GearView.nameText(id, nd) + " - " + @PKG@.GearView.rollsLine(id, nd) + note + ok(tx));
  } catch (Throwable t) {
    @PKG@.Gear.warn("/gear " + action + " failed: " + t);
    msg(pr, "error: " + t);
  }
}""")
# the player's own /gear: held item lines, active totals, Smithing rarity (spec 8.1, 5.3)
M(gad, r"""
public static void me(@ST@ store, @REF@ ref, @PR@ pr) {
  try {
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.getInventory() == null) return;
    @INV@ inv = p.getInventory();
    java.util.UUID u = pr.getUuid();
    @PKG@.GearGate.refresh(u);
    @IS@ h = hand(inv);
    if (h != null && !h.isEmpty() && @PKG@.GearData.gearish(h.getItemId(), h.getMetadata())) {
      @BD@ d = @PKG@.GearData.effective(h.getItemId(), h.getMetadata());
      if (d == null) msg(pr, "the gear data on your held item is unreadable");
      else {
        String[] ls = @PKG@.GearView.plain(h.getItemId(), d, u);
        for (int i = 0; i < ls.length; i++) pr.sendMessage(@MSG@.raw((i == 0 ? "[Gear] " : "  ") + ls[i]));
      }
    } else msg(pr, "hold a weapon or armor piece to see its gear lines");
    int[] t = @PKG@.GearStats.totals(u, inv);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < t.length; i++) {
      if (t[i] == 0) continue;
      if (sb.length() > 0) sb.append(", ");
      sb.append(@PKG@.GearDefs.S_LABEL[i]).append(' ').append(@PKG@.GearView.valText(@PKG@.GearDefs.S_KEY[i], t[i]));
      if (@PKG@.GearDefs.S_LIVE[i] == 0) sb.append(" (later)");
    }
    msg(pr, "Your active totals (held weapon + worn armor you meet the level for): " + (sb.length() > 0 ? sb.toString() : "none"));
    msg(pr, "Your Smithing rarity: +" + @PKG@.Gear.fnum(@PKG@.GearRoll.smithChance(u)) + " % chance of a better rarity when you craft gear");
  } catch (Throwable t) { @PKG@.Gear.warn("/gear failed: " + t); }
}""")

# ================================================================= /gear (player root) + admin sub-commands (spec 8.1)
# every sub-command: requirePermission("skyygear.admin") AND setPermissionGroups(new String[0]) (lint perm_group_leaks); the root lists
# hytale:Adventurer. Constructors are written out literally so tools/ci/lint.py reads each one.
# /gear give declares --rarity and --unid: AbstractCommand.acceptCall0 runs processOptionalArguments BEFORE execute, and that refuses
# every --name the command did not declare (server.commands.parsing.error.couldNotFindOptionalArgName; VERIFIED bytecode 2026-09-28)
F(subc["give"], "public @OA@ rarityArg;")
F(subc["give"], "public @OA@ unidArg;")
C(subc["give"], r"""
public GearGiveCmd() {
  super("give", "Give gear: /gear give <item> [--rarity <id>] [--unid true]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
  this.rarityArg = withOptionalArg("rarity", "normal, unique, rare, legendary, fabled, mythic or set", @ATY@.STRING);
  this.unidArg = withOptionalArg("unid", "true = the item comes unidentified", @ATY@.BOOLEAN);
}""")
C(subc["read"], r"""
public GearReadCmd() {
  super("read", "Show the gear document and raw metadata of the held item");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["reroll"], r"""
public GearRerollCmd() {
  super("reroll", "Free reforge of the held item");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["clear"], r"""
public GearClearCmd() {
  super("clear", "Remove SkyyGear data from the held item (it becomes Normal again)");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["rarity"], r"""
public GearRarityCmd() {
  super("rarity", "Set the held item's rarity: /gear rarity <id>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["unid"], r"""
public GearUnidCmd() {
  super("unid", "Make the held item unidentified (keeps its rarity)");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["identify"], r"""
public GearIdentifyCmd() {
  super("identify", "Identify the held item for free");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
}""")
C(subc["level"], r"""
public GearLevelCmd() {
  super("level", "Set or clear the held item's level: /gear level <n|clear>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["gate"], r"""
public GearGateCmd() {
  super("gate", "Set the held item's gate skill: /gear gate <skill|class>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["migrate"], r"""
public GearMigrateCmd() {
  super("migrate", "Run the stamp / migration scan now: /gear migrate [player]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
# give: the parsed --rarity / --unid values are appended last, so they win over the raw-text parse in GearAdmin.giveCmd
M(subc["give"], r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  String rest = @PKG@.GearAdmin.rest(ctx, "give");
  try {
    if (ctx.provided(this.rarityArg)) rest = rest + " --rarity " + String.valueOf(ctx.get(this.rarityArg)).trim();
    if (ctx.provided(this.unidArg)) rest = rest + " --unid " + String.valueOf(ctx.get(this.unidArg));
  } catch (Throwable t) { }
  @PKG@.GearAdmin.run(store, ref, pr, "give", rest.trim());
}""")
for _name, _cls, _desc, _args in SUBS:
    if _name == "give":
        continue
    M(subc[_name], r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.GearAdmin.run(store, ref, pr, "%s", %s);
}""" % (_name, ('@PKG@.GearAdmin.rest(ctx, "%s")' % _name) if _args else '""'))
C(gcm, r"""
public GearCmd() {
  super("gear", "Your gear: the held item's lines, your active totals and your Smithing rarity");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addSubCommand(new @PKG@.GearGiveCmd());
  addSubCommand(new @PKG@.GearReadCmd());
  addSubCommand(new @PKG@.GearRerollCmd());
  addSubCommand(new @PKG@.GearClearCmd());
  addSubCommand(new @PKG@.GearRarityCmd());
  addSubCommand(new @PKG@.GearUnidCmd());
  addSubCommand(new @PKG@.GearIdentifyCmd());
  addSubCommand(new @PKG@.GearLevelCmd());
  addSubCommand(new @PKG@.GearGateCmd());
  addSubCommand(new @PKG@.GearMigrateCmd());
}""")
M(gcm, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.GearAdmin.me(store, ref, pr);
}""")

# ================================================================= plugin (spec Appendix A setup() order)
C(pl, "public SkyyGearPlugin(@JPI@ init) { super(init); }")
_reg = "\n".join('  try { getEntityStoreRegistry().registerSystem(new @PKG@.%s()); } catch (Throwable t%d) { @PKG@.Gear.warn("%s could not be registered: " + t%d); }'
                 % (n, i, n, i) for i, n in enumerate(("GearInvSys", "GearThrowSys", "GearCraftSys", "GearTick")))
_fns = "\n".join('  br.put("gear:fn:%s", new @PKG@.GearFn(%d));' % (n, i) for i, n in enumerate(
    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid")))
M(pl, r"""
public void setup() {
  @PKG@.Gear.LOG = getLogger();
  java.nio.file.Path dir = getDataDirectory().resolveSibling("Skyy_SkyyGear");
  @PKG@.GearCfg.DIR = dir;
  @PKG@.GearCfg.FILE = dir.resolve("config.properties");
  @PKG@.GearLog.FILE = dir.resolve("gear.log");
  @PKG@.GearCfg.importRolls(@PKG@.GearCfg.FILE, getDataDirectory().resolveSibling("Skyy_SkyyRolls").resolve("reforge.properties"));
  @PKG@.GearCfg.load();
  if (@PKG@.Gear.bget("config:def:SkyyRolls") != null) @PKG@.Gear.warnOnce("rolls", "SkyyRolls is still enabled - retire it (tools/deploy_set.py RETIRED); both mods register /reforge");
@REG@
  getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.GearReady());
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.GearBye());
  getCommandRegistry().registerCommand(new @PKG@.ReforgeCmd());
  getCommandRegistry().registerCommand(new @PKG@.GearCmd());
  // ---- PART B PLUGS IN HERE (2/4): PARTB_SETUP ----
@PARTBSETUP@
  java.util.Map br = @PKG@.Gear.bridge();
@FNS@
  br.put("gear:gates", @PKG@.GearDefs.GATES);
  br.put("gear:tiers", @PKG@.GearDefs.TIERS);
  @PKG@.Gear.regSetting("gear.blockedPopup", "Gear level popups", "combat", true, "Popup when a weapon is too high level or unidentified");
  @PKG@.Gear.regSetting("gear.armorWarn", "Armor level warning", "combat", true, "Chat line when armor gives no stats because of its level");
  @PKG@.Gear.regSetting("gear.notices", "Gear update notices", "combat", true, "One-time line when your old rolled items move to the new gear system");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyGear] @VER@ ready - /reforge, /gear (admin: /gear give | read | reroll | clear | rarity | unid | identify | level | gate | migrate, node skyygear.admin); rarity + level + modifiers on every weapon and armor piece; crafted gear rolls; SkyyRolls items migrate on first sight; Server Setup -> Gear");
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""".replace("@REG@", _reg).replace("@FNS@", _fns).replace("@PDE@", PDE).replace("@VER@", VERSION)
   .replace("@PARTBSETUP@", "\n".join(PARTB_SETUP)))
M(pl, r"""
protected void shutdown() {
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.GearLog.flush(); } catch (Throwable t2) { }
  super.shutdown();
}""")

# ================================================================= write + build checks (spec 11.1 #2) + assemble
ALL = [gu, gdf, gcf, glg, gdt, glv, grl, ggt, gvw, gst, gnt, gsp, gspt, gfg, gfn, ginv, gthr, gcrs, gcrt, gtk, grft, grdy, gbye, gui,
       rpg, rfc, gad, gmt, gcm] + [subc[s[0]] for s in SUBS] + [pl] + [c for c, _n in PARTB_CLASSES]
for c in ALL:
    c.writeFile(OUT)
kit.write(OUT)
_src = open(os.path.abspath(__file__), encoding="utf-8").read()
assert ("new " + "ItemGridSlot") not in _src, "never put an ItemStack into an ItemGridSlot (spec 5.8)"
for _m in re.finditer(r'#(Skyy[A-Za-z0-9_]*)', _src):
    assert "_" not in _m.group(1), "UI id with an underscore: " + _m.group(1)
for _q in QUAL_IDS:
    _j = json.loads(EXTRA["Server/Item/Qualities/%s.json" % _q])
    assert _j["TextColor"] == RARITIES[QUAL_IDS.index(_q)][2].lower()
print("classes written: %d + %d config kit classes; %d config rows; %d stats; %d quality assets" % (len(ALL), len(kit.classes), len(CFG_ROWS), NS, NR))
jar = os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)
man = B.manifest("SkyyGear", VERSION, "SkyWynn gear: Wynn rarity, level and modifiers on every weapon and armor piece; crafted gear rolls (Smithing raises the rarity); /reforge re-rolls modifiers for coins; old SkyyRolls items keep their rolls; SkyBlock-style tooltips; Server Setup -> Gear. Replaces SkyyRolls. Zero dependencies.", PKG + ".SkyyGearPlugin")
assert man["IncludesAssetPack"] is True
B.assemble(jar, man, OUT, extra_files=EXTRA)
