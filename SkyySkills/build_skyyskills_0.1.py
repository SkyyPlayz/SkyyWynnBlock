"""SkyySkills 0.1 - build script (javassist via jpype). Hypixel-SkyBlock-style skills: Mining, Foraging, Farming, Combat.
Run:   python build_skyyskills_0.1.py            -> SkyySkills/SkyySkills-0.1.jar
       python build_skyyskills_0.1.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world
Design:
 - XP from BreakBlockEvent (Collections CollSystem pattern). The award is DEFERRED with world.execute(Runnable) and only paid when
   event.isCancelled() is still false (World.execute always queues, so every other system - e.g. SkyyIslands' GuardSystem, whose
   order relative to ours is unknown - has run by then). The engine creates a new BreakBlockEvent per break (BlockHarvestUtils).
 - Block -> skill/xp from Skyy_SkyySkills/xp.properties (written with defaults on first run): block.<id>, prefix.<start>,
   suffix.<end> rules; exact wins, then the longest prefix/suffix. Growth-stage crops resolve to their item id
   (BlockType.getItem().getId(), e.g. Plant_Crop_Wheat_Block) and only pay when the broken state is "StageFinal".
 - Anti-exploit (Hypixel does the same): positions of blocks placed by players (PlaceBlockEvent, also deferred + cancel-checked)
   are remembered per world (Skyy_SkyySkills/placed/<world>.bin, LRU capped); breaking such a block pays no XP. Ripe-checked
   crops are exempt (they are always planted). Creative mode pays no XP (creativeXp=false).
 - Farming also counts F-harvesting a ripe crop (UseBlockEvent.Post on a StageFinal block with a Harvest drop list: eternal
   crops, berry bushes). Post is NOT proof of a harvest: UseBlockInteraction fires it right after InteractionContext.execute(),
   which only pushes the HarvestCrop root onto the chain, and it fires even when the harvest then fails (world gathering
   disabled, broken tool, ...). So HarvestTask polls the block at that position on the world thread (next tick, then every
   100 ms for up to 2 s) and pays only once it has left the ripe state (HarvestCrop resets it to the after-harvest stage or
   EMPTY). One pending check per position; a position pays at most once per harvestCooldownMs (default 5 s, breaking a ripe
   crop shares that gate). Sickle-swing harvesting fires no event and is NOT counted.
 - Combat: DeathSystems.OnDeathSystem subclass (vanilla KillFeed / EndlessLeveling XpEventSystem pattern): onComponentAdded
   (DeathComponent) on an NPCEntity whose DeathComponent.getDeathInfo().getSource() is a Damage.EntitySource (ProjectileSource
   extends it) whose ref has a PlayerRef. XP = NPC max health (EntityStatMap/DefaultEntityStatTypes.getHealth) x perHealth,
   clamped; combat.role.<RoleName>=xp overrides.
 - Levels 0..50, Hypixel per-level XP table (levels= in xp.properties overrides). Level-up: gold chat line + coins through the
   SkyyCoins bridge coins:fn:add (coinsPerLevel x level). Rewards are paid once per level: <Skill>.paid (highest PAID level)
   only moves past a level after coins:fn:add really paid it, so a reward that could not be paid (SkyyCoins missing or
   failing) stays owed and is retried on that skill's next XP gain (a chat line reports the late coins). XP earned before a
   paid marker existed is not back-paid. XP feedback aggregated, at most one chat line per feedbackMs (2s) per player,
   leftovers flushed by a 1s ticker via world.execute; /skills quiet toggles it.
 - /skills (/skill) opens an inline page (row per skill: item icon, name + level, 2-Group progress bar, xp / next, Top 10 button);
   /skills top <skill> prints the top 10 in chat; /skills reload (perm skyyskills.admin) re-reads xp.properties.
 - Persistence Skyy_SkyySkills/players/<uuid>.properties (name, quiet, <Skill>=xp, <Skill>.paid=level), dirty-flush every 10s
   and on shutdown (Collections saver pattern). Bridge: skill:<uuid> = "Mining:12,Foraging:3,Farming:0,Combat:5",
   skill:fn:level = Function apply(Object[]{UUID, String skill}) -> Integer.
 - Threads/locks: no disk I/O runs while the global SkillStore lock is held (files are read before it and written after a
   snapshot taken under it; coin payouts hold only that player's own lock). HytaleServer.SCHEDULED_EXECUTOR is ONE shared
   thread, so the ticker never loads a player file there: an online player whose data is not in memory yet is handed to his
   world thread (PublishTask, FlushTask pattern) to be loaded and published. The 10s dirty-flush still writes on the ticker.
"""
import sys, os, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
CMP = "com.hypixel.hytale.component.Component"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
MSG = "com.hypixel.hytale.server.core.Message"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PAGE= "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE= "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
GM  = "com.hypixel.hytale.protocol.GameMode"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
CEV = "com.hypixel.hytale.component.system.CancellableEcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
BBE = "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent"
PBE = "com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent"
UBE = "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent"
UBP = "com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Post"
BTY = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
SDT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.StateData"
BGA = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
V3I = "org.joml.Vector3i"
ODS = "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$OnDeathSystem"
DTH = "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent"
DMG = "com.hypixel.hytale.server.core.modules.entity.damage.Damage"
DES = "com.hypixel.hytale.server.core.modules.entity.damage.Damage.EntitySource"   # javassist source name (dotted nested)
NPC = "com.hypixel.hytale.server.npc.entities.NPCEntity"
ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
DST = "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes"
CHS = "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore"
BSC = "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection"
BTM = "com.hypixel.hytale.assetstore.map.BlockTypeAssetMap"

