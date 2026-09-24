"""SkyyAccessories 0.2 - build script (derived from 0.1 by tools/acc_0_2_patch.py - edit the patch, not this file)
0.2: STAT TALISMANS (Hypixel SkyBlock style) that work while they sit in the Accessory Bag, bag capacity 6 -> 9 (old bags keep their
     slots), "Talisman bonuses" summary line on the bag page. Items Skyy_Talisman_<Family>_<Talisman|Ring|Artifact>; one per family
     counts (same swap rule as the bench accessories). Effects: AccEffects (EntityTickingSystem on Player, world thread, 1 s per player):
     StaticModifier(MAX, ADDITIVE) keys skyyacc_health / skyyacc_stamina / skyyacc_mana, Regeneration = addStatValue(Health) every 2 s,
     Speed = MovementSettings.baseSpeed = default * (1 + bonus) + update(packetHandler) (EndgameAndQoL AccessoryPassiveSystem /
     RPGLeveling MovementSpeedHelper pattern: baseSpeed only) with a back-off when another mod keeps resetting it. Modifiers are removed
     as soon as the talisman leaves the bag. Bridge: acc:has:<uuid> = bench accessories in the bag (0.1 meaning, SkyySacks reads it),
     acc:tal:<uuid> = talismans in the bag, acc:fn:has = both.
     Review fixes: baseSpeed-only speed (no f*f compounding), unequip undoes exactly the baseSpeed we wrote, equip pre-checks the bag and
     hand-backs fall back to a free bag slot then a logged loss, per-player locks, talismans use the vanilla crystal fragment model.
0.1 notes:
SkyyAccessories 0.1 - build script (javassist via jpype). Accessory bag + bench accessories (Skyy's design 2026-09-23).
Run:   python build_skyyaccessories_0.1.py            -> SkyyAccessories/SkyyAccessories-0.1.jar
       python build_skyyaccessories_0.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Design (pattern copied from TerrariaAddons' AccessoryPouchSharedContainer: per-player container persisted to a file, opened from the
item's Secondary interaction; effects are checked, never "applied"):
 - Item Skyy_Accessory_Bag (Fieldcraft recipe): right-click -> page "SkyyAccBag" (/accessories or /acc also opens it).
   6 slots stored in Skyy_SkyyAccessories/bags/<uuid>.properties (slot0..slot5 = item id). Equip moves the item out of your
   inventory into the bag; Unequip gives it back (if your storage is full the item stays in the bag).
 - Bench accessories Skyy_Accessory_<BenchId>_T<n>: one per bench tier. T1 = the bench item + 4 copper bars at a Workbench;
   T(n+1) = T(n) + exactly the materials the real bench needs to upgrade to that tier (from the bench's TierLevels).
   Only one accessory per bench fits in the bag; equipping a higher tier hands the lower one back.
 - Bridge: "acc:has:<uuid>" -> "id,id" (what is in the bag) republished on every change and for every online player (5s tick);
   "acc:fn:has" -> java.util.function.Function apply(Object[]{UUID, String itemId}) -> Boolean. SkyySacks 0.6.1 reads acc:has to
   add a craft-page tab per bench accessory (recipes filtered by BenchRequirement.requiredTierLevel <= accessory tier).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.2"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
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
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IST = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction"
ISS = "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction"
OCU = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction"
# 0.2 stat / movement API (verified with reflect.py + TerrariaAddons bytecode, see tools/acc_0_2_patch.py)
ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
DST = "com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes"
MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
MTG = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
MMG = "com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager"
MVS = "com.hypixel.hytale.protocol.MovementSettings"
ETS = "com.hypixel.hytale.component.system.tick.EntityTickingSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
QRY = "com.hypixel.hytale.component.query.Query"
CRP = "com.hypixel.hytale.component.ComponentRegistryProxy"

for c, m in ((PLA, "getInventory"), (INV, "getStorage"), (INV, "getHotbar"), (INV, "getBackpack"), (IC, "getItemStack"), (IC, "removeItemStackFromSlot"),
             (IC, "addItemStack"), (IC, "getCapacity"), (OCU, "registerSimple"), (HSV, "SCHEDULED_EXECUTOR"), (UNI, "getPlayers"),
             (PAGE, "rebuild"), ("com.hypixel.hytale.server.core.plugin.PluginBase", "shutdown")):
    B.probe(pool, c, m)
for c, m in ((ESM, "getComponentType"), (ESM, "putModifier"), (ESM, "removeModifier"), (ESM, "getModifier"), (ESM, "addStatValue"), (ESM, "get"),
             (ESV, "get"), (ESV, "getMax"), (DST, "getHealth"), (DST, "getStamina"), (DST, "getMana"), (SMO, "getAmount"), (MTG, "MAX"),
             (CAL, "ADDITIVE"), (MMG, "getComponentType"), (MMG, "getSettings"), (MMG, "getDefaultSettings"), (MMG, "update"),
             (MVS, "baseSpeed"), (PR, "getPacketHandler"), (PLA, "isWaitingForClientReady"),
             (ETS, "tick"), (ACH, "getReferenceTo"), (CB, "getComponent"), (REF, "isValid"), (CRP, "registerSystem"),
             ("com.hypixel.hytale.server.core.plugin.PluginBase", "getEntityStoreRegistry")):
    B.probe(pool, c, m)

PKG = "com.skyy.accessories"
dfs  = pool.makeClass(PKG + ".AccDefs")
st_  = pool.makeClass(PKG + ".AccStore")
fn   = pool.makeClass(PKG + ".AccFn")
page = pool.makeClass(PKG + ".AccPage", pool.get(PAGE))
fac  = pool.makeClass(PKG + ".AccPageFactory")
cmd  = pool.makeClass(PKG + ".AccCmd", pool.get(APC))
tick = pool.makeClass(PKG + ".AccTick")
eff  = pool.makeClass(PKG + ".AccEffects", pool.get(ETS))
pl   = pool.makeClass(PKG + ".SkyyAccessoriesPlugin", pool.get(JP))

# (benchId, bench item id, display name, tiers, [upgrade materials to reach T2, T3, ...])
BENCHES = [
    ("Workbench",      "Bench_WorkBench", "Workbench",      3, [[("Ingredient_Bar_Copper", 30), ("Ingredient_Bar_Iron", 20), ("Ingredient_Fabric_Scrap_Linen", 20)],
                                                               [("Ingredient_Bar_Thorium", 30), ("Ingredient_Bar_Cobalt", 20), ("Ingredient_Leather_Heavy", 30), ("Ingredient_Fabric_Scrap_Shadoweave", 50), ("Ingredient_Fire_Essence", 25)]]),
    ("Armor_Bench",    "Bench_Armour",    "Armor Bench",    3, [[("Ingredient_Bar_Copper", 20), ("Ingredient_Bone_Fragment", 20), ("Ingredient_Leather_Medium", 20), ("Wood_Azure_Trunk", 100)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fabric_Scrap_Shadoweave", 40), ("Ingredient_Chitin_Sturdy", 40), ("Ingredient_Voidheart", 3)]]),
    ("Weapon_Bench",   "Bench_Weapon",    "Weapon Bench",   3, [[("Ingredient_Bar_Iron", 20), ("Ingredient_Leather_Light", 30), ("Ingredient_Fabric_Scrap_Linen", 30), ("Ingredient_Sac_Venom", 15)],
                                                               [("Ingredient_Bar_Thorium", 25), ("Ingredient_Bar_Cobalt", 25), ("Ingredient_Fire_Essence", 20), ("Ingredient_Ice_Essence", 40), ("Ingredient_Void_Essence", 100)]]),
    ("Alchemybench",   "Bench_Alchemy",   "Alchemy Bench",  4, [[("Ingredient_Bar_Silver", 5), ("Ingredient_Bar_Gold", 10), ("Ingredient_Sac_Venom", 10), ("Rock_Gem_Emerald", 1)],
                                                               [("Ingredient_Bar_Silver", 10), ("Ingredient_Bar_Gold", 20), ("Ingredient_Chitin_Sturdy", 20), ("Rock_Gem_Zephyr", 1)],
                                                               [("Ingredient_Bar_Silver", 20), ("Ingredient_Bar_Gold", 40), ("Ingredient_Fabric_Scrap_Shadoweave", 30), ("Rock_Gem_Sapphire", 1)]]),
    ("Farmingbench",   "Bench_Farming",   "Farming Bench",  7, [[("Ingredient_Life_Essence", 50), ("Plant_Crop_Wheat_Item", 5), ("Plant_Crop_Lettuce_Item", 5), ("Wood_Softwood_Trunk", 5)],
                                                               [("Ingredient_Life_Essence_Concentrated", 1), ("Plant_Crop_Carrot_Item", 10), ("Plant_Crop_Corn_Item", 10), ("Wood_Lightwood_Trunk", 10)],
                                                               [("Ingredient_Life_Essence_Concentrated", 2), ("Plant_Crop_Cauliflower_Item", 20), ("Plant_Crop_Turnip_Item", 20), ("Wood_Hardwood_Trunk", 20)],
                                                               [("Ingredient_Life_Essence_Concentrated", 3), ("Plant_Crop_Aubergine_Item", 30), ("Plant_Crop_Pumpkin_Item", 30), ("Wood_Drywood_Trunk", 30)],
                                                               [("Ingredient_Life_Essence_Concentrated", 4), ("Plant_Crop_Tomato_Item", 40), ("Plant_Crop_Chilli_Item", 40), ("Wood_Darkwood_Trunk", 40)],
                                                               [("Ingredient_Life_Essence_Concentrated", 5), ("Plant_Crop_Cotton_Item", 50), ("Plant_Crop_Rice_Item", 50), ("Wood_Redwood_Trunk", 50)]]),
    ("Furnace",        "Bench_Furnace",   "Furnace",        2, [[("Ingredient_Bar_Copper", 5), ("Ingredient_Bar_Iron", 5), ("Ingredient_Bar_Thorium", 5), ("Ingredient_Bar_Cobalt", 5)]]),
    ("Tannery",        "Bench_Tannery",   "Tannery",        2, [[("Ingredient_Leather_Light", 5), ("Ingredient_Leather_Medium", 5), ("Ingredient_Leather_Heavy", 5), ("Ingredient_Chitin_Sturdy", 5)]]),
    ("Arcanebench",    "Bench_Arcane",    "Arcane Bench",   1, []),
    ("Cookingbench",   "Bench_Cooking",   "Cooking Bench",  1, []),
    ("Furniture_Bench","Bench_Furniture", "Furniture Bench",1, []),
    ("Loombench",      "Bench_Loom",      "Loom",           1, []),
    ("Salvagebench",   "Bench_Salvage",   "Salvage Bench",  1, []),
    ("Campfire",       "Bench_Campfire",  "Campfire",       1, []),
]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
BAG = "Skyy_Accessory_Bag"
CAP = 9          # 0.2: 6 -> 9 (slot6..slot8 are simply empty in bags saved by 0.1)
INV_ROWS = 6     # accessories/talismans listed from the inventory (Equip buttons eq:0..eq:5)
PAGE_H = 630

# ---- 0.2 stat talismans: (family, stat word, crystal colour, gem, per-tier values, T1 recipe, T2 extra, T3 extra)
# values: Vitality = +max Health, Endurance = +max Stamina (base 10), Intelligence = +max Mana (base 0, cloth armour gives 10-28 a piece),
# Regeneration = Health healed every REGEN_EVERY seconds, Speed = movement multiplier - 1 (percent / 100)
TIER_NAMES = ["", "Talisman", "Ring", "Artifact"]
TIER_QUAL = ["", "Uncommon", "Rare", "Epic"]
REGEN_EVERY = 2
TALISMANS = [
    ("Vitality",     "Health",  "Red",    "Rock_Gem_Ruby",     [5, 10, 20],
        [("Ingredient_Crystal_Red", 3), ("Ingredient_Life_Essence", 10), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Ruby", 1), ("Ingredient_Bar_Iron", 10), ("Ingredient_Life_Essence", 30)],
        [("Rock_Gem_Ruby", 3), ("Ingredient_Bar_Thorium", 10), ("Ingredient_Life_Essence_Concentrated", 2)]),
    ("Endurance",    "Stamina", "Yellow", "Rock_Gem_Topaz",    [1, 2, 4],
        [("Ingredient_Crystal_Yellow", 3), ("Ingredient_Leather_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Topaz", 1), ("Ingredient_Leather_Medium", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Topaz", 3), ("Ingredient_Leather_Heavy", 15), ("Ingredient_Bar_Thorium", 10)]),
    ("Intelligence", "Mana",    "Blue",   "Rock_Gem_Sapphire", [10, 20, 40],
        [("Ingredient_Crystal_Blue", 3), ("Ingredient_Fabric_Scrap_Linen", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Sapphire", 1), ("Ingredient_Fabric_Scrap_Silk", 10), ("Ingredient_Bar_Silver", 5)],
        [("Rock_Gem_Sapphire", 3), ("Ingredient_Bolt_Cindercloth", 5), ("Ingredient_Bar_Cobalt", 10)]),
    ("Regeneration", "Regen",   "Green",  "Rock_Gem_Emerald",  [1, 2, 4],
        [("Ingredient_Crystal_Green", 3), ("Ingredient_Life_Essence", 20), ("Ingredient_Tree_Sap", 5)],
        [("Rock_Gem_Emerald", 1), ("Ingredient_Life_Essence", 50), ("Ingredient_Bar_Gold", 5)],
        [("Rock_Gem_Emerald", 3), ("Ingredient_Life_Essence_Concentrated", 3), ("Ingredient_Bar_Cobalt", 10)]),
    ("Speed",        "Speed",   "Cyan",   "Rock_Gem_Zephyr",   [4, 8, 12],
        [("Ingredient_Crystal_Cyan", 3), ("Ingredient_Feathers_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Zephyr", 1), ("Ingredient_Feathers_Blue", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Zephyr", 3), ("Ingredient_Lightning_Essence", 10), ("Ingredient_Bar_Cobalt", 10)]),
]
FAM = dict((t[0], i) for i, t in enumerate(TALISMANS))
def jfloats(vals, scale=1.0):
    return ", ".join("%.4ff" % (v * scale) for v in [0] + list(vals))

# ================= AccDefs =================
bench_ids = ", ".join('"%s"' % b[0] for b in BENCHES)
bench_names = ", ".join('"%s"' % b[2] for b in BENCHES)
dfs.addField(CtField.make('public static final String BAG = "%s";' % BAG, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_IDS = new String[] { %s };' % bench_ids, dfs))
dfs.addField(CtField.make('public static final String[] BENCH_NAMES = new String[] { %s };' % bench_names, dfs))
dfs.addField(CtField.make('public static final String[] FAMILIES = new String[] { %s };' % ", ".join('"%s"' % t[0] for t in TALISMANS), dfs))
dfs.addField(CtField.make('public static final String[] TIER_NAMES = new String[] { "", "Talisman", "Ring", "Artifact" };', dfs))
dfs.addField(CtField.make('public static final float[] VIT = new float[] { %s };' % jfloats(TALISMANS[FAM["Vitality"]][4]), dfs))
dfs.addField(CtField.make('public static final float[] END = new float[] { %s };' % jfloats(TALISMANS[FAM["Endurance"]][4]), dfs))
dfs.addField(CtField.make('public static final float[] INT = new float[] { %s };' % jfloats(TALISMANS[FAM["Intelligence"]][4]), dfs))
dfs.addField(CtField.make('public static final float[] REG = new float[] { %s };' % jfloats(TALISMANS[FAM["Regeneration"]][4]), dfs))
dfs.addField(CtField.make('public static final float[] SPD = new float[] { %s };' % jfloats(TALISMANS[FAM["Speed"]][4], 0.01), dfs))
dfs.addField(CtField.make('public static final int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean isAccessory(String id) {
  if (id == null) return false;
  if (id.startsWith("Skyy_Talisman_")) return true;
  return id.startsWith("Skyy_Accessory_") && !id.equals(BAG);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean isTalisman(String id) {
  return id != null && id.startsWith("Skyy_Talisman_") && id.length() > "Skyy_Talisman_".length();
}""", dfs))
# "Skyy_Talisman_Vitality_Ring" -> "Vitality"
dfs.addMethod(CtNewMethod.make("""
public static String familyOf(String id) {
  if (!isTalisman(id)) return null;
  String tail = id.substring("Skyy_Talisman_".length());
  int k = tail.lastIndexOf('_');
  return k > 0 ? tail.substring(0, k) : tail;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static int familyIndex(String fam) {
  if (fam == null) return -1;
  for (int i = 0; i < FAMILIES.length; i++) if (FAMILIES[i].equals(fam)) return i;
  return -1;
}""", dfs))
# "Skyy_Accessory_Workbench_T2" -> "Workbench" ; ids without _T<n> -> whole tail
dfs.addMethod(CtNewMethod.make("""
public static String benchOf(String id) {
  if (!isAccessory(id) || isTalisman(id)) return null;
  String tail = id.substring("Skyy_Accessory_".length());
  int t = tail.lastIndexOf("_T");
  if (t > 0) {
    boolean digits = t + 2 < tail.length();
    for (int i = t + 2; i < tail.length(); i++) if (!Character.isDigit(tail.charAt(i))) digits = false;
    if (digits) return tail.substring(0, t);
  }
  return tail;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static int tierOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isTalisman(id)) {
    if (id.endsWith("_Artifact")) return 3;
    if (id.endsWith("_Ring")) return 2;
    return 1;
  }
  int t = id.lastIndexOf("_T");
  if (t < 0 || t + 2 >= id.length()) return 1;
  try { return Integer.parseInt(id.substring(t + 2)); } catch (Throwable e) { return 1; }
}""", dfs))
# one-per-group key used by AccStore.equip: bench id for bench accessories, "T:<family>" for talismans
dfs.addMethod(CtNewMethod.make("""
public static String groupOf(String id) {
  if (isTalisman(id)) return "T:" + familyOf(id);
  return benchOf(id);
}""", dfs))
# highest talisman tier per family (index = FAMILIES) among the bag slots
dfs.addMethod(CtNewMethod.make("""
public static int[] bestTiers(String[] s) {
  int[] out = new int[FAMILIES.length];
  if (s == null) return out;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (!isTalisman(id)) continue;
    int f = familyIndex(familyOf(id));
    if (f < 0) continue;
    int t = tierOf(id);
    if (t > 3) t = 3;
    if (t > out[f]) out[f] = t;
  }
  return out;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String bonusText(String[] s) {
  int[] b = bestTiers(s);
  StringBuilder sb = new StringBuilder();
  if (b[%(V)d] > 0) sb.append(" / +").append((int) VIT[b[%(V)d]]).append(" Health");
  if (b[%(E)d] > 0) sb.append(" / +").append((int) END[b[%(E)d]]).append(" Stamina");
  if (b[%(I)d] > 0) sb.append(" / +").append((int) INT[b[%(I)d]]).append(" Mana");
  if (b[%(R)d] > 0) sb.append(" / Regen ").append((int) REG[b[%(R)d]]).append(" HP/").append(REGEN_EVERY).append("s");
  if (b[%(S)d] > 0) sb.append(" / +").append(Math.round(SPD[b[%(S)d]] * 100.0f)).append("%% Speed");
  if (sb.length() == 0) return "Bonuses - none yet - put talismans in this bag";
  return "Bonuses - " + sb.substring(3);
}""" % dict(V=FAM["Vitality"], E=FAM["Endurance"], I=FAM["Intelligence"], R=FAM["Regeneration"], S=FAM["Speed"]), dfs))
dfs.addMethod(CtNewMethod.make("""
public static String roman(int t) {
  String[] r = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII" };
  return t >= 0 && t < r.length ? r[t] : String.valueOf(t);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String pretty(String id) {
  if (isTalisman(id)) {
    int tt = tierOf(id);
    return familyOf(id) + " " + (tt >= 0 && tt < TIER_NAMES.length ? TIER_NAMES[tt] : String.valueOf(tt));
  }
  String b = benchOf(id);
  if (b == null) return id == null ? "?" : id;
  for (int i = 0; i < BENCH_IDS.length; i++) if (BENCH_IDS[i].equals(b)) return BENCH_NAMES[i] + " " + roman(tierOf(id));
  return b.replace('_', ' ') + " " + roman(tierOf(id));
}""", dfs))

