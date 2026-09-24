"""Derive SkyyAccessories/build_skyyaccessories_0.4.py from 0.3 (same style as acc_0_2_patch.py / acc_0_3_patch.py: rep(old, new) with
asserted anchors, newline-agnostic; 0.3 stays untouched, the line endings of 0.3 are preserved).
0.4 (Skyy 2026-09-23):
 1. RARITY TIERS - "each accessory has rarity from common to legendary". Talismans come in 5 rarities Common, Uncommon, Rare, Epic,
    Legendary: ids Skyy_Talisman_<Family>_<Rarity>, item Quality = the vanilla quality of that name (the build reads
    Server/Item/Qualities/<Rarity>.json from Assets.zip - fails if one is missing - and uses its TextColor on the bag page).
    Common = crystals + basic materials at a Workbench; each next rarity = the previous talisman + materials (Uncommon/Rare/Epic reuse
    the 0.2 Talisman/Ring/Artifact materials, Legendary adds 5 gems + Adamantite/Mithril + a Voidheart).
    LEGACY 0.2/0.3 ids Skyy_Talisman_<Family>_<Talisman|Ring|Artifact> keep their item assets (old stacks still load, show and keep
    their quality) but have NO recipe; everywhere they count as Uncommon / Rare / Epic of the same family (AccDefs.tierOf), in the bag
    and in the inventory list. They are converted at the bag boundary only: Equip stores the modern id (Skyy_Talisman_<Family>_<Rarity>),
    Unequip hands back the modern item (upgradable), bags saved by 0.2/0.3 are NOT rewritten on load (a rollback to 0.3 still reads
    them). Still one talisman per family counts (best rarity wins; the swap rule compares the mapped rarity).
    Bench accessories get rarity by tier (SkyyAccessories-Plan.md): T1 Common, T2 Uncommon, T3 Rare, T4 Epic, T5+ Legendary
    (item Quality + AccDefs.rarityOf).
 2. PERCENT LAYER - "skills and armor add or minus flat numbers and accessories will generally add percentages on top of that flat
    rate". Vitality / Endurance / Intelligence = % of max Health / Stamina / Mana (2/4/6/8/10 % by rarity), Regeneration heals
    0.5/1/1.5/2/3 % of max Health every 2 s, Speed = 2/4/6/8/10 % through the movement protocol's pct layer (unchanged mechanism).
    Regeneration deliberately uses the FULL current max Health (flat + percent layer + vanilla buffs = the Health bar the item text
    "of your max Health" refers to), NOT flatMax: Vitality/Endurance/Intelligence use the flat max because they ARE the percent layer
    (summing, not compounding); a heal is not a max bonus. putModifier recomputes max at once (EntityStatValue.putModifier ->
    computeModifiers, bytecode 2026-09-23), so the heal already sees this tick's Vitality bonus. Commented at the regen code too.
    VERIFIED IN HytaleServer.jar BYTECODE (2026-09-23, EntityStatValue.computeModifiers + StaticModifier$CalculationType$1/$2):
      max = EntityStatType.max; ADDITIVE amounts targeting MAX are SUMMED and added (compute = a + b); THEN the MULTIPLICATIVE
      amounts are SUMMED and multiplied (compute = a * b). So MULTIPLICATIVE does apply after additive, but its value is a factor
      (1.10, not 0.10) and several multiplicative modifiers do NOT stack: vanilla's Meat_Buff_T1 already posts MULTIPLICATIVE 1.05 on
      max Health, and 1.10 + 1.05 = 2.15 -> x2.15. Therefore this mod does NOT use MULTIPLICATIVE: every second it computes
      flat = EntityStatType.max + every OTHER ADDITIVE MAX modifier (armour, SkyySkills, food boosts) and posts
      ADDITIVE round(flat x pct) under the 0.2/0.3 keys skyyacc_health / skyyacc_stamina / skyyacc_mana (the flat value those versions
      saved with the player is simply overwritten on the first tick). A vanilla multiplicative buff then scales (flat + ours), i.e.
      final = flat x (1 + pct) x buff - exactly Skyy's layer rule. Mana: vanilla max Mana is 0, so Intelligence only scales Mana
      your gear/skills give.
 3. OMNI ACCESSORY - Skyy_Accessory_Omni (Legendary), crafted at a Workbench from the max-tier accessory of all 13 benches. Own group
    "Omni" (sits next to bench accessories). In the bag it counts as every bench accessory at max tier: acc:has is published with the
    Omni EXPANDED into synthetic "Skyy_Accessory_<BenchId>_T<maxTier>" entries. acc:has holds EXACTLY ONE entry per bench, at the best
    tier of the real accessory and the Omni (AccDefs.benchList reduces bench id -> max tier, like SkyySacks' accessories() parser; a
    real Workbench_T2 next to the Omni publishes only Workbench_T3, so SkyyMenu's "N bench accessories" count stays 13). The Omni id
    itself is not listed, so acc:has stays "bench accessories only" and SkyySacks 0.6.x needs no change; acc:fn:has answers true for
    the Omni id, for every real slot id and for every acc:has entry (and for a modern talisman id when the bag holds its legacy one).
 4. COMMAND RULES - /accessories (aliases acc, accbag) calls setPermissionGroups(new String[] { "hytale:Adventurer" }) (no args, no
    subcommands, so no usage variants are needed).
 5. Unchanged: movement protocol use (MoveSync from tools/skyymove.py), acc:tal (now published with modern ids), 9 slots, per-player
    locks, hand-back rules. The bag page shows each accessory's rarity name in the vanilla quality colour. NOT built (Skyy's open
    questions in SkyyAccessories-Plan.md): accessory power, slot unlocks, crystals, tuning.
Run:  python tools/acc_0_4_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.4.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.3.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.3"
s = raw.decode("utf8").replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

def cut(start, end, new):
    """replace s[index(start):index(end)] (start and end both unique; end is kept)"""
    global s
    assert s.count(start) == 1, "start anchor count %d: %s" % (s.count(start), start[:80])
    assert s.count(end) == 1, "end anchor count %d: %s" % (s.count(end), end[:80])
    a = s.index(start); b = s.index(end)
    assert a < b, "anchors out of order: " + start[:60]
    s = s[:a] + new + s[b:]

# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.3 - build script (derived from 0.2 by tools/acc_0_3_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.3.py            -> SkyyAccessories/SkyyAccessories-0.3.jar
       python build_skyyaccessories_0.3.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.3: Speed talismans''', '''"""SkyyAccessories 0.4 - build script (derived from 0.3 by tools/acc_0_4_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.py            -> SkyyAccessories/SkyyAccessories-0.4.jar
       python build_skyyaccessories_0.4.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4: RARITY TIERS + PERCENT LAYER + OMNI (full notes in tools/acc_0_4_patch.py):
     - Talismans Skyy_Talisman_<Family>_<Common|Uncommon|Rare|Epic|Legendary> (Quality = vanilla quality of that name), upgrade recipe =
       previous rarity + materials at a Workbench. Legacy 0.2/0.3 ids <Talisman|Ring|Artifact> keep their assets (no recipe) and count
       as Uncommon/Rare/Epic; Equip stores the modern id, Unequip returns the modern (upgradable) item. Bench accessory rarity by tier
       (T1 Common .. T5+ Legendary). One talisman per family counts (best rarity).
     - Vitality/Endurance/Intelligence = % of the FLAT max Health/Stamina/Mana, Regeneration = % of the FULL current max Health
       every 2 s (deliberate: the Health bar the item text names; a heal is not a max bonus), Speed = %
       through the movement protocol's pct layer. StaticModifier MULTIPLICATIVE was checked in bytecode: it applies after ADDITIVE but
       all multiplicative amounts are SUMMED into one factor (vanilla Meat_Buff 1.05 + ours 1.10 = x2.15), so the % is computed here
       from type max + every other ADDITIVE MAX modifier and posted as ADDITIVE (keys skyyacc_health/stamina/mana, as in 0.2/0.3).
     - Skyy_Accessory_Omni (Legendary, Workbench, all 13 max-tier bench accessories) counts as every bench accessory at max tier:
       acc:has expands it into Skyy_Accessory_<BenchId>_T<maxTier> entries, exactly one entry per bench at the best tier of real +
       Omni (SkyySacks needs no change). Own group "Omni".
     - /accessories (acc, accbag): setPermissionGroups hytale:Adventurer. Bag page shows rarity names in the quality colours.
0.3 notes:
0.3: Speed talismans''')
rep('VERSION = "0.3"', 'VERSION = "0.4"')

# ---------------------------------------------------------------- probes (0.4 stat math + command rule)
rep('''MV.probe(B, pool)   # 0.3: MovementStates.mounting, MovementSettings.jumpForce, PhysicsConstants.GRAVITY_ACCELERATION, ...
''', '''MV.probe(B, pool)   # 0.3: MovementStates.mounting, MovementSettings.jumpForce, PhysicsConstants.GRAVITY_ACCELERATION, ...
# 0.4: percent layer reads the stat type's base max + the other MAX modifiers; /accessories gets the Adventurer permission group
EST = "com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
ACM = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
for c, m in ((EST, "getAssetMap"), (EST, "getMax"), (ILT, "getAsset"), (ESV, "getModifiers"), (SMO, "getCalculationType"),
             (MOD, "getTarget"), (MTG, "MAX"), (CAL, "ADDITIVE"), (ACM, "setPermissionGroups"), (ACM, "addAliases")):
    B.probe(pool, c, m)
''')

# ---------------------------------------------------------------- data: Omni id, rarities, talisman table
rep('BAG = "Skyy_Accessory_Bag"\n', '''BAG = "Skyy_Accessory_Bag"
OMNI = "Skyy_Accessory_Omni"   # 0.4: counts as every bench accessory at max tier (own group "Omni")
''')
cut("# ---- 0.2 stat talismans:", "FAM = dict((t[0], i) for i, t in enumerate(TALISMANS))", r'''# ---- 0.4 stat talismans in 5 RARITIES (Skyy: "each accessory has rarity from common to legendary")
# 0.2/0.3 LEGACY ids Skyy_Talisman_<Family>_<Talisman|Ring|Artifact>: assets kept WITHOUT a recipe, counted as Uncommon/Rare/Epic
TIER_NAMES = ["", "Talisman", "Ring", "Artifact"]
TIER_QUAL = ["", "Uncommon", "Rare", "Epic"]
LEGACY_TIER = [0, 2, 3, 4]
RARITIES = ["", "Common", "Uncommon", "Rare", "Epic", "Legendary"]   # tier 1..5 = vanilla item Quality of the same name
import zipfile as _zq
_QZ = _zq.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
RARITY_COLORS = ["#ffffff"]
for _r in RARITIES[1:]:
    _qn = "Server/Item/Qualities/%s.json" % _r
    assert _qn in _QZ.namelist(), "no vanilla item quality " + _r
    _qc = json.loads(_QZ.read(_qn).decode("utf-8-sig"))["TextColor"]
    assert len(_qc) == 7 and _qc[0] == "#" and all(ch in "0123456789abcdefABCDEF" for ch in _qc[1:]), _qc
    RARITY_COLORS.append(_qc)
REGEN_EVERY = 2
# PERCENT LAYER values per rarity Common..Legendary (Skyy: skills + armour = flat, accessories = % on top of that flat):
# Vitality / Endurance / Intelligence = % of the FLAT max Health / Stamina / Mana (vanilla base 100 / 10 / 0 + armour + skills),
# Regeneration = % of max Health healed every REGEN_EVERY seconds, Speed = % movement speed (movement protocol pct layer).
# recipes: [Common inputs, Uncommon extra, Rare extra, Epic extra, Legendary extra] - each upgrade also takes the previous rarity.
# Uncommon/Rare/Epic extras = the 0.2 Talisman/Ring/Artifact materials.
TALISMANS = [
    ("Vitality",     "Health",  "Red",    "Rock_Gem_Ruby",     [2, 4, 6, 8, 10], [
        [("Ingredient_Crystal_Red", 2), ("Ingredient_Life_Essence", 5), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Red", 3), ("Ingredient_Life_Essence", 10), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Ruby", 1), ("Ingredient_Bar_Iron", 10), ("Ingredient_Life_Essence", 30)],
        [("Rock_Gem_Ruby", 3), ("Ingredient_Bar_Thorium", 10), ("Ingredient_Life_Essence_Concentrated", 2)],
        [("Rock_Gem_Ruby", 5), ("Ingredient_Bar_Adamantite", 10), ("Ingredient_Life_Essence_Concentrated", 5), ("Ingredient_Voidheart", 1)]]),
    ("Endurance",    "Stamina", "Yellow", "Rock_Gem_Topaz",    [2, 4, 6, 8, 10], [
        [("Ingredient_Crystal_Yellow", 2), ("Ingredient_Leather_Light", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Yellow", 3), ("Ingredient_Leather_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Topaz", 1), ("Ingredient_Leather_Medium", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Topaz", 3), ("Ingredient_Leather_Heavy", 15), ("Ingredient_Bar_Thorium", 10)],
        [("Rock_Gem_Topaz", 5), ("Ingredient_Leather_Storm", 15), ("Ingredient_Bar_Adamantite", 10), ("Ingredient_Voidheart", 1)]]),
    ("Intelligence", "Mana",    "Blue",   "Rock_Gem_Sapphire", [2, 4, 6, 8, 10], [
        [("Ingredient_Crystal_Blue", 2), ("Ingredient_Fabric_Scrap_Linen", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Blue", 3), ("Ingredient_Fabric_Scrap_Linen", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Sapphire", 1), ("Ingredient_Fabric_Scrap_Silk", 10), ("Ingredient_Bar_Silver", 5)],
        [("Rock_Gem_Sapphire", 3), ("Ingredient_Bolt_Cindercloth", 5), ("Ingredient_Bar_Cobalt", 10)],
        [("Rock_Gem_Sapphire", 5), ("Ingredient_Bolt_Stormsilk", 5), ("Ingredient_Bar_Mithril", 10), ("Ingredient_Voidheart", 1)]]),
    ("Regeneration", "Regen",   "Green",  "Rock_Gem_Emerald",  [0.5, 1, 1.5, 2, 3], [
        [("Ingredient_Crystal_Green", 2), ("Ingredient_Life_Essence", 10), ("Ingredient_Tree_Sap", 3)],
        [("Ingredient_Crystal_Green", 3), ("Ingredient_Life_Essence", 20), ("Ingredient_Tree_Sap", 5)],
        [("Rock_Gem_Emerald", 1), ("Ingredient_Life_Essence", 50), ("Ingredient_Bar_Gold", 5)],
        [("Rock_Gem_Emerald", 3), ("Ingredient_Life_Essence_Concentrated", 3), ("Ingredient_Bar_Cobalt", 10)],
        [("Rock_Gem_Emerald", 5), ("Ingredient_Life_Essence_Concentrated", 6), ("Ingredient_Bar_Adamantite", 10), ("Ingredient_Voidheart", 1)]]),
    ("Speed",        "Speed",   "Cyan",   "Rock_Gem_Zephyr",   [2, 4, 6, 8, 10], [
        [("Ingredient_Crystal_Cyan", 2), ("Ingredient_Feathers_Light", 3), ("Ingredient_Bar_Copper", 2)],
        [("Ingredient_Crystal_Cyan", 3), ("Ingredient_Feathers_Light", 5), ("Ingredient_Bar_Copper", 4)],
        [("Rock_Gem_Zephyr", 1), ("Ingredient_Feathers_Blue", 10), ("Ingredient_Bar_Iron", 10)],
        [("Rock_Gem_Zephyr", 3), ("Ingredient_Lightning_Essence", 10), ("Ingredient_Bar_Cobalt", 10)],
        [("Rock_Gem_Zephyr", 5), ("Ingredient_Lightning_Essence", 25), ("Ingredient_Bar_Mithril", 10), ("Ingredient_Voidheart", 1)]]),
]
assert all(len(t[4]) == 5 and len(t[5]) == 5 for t in TALISMANS)
''')

# ---------------------------------------------------------------- AccDefs: rarity / Omni fields
rep('''dfs.addField(CtField.make('public static final int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))
''', '''dfs.addField(CtField.make('public static final int REGEN_EVERY = %d;' % REGEN_EVERY, dfs))
# 0.4: rarity names (index = tier 1..5) and the vanilla quality TextColor of each (read from Assets.zip Server/Item/Qualities)
dfs.addField(CtField.make('public static final String[] RARITY = new String[] { %s };' % ", ".join('"%s"' % r for r in RARITIES), dfs))
dfs.addField(CtField.make('public static final String[] RARITY_COLOR = new String[] { %s };' % ", ".join('"%s"' % c for c in RARITY_COLORS), dfs))
dfs.addField(CtField.make('public static final String OMNI = "%s";' % OMNI, dfs))
dfs.addField(CtField.make('public static final int[] BENCH_MAX = new int[] { %s };' % ", ".join(str(b[3]) for b in BENCHES), dfs))
''')

# ---------------------------------------------------------------- AccDefs.tierOf: rarity suffixes + legacy mapping
rep('''  if (isTalisman(id)) {
    if (id.endsWith("_Artifact")) return 3;
    if (id.endsWith("_Ring")) return 2;
    return 1;
  }''', '''  if (isTalisman(id)) {
    for (int r = RARITY.length - 1; r >= 1; r--) if (id.endsWith("_" + RARITY[r])) return r;
    if (id.endsWith("_Artifact")) return 4;
    if (id.endsWith("_Ring")) return 3;
    if (id.endsWith("_Talisman")) return 2;
    return 1;
  }''')

# ---------------------------------------------------------------- AccDefs: legacy / rarity / Omni helpers (after tierOf, before groupOf)
rep('''# one-per-group key used by AccStore.equip: bench id for bench accessories, "T:<family>" for talismans
''', r'''# 0.4: 0.2/0.3 talisman ids (Talisman/Ring/Artifact) - counted as Uncommon/Rare/Epic by tierOf
dfs.addMethod(CtNewMethod.make("""
public static boolean isLegacy(String id) {
  if (!isTalisman(id)) return false;
  return id.endsWith("_Talisman") || id.endsWith("_Ring") || id.endsWith("_Artifact");
}""", dfs))
# "Skyy_Talisman_Vitality_Ring" -> "Skyy_Talisman_Vitality_Rare"; every other id unchanged
dfs.addMethod(CtNewMethod.make("""
public static String modernOf(String id) {
  if (!isLegacy(id)) return id;
  String f = familyOf(id);
  int t = tierOf(id);
  if (f == null || t < 1 || t >= RARITY.length) return id;
  return "Skyy_Talisman_" + f + "_" + RARITY[t];
}""", dfs))
# rarity 1..5 (Common..Legendary) of any accessory: talismans by rarity, bench accessories T1..T5+ (plan), Omni Legendary; 0 = none
dfs.addMethod(CtNewMethod.make("""
public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (OMNI.equals(id)) return 5;
  int t = tierOf(id);
  if (t < 1) t = 1;
  if (t > 5) t = 5;
  return t;
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String rarityName(String id) {
  return RARITY[rarityOf(id)];
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String rarityColor(String id) {
  return RARITY_COLOR[rarityOf(id)];
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static boolean hasOmni(String[] s) {
  if (s == null) return false;
  for (int i = 0; i < s.length; i++) if (OMNI.equals(s[i])) return true;
  return false;
}""", dfs))
# one-per-group key used by AccStore.equip: bench id for bench accessories, "T:<family>" for talismans
''')

# ---------------------------------------------------------------- bestTiers: 5 rarities
rep('    if (t > 3) t = 3;\n', '    if (t > 5) t = 5;   // 0.4: Common..Legendary\n')

# ---------------------------------------------------------------- bonusText: percent values
cut('dfs.addMethod(CtNewMethod.make("""\npublic static String bonusText(String[] s) {',
    'dfs.addMethod(CtNewMethod.make("""\npublic static String roman(int t) {', r'''# 0.4: 2.0 -> "2", 1.5 -> "1.5" (one decimal, values are >= 0)
dfs.addMethod(CtNewMethod.make("""
public static String pctText(float v) {
  int i = Math.round(v * 10.0f);
  if (i % 10 == 0) return String.valueOf(i / 10);
  return String.valueOf(i / 10) + "." + String.valueOf(i % 10);
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String bonusText(String[] s) {
  int[] b = bestTiers(s);
  StringBuilder sb = new StringBuilder();
  if (b[%(V)d] > 0) sb.append(" / +").append(pctText(VIT[b[%(V)d]])).append("%% Health");
  if (b[%(E)d] > 0) sb.append(" / +").append(pctText(END[b[%(E)d]])).append("%% Stamina");
  if (b[%(I)d] > 0) sb.append(" / +").append(pctText(INT[b[%(I)d]])).append("%% Mana");
  if (b[%(R)d] > 0) sb.append(" / Regen ").append(pctText(REG[b[%(R)d]])).append("%% HP per ").append(REGEN_EVERY).append("s");
  if (b[%(S)d] > 0) sb.append(" / +").append(pctText(SPD[b[%(S)d]] * 100.0f)).append("%% Speed");
  if (sb.length() == 0) return hasOmni(s) ? "Bonuses - no talismans yet - the Omni counts as every bench accessory" : "Bonuses - none yet - put talismans in this bag";
  return "Bonuses - " + sb.substring(3);
}""" % dict(V=FAM["Vitality"], E=FAM["Endurance"], I=FAM["Intelligence"], R=FAM["Regeneration"], S=FAM["Speed"]), dfs))
''')

# ---------------------------------------------------------------- pretty: rarity names, legacy marker, Omni
rep('''  if (isTalisman(id)) {
    int tt = tierOf(id);
    return familyOf(id) + " " + (tt >= 0 && tt < TIER_NAMES.length ? TIER_NAMES[tt] : String.valueOf(tt));
  }
  String b = benchOf(id);''', '''  if (isTalisman(id)) {
    int tt = tierOf(id);
    String r = tt >= 0 && tt < RARITY.length ? RARITY[tt] : String.valueOf(tt);
    if (isLegacy(id)) return r + " " + familyOf(id) + " " + id.substring(id.lastIndexOf('_') + 1) + " - old";   // no parentheses in inline page text
    return r + " " + familyOf(id) + " Talisman";
  }
  if (OMNI.equals(id)) return "Omni Accessory";
  String b = benchOf(id);''')

# ---------------------------------------------------------------- benchList: acc:has value with the Omni expanded
rep('''# ================= AccStore =================
''', r'''# 0.4: bench accessory ids for the acc:has bridge value = EXACTLY ONE entry per bench id, at the best tier (a bench id -> max tier
# reduction, the same one SkyySacks' accessories() parser does). Real bench accessories first (slot order; the stored id of the best
# tier is kept as-is), then - when the Omni is in the bag - every bench at BENCH_MAX: a bench not listed yet is appended as the
# synthetic "Skyy_Accessory_<BenchId>_T<maxTier>", a listed bench whose real tier is lower is replaced IN PLACE by that synthetic id
# (review fix: a plain string-containment dedupe published a real Workbench_T2 AND the synthetic Workbench_T3, so SkyyMenu's
# "N bench accessories" count read 14 instead of 13). The Omni id itself is not listed, so acc:has keeps its 0.1 meaning.
# keys = bench id of out[k] (same index), best[k] = its tier; at most s.length + BENCH_IDS.length entries.
dfs.addMethod(CtNewMethod.make("""
public static java.util.ArrayList benchList(String[] s) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (s == null) return out;
  java.util.ArrayList keys = new java.util.ArrayList();
  int[] best = new int[s.length + BENCH_IDS.length];
  boolean omni = false;
  for (int i = 0; i < s.length; i++) {
    String id = s[i];
    if (id == null || isTalisman(id) || !isAccessory(id)) continue;
    if (OMNI.equals(id)) { omni = true; continue; }
    String bn = benchOf(id);
    if (bn == null) continue;
    int t = tierOf(id);
    int k = keys.indexOf(bn);
    if (k < 0) { keys.add(bn); out.add(id); best[out.size() - 1] = t; }
    else if (t > best[k]) { out.set(k, id); best[k] = t; }
  }
  if (omni) {
    for (int j = 0; j < BENCH_IDS.length; j++) {
      String syn = "Skyy_Accessory_" + BENCH_IDS[j] + "_T" + BENCH_MAX[j];
      int k2 = keys.indexOf(BENCH_IDS[j]);
      if (k2 < 0) { keys.add(BENCH_IDS[j]); out.add(syn); best[out.size() - 1] = BENCH_MAX[j]; }
      else if (BENCH_MAX[j] > best[k2]) { out.set(k2, syn); best[k2] = BENCH_MAX[j]; }
    }
  }
  return out;
}""", dfs))

# ================= AccStore =================
''')

# ---------------------------------------------------------------- AccStore.publish: expanded acc:has, modern acc:tal
cut('''# acc:has keeps its 0.1 meaning (bench accessories only''', '''st_.addMethod(CtNewMethod.make("""
public static void save(java.util.UUID u) {''', r'''# acc:has keeps its 0.1 meaning (bench accessories only - SkyySacks 0.6.1 parses every id there as Skyy_Accessory_<Bench>_T<n>, so a
# talisman id made a bogus "itality Talisman I" craft tab); talismans go to acc:tal:<uuid>; acc:fn:has still answers for both.
# 0.4: acc:has = AccDefs.benchList (one entry per bench at its best tier, the Omni counting as every bench at max tier); acc:tal lists modern ids (legacy
# Talisman/Ring/Artifact published as their Uncommon/Rare/Epic id)
st_.addMethod(CtNewMethod.make(f"""
public static void publish(java.util.UUID u) {{
  synchronized (lock(u)) {{
    String[] s = slots(u);
    StringBuilder acc = new StringBuilder();
    StringBuilder tal = new StringBuilder();
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null || !{PKG}.AccDefs.isTalisman(s[i])) continue;
      if (tal.length() > 0) tal.append(',');
      tal.append({PKG}.AccDefs.modernOf(s[i]));
    }}
    java.util.ArrayList bl = {PKG}.AccDefs.benchList(s);
    for (int i = 0; i < bl.size(); i++) {{
      if (acc.length() > 0) acc.append(',');
      acc.append((String) bl.get(i));
    }}
    bridge().put("acc:has:" + u.toString(), acc.toString());
    bridge().put("acc:tal:" + u.toString(), tal.toString());
    PUBLISHED.put(u, Boolean.TRUE);
  }}
}}""", st_))
''')

# ---------------------------------------------------------------- AccStore.has (acc:fn:has): legacy == modern, Omni synthetic entries
rep('''st_.addMethod(CtNewMethod.make("""
public static boolean has(java.util.UUID u, String id) {
  if (u == null || id == null) return false;
  synchronized (lock(u)) {
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) if (id.equals(s[i])) return true;
    return false;
  }
}""", st_))''', '''st_.addMethod(CtNewMethod.make(f"""
public static boolean has(java.util.UUID u, String id) {{
  if (u == null || id == null) return false;
  synchronized (lock(u)) {{
    String[] s = slots(u);
    for (int i = 0; i < s.length; i++) {{
      if (s[i] == null) continue;
      if (id.equals(s[i]) || id.equals({PKG}.AccDefs.modernOf(s[i]))) return true;
    }}
    if (id.startsWith("Skyy_Accessory_") && {PKG}.AccDefs.benchList(s).contains(id)) return true;   // 0.4: Omni = every bench at max tier
    return false;
  }}
}}""", st_))''')

# ---------------------------------------------------------------- bag page: rarity names + colours
rep(r'''Text: \\"Bench accessories unlock /craft recipes - talismans give stats while they sit in this bag.\\"''',
    r'''Text: \\"Bench accessories unlock /craft recipes - talismans add a percent on top of your stats while they sit here.\\"''')
rep(r'''b.appendInline("#SkyyAcc", "Label #SkyyAccBonus {{ Anchor: (Height: 20); Text: \\"" + safe({PKG}.AccDefs.bonusText(s)) + "\\"; Style: (FontSize: 12, RenderBold: true,''',
    r'''b.appendInline("#SkyyAcc", "Label #SkyyAccBonus {{ Anchor: (Height: 20); Text: \\"" + safe({PKG}.AccDefs.bonusText(s)) + "\\"; Style: (FontSize: 11, RenderBold: true,''')
rep(r'''      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 400, Height: 32); Text: \\"" + safe({PKG}.AccDefs.pretty(s[i])) + "\\"; Style: (FontSize: 13, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }}");
''', r'''      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 300, Height: 32); Text: \\"" + safe({PKG}.AccDefs.pretty(s[i])) + "\\"; Style: (FontSize: 13, RenderBold: true, TextColor: " + {PKG}.AccDefs.rarityColor(s[i]) + ", VerticalAlignment: Center); }}");
      b.appendInline("#SkyyAccSlot" + i, "Label {{ Anchor: (Width: 100, Height: 32); Text: \\"" + safe({PKG}.AccDefs.rarityName(s[i]).toUpperCase()) + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: " + {PKG}.AccDefs.rarityColor(s[i]) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
''')
rep(r'''    b.appendInline("#SkyyAccInv" + i, "Label {{ Anchor: (Width: 400, Height: 28); Text: \\"" + safe({PKG}.AccDefs.pretty(id)) + "\\"; Style: (FontSize: 12, TextColor: #ffffff, VerticalAlignment: Center); }}");
''', r'''    b.appendInline("#SkyyAccInv" + i, "Label {{ Anchor: (Width: 300, Height: 28); Text: \\"" + safe({PKG}.AccDefs.pretty(id)) + "\\"; Style: (FontSize: 12, TextColor: " + {PKG}.AccDefs.rarityColor(id) + ", VerticalAlignment: Center); }}");
    b.appendInline("#SkyyAccInv" + i, "Label {{ Anchor: (Width: 100, Height: 28); Text: \\"" + safe({PKG}.AccDefs.rarityName(id).toUpperCase()) + "\\"; Style: (FontSize: 11, RenderBold: true, TextColor: " + {PKG}.AccDefs.rarityColor(id) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }}");
''')

# ---------------------------------------------------------------- bag page events: legacy ids convert at the bag boundary
rep('''      String id = {PKG}.AccStore.unequip(u, i);
      if (id == null) return;
      if (!giveOne(player, id)) {{ {PKG}.AccStore.put(u, i, id); this.info = "your inventory is full"; }}
      else this.info = "unequipped " + {PKG}.AccDefs.pretty(id);
''', '''      String id = {PKG}.AccStore.unequip(u, i);
      if (id == null) return;
      String give = {PKG}.AccDefs.modernOf(id);   // 0.4: a legacy Talisman/Ring/Artifact comes back as the modern (upgradable) item
      if (!giveOne(player, give)) {{ {PKG}.AccStore.put(u, i, id); this.info = "your inventory is full"; }}
      else this.info = "unequipped " + {PKG}.AccDefs.pretty(give) + (give.equals(id) ? "" : " - your old " + {PKG}.AccDefs.pretty(id) + " came back as the new upgradable talisman");
''')
rep('''      String id = this.invIds[i];
      String why = "bag is full, or the same or a better " + ({PKG}.AccDefs.isTalisman(id) ? {PKG}.AccDefs.familyOf(id) + " talisman" : "bench accessory") + " is already equipped";
      if (!{PKG}.AccStore.canEquip(u, id)) {{ this.info = why; rebuild(); return; }}
      if (!takeOne(player, id)) {{ this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }}
      String res = {PKG}.AccStore.equip(u, id);
''', '''      String id = this.invIds[i];
      String put = {PKG}.AccDefs.modernOf(id);   // 0.4: a legacy talisman is stored as its modern rarity id
      String why = "bag is full, or the same or a better " + ({PKG}.AccDefs.isTalisman(id) ? {PKG}.AccDefs.familyOf(id) + " talisman" : ({PKG}.AccDefs.OMNI.equals(id) ? "Omni accessory" : "bench accessory")) + " is already equipped";
      if (!{PKG}.AccStore.canEquip(u, put)) {{ this.info = why; rebuild(); return; }}
      if (!takeOne(player, id)) {{ this.info = "could not find " + {PKG}.AccDefs.pretty(id) + " in your inventory"; rebuild(); return; }}
      String res = {PKG}.AccStore.equip(u, put);
''')
rep('''      if (res.length() > 0) {{
        int g = giveBack(player, u, res);
        String old = {PKG}.AccDefs.pretty(res);
''', '''      if (res.length() > 0) {{
        res = {PKG}.AccDefs.modernOf(res);
        int g = giveBack(player, u, res);
        String old = {PKG}.AccDefs.pretty(res);
''')
rep('''      else this.info = "equipped " + {PKG}.AccDefs.pretty(id);
''', '''      else this.info = "equipped " + {PKG}.AccDefs.pretty(put) + (put.equals(id) ? "" : " - converted from your old " + {PKG}.AccDefs.pretty(id));
''')

# ---------------------------------------------------------------- /accessories: COMMAND RULES (Adventurer group)
rep('''  super("accessories", "Open your accessory bag");
  addAliases(new String[] { "acc", "accbag" });
''', '''  super("accessories", "Open your accessory bag");
  addAliases(new String[] { "acc", "accbag" });
  setPermissionGroups(new String[] { "hytale:Adventurer" });   // 0.4: COMMAND RULES - ordinary players lack the auto node
''')

# ---------------------------------------------------------------- AccEffects: percent of the flat max, posted as ADDITIVE
cut('''# set (amt != 0) or remove (amt == 0) our MAX modifier on one stat; only writes when something changes''',
    '''# Speed (0.3): the talisman bonus is POSTED as source "accessories.talismans"''', r'''# 0.4 PERCENT LAYER. Verified in HytaleServer.jar bytecode (EntityStatValue.computeModifiers): max = EntityStatType.max, then
# max + SUM(ADDITIVE MAX amounts), then max * SUM(MULTIPLICATIVE MAX amounts). MULTIPLICATIVE amounts are summed, so ours (1.10) next
# to vanilla's Meat_Buff (1.05) would give x2.15 - not usable. Instead: flat = type max + every OTHER additive MAX modifier (armour,
# SkyySkills, food boosts), ours = ADDITIVE round(flat x pct / 100, 2 decimals) under the 0.2/0.3 key (overwrites the flat value
# those versions saved with the player). A vanilla multiplicative buff then scales flat + ours = flat x (1 + pct) x buff.
eff.addMethod(CtNewMethod.make(f"""
public static float flatMax({ESV} v, int idx, String key) {{
  float base = 0.0f;
  try {{
    {EST} t = ({EST}) {EST}.getAssetMap().getAsset(idx);
    if (t != null) base = t.getMax();
  }} catch (Throwable e) {{ }}
  java.util.Map mods = v.getModifiers();
  if (mods == null) return base;
  java.util.Iterator it = mods.keySet().iterator();
  while (it.hasNext()) {{
    Object k = it.next();
    if (key.equals(k)) continue;
    Object o = mods.get(k);
    if (!(o instanceof {SMO})) continue;
    {SMO} sm = ({SMO}) o;
    if (sm.getTarget() != {MTG}.MAX || sm.getCalculationType() != {CAL}.ADDITIVE) continue;
    base = base + sm.getAmount();
  }}
  return base;
}}""", eff))
# set (pct > 0) or remove (pct == 0) our MAX modifier on one stat (pct = percent of the flat max); only writes when something changes
eff.addMethod(CtNewMethod.make(f"""
public static void mod({ESM} m, int idx, String key, float pct) {{
  if (idx < 0) return;
  try {{
    {ESV} v = m.get(idx);
    if (v == null) return;   // getModifier/putModifier would log "No EntityStatValue found" every second
    {MOD} cur = m.getModifier(idx, key);
    float amt = 0.0f;
    if (pct > 0.0f) {{
      float flat = flatMax(v, idx, key);
      amt = Math.round(flat * pct) / 100.0f;
    }}
    if (amt <= 0.0f) {{ if (cur != null) m.removeModifier(idx, key); return; }}
    {SMO} want = new {SMO}({MTG}.MAX, {CAL}.ADDITIVE, amt);
    if (cur != null && cur.equals(want)) return;
    m.putModifier(idx, key, want);
  }} catch (Throwable t) {{ }}
}}""", eff))
''')
rep('''            float amt = {PKG}.AccDefs.REG[rt];
''', '''            // 0.4: percent of the FULL current max Health, ON PURPOSE (not flatMax like Vitality/Endurance/Intelligence, which ARE the
            // percent layer): the item text says "of your max Health" = the Health bar, incl. this tick's Vitality (putModifier recomputes max)
            float amt = max * {PKG}.AccDefs.REG[rt] / 100.0f;
''')

# ---------------------------------------------------------------- plugin log line
rep('''log("[SkyyAccessories] {VERSION} ready - /accessories, right-click the Accessory Bag; %d bench accessories, %d talismans (stat effects on)" );
}}""" % (sum(b[3] for b in BENCHES), len(TALISMANS) * 3), pl))''',
    '''log("[SkyyAccessories] {VERSION} ready - /accessories, right-click the Accessory Bag; %d bench accessories + Omni, %d talismans in 5 rarities (percent layer on)" );
}}""" % (sum(b[3] for b in BENCHES), len(TALISMANS) * 5), pl))''')

# ---------------------------------------------------------------- assets: bench rarity, bag text, talismans, legacy, Omni
rep('QUAL = ["Common", "Common", "Uncommon", "Rare", "Rare", "Rare", "Rare", "Rare"]\n',
    'QUAL = ["Common", "Common", "Uncommon", "Rare", "Epic", "Legendary", "Legendary", "Legendary"]   # 0.4: T1 Common .. T5+ Legendary (= AccDefs.rarityOf)\n'
    'assert all(q in RARITIES for q in QUAL)\n')
rep('''talismans in it give you stats (one per family counts)." % CAP''',
    '''talismans in it add a percent on top of your stats (one per family counts, best rarity wins); the Omni accessory counts as every bench accessory." % CAP''')
cut('EFFECT = {\n', 'files["Server/Languages/en-US/server.lang"] = ', r'''def pct_s(v):
    return "%g" % v
EFFECT = {
    "Vitality":     lambda v: "+%s%% max Health (on top of the flat Health your armour and skills give)" % pct_s(v),
    "Endurance":    lambda v: "+%s%% max Stamina (on top of the flat Stamina your armour and skills give)" % pct_s(v),
    "Intelligence": lambda v: "+%s%% max Mana (a percent of the Mana your gear and skills give)" % pct_s(v),
    "Regeneration": lambda v: "heals %s%% of your max Health every %d seconds" % (pct_s(v), REGEN_EVERY),
    "Speed":        lambda v: "+%s%% movement speed (on top of Acrobatics)" % pct_s(v),
}
tal_count = 0
legacy_count = 0
for fam, word, crystal, gem, vals, recipes in TALISMANS:
    vis = visual_of("Ingredient_Crystal_" + crystal)   # crystal fragment model in the family colour (the icon and Quality show the rarity)
    for t in range(1, 6):
        iid = "Skyy_Talisman_%s_%s" % (fam, RARITIES[t])
        if t == 1:
            rin = [mat(m, q) for m, q in recipes[0]]
        else:
            rin = [{"ItemId": "Skyy_Talisman_%s_%s" % (fam, RARITIES[t - 1]), "Quantity": 1}] + [mat(m, q) for m, q in recipes[t - 1]]
        icon = icon_of("Ingredient_Crystal_" + crystal) if t <= 2 else icon_of(gem)
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(item(iid, icon, RARITIES[t], rin, WB_REQ, visual=vis), indent=2)
        disp = "%s %s Talisman" % (RARITIES[t], fam)
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        d = "%s accessory. Keep it in your Accessory Bag: %s. Only your best %s talisman counts." % (RARITIES[t], EFFECT[fam](vals[t - 1]), fam)
        if t < 5:
            d += " Upgrade it at a Workbench into the %s %s Talisman (this talisman + %s)." % (
                RARITIES[t + 1], fam, ", ".join("%d %s" % (q, vname(m)) for m, q in recipes[t]))
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        tal_count += 1
    # 0.2/0.3 legacy ids: asset kept so old stacks still load and render, NO recipe; they count as Uncommon/Rare/Epic
    for lt in (1, 2, 3):
        iid = "Skyy_Talisman_%s_%s" % (fam, TIER_NAMES[lt])
        r = LEGACY_TIER[lt]
        icon = icon_of("Ingredient_Crystal_" + crystal) if lt == 1 else icon_of(gem)
        node = item(iid, icon, TIER_QUAL[lt], [], WB_REQ, visual=vis)
        del node["Recipe"]
        assert TIER_QUAL[lt] == RARITIES[r]
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        disp = "%s %s (old)" % (fam, TIER_NAMES[lt])
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        d = ("Old talisman that counts as the %s %s Talisman: %s. Equipping it in your Accessory Bag stores it as the new %s %s Talisman, "
             "and Unequip gives you that one back, which can be upgraded at a Workbench.") % (RARITIES[r], fam, EFFECT[fam](vals[r - 1]), RARITIES[r], fam)
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        legacy_count += 1
print("talisman items:", tal_count, "legacy (no recipe):", legacy_count)

# 0.4 OMNI accessory: Workbench recipe = the max-tier accessory of every bench; counts as all of them (AccDefs.benchList)
omni_in = []
for bench_id, bench_item, name, tiers, ups in BENCHES:
    top = "Skyy_Accessory_%s_T%d" % (bench_id, tiers)
    assert "Server/Item/Items/Utility/%s.json" % top in files, top
    omni_in.append({"ItemId": top, "Quantity": 1})
assert len(omni_in) == 13
files["Server/Item/Items/Utility/%s.json" % OMNI] = json.dumps(item(OMNI, icon_of("Rock_Gem_Diamond"), "Legendary", omni_in, WB_REQ), indent=2)
lang.append("items.%s.name=Omni Accessory" % OMNI); lang.append("server.items.%s.name=Omni Accessory" % OMNI)
d = ("Legendary accessory. Keep it in your Accessory Bag and it counts as EVERY bench accessory at its highest tier (%s), so /craft shows "
     "all of their recipes. It has its own slot rule, so it can sit next to other bench accessories. Crafted at a Workbench from all %d "
     "top-tier bench accessories.") % (", ".join(("%s %s" % (b[2], ROMAN[b[3]])) if b[3] > 1 else b[2] for b in BENCHES), len(BENCHES))
lang.append("items.%s.description=%s" % (OMNI, d)); lang.append("server.items.%s.description=%s" % (OMNI, d))
''')
rep('''stat talismans (Vitality, Endurance, Intelligence, Regeneration, Speed) work while they sit in the bag; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol. Zero dependencies."''',
    '''stat talismans (Vitality, Endurance, Intelligence, Regeneration, Speed) in rarities Common to Legendary add a percent on top of your flat stats while they sit in the bag; the Omni accessory counts as every bench accessory; speed stacks with SkyySkills Acrobatics through the shared Skyy movement protocol. Zero dependencies."''')

# ---------------------------------------------------------------- sanity
assert 'if (t > 3) t = 3;' not in s and 'TIER_NAMES[tt]' not in s and 'len(TALISMANS) * 3' not in s
assert s.count('setPermissionGroups(') == 1 and 'VERSION = "0.4"' in s
assert 'if (!out.contains(syn)) out.add(syn);' not in s and s.count('public static java.util.ArrayList benchList(') == 1   # review fix: per-bench max, not string dedupe
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.3
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == "\r\n" else "LF"))
