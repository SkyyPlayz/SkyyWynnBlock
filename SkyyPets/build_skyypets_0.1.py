"""SkyyPets 0.1 - build script (javassist via jpype, tools/skyybuild.py). NEW standalone mod: SLOT PETS, PHASE 1 (records + buffs).
Owner: Skyy (they/them). Run:  python SkyyPets/build_skyypets_0.1.py   -> SkyyPets/SkyyPets-0.1.jar
(no --deploy on purpose: tools/deploy_set.py installs the set once the round is ready). Test: python SkyyPets/test_skyypets_0.1.py

WHY (Skyy's own words, docs/answered/pets.md 2026-10-08): "we should make a pet for every nutral mob in the game, and a lot of the enemys
too, like the rat, the fox, the wolf, the void slug things, the beholder ... i want all the pets of them to be similar just a little
smaller and cuter." + this round: "If you have a few big builds like forging gear tools, and  pets, run through all of them."
Design: research/cloud/Pet-Core-Spec.md PHASE 1 (section 8 row 1) with the accepted defaults (pets are per-profile RECORDS, never items;
paid revive off; slot-1 pet shown by default - the flag is stored, creatures come in 0.2). Rarity / XP curve / perks:
research/cloud/Pets-Spec.md 2-5 (+ research/cloud/Gathering-Numbers-Reconciled.md F7 / S4: gathering pets +10 / +7 Fortune, +5 swing).
Roster: research/Pets-Roster.md (the ~30 launch pets of its question 2 default: the 14 Pets-Spec pets + Tusker + Skyy's named ones + the
vanilla pet models + small critters). Tamework (GPL v3): ideas only (owned cap vs active cap), no code, no numbers.

NO ASSET SHIPPED: the jar holds classes only (IncludesAssetPack false). Model ids are checked against Assets.zip at build (used from 0.2).

1. RECORDS (Pet-Core-Spec 1): <world>/mods/Skyy_SkyyPets/pets/<pkey>.properties per PROFILE (tools/PROFILES-CONTRACT.md pkey helper;
   profile 1 = <uuid>). Keys: v, seq (+1 every write), slot2.unlocked, active.1 / active.2, cmd, shown.1, starter, album, and per pet
   pet.<id>.kind / rarity (1 Common .. 5 Legendary, 6 Mythic = dragons later) / level (1-100) / xp (into the level) / skin / got / src.
   Unknown keys are kept as they are. Pet id = 8 random base-36 characters, never reused (rerolled against every id in every file).
   Writes: tmp + fsync + atomic rename, 5 retries 20 ms on Windows FileSystemException; create / take / slot change / unlock flush at
   once, XP every pets.xp.flushSeconds (30) and on logout / profile switch / shutdown. A file that cannot be read (I/O error, bad \\u
   escape, a folder, a newer format) is NEVER written: that profile shows "could not be read", gets no buffs, no XP, no changes, and
   the server log + /petadmin list say why; it is read again at the next join.
2. LEDGER + STARTUP CHECK (Pet-Core-Spec 7): append-only Skyy_SkyyPets/ledger.log, one tab line per create / take / slot change /
   unlock / quarantine / restore / starter (time id kind rarity level xp from to reason by). At start every pets/*.properties is read
   into a pet id -> profile index; an id found in TWO files stays in the file with the higher seq (equal: the first file name), the
   other copy's lines move to Skyy_SkyyPets/quarantine/<id>-<key>-<ms>.properties (+ ledger + log). A start with no conflict writes
   nothing. /petadmin restore <player> <id> rebuilds a pet nobody owns from its newest ledger line.
3. SLOTS + BUFFS (Pet-Core-Spec 4, no creatures yet): slot 1 = pet slot, 100% of the pet's buffs; slot 2 = summon slot, unlocked per
   profile by the Zone 2 Stable quest (until SkyyQuests: /petadmin unlock; Server Setup "Summon slot unlock" quest / always / off),
   pets.slot2.buffPercent (50%). Stat at level L = (Legendary Lv 100 value) x rarity factor (0.30 / 0.45 / 0.60 / 0.80 / 1.00 / 1.25)
   x L / 100 (Pets-Spec 2). Per kind the values come from the Server Setup table "Pet kinds" (Skill | Start rarity | Stats). Every
   second per online player (world thread, PetTickSys) the totals are recomputed and delivered:
     - Max Health / Stamina / Mana: EntityStatMap StaticModifier(MAX, ADDITIVE) keys skyypet_health / skyypet_stamina / skyypet_mana
       (the SkyySkills Perks.mod pattern; removed at 0)                                                  -> APPLIED BY SKYYPETS
     - Fortune (Mining / Foraging / Farming): skill:bonus:<uuid> source "pets" dd.<skill> = Fortune / 100 (capped by pets.fortune.cap)
       and Wisdom xp.<skill> = Wisdom / 100                                    -> APPLIED BY SKYYSKILLS (its existing reader)
     - Speed %: move:<uuid> source "pets", layer pct (tools/skyymove.py protocol)  -> APPLIED BY SKYYSKILLS' movement applier
     - Strength / Crit Chance / Crit Damage / Defense / Magical Power / Damage % (SkyyGear keys str cc cd def mp dmg) + swing.mining /
       swing.foraging: NEW key pets:stats:<uuid> = unmodifiable java.util.Map String -> Double (only non-zero keys; removed when empty
       and on leave). NOBODY READS IT YET - the next SkyyGear round adds the reader (gear:extra is SkyyAccessories' and is never written
       here). SkyyTrees may read swing.* later.
   Blocked worlds (pets.worlds.noBuffs), part off, a disabled kind, an unreadable file -> no buffs (everything removed).
4. XP (Pet-Core-Spec 1 "XP in"): bridge pets:fn:onxp = Function apply(Object[] { UUID, String skill, Number amount [, String source] })
   -> Boolean (TRUE = at least one slotted pet got XP; never throws). Each slotted pet gets amount x pets.xp.ownPercent (100) when the
   skill is its own ("Combat" matches Combat and every Combat.<class> row), else x pets.xp.otherPercent (50) (R6 lock). Curve:
   XP for level L = 60 (L-1) + 0.04 (L-1)^3 rounded to a nice step (Pets-Spec 3; rows). Lv 100 = max.
   FALLBACK until SkyySkills calls it: every pets.xp.pollSeconds (10) SkyyPets reads SkyySkills' existing skill:fn:xp totals (active
   profile) for pets.xp.fallbackSkills and gives the GROWTH since the last read (the first read and a profile switch only set the
   baseline; a drop or a jump over 1,000,000 re-baselines without XP). The first pets:fn:onxp call whose 4th element is "SkyySkills"
   switches the poll off for good (logged once). SKYYSKILLS MUST PASS "SkyySkills" AS THE 4TH ELEMENT; a call without a 4th element or
   from another mod gives XP but leaves the poll on (fixer 2: a forgetful caller must not stop pet XP from every other skill).
   The fallback is SkyyPets' OWN addition (Pet-Core-Spec 1 has only the SkyySkills hook; row pets.xp.fallback turns it off). It polls
   the per-class Combat.<class> rows (never the bare "Combat" = current class: a class switch would read as a gain), skips a player
   whose profile key changed since the last tick (no cross-profile delta), and admin /skills xp grants feed it too (admin only).
   Fixer round 2026-10-09: a pet file with bytes but no v=1 line, or 0 bytes, is unreadable (never overwritten, no new starter);
   every 30 s PetTimer.sweep() runs leave() again for anyone no longer online (a tick after PlayerDisconnectEvent); the locked summon
   slot text says "closed on this server" when Server Setup has it off.
   Fixer 2 (2026-10-09): a file read after the startup scan adds its pet ids to the index (PetStore.indexLate; a clash is logged and
   left for the next startup check); /petadmin restore needs an 8-character id + an existing kind and refuses while any pet file is
   unreadable (it may hold that id); ledger "-" lines (unlock / lock) are never a restore source; publish() re-posts an entry another
   mod removed; shutdown takes pets:fn:onxp + every "pets" bridge entry off; buff texts show values under 1 with two decimals.
   NOT IN 0.1 (accepted defaults with nothing to act on yet): the hide / show control for the slot-1 pet (the shown.1 flag is stored;
   the control comes with the creatures in 0.2) and the paid early revive rows (0.4 - nothing can be defeated in 0.1).
   /petadmin is an in-game command only (AbstractPlayerCommand - the server console cannot run it).
5. PAGE /pets (alias /pet; hytale:Adventurer): the two slot rows (pet, rarity colour, Lv, XP, state), the owned list (8 a page,
   Prev / Next), Details (kind, rarity, level, XP, skill, slot, buffs in each slot) with Pet slot / Summon slot / Take out / Back.
   Vanilla look from tools/skyyui.py, inline, fits 1080. Item icons = plain vanilla item ids (the skill's tool), never a stack.
6. ADMIN /petadmin (op only: requirePermission skyypets.admin + empty permission groups on the command and every usage variant):
   give <player> <kind> [rarity] [level] | take <player> <id> | unlock <player> | lock <player> | list <player> | restore <player>
   <id> | xp <player> <skill> <amount> | kinds. Targets must be online.
7. SERVER SETUP tab "Pets" (tools/skyycfg.py kit 1.1, KEEP=10): Pets, Pet XP, Rarity, Pet kinds (table).
8. STARTER (Pet-Core-Spec 4 "Unlock: from the start (starter Rabbit)"): the first time a profile is seen, it gets one Common Lv 1
   pets.starter (Rabbit) in the pet slot, once per profile (marker starter=<ms>; "none" = off).
ENGINE SEAM: PetsEng (online players, names, chat) - the harness sets PetsEng.API; everything else runs for real in the harness.
REMOVAL FLOOR: the skyypet_* MAX modifiers are saved with the player. Before removing SkyyPets: Server Setup > Pets > Pets OFF, let every
player log in once (the tick removes them), then remove the jar.
"""
import sys, os, json, zipfile, re, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyui as SUI
import skyycfg as CFG