for c, m in ((BBE, "getBlockType"), (BBE, "getTargetBlock"), (PBE, "getTargetBlock"), (UBE, "getBlockType"), (CEV, "isCancelled"),
             (BTY, "getId"), (BTY, "getItem"), (BTY, "getStateForBlock"), (BTY, "getState"), (BTY, "getGathering"), (SDT, "getStateNames"),
             (BGA, "getHarvest"), (ITM, "getId"), (V3I, "x"), (V3I, "y"), (V3I, "z"),
             (ACH, "getReferenceTo"), (ST, "getExternalData"), (ST, "getComponent"), (EST, "getWorld"), (WLD, "execute"), (WLD, "getName"),
             (ODS, "componentType"), (ODS, "onComponentSet"), (ODS, "onComponentRemoved"), ("com.hypixel.hytale.component.system.RefChangeSystem", "onComponentAdded"),
             (DTH, "getDeathInfo"), (DMG, "getSource"), ("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource", "getRef"),
             (REF, "isValid"), (REF, "getStore"), (NPC, "getComponentType"), (NPC, "getRoleName"),
             (ESM, "getComponentType"), (ESM, "get"), (ESV, "getMax"), (DST, "getHealth"),
             (PLA, "getGameMode"), (PLA, "getPageManager"), (GM, "Creative"),
             (UNI, "getPlayers"), (UNI, "getPlayer"), (UNI, "getWorld"), (PR, "getWorldUuid"), (PR, "getUsername"), (PR, "hasPermission"),
             (MSG, "raw"), (MSG, "color"), (PAGE, "rebuild"), (EVD, "of"), (HSV, "SCHEDULED_EXECUTOR"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addSubCommand"),
             ("com.hypixel.hytale.server.core.command.system.AbstractCommand", "addAliases"),
             ("com.hypixel.hytale.component.Archetype", "empty"),
             (UBE, "getTargetBlock"), (WLD, "getChunkStore"), (CHS, "getChunkSectionReferenceAtBlock"), (CHS, "getStore"),
             (BSC, "get"), (BSC, "getComponentType"), (BTY, "getAssetMap"), (BTM, "getAsset"),
             ("java.util.concurrent.ScheduledExecutorService", "schedule"), ("java.util.concurrent.ConcurrentHashMap", "putIfAbsent"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)

# ================= default xp.properties (generated here, every id checked against Assets.zip) =================
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
with zipfile.ZipFile(ASSETS) as z:
    ITEM_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
def must(i):
    if i not in ITEM_IDS: raise SystemExit("unknown item id in defaults: " + i)
    return i
def must_prefix(p):
    if not any(i.startswith(p) for i in ITEM_IDS): raise SystemExit("prefix matches no item: " + p)
    return p
def must_suffix(s):
    if not any(i.endswith(s) for i in ITEM_IDS): raise SystemExit("suffix matches no item: " + s)
    return s

LEVELS = [50, 125, 200, 300, 500, 750, 1000, 1500, 2000, 3500, 5000, 7500, 10000, 15000, 20000, 30000, 50000, 75000, 100000, 200000,
          300000, 400000, 500000, 600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1400000, 1500000, 1600000,
          1700000, 1800000, 1900000, 2000000, 2100000, 2200000, 2300000, 2400000, 2500000, 2600000, 2750000, 2900000, 3100000,
          3400000, 3700000, 4000000]
assert len(LEVELS) == 50
ICONS = ["Tool_Pickaxe_Iron", "Tool_Hatchet_Iron", "Tool_Hoe_Iron", "Weapon_Sword_Iron"]
for i in ICONS: must(i)

L = []
L.append("# SkyySkills %s - XP rules. Edit, then /skills reload (permission skyyskills.admin) or restart the server." % VERSION)
L.append("# Block ids are the ids /collections shows. Growth-stage crops use their item id, e.g. Plant_Crop_Wheat_Block.")
L.append("#   block.<exact id>=<Skill>:<xp>      exact id, beats every other rule")
L.append("#   prefix.<start of id>=<Skill>:<xp>  the LONGEST matching prefix or suffix wins")
L.append("#   suffix.<end of id>=<Skill>:<xp>")
L.append("#   <Skill>:0 or none = no XP.  Skill = Mining | Foraging | Farming   (Combat comes from kills, see combat.*)")
L.append("# ignorePlaced=true : blocks a player placed pay no XP (crops that must ripen are exempt; they only pay when fully grown)")
L.append("multiplier=1.0")
L.append("coinsPerLevel=100")
L.append("feedback=true")
L.append("feedbackMs=2000")
L.append("creativeXp=false")
L.append("ignorePlaced=true")
L.append("farmingNeedsRipe=true")
L.append("# F-harvest (eternal crops, berry bushes) pays only after the crop really was harvested, and one block pays at most once")
L.append("# per harvestCooldownMs (minimum 3000). Breaking a ripe crop uses the same per-block gate.")
L.append("harvestCooldownMs=5000")
L.append("# Combat XP per NPC kill = NPC max health x combat.perHealth, clamped to combat.min..combat.max (combat.default if the")
L.append("# health is unknown). Exact overrides by NPC role name: combat.role.<RoleName>=<xp>  (the server log prints unknown roles once)")
L.append("combat.perHealth=0.2")
L.append("combat.min=1")
L.append("combat.max=500")
L.append("combat.default=5")
L.append("# XP needed for each level, level 1 first (Hypixel SkyBlock table; the number of entries is the max level)")
L.append("levels=" + ",".join(str(x) for x in LEVELS))
L.append("")
L.append("# ---------- Mining ----------")
L.append("prefix.%s=Mining:1" % must_prefix("Rock_"))
L.append("prefix.%s=Mining:1" % must_prefix("Rubble_"))
L.append("prefix.%s=Mining:8" % must_prefix("Rock_Crystal_"))
L.append("prefix.%s=Mining:40" % must_prefix("Rock_Gem_"))
L.append("block.%s=none" % must("Rock_Bedrock"))
L.append("prefix.%s=Mining:2" % must_prefix("Soil_Sand"))
L.append("prefix.%s=Mining:2" % must_prefix("Soil_Gravel"))
L.append("suffix.%s=Mining:2" % must_suffix("_Gravel"))
L.append("prefix.%s=Mining:5" % must_prefix("Ore_"))
for ore, xp in (("Copper", 5), ("Iron", 8), ("Silver", 10), ("Gold", 12), ("Cobalt", 15), ("Thorium", 18), ("Mithril", 25),
                ("Adamantite", 30), ("Onyxium", 40), ("Prisma", 50)):
    L.append("prefix.%s=Mining:%d" % (must_prefix("Ore_" + ore), xp))
L.append("")
L.append("# ---------- Foraging ----------")
L.append("prefix.%s=Foraging:1" % must_prefix("Plant_Leaves_"))
L.append("suffix.%s=Foraging:6" % must_suffix("_Trunk"))
L.append("suffix.%s=Foraging:6" % must_suffix("_Trunk_Full"))
L.append("suffix.%s=Foraging:2" % must_suffix("_Roots"))
for s in ("_Branch_Short", "_Branch_Long", "_Branch_Corner"):
    L.append("suffix.%s=Foraging:1" % must_suffix(s))
WOOD_TIERS = [(3, ["Bamboo"]),
              (10, ["Redwood", "Banyan", "Bottletree", "Gumboab", "Wisteria_Wild", "Windwillow", "Fig_Blue", "Spiral", "Petrified", "Poisoned"]),
              (15, ["Azure", "Amber", "Stormbark"]), (20, ["Fire", "Ice"]), (30, ["Crystal"])]
for xp, woods in WOOD_TIERS:
    for w in woods:
        for suf in ("_Trunk", "_Trunk_Full"):
            iid = "Wood_%s%s" % (w, suf)
            if suf == "_Trunk": must(iid)
            if iid in ITEM_IDS: L.append("block.%s=Foraging:%d" % (iid, xp))
L.append("")
L.append("# ---------- Farming (crops pay only when fully grown) ----------")
L.append("prefix.%s=Farming:3" % must_prefix("Plant_Crop_"))
for crop, xp in (("Wheat", 4), ("Carrot", 4), ("Potato", 4), ("Lettuce", 4), ("Onion", 5), ("Turnip", 5), ("Cotton", 5), ("Rice", 5),
                 ("Corn", 6), ("Cauliflower", 6), ("Tomato", 6), ("Chilli", 7), ("Aubergine", 7), ("Pumpkin", 8), ("Berry", 3),
                 ("Apple", 5), ("Mushroom", 3), ("Wild_Grass", 1), ("Health1", 10), ("Health2", 15), ("Health3", 20),
                 ("Mana1", 10), ("Mana2", 15), ("Mana3", 20), ("Stamina1", 10), ("Stamina2", 15), ("Stamina3", 20)):
    L.append("prefix.%s=Farming:%d" % (must_prefix("Plant_Crop_" + crop), xp))
L.append("prefix.%s=Farming:2" % must_prefix("Plant_Cactus"))
DEFAULTS = "\n".join(L) + "\n"
assert all(ord(ch) < 128 for ch in DEFAULTS)
DEFAULTS_LIT = json.dumps(DEFAULTS)   # valid Java string literal for ASCII text (\n \" \\ escapes)

PKG = "com.skyy.skills"
defs = pool.makeClass(PKG + ".SkillDefs")
cfg  = pool.makeClass(PKG + ".SkillCfg")
sto  = pool.makeClass(PKG + ".SkillStore")
fn   = pool.makeClass(PKG + ".SkillFn")
msg  = pool.makeClass(PKG + ".SkillMsg")
fl   = pool.makeClass(PKG + ".FlushTask")
pub  = pool.makeClass(PKG + ".PublishTask")
xp   = pool.makeClass(PKG + ".SkillXp")
plc  = pool.makeClass(PKG + ".PlacedStore")
hg   = pool.makeClass(PKG + ".HarvestGate")
btk  = pool.makeClass(PKG + ".BreakTask")
ptk  = pool.makeClass(PKG + ".PlaceTask")
htk  = pool.makeClass(PKG + ".HarvestTask")
bsy  = pool.makeClass(PKG + ".BreakSys", pool.get(EES))
psy  = pool.makeClass(PKG + ".PlaceSys", pool.get(EES))
usy  = pool.makeClass(PKG + ".HarvestSys", pool.get(EES))
ksy  = pool.makeClass(PKG + ".KillSys", pool.get(ODS))
tcm  = pool.makeClass(PKG + ".TopCmp")
top  = pool.makeClass(PKG + ".SkillTop")
page = pool.makeClass(PKG + ".SkillsPage", pool.get(PAGE))
tcmd = pool.makeClass(PKG + ".TopCmd", pool.get(APC))
qcmd = pool.makeClass(PKG + ".QuietCmd", pool.get(APC))
rcmd = pool.makeClass(PKG + ".ReloadCmd", pool.get(APC))
cmd  = pool.makeClass(PKG + ".SkillsCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".SkillTick")
pl   = pool.makeClass(PKG + ".SkyySkillsPlugin", pool.get(JP))

# ================= SkillDefs: names, icons, level table =================
defs.addField(CtField.make('public static final String[] NAMES = new String[] { "Mining", "Foraging", "Farming", "Combat" };', defs))
defs.addField(CtField.make('public static final String[] ICONS = new String[] { %s };' % ", ".join('"%s"' % i for i in ICONS), defs))
defs.addField(CtField.make('public static final String[] COLORS = new String[] { "#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a" };', defs))
defs.addField(CtField.make("public static final int N = 4;", defs))
defs.addField(CtField.make("public static final int MINING = 0;", defs))
defs.addField(CtField.make("public static final int FORAGING = 1;", defs))
defs.addField(CtField.make("public static final int FARMING = 2;", defs))
defs.addField(CtField.make("public static final int COMBAT = 3;", defs))
defs.addField(CtField.make("public static final long[] DEFAULT_PER = new long[] { %s };" % ", ".join("%dL" % x for x in LEVELS), defs))
defs.addField(CtField.make("public static volatile long[] PER = DEFAULT_PER;", defs))
defs.addField(CtField.make("public static volatile long[] CUM = new long[] { 0L };", defs))
defs.addField(CtField.make("public static volatile int MAX = 50;", defs))
defs.addMethod(CtNewMethod.make("""
public static synchronized void setTable(long[] per) {
  if (per == null || per.length == 0) return;
  long[] cum = new long[per.length + 1];
  cum[0] = 0L;
  for (int i = 0; i < per.length; i++) cum[i + 1] = cum[i] + per[i];
  PER = per; CUM = cum; MAX = per.length;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int levelOf(long total) {
  long[] cum = CUM;
  int max = cum.length - 1;
  int l = 0;
  while (l < max && total >= cum[l + 1]) l++;
  return l;
}""", defs))
# XP into the current level
defs.addMethod(CtNewMethod.make("""
public static long intoLevel(long total) {
  int l = levelOf(total);
  return total - CUM[l];
}""", defs))
# XP the current level needs in total (0 at max level)
defs.addMethod(CtNewMethod.make("""
public static long needFor(long total) {
  int l = levelOf(total);
  long[] per = PER;
  return l < per.length ? per[l] : 0L;
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static int indexOf(String s) {
  if (s == null) return -1;
  String t = s.trim().toLowerCase();
  if (t.length() == 0) return -1;
  for (int i = 0; i < NAMES.length; i++) if (NAMES[i].toLowerCase().equals(t)) return i;
  if (t.length() >= 3) for (int i = 0; i < NAMES.length; i++) if (NAMES[i].toLowerCase().startsWith(t)) return i;
  return -1;
}""", defs))
# compact number: 950, 12.3k, 1.25m, 3.10b (no commas: UI text is sanitized)
defs.addMethod(CtNewMethod.make("""
public static String fmt(long n) {
  if (n < 0L) return "-" + fmt(n == Long.MIN_VALUE ? Long.MAX_VALUE : -n);
  if (n < 10000L) return String.valueOf(n);
  if (n < 1000000L) { long t = n / 100L; return (t / 10L) + "." + (t % 10L) + "k"; }
  if (n < 1000000000L) { long h = n / 10000L; return (h / 100L) + "." + ((h % 100L) < 10L ? "0" : "") + (h % 100L) + "m"; }
  long g = n / 10000000L;
  return (g / 100L) + "." + ((g % 100L) < 10L ? "0" : "") + (g % 100L) + "b";
}""", defs))
defs.addMethod(CtNewMethod.make("""
public static String progress(long total) {
  long need = needFor(total);
  if (need <= 0L) return "MAX";
  return fmt(intoLevel(total)) + "/" + fmt(need);
}""", defs))

# ================= SkillCfg: xp.properties =================
cfg.addField(CtField.make("public static java.nio.file.Path FILE;", cfg))
cfg.addField(CtField.make(f"public static {LOG} LOG;", cfg))
cfg.addField(CtField.make("public static final String DEFAULTS = " + DEFAULTS_LIT + ";", cfg))
cfg.addField(CtField.make("public static volatile double MULT = 1.0;", cfg))
cfg.addField(CtField.make("public static volatile long COINS_PER_LEVEL = 100L;", cfg))
cfg.addField(CtField.make("public static volatile boolean FEEDBACK = true;", cfg))
cfg.addField(CtField.make("public static volatile long FEEDBACK_MS = 2000L;", cfg))
cfg.addField(CtField.make("public static volatile boolean CREATIVE = false;", cfg))
cfg.addField(CtField.make("public static volatile boolean IGNORE_PLACED = true;", cfg))
cfg.addField(CtField.make("public static volatile boolean NEED_RIPE = true;", cfg))
cfg.addField(CtField.make("public static volatile long HARVEST_GATE_MS = 5000L;", cfg))
cfg.addField(CtField.make("public static volatile double C_PER_HP = 0.2;", cfg))
cfg.addField(CtField.make("public static volatile long C_MIN = 1L;", cfg))
cfg.addField(CtField.make("public static volatile long C_MAX = 500L;", cfg))
cfg.addField(CtField.make("public static volatile long C_DEFAULT = 5L;", cfg))
cfg.addField(CtField.make("public static volatile java.util.HashMap EXACT = new java.util.HashMap();", cfg))
cfg.addField(CtField.make("public static volatile java.util.ArrayList PFX = new java.util.ArrayList();", cfg))
cfg.addField(CtField.make("public static volatile java.util.ArrayList SFX = new java.util.ArrayList();", cfg))
cfg.addField(CtField.make("public static volatile java.util.HashMap ROLE = new java.util.HashMap();", cfg))
cfg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();", cfg))
cfg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN_ROLES = new java.util.concurrent.ConcurrentHashMap();", cfg))
cfg.addField(CtField.make("public static final long[] NONE = new long[] { -1L, 0L };", cfg))
cfg.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyySkills] " + msg); } catch (Throwable t) { }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyySkills] " + msg); } catch (Throwable t) { }
}""", cfg))
# "Mining:5" -> {0, 5}; "none" / ":0" -> NONE; bad -> null
cfg.addMethod(CtNewMethod.make(f"""
public static long[] parseRule(String v) {{
  if (v == null) return null;
  String s = v.trim();
  if (s.equalsIgnoreCase("none") || s.length() == 0) return NONE;
  int c = s.indexOf(':');
  if (c <= 0) return null;
  int sk = {PKG}.SkillDefs.indexOf(s.substring(0, c));
  if (sk < 0 || sk == {PKG}.SkillDefs.COMBAT) return null;
  try {{
    long x = Long.parseLong(s.substring(c + 1).trim());
    if (x <= 0L) return NONE;
    return new long[] {{ (long) sk, x }};
  }} catch (Throwable t) {{ return null; }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static double dbl(java.util.Properties p, String k, double d) {
  try { String v = p.getProperty(k); return v == null ? d : Double.parseDouble(v.trim()); } catch (Throwable t) { return d; }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim();
  if (v.equalsIgnoreCase("true")) return true;
  if (v.equalsIgnoreCase("false")) return false;
  return d;
}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{
  int bad = 0;
  try {{
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {{
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }}
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try {{ p.load(in); }} finally {{ in.close(); }}
    {PKG}.SkillDefs.setTable({PKG}.SkillDefs.DEFAULT_PER);
    java.util.HashMap ex = new java.util.HashMap();
    java.util.ArrayList pf = new java.util.ArrayList();
    java.util.ArrayList sf = new java.util.ArrayList();
    java.util.HashMap ro = new java.util.HashMap();
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {{
      String k = ((String) en.nextElement()).trim();
      String v = p.getProperty(k);
      if (k.startsWith("combat.role.")) {{
        try {{ ro.put(k.substring(12), Long.valueOf(Long.parseLong(v.trim()))); }} catch (Throwable t) {{ bad++; }}
        continue;
      }}
      int kind = k.startsWith("block.") ? 0 : (k.startsWith("prefix.") ? 1 : (k.startsWith("suffix.") ? 2 : -1));
      if (kind < 0) continue;
      String id = k.substring(kind == 0 ? 6 : 7);
      if (id.length() == 0) {{ bad++; continue; }}
      long[] r = parseRule(v);
      if (r == null) {{ bad++; warn("bad rule " + k + "=" + v + " (want <Skill>:<xp> or none)"); continue; }}
      if (kind == 0) ex.put(id, r);
      else if (kind == 1) pf.add(new Object[] {{ id, r }});
      else sf.add(new Object[] {{ id, r }});
    }}
    MULT = dbl(p, "multiplier", 1.0);
    if (MULT < 0.0) MULT = 0.0;
    COINS_PER_LEVEL = lng(p, "coinsPerLevel", 100L);
    FEEDBACK = bool(p, "feedback", true);
    FEEDBACK_MS = lng(p, "feedbackMs", 2000L);
    if (FEEDBACK_MS < 500L) FEEDBACK_MS = 500L;
    CREATIVE = bool(p, "creativeXp", false);
    IGNORE_PLACED = bool(p, "ignorePlaced", true);
    NEED_RIPE = bool(p, "farmingNeedsRipe", true);
    HARVEST_GATE_MS = lng(p, "harvestCooldownMs", 5000L);
    if (HARVEST_GATE_MS < 3000L) HARVEST_GATE_MS = 3000L;
    C_PER_HP = dbl(p, "combat.perHealth", 0.2);
    C_MIN = lng(p, "combat.min", 1L);
    C_MAX = lng(p, "combat.max", 500L);
    C_DEFAULT = lng(p, "combat.default", 5L);
    String lv = p.getProperty("levels");
    if (lv != null && lv.trim().length() > 0) {{
      String[] parts = lv.split(",");
      long[] per = new long[parts.length];
      boolean ok = parts.length >= 1 && parts.length <= 100;
      for (int i = 0; i < parts.length && ok; i++) {{
        try {{ per[i] = Long.parseLong(parts[i].trim()); if (per[i] <= 0L) ok = false; }} catch (Throwable t) {{ ok = false; }}
      }}
      if (ok) {PKG}.SkillDefs.setTable(per); else {{ bad++; warn("bad levels= line, using the default table"); }}
    }}
    EXACT = ex; PFX = pf; SFX = sf; ROLE = ro;
    CACHE.clear();
    return ex.size() + " exact, " + pf.size() + " prefix, " + sf.size() + " suffix, " + ro.size() + " role rule(s), max level " + {PKG}.SkillDefs.MAX + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");
  }} catch (Throwable t) {{
    warn("could not load xp.properties: " + t);
    return "load failed: " + t;
  }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long[] resolve(String id) {
  if (id == null) return NONE;
  long[] c = (long[]) CACHE.get(id);
  if (c != null) return c;
  long[] best = (long[]) EXACT.get(id);
  if (best == null) {
    int bestLen = -1;
    java.util.ArrayList pf = PFX;
    for (int i = 0; i < pf.size(); i++) {
      Object[] e = (Object[]) pf.get(i);
      String p = (String) e[0];
      if (p.length() > bestLen && id.startsWith(p)) { bestLen = p.length(); best = (long[]) e[1]; }
    }
    java.util.ArrayList sf = SFX;
    for (int i = 0; i < sf.size(); i++) {
      Object[] e = (Object[]) sf.get(i);
      String p = (String) e[0];
      if (p.length() > bestLen && id.endsWith(p)) { bestLen = p.length(); best = (long[]) e[1]; }
    }
  }
  if (best == null) best = NONE;
  CACHE.put(id, best);
  return best;
}""", cfg))
# the id rules match: the item id for a block (state variants share the base item), else the raw id without '*'/_State_ suffix
cfg.addMethod(CtNewMethod.make(f"""
public static String familyId({BTY} bt) {{
  try {{
    {ITM} it = bt.getItem();
    if (it != null) {{ String iid = it.getId(); if (iid != null && iid.length() > 0) return iid; }}
  }} catch (Throwable t) {{ }}
  String id = bt.getId();
  if (id == null) return null;
  if (id.startsWith("*")) id = id.substring(1);
  int s = id.indexOf("_State_");
  if (s > 0) id = id.substring(0, s);
  return id;
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static String stateOf({BTY} bt) {{
  try {{ return bt.getStateForBlock(bt.getId()); }} catch (Throwable t) {{ return null; }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static boolean hasFinalStage({BTY} bt) {{
  try {{
    {SDT} sd = bt.getState();
    if (sd == null) return false;
    java.util.Set names = sd.getStateNames();
    return names != null && names.contains("StageFinal");
  }} catch (Throwable t) {{ return false; }}
}}""", cfg))
# current block id at a position (world thread), "" for an unknown block, null when the section is not loaded.
# Same read path the engine uses in UseBlockInteraction.doInteraction / FarmingUtil.harvest (never loads a chunk).
cfg.addMethod(CtNewMethod.make(f"""
public static String blockIdAt({WLD} w, int x, int y, int z) {{
  try {{
    {CHS} cs = w.getChunkStore();
    if (cs == null) return null;
    {REF} sr = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (sr == null || !sr.isValid()) return null;
    {BSC} sec = ({BSC}) cs.getStore().getComponent(sr, {BSC}.getComponentType());
    if (sec == null) return null;
    {BTY} bt = ({BTY}) {BTY}.getAssetMap().getAsset(sec.get(x, y, z));
    if (bt == null) return "";
    String id = bt.getId();
    return id == null ? "" : id;
  }} catch (Throwable t) {{ return null; }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long scaled(long base) {
  if (base <= 0L) return 0L;
  double m = MULT;
  if (m == 1.0) return base;
  long v = Math.round(base * m);
  return v < 0L ? 0L : v;
}""", cfg))
# block break -> {skill, xp, placedCheck 1/0} or null (no XP)
cfg.addMethod(CtNewMethod.make(f"""
public static long[] classifyBreak({BTY} bt) {{
  if (bt == null) return null;
  long[] r = resolve(familyId(bt));
  if (r == null || r[0] < 0L || r[1] <= 0L) return null;
  boolean ripeCrop = hasFinalStage(bt);
  if (ripeCrop && NEED_RIPE && !"StageFinal".equals(stateOf(bt))) return null;
  long x = scaled(r[1]);
  if (x <= 0L) return null;
  return new long[] {{ r[0], x, ripeCrop ? 0L : 1L }};
}}""", cfg))
cfg.addMethod(CtNewMethod.make("""
public static long combatXp(String role, float maxHp) {
  if (role != null) {
    Long o = (Long) ROLE.get(role);
    if (o != null) return scaled(o.longValue());
    if (SEEN_ROLES.putIfAbsent(role, Boolean.TRUE) == null) info("combat: first kill of NPC role " + role + " (max health " + maxHp + ") - override with combat.role." + role + "=<xp>");
  }
  long x;
  if (maxHp > 0.0f) x = Math.round(maxHp * C_PER_HP); else x = C_DEFAULT;
  if (x < C_MIN) x = C_MIN;
  if (x > C_MAX) x = C_MAX;
  return scaled(x);
}""", cfg))

# ================= SkillStore: per-player XP, persistence, bridge =================
# data layout: long[8] = xp[0..3], paid level[4..7]
sto.addField(CtField.make("public static java.nio.file.Path DIR;", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap QUIET = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DIRTY = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", sto))
sto.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", sto))
sto.addField(CtField.make("public static final Object IO = new Object();", sto))
sto.addField(CtField.make("public static volatile long WARNED = 0L;", sto))
# player file -> {long[8] data, String name, Boolean quiet}. Runs WITHOUT any lock (no disk I/O under the SkillStore lock).
sto.addMethod(CtNewMethod.make(f"""
public static Object[] readFile(java.util.UUID u) {{
  long[] d = new long[8];
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) d[4 + i] = -1L;
  String nm = null;
  boolean quiet = false;
  try {{
    java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try {{ p.load(in); }} finally {{ in.close(); }}
      for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
        String n = {PKG}.SkillDefs.NAMES[i];
        try {{ String v = p.getProperty(n); if (v != null) d[i] = Math.max(0L, Long.parseLong(v.trim())); }} catch (Throwable t) {{ }}
        try {{ String v = p.getProperty(n + ".paid"); if (v != null) d[4 + i] = Long.parseLong(v.trim()); }} catch (Throwable t) {{ d[4 + i] = -1L; }}
      }}
      String s = p.getProperty("name");
      if (s != null && s.trim().length() > 0) nm = s.trim();
      quiet = "true".equalsIgnoreCase(String.valueOf(p.getProperty("quiet")).trim());
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load skills for " + u + ": " + t); }}
  // no paid marker yet -> current level counts as paid (no retroactive rewards)
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) if (d[4 + i] < 0L) d[4 + i] = (long) {PKG}.SkillDefs.levelOf(d[i]);
  return new Object[] {{ d, nm, Boolean.valueOf(quiet) }};
}}""", sto))
# cached data; a first load reads the file BEFORE taking the lock, the lock only decides whose copy is installed
sto.addMethod(CtNewMethod.make(f"""
public static long[] data(java.util.UUID u) {{
  long[] d = (long[]) DATA.get(u);
  if (d != null) return d;
  Object[] got = readFile(u);
  synchronized ({PKG}.SkillStore.class) {{
    d = (long[]) DATA.get(u);
    if (d == null) {{
      d = (long[]) got[0];
      if (got[1] != null) NAMES.putIfAbsent(u, got[1]);
      if (((Boolean) got[2]).booleanValue()) QUIET.put(u, Boolean.TRUE);
      DATA.put(u, d);
    }}
  }}
  return d;
}}""", sto))
# element read/write under the SkillStore lock (keeps snap() consistent with add() and payOwed())
sto.addMethod(CtNewMethod.make("""
public static synchronized long rd(long[] d, int i) {
  return d[i];
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static synchronized void wr(long[] d, int i, long v) {
  d[i] = v;
}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.Properties snap(java.util.UUID u) {{
  long[] d = (long[]) DATA.get(u);
  if (d == null) return null;
  java.util.Properties p = new java.util.Properties();
  String nm = (String) NAMES.get(u);
  if (nm != null) p.setProperty("name", nm);
  p.setProperty("quiet", QUIET.containsKey(u) ? "true" : "false");
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    p.setProperty({PKG}.SkillDefs.NAMES[i], String.valueOf(d[i]));
    p.setProperty({PKG}.SkillDefs.NAMES[i] + ".paid", String.valueOf(d[4 + i]));
  }}
  return p;
}}""", sto))
# snapshot under the SkillStore lock, write outside it; IO keeps two saves of the same file (ticker + shutdown) ordered
sto.addMethod(CtNewMethod.make(f"""
public static void saveNow(java.util.UUID u) {{
  try {{
    java.util.Properties p = snap(u);
    if (p == null) return;
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
    java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
    try {{ p.store(out, "SkyySkills"); }} finally {{ out.close(); }}
    java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not save skills for " + u + ": " + t); }}
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  synchronized (IO) { saveNow(u); }
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void flushDirty() {
  java.util.Iterator it = DIRTY.keySet().iterator();
  while (it.hasNext()) {
    java.util.UUID u = (java.util.UUID) it.next();
    it.remove();
    save(u);
  }
}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static int level(java.util.UUID u, int skill) {{
  if (skill < 0 || skill >= {PKG}.SkillDefs.N) return 0;
  return {PKG}.SkillDefs.levelOf(data(u)[skill]);
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static String levelsString(java.util.UUID u) {{
  long[] d = data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    if (i > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.NAMES[i]).append(':').append({PKG}.SkillDefs.levelOf(d[i]));
  }}
  return sb.toString();
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static void publish(java.util.UUID u) {
  try {
    bridge().put("skill:" + u.toString(), levelsString(u));
    PUBLISHED.put(u, Boolean.TRUE);
  } catch (Throwable t) { }
}""", sto))
# world thread: load a player's file and publish it (handed over by publishOnline, FlushTask pattern)
pub.addInterface(pool.get("java.lang.Runnable"))
pub.addField(CtField.make("public java.util.UUID u;", pub))
pub.addConstructor(CtNewConstructor.make("public PublishTask(java.util.UUID u) { this.u = u; }", pub))
pub.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    {PKG}.SkillStore.data(this.u);
    {PKG}.SkillStore.publish(this.u);
  }} catch (Throwable t) {{ }}
}}""", pub))
# scheduler thread (shared, single thread): memory only. Players not loaded yet go to their world thread.
sto.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (PUBLISHED.containsKey(u)) continue;
      try {{ String n = pr.getUsername(); if (n != null) NAMES.put(u, n); }} catch (Throwable t) {{ }}
      if (DATA.containsKey(u)) {{ publish(u); continue; }}
      try {{
        {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
        if (w != null) w.execute(new {PKG}.PublishTask(u));
      }} catch (Throwable t) {{ }}
    }}
    PUBLISHED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", sto))
# add xp; returns {{oldLevel, newLevel, total}}. The paid marker is NOT touched here (payOwed moves it after a real payout).
sto.addMethod(CtNewMethod.make("""
public static synchronized long[] bump(long[] d, int skill, long amount) {
  long before = d[skill];
  long after = before + amount;
  if (after < before) after = Long.MAX_VALUE;
  d[skill] = after;
  return new long[] { before, after };
}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static long[] add(java.util.UUID u, String name, int skill, long amount) {{
  long[] d = data(u);
  long[] ba = bump(d, skill, amount);
  if (name != null) NAMES.put(u, name);
  DIRTY.put(u, Boolean.TRUE);
  return new long[] {{ (long) {PKG}.SkillDefs.levelOf(ba[0]), (long) {PKG}.SkillDefs.levelOf(ba[1]), ba[1] }};
}}""", sto))
# true only when SkyyCoins really paid (its add fn returns the new balance, or null when nothing was changed)
sto.addMethod(CtNewMethod.make(f"""
public static boolean coinsAdd(java.util.UUID u, long n) {{
  Object f = null;
  try {{
    f = bridge().get("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] {{ u, Long.valueOf(n) }});
    if (r instanceof Number) return true;
  }} catch (Throwable t) {{ }}
  long now = System.currentTimeMillis();
  if (f != null && now - WARNED > 60000L) {{
    WARNED = now;
    {PKG}.SkillCfg.warn("coins:fn:add did not pay " + n + " coins to " + u + " - that level reward stays owed and is retried on the next XP gain");
  }}
  return false;
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static boolean owes(java.util.UUID u, int skill) {{
  long[] d = data(u);
  return rd(d, 4 + skill) < (long) {PKG}.SkillDefs.levelOf(rd(d, skill));
}}""", sto))
# pay every owed level of one skill, lowest first; the paid marker only moves past a level whose coins really arrived.
# Caller holds the player's own lock (his data array), never the global one, while SkyyCoins writes its file.
# -> {{first paid level (-1 none), last, coins sum, perLevel, changed 1/0}}; payOwed returns null when nothing was paid
sto.addMethod(CtNewMethod.make(f"""
public static long[] payLocked(java.util.UUID u, int skill, long[] d) {{
  long first = -1L;
  long last = -1L;
  long sum = 0L;
  long per = {PKG}.SkillCfg.COINS_PER_LEVEL;
  long changed = 0L;
  int lv = {PKG}.SkillDefs.levelOf(rd(d, skill));
  boolean stop = false;
  while (!stop && rd(d, 4 + skill) < (long) lv) {{
    long next = rd(d, 4 + skill) + 1L;
    long coins = per * next;
    if (per <= 0L || coins / next != per) {{
      wr(d, 4 + skill, next);
      changed = 1L;
    }} else if (coinsAdd(u, coins)) {{
      wr(d, 4 + skill, next);
      changed = 1L;
      if (first < 0L) first = next;
      last = next;
      sum += coins;
    }} else {{
      stop = true;
    }}
  }}
  return new long[] {{ first, last, sum, per, changed }};
}}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] payGuarded(java.util.UUID u, int skill, long[] d) {
  synchronized (d) { return payLocked(u, skill, d); }
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static long[] payOwed(java.util.UUID u, int skill) {
  long[] d = data(u);
  long[] res = payGuarded(u, skill, d);
  if (res == null) return null;
  if (res[4] != 0L) DIRTY.put(u, Boolean.TRUE);
  if (res[0] < 0L) return null;
  return res;
}""", sto))
sto.addMethod(CtNewMethod.make("""
public static boolean toggleQuiet(java.util.UUID u) {
  data(u);
  boolean q;
  if (QUIET.remove(u) != null) q = false; else { QUIET.put(u, Boolean.TRUE); q = true; }
  DIRTY.put(u, Boolean.TRUE);
  return q;
}""", sto))

# ================= SkillFn: bridge skill:fn:level =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public SkillFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    int i = {PKG}.SkillDefs.indexOf(String.valueOf(a[1]));
    if (i < 0) return Integer.valueOf(0);
    return Integer.valueOf({PKG}.SkillStore.level((java.util.UUID) a[0], i));
  }} catch (Throwable t) {{ return Integer.valueOf(0); }}
}}""", fn))

# ================= SkillMsg: throttled "+12 Mining XP (340/500)" =================
msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();", msg))
msg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();", msg))
msg.addMethod(CtNewMethod.make(f"""
public static synchronized String take(java.util.UUID u) {{
  long[] p = (long[]) PEND.get(u);
  if (p == null) return null;
  long[] d = {PKG}.SkillStore.data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < p.length; i++) {{
    if (p[i] <= 0L) continue;
    if (sb.length() > 0) sb.append("    ");
    sb.append("+").append({PKG}.SkillDefs.fmt(p[i])).append(" ").append({PKG}.SkillDefs.NAMES[i]).append(" XP (").append({PKG}.SkillDefs.progress(d[i])).append(")");
  }}
  PEND.remove(u);
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  return sb.length() == 0 ? null : sb.toString();
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static void send({PR} pr) {{
  try {{
    String s = take(pr.getUuid());
    if (s != null) pr.sendMessage({MSG}.raw(s).color("#9fd8ff"));
  }} catch (Throwable t) {{ }}
}}""", msg))
msg.addMethod(CtNewMethod.make(f"""
public static void note({PR} pr, int skill, long amount) {{
  if (!{PKG}.SkillCfg.FEEDBACK) return;
  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillStore.QUIET.containsKey(u)) return;
  boolean due;
  synchronized ({PKG}.SkillMsg.class) {{
    long[] p = (long[]) PEND.get(u);
    if (p == null) {{ p = new long[{PKG}.SkillDefs.N]; PEND.put(u, p); }}
    p[skill] += amount;
    Long last = (Long) LAST.get(u);
    due = last == null || System.currentTimeMillis() - last.longValue() >= {PKG}.SkillCfg.FEEDBACK_MS;
  }}
  if (due) send(pr);
}}""", msg))

fl.addInterface(pool.get("java.lang.Runnable"))
fl.addField(CtField.make("public java.util.UUID u;", fl))
fl.addConstructor(CtNewConstructor.make("public FlushTask(java.util.UUID u) { this.u = u; }", fl))
fl.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) {{ {PKG}.SkillMsg.PEND.remove(this.u); return; }}
    {PKG}.SkillMsg.send(pr);
  }} catch (Throwable t) {{ }}
}}""", fl))
# scheduler thread: hand leftover feedback to each player's world thread
msg.addMethod(CtNewMethod.make(f"""
public static void flushDue() {{
  try {{
    long now = System.currentTimeMillis();
    java.util.Iterator it = new java.util.ArrayList(PEND.keySet()).iterator();
    while (it.hasNext()) {{
      java.util.UUID u = (java.util.UUID) it.next();
      Long last = (Long) LAST.get(u);
      if (last != null && now - last.longValue() < {PKG}.SkillCfg.FEEDBACK_MS) continue;
      {PR} pr = {UNI}.get().getPlayer(u);
      if (pr == null || !pr.isValid()) {{ PEND.remove(u); LAST.remove(u); continue; }}
      {WLD} w = {UNI}.get().getWorld(pr.getWorldUuid());
      if (w == null) continue;
      LAST.put(u, Long.valueOf(now));
      try {{ w.execute(new {PKG}.FlushTask(u)); }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ }}
}}""", msg))

# ================= SkillXp: award + level-up (world thread) =================
xp.addMethod(CtNewMethod.make(f"""
public static boolean creative({ST} st, {REF} r) {{
  if ({PKG}.SkillCfg.CREATIVE) return false;
  try {{
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    return p != null && p.getGameMode() == {GM}.Creative;
  }} catch (Throwable t) {{ return false; }}
}}""", xp))
xp.addMethod(CtNewMethod.make(f"""
public static void gain({PR} pr, int skill, long amount) {{
  if (pr == null || amount <= 0L || skill < 0 || skill >= {PKG}.SkillDefs.N) return;
  java.util.UUID u = pr.getUuid();
  String name = null;
  try {{ name = pr.getUsername(); }} catch (Throwable t) {{ }}
  long[] r = {PKG}.SkillStore.add(u, name, skill, amount);
  {PKG}.SkillMsg.note(pr, skill, amount);
  long[] paid = null;
  if ({PKG}.SkillStore.owes(u, skill)) paid = {PKG}.SkillStore.payOwed(u, skill);
  String sk = {PKG}.SkillDefs.NAMES[skill];
  long shown = 0L;
  if (r[1] > r[0]) {{
    {PKG}.SkillMsg.send(pr);
    for (long lv = r[0] + 1L; lv <= r[1]; lv++) {{
      String reward = "";
      if (paid != null && lv >= paid[0] && lv <= paid[1]) {{
        long coins = paid[3] * lv;
        shown += coins;
        reward = "   +" + {PKG}.SkillDefs.fmt(coins) + " coins";
      }}
      pr.sendMessage({MSG}.raw("SKILL LEVEL UP  " + sk + " " + (lv - 1L) + " -> " + lv + reward).color("#ffc800"));
    }}
    long need = {PKG}.SkillDefs.needFor(r[2]);
    pr.sendMessage({MSG}.raw(need > 0L ? "  next: " + sk + " " + (r[1] + 1L) + " at " + {PKG}.SkillDefs.progress(r[2]) + " XP - /skills" : "  " + sk + " is now MAX level!").color("#c8b070"));
    {PKG}.SkillStore.publish(u);
  }}
  if (paid != null && paid[2] > shown) pr.sendMessage({MSG}.raw("[Skills] +" + {PKG}.SkillDefs.fmt(paid[2] - shown) + " coins for earlier " + sk + " level ups that could not be paid at the time").color("#ffc800"));
}}""", xp))

# ================= PlacedStore: positions of player-placed blocks, per world =================
plc.addField(CtField.make("public static java.nio.file.Path DIR;", plc))
plc.addField(CtField.make("public static final int CAP = 400000;", plc))
plc.addField(CtField.make("public static final java.util.HashMap WORLDS = new java.util.HashMap();", plc))
plc.addField(CtField.make("public static final java.util.HashSet DIRTY = new java.util.HashSet();", plc))
plc.addMethod(CtNewMethod.make("""
public static long key(int x, int y, int z) {
  return ((((long) x) & 67108863L) << 38) | ((((long) z) & 67108863L) << 12) | (((long) y) & 4095L);
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static String fileName(String w) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < w.length(); i++) {
    char c = w.charAt(i);
    sb.append(Character.isLetterOrDigit(c) || c == '-' || c == '_' ? c : '_');
  }
  return sb.toString() + ".bin";
}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.LinkedHashSet set(String w) {{
  java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
  if (s != null) return s;
  s = new java.util.LinkedHashSet();
  try {{
    java.nio.file.Path f = DIR.resolve(fileName(w));
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {{
      java.io.DataInputStream in = new java.io.DataInputStream(new java.io.BufferedInputStream(java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0])));
      try {{
        int n = in.readInt();
        for (int i = 0; i < n; i++) s.add(Long.valueOf(in.readLong()));
      }} finally {{ in.close(); }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not load placed blocks for " + w + ": " + t); }}
  WORLDS.put(w, s);
  return s;
}}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized void add(String w, long k) {
  java.util.LinkedHashSet s = set(w);
  Long v = Long.valueOf(k);
  s.remove(v);
  s.add(v);
  if (s.size() > CAP) { java.util.Iterator it = s.iterator(); it.next(); it.remove(); }
  DIRTY.add(w);
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized boolean remove(String w, long k) {
  boolean r = set(w).remove(Long.valueOf(k));
  if (r) DIRTY.add(w);
  return r;
}""", plc))
plc.addMethod(CtNewMethod.make("""
public static synchronized void snapshot(java.util.ArrayList names, java.util.ArrayList snaps) {
  java.util.Iterator it = DIRTY.iterator();
  while (it.hasNext()) {
    String w = (String) it.next();
    java.util.LinkedHashSet s = (java.util.LinkedHashSet) WORLDS.get(w);
    if (s != null) {
      long[] a = new long[s.size()];
      int i = 0;
      java.util.Iterator si = s.iterator();
      while (si.hasNext() && i < a.length) { a[i] = ((Long) si.next()).longValue(); i++; }
      names.add(w); snaps.add(a);
    }
  }
  DIRTY.clear();
}""", plc))
plc.addMethod(CtNewMethod.make(f"""
public static void flush() {{
  java.util.ArrayList names = new java.util.ArrayList();
  java.util.ArrayList snaps = new java.util.ArrayList();
  snapshot(names, snaps);
  for (int j = 0; j < names.size(); j++) {{
    String w = (String) names.get(j);
    long[] a = (long[]) snaps.get(j);
    try {{
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = DIR.resolve(fileName(w) + ".tmp");
      java.io.DataOutputStream out = new java.io.DataOutputStream(new java.io.BufferedOutputStream(java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0])));
      try {{
        out.writeInt(a.length);
        for (int i = 0; i < a.length; i++) out.writeLong(a[i]);
      }} finally {{ out.close(); }}
      java.nio.file.Files.move(tmp, DIR.resolve(fileName(w)), new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
    }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not save placed blocks for " + w + ": " + t); }}
  }}
}}""", plc))

# ================= HarvestGate: one pending harvest check per block, one payout per block per harvestCooldownMs =================
hg.addField(CtField.make("public static final java.util.HashMap LAST = new java.util.HashMap();", hg))
hg.addField(CtField.make("public static final java.util.HashMap PENDING = new java.util.HashMap();", hg))
hg.addMethod(CtNewMethod.make("""
public static String id(String w, long k) {
  return w + "|" + k;
}""", hg))
hg.addMethod(CtNewMethod.make("""
public static void prune(java.util.HashMap m, long now, long keep) {
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) { Long t = (Long) it.next(); if (now - t.longValue() >= keep) it.remove(); }
}""", hg))
hg.addMethod(CtNewMethod.make("""
public static synchronized boolean claim(String w, long k, long now, long gap) {
  String id = id(w, k);
  Long t = (Long) LAST.get(id);
  if (t != null && now - t.longValue() < gap) return false;
  LAST.put(id, Long.valueOf(now));
  if (LAST.size() > 20000) prune(LAST, now, gap);
  return true;
}""", hg))
# a pending entry older than 10 s is stale (its task died with a world), so it never blocks a block forever
hg.addMethod(CtNewMethod.make("""
public static synchronized boolean begin(String w, long k, long now) {
  String id = id(w, k);
  Long t = (Long) PENDING.get(id);
  if (t != null && now - t.longValue() < 10000L) return false;
  PENDING.put(id, Long.valueOf(now));
  if (PENDING.size() > 5000) prune(PENDING, now, 10000L);
  return true;
}""", hg))
hg.addMethod(CtNewMethod.make("""
public static synchronized void end(String w, long k) {
  PENDING.remove(id(w, k));
}""", hg))

# ================= deferred tasks (run on the world thread after every system saw the event) =================
btk.addInterface(pool.get("java.lang.Runnable"))
btk.addField(CtField.make(f"public {BBE} ev;", btk))
btk.addField(CtField.make("public java.util.UUID u;", btk))
btk.addField(CtField.make("public String world;", btk))
btk.addField(CtField.make("public long[] rule;", btk))
btk.addConstructor(CtNewConstructor.make(f"""
public BreakTask({BBE} ev, java.util.UUID u, String world, long[] rule) {{
  this.ev = ev; this.u = u; this.world = world; this.rule = rule;
}}""", btk))
btk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    boolean wasPlaced = false;
    if ({PKG}.SkillCfg.IGNORE_PLACED) {{
      {V3I} t = this.ev.getTargetBlock();
      if (t != null) wasPlaced = {PKG}.PlacedStore.remove(this.world, {PKG}.PlacedStore.key(t.x(), t.y(), t.z()));
    }}
    if (this.rule == null) return;
    if (wasPlaced && this.rule[2] == 1L) return;
    if (this.rule[2] == 0L) {{
      {V3I} c = this.ev.getTargetBlock();
      if (c != null && !{PKG}.HarvestGate.claim(this.world, {PKG}.PlacedStore.key(c.x(), c.y(), c.z()), System.currentTimeMillis(), {PKG}.SkillCfg.HARVEST_GATE_MS)) return;
    }}
    {PR} pr = {UNI}.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("break award failed: " + t); }}
}}""", btk))

ptk.addInterface(pool.get("java.lang.Runnable"))
ptk.addField(CtField.make(f"public {PBE} ev;", ptk))
ptk.addField(CtField.make("public String world;", ptk))
ptk.addConstructor(CtNewConstructor.make(f"public PlaceTask({PBE} ev, String world) {{ this.ev = ev; this.world = world; }}", ptk))
ptk.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.ev.isCancelled()) return;
    {V3I} t = this.ev.getTargetBlock();
    if (t == null) return;
    {PKG}.PlacedStore.add(this.world, {PKG}.PlacedStore.key(t.x(), t.y(), t.z()));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("place record failed: " + t); }}
}}""", ptk))

# F-harvest verification (world thread): pay only once the block at the position is no longer the ripe block the player used.
# UseBlockEvent.Post fires before the pushed HarvestCrop root runs and also when it fails, so poll: next tick, then every
# 100 ms (scheduler hop -> world.execute, FlushTask pattern) for up to 20 retries; still ripe after that = no harvest, no XP.
htk.addInterface(pool.get("java.lang.Runnable"))
htk.addField(CtField.make("public java.util.UUID u;", htk))
htk.addField(CtField.make(f"public {WLD} w;", htk))
htk.addField(CtField.make("public String wn;", htk))
htk.addField(CtField.make("public int x;", htk))
htk.addField(CtField.make("public int y;", htk))
htk.addField(CtField.make("public int z;", htk))
htk.addField(CtField.make("public String ripe;", htk))
htk.addField(CtField.make("public long amount;", htk))
htk.addField(CtField.make("public int tries;", htk))
htk.addField(CtField.make("public boolean hop;", htk))
htk.addConstructor(CtNewConstructor.make(f"""
public HarvestTask(java.util.UUID u, {WLD} w, String wn, int x, int y, int z, String ripe, long amount) {{
  this.u = u; this.w = w; this.wn = wn; this.x = x; this.y = y; this.z = z; this.ripe = ripe; this.amount = amount;
  this.tries = 0; this.hop = false;
}}""", htk))
htk.addMethod(CtNewMethod.make(f"""
public void run() {{
  long k = {PKG}.PlacedStore.key(this.x, this.y, this.z);
  if (this.hop) {{
    this.hop = false;
    try {{ this.w.execute(this); }} catch (Throwable t) {{ {PKG}.HarvestGate.end(this.wn, k); }}
    return;
  }}
  try {{
    String cur = {PKG}.SkillCfg.blockIdAt(this.w, this.x, this.y, this.z);
    if (cur == null) {{ {PKG}.HarvestGate.end(this.wn, k); return; }}
    if (!cur.equals(this.ripe)) {{
      {PKG}.HarvestGate.end(this.wn, k);
      if (!{PKG}.HarvestGate.claim(this.wn, k, System.currentTimeMillis(), {PKG}.SkillCfg.HARVEST_GATE_MS)) return;
      {PR} pr = {UNI}.get().getPlayer(this.u);
      if (pr == null || !pr.isValid()) return;
      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
      return;
    }}
    this.tries++;
    if (this.tries > 20) {{ {PKG}.HarvestGate.end(this.wn, k); return; }}
    this.hop = true;
    {HSV}.SCHEDULED_EXECUTOR.schedule(this, 100L, java.util.concurrent.TimeUnit.MILLISECONDS);
  }} catch (Throwable t) {{
    {PKG}.HarvestGate.end(this.wn, k);
    {PKG}.SkillCfg.warn("harvest award failed: " + t);
  }}
}}""", htk))

# ================= ECS systems =================
def event_system(cls, ctor_name, event_cls, body):
    cls.addConstructor(CtNewConstructor.make(f"public {ctor_name}() {{ super({event_cls}.class); }}", cls))
    cls.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return com.hypixel.hytale.component.Archetype.empty();
}}""", cls))
    cls.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
{body}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("{ctor_name} failed: " + t); }}
}}""", cls))