# ================= AccStore =================
st_.addField(CtField.make("public static java.nio.file.Path DIR;", st_))
st_.addField(CtField.make(f"public static {LOG} LOG;", st_))
st_.addField(CtField.make("public static final int CAP = %d;" % CAP, st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap BAGS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap PUBLISHED = new java.util.concurrent.ConcurrentHashMap();", st_))
# 0.2 effect state (world thread writes, 5 s tick prunes offline players): CLOCK uuid -> float[]{secondsSinceSync, regenSeconds},
# SPEED uuid -> float[]{appliedMultiplier, consecutiveReapplies, baseSpeedWeWrote (-1 = none)}
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap CLOCK = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SPEED = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyAccessories] " + msg); } catch (Throwable t) { }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""", st_))
st_.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LOCKS = new java.util.concurrent.ConcurrentHashMap();", st_))
st_.addMethod(CtNewMethod.make("""
public static Object lock(java.util.UUID u) {
  Object o = LOCKS.get(u);
  if (o != null) return o;
  Object n = new Object();
  o = LOCKS.putIfAbsent(u, n);
  return o == null ? n : o;
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String[] slots(java.util.UUID u) {
  String[] s = (String[]) BAGS.get(u);
  if (s != null) return s;
  synchronized (lock(u)) {
    s = (String[]) BAGS.get(u);
    if (s != null) return s;
    s = new String[CAP];
    try {
      java.nio.file.Path f = DIR.resolve(u.toString() + ".properties");
      if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
        java.util.Properties p = new java.util.Properties();
        java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
        try { p.load(in); } finally { in.close(); }
        for (int i = 0; i < CAP; i++) {
          String v = p.getProperty("slot" + i);
          if (v != null && v.trim().length() > 0) s[i] = v.trim();
        }
      }
    } catch (Throwable t) { warn("could not load bag for " + u + ": " + t); }
    BAGS.put(u, s);
    return s;
  }
}""", st_))
# copy of the bag for readers (talisman tick, page build) - never the live array
st_.addMethod(CtNewMethod.make("""
public static String[] snapshot(java.util.UUID u) {
  String[] s = slots(u);
  String[] c = new String[s.length];
  synchronized (lock(u)) { System.arraycopy(s, 0, c, 0, s.length); }
  return c;
}""", st_))
# acc:has keeps its 0.1 meaning (bench accessories only - SkyySacks 0.6.1 parses every id there as Skyy_Accessory_<Bench>_T<n>, so a
# talisman id made a bogus "itality Talisman I" craft tab); talismans go to acc:tal:<uuid>; acc:fn:has still answers for both
st_.addMethod(CtNewMethod.make(f"""
public static void publish(java.util.UUID u) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);
    StringBuilder acc = new StringBuilder();
    StringBuilder tal = new StringBuilder();
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      StringBuilder sb = {PKG}.AccDefs.isTalisman(s[i]) ? tal : acc;
      if (sb.length() > 0) sb.append(',');
      sb.append(s[i]);
    }}
    bridge().put("acc:has:" + u.toString(), acc.toString());
    bridge().put("acc:tal:" + u.toString(), tal.toString());
    PUBLISHED.put(u, Boolean.TRUE);
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {
  synchronized (lock(u)) {
    try {
      String[] s = slots(u);
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.util.Properties p = new java.util.Properties();
      for (int i = 0; i < s.length; i++) if (s[i] != null) p.setProperty("slot" + i, s[i]);
      java.nio.file.Path tmp = DIR.resolve(u.toString() + ".properties.tmp");
      java.io.OutputStream out = java.nio.file.Files.newOutputStream(tmp, new java.nio.file.OpenOption[0]);
      try { p.store(out, "SkyyAccessories bag"); } finally { out.close(); }
      java.nio.file.Files.move(tmp, DIR.resolve(u.toString() + ".properties"), new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
    } catch (Throwable t) { warn("could not save bag for " + u + ": " + t); }
    publish(u);
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static boolean has(java.util.UUID u, String id) {
  if (u == null || id == null) return false;
  synchronized (lock(u)) {
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) if (id.equals(s[i])) return true;
    return false;
  }
}""", st_))
# would equip(u, id) take the item? same rule as equip - asked BEFORE the item leaves the inventory
st_.addMethod(CtNewMethod.make(f"""
public static boolean canEquip(java.util.UUID u, String id) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);
    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (g != null && g.equals({PKG}.AccDefs.groupOf(s[i]))) return {PKG}.AccDefs.tierOf(s[i]) < tier;
    }}
    for (int i = 0; i < s.length; i++) if (s[i] == null) return true;
    return false;
  }}
}}""", st_))
# equips id; returns the item id that was displaced (same group, lower tier) or "" when a free slot was used, or null when the bag is full / an equal or better one is in
st_.addMethod(CtNewMethod.make(f"""
public static String equip(java.util.UUID u, String id) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);
    String g = {PKG}.AccDefs.groupOf(id);
    int tier = {PKG}.AccDefs.tierOf(id);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (g != null && g.equals({PKG}.AccDefs.groupOf(s[i]))) {{
        if ({PKG}.AccDefs.tierOf(s[i]) >= tier) return null;
        String old = s[i]; s[i] = id; save(u); return old;
      }}
    }}
    for (int i = 0; i < s.length; i++) if (s[i] == null) {{ s[i] = id; save(u); return ""; }}
    return null;
  }}
}}""", st_))
st_.addMethod(CtNewMethod.make("""
public static String unequip(java.util.UUID u, int idx) {
  synchronized (lock(u)) {
    String[] s = slots(u);
    if (idx < 0 || idx >= s.length || s[idx] == null) return null;
    String id = s[idx]; s[idx] = null; save(u); return id;
  }
}""", st_))
st_.addMethod(CtNewMethod.make("""
public static void put(java.util.UUID u, int idx, String id) {
  synchronized (lock(u)) {
    String[] s = slots(u);
    if (idx < 0 || idx >= s.length) return;
    s[idx] = id; save(u);
  }
}""", st_))
# last resort so an item can never vanish: first free slot, ignoring the one-per-group rule (bestTiers and SkyySacks use the best tier)
st_.addMethod(CtNewMethod.make("""
public static boolean stash(java.util.UUID u, String id) {
  synchronized (lock(u)) {
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) if (s[i] == null) { s[i] = id; save(u); return true; }
    return false;
  }
}""", st_))
st_.addMethod(CtNewMethod.make(f"""
public static void publishOnline() {{
  try {{
    java.util.HashSet online = new java.util.HashSet();
    java.util.Iterator it = {UNI}.get().getPlayers().iterator();
    while (it.hasNext()) {{
      {PR} pr = ({PR}) it.next();
      if (pr == null || !pr.isValid()) continue;
      java.util.UUID u = pr.getUuid();
      online.add(u);
      if (!PUBLISHED.containsKey(u)) publish(u);
    }}
    PUBLISHED.keySet().retainAll(online);
    CLOCK.keySet().retainAll(online);
    SPEED.keySet().retainAll(online);
  }} catch (Throwable t) {{ }}
}}""", st_))