if "--deploy" in sys.argv:
    raise SystemExit("SkyyPets: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
MOD = "SkyyPets"
NODE = "skyypets.admin"
PKG = "com.skyy.pets"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
CFG_FILE = "Skyy_SkyyPets/config.properties"
SUI.verify()
KIT_ID = SUI.kit_id()
COL = SUI.COLOR
COL_OK, COL_ERR, COL_INFO, COL_GOLD = COL["success"], COL["error"], COL["info"], COL["gold"]

# ---------------------------------------------------------------------------------------------------------------- the launch roster
# (kind id, skill, start rarity, Legendary Lv 100 stats, vanilla model id (0.2+), roster zone)
# Stats: Pets-Spec 5 (the 14 launch pets, Fortune per Gathering-Numbers-Reconciled F7 / S4) - placeholders, every line is a Server Setup
# table row. The other pets reuse one of those as an ARCHETYPE (Pets-Roster 3.2: "the archetype holds the perks and numbers").
# Conditional perks of Pets-Spec ("while below ground", "with bows", "at low health", "in forests") are flat in 0.1 (noted in the report).
MELEE, RANGED, MAGIC, TANK = "str:20,cd:15,cc:5", "cc:20,cd:25", "mp:40,mana:40", "health:60,def:20"
SPEEDY = "speed:5,stamina:20"
KINDS = [
    # the 14 Pets-Spec pets (+ Tusker, the Berserker pet; art id SkyyPets_Tusker)
    ("Rabbit", "Farming", "Common", "fortune.farming:10", "Rabbit", "Z1"),
    ("Chicken", "Farming", "Common", "fortune.farming:7,stamina:10", "Chicken", "Z1"),
    ("Goat", "Mining", "Uncommon", "fortune.mining:10,swing.mining:5", "Goat", "Z3"),
    ("Warthog", "Mining", "Uncommon", "fortune.mining:7,def:15", "Warthog", "Z2"),
    ("Bear", "Foraging", "Rare", "fortune.foraging:10,swing.foraging:5,str:5", "Bear_Grizzly", "Z3"),
    ("Turkey", "Foraging", "Uncommon", "fortune.foraging:7", "Turkey", "Z1"),
    ("Wolf", "Combat", "Rare", MELEE, "Wolf_Black", "Z3"),
    ("Boar", "Combat", "Uncommon", TANK, "Boar", "Z1"),
    ("Hawk", "Combat", "Epic", RANGED, "Hawk", "Z2"),
    ("Ram", "Combat", "Epic", "def:50,health:80", "Ram", "Z3"),
    ("Skrill", "Combat", "Epic", MAGIC, "Skrill", "Z4"),
    ("Tusker", "Combat", "Rare", "str:30", "Warthog", "Z2"),
    ("Mouflon", "Combat", "Epic", "mp:30,health:50", "Mouflon", "Z2"),
    ("Horse", "Exploration", "Uncommon", SPEEDY, "Horse", "Z2"),
    ("Camel", "Exploration", "Rare", "stamina:30", "Camel", "Z2"),
    # Skyy's named ones (docs/answered/pets.md 2026-10-08)
    ("Fox", "Combat", "Uncommon", MELEE, "Fox", "Z1"),
    ("Rat", "Exploration", "Common", SPEEDY, "Rat", "Z1"),
    ("Skeleton", "Combat", "Rare", RANGED, "Skeleton", "Z1"),
    ("VoidEye", "Combat", "Epic", MAGIC, "Eye_Void", "Z4"),
    ("VoidCrawler", "Combat", "Rare", TANK, "Crawler_Void", "Z4"),
    ("VoidLarva", "Combat", "Uncommon", MAGIC, "Larva_Void", "Z4"),
    # the vanilla pet models + small critters (Pets-Roster question 2 default)
    ("Cat", "Foraging", "Common", "fortune.foraging:7", "Cat", "Z1"),
    ("Dog", "Combat", "Common", MELEE, "Dog", "Z1"),
    ("Corgi", "Farming", "Common", "fortune.farming:7", "Corgi", "Z1"),
    ("Frog", "Farming", "Common", "fortune.farming:7", "Frog_Green", "Z1"),
    ("Mouse", "Mining", "Common", "fortune.mining:7", "Mouse", "Z1"),
    ("Squirrel", "Foraging", "Common", "fortune.foraging:7", "Squirrel", "Z1"),
    ("Bunny", "Farming", "Common", "fortune.farming:10", "Bunny", "Z1"),
    ("Meerkat", "Mining", "Common", "fortune.mining:7", "Meerkat", "Z2"),
    ("Gecko", "Exploration", "Common", SPEEDY, "Gecko", "Z2"),
]
RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
FACTORS = ["0.3", "0.45", "0.6", "0.8", "1", "1.25"]
# stat keys: (key, display name, delivery) - delivery: gear = pets:stats (SkyyGear later), swing = pets:stats (SkyyTrees later),
# stat = our EntityStatMap modifier, move = move:<uuid>, dd / xp = skill:bonus:<uuid>
STATS = [("str", "Strength", "gear"), ("cc", "Crit Chance", "gear"), ("cd", "Crit Damage", "gear"), ("def", "Defense", "gear"),
         ("mp", "Magical Power", "gear"), ("dmg", "Damage %", "gear"),
         ("swing.mining", "Mining Swing %", "swing"), ("swing.foraging", "Chopping Swing %", "swing"),
         ("health", "Max Health", "stat"), ("stamina", "Max Stamina", "stat"), ("mana", "Max Mana", "stat"), ("speed", "Speed %", "move"),
         ("fortune.mining", "Mining Fortune", "dd"), ("fortune.foraging", "Foraging Fortune", "dd"), ("fortune.farming", "Farming Fortune", "dd"),
         ("wisdom.mining", "Mining Wisdom", "xp"), ("wisdom.foraging", "Foraging Wisdom", "xp"), ("wisdom.farming", "Farming Wisdom", "xp"),
         ("wisdom.cooking", "Cooking Wisdom", "xp")]
STAT_KEYS = [s[0] for s in STATS]
SKILL_ICON = {"Farming": "Tool_Hoe_Iron", "Mining": "Tool_Pickaxe_Iron", "Foraging": "Tool_Hatchet_Iron", "Combat": "Weapon_Sword_Iron",
              "Exploration": "Tool_Map"}          # the SkyySkills row icons (vanilla item ids, checked below)
ICON_OTHER = "Tool_Map"
# per-class Combat rows, never the bare "Combat" (= the CURRENT class skill: a class switch would read as a big gain)
POLL_SKILLS = ("Mining,Foraging,Farming,Combat.Archer,Combat.Warrior,Combat.Assassin,Combat.Shaman,Combat.Mage,Combat.Berserker,"
               "Combat.Priest,Acrobatics,Alchemy,Smithing,Cooking,Exploration")
# one colour per rarity: the vanilla item quality colours (Server/Item/Qualities) + the SkyyGear Mythic colour
RARITY_COLORS = [SUI.QUALITY["Common"], SUI.QUALITY["Uncommon"], SUI.QUALITY["Rare"], SUI.QUALITY["Epic"], SUI.QUALITY["Legendary"],
                 SUI.RARITY["Mythic"]]

# ================= build-time desk checks (Assets.zip, read only)
az = zipfile.ZipFile(ASSETS)
AZ = az.namelist()
MODELS = set(n.rsplit("/", 1)[1][:-5] for n in AZ if n.startswith("Server/Models/") and n.endswith(".json"))
ITEMS = set(n.rsplit("/", 1)[1][:-5] for n in AZ if n.startswith("Server/Item/Items/") and n.endswith(".json"))
for _k in KINDS:
    assert _k[4] in MODELS, "model %s of pet %s is not in Assets.zip Server/Models" % (_k[4], _k[0])
    assert _k[1] in SKILL_ICON and _k[2] in RARITIES[:5], _k
    for _p in _k[3].split(","):
        assert _p.split(":")[0] in STAT_KEYS, (_k[0], _p)
for _i in list(SKILL_ICON.values()) + [ICON_OTHER]:
    assert _i in ITEMS, "icon item %s missing in Assets.zip" % _i
assert len(KINDS) == 30 and len(set(k[0] for k in KINDS)) == 30
assert "Rabbit" in [k[0] for k in KINDS]

# ================= Java
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE, "KITID": KIT_ID,
    "COLOK": COL_OK, "COLERR": COL_ERR, "COLINF": COL_INFO, "COLGLD": COL_GOLD,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "CB": "com.hypixel.hytale.component.CommandBuffer",
    "ACH": "com.hypixel.hytale.component.ArchetypeChunk",
    "QRY": "com.hypixel.hytale.component.query.Query",
    "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
    "UNI": "com.hypixel.hytale.server.core.universe.Universe",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "ESM": "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap",
    "DST": "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes",
    "MODF": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier",
    "SMO": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier",
    "MTG": "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget",
    "CAL": "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType",
    "PDE": "com.hypixel.hytale.server.core.event.events.player.PlayerDisconnectEvent",
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
for c, m in ((T["PR"], "getUuid"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"), (T["PR"], "getComponentType"), (T["PR"], "isValid"),
             (T["UNI"], "get"), (T["UNI"], "getPlayers"), (T["UNI"], "getPlayer"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["MSG"], "raw"),
             (T["MSG"], "color"), (T["PLA"], "getComponentType"), (T["PLA"], "getPageManager"), (T["PLA"], "isWaitingForClientReady"),
             (T["ESM"], "getComponentType"), (T["ESM"], "get"), (T["ESM"], "putModifier"), (T["ESM"], "removeModifier"),
             (T["ESM"], "getModifier"), (T["DST"], "getHealth"), (T["DST"], "getStamina"), (T["DST"], "getMana"), (T["MTG"], "MAX"),
             (T["CAL"], "ADDITIVE"), (T["PDE"], "getPlayerRef"), (T["EST"], "getWorld"), (T["WLD"], "getName"), (T["ST"], "getComponent"),
             (T["ST"], "getExternalData"), (T["CB"], "getComponent"), (T["ACH"], "getReferenceTo"), (T["ETS"], "tick"),
             (T["PAGE"], "rebuild"), (T["PAGE"], "close"), (T["EVD"], "of"), (T["EVD"], "append"), (T["UEB"], "addEventBinding"),
             (T["UCB"], "set"), (T["UCB"], "appendInline"), (AC, "requirePermission"), (AC, "setPermissionGroups"),
             (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "addAliases"), (T["CTX"], "get"), (T["ATY"], "STRING"),
             (PB_, "getCommandRegistry"), (PB_, "getEntityStoreRegistry"), (PB_, "getEventRegistry"), (PB_, "getLogger"),
             (PB_, "getDataDirectory"), (PB_, "shutdown"), ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem"),
             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):
    B.probe(pool, c, m)
_sig = lambda cls, name: [str(m.getSignature()) for m in pool.get(cls).getDeclaredMethods() if str(m.getName()) == name]
assert "(FILcom/hypixel/hytale/component/ArchetypeChunk;Lcom/hypixel/hytale/component/Store;Lcom/hypixel/hytale/component/CommandBuffer;)V" in _sig(T["ETS"], "tick"), _sig(T["ETS"], "tick")
assert any(s.startswith("(ILjava/lang/String;Lcom/hypixel/hytale/server/core/modules/entitystats/modifier/Modifier;)") for s in _sig(T["ESM"], "putModifier")), _sig(T["ESM"], "putModifier")

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


def jstr(s):
    return json.dumps(s)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs) if xs else "new String[0]"


ALL = []


def cls(name, sup=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    ALL.append(c)
    return c


# =====================================================================================================================
# PetsLog: server log (+ LINES, a harness hook) + the bridge helpers
# =====================================================================================================================
log = cls("PetsLog")
F(log, "public static @LOG@ LOG;")
F(log, "public static java.util.List LINES;")
F(log, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
M(log, r"""
public static void info(String msg) {
  try { if (LINES != null) LINES.add("INFO " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyPets] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LINES != null) LINES.add("WARN " + msg); } catch (Throwable t) { }
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyPets] " + msg); } catch (Throwable t) { }
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
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
}""")
# 12.5 -> "12.5", 20.0 -> "20", 0.04 -> "0" (one decimal)
M(log, r"""
public static String num(double d) {
  if (Double.isNaN(d) || Double.isInfinite(d)) return "0";
  long t = Math.round(d * 10.0);
  long a = Math.abs(t);
  String s = (a % 10L == 0L) ? String.valueOf(a / 10L) : (a / 10L) + "." + (a % 10L);
  return (t < 0L ? "-" : "") + s;
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

# =====================================================================================================================
# PetsApi (interface) + PetsEng: the engine seam (online players, names, chat). API == null in game = the real calls.
# =====================================================================================================================
api = pool.makeInterface(PKG + ".PetsApi")
ALL.append(api)
for sig in ("public abstract java.util.UUID[] online();",
            "public abstract java.util.UUID byName(String name);",
            "public abstract String nameOf(java.util.UUID u);",
            "public abstract void tell(java.util.UUID u, String text, String color);"):
    M(api, sig)
eng = cls("PetsEng")
F(eng, "public static volatile @PKG@.PetsApi API = null;")
M(eng, r"""
public static void say(@PR@ pr, String text, String color) {
  if (pr == null) return;
  try { @MSG@ m = @MSG@.raw(text); if (color != null) m = m.color(color); pr.sendMessage(m); } catch (Throwable t) { }
}""")
M(eng, r"""
public static java.util.UUID[] online() {
  if (API != null) return API.online();
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      @PR@ pr = (@PR@) o;
      if (pr.getUuid() != null) out.add(pr.getUuid());
    }
  } catch (Throwable t) { }
  java.util.UUID[] a = new java.util.UUID[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (java.util.UUID) out.get(i);
  return a;
}""")
M(eng, r"""
public static java.util.UUID byName(String name) {
  if (name == null || name.trim().length() == 0) return null;
  if (API != null) return API.byName(name.trim());
  try {
    java.util.Iterator it = @UNI@.get().getPlayers().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @PR@)) continue;
      @PR@ pr = (@PR@) o;
      if (name.trim().equalsIgnoreCase(pr.getUsername())) return pr.getUuid();
    }
  } catch (Throwable t) { }
  return null;
}""")
M(eng, r"""
public static String nameOf(java.util.UUID u) {
  if (u == null) return "?";
  if (API != null) return API.nameOf(u);
  try { @PR@ pr = @UNI@.get().getPlayer(u); if (pr != null) return pr.getUsername(); } catch (Throwable t) { }
  return u.toString();
}""")
M(eng, r"""
public static void tell(java.util.UUID u, String text, String color) {
  if (u == null) return;
  if (API != null) { API.tell(u, text, color); return; }
  try { @PR@ pr = @UNI@.get().getPlayer(u); if (pr != null) say(pr, text, color); } catch (Throwable t) { }
}""")
M(eng, r"""
public static String worldOf(@ST@ st) {
  try {
    Object ext = st == null ? null : st.getExternalData();
    if (ext instanceof @EST@) { @WLD@ w = ((@EST@) ext).getWorld(); return w == null ? null : w.getName(); }
  } catch (Throwable t) { }
  return null;
}""")
M(eng, r"""
public static boolean open(@REF@ ref, @ST@ st, @PAGE@ page) {
  if (ref == null || st == null || page == null) return false;
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return false;
    p.getPageManager().openCustomPage(ref, st, page);
    return true;
  } catch (Throwable t) { @PKG@.PetsLog.warn("the Pets page could not open: " + t); return false; }
}""")

# =====================================================================================================================
# PetKind (one row of the Pet kinds table) + PetsCfg (settings; the kit binds the scalars, RELOAD re-reads the table)
# =====================================================================================================================
kind = cls("PetKind")
for _f in ("String id", "String name", "String skill", "int rarity", "String stats", "String[] keys", "double[] vals", "boolean on",
           "String model", "String icon"):
    F(kind, "public %s;" % _f)
F(kind, "public static final String[] STAT_KEYS = %s;" % jarr(STAT_KEYS))
F(kind, "public static final String[] STAT_NAMES = %s;" % jarr([s[1] for s in STATS]))
F(kind, "public static final String[] STAT_HOW = %s;" % jarr([s[2] for s in STATS]))
F(kind, "public static final String[] RARITIES = %s;" % jarr(RARITIES))
F(kind, "public static final String[] MODEL_IDS = %s;" % jarr([k[0] + "=" + k[4] for k in KINDS]))
F(kind, "public static final String[] SKILL_ICONS = %s;" % jarr([k + "=" + v for k, v in sorted(SKILL_ICON.items())]))
C(kind, 'public PetKind() { this.id = ""; this.name = ""; this.skill = ""; this.stats = ""; this.keys = new String[0]; this.vals = new double[0]; this.on = true; this.model = ""; this.icon = %s; }' % jstr(ICON_OTHER))
M(kind, r"""
public static int statIndex(String k) {
  if (k == null) return -1;
  for (int i = 0; i < STAT_KEYS.length; i++) if (STAT_KEYS[i].equals(k)) return i;
  return -1;
}""")
# "Common" / "legendary" / "3" -> 1..6, 0 = not a rarity
M(kind, r"""
public static int rarityOf(String s) {
  if (s == null) return 0;
  String t = s.trim();
  for (int i = 0; i < RARITIES.length; i++) if (RARITIES[i].equalsIgnoreCase(t)) return i + 1;
  try { int n = Integer.parseInt(t); return n >= 1 && n <= RARITIES.length ? n : 0; } catch (Throwable x) { return 0; }
}""")
M(kind, r"""
public static String rarityName(int r) {
  return r >= 1 && r <= RARITIES.length ? RARITIES[r - 1] : "Unknown";
}""")
# "VoidEye" -> "Void Eye"
M(kind, r"""
public static String display(String id) {
  if (id == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < id.length(); i++) {
    char c = id.charAt(i);
    if (c == '_') { b.append(' '); continue; }
    if (i > 0 && Character.isUpperCase(c) && Character.isLowerCase(id.charAt(i - 1))) b.append(' ');
    b.append(c);
  }
  return b.toString();
}""")
M(kind, r"""
public static String lookup(String[] pairs, String k, String d) {
  if (k == null) return d;
  for (int i = 0; i < pairs.length; i++) {
    int e = pairs[i].indexOf('=');
    if (e > 0 && pairs[i].substring(0, e).equals(k)) return pairs[i].substring(e + 1);
  }
  return d;
}""")
# "str:20,cd:15" -> null when a part is not key:number with a known key
M(kind, r"""
public static Object[] parseStats(String s) {
  java.util.ArrayList ks = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList();
  if (s == null) return null;
  String t = s.trim();
  if (t.length() > 0 && !t.equals("-") && !t.equalsIgnoreCase("none")) {
    String[] a = t.split(",");
    for (int i = 0; i < a.length; i++) {
      String p = a[i].trim();
      if (p.length() == 0) continue;
      int c = p.indexOf(':');
      if (c <= 0) return null;
      String k = p.substring(0, c).trim().toLowerCase();
      if (statIndex(k) < 0) return null;
      double v = 0.0;
      try { v = Double.parseDouble(p.substring(c + 1).trim()); } catch (Throwable x) { return null; }
      if (Double.isNaN(v) || Double.isInfinite(v) || v < -100000.0 || v > 100000.0) return null;
      if (ks.contains(k)) return null;
      ks.add(k);
      vs.add(Double.valueOf(v));
    }
  }
  String[] ka = new String[ks.size()];
  double[] va = new double[vs.size()];
  for (int i = 0; i < ka.length; i++) { ka[i] = (String) ks.get(i); va[i] = ((Double) vs.get(i)).doubleValue(); }
  return new Object[] { ka, va };
}""")
M(kind, r"""
public static boolean skillOk(String s) {
  if (s == null) return false;
  String t = s.trim();
  if (t.length() < 2 || t.length() > 24) return false;
  for (int i = 0; i < t.length(); i++) {
    char c = t.charAt(i);
    if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') && c != '.') return false;
  }
  return true;
}""")
# value "Skill<sep>Rarity<sep>Stats" -> a kind, null = bad (Mythic is for dragons, never a start rarity)
M(kind, r"""
public static @PKG@.PetKind parse(String id, String value, String sep) {
  if (id == null || value == null) return null;
  String k = id.trim();
  if (k.length() == 0 || k.length() > 40) return null;
  for (int i = 0; i < k.length(); i++) {
    char c = k.charAt(i);
    if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') && !(c >= '0' && c <= '9') && c != '_') return null;
  }
  String[] p = value.split(java.util.regex.Pattern.quote(sep), -1);
  if (p.length != 3) return null;
  if (!skillOk(p[0])) return null;
  int r = rarityOf(p[1]);
  if (r < 1 || r > 5) return null;
  Object[] st = parseStats(p[2]);
  if (st == null) return null;
  @PKG@.PetKind out = new @PKG@.PetKind();
  out.id = k;
  out.name = display(k);
  out.skill = p[0].trim();
  out.rarity = r;
  out.stats = p[2].trim();
  out.keys = (String[]) st[0];
  out.vals = (double[]) st[1];
  out.model = lookup(MODEL_IDS, k, "");
  out.icon = lookup(SKILL_ICONS, out.skill, %s);
  return out;
}""".replace("%s", jstr(ICON_OTHER)))
M(kind, r"""
public double value(String key) {
  for (int i = 0; i < this.keys.length; i++) if (this.keys[i].equals(key)) return this.vals[i];
  return 0.0;
}""")
# skill match: "Combat" matches Combat and every Combat.<class> row; else case-insensitive equality
M(kind, r"""
public static boolean skillMatch(String petSkill, String skill) {
  if (petSkill == null || skill == null) return false;
  String a = petSkill.trim(), b = skill.trim();
  if (a.equalsIgnoreCase(b)) return true;
  if (a.equalsIgnoreCase("Combat") && b.toLowerCase().startsWith("combat.")) return true;
  return false;
}""")

cfgc = cls("PetsCfg")
SCALARS = [
    # key, label, cat, type, default, min, max, opts, unit, flags, help, FIELD, java type
    ("pets.enabled", "Pets", "pets", "bool", "true", "", "", "", "", "live,part,danger",
     "Off = no pet buffs, no pet XP, no starter pet. Every pet record is kept.", "ON", "boolean"),
    ("pets.owned.max", "Pets one profile may own", "pets", "int", "120", "1", "1000", "", "", "live",
     "Giving a pet to a full collection is refused. Lowering it never removes a pet.", "OWNED_MAX", "int"),
    ("pets.slot2.unlock", "Summon slot unlock", "pets", "choice", "quest", "", "", "quest|Stable quest,always|Always open,off|Closed", "",
     "live", "Stable quest = per profile (the Zone 2 quest or /petadmin unlock). Closed = nobody.", "SLOT2_MODE", "java.lang.String"),
    ("pets.slot2.buffPercent", "Summon slot buff strength", "pets", "int", "50", "0", "100", "", "%", "live",
     "A pet in the summon slot gives this much of its buffs.", "SLOT2_PCT", "int"),
    ("pets.starter", "Starter pet", "pets", "text", "Rabbit", "1", "40", "", "", "live",
     "Every new profile gets one Common Lv 1 pet of this kind in its pet slot. none = no starter.", "STARTER", "java.lang.String"),
    ("pets.fortune.cap", "Pet Fortune cap", "pets", "dec", "10", "0", "1000", "", "", "live",
     "Most Fortune per skill all pets together may add (Mining, Foraging, Farming).", "FORT_CAP", "double"),
    ("pets.swing.cap", "Pet swing cap", "pets", "dec", "5", "0", "100", "", "%", "live",
     "Most swing speed per skill all pets together may add (shared with SkyyTrees later).", "SWING_CAP", "double"),
    ("pets.worlds.noBuffs", "Worlds without pet buffs", "pets", "text", "-", "1", "2000", "", "", "live",
     "World names, comma separated. - = none. Pets give no buffs there.", "NOBUFF", "java.lang.String"),
    ("pets.kinds.off", "Pet kinds switched off", "kinds", "text", "-", "1", "2000", "", "", "live",
     "Kind ids, comma separated. - = none. Owned pets of these kinds are kept but give nothing.", "KINDS_OFF", "java.lang.String"),
    ("pets.xp.ownPercent", "XP from the pet's own skill", "xp", "int", "100", "0", "500", "", "%", "live",
     "A slotted pet gets this much of the XP you earn in its own skill.", "XP_OWN", "int"),
    ("pets.xp.otherPercent", "XP from other skills", "xp", "int", "50", "0", "500", "", "%", "live",
     "...and this much of the XP you earn in every other skill.", "XP_OTHER", "int"),
    ("pets.curve.linear", "Level curve: per level", "xp", "dec", "60", "1", "100000", "", "", "live",
     "XP for level L = this x (L-1) + the cubic number x (L-1) cubed, rounded.", "CURVE_LIN", "double"),
    ("pets.curve.cubic", "Level curve: cubic", "xp", "dec", "0.04", "0", "100", "", "", "live",
     "The cubic part of the level curve (0.04 = 1.28 million XP to Lv 100).", "CURVE_CUB", "double"),
    ("pets.xp.flushSeconds", "Save pet XP every", "xp", "int", "30", "5", "600", "", "s", "live,adv",
     "Pet XP is saved this often (and on logout). A crash loses at most this much pet XP.", "FLUSH_S", "int"),
    ("pets.xp.fallback", "Read skill XP (fallback)", "xp", "bool", "true", "", "", "", "", "live",
     "Until SkyySkills reports XP to pets itself, read its XP totals and give pets the growth.", "FALLBACK", "boolean"),
    ("pets.xp.pollSeconds", "Fallback read every", "xp", "int", "10", "2", "120", "", "s", "live,adv",
     "How often the fallback reads the skill XP totals.", "POLL_S", "int"),
    ("pets.xp.fallbackSkills", "Fallback skills", "xp", "text", POLL_SKILLS, "1", "400", "", "", "live,adv",
     "SkyySkills skills the fallback reads. Use Combat.<class> rows; a bare Combat is skipped.", "POLL_SKILLS", "java.lang.String"),
]
for _i, _r in enumerate(RARITIES):
    SCALARS.append(("pets.rarity.%s" % _r.lower(), "%s stat factor" % _r, "rarity", "dec", FACTORS[_i], "0", "10", "", "x", "live",
                    "Buff = Legendary Lv 100 value x this x level / 100.", "F%d" % (_i + 1), "double"))
TABLES = [
    ("pets.kinds", "Pet kinds", "kinds", "table", "", "", "400", "text|text|text;none;Skill|Start rarity|Stats", "", "live",
     "Stats at Legendary Lv 100, e.g. str:20,cd:15. Keys: /petadmin kinds. Skill gets 100% pet XP.", "kind."),
]
for _r in SCALARS + TABLES:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, (_r[0], len(_r[1]), len(_r[10]))
_chk = {"pets.starter": "PetsCfg.checkStarter", "pets.kinds.off": "PetsCfg.checkList", "pets.worlds.noBuffs": "PetsCfg.checkList",
        "pets.xp.fallbackSkills": "PetsCfg.checkSkills"}
CFG_ROWS = [r[:11] + ("field:PetsCfg.%s" % r[11] + (";check=%s" % _chk[r[0]] if r[0] in _chk else ""),) for r in SCALARS]
CFG_ROWS += [r[:11] + ("reload@%s:%s;sep=/;check=PetsCfg.checkKind" % (CFG_FILE, r[11]),) for r in TABLES]
CFG_CATS = [("pets", "Pets"), ("xp", "Pet XP"), ("rarity", "Rarity"), ("kinds", "Pet kinds")]
CFG_NOTE = "Chat: /pets (players), /petadmin give | take | unlock | lock | list | restore | xp | kinds (admins)."
assert len(CFG_NOTE) <= 100
_d = ["# SkyyPets %s - slot pets. Also in game: SkyWynn Menu > Server Setup > Pets (admins). Times in seconds." % VERSION,
      "# Hand edits: Server Setup > Pets > Reload (or restart).", ""]
for _r in SCALARS:
    _d.append("# %s - %s" % (_r[1], _r[10]))
    _d.append("%s=%s" % (_r[0], _r[4]))
_d += ["", "# Pet kinds: kind.<Kind>=Skill/Start rarity/Stats at Legendary Lv 100 (stat:value, comma separated; - = none).",
       "# Stat keys: " + ", ".join(STAT_KEYS) + ".",
       "# Applied now: health stamina mana (max stats), speed, fortune.* and wisdom.* (via SkyySkills). The SkyyGear stats",
       "# (str cc cd def mp dmg) and swing.* are published on pets:stats:<uuid> for SkyyGear / SkyyTrees to read later."]
for _k in KINDS:
    _d.append("kind.%s=%s/%s/%s" % (_k[0], _k[1], _k[2], _k[3]))
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
    elif jt == "double":
        F(cfgc, "public static volatile double %s = %s;" % (fld, repr(float(dv))))
    else:
        F(cfgc, "public static volatile String %s = %s;" % (fld, jstr(dv)))
F(cfgc, "public static volatile @PKG@.PetKind[] KINDS = new @PKG@.PetKind[0];")
F(cfgc, "public static java.nio.file.Path FILE;")
F(cfgc, "public static volatile long LOADS = 0L;")
F(cfgc, "public static final String DEFAULT_TEXT = %s;" % jstr(DEFAULT_TEXT))
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
public static double dv(java.util.Properties p, String k, double d, double lo, double hi) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null) return d;
  try { double v = Double.parseDouble(s.trim()); if (Double.isNaN(v)) return d; return v < lo ? lo : (v > hi ? hi : v); } catch (Throwable t) { return d; }
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
    elif jt == "double":
        _ap.append('  %s = dv(p, %s, %s, %s, %s);' % (fld, jstr(k), repr(float(dv)), repr(float(r[5])), repr(float(r[6]))))
    else:
        _ap.append('  %s = sv(p, %s, %s);' % (fld, jstr(k), jstr(dv)))
_ap.append('  if (!SLOT2_MODE.equals("quest") && !SLOT2_MODE.equals("always") && !SLOT2_MODE.equals("off")) SLOT2_MODE = "quest";')
_ap.append("}")
M(cfgc, "\n".join(_ap))
M(cfgc, r"""
public static void applyTables(java.util.Properties p) {
  java.util.ArrayList ks = new java.util.ArrayList();
  if (p != null) {
    java.util.ArrayList keys = new java.util.ArrayList(p.stringPropertyNames());
    java.util.Collections.sort(keys);
    for (int i = 0; i < keys.size(); i++) {
      String k = (String) keys.get(i);
      if (!k.startsWith("kind.")) continue;
      @PKG@.PetKind pk = @PKG@.PetKind.parse(k.substring(5), p.getProperty(k), "/");
      if (pk == null) { @PKG@.PetsLog.warnOnce("kind:" + k + "=" + p.getProperty(k), k + "=" + p.getProperty(k) + " is not 'Skill/Start rarity/Stats' with known stat keys - that kind is off until it is fixed"); continue; }
      ks.add(pk);
    }
  }
  @PKG@.PetKind[] a = new @PKG@.PetKind[ks.size()];
  for (int i = 0; i < a.length; i++) a[i] = (@PKG@.PetKind) ks.get(i);
  KINDS = a;
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
    @PKG@.PetsLog.warn("could not read " + f + ": " + t + " - using the built-in defaults");
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
    @PKG@.PetsLog.info("wrote the default " + f.getFileName());
  } catch (Throwable t) { @PKG@.PetsLog.warn("could not write the default " + f + ": " + t); }
}""")
M(cfgc, r"""
public static void applyAll(java.util.Properties p) {
  java.util.Properties q = p != null ? p : props(DEFAULT_TEXT);
  applyScalars(q);
  applyTables(q);
  LOADS = LOADS + 1L;
}""")
M(cfgc, r"""
public static void reloadAll() {
  applyAll(read(FILE));
}""")
M(cfgc, r"""
public static void load(java.nio.file.Path modsDir) {
  FILE = modsDir == null ? null : modsDir.resolve("Skyy_SkyyPets").resolve("config.properties");
  seed(FILE);
  reloadAll();
}""")
M(cfgc, r"""
public static boolean listed(String list, String s) {
  if (list == null || s == null) return false;
  String[] a = list.split(",");
  for (int i = 0; i < a.length; i++) if (a[i].trim().equalsIgnoreCase(s.trim())) return true;
  return false;
}""")
# the kind of that id (null = unknown); off kinds still answer (kindOn says whether it gives anything)
M(cfgc, r"""
public static @PKG@.PetKind kind(String id) {
  if (id == null) return null;
  @PKG@.PetKind[] a = KINDS;
  for (int i = 0; i < a.length; i++) if (a[i].id.equalsIgnoreCase(id.trim())) return a[i];
  return null;
}""")
M(cfgc, r"""
public static boolean kindOn(String id) {
  return kind(id) != null && !listed(KINDS_OFF, id);
}""")
M(cfgc, r"""
public static double factor(int rarity) {
  if (rarity == 1) return F1;
  if (rarity == 2) return F2;
  if (rarity == 3) return F3;
  if (rarity == 4) return F4;
  if (rarity == 5) return F5;
  if (rarity == 6) return F6;
  return 0.0;
}""")
M(cfgc, r"""
public static String kindList() {
  StringBuilder b = new StringBuilder();
  @PKG@.PetKind[] a = KINDS;
  for (int i = 0; i < a.length; i++) {
    if (i > 0) b.append(", ");
    b.append(a[i].id);
    if (listed(KINDS_OFF, a[i].id)) b.append(" (off)");
  }
  return b.toString();
}""")
# ---- the kit's check= hooks (null = fine, text = refused)
M(cfgc, r"""
public static String entryOf(String key) {
  if (key == null) return "";
  int a = key.indexOf('['), b = key.lastIndexOf(']');
  return a >= 0 && b > a ? key.substring(a + 1, b) : key;
}""")
M(cfgc, r"""
public static String checkKind(String key, String value) {
  if (value == null) return null;
  if (value.indexOf('/') >= 0) return "No / in a pet kind line.";
  if (@PKG@.PetKind.parse(entryOf(key), value, "|") == null) return "Use Skill | Start rarity | Stats, e.g. Combat | Rare | str:20,cd:15 (rarity Common..Legendary; stat keys: /petadmin kinds).";
  return null;
}""")
M(cfgc, r"""
public static String checkStarter(String key, String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.equalsIgnoreCase("none")) return null;
  if (kind(v) == null) return "There is no pet kind called " + v + " (see Pet kinds), or type none.";
  return null;
}""")
M(cfgc, r"""
public static String checkList(String key, String value) {
  if (value == null) return null;
  if (value.indexOf('/') >= 0 || value.indexOf('|') >= 0) return "Names separated by commas only (- = none).";
  return null;
}""")
M(cfgc, r"""
public static String checkSkills(String key, String value) {
  if (value == null) return null;
  String[] a = value.split(",");
  for (int i = 0; i < a.length; i++) if (!@PKG@.PetKind.skillOk(a[i])) return "Skill names separated by commas, e.g. Mining,Foraging,Combat.";
  return null;
}""")

# ---------------------------------------------------------------- the config kit (Server Setup > Pets): PetsCfg's fields exist now
kit = CFG.emit(pool, PKG, MOD=MOD, TITLE="Pets", VERSION=VERSION, NODE=NODE, CATS=CFG_CATS, ROWS=CFG_ROWS, FILES=[CFG_FILE], NOTE=CFG_NOTE,
               RELOAD="PetsCfg.reloadAll", KEEP=10, DEFAULTS={"config.properties": DEFAULT_TEXT})

# =====================================================================================================================
# PetMath: the level curve
# =====================================================================================================================
pm = cls("PetMath")
F(pm, "public static final int MAX_LEVEL = 100;")
# XP to go from level L-1 to L: lin (L-1) + cub (L-1)^3, rounded to 10 / 50 / 500 (Pets-Spec 3: 60, 240, 570, ... 45,000)
M(pm, r"""
public static long need(int level) {
  if (level <= 1) return 0L;
  double n = (double) (level - 1);
  double raw = @PKG@.PetsCfg.CURVE_LIN * n + @PKG@.PetsCfg.CURVE_CUB * n * n * n;
  if (Double.isNaN(raw) || raw < 1.0) return 1L;
  long step = raw < 1000.0 ? 10L : (raw < 10000.0 ? 50L : 500L);
  long r = Math.round(raw / (double) step) * step;
  return r < 1L ? 1L : r;
}""")
M(pm, r"""
public static int clampLevel(int l) {
  return l < 1 ? 1 : (l > MAX_LEVEL ? MAX_LEVEL : l);
}""")
M(pm, r"""
public static long total(int level) {
  long t = 0L;
  for (int l = 2; l <= clampLevel(level); l++) t = t + need(l);
  return t;
}""")

# =====================================================================================================================
# PetRec: one profile's pet record (all lines of its file; every access synchronized on the record)
# =====================================================================================================================
rec = cls("PetRec")
for _f in ("String key", "java.util.Properties p", "boolean bad", "String why", "boolean dirty", "long mods", "long snapMods",
           "java.util.HashMap frac", "Object io"):
    F(rec, "public %s;" % _f)
C(rec, "public PetRec(String key) { this.key = key; this.p = new java.util.Properties(); this.why = \"\"; this.frac = new java.util.HashMap(); this.io = new Object(); }")
M(rec, "public synchronized void touch() { this.mods = this.mods + 1L; this.dirty = true; }")
M(rec, "public synchronized String get(String k) { return this.p.getProperty(k); }")
M(rec, r"""
public synchronized void set(String k, String v) {
  if (v == null) this.p.remove(k); else this.p.setProperty(k, v);
  touch();
}""")
M(rec, r"""
public synchronized long lv(String k, long d) {
  String s = this.p.getProperty(k);
  if (s == null) return d;
  try { return Long.parseLong(s.trim()); } catch (Throwable t) { return d; }
}""")
M(rec, r"""
public synchronized String[] ids() {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.Iterator it = this.p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("pet.") && k.endsWith(".kind") && k.length() > 9) out.add(k.substring(4, k.length() - 5));
  }
  java.util.Collections.sort(out);
  String[] a = new String[out.size()];
  for (int i = 0; i < a.length; i++) a[i] = (String) out.get(i);
  return a;
}""")
M(rec, "public synchronized boolean has(String id) { return id != null && id.length() > 0 && this.p.getProperty(\"pet.\" + id + \".kind\") != null; }")
M(rec, "public synchronized int count() { return ids().length; }")
M(rec, "public synchronized String kindOf(String id) { String s = this.p.getProperty(\"pet.\" + id + \".kind\"); return s == null ? \"\" : s.trim(); }")
M(rec, r"""
public synchronized int rarityOf(String id) {
  long r = lv("pet." + id + ".rarity", 1L);
  return r < 1L ? 1 : (r > 6L ? 6 : (int) r);
}""")
M(rec, "public synchronized int levelOf(String id) { return @PKG@.PetMath.clampLevel((int) lv(\"pet.\" + id + \".level\", 1L)); }")
M(rec, r"""
public synchronized long xpOf(String id) {
  long x = lv("pet." + id + ".xp", 0L);
  return x < 0L ? 0L : x;
}""")
# the pet id in a slot ("" = empty or it points at a pet this file does not hold)
M(rec, r"""
public synchronized String active(int slot) {
  String v = this.p.getProperty("active." + slot, "").trim();
  return has(v) ? v : "";
}""")
M(rec, r"""
public synchronized int slotOf(String id) {
  if (id == null || id.length() == 0) return 0;
  if (id.equals(active(1))) return 1;
  if (id.equals(active(2))) return 2;
  return 0;
}""")
M(rec, "public synchronized boolean unlocked() { String s = this.p.getProperty(\"slot2.unlocked\"); return s != null && s.trim().equalsIgnoreCase(\"true\"); }")
M(rec, r"""
public synchronized void addAlbum(String kind) {
  String a = this.p.getProperty("album", "").trim();
  String[] x = a.length() == 0 ? new String[0] : a.split(",");
  for (int i = 0; i < x.length; i++) if (x[i].trim().equalsIgnoreCase(kind)) return;
  this.p.setProperty("album", a.length() == 0 ? kind : a + "," + kind);
  touch();
}""")
M(rec, r"""
public synchronized void create(String id, String kind, int rarity, int level, long xp, String src, long now) {
  String k = "pet." + id + ".";
  this.p.setProperty(k + "kind", kind);
  this.p.setProperty(k + "rarity", String.valueOf(rarity));
  this.p.setProperty(k + "level", String.valueOf(@PKG@.PetMath.clampLevel(level)));
  this.p.setProperty(k + "xp", String.valueOf(xp < 0L ? 0L : xp));
  this.p.setProperty(k + "skin", @PKG@.PetKind.lookup(@PKG@.PetKind.MODEL_IDS, kind, kind));
  this.p.setProperty(k + "got", String.valueOf(now));
  this.p.setProperty(k + "src", src == null ? "" : src);
  if (this.p.getProperty("v") == null) this.p.setProperty("v", "1");
  if (this.p.getProperty("cmd") == null) this.p.setProperty("cmd", "follow");
  if (this.p.getProperty("shown.1") == null) this.p.setProperty("shown.1", "true");
  addAlbum(kind);
  touch();
}""")
# take a pet out of the file: its lines (for the ledger / quarantine) and every slot that held it
M(rec, r"""
public synchronized java.util.Properties remove(String id) {
  java.util.Properties out = new java.util.Properties();
  if (id == null || id.length() == 0) return out;
  String pre = "pet." + id + ".";
  java.util.ArrayList ks = new java.util.ArrayList(this.p.stringPropertyNames());
  for (int i = 0; i < ks.size(); i++) {
    String k = (String) ks.get(i);
    if (!k.startsWith(pre)) continue;
    out.setProperty(k, this.p.getProperty(k));
    this.p.remove(k);
  }
  if (id.equals(this.p.getProperty("active.1", "").trim())) this.p.setProperty("active.1", "");
  if (id.equals(this.p.getProperty("active.2", "").trim())) this.p.setProperty("active.2", "");
  this.frac.remove(id);
  touch();
  return out;
}""")
# XP into one pet: the whole part now, the fraction kept in memory; returns the levels gained (Lv 100 = max, XP stops there)
M(rec, r"""
public synchronized int addXp(String id, double amt) {
  if (!has(id) || !(amt > 0.0) || Double.isInfinite(amt)) return 0;
  String k = "pet." + id + ".";
  int lv = levelOf(id);
  if (lv >= @PKG@.PetMath.MAX_LEVEL) return 0;
  Object fo = this.frac.get(id);
  double fr = (fo instanceof Double ? ((Double) fo).doubleValue() : 0.0) + amt;
  if (fr > 1.0E12) fr = 1.0E12;
  long whole = (long) Math.floor(fr);
  this.frac.put(id, Double.valueOf(fr - (double) whole));
  if (whole <= 0L) return 0;
  long xp = xpOf(id) + whole;
  int start = lv;
  while (lv < @PKG@.PetMath.MAX_LEVEL) {
    long need = @PKG@.PetMath.need(lv + 1);
    if (xp < need) break;
    xp = xp - need;
    lv++;
  }
  if (lv >= @PKG@.PetMath.MAX_LEVEL) xp = 0L;
  this.p.setProperty(k + "level", String.valueOf(lv));
  this.p.setProperty(k + "xp", String.valueOf(xp));
  touch();
  return lv - start;
}""")
M(rec, r"""
public synchronized boolean anyActive() {
  return active(1).length() > 0 || active(2).length() > 0;
}""")
# the file text: seq + 1, v=1, sorted escaped lines (Properties.store to ISO-8859-1 bytes, minus its date comment)
M(rec, r"""
public synchronized byte[] snap() {
  try {
    long seq = lv("seq", 0L) + 1L;
    this.p.setProperty("seq", String.valueOf(seq));
    if (this.p.getProperty("v") == null) this.p.setProperty("v", "1");
    this.snapMods = this.mods;
    java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
    this.p.store(bo, (String) null);
    String s = new String(bo.toByteArray(), "ISO-8859-1");
    String[] ls = s.split("\n");
    java.util.ArrayList keep = new java.util.ArrayList();
    for (int i = 0; i < ls.length; i++) {
      String l = ls[i];
      if (l.endsWith("\r")) l = l.substring(0, l.length() - 1);
      if (l.length() == 0 || l.startsWith("#")) continue;
      keep.add(l);
    }
    java.util.Collections.sort(keep);
    StringBuilder b = new StringBuilder();
    b.append("# SkyyPets pet records of one profile (" + this.key + "). Do not edit while this player is online; seq goes up on every save.\n");
    for (int i = 0; i < keep.size(); i++) { b.append((String) keep.get(i)); b.append('\n'); }
    return b.toString().getBytes("ISO-8859-1");
  } catch (Throwable t) {
    @PKG@.PetsLog.warn("could not prepare the pet file of " + this.key + ": " + t);
    return null;
  }
}""")
M(rec, "public synchronized void saved() { if (this.mods == this.snapMods) this.dirty = false; }")
M(rec, "public synchronized boolean isDirty() { return this.dirty; }")

# =====================================================================================================================
# PetStore: files, the record cache (pkey -> PetRec), the global id index, the ledger, the startup check
# =====================================================================================================================
st = cls("PetStore")
F(st, "public static java.nio.file.Path ROOT;")
F(st, "public static java.nio.file.Path DIR;")
F(st, "public static final java.util.concurrent.ConcurrentHashMap REC = new java.util.concurrent.ConcurrentHashMap();")
F(st, "public static final java.util.concurrent.ConcurrentHashMap INDEX = new java.util.concurrent.ConcurrentHashMap();")
F(st, "public static final java.util.concurrent.ConcurrentHashMap BAD = new java.util.concurrent.ConcurrentHashMap();")
F(st, "public static final java.util.concurrent.ConcurrentHashMap KEYOF = new java.util.concurrent.ConcurrentHashMap();")
F(st, "public static final java.security.SecureRandom RND = new java.security.SecureRandom();")
F(st, "public static volatile long WRITES = 0L;")
F(st, "public static volatile long FAILS = 0L;")
F(st, "public static volatile int QUARANTINED = 0;")
# fixer 2: true while scanAll runs (its own index pass); afterwards every file read later by get() adds its pet ids to INDEX
F(st, "public static volatile boolean SCANNING = false;")
F(st, "public static volatile int LATE_CLASH = 0;")
F(st, "public static final Object LEDGER_LOCK = new Object();")
# PROFILES-CONTRACT helper (profile 1 / no SkyyProfiles = the UUID)
M(st, r"""
public static String pkey(java.util.UUID u) {
  if (u == null) return "";
  try {
    Object f = @PKG@.PetsLog.bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
M(st, r"""
public static boolean keyOk(String key) {
  if (key == null || key.length() == 0 || key.length() > 80) return false;
  for (int i = 0; i < key.length(); i++) {
    char c = key.charAt(i);
    if (!(c >= 'a' && c <= 'z') && !(c >= 'A' && c <= 'Z') && !(c >= '0' && c <= '9') && c != '-' && c != '_') return false;
  }
  return true;
}""")
M(st, r"""
public static java.nio.file.Path file(String key) {
  if (DIR == null || !keyOk(key)) return null;
  return DIR.resolve(key + ".properties");
}""")
# tmp + fsync + atomic rename (5 tries, 20 ms apart on a Windows FileSystemException); false = not written (the old file stays)
M(st, r"""
public static boolean writeAtomic(java.nio.file.Path f, byte[] b) {
  if (f == null || b == null) return false;
  java.nio.file.Path tmp = f.resolveSibling(f.getFileName().toString() + ".tmp");
  java.io.FileOutputStream fo = null;
  try {
    java.nio.file.Path dir = f.getParent();
    if (dir != null) java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
    fo = new java.io.FileOutputStream(tmp.toFile());
    fo.write(b);
    fo.flush();
    fo.getFD().sync();
    fo.close();
    fo = null;
    for (int i = 0; i < 5; i++) {
      try {
        java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING });
        WRITES = WRITES + 1L;
        return true;
      } catch (java.nio.file.FileSystemException e) {
        if (i == 4) throw e;
        try { Thread.sleep(20L); } catch (Throwable z) { }
      }
    }
    return false;
  } catch (Throwable t) {
    FAILS = FAILS + 1L;
    @PKG@.PetsLog.warn("could not write " + f + ": " + t + " - the old file is kept");
    try { if (fo != null) fo.close(); } catch (Throwable t2) { }
    try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable t3) { }
    return false;
  }
}""")
# read one profile file: a fresh empty record when there is none; bad = never written (I/O, bad escape, a folder, a newer format)
M(st, r"""
public static @PKG@.PetRec load(String key) {
  @PKG@.PetRec r = new @PKG@.PetRec(key);
  java.nio.file.Path f = file(key);
  if (f == null) { r.bad = true; r.why = "no pet folder or a bad profile key"; return r; }
  if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return r;
  try {
    byte[] b = java.nio.file.Files.readAllBytes(f);
    java.util.Properties p = new java.util.Properties();
    p.load(new java.io.ByteArrayInputStream(b));
    String v = p.getProperty("v");
    if (v == null) { r.bad = true; r.why = b.length == 0 ? "the file is empty (0 bytes)" : "the file has no v=1 line (cut off or hand-edited?)"; }
    else if (!v.trim().equals("1")) { r.bad = true; r.why = "written by a newer SkyyPets (format " + v.trim() + ")"; }
    else r.p = p;
  } catch (Throwable t) { r.bad = true; r.why = t.toString(); }
  if (r.bad) {
    BAD.put(key, r.why);
    @PKG@.PetsLog.warnOnce("bad:" + key + ":" + r.why, "the pet file " + f.getFileName() + " could not be read (" + r.why + ") - that profile gets no pet buffs and nothing is written until it is fixed");
  } else BAD.remove(key);
  return r;
}""")
# fixer 2: a file read after the startup scan (it was unreadable then and fixed since) puts its pet ids into INDEX, so restore / give
# see them; an id another profile already holds is logged (both copies kept - the startup check settles it at the next start)
M(st, r"""
public static void indexLate(@PKG@.PetRec r) {
  String[] ids = r.ids();
  for (int k = 0; k < ids.length; k++) {
    Object prev = INDEX.putIfAbsent(ids[k], r.key);
    if (prev == null || prev.equals(r.key)) continue;
    LATE_CLASH = LATE_CLASH + 1;
    @PKG@.PetsLog.warnOnce("late:" + ids[k] + ":" + r.key, "pet " + ids[k] + " is in " + prev + " AND in " + r.key + " (read after the startup check) - both kept for now; the startup check at the next server start keeps one and quarantines the other");
  }
}""")
M(st, r"""
public static synchronized @PKG@.PetRec get(String key) {
  Object o = REC.get(key);
  if (o != null) return (@PKG@.PetRec) o;
  @PKG@.PetRec r = load(key);
  if (!r.bad && !SCANNING) indexLate(r);
  REC.put(key, r);
  return r;
}""")
M(st, r"""
public static boolean write(@PKG@.PetRec r) {
  if (r == null || r.bad || DIR == null) return false;
  byte[] b = r.snap();
  if (b == null) return false;
  if (!writeAtomic(file(r.key), b)) return false;
  r.saved();
  return true;
}""")
M(st, r"""
public static boolean save(@PKG@.PetRec r) {
  if (r == null) return false;
  boolean ok = false;
  synchronized (r.io) { ok = write(r); }
  return ok;
}""")
M(st, r"""
public static int flushDirty() {
  int n = 0;
  Object[] a = REC.values().toArray();
  for (int i = 0; i < a.length; i++) {
    @PKG@.PetRec r = (@PKG@.PetRec) a[i];
    if (r.bad || !r.isDirty()) continue;
    if (save(r)) n++;
  }
  return n;
}""")
# flush + forget a record nobody online uses any more (logout / profile switch)
M(st, r"""
public static void release(String key) {
  if (key == null) return;
  Object o = REC.get(key);
  if (o == null) return;
  @PKG@.PetRec r = (@PKG@.PetRec) o;
  if (!r.bad && r.isDirty()) save(r);
  if (KEYOF.containsValue(key)) return;
  if (!r.isDirty() || r.bad) REC.remove(key, r);
}""")
M(st, r"""
public static String newId() {
  String abc = "0123456789abcdefghijklmnopqrstuvwxyz";
  for (int t = 0; t < 200; t++) {
    StringBuilder b = new StringBuilder();
    for (int i = 0; i < 8; i++) b.append(abc.charAt(RND.nextInt(36)));
    String id = b.toString();
    if (!INDEX.containsKey(id)) return id;
  }
  return null;
}""")
# ---- the ledger: time id kind rarity level xp from to reason by (append-only, one line)
M(st, r"""
public static void appendLedger(String line) {
  if (ROOT == null) return;
  try {
    java.nio.file.Files.createDirectories(ROOT, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Files.write(ROOT.resolve("ledger.log"), (line + "\n").getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE, java.nio.file.StandardOpenOption.APPEND });
  } catch (Throwable t) { @PKG@.PetsLog.warn("could not append to ledger.log: " + t + " - line: " + line); }
}""")
M(st, r"""
public static void ledger(String id, String kind, int rarity, int level, long xp, String from, String to, String reason, String by) {
  String l = System.currentTimeMillis() + "\t" + @PKG@.PetsLog.clean(id) + "\t" + @PKG@.PetsLog.clean(kind) + "\t" + rarity + "\t" + level + "\t" + xp + "\t" + @PKG@.PetsLog.clean(from) + "\t" + @PKG@.PetsLog.clean(to) + "\t" + @PKG@.PetsLog.clean(reason) + "\t" + @PKG@.PetsLog.clean(by);
  synchronized (LEDGER_LOCK) { appendLedger(l); }
}""")
# the newest ledger line of that id (split on tabs) or null
M(st, r"""
public static String[] ledgerFind(String id) {
  if (ROOT == null || id == null) return null;
  try {
    java.nio.file.Path f = ROOT.resolve("ledger.log");
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return null;
    java.util.List ls = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = ls.size() - 1; i >= 0; i--) {
      String[] p = ((String) ls.get(i)).split("\t", -1);
      if (p.length >= 10 && p[1].equals(id) && p[2].length() > 0 && !p[2].equals("-")) return p;
    }
  } catch (Throwable t) { @PKG@.PetsLog.warn("could not read ledger.log: " + t); }
  return null;
}""")
# ---- the startup check: every file into the id index; an id in two files stays in the higher seq file, the other copy goes to quarantine
M(st, r"""
public static void quarantine(String id, String keep, String lose) {
  @PKG@.PetRec lr = get(lose);
  if (lr.bad || !lr.has(id)) return;
  String kind = lr.kindOf(id);
  int rar = lr.rarityOf(id), lvl = lr.levelOf(id);
  long xp = lr.xpOf(id);
  java.util.Properties gone = lr.remove(id);
  long now = System.currentTimeMillis();
  StringBuilder b = new StringBuilder();
  b.append("# SkyyPets quarantine: pet " + id + " was also in " + keep + " (kept there, higher seq). This copy came from " + lose + ".\n");
  java.util.ArrayList ks = new java.util.ArrayList(gone.stringPropertyNames());
  java.util.Collections.sort(ks);
  for (int i = 0; i < ks.size(); i++) { String k = (String) ks.get(i); b.append(k + "=" + gone.getProperty(k) + "\n"); }
  boolean q = false;
  try { q = writeAtomic(ROOT.resolve("quarantine").resolve(id + "-" + lose + "-" + now + ".properties"), b.toString().getBytes("ISO-8859-1")); } catch (Throwable t) { q = false; }
  if (!q) { @PKG@.PetsLog.warn("pet " + id + " is in " + keep + " AND " + lose + " but the quarantine copy could not be written - both kept for now"); REC.remove(lose); return; }
  if (!save(lr)) { @PKG@.PetsLog.warn("pet " + id + ": the quarantine copy is written but " + lose + " could not be saved - both kept for now"); REC.remove(lose); return; }
  ledger(id, kind, rar, lvl, xp, lose, "quarantine", "duplicate (kept in " + keep + ")", "startup");
  QUARANTINED = QUARANTINED + 1;
  @PKG@.PetsLog.warn("pet " + id + " (" + kind + ") was in two files: kept in " + keep + ", the copy in " + lose + " moved to quarantine/");
}""")
M(st, r"""
public static int[] scanAll() {
  SCANNING = true;
  INDEX.clear();
  BAD.clear();
  REC.clear();
  int files = 0, pets = 0, bad = 0, dup = 0;
  if (DIR == null || !java.nio.file.Files.isDirectory(DIR, new java.nio.file.LinkOption[0])) { SCANNING = false; return new int[] { 0, 0, 0, 0 }; }
  java.util.ArrayList names = new java.util.ArrayList();
  java.nio.file.DirectoryStream ds = null;
  try {
    ds = java.nio.file.Files.newDirectoryStream(DIR, "*.properties");
    java.util.Iterator it = ds.iterator();
    while (it.hasNext()) names.add(((java.nio.file.Path) it.next()).getFileName().toString());
  } catch (Throwable t) { @PKG@.PetsLog.warn("could not list " + DIR + ": " + t); }
  finally { try { if (ds != null) ds.close(); } catch (Throwable t2) { } }
  java.util.Collections.sort(names);
  java.util.HashMap seqs = new java.util.HashMap();
  java.util.ArrayList dups = new java.util.ArrayList();
  for (int i = 0; i < names.size(); i++) {
    String n = (String) names.get(i);
    String key = n.substring(0, n.length() - ".properties".length());
    if (!keyOk(key)) continue;
    files++;
    @PKG@.PetRec r = load(key);
    if (r.bad) { bad++; continue; }
    seqs.put(key, Long.valueOf(r.lv("seq", 0L)));
    String[] ids = r.ids();
    for (int k = 0; k < ids.length; k++) {
      Object prev = INDEX.putIfAbsent(ids[k], key);
      if (prev == null) { pets++; continue; }
      dups.add(new String[] { ids[k], (String) prev, key });
    }
  }
  for (int i = 0; i < dups.size(); i++) {
    String[] d = (String[]) dups.get(i);
    long sa = seqs.get(d[1]) == null ? 0L : ((Long) seqs.get(d[1])).longValue();
    long sb = seqs.get(d[2]) == null ? 0L : ((Long) seqs.get(d[2])).longValue();
    String keep = sb > sa ? d[2] : d[1];
    String lose = keep.equals(d[1]) ? d[2] : d[1];
    INDEX.put(d[0], keep);
    quarantine(d[0], keep, lose);
    dup++;
  }
  REC.clear();
  SCANNING = false;
  return new int[] { files, pets, bad, dup };
}""")

# =====================================================================================================================
# PetBuff: the slotted pets' totals -> skyypet_* max-stat modifiers, skill:bonus "pets", move "pets", pets:stats:<uuid>
# =====================================================================================================================
bf = cls("PetBuff")
F(bf, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(bf, "public static final String SOURCE = \"pets\";")
F(bf, "public static final int N = %d;" % len(STAT_KEYS))
M(bf, r"""
public static boolean slot2Open(@PKG@.PetRec r) {
  if (r == null) return false;
  String m = @PKG@.PetsCfg.SLOT2_MODE;
  if ("always".equals(m)) return true;
  if ("off".equals(m)) return false;
  return r.unlocked();
}""")
M(bf, r"""
public static String lockedWhy() {
  return "off".equals(@PKG@.PetsCfg.SLOT2_MODE) ? "The summon slot is closed on this server." : "It opens with the Zone 2 Stable quest.";
}""")
# one pet's contribution to the totals at strength `pct` percent
M(bf, r"""
public static void addPet(double[] t, @PKG@.PetRec r, String id, double pct) {
  if (id == null || id.length() == 0 || !(pct > 0.0)) return;
  String k = r.kindOf(id);
  if (!@PKG@.PetsCfg.kindOn(k)) return;
  @PKG@.PetKind pk = @PKG@.PetsCfg.kind(k);
  double f = @PKG@.PetsCfg.factor(r.rarityOf(id)) * (double) r.levelOf(id) / 100.0 * pct / 100.0;
  for (int i = 0; i < pk.keys.length; i++) {
    int x = @PKG@.PetKind.statIndex(pk.keys[i]);
    if (x >= 0) t[x] = t[x] + pk.vals[i] * f;
  }
}""")
M(bf, r"""
public static double[] compute(@PKG@.PetRec r, String world) {
  double[] t = new double[N];
  if (!@PKG@.PetsCfg.ON || r == null || r.bad) return t;
  if (world != null && @PKG@.PetsCfg.listed(@PKG@.PetsCfg.NOBUFF, world)) return t;
  addPet(t, r, r.active(1), 100.0);
  if (slot2Open(r)) addPet(t, r, r.active(2), (double) @PKG@.PetsCfg.SLOT2_PCT);
  for (int i = 0; i < N; i++) {
    String k = @PKG@.PetKind.STAT_KEYS[i];
    if (k.startsWith("fortune.") && t[i] > @PKG@.PetsCfg.FORT_CAP) t[i] = @PKG@.PetsCfg.FORT_CAP;
    if (k.startsWith("swing.") && t[i] > @PKG@.PetsCfg.SWING_CAP) t[i] = @PKG@.PetsCfg.SWING_CAP;
  }
  return t;
}""")
M(bf, r"""
public static double get(double[] t, String key) {
  int i = @PKG@.PetKind.statIndex(key);
  return t == null || i < 0 ? 0.0 : t[i];
}""")
# fixer 2: under 1 two decimals (a Common Lv 1 Rabbit = "+0.03 Farming Fortune", not "nothing"); 1 and up one decimal as before
M(bf, r"""
public static String fmt(double d) {
  if (Math.abs(d) >= 0.95) return @PKG@.PetsLog.num(d);
  long t = Math.round(Math.abs(d) * 100.0);
  String s = t >= 10L ? (t % 10L == 0L ? "0." + (t / 10L) : "0." + t) : "0.0" + t;
  return (d < 0.0 ? "-" : "") + s;
}""")
# "+20 Strength, +15 Crit Damage" ("" = nothing)
M(bf, r"""
public static String text(double[] t) {
  StringBuilder b = new StringBuilder();
  for (int i = 0; t != null && i < t.length; i++) {
    if (Math.abs(t[i]) < 0.005) continue;
    if (b.length() > 0) b.append(", ");
    b.append(t[i] > 0.0 ? "+" : "").append(fmt(t[i])).append(' ').append(@PKG@.PetKind.STAT_NAMES[i]);
  }
  return b.toString();
}""")
# one pet's own buffs at a slot strength (for the details view)
M(bf, r"""
public static String petText(@PKG@.PetRec r, String id, double pct) {
  double[] t = new double[N];
  addPet(t, r, id, pct);
  String s = text(t);
  return s.length() == 0 ? "nothing" : s;
}""")
M(bf, r"""
public static java.util.Map sources(String key, boolean create) {
  java.util.Map b = @PKG@.PetsLog.bridge();
  Object o = b.get(key);
  if (o instanceof java.util.Map) return (java.util.Map) o;
  if (!create) return null;
  java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
  Object prev = b.putIfAbsent(key, n);
  if (prev instanceof java.util.Map) return (java.util.Map) prev;
  return n;
}""")
# fixer 2: are the entries publish() posted for these totals still on the bridge? (another mod may replace a skill:bonus / move map;
# SkyyTrees postBonus pattern "so a replaced map is re-filled")
M(bf, r"""
public static boolean intact(java.util.UUID u, double[] t) {
  String us = u.toString();
  java.util.Map br = @PKG@.PetsLog.bridge();
  boolean gear = false, bon = false, mv = false;
  for (int i = 0; i < t.length; i++) {
    if (Math.abs(t[i]) < 1.0E-9) continue;
    String how = @PKG@.PetKind.STAT_HOW[i];
    if (how.equals("gear") || how.equals("swing")) gear = true;
    else if (how.equals("dd") || how.equals("xp")) bon = true;
    else if (how.equals("move")) mv = true;
  }
  if (gear && br.get("pets:stats:" + us) == null) return false;
  if (bon) { java.util.Map m = sources("skill:bonus:" + us, false); if (m == null || m.get(SOURCE) == null) return false; }
  if (mv) { java.util.Map m = sources("move:" + us, false); if (m == null || m.get(SOURCE) == null) return false; }
  return true;
}""")
# deliver the totals of one player (UUID keys = the ACTIVE profile); only touches the bridge when something changed (or went missing)
M(bf, r"""
public static void publish(java.util.UUID u, double[] t) {
  if (u == null || t == null) return;
  StringBuilder sig = new StringBuilder();
  for (int i = 0; i < t.length; i++) sig.append(Math.round(t[i] * 10000.0)).append(';');
  String s = sig.toString();
  Object last = LAST.put(u, s);
  if (s.equals(last) && intact(u, t)) return;
  java.util.Map br = @PKG@.PetsLog.bridge();
  String us = u.toString();
  java.util.HashMap gear = new java.util.HashMap();
  java.util.HashMap bon = new java.util.HashMap();
  for (int i = 0; i < t.length; i++) {
    if (Math.abs(t[i]) < 1.0E-9) continue;
    String k = @PKG@.PetKind.STAT_KEYS[i];
    String how = @PKG@.PetKind.STAT_HOW[i];
    if (how.equals("gear") || how.equals("swing")) gear.put(k, Double.valueOf(t[i]));
    else if (how.equals("dd")) bon.put("dd." + k.substring(8), Double.valueOf(t[i] / 100.0));
    else if (how.equals("xp")) bon.put("xp." + k.substring(7), Double.valueOf(t[i] / 100.0));
  }
  if (gear.isEmpty()) br.remove("pets:stats:" + us); else br.put("pets:stats:" + us, java.util.Collections.unmodifiableMap(gear));
  if (bon.isEmpty()) { java.util.Map m = sources("skill:bonus:" + us, false); if (m != null) m.remove(SOURCE); }
  else sources("skill:bonus:" + us, true).put(SOURCE, java.util.Collections.unmodifiableMap(bon));
  float sp = (float) (get(t, "speed") / 100.0);
  if (sp == 0.0f) { java.util.Map m = sources("move:" + us, false); if (m != null) m.remove(SOURCE); }
  else {
    java.util.HashMap e = new java.util.HashMap();
    e.put("layer", "pct");
    e.put("speed", Float.valueOf(sp));
    e.put("jump", Float.valueOf(0.0f));
    e.put("fallDamage", Float.valueOf(0.0f));
    sources("move:" + us, true).put(SOURCE, java.util.Collections.unmodifiableMap(e));
  }
}""")
M(bf, r"""
public static void clear(java.util.UUID u) {
  if (u == null) return;
  LAST.remove(u);
  String us = u.toString();
  java.util.Map br = @PKG@.PetsLog.bridge();
  br.remove("pets:stats:" + us);
  java.util.Map m = sources("skill:bonus:" + us, false);
  if (m != null) m.remove(SOURCE);
  java.util.Map v = sources("move:" + us, false);
  if (v != null) v.remove(SOURCE);
}""")
# fixer 2 (plugin shutdown / reload): take every player's "pets" entries off the shared bridge (it outlives the plugin)
M(bf, r"""
public static int clearAll() {
  java.util.HashSet all = new java.util.HashSet();
  all.addAll(LAST.keySet());
  all.addAll(@PKG@.PetStore.KEYOF.keySet());
  Object[] us = all.toArray();
  for (int i = 0; i < us.length; i++) if (us[i] instanceof java.util.UUID) clear((java.util.UUID) us[i]);
  return us.length;
}""")
# set (amt != 0) or remove (amt == 0) our MAX modifier on one stat (SkyySkills Perks.mod / SkyyAccessories AccEffects.mod pattern)
M(bf, r"""
public static void mod(@ESM@ m, int idx, String key, float amt) {
  if (m == null || idx < 0) return;
  try {
    if (m.get(idx) == null) return;
    @MODF@ cur = m.getModifier(idx, key);
    if (amt == 0.0f) { if (cur != null) m.removeModifier(idx, key); return; }
    @SMO@ want = new @SMO@(@MTG@.MAX, @CAL@.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, key, want);
  } catch (Throwable t) { }
}""")
M(bf, r"""
public static float r2(double d) {
  return (float) (Math.round(d * 100.0) / 100.0);
}""")
M(bf, r"""
public static void stats(@ESM@ m, double[] t) {
  if (m == null || t == null) return;
  mod(m, @DST@.getHealth(), "skyypet_health", r2(get(t, "health")));
  mod(m, @DST@.getStamina(), "skyypet_stamina", r2(get(t, "stamina")));
  mod(m, @DST@.getMana(), "skyypet_mana", r2(get(t, "mana")));
}""")

# =====================================================================================================================
# PetXp: pets:fn:onxp + the fallback poll of skill:fn:xp
# =====================================================================================================================
xp = cls("PetXp")
F(xp, "public static volatile boolean HOOKED = false;")
F(xp, "public static final java.util.concurrent.ConcurrentHashMap BASE = new java.util.concurrent.ConcurrentHashMap();")
F(xp, "public static final java.util.concurrent.atomic.AtomicLong GIVEN = new java.util.concurrent.atomic.AtomicLong();")
F(xp, "public static final java.util.concurrent.atomic.AtomicLong POLLS = new java.util.concurrent.atomic.AtomicLong();")
F(xp, "public static final long JUMP = 1000000L;")
F(xp, "public static final java.util.concurrent.atomic.AtomicLong SKIPPED = new java.util.concurrent.atomic.AtomicLong();")
# the core: XP `amount` earned in `skill` -> every slotted pet of the ACTIVE profile (records already loaded only)
M(xp, r"""
public static int give(java.util.UUID u, String skill, long amount) {
  if (!@PKG@.PetsCfg.ON || u == null || skill == null || amount <= 0L) return 0;
  Object o = @PKG@.PetStore.REC.get(@PKG@.PetStore.pkey(u));
  if (o == null) return 0;
  @PKG@.PetRec r = (@PKG@.PetRec) o;
  if (r.bad) return 0;
  int n = 0;
  for (int s = 1; s <= 2; s++) {
    if (s == 2 && !@PKG@.PetBuff.slot2Open(r)) continue;
    String id = r.active(s);
    if (id.length() == 0) continue;
    String k = r.kindOf(id);
    @PKG@.PetKind pk = @PKG@.PetsCfg.kind(k);
    if (pk == null || !@PKG@.PetsCfg.kindOn(k)) continue;
    int pct = @PKG@.PetKind.skillMatch(pk.skill, skill) ? @PKG@.PetsCfg.XP_OWN : @PKG@.PetsCfg.XP_OTHER;
    if (pct <= 0) continue;
    int up = r.addXp(id, (double) amount * (double) pct / 100.0);
    n++;
    if (up > 0) @PKG@.PetsEng.tell(u, "[Pets] Your " + @PKG@.PetKind.rarityName(r.rarityOf(id)) + " " + pk.name + " reached Lv " + r.levelOf(id) + "!", "@COLGLD@");
  }
  if (n > 0) GIVEN.addAndGet(amount);
  return n;
}""")
# the fallback: growth of skill:fn:xp since the last read (first read / profile switch = baseline; a drop or a huge jump re-baselines)
M(xp, r"""
public static int pollOne(java.util.UUID u, java.util.function.Function f, String[] skills) {
  String key = (String) @PKG@.PetStore.KEYOF.get(u);
  if (key == null) return 0;
  if (!key.equals(@PKG@.PetStore.pkey(u))) { SKIPPED.incrementAndGet(); return 0; }
  int n = 0;
  for (int i = 0; i < skills.length; i++) {
    String sk = skills[i].trim();
    if (sk.length() == 0 || sk.equalsIgnoreCase("Combat")) continue;
    long v = -1L;
    try { Object o = f.apply(new Object[] { u, sk }); if (o instanceof Number) v = ((Number) o).longValue(); } catch (Throwable t) { v = -1L; }
    if (v <= 0L) continue;
    String bk = u.toString() + "|" + key + "|" + sk;
    Object prev = BASE.put(bk, Long.valueOf(v));
    if (prev == null) continue;
    long d = v - ((Long) prev).longValue();
    if (d <= 0L || d > JUMP) continue;
    if (give(u, sk, d) > 0) n++;
  }
  return n;
}""")
M(xp, r"""
public static int poll() {
  if (!@PKG@.PetsCfg.ON || !@PKG@.PetsCfg.FALLBACK || HOOKED) return 0;
  java.util.function.Function f = @PKG@.PetsLog.fn("skill:fn:xp");
  if (f == null) return 0;
  POLLS.incrementAndGet();
  String[] skills = @PKG@.PetsCfg.POLL_SKILLS.split(",");
  java.util.UUID[] on = @PKG@.PetsEng.online();
  int n = 0;
  for (int i = 0; i < on.length; i++) n = n + pollOne(on[i], f, skills);
  if (BASE.size() > 20000) BASE.clear();
  return n;
}""")
M(xp, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String p = u.toString() + "|";
  Object[] ks = BASE.keySet().toArray();
  for (int i = 0; i < ks.length; i++) if (((String) ks[i]).startsWith(p)) BASE.remove(ks[i]);
}""")
xfn = cls("PetXpFn")
xfn.addInterface(pool.get("java.util.function.Function"))
C(xfn, "public PetXpFn() { }")
M(xfn, r"""
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || a[1] == null || !(a[2] instanceof Number)) return Boolean.FALSE;
    String src = a.length > 3 && a[3] != null ? String.valueOf(a[3]) : null;
    if (src != null && src.equalsIgnoreCase("SkyySkills") && !@PKG@.PetXp.HOOKED) {
      @PKG@.PetXp.HOOKED = true;
      @PKG@.PetsLog.info("SkyySkills reports XP to pets itself now - the skill:fn:xp fallback poll is off");
    }
    long n = ((Number) a[2]).longValue();
    return @PKG@.PetXp.give((java.util.UUID) a[0], String.valueOf(a[1]), n) > 0 ? Boolean.TRUE : Boolean.FALSE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")

# =====================================================================================================================
# PetOps: slots, starter, admin operations (each returns a "+"/"-"/"=" marked line)
# =====================================================================================================================
ops = cls("PetOps")
M(ops, r"""
public static String petName(@PKG@.PetRec r, String id) {
  String k = r.kindOf(id);
  @PKG@.PetKind pk = @PKG@.PetsCfg.kind(k);
  return @PKG@.PetKind.rarityName(r.rarityOf(id)) + " " + (pk == null ? @PKG@.PetKind.display(k) : pk.name);
}""")
M(ops, r"""
public static String slotName(int s) {
  return s == 1 ? "pet slot" : (s == 2 ? "summon slot" : "no slot");
}""")
# move a pet into slot 1 or 2 (from the other slot too); saved at once + a ledger line
M(ops, r"""
public static String toSlot(java.util.UUID u, String id, int slot, String by) {
  if (!@PKG@.PetsCfg.ON) return "-Pets are switched off on this server.";
  @PKG@.PetRec r = @PKG@.PetStore.get(@PKG@.PetStore.pkey(u));
  if (r.bad) return "-Your pet file could not be read - an admin has been told. Nothing was changed.";
  if (!r.has(id)) return "-That pet is not yours any more.";
  if (slot == 2 && !@PKG@.PetBuff.slot2Open(r)) return "-The summon slot is locked. " + @PKG@.PetBuff.lockedWhy();
  if (slot != 1 && slot != 2) return "-There is no such slot.";
  int was = r.slotOf(id);
  if (was == slot) return "=That pet is already in your " + slotName(slot) + ".";
  r.set("active." + slot, id);
  if (was != 0) r.set("active." + was, "");
  if (!@PKG@.PetStore.save(r)) return "-Your pets could not be saved - try again in a moment.";
  @PKG@.PetStore.ledger(id, r.kindOf(id), r.rarityOf(id), r.levelOf(id), r.xpOf(id), slotName(was), slotName(slot), "slot", by);
  return "+" + petName(r, id) + " is now in your " + slotName(slot) + (slot == 2 ? " (" + @PKG@.PetsCfg.SLOT2_PCT + "% buffs)." : ".");
}""")
M(ops, r"""
public static String takeOut(java.util.UUID u, String id, String by) {
  if (!@PKG@.PetsCfg.ON) return "-Pets are switched off on this server.";
  @PKG@.PetRec r = @PKG@.PetStore.get(@PKG@.PetStore.pkey(u));
  if (r.bad) return "-Your pet file could not be read - an admin has been told. Nothing was changed.";
  if (!r.has(id)) return "-That pet is not yours any more.";
  int was = r.slotOf(id);
  if (was == 0) return "=That pet is not in a slot.";
  r.set("active." + was, "");
  if (!@PKG@.PetStore.save(r)) return "-Your pets could not be saved - try again in a moment.";
  @PKG@.PetStore.ledger(id, r.kindOf(id), r.rarityOf(id), r.levelOf(id), r.xpOf(id), slotName(was), "no slot", "slot", by);
  return "+" + petName(r, id) + " left your " + slotName(was) + ".";
}""")
# a new pet into a profile (give / starter / restore); null id = a fresh one. Returns the id or a "-" reason.
M(ops, r"""
public static String create(@PKG@.PetRec r, String id, String kind, int rarity, int level, long xpv, String src, String by, boolean cap) {
  if (r == null || r.bad) return "-That pet file could not be read - nothing was changed.";
  if (cap && r.count() >= @PKG@.PetsCfg.OWNED_MAX) return "-That collection is full (" + @PKG@.PetsCfg.OWNED_MAX + " pets).";
  String nid = id == null ? @PKG@.PetStore.newId() : id;
  if (nid == null) return "-No free pet id - try again.";
  if (@PKG@.PetStore.INDEX.putIfAbsent(nid, r.key) != null) return "-Pet " + nid + " already belongs to someone.";
  r.create(nid, kind, rarity, level, xpv, src, System.currentTimeMillis());
  if (r.active(1).length() == 0) r.set("active.1", nid);
  if (!@PKG@.PetStore.save(r)) {
    r.remove(nid);
    @PKG@.PetStore.INDEX.remove(nid, r.key);
    return "-The pet file could not be saved - nothing was given.";
  }
  @PKG@.PetStore.ledger(nid, kind, rarity, r.levelOf(nid), r.xpOf(nid), "", r.key, src, by);
  return nid;
}""")
# the starter pet: once per profile (marker starter=<ms>), only when part on + the kind exists
M(ops, r"""
public static boolean starter(java.util.UUID u, @PKG@.PetRec r) {
  if (!@PKG@.PetsCfg.ON || r == null || r.bad) return false;
  if (r.get("starter") != null) return false;
  String k = @PKG@.PetsCfg.STARTER == null ? "none" : @PKG@.PetsCfg.STARTER.trim();
  if (k.equalsIgnoreCase("none") || !@PKG@.PetsCfg.kindOn(k)) return false;
  @PKG@.PetKind pk = @PKG@.PetsCfg.kind(k);
  r.set("starter", String.valueOf(System.currentTimeMillis()));
  String res = create(r, null, pk.id, 1, 1, 0L, "starter", "starter", false);
  if (res.startsWith("-")) { r.set("starter", null); @PKG@.PetsLog.warnOnce("starter:" + r.key, "the starter pet of " + r.key + " could not be given: " + res.substring(1)); return false; }
  @PKG@.PetsEng.tell(u, "[Pets] You got your first pet: a Common " + pk.name + "! It is in your pet slot - open /pets to see it.", "@COLGLD@");
  return true;
}""")
M(ops, r"""
public static String line(@PKG@.PetRec r, String id) {
  int s = r.slotOf(id);
  return id + "  " + petName(r, id) + "  Lv " + r.levelOf(id) + " (" + @PKG@.PetsLog.grp(r.xpOf(id)) + " / " + @PKG@.PetsLog.grp(@PKG@.PetMath.need(r.levelOf(id) + 1)) + " XP)" + (s > 0 ? "  [" + slotName(s) + "]" : "");
}""")
# /petadmin <verb> [args]: the target must be online (its active profile)
M(ops, r"""
public static String admin(String by, String verb, String player, String a, String b, String c) {
  String v = verb == null ? "" : verb.trim().toLowerCase();
  if (v.length() == 0 || v.equals("help")) return "=/petadmin give <player> <kind> [rarity] [level] | take <player> <id> | unlock <player> | lock <player> | list <player> | restore <player> <id> | xp <player> <skill> <amount> | kinds";
  if (v.equals("kinds")) {
    StringBuilder sb = new StringBuilder();
    sb.append("Pet kinds: " + @PKG@.PetsCfg.kindList() + "\nRarities: Common, Uncommon, Rare, Epic, Legendary\nStat keys: ");
    for (int i = 0; i < @PKG@.PetKind.STAT_KEYS.length; i++) sb.append(i > 0 ? ", " : "").append(@PKG@.PetKind.STAT_KEYS[i]);
    return "=" + sb.toString();
  }
  if (!v.equals("give") && !v.equals("take") && !v.equals("unlock") && !v.equals("lock") && !v.equals("list") && !v.equals("restore") && !v.equals("xp"))
    return "-Unknown option " + verb + ". /petadmin help";
  if (player == null || player.trim().length() == 0) return "-Which player? /petadmin " + v + " <player> ...";
  java.util.UUID u = @PKG@.PetsEng.byName(player);
  if (u == null) return "-" + player + " is not online (pets live in the active profile of an online player).";
  String nm = @PKG@.PetsEng.nameOf(u);
  @PKG@.PetRec r = @PKG@.PetStore.get(@PKG@.PetStore.pkey(u));
  if (v.equals("list")) {
    if (r.bad) return "-" + nm + "'s pet file (" + r.key + ") could not be read: " + r.why;
    String[] ids = r.ids();
    StringBuilder sb = new StringBuilder();
    sb.append(nm + " (" + r.key + "): " + ids.length + " pets, summon slot " + (@PKG@.PetBuff.slot2Open(r) ? "open" : "locked"));
    for (int i = 0; i < ids.length && i < 40; i++) sb.append("\n").append(line(r, ids[i]));
    if (ids.length > 40) sb.append("\n... and " + (ids.length - 40) + " more");
    return "=" + sb.toString();
  }
  if (r.bad) return "-" + nm + "'s pet file could not be read (" + r.why + ") - nothing was changed.";
  if (v.equals("unlock") || v.equals("lock")) {
    boolean on = v.equals("unlock");
    if (r.unlocked() == on) return "=" + nm + "'s summon slot is already " + (on ? "unlocked." : "locked.");
    r.set("slot2.unlocked", on ? "true" : "false");
    if (!@PKG@.PetStore.save(r)) return "-Could not save " + nm + "'s pets - nothing changed.";
    @PKG@.PetStore.ledger("-", "-", 0, 0, 0L, "", r.key, on ? "unlock slot 2" : "lock slot 2", by);
    if (on) @PKG@.PetsEng.tell(u, "[Pets] Your summon slot is unlocked! A pet there gives " + @PKG@.PetsCfg.SLOT2_PCT + "% of its buffs - /pets.", "@COLGLD@");
    return "+" + nm + "'s summon slot is now " + (on ? "unlocked" : "locked") + (on && "off".equals(@PKG@.PetsCfg.SLOT2_MODE) ? " (but Server Setup has the summon slot closed for everyone)." : ".");
  }
  if (v.equals("give")) {
    if (a == null || a.trim().length() == 0) return "-Which kind? /petadmin kinds";
    @PKG@.PetKind pk = @PKG@.PetsCfg.kind(a);
    if (pk == null) return "-No pet kind " + a + ". /petadmin kinds";
    if (!@PKG@.PetsCfg.kindOn(pk.id)) return "-" + pk.name + " is switched off (Server Setup > Pets > Pet kinds switched off).";
    int rar = b == null || b.trim().length() == 0 ? pk.rarity : @PKG@.PetKind.rarityOf(b);
    if (rar < 1 || rar > 5) return "-Rarity is Common, Uncommon, Rare, Epic or Legendary (1-5). Mythic is for dragons.";
    int lvl = 1;
    if (c != null && c.trim().length() > 0) { try { lvl = Integer.parseInt(c.trim()); } catch (Throwable t) { lvl = -1; } }
    if (lvl < 1 || lvl > 100) return "-Level is 1-100.";
    String res = create(r, null, pk.id, rar, lvl, 0L, "admin", by, true);
    if (res.startsWith("-")) return res;
    @PKG@.PetsEng.tell(u, "[Pets] You got a new pet: " + @PKG@.PetKind.rarityName(rar) + " " + pk.name + " (Lv " + lvl + ")! Open /pets.", "@COLGLD@");
    return "+Gave " + nm + " a " + @PKG@.PetKind.rarityName(rar) + " " + pk.name + " Lv " + lvl + " (id " + res + (r.slotOf(res) == 1 ? ", in the pet slot" : "") + ").";
  }
  if (v.equals("take")) {
    if (a == null || !r.has(a.trim())) return "-" + nm + " has no pet " + a + ". /petadmin list " + nm;
    String id = a.trim();
    String kd = r.kindOf(id);
    int rar = r.rarityOf(id), lvl = r.levelOf(id);
    long x = r.xpOf(id);
    int was = r.slotOf(id);
    String pn = petName(r, id);
    java.util.Properties gone = r.remove(id);
    if (!@PKG@.PetStore.save(r)) {
      java.util.Iterator it = gone.stringPropertyNames().iterator();
      while (it.hasNext()) { String k = (String) it.next(); r.set(k, gone.getProperty(k)); }
      if (was > 0) r.set("active." + was, id);
      return "-Could not save " + nm + "'s pets - nothing was taken.";
    }
    @PKG@.PetStore.INDEX.remove(id, r.key);
    @PKG@.PetStore.ledger(id, kd, rar, lvl, x, r.key, "", "take", by);
    @PKG@.PetsEng.tell(u, "[Pets] An admin took your " + pn + ".", "@COLINF@");
    return "+Took " + nm + "'s " + pn + " (" + id + "). Undo: /petadmin restore " + nm + " " + id;
  }
  if (v.equals("restore")) {
    if (a == null || a.trim().length() == 0) return "-Which pet id? (ledger.log)";
    String id = a.trim().toLowerCase();
    if (!id.matches("[0-9a-z]{8}")) return "-" + a.trim() + " is not a pet id (8 letters / digits, see /petadmin list or ledger.log).";
    Object owner = @PKG@.PetStore.INDEX.get(id);
    if (owner != null) return "-Pet " + id + " still belongs to " + owner + " - nothing to restore.";
    if (!@PKG@.PetStore.BAD.isEmpty()) {
      Object[] bk = @PKG@.PetStore.BAD.keySet().toArray();
      StringBuilder bs = new StringBuilder();
      for (int i = 0; i < bk.length && i < 5; i++) bs.append(i > 0 ? ", " : "").append(String.valueOf(bk[i]));
      if (bk.length > 5) bs.append(" and " + (bk.length - 5) + " more");
      return "-Not now: " + bk.length + " pet file(s) could not be read (" + bs.toString() + ") and may still hold pet " + id + ". Fix or move those files first (a fixed file is read again when its player joins), then restore.";
    }
    String[] l = @PKG@.PetStore.ledgerFind(id);
    if (l == null) return "-Pet " + id + " is not in ledger.log.";
    if (@PKG@.PetsCfg.kind(l[2]) == null) return "-Pet " + id + " was a " + l[2] + ", and that pet kind does not exist any more (Server Setup > Pets > Pet kinds).";
    int rar = 1, lvl = 1;
    long x = 0L;
    try { rar = Integer.parseInt(l[3]); lvl = Integer.parseInt(l[4]); x = Long.parseLong(l[5]); } catch (Throwable t) { }
    if (rar < 1 || rar > 6) rar = 1;
    String res = create(r, id, l[2], rar, lvl, x, "restore", by, false);
    if (res.startsWith("-")) return res;
    @PKG@.PetsEng.tell(u, "[Pets] An admin gave back your " + petName(r, id) + ".", "@COLGLD@");
    return "+Restored " + petName(r, id) + " Lv " + r.levelOf(id) + " (" + id + ") to " + nm + ".";
  }
  if (a == null || a.trim().length() == 0 || b == null) return "-Use /petadmin xp <player> <skill> <amount>.";
  long n = 0L;
  try { n = Long.parseLong(b.trim()); } catch (Throwable t) { n = -1L; }
  if (n <= 0L || n > 100000000L) return "-Amount is 1 - 100,000,000.";
  if (@PKG@.PetStore.REC.get(r.key) == null) @PKG@.PetStore.REC.put(r.key, r);
  int got = @PKG@.PetXp.give(u, a.trim(), n);
  if (got == 0) return "=No slotted pet of " + nm + " got XP (empty slots, kinds off, or pets off).";
  return "+" + got + " slotted pet(s) of " + nm + " got " + a.trim() + " XP from " + @PKG@.PetsLog.grp(n) + ".";
}""")

# =====================================================================================================================
# PetsPage: /pets (two slot rows + the owned list / details; the vanilla kit look)
# =====================================================================================================================
PAGEC = cls("PetsPage", T["PAGE"])
PW, PH = 960, 880
SH = SUI.page_shell("SkyyPt", PW, PH, "Pets", body_id="SkyyPtBody")
IW = SH.inner_w
J_ = SUI.J
SEC_H = 28
SR_ON = SUI.static_row("SkyyPtS" + J_("s", "1"), IW, icon=J_("ic", "Tool_Hoe_Iron"), name=J_("nm", "Biscuit"), sub=J_("sb", "Common - Lv 1"),
                       tag=J_("tg", "Full buffs"), tag_col=J_("tc", COL["gold"]), tag_w=220, action="Open", action_on=True)
SR_OFF = SUI.static_row("SkyyPtS" + J_("s", "1"), IW, icon=J_("ic", "Tool_Hoe_Iron"), name=J_("nm", "Biscuit"), sub=J_("sb", "Common - Lv 1"),
                        tag=J_("tg", "Full buffs"), tag_col=J_("tc", COL["gold"]), tag_w=220, action="Open", action_on=False)
assert [s[0] for s in SR_ON.sets] == [s[0] for s in SR_OFF.sets]
TOP_H = SEC_H + 2 * SR_ON.h
STATUS_H, STATUS_M = 30, 6
FOOT_H = SUI.BTN_H + 8
LOW_H = SH.inner_h - TOP_H - (STATUS_H + STATUS_M) - FOOT_H
PG = SUI.pager("SkyyPtLow", "SkyyPtPg", IW, text=None)
PG_H = PG.h
LIST_H = LOW_H - SEC_H - PG_H
LIST_IN = IW - 2 * SUI.WELL_LIST_PAD - 12
RW_ON = SUI.static_row("SkyyPtR" + J_("i", "0"), LIST_IN, icon=J_("ic", "Tool_Hoe_Iron"), name=J_("nm", "Biscuit"), sub=J_("sb", "Common - Lv 1"),
                       tag=J_("tg", "Pet slot"), tag_col=J_("tc", COL["gold"]), tag_w=200, action="Open")
assert LIST_H >= 8 * RW_ON.h + 2 * SUI.WELL_LIST_PAD, (LIST_H, RW_ON.h)
BROW_H = SUI.BTN_H + 8
PROP_H = LOW_H - SEC_H - BROW_H
DETAIL_KEYS = ["Kind", "Rarity", "Level", "XP", "Skill", "Slot", "In the pet slot", "In the summon slot", "Owned since", "Pet id"]
assert SH.fit([TOP_H, LOW_H, STATUS_H + STATUS_M, FOOT_H]) == 0, "the Pets page body must be filled exactly"
BTN_IDS = ["SkyyPtB1", "SkyyPtB2", "SkyyPtB3", "SkyyPtB4"]
BTN_TXT = ["Pet slot", "Summon slot", "Take out", "Back"]


def jl(parent, mkup, root=True):
    return SUI.java_append(parent, mkup, page_root=root)


def jsets(mkup):
    return "\n".join(SUI.java_set(i, p, v) for i, p, v in getattr(mkup, "sets", []))


def page_java():
    ap = SUI.Appends()
    ap.text(SH.body, "SkyyPtSlotsH", "Your slots", "section", h=SEC_H)
    top_head = ap.java("b")
    slot = jl(SH.body, SUI.choose(J_("on"), SR_ON, SR_OFF), True) + "\n" + jsets(SR_ON)
    low = jl(SH.body, SUI.group("SkyyPtLow", "Top", h=LOW_H))
    ap2 = SUI.Appends()
    ap2.text("SkyyPtLow", "SkyyPtLowH", "", "section", h=SEC_H)
    low_head = ap2.java("b", page_root=False)
    lst = jl("SkyyPtLow", SUI.scroll_list("SkyyPtList", h=LIST_H, well=True), False)
    row = jl("SkyyPtList", RW_ON, False) + "\n" + jsets(RW_ON)
    ap3 = SUI.Appends()
    ap3.text("SkyyPtList", "SkyyPtEmpty", J_("empty", "No pets yet."), "caption", h=48, wrap=True, max_lines=2)
    empty = ap3.java("b", page_root=False)
    pager = PG.java("b", page_root=False)
    props = jl("SkyyPtLow", SUI.scroll_list("SkyyPtProps", h=PROP_H, well=True), False)
    prow = "\n".join(jl("SkyyPtProps", SUI.property_row("SkyyPtD%d" % i, "SkyyPtD%dK" % i, "SkyyPtD%dV" % i, key_text=k, key_w=220), False)
                     for i, k in enumerate(DETAIL_KEYS))
    used = 4 * 200 + 3 * 12
    brow = jl("SkyyPtLow", SUI.button_row("SkyyPtBtns", align="center", used=used, avail=IW), False)
    btns = "\n".join(jl("SkyyPtBtns", SUI.button(BTN_IDS[i], BTN_TXT[i], "primary" if i < 2 else "secondary", w=200,
                                                 sound="cancel" if i == 3 else None, anchor={"left": 12} if i > 0 else None), False)
                     for i in range(4))
    status = jl(SH.body, SUI.status_line("SkyyPtStatus", anchor={"top": STATUS_M}))
    close_btn = SUI.button("SkyyPtClose", "Close", "secondary", sound="cancel")
    foot = jl(SH.body, SUI.button_row("SkyyPtFoot", align="right", used=SUI.BTN_MIN_W, avail=IW)) + "\n" + jl("SkyyPtFoot", close_btn, False)
    return dict(shell=SH.java("b"), tophead=top_head, slot=slot, low=low, lowhead=low_head, lst=lst, row=row, empty=empty, pager=pager,
                props=props, prow=prow, brow=brow, btns=btns, status=status, foot=foot)


PJ = page_java()


def ind(s, n=2):
    return "\n".join((" " * n) + l for l in s.split("\n"))


for _f in ("public int view;", "public int pg;", "public String sel;", "public String info;", "public String tok;", "public long base;",
           "public long seq;", "public String[] ids;", "public String[] slotIds;",
           "public static volatile long BUILDS = 0L;", "public static volatile long CLICKS = 0L;", "public static volatile long STALE = 0L;"):
    F(PAGEC, _f)
F(PAGEC, "public static final String[] RCOL = %s;" % jarr(RARITY_COLORS))
F(PAGEC, "public static final int PER_PAGE = 8;")
C(PAGEC, r"""
public PetsPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.view = 0; this.pg = 0; this.sel = ""; this.info = ""; this.tok = "0";
  this.base = System.nanoTime() & 0xffffffL; this.seq = 0L; this.ids = new String[0]; this.slotIds = new String[] { "", "" };
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
public static String rcol(int r) {
  return r >= 1 && r <= RCOL.length ? RCOL[r - 1] : RCOL[0];
}""")
M(PAGEC, r"""
public static String iconOf(@PKG@.PetRec r, String id) {
  @PKG@.PetKind pk = @PKG@.PetsCfg.kind(r.kindOf(id));
  return pk == null ? %s : pk.icon;
}""".replace("%s", jstr(ICON_OTHER)))
M(PAGEC, r"""
public static String xpText(@PKG@.PetRec r, String id) {
  int lv = r.levelOf(id);
  if (lv >= @PKG@.PetMath.MAX_LEVEL) return "Lv " + lv + " (max)";
  return "Lv " + lv + " - " + @PKG@.PetsLog.grp(r.xpOf(id)) + " / " + @PKG@.PetsLog.grp(@PKG@.PetMath.need(lv + 1)) + " XP";
}""")
M(PAGEC, r"""
public @PKG@.PetRec rec() {
  return @PKG@.PetStore.get(@PKG@.PetStore.pkey(this.playerRef.getUuid()));
}""")
BUILD_SRC = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  BUILDS = BUILDS + 1L;
  this.seq = this.seq + 1L;
  this.tok = Long.toHexString(this.base + this.seq);
  @PKG@.PetRec r = rec();
  boolean bad = r.bad;
  boolean open2 = @PKG@.PetBuff.slot2Open(r);
@SHELL@
@TOPHEAD@
  for (int s = 1; s <= 2; s++) {
    String sid = bad ? "" : r.active(s);
    this.slotIds[s - 1] = sid;
    boolean on = sid.length() > 0;
    String ic = on ? iconOf(r, sid) : "@ICON@";
    String nm = on ? @PKG@.PetOps.petName(r, sid) : (s == 1 ? "Pet slot - empty" : (open2 ? "Summon slot - empty" : "Summon slot - locked"));
    String sb = on ? xpText(r, sid) : (s == 1 ? "Open a pet below and press Pet slot." : (open2 ? "Open a pet below and press Summon slot." : @PKG@.PetBuff.lockedWhy()));
    String tg = s == 1 ? "Full buffs" : (open2 ? @PKG@.PetsCfg.SLOT2_PCT + "% buffs" : "Locked");
    String tc = on ? rcol(r.rarityOf(sid)) : "@DISABLED@";
@SLOT@
    if (on) ev.addEventBinding(@BT@.Activating, "#SkyyPtS" + s + "Act", @EVD@.of("a", "slot").append("i", String.valueOf(s)).append("t", this.tok));
  }
@LOW@
@LOWHEAD@
  if (this.view == 1 && !bad && r.has(this.sel)) {
    String id = this.sel;
    @PKG@.PetKind pk = @PKG@.PetsCfg.kind(r.kindOf(id));
    b.set("#SkyyPtLowH.Text", @PKG@.PetOps.petName(r, id));
@PROPS@
@PROW@
    int lv = r.levelOf(id);
    String[] v = new String[10];
    v[0] = pk == null ? r.kindOf(id) + " (unknown kind - gives nothing)" : pk.name + (@PKG@.PetsCfg.kindOn(pk.id) ? "" : " (switched off by the server)");
    v[1] = @PKG@.PetKind.rarityName(r.rarityOf(id)) + " (stats x" + @PKG@.PetsLog.num(@PKG@.PetsCfg.factor(r.rarityOf(id))) + ")";
    v[2] = lv + " / " + @PKG@.PetMath.MAX_LEVEL;
    v[3] = lv >= @PKG@.PetMath.MAX_LEVEL ? "max level" : @PKG@.PetsLog.grp(r.xpOf(id)) + " / " + @PKG@.PetsLog.grp(@PKG@.PetMath.need(lv + 1)) + " to Lv " + (lv + 1);
    v[4] = pk == null ? "-" : pk.skill + " (" + @PKG@.PetsCfg.XP_OWN + "% of that XP, " + @PKG@.PetsCfg.XP_OTHER + "% of other XP)";
    int sl = r.slotOf(id);
    v[5] = sl == 1 ? "Pet slot (full buffs)" : (sl == 2 ? "Summon slot (" + @PKG@.PetsCfg.SLOT2_PCT + "% buffs)" : "Not in a slot");
    v[6] = @PKG@.PetBuff.petText(r, id, 100.0);
    v[7] = open2 ? @PKG@.PetBuff.petText(r, id, (double) @PKG@.PetsCfg.SLOT2_PCT) : "summon slot locked";
    long got = r.lv("pet." + id + ".got", 0L);
    v[8] = got > 0L ? new java.text.SimpleDateFormat("yyyy-MM-dd").format(new java.util.Date(got)) : "-";
    v[9] = id;
    for (int i = 0; i < 10; i++) b.set("#SkyyPtD" + i + "V.Text", v[i]);
@BROW@
@BTNS@
    ev.addEventBinding(@BT@.Activating, "#SkyyPtB1", @EVD@.of("a", "to1").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyPtB2", @EVD@.of("a", "to2").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyPtB3", @EVD@.of("a", "out").append("t", this.tok));
    ev.addEventBinding(@BT@.Activating, "#SkyyPtB4", @EVD@.of("a", "back"));
  } else {
    this.view = 0;
    String[] all = bad ? new String[0] : r.ids();
    int pages = all.length == 0 ? 1 : (all.length + PER_PAGE - 1) / PER_PAGE;
    if (this.pg >= pages) this.pg = pages - 1;
    if (this.pg < 0) this.pg = 0;
    b.set("#SkyyPtLowH.Text", "Your pets (" + all.length + " / " + @PKG@.PetsCfg.OWNED_MAX + ")");
@LST@
    int from = this.pg * PER_PAGE;
    int n = all.length - from < PER_PAGE ? all.length - from : PER_PAGE;
    if (n < 0) n = 0;
    this.ids = new String[n];
    for (int i = 0; i < n; i++) {
      String id = all[from + i];
      this.ids[i] = id;
      String ic = iconOf(r, id);
      String nm = @PKG@.PetOps.petName(r, id);
      String sb = xpText(r, id);
      int sl = r.slotOf(id);
      String tg = sl == 1 ? "Pet slot" : (sl == 2 ? "Summon slot" : "");
      String tc = rcol(r.rarityOf(id));
@ROW@
      ev.addEventBinding(@BT@.Activating, "#SkyyPtR" + i + "Act", @EVD@.of("a", "open").append("i", String.valueOf(i)).append("t", this.tok));
    }
    if (n == 0) {
      String empty = bad ? "Your pet file could not be read - an admin has been told. Nothing is changed until it is fixed." : (!@PKG@.PetsCfg.ON ? "Pets are switched off on this server." : "No pets yet. Pets come from eggs, the Stable and quests.");
@EMPTY@
    }
@PAGER@
    b.set("#SkyyPtPgPage.Text", "Page " + (this.pg + 1) + " / " + pages);
    ev.addEventBinding(@BT@.Activating, "#SkyyPtPgPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyPtPgNext", @EVD@.of("a", "next"));
  }
@STATUS@
  String note = this.info;
  if (note.length() == 0 && !@PKG@.PetsCfg.ON) note = "-Pets are switched off on this server.";
  if (note.length() == 0 && bad) note = "-Your pet file could not be read - an admin has been told.";
  if (note.length() == 0) note = "=Strength, Crit, Defense and Magical Power count once SkyyGear reads pet stats.";
  b.set("#SkyyPtStatus.Text", textOf(note));
@FOOT@
  ev.addEventBinding(@BT@.Activating, "#SkyyPtClose", @EVD@.of("a", "close"));
}"""
_rep = {"@SHELL@": ind(PJ["shell"]), "@TOPHEAD@": ind(PJ["tophead"]), "@SLOT@": ind(PJ["slot"], 4), "@LOW@": ind(PJ["low"]),
        "@LOWHEAD@": ind(PJ["lowhead"]), "@PROPS@": ind(PJ["props"], 4), "@PROW@": ind(PJ["prow"], 4), "@BROW@": ind(PJ["brow"], 4),
        "@BTNS@": ind(PJ["btns"], 4), "@LST@": ind(PJ["lst"], 4), "@ROW@": ind(PJ["row"], 6), "@EMPTY@": ind(PJ["empty"], 6),
        "@PAGER@": ind(PJ["pager"], 4), "@STATUS@": ind(PJ["status"]), "@FOOT@": ind(PJ["foot"]), "@DISABLED@": COL["disabled"],
        "@ICON@": ICON_OTHER}
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
    if (a.equals("prev")) { if (this.pg > 0) this.pg = this.pg - 1; this.info = ""; rebuild(); return; }
    if (a.equals("next")) { this.pg = this.pg + 1; this.info = ""; rebuild(); return; }
    if (a.equals("back")) { this.view = 0; this.info = ""; rebuild(); return; }
    if (!jsonStr(data, "t").equals(this.tok)) { STALE = STALE + 1L; this.info = "=The page changed - here it is again."; rebuild(); return; }
    java.util.UUID u = this.playerRef.getUuid();
    String by = this.playerRef.getUsername();
    if (a.equals("open")) {
      if (i < 0 || i >= this.ids.length) this.info = "-That pet is gone.";
      else { this.sel = this.ids[i]; this.view = 1; this.info = ""; }
    } else if (a.equals("slot")) {
      if (i < 1 || i > 2 || this.slotIds[i - 1].length() == 0) this.info = "-That slot is empty.";
      else { this.sel = this.slotIds[i - 1]; this.view = 1; this.info = ""; }
    } else if (a.equals("to1")) this.info = @PKG@.PetOps.toSlot(u, this.sel, 1, by);
    else if (a.equals("to2")) this.info = @PKG@.PetOps.toSlot(u, this.sel, 2, by);
    else if (a.equals("out")) this.info = @PKG@.PetOps.takeOut(u, this.sel, by);
    else this.info = "";
  } catch (Throwable t) {
    @PKG@.PetsLog.warn("pets page click " + a + " failed: " + t);
    this.info = "-Something went wrong. The server log has the details.";
  }
  rebuild();
}""")