event_system(bsy, "BreakSys", BBE, f"""
    {BBE} e = ({BBE}) ev;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    long[] rule = {PKG}.SkillCfg.classifyBreak(e.getBlockType());
    if (rule != null && {PKG}.SkillXp.creative(st, r)) rule = null;
    if (rule == null && !{PKG}.SkillCfg.IGNORE_PLACED) return;
    w.execute(new {PKG}.BreakTask(e, pr.getUuid(), w.getName(), rule));""")

event_system(psy, "PlaceSys", PBE, f"""
    if (!{PKG}.SkillCfg.IGNORE_PLACED) return;
    {PBE} e = ({PBE}) ev;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    w.execute(new {PKG}.PlaceTask(e, w.getName()));""")

# F-harvest of a ripe crop (eternal crops, berry bushes): UseBlockEvent.Post is not cancellable and is NOT proof of a harvest
# (fires before the HarvestCrop root runs, and also when it fails) -> HarvestTask verifies the block really changed.
event_system(usy, "HarvestSys", UBP, f"""
    {UBE} e = ({UBE}) ev;
    {BTY} bt = e.getBlockType();
    if (bt == null) return;
    if (!"StageFinal".equals({PKG}.SkillCfg.stateOf(bt))) return;
    {BGA} g = bt.getGathering();
    if (g == null || g.getHarvest() == null) return;
    long[] rr = {PKG}.SkillCfg.resolve({PKG}.SkillCfg.familyId(bt));
    if (rr == null || rr[0] != (long) {PKG}.SkillDefs.FARMING || rr[1] <= 0L) return;
    long amt = {PKG}.SkillCfg.scaled(rr[1]);
    String ripe = bt.getId();
    {V3I} tb = e.getTargetBlock();
    if (amt <= 0L || ripe == null || tb == null) return;
    {REF} r = chunk.getReferenceTo(idx);
    if (r == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null || {PKG}.SkillXp.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof {EST})) return;
    {WLD} w = (({EST}) ext).getWorld();
    if (w == null) return;
    String wn = w.getName();
    int bx = tb.x();
    int by = tb.y();
    int bz = tb.z();
    if (!{PKG}.HarvestGate.begin(wn, {PKG}.PlacedStore.key(bx, by, bz), System.currentTimeMillis())) return;
    w.execute(new {PKG}.HarvestTask(pr.getUuid(), w, wn, bx, by, bz, ripe, amt));""")

