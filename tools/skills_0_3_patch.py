"""Derive SkyySkills/build_skyyskills_0.3.py from 0.2 (same style as skills_0_2_patch.py / acc_0_3_patch.py: rep(old, new) with
asserted anchors, newline-agnostic; 0.2 stays untouched, the CRLF/LF line endings of 0.2 are preserved).
0.3 (Skyy 2026-09-23):
 1. MAX LEVEL 100 for every skill ("max level for all skills is 100"). Levels 1-60 = Hypixel SkyBlock's own table (51-60 =
    4.3M .. 7.0M, +300k per level, cumulative 111,672,425 at 60 - asserted below), 61-100 continue that +300k step (level 100
    needs 19M, 0 -> 100 = 637,672,425 XP). An xp.properties whose levels= line is still exactly the 0.1/0.2 50-level default is
    rewritten to the 100-level table on load (SkillCfg.upgradeLevels; custom tables are kept). Player files keep their XP and
    levels 1-50 are unchanged, so nobody's level moves. Level-up coins keep paying up to 100 (coinsPerLevel x level).
    Acrobatics already reaches Skyy's level-100 targets with the 0.2 per-level keys (x2 speed, +1.5 blocks, -50% fall) - kept.
 2. STATS button replaces "Top 10" on every /skills row -> StatsPage (level, XP to next, boosts now with numbers, what the next
    level adds incl. its coins, how to earn XP, "< Back" to /skills, "Top 10" -> the old leaderboard view). /skills stats <skill>
    opens it too; /skills top <skill> (chat) stays.
 3. GATHERING PERKS (flat layer, perk.* keys appended once to an existing xp.properties, shown on the Stats page):
    max Health/Stamina/Mana per level for any skill as EntityStatMap StaticModifier(MAX, ADDITIVE) keys skyyskill_health /
    skyyskill_stamina / skyyskill_mana (SkyyAccessories AccEffects pattern), refreshed once per second by the existing
    Acrobatics player tick on the world thread. Double drops for Mining / Foraging (logs) / Farming (ripe crops, broken or
    F-harvested): VERIFIED against HytaleServer.jar bytecode - the engine's break drops are
    BlockHarvestUtils.getDrops(blockType, Breaking.getQuantity(), Breaking.getItemId(), Breaking.getDropListId())
    (damageSingleBlock -> performBlockBreak -> naturallyRemoveBlock), soft blocks use Soft.getItemId/getDropListId with
    quantity 1, F-harvest uses getDrops(bt, 1, Harvest.getItemId(), Harvest.getDropListId()) (FarmingUtil.giveDrops). The extra
    copy goes to Inventory.getCombinedStorageHotbarBackpack() via SimpleItemContainer.addOrDropItemStack (SkyySacks 0.6.5).
 4. CLASS-BASED COMBAT: Combat row = class skill (bridge class:<uuid>, class:skill:<uuid>); combat XP only with a class and a kill
    with a weapon class:fn:allowed accepts (+ class:weapons:<Class> when combat.classWeaponOnly=true); missing key -> no XP, told
    once. XP per class (Combat.<Class>), legacy Combat XP migrates to the first class seen. Combat perk: damage with class
    weapons (CombatDmgSys, Filter group, isCancelled checked) + max Health.
 5. COMMAND RULES: Adventurer group on /skills, stats, top, quiet; reload = requirePermission + empty group list.
Run:  python tools/skills_0_3_patch.py   then   python SkyySkills/build_skyyskills_0.3.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.2.py")
dst = os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.2"
s = raw.decode("utf8").replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------------------------------------------------------- header / version
rep('''"""SkyySkills 0.2 - build script (derived from 0.1 by tools/skills_0_2_patch.py - edit the patch, not this file)
Run:   python build_skyyskills_0.2.py            -> SkyySkills/SkyySkills-0.2.jar
       python build_skyyskills_0.2.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world
       DEPLOY TOGETHER WITH SkyyAccessories 0.3 (0.2's speed talisman does not speak the movement protocol and would fight Acrobatics)
''', r'''"""SkyySkills 0.3 - build script (derived from 0.2 by tools/skills_0_3_patch.py - edit the patch, not this file)
Run:   python build_skyyskills_0.3.py            -> SkyySkills/SkyySkills-0.3.jar
       python build_skyyskills_0.3.py --deploy   -> also copies to Mods/SkyySkills.jar and enables it in the HUD mod world
       Deploy with SkyyAccessories 0.3 (movement protocol) and SkyyClasses 0.1.1+ (combat = class skill; without it no combat XP
       at all). SkyyClasses 0.1.1 enables Mage with skill "Sorcery" = CLASS_ROWS below (0.1 had Mage disabled, skill "Magic").
0.3: MAX LEVEL 100 for every skill (Skyy). Levels 1-60 = Hypixel SkyBlock's table, 61-100 continue its +300k step (level 100
     needs 19M XP, 0 -> 100 = 637.7M). An xp.properties whose levels= line is still the old 50-level default is rewritten to the
     100-level table on load (a custom levels= line is kept; at most 100 entries). Player files keep their XP (levels 1-50 are
     unchanged, so nobody's level moves); level-up coins (coinsPerLevel x level) keep paying up to 100. Acrobatics already hits
     Skyy's level-100 targets (x2 speed, +1.5 blocks jump, -50% fall damage) with the 0.2 per-level keys - unchanged.
     STATS PAGE: the "Top 10" button of every /skills row is now "Stats" -> StatsPage: level / 100, XP to next, the boosts the
     skill gives right now (numbers) and what the next level adds (+ its coins), how to earn XP, "< Back" (to /skills) and
     "Top 10" (the old leaderboard view). Also /skills stats <skill>. /skills top <skill> still prints the top 10 in chat.
     GATHERING PERKS (flat layer, perk.* keys appended once to an existing xp.properties): max Health / Stamina / Mana per level
     for any skill (defaults: Mining +0.05 Stamina, Foraging +0.1 Health, Farming +0.25 Health, Combat +0.1 Health per level =
     +5 Stamina / +10 / +25 / +10 Health at 100), applied once per second on the world thread by the Acrobatics player tick as
     EntityStatMap StaticModifier(MAX, ADDITIVE) keys skyyskill_health / skyyskill_stamina / skyyskill_mana (SkyyAccessories
     AccEffects pattern; the modifiers are saved with the player - they are removed again when their amount becomes 0, e.g.
     perk.enabled=false, but NOT when the mod is uninstalled). DOUBLE DROPS: Mining (every block that pays Mining XP), Foraging
     (logs: doubleDropOnly=_Trunk) and Farming (ripe crops, broken or F-harvested) roll level x 0.5% (50% at 100, capped by
     perk.doubleDropMax) to give the block's drops once more, straight into the player's storage/hotbar/backpack
     (Inventory.getCombinedStorageHotbarBackpack + SimpleItemContainer.addOrDropItemStack, dropped at the feet when full).
     The drops are computed exactly like the engine (bytecode 2026-09-23): break = BlockHarvestUtils.getDrops(blockType,
     Breaking.Quantity, Breaking.ItemId, Breaking.DropListId) (BlockHarvestUtils.damageSingleBlock -> performBlockBreak ->
     naturallyRemoveBlock), soft blocks (crops) = getDrops(bt, 1, Soft.ItemId, Soft.DropListId), F-harvest = getDrops(bt, 1,
     Harvest.ItemId, Harvest.DropListId) (FarmingUtil.giveDrops). A drop LIST is rolled again (same odds, not a copy of the
     first roll's result). Never doubled: placed blocks (needs ignorePlaced=true - the placed-block tracker), blocks whose drops
     depend on the tool (a Gathering.Tools entry without State, e.g. Soil_Gravel + pickaxe, shears on plants), blocks with both
     Soft and Breaking drops. "Double drop!" chat line at most once per feedbackMs (perk.doubleDropMessage, /skills quiet).
     CLASS COMBAT (Skyy: "combat will be based on your class"): the Combat row shows your class skill (class:<uuid> /
     class:skill:<uuid> from SkyyClasses; "Combat - choose a class with /class" without one). Combat XP only with a class AND a
     kill made with a weapon SkyyClasses allows for it (bridge class:fn:allowed on the attacker's main-hand item, then the active
     utility item - the Kunai), plus (combat.classWeaponOnly=true) one of the class's own weapons (class:weapons:<Class>), so
     tools / fists / shields earn nothing. No class:fn:allowed (SkyyClasses missing) = no combat XP; each reason is told to the
     player once per session. XP is stored PER CLASS (players/<uuid>.properties "Combat.Archer" .. "Combat.Mage", slots 5-9 with
     their own paid markers), so switching class keeps every class's level. Legacy "Combat" XP (0.1/0.2) moves ONCE to the class
     the player has when 0.3 first sees him with a class while every class slot is still 0 (chat line); after that slot 3 stays 0.
     Combat perk: +0.2% damage per class level with class weapons (CombatDmgSys = DamageEventSystem in the Filter group, Query.any;
     skips cancelled damage - SkyyClasses' DamageLock cancels AND zeroes, so either system order is safe; monsters only unless
     perk.combat.damageVsPlayers=true) and +0.1 max Health per class level. Known edge (same as SkyyClasses): an arrow is judged
     by what the shooter holds when it lands.
     BRIDGE: skill:<uuid> = "Mining:12,Foraging:3,Farming:0,Combat:5,Acrobatics:2,Archery:5" (the five rows, Combat = current class
     skill level, then every class skill that is current or has XP); skill:fn:level also answers class skill names, class names
     and "Combat" (= current class skill). Republished on the player's first Acrobatics tick of a session (SkyyClasses may publish
     class:<uuid> after our 5 s publishOnline already published him, and publishOnline never republishes a published player) and
     whenever the player's class changes.
     COMMANDS (HANDOFF command rules): /skills (alias /skill) + stats <skill> + top <skill> + quiet carry
     setPermissionGroups({"hytale:Adventurer"}); reload = requirePermission("skyyskills.admin") + setPermissionGroups(new String[0])
     (does not inherit the Adventurer group). Skill args: mining foraging farming acrobatics combat archery swordsmanship
     assassination berserking sorcery (or a class name; 3+ letter prefixes work).
0.2 notes:
''')
rep('VERSION = "0.2"', 'VERSION = "0.3"')

# ---------------------------------------------------------------- 0.3 API constants + probes
rep('''SYG = "com.hypixel.hytale.component.SystemGroup"
''', r'''SYG = "com.hypixel.hytale.component.SystemGroup"
# 0.3 perks / class combat API (verified with reflect.py / bcfull.py against HytaleServer.jar 2026-09-23, see tools/skills_0_3_patch.py)
BHU = "com.hypixel.hytale.server.core.modules.interaction.BlockHarvestUtils"
BBD = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockBreakingDropType"
SBD = "com.hypixel.hytale.server.core.asset.type.blocktype.config.SoftBlockDropType"
HDT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.HarvestingDropType"
BTD = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering$BlockToolData"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
INVC= "com.hypixel.hytale.server.core.inventory.InventoryComponent"
UTIL= "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
CAC = "com.hypixel.hytale.component.ComponentAccessor"
MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
MTG = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier$ModifierTarget"
CAL = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier$CalculationType"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
''')
rep('''MV.probe(B, pool)
''', r'''MV.probe(B, pool)
for c, m in ((BHU, "getDrops"), (BGA, "getBreaking"), (BGA, "getSoft"), (BGA, "isSoft"), (BGA, "getToolData"), (BGA, "getHarvest"),
             (BBD, "getQuantity"), (BBD, "getItemId"), (BBD, "getDropListId"), (SBD, "getItemId"), (SBD, "getDropListId"),
             (HDT, "getItemId"), (HDT, "getDropListId"), (BTD, "getStateId"), (IS, "getItemId"), (IS, "isEmpty"), (IS, "getQuantity"),
             (INVC, "getItemInHand"), (UTIL, "getComponentType"), (UTIL, "getActiveItem"), (PLA, "getInventory"),
             (INV, "getCombinedStorageHotbarBackpack"), (SIC, "addOrDropItemStack"), (PR, "getReference"), (REF, "getStore"),
             (ESM, "putModifier"), (ESM, "removeModifier"), (ESM, "getModifier"), (DST, "getStamina"), (DST, "getMana"),
             (SMO, "getAmount"), (MTG, "MAX"), (CAL, "ADDITIVE"), (QRY, "any"), (DMG, "isCancelled"), (CAC, "getComponent"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "withRequiredArg"), (AC, "addAliases")):
    B.probe(pool, c, m)
''')

# ---------------------------------------------------------------- level table to 100
rep('''assert len(LEVELS) == 50
''', r'''assert len(LEVELS) == 50
LEVELS_OLD50 = list(LEVELS)   # the 0.1/0.2 default: an xp.properties still carrying exactly this levels= line is upgraded on load
# 0.3: max level 100 (Skyy). Levels 51-60 = Hypixel SkyBlock's own 51-60 (4.3M .. 7.0M, +300k per level); 61-100 continue that
# +300k step (level 100 needs 19,000,000 XP; 0 -> 60 = Hypixel's 111,672,425, 0 -> 100 = 637,672,425).
LEVELS = LEVELS + [4300000 + 300000 * i for i in range(50)]
assert len(LEVELS) == 100 and LEVELS[59] == 7000000 and sum(LEVELS[:60]) == 111672425 and LEVELS[99] == 19000000
''')

# ---------------------------------------------------------------- xp.properties defaults
rep('L.append("#   <Skill>:0 or none = no XP.  Skill = Mining | Foraging | Farming   (Combat comes from kills, see combat.*)")',
    'L.append("#   <Skill>:0 or none = no XP.  Skill = Mining | Foraging | Farming   (Combat = your class skill, from kills, see combat.*)")')
rep('L.append("# XP needed for each level, level 1 first (Hypixel SkyBlock table; the number of entries is the max level)")',
    'L.append("# XP needed for each level, level 1 first (Hypixel SkyBlock table to 60, then +300k per level; the number of entries")\n'
    'L.append("# is the max level, at most 100)")')
rep('''DEFAULTS = "\\n".join(L) + "\\n"
''', r'''# 0.3: perks + class combat - also appended once to an existing xp.properties that has no perk.* key (PerkCfg.ensureDefaults)
PERK_L = []
PERK_L.append("# ---------- Perks (SkyySkills 0.3) - the FLAT layer: skills add flat amounts to the default stats ----------")
PERK_L.append("# Comments must stay on their own lines. Every skill (mining, foraging, farming, combat, acrobatics) accepts")
PERK_L.append("#   perk.<skill>.healthPerLevel / staminaPerLevel / manaPerLevel = max stat added per level (summed over all skills and")
PERK_L.append("#   applied as MAX modifiers skyyskill_health / skyyskill_stamina / skyyskill_mana; vanilla max: 100 health, 10 stamina)")
PERK_L.append("#   perk.<skill>.doubleDropPerLevel = chance per level (0.005 = 0.5 percent, 50 percent at level 100) that a block which paid")
PERK_L.append("#   that skill's XP gives its drops a second time, straight into your inventory (mining, foraging, farming; capped by")
PERK_L.append("#   perk.doubleDropMax). perk.<skill>.doubleDropOnly = comma list of id parts: only blocks whose id contains one can double")
PERK_L.append("#   (empty = every block of that skill). Placed blocks never double (needs ignorePlaced=true), neither do blocks whose")
PERK_L.append("#   drops depend on the tool (gravel + pickaxe, shears on plants).")
PERK_L.append("perk.enabled=true")
PERK_L.append("perk.doubleDropMax=1.0")
PERK_L.append("perk.doubleDropMessage=true")
PERK_L.append("perk.mining.staminaPerLevel=0.05")
PERK_L.append("perk.mining.doubleDropPerLevel=0.005")
PERK_L.append("perk.mining.doubleDropOnly=")
PERK_L.append("perk.foraging.healthPerLevel=0.1")
PERK_L.append("perk.foraging.doubleDropPerLevel=0.005")
PERK_L.append("perk.foraging.doubleDropOnly=_Trunk")
PERK_L.append("perk.farming.healthPerLevel=0.25")
PERK_L.append("perk.farming.doubleDropPerLevel=0.005")
PERK_L.append("perk.farming.doubleDropOnly=")
PERK_L.append("# Combat = your CLASS skill (needs SkyyClasses); perk.combat.* uses the level of your current class. damagePerLevel = extra")
PERK_L.append("# damage with your class weapons (0.002 = +0.2 percent per level, +20 percent at 100), vs monsters only unless damageVsPlayers=true.")
PERK_L.append("perk.combat.healthPerLevel=0.1")
PERK_L.append("perk.combat.damagePerLevel=0.002")
PERK_L.append("perk.combat.damageVsPlayers=false")
PERK_L.append("# Combat XP only with a class (/class) and only for kills with a weapon SkyyClasses allows for it (bridge class:fn:allowed);")
PERK_L.append("# classWeaponOnly=true also needs one of the class's own weapons (class:weapons:<Class>), so tools and fists earn nothing.")
PERK_L.append("# Each class keeps its own level (Combat.<Class> in players/<uuid>.properties).")
PERK_L.append("combat.classWeaponOnly=true")
L.append("")
L.extend(PERK_L)
PERK_DEFAULTS = "\n".join(PERK_L) + "\n"
assert all(ord(ch) < 128 for ch in PERK_DEFAULTS)
PERK_LIT = json.dumps(PERK_DEFAULTS)
DEFAULTS = "\n".join(L) + "\n"
''')

# ---------------------------------------------------------------- new classes
rep('''afs  = pool.makeClass(PKG + ".AcroFallSys", pool.get(DEVS))
''', '''afs  = pool.makeClass(PKG + ".AcroFallSys", pool.get(DEVS))
pcfg = pool.makeClass(PKG + ".PerkCfg")
scls = pool.makeClass(PKG + ".SkillClass")
perk = pool.makeClass(PKG + ".Perks")
cds  = pool.makeClass(PKG + ".CombatDmgSys", pool.get(DEVS))
spg  = pool.makeClass(PKG + ".StatsPage", pool.get(PAGE))
scmd = pool.makeClass(PKG + ".StatsCmd", pool.get(APC))
''')

# ---------------------------------------------------------------- SkillDefs: 10 storage slots (5 rows + one combat skill per class)
rep('''defs.addField(CtField.make('public static final String[] NAMES = new String[] { "Mining", "Foraging", "Farming", "Combat", "Acrobatics" };', defs))
defs.addField(CtField.make('public static final String[] ICONS = new String[] { %s };' % ", ".join('"%s"' % i for i in ICONS), defs))
defs.addField(CtField.make('public static final String[] COLORS = new String[] { "#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff" };', defs))
defs.addField(CtField.make("public static final int N = 5;", defs))
''', r'''# 0.3 storage slots: 0-4 as in 0.2 (slot 3 "Combat" = legacy classless XP, no longer earned), 5-9 = one combat skill per class
# (SkyyClasses roster, HANDOFF "Skills + classes design"). NAMES = keys in players/<uuid>.properties, LABELS = what players see,
# N = storage slots (data array long[2*N], paid markers at N+slot), ROWS = rows on /skills (row 3 shows the current class slot).
CLASS_ROWS = [("Archer", "Archery", "Weapon_Shortbow_Iron", "#8fd67a"), ("Warrior", "Swordsmanship", "Weapon_Sword_Iron", "#e0b060"),
              ("Assassin", "Assassination", "Weapon_Daggers_Iron", "#b58cff"), ("Berserker", "Berserking", "Weapon_Battleaxe_Iron", "#ff7a5c"),
              ("Mage", "Sorcery", "Weapon_Staff_Iron", "#7fb0e0")]
for _c in CLASS_ROWS: must(_c[2])
SLOT_NAMES = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + ["Combat." + c[0] for c in CLASS_ROWS]
SLOT_LABELS = ["Mining", "Foraging", "Farming", "Combat", "Acrobatics"] + [c[1] for c in CLASS_ROWS]
SLOT_ICONS = ICONS + [c[2] for c in CLASS_ROWS]
SLOT_COLORS = ["#8fc8ff", "#8fe08a", "#f0d060", "#ff8a7a", "#c8a0ff"] + [c[3] for c in CLASS_ROWS]
assert len(SLOT_NAMES) == len(SLOT_LABELS) == len(SLOT_ICONS) == len(SLOT_COLORS) == 10
def jarr(xs): return "new String[] { " + ", ".join('"%s"' % x for x in xs) + " }"
defs.addField(CtField.make("public static final String[] NAMES = %s;" % jarr(SLOT_NAMES), defs))
defs.addField(CtField.make("public static final String[] LABELS = %s;" % jarr(SLOT_LABELS), defs))
defs.addField(CtField.make("public static final String[] ICONS = %s;" % jarr(SLOT_ICONS), defs))
defs.addField(CtField.make("public static final String[] COLORS = %s;" % jarr(SLOT_COLORS), defs))
defs.addField(CtField.make("public static final String[] CLASSES = %s;" % jarr([c[0] for c in CLASS_ROWS]), defs))
defs.addField(CtField.make("public static final int N = %d;" % len(SLOT_NAMES), defs))
defs.addField(CtField.make("public static final int ROWS = 5;", defs))
defs.addField(CtField.make("public static final int CLASS0 = 5;", defs))
''')
rep('defs.addField(CtField.make("public static volatile int MAX = 50;", defs))',
    'defs.addField(CtField.make("public static volatile int MAX = 100;", defs))')
rep('''  for (int i = 0; i < NAMES.length; i++) if (NAMES[i].toLowerCase().equals(t)) return i;
  if (t.length() >= 3) for (int i = 0; i < NAMES.length; i++) if (NAMES[i].toLowerCase().startsWith(t)) return i;
  return -1;
''', '''  for (int i = 0; i < LABELS.length; i++) if (LABELS[i].toLowerCase().equals(t) || NAMES[i].toLowerCase().equals(t)) return i;
  for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().equals(t)) return CLASS0 + i;
  if (t.length() >= 3) {
    for (int i = 0; i < LABELS.length; i++) if (LABELS[i].toLowerCase().startsWith(t)) return i;
    for (int i = 0; i < CLASSES.length; i++) if (CLASSES[i].toLowerCase().startsWith(t)) return CLASS0 + i;
  }
  return -1;
''')
# block rules may only name the three gathering skills (class skills now resolve too)
rep('  if (sk < 0 || sk == {PKG}.SkillDefs.COMBAT || sk == {PKG}.SkillDefs.ACROBATICS) return null;',
    '  if (sk < 0 || sk > {PKG}.SkillDefs.FARMING) return null;')

# ---------------------------------------------------------------- PerkCfg + levels upgrade (before SkillCfg.load)
rep('''cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''', r'''# ================= PerkCfg: perk.* keys (+ combat.classWeaponOnly) of xp.properties (0.3) =================
pcfg.addField(CtField.make("public static final String DEFAULTS = " + PERK_LIT + ";", pcfg))
pcfg.addField(CtField.make('public static final String[] KEYS = new String[] { "mining", "foraging", "farming", "combat", "acrobatics" };', pcfg))
for _decl in ("boolean ENABLED = true", "double DD_MAX = 1.0", "boolean DD_MSG = true", "double DMG = 0.002", "boolean DMG_PVP = false",
              "boolean WEAPON_ONLY = true", "double[] HP = new double[] { 0.0, 0.1, 0.25, 0.1, 0.0 }",
              "double[] STA = new double[] { 0.05, 0.0, 0.0, 0.0, 0.0 }", "double[] MANA = new double[] { 0.0, 0.0, 0.0, 0.0, 0.0 }",
              "double[] DD = new double[] { 0.005, 0.005, 0.005, 0.0, 0.0 }", 'String[] ONLY = new String[] { "", "_Trunk", "", "", "" }'):
    pcfg.addField(CtField.make("public static volatile %s;" % _decl, pcfg))
# a rate is never negative (skills only ADD in the flat layer; gear will carry the trade-offs); bad / negative -> 0
pcfg.addMethod(CtNewMethod.make(f"""
public static double rate(java.util.Properties p, String k, double d) {{
  double v = {PKG}.SkillCfg.dbl(p, k, d);
  if (Double.isNaN(v) || Double.isInfinite(v) || v < 0.0) return 0.0;
  return v;
}}""", pcfg))
pcfg.addMethod(CtNewMethod.make(f"""
public static void read(java.util.Properties p) {{
  ENABLED = {PKG}.SkillCfg.bool(p, "perk.enabled", true);
  DD_MAX = Math.min(1.0, rate(p, "perk.doubleDropMax", 1.0));
  DD_MSG = {PKG}.SkillCfg.bool(p, "perk.doubleDropMessage", true);
  double[] dhp = new double[] {{ 0.0, 0.1, 0.25, 0.1, 0.0 }};
  double[] dsta = new double[] {{ 0.05, 0.0, 0.0, 0.0, 0.0 }};
  double[] ddd = new double[] {{ 0.005, 0.005, 0.005, 0.0, 0.0 }};
  String[] donly = new String[] {{ "", "_Trunk", "", "", "" }};
  double[] hp = new double[5];
  double[] sta = new double[5];
  double[] mana = new double[5];
  double[] dd = new double[5];
  String[] only = new String[5];
  for (int i = 0; i < 5; i++) {{
    String k = "perk." + KEYS[i] + ".";
    hp[i] = rate(p, k + "healthPerLevel", dhp[i]);
    sta[i] = rate(p, k + "staminaPerLevel", dsta[i]);
    mana[i] = rate(p, k + "manaPerLevel", 0.0);
    dd[i] = i <= 2 ? rate(p, k + "doubleDropPerLevel", ddd[i]) : 0.0;
    String o = p.getProperty(k + "doubleDropOnly");
    only[i] = o == null ? donly[i] : o.trim();
  }}
  HP = hp; STA = sta; MANA = mana; DD = dd; ONLY = only;
  DMG = rate(p, "perk.combat.damagePerLevel", 0.002);
  DMG_PVP = {PKG}.SkillCfg.bool(p, "perk.combat.damageVsPlayers", false);
  WEAPON_ONLY = {PKG}.SkillCfg.bool(p, "combat.classWeaponOnly", true);
}}""", pcfg))
# an xp.properties written by 0.1 / 0.2 has no perk.* key: append the documented section once (the code defaults apply either way)
pcfg.addMethod(CtNewMethod.make(f"""
public static void ensureDefaults(java.util.Properties p) {{
  java.util.Enumeration en = p.propertyNames();
  while (en.hasMoreElements()) {{
    if (String.valueOf(en.nextElement()).startsWith("perk.")) return;
  }}
  try {{
    java.nio.file.Files.write({PKG}.SkillCfg.FILE, ("\\n" + DEFAULTS).getBytes("UTF-8"), new java.nio.file.OpenOption[] {{ java.nio.file.StandardOpenOption.APPEND }});
    {PKG}.SkillCfg.info("xp.properties: appended the perks + class combat section (perk.* keys, default values)");
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("could not append the perk.* section to xp.properties: " + t); }}
}}""", pcfg))
# 0.3: the 0.1/0.2 default levels= line (50 levels) -> the 100-level table, in memory AND in the file (custom tables are kept)
cfg.addField(CtField.make('public static final String OLD_LEVELS = "%s";' % ",".join(str(x) for x in LEVELS_OLD50), cfg))
cfg.addField(CtField.make('public static final String NEW_LEVELS = "%s";' % ",".join(str(x) for x in LEVELS), cfg))
cfg.addMethod(CtNewMethod.make("""
public static String squash(String v) {
  if (v == null) return "";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length(); i++) { char c = v.charAt(i); if (c != ' ' && c != '\\t') sb.append(c); }
  return sb.toString();
}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static void upgradeLevels(java.util.Properties p) {{
  if (!OLD_LEVELS.equals(squash(p.getProperty("levels")))) return;
  p.setProperty("levels", NEW_LEVELS);
  try {{
    java.util.List lines = java.nio.file.Files.readAllLines(FILE, java.nio.charset.StandardCharsets.UTF_8);
    StringBuilder sb = new StringBuilder();
    boolean done = false;
    for (int i = 0; i < lines.size(); i++) {{
      String ln = (String) lines.get(i);
      String t = ln.trim();
      if (!done && t.startsWith("levels=") && OLD_LEVELS.equals(squash(t.substring(7)))) {{
        sb.append("# SkyySkills 0.3: max level 100 - the old 50-level default table was extended (levels 1-50 unchanged)\\n");
        sb.append("levels=").append(NEW_LEVELS).append("\\n");
        done = true;
      }} else {{
        sb.append(ln).append("\\n");
      }}
    }}
    if (!done) return;
    java.nio.file.Path tmp = FILE.resolveSibling("xp.properties.tmp");
    java.nio.file.Files.write(tmp, sb.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] {{ java.nio.file.StandardCopyOption.REPLACE_EXISTING }});
    info("xp.properties: levels= upgraded from the old 50-level default to the 100-level table (levels 1-50 unchanged)");
  }} catch (Throwable t) {{ warn("could not rewrite the levels= line of xp.properties (the 100-level table is used anyway): " + t); }}
}}""", cfg))
cfg.addMethod(CtNewMethod.make(f"""
public static synchronized String load() {{''')
rep('''    {PKG}.AcroCfg.ensureDefaults(p);
''', '''    upgradeLevels(p);
    {PKG}.AcroCfg.ensureDefaults(p);
    {PKG}.PerkCfg.ensureDefaults(p);
''')
rep('''    {PKG}.AcroCfg.read(p);
''', '''    {PKG}.AcroCfg.read(p);
    {PKG}.PerkCfg.read(p);
''')
rep('''+ " role rule(s), acrobatics " + ({PKG}.AcroCfg.ENABLED ? "on" : "off") + ", max level "''',
    '''+ " role rule(s), acrobatics " + ({PKG}.AcroCfg.ENABLED ? "on" : "off") + ", perks " + ({PKG}.PerkCfg.ENABLED ? "on" : "off") + ", max level "''')

# ---------------------------------------------------------------- SkillClass (right after SkillStore.bridge())
rep('''sto.addField(CtField.make("public static final Object IO = new Object();", sto))
''', r'''# ================= SkillClass (0.3): the player's class from SkyyClasses (bridge), class combat rules =================
scls.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();", scls))
scls.addMethod(CtNewMethod.make(f"""
public static int slotOfClass(String c) {{
  if (c == null) return -1;
  String t = c.trim();
  for (int i = 0; i < {PKG}.SkillDefs.CLASSES.length; i++) if ({PKG}.SkillDefs.CLASSES[i].equalsIgnoreCase(t)) return {PKG}.SkillDefs.CLASS0 + i;
  return -1;
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static String className(java.util.UUID u) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("class:" + u.toString());
    if (!(o instanceof String)) return null;
    String c = ((String) o).trim();
    return c.length() == 0 ? null : c;
  }} catch (Throwable t) {{ return null; }}
}}""", scls))
scls.addMethod(CtNewMethod.make("""
public static int slot(java.util.UUID u) {
  return slotOfClass(className(u));
}""", scls))
# storage slot a /skills row shows: the Combat row = the current class's skill (legacy slot 3 without a class)
scls.addMethod(CtNewMethod.make(f"""
public static int rowSlot(java.util.UUID u, int row) {{
  if (row != {PKG}.SkillDefs.COMBAT) return row;
  int c = slot(u);
  return c >= 0 ? c : {PKG}.SkillDefs.COMBAT;
}}""", scls))
# display name of a slot: the class skill name SkyyClasses publishes for the CURRENT class (class:skill:<uuid>), else our label
scls.addMethod(CtNewMethod.make(f"""
public static String skillName(java.util.UUID u, int s) {{
  if (s < 0 || s >= {PKG}.SkillDefs.N) return "?";
  if (s >= {PKG}.SkillDefs.CLASS0 && s == slot(u)) {{
    try {{
      Object o = {PKG}.SkillStore.bridge().get("class:skill:" + u.toString());
      if (o instanceof String && ((String) o).trim().length() > 0) return ((String) o).trim();
    }} catch (Throwable t) {{ }}
  }}
  return {PKG}.SkillDefs.LABELS[s];
}}""", scls))
# "Weapon_Shortbow_,Weapon_Crossbow_" (bridge class:weapons:<Class>) -> "Shortbow / Crossbow"; null when not published
scls.addMethod(CtNewMethod.make(f"""
public static String weaponsText(String cls) {{
  try {{
    Object o = {PKG}.SkillStore.bridge().get("class:weapons:" + cls);
    if (!(o instanceof String)) return null;
    String[] ps = ((String) o).split(",");
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < ps.length; i++) {{
      String w = ps[i].trim();
      if (w.startsWith("Weapon_")) w = w.substring(7);
      while (w.endsWith("_")) w = w.substring(0, w.length() - 1);
      w = w.replace('_', ' ').trim();
      if (w.length() == 0) continue;
      if (sb.length() > 0) sb.append(" / ");
      sb.append(w);
    }}
    return sb.length() == 0 ? null : sb.toString();
  }} catch (Throwable t) {{ return null; }}
}}""", scls))
# one chat line per reason (bit) per player per session; TOLD is pruned to online players by Acro.retainOnline
scls.addMethod(CtNewMethod.make("""
public static synchronized boolean claimTold(java.util.UUID u, int bit) {
  Integer m = (Integer) TOLD.get(u);
  int v = m == null ? 0 : m.intValue();
  if ((v & bit) != 0) return false;
  TOLD.put(u, Integer.valueOf(v | bit));
  return true;
}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static void tellOnce({PR} pr, int bit, String text) {{
  try {{
    if (claimTold(pr.getUuid(), bit)) pr.sendMessage({MSG}.raw("[Skills] " + text).color("#ffb080"));
  }} catch (Throwable t) {{ }}
}}""", scls))
scls.addMethod(CtNewMethod.make(f"""
public static java.util.function.Function allowedFn() {{
  Object f = {PKG}.SkillStore.bridge().get("class:fn:allowed");
  return f instanceof java.util.function.Function ? (java.util.function.Function) f : null;
}}""", scls))
# may this item earn / boost class combat: SkyyClasses allows it for this player AND (classWeaponOnly) it is one of the class's own
# weapons (prefix list class:weapons:<Class>; when that key is missing the allowed answer alone decides)
scls.addMethod(CtNewMethod.make(f"""
public static boolean itemOk(java.util.UUID u, {IS} it, java.util.function.Function f, String prefixes) {{
  if (it == null || it.isEmpty()) return false;
  String id = it.getItemId();
  if (id == null || id.length() == 0) return false;
  Object r = null;
  try {{ r = f.apply(new Object[] {{ u, id }}); }} catch (Throwable t) {{ return false; }}
  if (!Boolean.TRUE.equals(r)) return false;
  if (!{PKG}.PerkCfg.WEAPON_ONLY || prefixes == null) return true;
  String[] ps = prefixes.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String p = ps[i].trim();
    if (p.length() > 0 && id.startsWith(p)) return true;
  }}
  return false;
}}""", scls))
# the weapon a hit / kill was made with = the attacker's main-hand item, else the active utility item (the Kunai is thrown from the
# utility slot) - the same two places SkyyClasses' DamageLock judges (InventoryComponent.getItemInHand, vanilla DamageAttackerTool)
scls.addMethod(CtNewMethod.make(f"""
public static boolean weaponOk(java.util.UUID u, int slot, java.util.function.Function f, {CAC} acc, {REF} att) {{
  if (slot < {PKG}.SkillDefs.CLASS0 || slot >= {PKG}.SkillDefs.N) return false;
  Object po = {PKG}.SkillStore.bridge().get("class:weapons:" + {PKG}.SkillDefs.CLASSES[slot - {PKG}.SkillDefs.CLASS0]);
  String prefixes = po instanceof String ? (String) po : null;
  try {{ if (itemOk(u, {INVC}.getItemInHand(acc, att), f, prefixes)) return true; }} catch (Throwable t) {{ }}
  try {{
    {UTIL} ut = ({UTIL}) acc.getComponent(att, {UTIL}.getComponentType());
    if (ut != null && itemOk(u, ut.getActiveItem(), f, prefixes)) return true;
  }} catch (Throwable t) {{ }}
  return false;
}}""", scls))
# storage slot that earns this kill's combat XP, or -1 (and the reason is told once): SkyyClasses present, a class, a known class,
# a class weapon
scls.addMethod(CtNewMethod.make(f"""
public static int killSlot({PR} pr, {CAC} acc, {REF} att) {{
  java.util.UUID u = pr.getUuid();
  java.util.function.Function f = allowedFn();
  if (f == null) {{ tellOnce(pr, 1, "Combat XP comes from your class skill, but SkyyClasses is not installed on this server - no combat XP is awarded."); return -1; }}
  String c = className(u);
  if (c == null) {{ tellOnce(pr, 2, "Choose a class with /class to earn combat XP - your combat skill is your class skill."); return -1; }}
  int s = slotOfClass(c);
  if (s < 0) {{ tellOnce(pr, 4, "Your class " + c + " has no combat skill in SkyySkills yet - no combat XP."); return -1; }}
  if (!weaponOk(u, s, f, acc, att)) {{
    String w = weaponsText({PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0]);
    tellOnce(pr, 8, "Only kills with your " + c + " weapons" + (w == null ? "" : " (" + w + ")") + " earn " + skillName(u, s) + " XP.");
    return -1;
  }}
  return s;
}}""", scls))
# /skills top|stats <skill>: "combat" = your class skill (the legacy Combat slot without a class)
scls.addMethod(CtNewMethod.make(f"""
public static int argSlot({PR} pr, String arg) {{
  int s = {PKG}.SkillDefs.indexOf(arg);
  if (s < 0) {{
    pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming, acrobatics, combat (your class skill) or a class skill: archery, swordsmanship, assassination, berserking, sorcery."));
    return -1;
  }}
  if (s == {PKG}.SkillDefs.COMBAT) {{ int c = slot(pr.getUuid()); if (c >= 0) return c; }}
  return s;
}}""", scls))
sto.addField(CtField.make("public static final Object IO = new Object();", sto))
''')

# ---------------------------------------------------------------- SkillStore: bridge string, legacy combat move
rep('''  long[] d = data(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
    if (i > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.NAMES[i]).append(':').append({PKG}.SkillDefs.levelOf(d[i]));
  }}
  return sb.toString();
''', '''  long[] d = data(u);
  int cs = {PKG}.SkillClass.slot(u);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < {PKG}.SkillDefs.ROWS; i++) {{
    int s = i == {PKG}.SkillDefs.COMBAT && cs >= 0 ? cs : i;
    if (i > 0) sb.append(',');
    sb.append({PKG}.SkillDefs.LABELS[i]).append(':').append({PKG}.SkillDefs.levelOf(d[s]));
  }}
  for (int s = {PKG}.SkillDefs.CLASS0; s < {PKG}.SkillDefs.N; s++) {{
    if (s != cs && d[s] <= 0L) continue;
    sb.append(',').append({PKG}.SkillDefs.LABELS[s]).append(':').append({PKG}.SkillDefs.levelOf(d[s]));
  }}
  return sb.toString();