# =====================================================================================================================
# PetTick (the per-second logic, world thread) + PetTickSys (EntityTickingSystem on Player entities)
# =====================================================================================================================
tk = cls("PetTick")
F(tk, "public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();")
F(tk, "public static final java.util.concurrent.atomic.AtomicLong SECONDS = new java.util.concurrent.atomic.AtomicLong();")
F(tk, "public static final double[] ZERO = new double[%d];" % len(STAT_KEYS))
# a profile switch (the storage key changed): flush + forget the old record, re-baseline the XP fallback
M(tk, r"""
public static void switched(java.util.UUID u, String oldKey) {
  @PKG@.PetStore.release(oldKey);
  @PKG@.PetXp.forget(u);
  @PKG@.PetsLog.info("profile switch of " + u + ": pets of " + oldKey + " saved, now the active profile's pets");
}""")
M(tk, r"""
public static void second(java.util.UUID u, String world, @ESM@ m) {
  SECONDS.incrementAndGet();
  if (!@PKG@.PetsCfg.ON) { @PKG@.PetBuff.clear(u); @PKG@.PetBuff.stats(m, ZERO); return; }
  String key = @PKG@.PetStore.pkey(u);
  Object old = @PKG@.PetStore.KEYOF.put(u, key);
  if (old != null && !old.equals(key)) switched(u, (String) old);
  @PKG@.PetRec r = @PKG@.PetStore.get(key);
  @PKG@.PetOps.starter(u, r);
  double[] t = @PKG@.PetBuff.compute(r, world);
  @PKG@.PetBuff.publish(u, t);
  @PKG@.PetBuff.stats(m, t);
}""")
# dt accumulates per player; true once a second
M(tk, r"""
public static boolean due(java.util.UUID u, float dt) {
  Object o = CLOCK.get(u);
  double[] c = null;
  if (o instanceof double[]) c = (double[]) o;
  if (c == null) { c = new double[] { 1.0 }; CLOCK.put(u, c); }
  c[0] = c[0] + (double) dt;
  if (c[0] < 1.0) return false;
  c[0] = 0.0;
  return true;
}""")
tsys = cls("PetTickSys", T["ETS"])
F(tsys, "public static boolean FAILED_ONCE = false;")
C(tsys, "public PetTickSys() { super(); }")
M(tsys, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(tsys, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    @REF@ ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    @PR@ pr = (@PR@) store.getComponent(ref, @PR@.getComponentType());
    if (pr == null || pr.getUuid() == null) return;
    java.util.UUID u = pr.getUuid();
    if (!@PKG@.PetTick.due(u, dt)) return;
    @ESM@ m = (@ESM@) cb.getComponent(ref, @ESM@.getComponentType());
    @PKG@.PetTick.second(u, @PKG@.PetsEng.worldOf(store), m);
  } catch (Throwable t) {
    if (!FAILED_ONCE) { FAILED_ONCE = true; @PKG@.PetsLog.warn("pet tick failed (logged once): " + t); }
  }
}""")

# =====================================================================================================================
# PetLeave (flush + forget on the scheduler) + PetQuit (PlayerDisconnectEvent) + PetTimer (1 s: XP flush + fallback poll)
# =====================================================================================================================
lv_ = cls("PetLeave")
lv_.addInterface(pool.get("java.lang.Runnable"))
F(lv_, "public String key;")
C(lv_, "public PetLeave(String key) { this.key = key; }")
M(lv_, r"""
public void run() {
  try { @PKG@.PetStore.release(this.key); } catch (Throwable t) { @PKG@.PetsLog.warn("saving the pets of " + this.key + " at logout failed: " + t); }
}""")
M(tk, r"""
public static void leave(java.util.UUID u) {
  if (u == null) return;
  @PKG@.PetBuff.clear(u);
  CLOCK.remove(u);
  @PKG@.PetXp.forget(u);
  Object k = @PKG@.PetStore.KEYOF.remove(u);
  if (k == null) return;
  @PKG@.PetLeave job = new @PKG@.PetLeave((String) k);
  try { @HSV@.SCHEDULED_EXECUTOR.execute(job); } catch (Throwable t) { job.run(); }
}""")
quit_ = cls("PetQuit")
quit_.addInterface(pool.get("java.util.function.Consumer"))
C(quit_, "public PetQuit() { }")
M(quit_, r"""
public void accept(Object ev) {
  try {
    @PR@ pr = ((@PDE@) ev).getPlayerRef();
    if (pr != null) @PKG@.PetTick.leave(pr.getUuid());
  } catch (Throwable t) { @PKG@.PetsLog.warnOnce("quit:" + t.getClass().getName(), "logout handler failed: " + t); }
}""")
timer = cls("PetTimer")
timer.addInterface(pool.get("java.lang.Runnable"))
F(timer, "public static final java.util.concurrent.atomic.AtomicLong RUNS = new java.util.concurrent.atomic.AtomicLong();")
F(timer, "public static volatile long NEXT_FLUSH = 0L;")
F(timer, "public static volatile long NEXT_POLL = 0L;")
F(timer, "public static volatile long NEXT_SWEEP = 0L;")
F(timer, "public static final java.util.concurrent.atomic.AtomicLong SWEPT = new java.util.concurrent.atomic.AtomicLong();")
# a tick that runs after PlayerDisconnectEvent re-adds KEYOF / CLOCK / LAST + the bridge entries: every 30 s everything of a player
# who is not online any more goes through leave() again (SkyyTrees retainOnline pattern)
M(timer, r"""
public static int sweep() {
  java.util.UUID[] on = @PKG@.PetsEng.online();
  java.util.HashSet live = new java.util.HashSet();
  for (int i = 0; i < on.length; i++) live.add(on[i]);
  java.util.HashSet seen = new java.util.HashSet();
  seen.addAll(@PKG@.PetStore.KEYOF.keySet());
  seen.addAll(@PKG@.PetTick.CLOCK.keySet());
  seen.addAll(@PKG@.PetBuff.LAST.keySet());
  int n = 0;
  java.util.Iterator it = seen.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof java.util.UUID) || live.contains(o)) continue;
    @PKG@.PetTick.leave((java.util.UUID) o);
    n++;
  }
  if (n > 0) SWEPT.addAndGet((long) n);
  return n;
}""")
C(timer, "public PetTimer() { }")
M(timer, r"""
public void run() {
  try {
    RUNS.incrementAndGet();
    long now = System.currentTimeMillis();
    if (now >= NEXT_FLUSH) { NEXT_FLUSH = now + (long) @PKG@.PetsCfg.FLUSH_S * 1000L; @PKG@.PetStore.flushDirty(); }
    if (now >= NEXT_POLL) { NEXT_POLL = now + (long) @PKG@.PetsCfg.POLL_S * 1000L; @PKG@.PetXp.poll(); }
    if (now >= NEXT_SWEEP) { NEXT_SWEEP = now + 30000L; sweep(); }
  } catch (Throwable t) { @PKG@.PetsLog.warnOnce("timer:" + t.getClass().getName(), "the pet timer failed: " + t); }
}""")

# =====================================================================================================================
# Commands: /pets (alias /pet; every player) + /petadmin (op only, every positional form a usage variant)
# =====================================================================================================================
cmds = cls("PetCmds")
M(cmds, r"""
public static void reply(@PR@ pr, String res) {
  if (res == null || res.length() == 0) return;
  char c = res.charAt(0);
  String col = c == '+' ? "@COLOK@" : (c == '-' ? "@COLERR@" : "@COLINF@");
  String t = (c == '+' || c == '-' || c == '=') ? res.substring(1) : res;
  String[] ls = t.split("\n");
  for (int i = 0; i < ls.length; i++) @PKG@.PetsEng.say(pr, (i == 0 ? "[Pets] " : "  ") + ls[i], col);
}""")
M(cmds, r"""
public static String run(@PR@ pr, String[] a) {
  String by = pr == null ? "console" : pr.getUsername();
  String res = @PKG@.PetOps.admin(by, a.length > 0 ? a[0] : "", a.length > 1 ? a[1] : null, a.length > 2 ? a[2] : null, a.length > 3 ? a[3] : null, a.length > 4 ? a[4] : null);
  String v = a.length > 0 && a[0] != null ? a[0].trim().toLowerCase() : "";
  if (!v.equals("list") && !v.equals("kinds") && !v.equals("help") && res.startsWith("+")) @PKG@.PetsLog.info(by + ": /petadmin " + v + " " + (a.length > 1 ? a[1] : "") + " -> " + res.substring(1));
  return res;
}""")
EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
pcmd = cls("PetsCmd", T["APC"])
C(pcmd, r"""
public PetsCmd() {
  super("pets", "Your pets: the pet slot, the summon slot and every pet you own");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addAliases(new String[] { "pet" });
}""")
M(pcmd, EXEC + r""" {
  if (!@PKG@.PetsEng.open(ref, store, new @PKG@.PetsPage(pr))) @PKG@.PetsEng.say(pr, "[Pets] The Pets page could not open right now.", "@COLERR@");
}""")
ADMIN_FORMS = [  # class, description, arg names
    ("PetAdminArg1Cmd", "(admin) /petadmin kinds | help", ["option"]),
    ("PetAdminArg2Cmd", "(admin) /petadmin list | unlock | lock <player>", ["option", "player"]),
    ("PetAdminArg3Cmd", "(admin) /petadmin give <player> <kind> | take <player> <id> | restore <player> <id>", ["option", "player", "a"]),
    ("PetAdminArg4Cmd", "(admin) /petadmin give <player> <kind> <rarity> | xp <player> <skill> <amount>", ["option", "player", "a", "b"]),
    ("PetAdminArg5Cmd", "(admin) /petadmin give <player> <kind> <rarity> <level>", ["option", "player", "a", "b", "c"]),
]
ARG_HELP = {"option": "give, take, unlock, lock, list, restore, xp or kinds", "player": "an online player", "a": "kind, pet id or skill",
            "b": "rarity or amount", "c": "level 1-100"}
for _cn, _desc, _args in ADMIN_FORMS:
    _c = cls(_cn, T["APC"])
    for _a in _args:
        F(_c, "public @RA@ %sArg;" % _a)
    _ctor = ["public %s() {" % _cn, '  super(%s);' % jstr(_desc), '  requirePermission("@NODE@");', "  setPermissionGroups(new String[0]);"]
    for _a in _args:
        _ctor.append('  this.%sArg = withRequiredArg(%s, %s, @ATY@.STRING);' % (_a, jstr(_a), jstr(ARG_HELP[_a])))
    _ctor.append("}")
    C(_c, "\n".join(_ctor))
    _body = [EXEC + " {", "  String[] a = new String[%d];" % len(_args)]
    for _i, _a in enumerate(_args):
        _body.append("  try { a[%d] = String.valueOf(ctx.get(this.%sArg)); } catch (Throwable t%d) { a[%d] = \"\"; }" % (_i, _a, _i, _i))
    _body.append("  @PKG@.PetCmds.reply(pr, @PKG@.PetCmds.run(pr, a));")
    _body.append("}")
    M(_c, "\n".join(_body))
acmd = cls("PetAdminCmd", T["APC"])
_ac = ["public PetAdminCmd() {", '  super("petadmin", "(admin) Pets: /petadmin give | take | unlock | lock | list | restore | xp | kinds");',
       '  requirePermission("@NODE@");', "  setPermissionGroups(new String[0]);"]
for _cn, _d, _a in ADMIN_FORMS:
    _ac.append("  addUsageVariant(new @PKG@.%s());" % _cn)
_ac.append("}")
C(acmd, "\n".join(_ac))
M(acmd, EXEC + " { @PKG@.PetCmds.reply(pr, @PKG@.PetCmds.run(pr, new String[] { \"help\" })); }")

# =====================================================================================================================
# the plugin
# =====================================================================================================================
plug = cls("SkyyPetsPlugin", T["JP"])
F(plug, "public static volatile Object TIMER = null;")
C(plug, "public SkyyPetsPlugin(@JPI@ init) { super(init); }")
M(plug, r"""
public void setup() {
  @PKG@.PetsLog.LOG = getLogger();
  java.nio.file.Path mods = getDataDirectory().getParent();
  @PKG@.PetsCfg.load(mods);
  @PKG@.PetStore.ROOT = mods.resolve("Skyy_SkyyPets");
  @PKG@.PetStore.DIR = @PKG@.PetStore.ROOT.resolve("pets");
  int[] sc = @PKG@.PetStore.scanAll();
  @PKG@.CfgPub.start(mods, getLogger());
  @PKG@.PetsLog.bridge().put("pets:fn:onxp", new @PKG@.PetXpFn());
  getCommandRegistry().registerCommand(new @PKG@.PetsCmd());
  getCommandRegistry().registerCommand(new @PKG@.PetAdminCmd());
  try { getEntityStoreRegistry().registerSystem(new @PKG@.PetTickSys()); }
  catch (Throwable t) { @PKG@.PetsLog.warn("PetTickSys could not be registered: " + t + " - no pet buffs and no starter pets"); }
  getEventRegistry().registerGlobal(@PDE@.class, new @PKG@.PetQuit());
  try { TIMER = @HSV@.SCHEDULED_EXECUTOR.scheduleWithFixedDelay(new @PKG@.PetTimer(), 5L, 1L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t3) { @PKG@.PetsLog.warn("the pet timer could not start: " + t3 + " - pet XP is saved only at logout / shutdown"); }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyPets] @VERSION@ ready - " + @PKG@.PetsCfg.KINDS.length + " pet kinds, " + sc[0] + " pet files, " + sc[1] + " pets, " + sc[2] + " unreadable, " + sc[3] + " duplicates quarantined; " + (@PKG@.PetsCfg.ON ? "ON" : "OFF") + ", summon slot " + @PKG@.PetsCfg.SLOT2_MODE + " (" + @PKG@.PetsCfg.SLOT2_PCT + "%), starter " + @PKG@.PetsCfg.STARTER + ", XP fallback " + (@PKG@.PetsCfg.FALLBACK ? "on" : "off") + "; bridge pets:fn:onxp + pets:stats:<uuid>; /pets, /petadmin; kit @KITID@, page @PAGEID@");
}""".replace("@PAGEID@", PAGE_ID))
M(plug, r"""
protected void shutdown() {
  try { if (TIMER instanceof java.util.concurrent.Future) ((java.util.concurrent.Future) TIMER).cancel(false); } catch (Throwable t) { }
  try { @PKG@.PetStore.flushDirty(); } catch (Throwable t2) { @PKG@.PetsLog.warn("the last pet save failed: " + t2); }
  try {
    java.util.Map br = @PKG@.PetsLog.bridge();
    Object f = br.get("pets:fn:onxp");
    if (f instanceof @PKG@.PetXpFn) br.remove("pets:fn:onxp", f);
    @PKG@.PetBuff.clearAll();
  } catch (Throwable t5) { @PKG@.PetsLog.warn("could not take the pet entries off the bridge: " + t5); }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t4) { }
  super.shutdown();
}""")

# ================================================================= write + assemble
kit.write(OUT)
for c in ALL:
    c.writeFile(OUT)
print("classes written: %d (+ the config kit's 7); pets page id %s; %d pet kinds" % (len(ALL), PAGE_ID, len(KINDS)))
jar = os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)
man = B.manifest(MOD, VERSION, "SkyWynn slot pets (phase 1): per-profile pet records, the pet slot + summon slot with buffs, pet XP and "
                 "levels, /pets page, /petadmin. Visible pets, eggs and fighting come in later versions.", PKG + ".SkyyPetsPlugin")
man["IncludesAssetPack"] = False
B.assemble(jar, man, OUT)