# Combat: DeathComponent added to an NPC killed by a player
ksy.addConstructor(CtNewConstructor.make("public KillSys() { super(); }", ksy))
ksy.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return com.hypixel.hytale.component.Archetype.empty();
}}""", ksy))
ksy.addMethod(CtNewMethod.make(f"""
public void onComponentAdded({REF} r, {CMP} c, {ST} s, {CB} b) {{
  try {{
    if (r == null || !(c instanceof {DTH})) return;
    {NPC} npc = ({NPC}) s.getComponent(r, {NPC}.getComponentType());
    if (npc == null) return;
    {DMG} d = (({DTH}) c).getDeathInfo();
    if (d == null) return;
    Object src = d.getSource();
    if (!(src instanceof {DES})) return;
    {REF} k = (({DES}) src).getRef();
    if (k == null || !k.isValid() || k.getStore() != s) return;
    {PR} pr = ({PR}) s.getComponent(k, {PR}.getComponentType());
    if (pr == null || !pr.isValid()) return;
    if ({PKG}.SkillXp.creative(s, k)) return;
    float maxHp = -1.0f;
    try {{
      {ESM} sm = ({ESM}) s.getComponent(r, {ESM}.getComponentType());
      if (sm != null) {{ {ESV} hv = sm.get({DST}.getHealth()); if (hv != null) maxHp = hv.getMax(); }}
    }} catch (Throwable t) {{ }}
    String role = null;
    try {{ role = npc.getRoleName(); }} catch (Throwable t) {{ }}
    {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.COMBAT, {PKG}.SkillCfg.combatXp(role, maxHp));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("kill handler failed: " + t); }}
}}""", ksy))

# ================= leaderboard =================
tcm.addInterface(pool.get("java.util.Comparator"))
tcm.addConstructor(CtNewConstructor.make("public TopCmp() { }", tcm))
tcm.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {
  long x = ((Long) ((Object[]) a)[1]).longValue();
  long y = ((Long) ((Object[]) b)[1]).longValue();
  if (x != y) return x > y ? -1 : 1;
  return String.valueOf(((Object[]) a)[0]).compareToIgnoreCase(String.valueOf(((Object[]) b)[0]));
}""", tcm))
top.addField(CtField.make("public static final long[] AT = new long[4];", top))
top.addField(CtField.make("public static final Object[] CACHE = new Object[4];", top))
# rows: Object[]{name, Long xp, uuidString}, sorted, all players on disk + in memory; cached 30s
top.addMethod(CtNewMethod.make(f"""
public static synchronized java.util.ArrayList all(int skill) {{
  long now = System.currentTimeMillis();
  if (CACHE[skill] != null && now - AT[skill] < 30000L) return (java.util.ArrayList) CACHE[skill];
  java.util.HashMap m = new java.util.HashMap();
  try {{
    java.io.File[] fs = {PKG}.SkillStore.DIR.toFile().listFiles();
    if (fs != null) for (int i = 0; i < fs.length; i++) {{
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties")) continue;
      String us = fn.substring(0, fn.length() - 11);
      try {{
        java.util.Properties p = new java.util.Properties();
        java.io.InputStream in = new java.io.FileInputStream(fs[i]);
        try {{ p.load(in); }} finally {{ in.close(); }}
        long x = 0L;
        try {{ x = Long.parseLong(String.valueOf(p.getProperty({PKG}.SkillDefs.NAMES[skill], "0")).trim()); }} catch (Throwable t) {{ }}
        String nm = p.getProperty("name");
        m.put(us, new Object[] {{ nm == null ? us.substring(0, 8) : nm, Long.valueOf(x), us }});
      }} catch (Throwable t) {{ }}
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("leaderboard scan failed: " + t); }}
  java.util.Iterator it = {PKG}.SkillStore.DATA.entrySet().iterator();
  while (it.hasNext()) {{
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    java.util.UUID u = (java.util.UUID) e.getKey();
    long[] d = (long[]) e.getValue();
    String nm = (String) {PKG}.SkillStore.NAMES.get(u);
    m.put(u.toString(), new Object[] {{ nm == null ? u.toString().substring(0, 8) : nm, Long.valueOf(d[skill]), u.toString() }});
  }}
  java.util.ArrayList rows = new java.util.ArrayList(m.values());
  java.util.Collections.sort(rows, new {PKG}.TopCmp());
  CACHE[skill] = rows; AT[skill] = now;
  return rows;
}}""", top))
top.addMethod(CtNewMethod.make("""
public static int rankOf(java.util.ArrayList rows, java.util.UUID u) {
  String s = u.toString();
  for (int i = 0; i < rows.size(); i++) if (s.equals(((Object[]) rows.get(i))[2])) return i + 1;
  return 0;
}""", top))