# ================= AccFn (bridge function acc:fn:has) =================
fn.addInterface(pool.get("java.util.function.Function"))
fn.addConstructor(CtNewConstructor.make("public AccFn() { }", fn))
fn.addMethod(CtNewMethod.make(f"""
public Object apply(Object arg) {{
  try {{
    Object[] a = (Object[]) arg;
    return Boolean.valueOf({PKG}.AccStore.has((java.util.UUID) a[0], String.valueOf(a[1])));
  }} catch (Throwable t) {{ return Boolean.FALSE; }}
}}""", fn))

# ================= AccPage =================
page.addField(CtField.make("public String info;", page))
page.addField(CtField.make("public String[] invIds;", page))
page.addConstructor(CtNewConstructor.make(f"""
public AccPage({PR} pr) {{
  super(pr, {LIFE}.CanDismiss);
  this.info = "";
}}""", page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ');
}""", page))
# accessory item ids carried in storage/hotbar/backpack (distinct)
page.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList carried({PLA} p) {{
  java.util.ArrayList out = new java.util.ArrayList();
  {INV} inv = p.getInventory();
  if (inv == null) return out;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if ({PKG}.AccDefs.isAccessory(id) && !out.contains(id)) out.add(id);
    }}
  }}
  return out;
}}""", page))
# remove one of item id from any inventory section; true when removed
page.addMethod(CtNewMethod.make(f"""
public static boolean takeOne({PLA} p, String id) {{
  {INV} inv = p.getInventory();
  if (inv == null) return false;
  {IC}[] scan = new {IC}[] {{ inv.getStorage(), inv.getHotbar(), inv.getBackpack() }};
  for (int c = 0; c < scan.length; c++) {{
    {IC} cont = scan[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {{
      {IS} it = cont.getItemStack(s);
      if (it == null || it.isEmpty() || !id.equals(it.getItemId())) continue;
      {ISS} tx = cont.removeItemStackFromSlot(s, 1);
      if (tx != null && tx.succeeded()) return true;
    }}
  }}
  return false;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public static boolean giveOne({PLA} p, String id) {{
  try {{
    {IST} tx = p.getInventory().getStorage().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    tx = p.getInventory().getHotbar().addItemStack(new {IS}(id, 1));
    if (tx != null && tx.succeeded()) return true;
    {IC} bp = p.getInventory().getBackpack();
    if (bp == null) return false;
    tx = bp.addItemStack(new {IS}(id, 1));
    return tx != null && tx.succeeded();
  }} catch (Throwable t) {{ return false; }}
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
  String[] s = {PKG}.AccStore.snapshot(u);
  String bs = "Style: TextButtonStyle(Default: (Background: #5a4420, LabelStyle: (FontSize: 12, TextColor: #ffe9c9, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #8a6a30, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #3a2a10, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyyAcc {{ Anchor: (Width: 640, Height: {PAGE_H}); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyyAcc", "Group {{ Anchor: (Height: 2); Background: #8fd0ff; }}");
  b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 30); Text: \\"Accessory Bag\\"; Style: (FontSize: 16, RenderBold: true, TextColor: #e6f4ff, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 18); Text: \\"Bench accessories unlock /craft recipes - talismans give stats while they sit in this bag.\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.appendInline("#SkyyAcc", "Label #SkyyAccBonus {{ Anchor: (Height: 20); Text: \\"" + safe({PKG}.AccDefs.bonusText(s)) + "\\"; Style: (FontSize: 12, RenderBold: true, TextColor: #9be89b, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  for (int i = 0; i < s.length; i++) {{
    b.appendInline("#SkyyAcc", "Group #SkyyAccSlot" + i + " {{ Anchor: (Height: 34); LayoutMode: Left; Padding: (Top: 2); Background: #142030(0.9); }}");
    if (s[i] != null) {{
      b.appendInline("#SkyyAccSlot" + i, "Group {{ Anchor: (Width: 40, Height: 32); ItemIcon {{ Anchor: (Width: 28, Height: 28, Left: 6, Top: 2); ItemId: \\"" + safe(s[i]) + "\\"; }} }}");
      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 400, Height: 32); Text: \\"" + safe({PKG}.AccDefs.pretty(s[i])) + "\\"; Style: (FontSize: 13, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
      b.appendInline("#SkyyAccSlot" + i, "TextButton #SkyyAccUn" + i + " {{ Anchor: (Width: 120, Height: 28); Text: \\"Unequip\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyyAccUn" + i, {EVD}.of("a", "un:" + i));
    }} else {{
      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 560, Height: 32); Text: \\"  empty slot\\"; Style: (FontSize: 12, TextColor: #5f7a90, VerticalAlignment: Center); }}");
    }}
  }}
  b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 22); Text: \\"Accessories and talismans in your inventory\\"; Style: (FontSize: 12, RenderBold: true, TextColor: #c9dff0, VerticalAlignment: Center); }}");
  java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);
  this.invIds = new String[inv.size()];
  if (inv.isEmpty()) b.appendInline("#SkyyAcc", "Label {{ Anchor: (Height: 20); Text: \\"  none - craft bench accessories and talismans at a Workbench\\"; Style: (FontSize: 11, TextColor: #5f7a90, VerticalAlignment: Center); }}");
  for (int i = 0; i < inv.size() && i < {INV_ROWS}; i++) {{
    String id = (String) inv.get(i);
    this.invIds[i] = id;
    b.appendInline("#SkyyAcc", "Group #SkyyAccInv" + i + " {{ Anchor: (Height: 30); LayoutMode: Left; Padding: (Top: 1); }}");
    b.appendInline("#SkyyAccInv" + i, "Group {{ Anchor: (Width: 40, Height: 28); ItemIcon {{ Anchor: (Width: 26, Height: 26, Left: 7, Top: 1); ItemId: \\"" + safe(id) + "\\"; }} }}");
    b.appendInline("#SkyyAccInv" + i, "Label {{ Anchor: (Width: 400, Height: 28); Text: \\"" + safe({PKG}.AccDefs.pretty(id)) + "\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
    b.appendInline("#SkyyAccInv" + i, "TextButton #SkyyAccEq" + i + " {{ Anchor: (Width: 120, Height: 26); Text: \\"Equip\\"; " + bs + " }}");
    ev.addEventBinding({BT}.Activating, "#SkyyAccEq" + i, {EVD}.of("a", "eq:" + i));
  }}
  b.appendInline("#SkyyAcc", "Label #SkyyAccInfo {{ Anchor: (Height: 22); Text: \\"" + safe(this.info) + "\\"; Style: (FontSize: 12, TextColor: #c9b89a, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
}}""", page))
# giveBack: 0 = back in the inventory, 1 = kept in a free bag slot, 2 = lost (logged with the player's uuid so an admin can give it back)
page.addMethod(CtNewMethod.make(f"""
public static int giveBack({PLA} p, java.util.UUID u, String id) {{
  if (giveOne(p, id)) return 0;
  if ({PKG}.AccStore.stash(u, id)) return 1;
  {PKG}.AccStore.warn("ITEM LOST - could not return " + id + " to player " + u + " (inventory and accessory bag full), give it back by hand");
  return 2;
}}""", page))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    java.util.UUID u = this.playerRef.getUuid();
    {PLA} player = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    for (int i = 0; i < {PKG}.AccStore.CAP; i++) {{
      if (data.indexOf("un:" + i + "\\"") < 0) continue;
      String id = {PKG}.AccStore.unequip(u, i);
      if (id == null) return;
      if (!giveOne(player, id)) {{ {PKG}.AccStore.put(u, i, id); this.info = "your inventory is full"; }}
      else this.info = "unequipped " + {PKG}.AccDefs.pretty(id);
      rebuild(); return;
    }}
    for (int i = 0; i < {INV_ROWS}; i++) {{
      if (data.indexOf("eq:" + i + "\\"") < 0) continue;
      if (this.invIds == null || i >= this.invIds.length || this.invIds[i] == null) return;
      String id = this.invIds[i];
      String why = "bag is full, or the same or a better " + ({PKG}.AccDefs.isTalisman(id) ? {PKG}.AccDefs.familyOf(id) + " talisman" : "bench accessory") + " is already equipped";
      if (!{PKG}.AccStore.canEquip(u, id)) {{ this.info = why; rebuild(); return; }}
      if (!takeOne(player, id)) {{ this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }}
      String res = {PKG}.AccStore.equip(u, id);
      if (res == null) {{
        int g = giveBack(player, u, id);
        this.info = g == 0 ? why : (g == 1 ? why + " - it was kept in a free bag slot" : "could not give " + {PKG}.AccDefs.pretty(id) + " back - inventory and bag full, reported to the server log");
        rebuild(); return;
      }}
      if (res.length() > 0) {{
        int g = giveBack(player, u, res);
        String old = {PKG}.AccDefs.pretty(res);
        this.info = "upgraded to " + {PKG}.AccDefs.pretty(id) + " - " + (g == 0 ? old + " returned" : (g == 1 ? old + " kept in the bag - inventory full" : old + " could not be returned - reported to the server log"));
      }}
      else this.info = "equipped " + {PKG}.AccDefs.pretty(id);
      rebuild(); return;
    }}
  }} catch (Throwable t) {{ {PKG}.AccStore.warn("bag page event failed: " + t); }}
}}""", page))

fac.addInterface(pool.get("java.util.function.Function"))
fac.addConstructor(CtNewConstructor.make("public AccPageFactory() { }", fac))
fac.addMethod(CtNewMethod.make(f"""
public Object apply(Object o) {{
  return new {PKG}.AccPage(({PR}) o);
}}""", fac))

# ================= /accessories =================
cmd.addConstructor(CtNewConstructor.make("""
public AccCmd() {
  super("accessories", "Open your accessory bag");
  addAliases(new String[] { "acc", "accbag" });
}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.AccPage(pr));
  }} catch (Throwable t) {{
    {PKG}.AccStore.warn("/accessories failed: " + t);
    pr.sendMessage({MSG}.raw("[Accessories] could not open the bag"));
  }}
}}""", cmd))

tick.addInterface(pool.get("java.lang.Runnable"))
tick.addConstructor(CtNewConstructor.make("public AccTick() { }", tick))
tick.addMethod(CtNewMethod.make(f"public void run() {{ {PKG}.AccStore.publishOnline(); }}", tick))

# ================= AccEffects: talisman stats (EntityTickingSystem on Player entities, runs on each world's thread) =================
# Pattern copied from TerrariaAddons 1.7.4 (DivingHelmetSystem: putModifier/removeModifier with a StaticModifier under a fixed key;
# BandOfRegenerationSystem: addStatValue(DefaultEntityStatTypes.getHealth(), n); speed: EndgameAndQoL AccessoryPassiveSystem baseSpeed =
# default * f, then update(playerRef.getPacketHandler())). Work is throttled to once per second per player.
eff.addConstructor(CtNewConstructor.make("public AccEffects() { super(); }", eff))
eff.addField(CtField.make("public static boolean FAILED_ONCE = false;", eff))
eff.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return ({QRY}) {PLA}.getComponentType();
}}""", eff))
# set (amt != 0) or remove (amt == 0) our MAX modifier on one stat; only writes when something changes
eff.addMethod(CtNewMethod.make(f"""
public static void mod({ESM} m, int idx, String key, float amt) {{
  if (idx < 0) return;
  try {{
    if (m.get(idx) == null) return;   // getModifier/putModifier would log "No EntityStatValue found" every second
    {MOD} cur = m.getModifier(idx, key);
    if (amt == 0.0f) {{ if (cur != null) m.removeModifier(idx, key); return; }}
    {SMO} want = new {SMO}({MTG}.MAX, {CAL}.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, key, want);
  }} catch (Throwable t) {{ }}
}}""", eff))
# Speed (review fix): ONLY MovementSettings.baseSpeed is scaled. The direction multipliers are factors ON baseSpeed (vanilla
# Server/Entity/MovementConfig/Default.json: BaseSpeed 5.5, ForwardRun 1.0, ForwardWalk 0.3, ForwardSprint 1.273), so the first 0.2 build
# (TerrariaAddons SpeedBoostSystem: baseSpeed AND every multiplier times f) compounded to f*f - the +12% Artifact ran about +25%.
# baseSpeed only = EndgameAndQoL AccessoryPassiveSystem, RPGLeveling MovementSpeedHelper, Hylamity GroundMoveSpeedModifierSystem; it also
# composes with mods that scale the multipliers instead (EndlessLeveling SkillManager, CarryChest) instead of fighting them.
# want = 1 + speed bonus; st = {appliedMultiplier, consecutiveReapplies, baseSpeedWeWrote}. Backs off after 5 re-applies in a row (another
# mod resetting it). Without the talisman: the default baseSpeed is restored whenever the live value is (still, or again - a snapshot/
# restore mod may put it back) the value WE wrote; the entry is dropped once that happened or the live value is back at the default.
# The engine's applyDefaultSettings() (join, world change, game mode, mount, model) replaces the whole settings object with defaults.
eff.addMethod(CtNewMethod.make("""
public static boolean near(float a, float b) {
  float m = Math.abs(b);
  if (m < 1.0f) m = 1.0f;
  return Math.abs(a - b) <= 0.001f * m;
}""", eff))
eff.addMethod(CtNewMethod.make(f"""
public static void speed(java.util.UUID u, {PR} pr, {MMG} mm, float want) {{
  {MVS} s = mm.getSettings();
  {MVS} d = mm.getDefaultSettings();
  if (s == null || d == null || d.baseSpeed <= 0.0f) return;
  float[] st = (float[]) {PKG}.AccStore.SPEED.get(u);
  if (want > 1.0001f) {{
    if (st == null) {{ st = new float[] {{ 1.0f, 0.0f, -1.0f }}; {PKG}.AccStore.SPEED.put(u, st); }}
    if (Math.abs(st[0] - want) > 0.0001f) st[1] = 0.0f;
    float target = d.baseSpeed * want;
    if (near(s.baseSpeed, target)) {{ st[0] = want; st[1] = 0.0f; st[2] = s.baseSpeed; return; }}
    if (st[1] >= 5.0f) return;
    s.baseSpeed = target;
    mm.update(pr.getPacketHandler());
    st[0] = want; st[1] = st[1] + 1.0f; st[2] = target;
    if (st[1] >= 5.0f) {PKG}.AccStore.warn("speed talisman of " + u + " keeps being reset (another movement mod?) - speed bonus paused until the talisman changes");
  }} else if (st != null) {{
    if (st[2] > 0.0f && near(s.baseSpeed, st[2]) && !near(s.baseSpeed, d.baseSpeed)) {{
      s.baseSpeed = d.baseSpeed;
      mm.update(pr.getPacketHandler());
      {PKG}.AccStore.SPEED.remove(u);
      return;
    }}
    if (st[2] <= 0.0f || near(s.baseSpeed, d.baseSpeed)) {{ {PKG}.AccStore.SPEED.remove(u); return; }}
    st[0] = 1.0f; st[1] = 0.0f;   // another mod owns baseSpeed right now: keep watching for our value; a re-equip starts un-paused
  }}
}}""", eff))
eff.addMethod(CtNewMethod.make(f"""
public void tick(float dt, int idx, {ACH} chunk, {ST} store, {CB} cb) {{
  try {{
    {REF} ref = chunk.getReferenceTo(idx);
    if (ref == null || !ref.isValid()) return;
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p == null || p.isWaitingForClientReady()) return;
    {PR} pr = ({PR}) store.getComponent(ref, {PR}.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    float[] c = (float[]) {PKG}.AccStore.CLOCK.get(u);
    if (c == null) {{ c = new float[] {{ 1.0f, 0.0f }}; {PKG}.AccStore.CLOCK.put(u, c); }}
    c[0] = c[0] + dt;
    if (c[0] < 1.0f) return;
    c[0] = 0.0f;
    int[] best = {PKG}.AccDefs.bestTiers({PKG}.AccStore.snapshot(u));
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m != null) {{
      mod(m, {DST}.getHealth(), "skyyacc_health", {PKG}.AccDefs.VIT[best[{FAM['Vitality']}]]);
      mod(m, {DST}.getStamina(), "skyyacc_stamina", {PKG}.AccDefs.END[best[{FAM['Endurance']}]]);
      mod(m, {DST}.getMana(), "skyyacc_mana", {PKG}.AccDefs.INT[best[{FAM['Intelligence']}]]);
      int rt = best[{FAM['Regeneration']}];
      if (rt > 0) {{
        c[1] = c[1] + 1.0f;
        if (c[1] >= (float) {PKG}.AccDefs.REGEN_EVERY) {{
          c[1] = 0.0f;
          int hi = {DST}.getHealth();
          {ESV} hv = hi < 0 ? null : m.get(hi);
          if (hv != null) {{
            float now = hv.get();
            float max = hv.getMax();
            float amt = {PKG}.AccDefs.REG[rt];
            if (now > 0.0f && now < max) {{
              if (now + amt > max) amt = max - now;
              m.addStatValue(hi, amt);
            }}
          }}
        }}
      }} else c[1] = 0.0f;
    }}
    {MMG} mm = ({MMG}) cb.getComponent(ref, {MMG}.getComponentType());
    if (mm != null) speed(u, pr, mm, 1.0f + {PKG}.AccDefs.SPD[best[{FAM['Speed']}]]);
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.AccStore.warn("talisman effects failed (logged once): " + t); }}
  }}
}}""", eff))

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
pl.addConstructor(CtNewConstructor.make(f"public SkyyAccessoriesPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.AccStore.LOG = getLogger();
  {PKG}.AccStore.DIR = getDataDirectory().resolveSibling("Skyy_SkyyAccessories").resolve("bags");
  {OCU}.registerSimple(this, {PKG}.SkyyAccessoriesPlugin.class, "SkyyAccBag", new {PKG}.AccPageFactory());
  getCommandRegistry().registerCommand(new {PKG}.AccCmd());
  {PKG}.AccStore.bridge().put("acc:fn:has", new {PKG}.AccFn());
  getEntityStoreRegistry().registerSystem(new {PKG}.AccEffects());
  this.ticker = {HSV}.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new {PKG}.AccTick(), 5L, 5L, java.util.concurrent.TimeUnit.SECONDS);
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyAccessories] {VERSION} ready - /accessories, right-click the Accessory Bag; %d bench accessories, %d talismans (stat effects on)" );
}}""" % (sum(b[3] for b in BENCHES), len(TALISMANS) * 3), pl))
pl.addMethod(CtNewMethod.make("""
protected void shutdown() {
  try { if (this.ticker != null) this.ticker.cancel(false); } catch (Throwable t) { }
  try { com.skyy.accessories.AccStore.bridge().remove("acc:fn:has"); } catch (Throwable t) { }
  super.shutdown();
}""", pl))

for c in (dfs, st_, fn, page, fac, cmd, tick, eff, pl):
    c.writeFile(OUT)
print("classes written")

# ================= assets: items + lang =================
def item(iid, icon, quality, recipe_in, bench_req, page_id=None, visual=None):
    node = {
      "TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid},
      "Categories": ["Items.Tools"],
      "Icon": icon,
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": bench_req},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
    }
    if visual:
        node.update(visual)   # 0.2 review fix: talismans look like the vanilla crystal they are made from (0.1 placeholder: backpack)
    if page_id:
        node["Interactions"] = {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    return node

WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]
# 0.2: every recipe input / icon is checked against the vanilla Assets.zip (build fails on a typo instead of a broken recipe in game)
import zipfile
_ASSETS = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
_ITEMS = {}
for _n in _ASSETS.namelist():
    if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
        _ITEMS[os.path.basename(_n)[:-5]] = _n
_COMMON = set(n for n in _ASSETS.namelist() if n.startswith("Common/"))
_RTYPES = set(os.path.basename(n)[:-5] for n in _ASSETS.namelist() if n.startswith("Server/Item/ResourceTypes/") and n.endswith(".json"))
_VNAMES = {}
for _l in _ASSETS.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
    if _l.startswith("items.") and ".name" in _l and "=" in _l:
        _k, _v = _l.split("=", 1)
        _VNAMES[_k.strip()[len("items."):-len(".name")]] = _v.strip()
def vname(iid):
    """vanilla display name (en-US server.lang), e.g. Ingredient_Bar_Iron -> Iron Ingot"""
    return _VNAMES.get(iid) or iid.replace("Ingredient_", "").replace("Rock_Gem_", "").replace("_", " ")
def need_item(iid):
    assert iid in _ITEMS, "unknown vanilla item id: " + iid
def mat(m, q):
    """recipe input: ItemId for items, ResourceTypeId for resource types (0.1 bug: the Farming Bench upgrades used
    ItemId Wood_Softwood_Trunk etc. - those are ResourceTypes in vanilla Bench_Farming TierLevels, so the recipes could not resolve)"""
    if m in _ITEMS: return {"ItemId": m, "Quantity": q}
    assert m in _RTYPES, "unknown vanilla item / resource type: " + m
    return {"ResourceTypeId": m, "Quantity": q}
def icon_of(iid):
    """the vanilla item's own Icon (follows Parent), checked to exist under Common/"""
    seen = 0
    cur = iid
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(_ASSETS.read(_ITEMS[cur]).decode("utf-8-sig"))
        if d.get("Icon"):
            assert "Common/" + d["Icon"] in _COMMON, "missing icon file for %s: %s" % (iid, d["Icon"])
            return d["Icon"]
        cur = d.get("Parent"); seen += 1
    raise SystemExit("no icon for " + iid)