''')
rep('''sto.addMethod(CtNewMethod.make(f"""
public static long[] add(java.util.UUID u, String name, int skill, long amount) {{''', r'''# 0.3: legacy "Combat" XP (slot 3) -> the class slot, only while every class slot is still 0; returns the XP moved or -1
sto.addMethod(CtNewMethod.make(f"""
public static synchronized long moveLegacy(long[] d, int slot) {{
  int c = {PKG}.SkillDefs.COMBAT;
  int n = {PKG}.SkillDefs.N;
  if (slot < {PKG}.SkillDefs.CLASS0 || slot >= n || d[c] <= 0L) return -1L;
  for (int k = {PKG}.SkillDefs.CLASS0; k < n; k++) if (d[k] > 0L) return -1L;
  long x = d[c];
  d[slot] = x;
  d[n + slot] = d[n + c] < 0L ? 0L : d[n + c];
  d[c] = 0L;
  d[n + c] = 0L;
  return x;
}}""", sto))
sto.addMethod(CtNewMethod.make(f"""
public static long[] add(java.util.UUID u, String name, int skill, long amount) {{''')

# ---------------------------------------------------------------- SkillFn / SkillMsg / SkillXp: labels, Combat = class skill
rep('''    if (i < 0) return Integer.valueOf(0);
    return Integer.valueOf({PKG}.SkillStore.level((java.util.UUID) a[0], i));
''', '''    if (i < 0) return Integer.valueOf(0);
    java.util.UUID u = (java.util.UUID) a[0];
    if (i == {PKG}.SkillDefs.COMBAT) i = {PKG}.SkillClass.rowSlot(u, i);
    return Integer.valueOf({PKG}.SkillStore.level(u, i));
''')
rep('.append({PKG}.SkillDefs.NAMES[i]).append(" XP (")', '.append({PKG}.SkillDefs.LABELS[i]).append(" XP (")')
rep('  String sk = {PKG}.SkillDefs.NAMES[skill];', '  String sk = {PKG}.SkillDefs.LABELS[skill];')

# ---------------------------------------------------------------- Perks (before the Acrobatics section: AcroSys, BreakTask, HarvestTask call it)
rep('''# ================= 0.2 ACROBATICS =================
''', r'''# ================= Perks (0.3): flat stat perks, legacy combat migration, double drops =================
perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap LASTCLS = new java.util.concurrent.ConcurrentHashMap();", perk))
perk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DDMSG = new java.util.concurrent.ConcurrentHashMap();", perk))
perk.addField(CtField.make("public static boolean FAILED_ONCE = false;", perk))
perk.addField(CtField.make("public static boolean DD_FAILED_ONCE = false;", perk))
# level a perk row uses: Combat = the current class's level (no class = no combat perks)
perk.addMethod(CtNewMethod.make(f"""
public static int rowLevel(java.util.UUID u, int row) {{
  if (row == {PKG}.SkillDefs.COMBAT) {{
    int s = {PKG}.SkillClass.slot(u);
    return s < 0 ? 0 : {PKG}.SkillStore.level(u, s);
  }}
  return {PKG}.SkillStore.level(u, row);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static float flat(double per, int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || lvl <= 0 || per <= 0.0) return 0.0f;
  return (float) (Math.round(per * lvl * 100.0) / 100.0);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static float total(double[] per, int[] lv) {{
  double sum = 0.0;
  for (int r = 0; r < lv.length && r < per.length; r++) sum = sum + flat(per[r], lv[r]);
  return (float) (Math.round(sum * 100.0) / 100.0);
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static int[] levels(java.util.UUID u) {{
  int[] lv = new int[{PKG}.SkillDefs.ROWS];
  for (int r = 0; r < lv.length; r++) lv[r] = rowLevel(u, r);
  return lv;
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static double chance(int row, int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || row < 0 || row > {PKG}.SkillDefs.FARMING || lvl <= 0) return 0.0;
  double c = lvl * {PKG}.PerkCfg.DD[row];
  return c > {PKG}.PerkCfg.DD_MAX ? {PKG}.PerkCfg.DD_MAX : c;
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static double damage(int lvl) {{
  if (!{PKG}.PerkCfg.ENABLED || lvl <= 0) return 0.0;
  return lvl * {PKG}.PerkCfg.DMG;
}}""", perk))
# set (amt != 0) or remove (amt == 0) our MAX modifier on one stat - SkyyAccessories AccEffects.mod (TerrariaAddons pattern)
perk.addMethod(CtNewMethod.make(f"""
public static void mod({ESM} m, int idx, String key, float amt) {{
  if (idx < 0) return;
  try {{
    if (m.get(idx) == null) return;
    {MOD} cur = m.getModifier(idx, key);
    if (amt == 0.0f) {{ if (cur != null) m.removeModifier(idx, key); return; }}
    {SMO} want = new {SMO}({MTG}.MAX, {CAL}.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, key, want);
  }} catch (Throwable t) {{ }}
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static void migrate({PR} pr, java.util.UUID u, int slot) {{
  long x = {PKG}.SkillStore.moveLegacy({PKG}.SkillStore.data(u), slot);
  if (x <= 0L) return;
  {PKG}.SkillStore.DIRTY.put(u, Boolean.TRUE);
  {PKG}.SkillStore.publish(u);
  {PKG}.SkillCfg.info("moved legacy Combat XP " + x + " of " + u + " to " + {PKG}.SkillDefs.NAMES[slot]);
  pr.sendMessage({MSG}.raw("[Skills] Your old Combat XP (level " + {PKG}.SkillDefs.levelOf(x) + ") now counts for " + {PKG}.SkillClass.skillName(u, slot) + ". Each class keeps its own combat level.").color("#ffc800"));
}}""", perk))
# once per second per player from AcroSys (world thread): first tick of the session or class change -> republish skill:<uuid>,
# legacy combat move, stat modifiers. The first tick (LASTCLS has no entry: new session / plugin start) always republishes:
# SkyyClasses publishes class:<uuid> from its ReadyTask (scheduler thread), possibly AFTER our 5 s publishOnline already put a
# classless skill:<uuid>, and publishOnline never republishes a player it has published (PUBLISHED) -> the Combat entry would stay
# stale until the next level up. Cheap: one bridge put per player per session.
perk.addMethod(CtNewMethod.make(f"""
public static void tick(java.util.UUID u, {PR} pr, {CB} cb, {REF} ref) {{
  try {{
    int cs = {PKG}.SkillClass.slot(u);
    String cn = cs < 0 ? "" : {PKG}.SkillDefs.CLASSES[cs - {PKG}.SkillDefs.CLASS0];
    Object last = LASTCLS.put(u, cn);
    boolean repub = last == null || !last.equals(cn);
    if (cs >= 0) migrate(pr, u, cs);
    if (repub) {PKG}.SkillStore.publish(u);
    int[] lv = levels(u);
    {ESM} m = ({ESM}) cb.getComponent(ref, {ESM}.getComponentType());
    if (m == null) return;
    mod(m, {DST}.getHealth(), "skyyskill_health", total({PKG}.PerkCfg.HP, lv));
    mod(m, {DST}.getStamina(), "skyyskill_stamina", total({PKG}.PerkCfg.STA, lv));
    mod(m, {DST}.getMana(), "skyyskill_mana", total({PKG}.PerkCfg.MANA, lv));
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("perk tick failed (logged once): " + t); }}
  }}
}}""", perk))
# drops that depend on the held tool (a Gathering.Tools entry WITHOUT State breaks the block with the tool's own drop list,
# BlockHarvestUtils.damageSingleBlock) cannot be reproduced from the event -> such blocks never double. Tools entries WITH a State
# (Scraper -> Stripped on oak trunks) change the block instead of breaking it and fire no BreakBlockEvent.
perk.addMethod(CtNewMethod.make(f"""
public static boolean toolDependent({BGA} g) {{
  try {{
    java.util.Map td = g.getToolData();
    if (td == null || td.isEmpty()) return false;
    java.util.Iterator it = td.values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (o instanceof {BTD} && (({BTD}) o).getStateId() == null) return true;
    }}
    return false;
  }} catch (Throwable t) {{ return true; }}
}}""", perk))
# the engine's break drops (verified bytecode, see the 0.3 notes): Breaking -> getDrops(bt, quantity, itemId, dropListId); a soft
# block (crops) -> getDrops(bt, 1, soft itemId, soft dropListId); both kinds on one block = which one applied is unknown -> none
perk.addMethod(CtNewMethod.make(f"""
public static java.util.List breakDrops({BTY} bt) {{
  if (bt == null) return null;
  {BGA} g = bt.getGathering();
  if (g == null || toolDependent(g)) return null;
  {BBD} br = g.getBreaking();
  if (g.isSoft()) {{
    if (br != null) return null;
    {SBD} so = g.getSoft();
    if (so == null) return null;
    return {BHU}.getDrops(bt, 1, so.getItemId(), so.getDropListId());
  }}
  if (br == null) return null;
  int q = br.getQuantity();
  if (q <= 0) return null;
  return {BHU}.getDrops(bt, q, br.getItemId(), br.getDropListId());
}}""", perk))
# F-harvest drops = FarmingUtil.giveDrops: getDrops(bt, 1, harvest itemId, harvest dropListId)
perk.addMethod(CtNewMethod.make(f"""
public static java.util.List harvestDrops({BTY} bt) {{
  if (bt == null) return null;
  {BGA} g = bt.getGathering();
  if (g == null) return null;
  {HDT} h = g.getHarvest();
  if (h == null) return null;
  return {BHU}.getDrops(bt, 1, h.getItemId(), h.getDropListId());
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static boolean matches(int row, String fam) {{
  String o = {PKG}.PerkCfg.ONLY[row];
  if (o == null || o.trim().length() == 0) return true;
  if (fam == null) return false;
  String[] ps = o.split(",");
  for (int i = 0; i < ps.length; i++) {{
    String p = ps[i].trim();
    if (p.length() > 0 && fam.indexOf(p) >= 0) return true;
  }}
  return false;
}}""", perk))
# world thread (BreakTask / HarvestTask run through world.execute): the extra copy goes into storage > hotbar > backpack, dropped at
# the player's feet when full (SkyySacks 0.6.5 craft output path). Only while the player is still in the world of the block.
perk.addMethod(CtNewMethod.make(f"""
public static String give({PR} pr, java.util.List drops, String world) {{
  if (drops == null || drops.isEmpty() || world == null) return null;
  {REF} r = pr.getReference();
  if (r == null || !r.isValid()) return null;
  {ST} st = r.getStore();
  Object ext = st.getExternalData();
  if (!(ext instanceof {EST})) return null;
  {WLD} w = (({EST}) ext).getWorld();
  if (w == null || !world.equals(w.getName())) return null;
  {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
  if (p == null) return null;
  StringBuilder sb = new StringBuilder();
  int n = 0;
  for (int i = 0; i < drops.size(); i++) {{
    Object o = drops.get(i);
    if (!(o instanceof {IS})) continue;
    {IS} is = ({IS}) o;
    if (is.isEmpty() || is.getItemId() == null) continue;
    {SIC}.addOrDropItemStack(st, r, p.getInventory().getCombinedStorageHotbarBackpack(), is);
    n++;
    if (n <= 3) sb.append(" +").append(is.getQuantity()).append(' ').append(is.getItemId().replace('_', ' '));
  }}
  if (n == 0) return null;
  if (n > 3) sb.append(" ...");
  return sb.toString();
}}""", perk))
# "Double drop!" chat line: at most one per feedbackMs per player (count of doubles since the last line), hidden by /skills quiet
perk.addMethod(CtNewMethod.make(f"""
public static void doubled({PR} pr, java.util.List drops, int row, String world) {{
  String what = give(pr, drops, world);
  if (what == null || !{PKG}.PerkCfg.DD_MSG) return;
  java.util.UUID u = pr.getUuid();
  if ({PKG}.SkillStore.QUIET.containsKey(u)) return;
  long now = System.currentTimeMillis();
  long[] c = (long[]) DDMSG.get(u);
  if (c == null) {{ c = new long[2]; DDMSG.put(u, c); }}
  c[0] = c[0] + 1L;
  if (now - c[1] < {PKG}.SkillCfg.FEEDBACK_MS) return;
  pr.sendMessage({MSG}.raw("Double drop" + (c[0] > 1L ? " x" + c[0] : "") + "!" + what + "  (" + {PKG}.SkillDefs.LABELS[row] + " perk)").color("#b8f0a0"));
  c[0] = 0L;
  c[1] = now;
}}""", perk))
# tracked = the block cannot have been placed by a player (ripe crops, or the placed-block tracker is on and cleared it)
perk.addMethod(CtNewMethod.make(f"""
public static void breakDouble({PR} pr, int row, {BTY} bt, String world, boolean tracked) {{
  try {{
    if (!tracked || row < 0 || row > {PKG}.SkillDefs.FARMING || bt == null) return;
    double c = chance(row, {PKG}.SkillStore.level(pr.getUuid(), row));
    if (c <= 0.0 || !matches(row, {PKG}.SkillCfg.familyId(bt))) return;
    if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
    doubled(pr, breakDrops(bt), row, world);
  }} catch (Throwable t) {{
    if (!DD_FAILED_ONCE) {{ DD_FAILED_ONCE = true; {PKG}.SkillCfg.warn("double drop failed (logged once): " + t); }}
  }}
}}""", perk))
perk.addMethod(CtNewMethod.make(f"""
public static void harvestDouble({PR} pr, {BTY} bt, String world) {{
  try {{
    int row = {PKG}.SkillDefs.FARMING;
    if (bt == null) return;
    double c = chance(row, {PKG}.SkillStore.level(pr.getUuid(), row));
    if (c <= 0.0 || !matches(row, {PKG}.SkillCfg.familyId(bt))) return;
    if (java.util.concurrent.ThreadLocalRandom.current().nextDouble() >= c) return;
    doubled(pr, harvestDrops(bt), row, world);
  }} catch (Throwable t) {{
    if (!DD_FAILED_ONCE) {{ DD_FAILED_ONCE = true; {PKG}.SkillCfg.warn("double drop failed (logged once): " + t); }}
  }}
}}""", perk))

# ================= 0.2 ACROBATICS =================
''')
# prune the new per-player maps with the Acrobatics ones; the perk tick rides on the existing 1 s player tick (world thread)
rep('''    MOVE.keySet().retainAll(online);
''', '''    MOVE.keySet().retainAll(online);
    {PKG}.SkillClass.TOLD.keySet().retainAll(online);
    {PKG}.Perks.LASTCLS.keySet().retainAll(online);
    {PKG}.Perks.DDMSG.keySet().retainAll(online);
''')
rep('''    {PKG}.Acro.bonuses(u, pr, cb, ref);
''', '''    {PKG}.Acro.bonuses(u, pr, cb, ref);
    {PKG}.Perks.tick(u, pr, cb, ref);
''')

# ---------------------------------------------------------------- CombatDmgSys (after AcroFallSys)
rep('''# ================= PlacedStore: positions of player-placed blocks, per world =================
''', r'''# ================= CombatDmgSys (0.3): combat perk = more damage with your class weapons =================
# DamageEventSystem in the FILTER group (like AcroFallSys / SkyyClasses DamageLock), Query.any (the target is usually an NPC).
# Skips cancelled damage; SkyyClasses' DamageLock sets amount 0 AND cancels, so the result is right whichever of the two runs first.
cds.addConstructor(CtNewConstructor.make("public CombatDmgSys() { super(); }", cds))
cds.addField(CtField.make("public static boolean FAILED_ONCE = false;", cds))
cds.addMethod(CtNewMethod.make(f"""
public {QRY} getQuery() {{
  return {QRY}.any();
}}""", cds))
cds.addMethod(CtNewMethod.make(f"""
public {SYG} getGroup() {{
  return {DMM}.get().getFilterDamageGroup();
}}""", cds))
cds.addMethod(CtNewMethod.make(f"""
public void handle(int idx, {ACH} chunk, {ST} st, {CB} buf, {EV} ev) {{
  try {{
    if (!(ev instanceof {DMG})) return;
    {DMG} d = ({DMG}) ev;
    if (d.isCancelled()) return;
    if (!{PKG}.PerkCfg.ENABLED || {PKG}.PerkCfg.DMG <= 0.0) return;
    Object src = d.getSource();
    if (!(src instanceof {DES})) return;
    {REF} att = (({DES}) src).getRef();
    if (att == null || !att.isValid()) return;
    {PR} pr = ({PR}) buf.getComponent(att, {PR}.getComponentType());
    if (pr == null) return;
    if (!{PKG}.PerkCfg.DMG_PVP) {{
      {REF} tr = chunk.getReferenceTo(idx);
      if (tr != null && st.getComponent(tr, {PR}.getComponentType()) != null) return;
    }}
    java.util.UUID u = pr.getUuid();
    int slot = {PKG}.SkillClass.slot(u);
    if (slot < 0) return;
    java.util.function.Function f = {PKG}.SkillClass.allowedFn();
    if (f == null) return;
    double bonus = {PKG}.Perks.damage({PKG}.SkillStore.level(u, slot));
    if (bonus <= 0.0) return;
    if (!{PKG}.SkillClass.weaponOk(u, slot, f, buf, att)) return;
    float a = d.getAmount();
    if (a <= 0.0f) return;
    d.setAmount((float) (a * (1.0 + bonus)));
  }} catch (Throwable t) {{
    if (!FAILED_ONCE) {{ FAILED_ONCE = true; {PKG}.SkillCfg.warn("combat damage perk failed (logged once): " + t); }}
  }}
}}""", cds))

# ================= PlacedStore: positions of player-placed blocks, per world =================
''')

# ---------------------------------------------------------------- double drops in the deferred break / harvest tasks
rep('''    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);
''', '''    {PKG}.SkillXp.gain(pr, (int) this.rule[0], this.rule[1]);
    {PKG}.Perks.breakDouble(pr, (int) this.rule[0], this.ev.getBlockType(), this.world, this.rule[2] == 0L || {PKG}.SkillCfg.IGNORE_PLACED);
''')
rep('''htk.addField(CtField.make("public boolean hop;", htk))
''', '''htk.addField(CtField.make("public boolean hop;", htk))
htk.addField(CtField.make(f"public {BTY} bt;", htk))   # 0.3: the ripe block type, for the Farming double drop
''')
rep('''      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
      return;
''', '''      {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.FARMING, this.amount);
      {PKG}.Perks.harvestDouble(pr, this.bt, this.wn);
      return;
''')
rep('''    w.execute(new {PKG}.HarvestTask(pr.getUuid(), w, wn, bx, by, bz, ripe, amt));''',
    '''    {PKG}.HarvestTask ht = new {PKG}.HarvestTask(pr.getUuid(), w, wn, bx, by, bz, ripe, amt);
    ht.bt = bt;
    w.execute(ht);''')

# ---------------------------------------------------------------- KillSys: class combat
rep('''    if ({PKG}.SkillXp.creative(s, k)) return;
    float maxHp = -1.0f;
''', '''    if ({PKG}.SkillXp.creative(s, k)) return;
    int slot = {PKG}.SkillClass.killSlot(pr, b, k);
    if (slot < 0) return;
    float maxHp = -1.0f;
''')
rep('    {PKG}.SkillXp.gain(pr, {PKG}.SkillDefs.COMBAT, {PKG}.SkillCfg.combatXp(role, maxHp));',
    '    {PKG}.SkillXp.gain(pr, slot, {PKG}.SkillCfg.combatXp(role, maxHp));')

# ---------------------------------------------------------------- leaderboard caches sized by the slot count
rep('top.addField(CtField.make("public static final long[] AT = new long[%d];" % 5, top))   # = SkillDefs.N',
    'top.addField(CtField.make("public static final long[] AT = new long[%d];" % len(SLOT_NAMES), top))   # = SkillDefs.N')
rep('top.addField(CtField.make("public static final Object[] CACHE = new Object[%d];" % 5, top))',
    'top.addField(CtField.make("public static final Object[] CACHE = new Object[%d];" % len(SLOT_NAMES), top))')

# ---------------------------------------------------------------- /skills page: rows = 5, Combat row = class skill, Stats buttons
rep('''    int sum = 0;
    for (int i = 0; i < {PKG}.SkillDefs.N; i++) sum += {PKG}.SkillDefs.levelOf(d[i]);
    long avg10 = Math.round(sum * 10.0 / {PKG}.SkillDefs.N);
''', '''    int cs = {PKG}.SkillClass.slot(u);
    int sum = 0;
    for (int i = 0; i < {PKG}.SkillDefs.ROWS; i++) sum += {PKG}.SkillDefs.levelOf(d[i == {PKG}.SkillDefs.COMBAT && cs >= 0 ? cs : i]);
    long avg10 = Math.round(sum * 10.0 / {PKG}.SkillDefs.ROWS);
''')
rep('''    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      long total = d[i];
''', '''    for (int i = 0; i < {PKG}.SkillDefs.ROWS; i++) {{
      int sl = i == {PKG}.SkillDefs.COMBAT && cs >= 0 ? cs : i;
      long total = d[sl];
''')
rep('''      String col = {PKG}.SkillDefs.COLORS[i];
''', '''      String col = {PKG}.SkillDefs.COLORS[sl];
      String title = {PKG}.SkillDefs.LABELS[sl] + "  " + lv;
      if (i == {PKG}.SkillDefs.COMBAT) {{
        if (cs >= 0) title = {PKG}.SkillClass.skillName(u, cs) + "  " + lv;
        else {{
          title = "Combat - choose a class with /class";
          prog = total > 0L ? "Old Combat XP (level " + lv + ") moves to the first class you choose" : "Your combat skill is your class skill";
          fill = 0;
        }}
      }}
''')
rep('ItemId: \\\\"" + {PKG}.SkillDefs.ICONS[i] + "\\\\"; }} }}");',
    'ItemId: \\\\"" + {PKG}.SkillDefs.ICONS[sl] + "\\\\"; }} }}");')
rep('Text: \\\\"" + {PKG}.SkillDefs.NAMES[i] + "  " + lv + "\\\\"; Style: (FontSize: 15,',
    'Text: \\\\"" + safe(title) + "\\\\"; Style: (FontSize: 15,')
rep('''      b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkTop" + i + " {{ Anchor: (Width: 100, Height: 30); Text: \\\\"Top 10\\\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyySkTop" + i, {EVD}.of("a", "sktop" + i));
''', '''      b.appendInline("#SkyySkRow" + i, "TextButton #SkyySkStat" + i + " {{ Anchor: (Width: 100, Height: 30); Text: \\\\"Stats\\\\"; " + bs + " }}");
      ev.addEventBinding({BT}.Activating, "#SkyySkStat" + i, {EVD}.of("a", "skstat" + sl));
''')
rep('Text: \\\\"Mine - chop trees - harvest ripe crops - defeat monsters - run jump fall and dodge.  /skills quiet hides XP messages\\\\";',
    'Text: \\\\"Mine - chop trees - harvest ripe crops - fight with your class weapons - run jump fall dodge.  Stats shows every boost\\\\";')
rep('safe("Top 10 - " + {PKG}.SkillDefs.NAMES[s])', 'safe("Top 10 - " + {PKG}.SkillDefs.LABELS[s])')

# ---------------------------------------------------------------- StatsPage (before SkillsPage.handleDataEvent, which constructs it)
rep('''page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''', r'''# ================= StatsPage (0.3): one skill - level, XP to next, boosts now (numbers), what the next level adds =================
# Inline page like SkillsPage (root Group with Width/Height only, no underscores in ids, TextButton + EventData with a trailing-quote
# match); every dynamic text goes through b.set("#Id.Text", ...), which is safe for any character.
spg.addField(CtField.make("public int slot;", spg))
spg.addConstructor(CtNewConstructor.make(f"""
public StatsPage({PR} pr, int slot) {{
  super(pr, {LIFE}.CanDismiss);
  this.slot = slot;
}}""", spg))
# at most 3 decimals, trailing zeros cut, no Locale (String.format could print a decimal comma): 2.5 -> "2.5", 0.015 -> "0.015",
# 10.0 -> "10"
spg.addMethod(CtNewMethod.make("""
public static String num(double v) {
  long t = Math.round(v * 1000.0);
  String sign = t < 0L ? "-" : "";
  if (t < 0L) t = -t;
  long w = t / 1000L;
  long f = t % 1000L;
  if (f == 0L) return sign + w;
  String fs = String.valueOf(f + 1000L).substring(1);
  while (fs.endsWith("0")) fs = fs.substring(0, fs.length() - 1);
  return sign + w + "." + fs;
}""", spg))
spg.addMethod(CtNewMethod.make("""
public static String pc(double frac) {
  return num(frac * 100.0) + "%";
}""", spg))
# a flat stat perk: now = per x level, next level adds per (linear)
spg.addMethod(CtNewMethod.make(f"""
public static void stat(java.util.ArrayList out, double per, int lv, boolean next, String what) {{
  if (per <= 0.0 || !{PKG}.PerkCfg.ENABLED) return;
  double v = next ? per : per * lv;
  if (v <= 0.0) return;
  out.add("+" + num(v) + " " + what);
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static java.util.ArrayList lines(java.util.UUID u, int s, int lv, boolean next) {{
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == {PKG}.SkillDefs.COMBAT) {{
    if (!next) {{
      out.add("No class yet - choose one with /class to start leveling combat");
      if ({PKG}.SkillStore.data(u)[s] > 0L) out.add("Old Combat XP - level " + lv + " - moves to the first class you choose");
    }}
    return out;
  }}
  int row = s >= {PKG}.SkillDefs.CLASS0 ? {PKG}.SkillDefs.COMBAT : s;
  int b = next ? lv + 1 : lv;
  if (row == {PKG}.SkillDefs.ACROBATICS) {{
    if (!{PKG}.AcroCfg.ENABLED) {{
      if (!next) out.add("Acrobatics bonuses are turned off on this server");
    }} else {{
      double sp = {PKG}.Acro.speedBonus(b) - (next ? {PKG}.Acro.speedBonus(lv) : 0.0);
      double jp = {PKG}.Acro.jumpBonus(b) - (next ? {PKG}.Acro.jumpBonus(lv) : 0.0);
      double fb = {PKG}.Acro.fallBonus(b) - (next ? {PKG}.Acro.fallBonus(lv) : 0.0);
      double db = {PKG}.Acro.dodgeBonus(b) - (next ? {PKG}.Acro.dodgeBonus(lv) : 0.0);
      if (sp > 0.00001) out.add("+" + pc(sp) + " movement speed (of vanilla speed)");
      if (jp > 0.00001) out.add("+" + num(jp) + " blocks jump height");
      if (fb > 0.00001) out.add("-" + pc(fb) + " fall damage");
      if (db > 0.00001) out.add("+" + pc(db) + " dodge push");
    }}
  }}
  stat(out, {PKG}.PerkCfg.HP[row], lv, next, "max Health");
  stat(out, {PKG}.PerkCfg.STA[row], lv, next, "max Stamina");
  stat(out, {PKG}.PerkCfg.MANA[row], lv, next, "max Mana");
  if (row <= {PKG}.SkillDefs.FARMING) {{
    String[] what = new String[] {{ "mined blocks", "chopped logs", "harvested crops" }};
    double c = {PKG}.Perks.chance(row, b) - (next ? {PKG}.Perks.chance(row, lv) : 0.0);
    if (c > 0.00001) out.add((next ? "+" : "") + pc(c) + " chance to double the drops of " + what[row]);
  }}
  if (row == {PKG}.SkillDefs.COMBAT && {PKG}.PerkCfg.ENABLED && {PKG}.PerkCfg.DMG > 0.0) {{
    double dm = next ? {PKG}.PerkCfg.DMG : {PKG}.Perks.damage(lv);
    if (dm > 0.0) out.add("+" + pc(dm) + " damage with " + {PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0] + " weapons" + ({PKG}.PerkCfg.DMG_PVP ? "" : " (against monsters)"));
  }}
  if (next && {PKG}.SkillCfg.COINS_PER_LEVEL > 0L) out.add("+" + {PKG}.SkillDefs.fmt({PKG}.SkillCfg.COINS_PER_LEVEL * (long) b) + " coins when you reach level " + b);
  if (!next && out.isEmpty()) out.add(lv <= 0 ? "Nothing yet - level up to unlock boosts" : "This skill gives no boosts on this server");
  return out;
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static String how(int s) {{
  if (s == {PKG}.SkillDefs.MINING) return "Earn XP by mining stone and ores - rarer ores pay more";
  if (s == {PKG}.SkillDefs.FORAGING) return "Earn XP by chopping trees - rare woods pay more";
  if (s == {PKG}.SkillDefs.FARMING) return "Earn XP by harvesting fully grown crops - break them or press F on eternal crops and bushes";
  if (s == {PKG}.SkillDefs.ACROBATICS) return "Earn XP by running - jumping - falling and dodging";
  if (s == {PKG}.SkillDefs.COMBAT) return "Your combat skill is your class skill - Archer Archery / Warrior Swordsmanship / Assassin Assassination / Berserker Berserking / Mage Sorcery";
  String c = {PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0];
  String w = {PKG}.SkillClass.weaponsText(c);
  return "Earn XP by defeating monsters with " + c + " weapons" + (w == null ? "" : " - " + w);
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public static void line({UCB} b, String id, String text, String color, int size, boolean bold, int h) {{
  b.appendInline("#SkyySkStats", "Label #" + id + " {{ Anchor: (Height: " + h + "); Text: \\"\\"; Style: (FontSize: " + size + ", " + (bold ? "RenderBold: true, " : "") + "TextColor: " + color + ", VerticalAlignment: Center); }}");
  b.set("#" + id + ".Text", text);
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public void build({REF} ref, {UCB} b, {UEB} ev, {ST} st) {{
  java.util.UUID u = this.playerRef.getUuid();
  long[] d = {PKG}.SkillStore.data(u);
  int s = this.slot;
  if (s < 0 || s >= {PKG}.SkillDefs.N) s = 0;
  int cs = {PKG}.SkillClass.slot(u);
  if (s == {PKG}.SkillDefs.COMBAT && cs >= 0) s = cs;
  long total = d[s];
  int lv = {PKG}.SkillDefs.levelOf(total);
  long cur = {PKG}.SkillDefs.intoLevel(total);
  long need = {PKG}.SkillDefs.needFor(total);
  int fill = need > 0L ? (int) ({BARW}L * cur / need) : {BARW};
  if (fill < 0) fill = 0;
  if (fill > {BARW}) fill = {BARW};
  boolean legacy = s == {PKG}.SkillDefs.COMBAT;
  if (legacy) fill = 0;
  String col = {PKG}.SkillDefs.COLORS[s];
  String name = legacy ? "Combat" : {PKG}.SkillClass.skillName(u, s);
  String bs = "Style: TextButtonStyle(Default: (Background: #27463a, LabelStyle: (FontSize: 12, TextColor: #dcffe8, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Hovered: (Background: #3b6b54, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)), Pressed: (Background: #172a22, LabelStyle: (FontSize: 12, TextColor: #ffffff, RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)));";
  b.appendInline((String) null, "Group #SkyySkStats {{ Anchor: (Width: 640, Height: 530); Background: #0b1524(0.96); Padding: (Horizontal: 16, Vertical: 10); LayoutMode: Top; }}");
  b.appendInline("#SkyySkStats", "Group {{ Anchor: (Height: 2); Background: #9fe0a0; }}");
  b.appendInline("#SkyySkStats", "Label #SkyyStTitle {{ Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + col + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  b.set("#SkyyStTitle.Text", legacy ? "Combat - no class" : name + " - level " + lv + " of " + {PKG}.SkillDefs.MAX);
  b.appendInline("#SkyySkStats", "Label #SkyyStSub {{ Anchor: (Height: 18); Text: \\"\\"; Style: (FontSize: 11, TextColor: #9fb8cc, HorizontalAlignment: Center, VerticalAlignment: Center); }}");
  String sub;
  if (legacy) sub = "Choose a class with /class - each class has its own combat skill";
  else if (need > 0L) sub = {PKG}.SkillDefs.fmt(cur) + " / " + {PKG}.SkillDefs.fmt(need) + " XP to level " + (lv + 1) + "  (" + {PKG}.SkillDefs.fmt(need - cur) + " to go)";
  else sub = "MAX LEVEL - " + {PKG}.SkillDefs.fmt(total) + " XP";
  b.set("#SkyyStSub.Text", sub);
  b.appendInline("#SkyySkStats", "Group #SkyyStBarRow {{ Anchor: (Height: 16); LayoutMode: Left; Padding: (Top: 2); }}");
  b.appendInline("#SkyyStBarRow", "Label {{ Anchor: (Width: 104, Height: 12); Text: \\"\\"; }}");
  b.appendInline("#SkyyStBarRow", "Group #SkyyStBar {{ Anchor: (Width: {BARW}, Height: 12); Background: #22324a; }}");
  if (fill > 0) b.appendInline("#SkyyStBar", "Group {{ Anchor: (Left: 0, Top: 0, Width: " + fill + ", Height: 12); Background: " + col + "; }}");
  if (s >= {PKG}.SkillDefs.CLASS0 && s != cs) {{
    String cn = {PKG}.SkillDefs.CLASSES[s - {PKG}.SkillDefs.CLASS0];
    String art = (cn.startsWith("A") || cn.startsWith("E") || cn.startsWith("I") || cn.startsWith("O") || cn.startsWith("U")) ? "an " : "a ";
    line(b, "SkyyStNote", "You are not " + art + cn + " right now - these boosts work while you are one", "#ffb080", 11, true, 20);
  }} else {{
    b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  }}
  line(b, "SkyyStNowHd", legacy ? "Your combat" : "Boosts right now (level " + lv + ")", "#e6fff0", 13, true, 24);
  java.util.ArrayList now = lines(u, s, lv, false);
  for (int i = 0; i < now.size() && i < 7; i++) line(b, "SkyyStNow" + i, "   " + (String) now.get(i), "#dfe8f0", 12, false, 19);
  b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  if (!legacy) {{
    if (need > 0L) {{
      line(b, "SkyyStNextHd", "Level " + (lv + 1) + " adds", "#e6fff0", 13, true, 24);
      java.util.ArrayList nx = lines(u, s, lv, true);
      for (int i = 0; i < nx.size() && i < 7; i++) line(b, "SkyyStNext" + i, "   " + (String) nx.get(i), "#bfe8c8", 12, false, 19);
    }} else {{
      line(b, "SkyyStNextHd", "Max level reached - nothing more to unlock", "#ffe08a", 13, true, 24);
    }}
    b.appendInline("#SkyySkStats", "Label {{ Anchor: (Height: 8); Text: \\"\\"; }}");
  }}
  line(b, "SkyyStHow", how(s), "#8fa6ba", 10, false, 22);
  b.appendInline("#SkyySkStats", "Group #SkyyStNav {{ Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 8); }}");
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 164, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStBack {{ Anchor: (Width: 130, Height: 30); Text: \\"< Back\\"; " + bs + " }}");
  b.appendInline("#SkyyStNav", "Label {{ Anchor: (Width: 20, Height: 30); Text: \\"\\"; }}");
  b.appendInline("#SkyyStNav", "TextButton #SkyyStTop {{ Anchor: (Width: 130, Height: 30); Text: \\"Top 10\\"; " + bs + " }}");
  ev.addEventBinding({BT}.Activating, "#SkyyStBack", {EVD}.of("a", "stback"));
  ev.addEventBinding({BT}.Activating, "#SkyyStTop", {EVD}.of("a", "sttop"));
}}""", spg))
spg.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{
  try {{
    if (data == null) return;
    {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
    if (p == null) return;
    if (data.indexOf("stback\\"") >= 0) {{ p.getPageManager().openCustomPage(ref, st, new {PKG}.SkillsPage(this.playerRef)); return; }}
    if (data.indexOf("sttop\\"") >= 0) {{
      int s = this.slot;
      if (s == {PKG}.SkillDefs.COMBAT) {{ int c = {PKG}.SkillClass.slot(this.playerRef.getUuid()); if (c >= 0) s = c; }}
      {PKG}.SkillsPage sp = new {PKG}.SkillsPage(this.playerRef);
      sp.view = s;
      p.getPageManager().openCustomPage(ref, st, sp);
    }}
  }} catch (Throwable t) {{ {PKG}.SkillCfg.warn("stats page event failed: " + t); }}
}}""", spg))
page.addMethod(CtNewMethod.make(f"""
public void handleDataEvent({REF} ref, {ST} st, String data) {{''')
rep('''    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("sktop" + i + "\\\\"") >= 0) {{ this.view = i; rebuild(); return; }}
    }}
''', '''    for (int i = 0; i < {PKG}.SkillDefs.N; i++) {{
      if (data.indexOf("skstat" + i + "\\\\"") >= 0) {{
        {PLA} p = ({PLA}) st.getComponent(ref, {PLA}.getComponentType());
        if (p != null) p.getPageManager().openCustomPage(ref, st, new {PKG}.StatsPage(this.playerRef, i));
        return;
      }}
    }}
''')

# ---------------------------------------------------------------- commands (HANDOFF command rules)
rep('''  super("top", "Top 10 players of a skill: /skills top mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | combat | acrobatics", {ATY}.STRING);
''', '''  super("top", "Top 10 players of a skill: /skills top mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | acrobatics | combat (your class skill) | archery | swordsmanship | assassination | berserking | sorcery", {ATY}.STRING);
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
''')
rep('''    int s = {PKG}.SkillDefs.indexOf(String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) {{ pr.sendMessage({MSG}.raw("[Skills] Unknown skill. Use mining, foraging, farming, combat or acrobatics.")); return; }}
''', '''    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) return;
''')
rep('''pr.sendMessage({MSG}.raw("[Skills] Top 10 " + {PKG}.SkillDefs.NAMES[s] + ":").color("#ffc800"));''',
    '''pr.sendMessage({MSG}.raw("[Skills] Top 10 " + {PKG}.SkillDefs.LABELS[s] + ":").color("#ffc800"));''')
rep('''qcmd.addConstructor(CtNewConstructor.make('public QuietCmd() { super("quiet", "Toggle the +XP chat messages (level ups always show)"); }', qcmd))''',
    '''qcmd.addConstructor(CtNewConstructor.make('public QuietCmd() { super("quiet", "Toggle the +XP chat messages (level ups always show)"); setPermissionGroups(new String[] { "hytale:Adventurer" }); }', qcmd))''')
# admin: gate + EMPTY group list, else putRecursivePermissionGroups hands the parent's Adventurer group this node (coll_0_1_4_patch.py)
rep('''rcmd.addConstructor(CtNewConstructor.make('public ReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyySkills/xp.properties"); }', rcmd))''',
    '''rcmd.addConstructor(CtNewConstructor.make('public ReloadCmd() { super("reload", "(admin) Re-read Skyy_SkyySkills/xp.properties"); requirePermission("skyyskills.admin"); setPermissionGroups(new String[0]); }', rcmd))''')
rep('''cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{
  super("skills", "Open your skills page; /skills top <skill>, /skills quiet");
  addAliases(new String[] {{ "skill" }});
  addSubCommand(new {PKG}.TopCmd());
''', r'''# /skills stats <skill> (0.3): a subcommand with a required arg (optional args are not positional - HANDOFF command rules)
scmd.addField(CtField.make(f"public {RA} skillArg;", scmd))
scmd.addConstructor(CtNewConstructor.make(f"""
public StatsCmd() {{
  super("stats", "Open the Stats page of a skill: /skills stats mining");
  this.skillArg = withRequiredArg("skill", "mining | foraging | farming | acrobatics | combat (your class skill) | archery | swordsmanship | assassination | berserking | sorcery", {ATY}.STRING);
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
}}""", scmd))
scmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    int s = {PKG}.SkillClass.argSlot(pr, String.valueOf(ctx.get(this.skillArg)));
    if (s < 0) return;
    {PLA} player = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (player == null) return;
    player.getPageManager().openCustomPage(ref, store, new {PKG}.StatsPage(pr, s));
  }} catch (Throwable t) {{
    {PKG}.SkillCfg.warn("/skills stats failed: " + t);
    pr.sendMessage({MSG}.raw("[Skills] could not open the stats page"));
  }}
}}""", scmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public SkillsCmd() {{
  super("skills", "Open your skills page; /skills stats <skill>, /skills top <skill>, /skills quiet");
  addAliases(new String[] {{ "skill" }});
  setPermissionGroups(new String[] {{ "hytale:Adventurer" }});
  addSubCommand(new {PKG}.StatsCmd());
  addSubCommand(new {PKG}.TopCmd());
''')

# ---------------------------------------------------------------- plugin setup, class list, manifest
rep('''  getEntityStoreRegistry().registerSystem(new {PKG}.AcroFallSys());
''', '''  getEntityStoreRegistry().registerSystem(new {PKG}.AcroFallSys());
  getEntityStoreRegistry().registerSystem(new {PKG}.CombatDmgSys());
''')
rep('''log("[SkyySkills] {VERSION} ready - /skills; xp rules: " + rules + (fallOwner ? "" : ''',
    '''log("[SkyySkills] {VERSION} ready - /skills; xp rules: " + rules + "; combat = class skill (SkyyClasses " + ({PKG}.SkillClass.allowedFn() != null ? "found" : "not loaded yet - no combat XP without it") + ")" + (fallOwner ? "" : ''')
rep('for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl, acfg, mvs_, acro, asy, afs):',
    'for c in (defs, cfg, sto, pub, fn, msg, fl, xp, plc, hg, btk, ptk, htk, bsy, psy, usy, ksy, tcm, top, page, tcmd, qcmd, rcmd, cmd, tick, pl, acfg, mvs_, acro, asy, afs,\n'
    '          pcfg, scls, perk, cds, spg, scmd):')
rep('"SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Combat, Acrobatics to level 50. XP from breaking blocks, ripe crops, NPC kills and running / jumping / falling / dodging; Acrobatics raises speed, jump height and dodge push and lowers fall damage (shared Skyy movement protocol). Level ups pay SkyyCoins. /skills. Zero dependencies."',
    '"SkyWynn skills (Hypixel SkyBlock style): Mining, Foraging, Farming, Acrobatics and your class combat skill (SkyyClasses) to level 100. XP from breaking blocks, ripe crops, kills with class weapons and running / jumping / falling / dodging. Perks: max health / stamina, double drops, class weapon damage; Acrobatics raises speed, jump height and dodge push and lowers fall damage (shared Skyy movement protocol). Stats page per skill. Level ups pay SkyyCoins. /skills. Zero dependencies."')

# ---------------------------------------------------------------- sanity
assert "sktop" not in s, "old Top 10 button payload left"
assert 'new long[%d];" % 5' not in s
assert s.count("setPermissionGroups(new String[] {{ \"hytale:Adventurer\" }});") == 3   # skills, top, stats (quiet is a plain string ctor)
assert "setPermissionGroups(new String[] { \"hytale:Adventurer\" });" in s                # quiet
assert "{PKG}.SkillDefs.NAMES[i]).append(':')" not in s
assert "boolean repub = last == null || !last.equals(cn);" in s   # first tick of a session republishes skill:<uuid> (review fix)
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.2
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