# ================= /skills page (inline, TextButtons; syntax copied from AccPage / SacksPage) =================
BARW = 400
page.addField(CtField.make("public int view;", page))
page.addConstructor(CtNewConstructor.make(f"""
public SkillsPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.view = -1;
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  String bs = "Style: TextButtonStyle(Default: (Background: #27463a, LabelStyle: (FontSize: 12, TextColor: #dcffe8, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3b6b54, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #172a22, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySkills {{ Anchor: (Width: 640, Height: 480); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySkills", "Group {{ Anchor: (Height: 2); Background: #9fe0a0; }}");
  if (this.view < 0 || this.view >= {PKG}.SkillDefs.N) {{
    int sum = 0;
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) sum += {PKG}.SkillDefs.levelOf(d[i]);
    long avg10 = Math.round(sum * 10.0 / {PKG}.SkillDefs.N);
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\"Skills\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6fff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\"" + safe("Skill average " + (avg10 / 10L) + "." + (avg10 % 10L) + " - every level up pays coins") + "\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 6); Text: \\"\\"; }}");
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      long total = d[i];
      int lv = {PKG}.SkillDefs.levelOf(total);
      long cur = {PKG}.SkillDefs.intoLevel(total);
      long need = {PKG}.SkillDefs.needFor(total);
      int fill = need > 0L ? (int) ({BARW}L * cur / need) : {BARW};
      if (fill < 0) fill = 0;
      if (fill > {BARW}) fill = {BARW};
      String prog = need > 0L ? ({PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1)) : ("MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP");
      String col = {PKG}.SkillDefs.COLORS[i];
      b.appendInline("#SkyySkills", "Group #SkyySkRow" + i + " {{ Anchor: (Height: 72); LayoutMode: Left; Padding: (Top: 6); Background: #142030(0.9); }}");
      b.appendInline("#SkyySkRow" + i, "Group {{ Anchor: (Width: 66, Height: 60); ItemIcon {{ Anchor: (Width: 48, Height: 48, Left: 10, Top: 4); ItemId: \\"" + {PKG}.SkillDefs.ICONS[i] + "\\"; }} }}");
      b.appendInline("#SkyySkRow" + i, "Group #SkyySkTxt" + i + " {{ Anchor: (Width: 420, Height: 60); LayoutMode: Top; }}");
      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 24); Text: \\"" + {PKG}.SkillDefs.NAMES[i] + "  " + lv + "\\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }}");
      b.appendInline("#SkyySkTxt" + i, "Group #SkyySkBar" + i + " {{ Anchor: (Width: {BARW}, Height: 12); Background: #22324a; }}");
      if (fill > 0) b.appendInline("#SkyySkBar" + i, "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 12); Background: " + col + "; }}");
      b.appendInline("#SkyySkTxt" + i, "Label {{ Anchor: (Height: 20); Text: \\"" + safe(prog) + "\\"; Style: (FontSize: 11, TextColor: #b8c8d8, VerticalAlignment: Center); }}");
      b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkTop" + i + " {{ Anchor: (Width: 100, Height: 30); Text: \\"Top 10\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyySkTop" + i, {EVD}.of("a", "sktop" + i));
      b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 6); Text: \\"\\"; }}");
    }}
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 18); Text: \\"Mine ores and stone - chop trees - harvest ripe crops - defeat monsters.  /skills quiet hides XP messages\\"; Style: (FontSize: 10, TextColor: #7f94a8, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
    return;
  }}
  int s = this.view;
  java.util.ArrayList rows = {PKG}.SkillTop.all(s);
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 30); Text: \\"" + safe("Top 10 - " + {PKG}.SkillDefs.NAMES[s]) + "\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + {PKG}.SkillDefs.COLORS[s] + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  int n = rows.size() < 10 ? rows.size() : 10;
  if (n == 0) b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 24); Text: \\"Nobody has any XP yet.\\"; Style: (FontSize: 12, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int i = 0; i < n; i++) {{
    Object[] e = (Object[]) rows.get(i);
    long x = ((Long) e[1]).longValue();
    boolean me = u.toString().equals(e[2]);
    String line = (i + 1) + ".   " + e[0] + "     Level " + {PKG}.SkillDefs.levelOf(x) + "     " + {PKG}.SkillDefs.fmt(x) + " XP";
    b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 26); Text: \\"" + safe(line) + "\\"; Style: (FontSize: 13, " + (me ? "RenderBold: true, TextColor: #ffe08a" : "TextColor: #e6f0ff") + ", VerticalAlignment: Center); }}");
  }}
  int rank = {PKG}.SkillTop.rankOf(rows, u);
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  b.appendInline("#SkyySkills", "Label {{ Anchor: (Height: 20); Text: \\"" + safe(rank > 0 ? "Your rank #" + rank + " of " + rows.size() + " - level " + {PKG}.SkillDefs.levelOf(d[s]) + " - " + {PKG}.SkillDefs.fmt(d[s]) + " XP" : "You are not ranked yet") + "\\"; Style: (FontSize: 12, TextColor: #c9dff0, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyySkills", "Group #SkyySkNav {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyySkNav", "Label {{ Anchor: (Width: 250, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyySkNav", "TextButton #SkyySkBack {{ Anchor: (Width: 106, Height: 30); Text: \\"Back\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyySkBack", {EVD}.of("a", "skback"));
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("sktop" + i + "\\"") >= 0) {{ this.view = i; rebuild(); return; }}
    }}
    if (data.indexOf("skback\\"") >= 0) {{ this.view = -1; rebuild(); return; }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("skills page event failed: " + t); }}
}}""", page))