VISUAL_KEYS = ("Model", "Texture", "IconProperties", "Scale", "PlayerAnimationsId", "ItemSoundSetId")
def visual_of(iid):
    """held / dropped look of a vanilla item (follows Parent, the child's value wins); Model and Texture checked to exist under Common/"""
    out = {}
    cur = iid
    seen = 0
    while cur and seen < 8:
        need_item(cur)
        d = json.loads(_ASSETS.read(_ITEMS[cur]).decode("utf-8-sig"))
        for k in VISUAL_KEYS:
            if k in d and k not in out: out[k] = d[k]
        cur = d.get("Parent"); seen += 1
    assert "Model" in out and "Texture" in out, "no model for " + iid
    for k in ("Model", "Texture"):
        assert "Common/" + out[k] in _COMMON, "missing %s file for %s: %s" % (k, iid, out[k])
    return out
FIELD_REQ = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}]
QUAL = ["Common", "Common", "Uncommon", "Rare", "Rare", "Rare", "Rare", "Rare"]
files = {}
lang = []
files["Server/Item/Items/Utility/%s.json" % BAG] = json.dumps(item(BAG, "Icons/ItemsGenerated/Utility_Bag_Seed.png", "Uncommon",
    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], FIELD_REQ, "SkyyAccBag"), indent=2)