# ================= commands =================
tcmd.addField(CtField.make(f"public {RA} skillArg;", tcmd))
tcmd.addConstructor(CtNewConstructor.make(f"""
public TopCmd() {{
  super("top", "Top 10 players of a skill: /skills top mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | combat", {ATY}.STRING);
}}""", tcmd))
tcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    int s = {PKG}.SkillDefs.indexOf(String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) {{ pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming or combat.")); return; }}
    java.util.ArrayList rows = {PKG}.SkillTop.all(s);
    pr.sendMessage({MSG}.raw("[Skills] Top 10 " + {PKG}.SkillDefs.NAMES[s] + ":").color("#ffc800"));
    int n = rows.size() < 10 ? rows.size() : 10;
    if (n == 0) pr.sendMessage({MSG}.raw("  nobody has any XP yet"));
    for (int i = 0; i < n; i++) {{
      Object[] e = (Object[]) rows.get(i);
      long x = ((Long) e[1]).longValue();
      pr.sendMessage({MSG}.raw("  " + (i + 1) + ". " + e[0] + " - level " + {PKG}.SkillDefs.levelOf(x) + " (" + {PKG}.SkillDefs.fmt(x) + " XP)"));
    }}
    int rank = {PKG}.SkillTop.rankOf(rows, pr.getUuid());
    if (rank > 10) pr.sendMessage({MSG}.raw("  you: #" + rank + " of " + rows.size()));
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("/skills top failed: " + t); pr.sendMessage({MSG}.raw("[Skills] could not read the leaderboard")); }}
}}""", tcmd))

qcmd.addConstructor(CtNewConstructor.make('public QuietCmd() { super("quiet", "Toggle the +XP chat messages (level ups always show)"); }', qcmd))
qcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  boolean q = {PKG}.SkillStore.toggleQuiet(pr.getUuid());
  pr.sendMessage({MSG}.raw(q ? "[Skills] XP messages hidden (level ups still show). /skills quiet again to show them." : "[Skills] XP messages shown."));
}}""", qcmd))