lang.append("items.%s.name=Accessory Bag" % BAG); lang.append("server.items.%s.name=Accessory Bag" % BAG)
d = "Right-click to open. Holds up to %d accessories. Bench accessories in it let /craft make that bench's recipes straight from your inventory; talismans in it give you stats (one per family counts)." % CAP
lang.append("items.%s.description=%s" % (BAG, d)); lang.append("server.items.%s.description=%s" % (BAG, d))
count = 0
for bench_id, bench_item, name, tiers, ups in BENCHES:
    for t in range(1, tiers + 1):
        iid = "Skyy_Accessory_%s_T%d" % (bench_id, t)
        if t == 1:
            need_item(bench_item)
            rin = [{"ItemId": bench_item, "Quantity": 1}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 4}]
        else:
            rin = [{"ItemId": "Skyy_Accessory_%s_T%d" % (bench_id, t - 1), "Quantity": 1}] + [mat(m, q) for m, q in ups[t - 2]]   # 0.2: mat() fixes resource types
        icon = "Icons/ItemsGenerated/%s.png" % ("Bench_Architects" if bench_item == "Bench_Builders" else bench_item)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ), indent=2)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        d = "Put it in your Accessory Bag to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1
need_item("Ingredient_Bar_Copper"); need_item("Ingredient_Fabric_Scrap_Cotton"); assert "Wood_Trunk" in _RTYPES