rcmd.addConstructor(CtNewConstructor.make('public ReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyySkills/xp.properties"); }', rcmd))
rcmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  if (!pr.hasPermission("skyyskills.admin")) {{ pr.sendMessage({MSG}.raw("[Skills] no permission (skyyskills.admin)")); return; }}
  pr.sendMessage({MSG}.raw("[Skills] xp.properties reloaded: " + {PKG}.SkillCfg.load()));
}}""", rcmd))

cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{
  super("skills", "Open your skills page; /skills top <skill>, /skills quiet");
  addAliases(new String[] {{ "skill" }});
  addSubCommand(new {PKG}.TopCmd());
  addSubCommand(new {PKG}.QuietCmd());
  addSubCommand(new {PKG}.ReloadCmd());
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.SkillsPage(pr));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not open the page: " + {PKG}.SkillStore.levelsString(pr.getUuid())));
  }}
}}""", cmd))

# ================= 1s ticker: feedback leftovers, bridge publish (5s), save (10s), placed blocks (60s) =================
tick.addInterface(pool.get("java.lang.Runnable"))
tick.addField(CtField.make("public long n;", tick))
tick.addConstructor(CtNewConstructor.make("public SkillTick() { this.n = 0L; }", tick))
tick.addMethod(CtNewMethod.make(f"""
public void run() {{
  this.n++;
  try {{ {PKG}.SkillMsg.flushDue(); }} catch (Throwable t) {{ }}
  if (this.n % 5L == 0L) {{ try {{ {PKG}.SkillStore.publishOnline(); }} catch (Throwable t) {{ }} }}
  if (this.n % 10L == 0L) {{ try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }} }}
  if (this.n % 60L == 0L) {{ try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }} }}
}}""", tick))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyySkillsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.SkillCfg.LOG = getLogger();
  java.nio.file.Path base = getDataDirectory().resolveSibling("Skyy_SkyySkills");
  {PKG}.SkillStore.DIR = base.resolve("players");
  {PKG}.PlacedStore.DIR = base.resolve("placed");
  {PKG}.SkillCfg.FILE = base.resolve("xp.properties");
  String rules = {PKG}.SkillCfg.load();
  getEntityStoreRegistry().registerSystem(new {PKG}.BreakSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.PlaceSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.HarvestSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.KillSys());
  getCommandRegistry().registerCommand(new {PKG}.SkillsCmd());
  {PKG}.SkillStore.bridge().put("skill:fn:level", new {PKG}.SkillFn());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.SkillTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyySkills] {VERSION} ready - /skills; xp rules: " + rules);
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{
  try {{ if (this.ticker != null) this.ticker.cancel(false); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.flushDirty(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.PlacedStore.flush(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SkillStore.bridge().remove("skill:fn:level"); }} catch (Throwable t) {{ }}
  super.shutdown();
}}""", pl))

for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)
m = B.manifest("SkyySkills", VERSION, "SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Combat to level 50. XP from breaking blocks, ripe crops and NPC kills; level ups pay SkyyCoins. /skills. Zero dependencies.", PKG + ".SkyySkillsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT, {})  # no assets: page built inline (see memory hytale-ui-rules)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyySkills.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyySkills" % VERSION, disable_prefix="Skyy:")