EFFECT = {
    "Vitality":     lambda v: "+%d max Health" % v,
    "Endurance":    lambda v: "+%d max Stamina" % v,
    "Intelligence": lambda v: "+%d max Mana" % v,
    "Regeneration": lambda v: "heals %d Health every %d seconds" % (v, REGEN_EVERY),
    "Speed":        lambda v: "+%d%% movement speed" % v,
}
tal_count = 0
for fam, word, crystal, gem, vals, r1, r2, r3 in TALISMANS:
    ups = [r1, r2, r3]
    vis = visual_of("Ingredient_Crystal_" + crystal)   # crystal fragment model in the family colour (all three tiers; the icon shows the tier)
    for t in (1, 2, 3):
        iid = "Skyy_Talisman_%s_%s" % (fam, TIER_NAMES[t])
        if t == 1:
            rin = [mat(m, q) for m, q in r1]
        else:
            rin = [{"ItemId": "Skyy_Talisman_%s_%s" % (fam, TIER_NAMES[t - 1]), "Quantity": 1}] + [mat(m, q) for m, q in ups[t - 1]]
        for m, q in ups[t - 1]: need_item(m)
        icon = icon_of("Ingredient_Crystal_" + crystal) if t == 1 else icon_of(gem)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(item(iid, icon, TIER_QUAL[t], rin, WB_REQ, visual=vis), indent=2)
        disp = "%s %s" % (fam, TIER_NAMES[t])
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        d = "Keep it in your Accessory Bag: %s. Only your best %s talisman counts." % (EFFECT[fam](vals[t - 1]), fam)
        if t < 3:
            d += " Upgrade it at a Workbench into the %s %s (%s)." % (fam, TIER_NAMES[t + 1], ", ".join("%d %s" % (q, vname(m)) for m, q in ups[t]))
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        tal_count += 1
print("talisman items:", tal_count)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("accessory items:", count)

jar = os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyAccessories", VERSION, "SkyWynn accessory bag: bench accessories unlock /craft (SkyySacks) recipes, stat talismans (Vitality, Endurance, Intelligence, Regeneration, Speed) work while they sit in the bag. Zero dependencies.", PKG + ".SkyyAccessoriesPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyAccessories.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyAccessories" % VERSION, disable_prefix="Skyy:")
