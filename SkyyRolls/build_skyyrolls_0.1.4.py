"""SkyyRolls 0.1.4 - build script (javassist via jpype). Item rolls (reforge + stats) in ItemStack metadata, shown on the tooltip,
and the Reforge Anvil page.
Run:   python build_skyyrolls_0.1.4.py            -> SkyyRolls/SkyyRolls-0.1.4.jar
       python build_skyyrolls_0.1.4.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Player command (hytale:Adventurer):
  /reforge               opens the Reforge Anvil page: pick a weapon, armor piece or tool from "Your gear" (or hold it when you
                         type /reforge), see its roll + the coin cost for its rarity, click Reforge to reroll it for coins
                         (SkyyCoins bridge: taken first, refunded if the reroll fails); the item stays in its own slot.
                         Costs: Skyy_SkyyRolls/reforge.properties (re-read when the file changes).
Commands (ADMIN ONLY, see Permissions below):
  /rolls                 same as /rolls read
  /rolls read            prints the rolls on the item in your hand + the raw metadata JSON (shows what vanilla stores too);
                         an item rolled before 0.1.3 gets its tooltip written here
  /rolls reroll          replaces the item in your hand with the same item + fresh rolls (same slot) - weapons, armor, tools only
  /rolls give [itemId]   gives one item (default Weapon_Longsword_Copper) with random rolls stored in metadata key "SkyyRolls"
                         {reforge: <name>, dmg: +%, str: n, crit: n, quality: 0..100, rolledAt: millis} - weapons, armor, tools only
  /rolls clear           removes the rolls (and the rolls tooltip) from the item in your hand, keeps everything else
  The 0.1 flag forms still work: /rolls --action give|read|reroll|clear [--item <itemId>]
Test protocol: give -> read -> relog -> read again (must match) -> drop + pick up -> read -> put in a chest and take out -> read.
API: ItemStack.withMetadata(String, BsonValue) returns a NEW stack; ItemStack.getMetadata() -> org.bson.BsonDocument;
Inventory.getItemInHand(), getActiveHotbarSlot(), getHotbar().setItemStackForSlot(short, ItemStack).

0.1.4: /reforge Reforge Anvil page (pick from your gear, coins taken first + refunded on failure, cost by rarity from
  reforge.properties); tooltip stat lines show the BASE value with the roll in brackets, 'Damage: 11-48 (+24%)', base damage read
  from the engine's own weapon damage data (ItemWeapon.getBasicDamageBreakdown, computed by ItemModule at asset load - covers
  modded weapons); one STATS table drives rolls, tooltip, page and chat (easy to extend); VIEW_V 2 refreshes old tooltips.
  Design, evidence and what is left out: tools/rolls_0_1_4_patch.py.
0.1.3: the rolls are SHOWN on the item: native ItemDisplay metadata (Name = rarity-coloured '<Reforge> <item>', Description =
  vanilla description + one line per roll), written by give/reroll, by /rolls read and by a join refresh for older rolled items;
  only Weapon_* (no ammo) / Armor_* / Tool_* items can be given or rerolled (never Skyy_* items); new /rolls clear; hand read and
  write use the same slot. Evidence + details in tools/rolls_0_1_3_patch.py.
0.1.2: /rolls give takes a plain name or any-case id ("/rolls give mithril bow", "/rolls give weapon_shortbow_mithril") and never
  gives an unknown id (it suggests matches instead) - notes in tools/rolls_0_1_2_patch.py.
0.1.1: positional arguments fixed. In 0.1 "give|read|reroll" and the item id were OPTIONAL args, and optional args are not
  positional: AbstractCommand.acceptCall0 needs the number of positional tokens to EQUAL the number of required args (this
  command never calls setAllowsExtraArguments), so "/rolls give" failed with server.commands.parsing.error.wrongNumberRequiredParameters
  and only "/rolls --action give" worked. Now read / reroll / give are real subcommands (SkyyParty addSubCommand pattern) and
  "give <itemId>" is a usage variant of give (SkyyEssentials TpAccept pattern: description-only constructor + withRequiredArg,
  the parent calls addUsageVariant). Bytecode checks against HytaleServer.jar (2026-09-23):
  - checkForExecutingSubcommands (called first by acceptCall0): if the first positional token names a subcommand
    (getSubCommand: lower-cased name, then aliases) -> convertToSubCommand + that subcommand's acceptCall0. Otherwise
    variantCommands.get(tokenCount) runs when this command's own required count differs. addUsageVariant keys variants by
    their required-arg count (a duplicate count throws), so "give" (0) and "give <itemId>" (1) are picked by count.
  - acceptCall0: only an AbstractCommandCollection refuses to run itself when a token is not a subcommand; this root is an
    AbstractPlayerCommand with 0 required args, so "/rolls" alone reaches its own execute() (= read). The root keeps the 0.1
    optional --action/--item args, so the old flag forms still work for free (flags are not positional tokens).
  Rolls, messages and item handling are otherwise identical to 0.1.
Permissions (0.1.4): /reforge is a PLAYER command - its constructor calls setPermissionGroups(new String[] { "hytale:Adventurer" })
  (COMMAND RULES; vanilla /help pattern, same as SkyyAccessories /accessories). Everything below is about /rolls only.
Permissions: SkyyRolls is a test spike and /rolls give creates items, so it stays ADMIN-ONLY on purpose: there is NO
  setPermissionGroups(new String[] { "hytale:Adventurer" }) here (unlike the player commands in SkyyEssentials and the other
  Skyy mods). AbstractCommand.setOwner() gives the root, every subcommand and the variant an auto node (plugin base
  "<group>.<name>" lower-cased, spaces -> "_"; a subcommand appends ".<name>", a variant reuses its parent's node):
  skyy.0.1.4_skyyrolls.command.rolls, ...command.rolls.read, ...command.rolls.reroll, ...command.rolls.give, ...command.rolls.clear.
  hasPermission() on a subcommand without permission groups also requires the parent's node. Default players
  (hytale:Adventurer) have none of these; only "*" admins do. The version is part of the node, so it changes on every bump.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.4"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
BD  = "org.bson.BsonDocument"
BV  = "org.bson.BsonValue"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IDM = "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata"
IQ  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality"
I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"
PCOL = "com.hypixel.hytale.protocol.Color"
TXN = "com.hypixel.hytale.server.core.inventory.transaction.Transaction"
HSV = "com.hypixel.hytale.server.core.HytaleServer"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"
# 0.1.4: engine weapon damage data (tooltip base values) + the inline page API (same classes as SkyyAccessories / SkyyGuilds pages)
IWP = "com.hypixel.hytale.server.core.asset.type.item.config.ItemWeapon"
DBD = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown"
DBE = "com.hypixel.hytale.server.core.asset.type.item.config.damageData.DamageBreakdown$Entry"
ILT = "com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap"
PAGE = "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage"
LIFE = "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime"
UCB = "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"
UEB = "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder"
EVD = "com.hypixel.hytale.server.core.ui.builder.EventData"
BT  = "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType"

for c, m in ((IS, "withMetadata"), (IS, "getMetadata"), (INV, "getItemInHand"), (INV, "getActiveHotbarSlot"), (INV, "getHotbar"),
             (IC, "setItemStackForSlot"), (IC, "addItemStack"), (PLA, "getInventory"), (CTX, "provided"), (BD, "append"),
             (AC, "addSubCommand"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "withOptionalArg"),
             (AC, "setAllowsExtraArguments"), (CTX, "getInputString"), (ITM, "getAssetMap"),
             (IDM, "KEYED_CODEC"), (IDM, "KEY"), (IS, "getItem"), (IS, "getQualityIndex"), (IS, "getItemId"), (IS, "getQuantity"),
             (IS, "getDurability"), (IS, "getMaxDurability"), (IS, "isEmpty"),
             (ITM, "getTranslationKey"), (ITM, "getTranslationMessage"), (ITM, "getDescriptionTranslationKey"),
             (ITM, "getDescriptionTranslationMessage"), (IQ, "getAssetMap"), (IQ, "getTextColor"), (PCOL, "red"), (PCOL, "green"),
             (PCOL, "blue"), (I18N, "get"), (I18N, "getMessage"), (MSG, "color"), (MSG, "insert"), (MSG, "translation"), (MSG, "empty"),
             (TXN, "succeeded"), (INV, "usingToolsItem"), (INV, "getTools"), (INV, "getActiveToolsSlot"), (INV, "getBackpack"),
             (INV, "getArmor"), (INV, "getUtility"), (INV, "getStorage"), (IC, "getItemStack"), (IC, "getCapacity"),
             (HSV, "SCHEDULED_EXECUTOR"), (UNI, "get"), (UNI, "getWorld"), (PR, "getWorldUuid"), (PR, "getReference"),
             (PR, "isValid"), (PR, "getUuid"), (PR, "getUsername"), (PR, "getComponentType"), (PRE, "getPlayerRef"), (WLD, "execute"),
             (REF, "isValid"), (REF, "getStore"), (BD, "containsKey"), (BD, "remove"), (BD, "clone"), (BV, "asNumber"),
             (IS, "getFromMetadataOrNull"), ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):
    B.probe(pool, c, m)
for c, m in ((ITM, "getWeapon"), (IWP, "getBasicDamageBreakdown"), (IWP, "getUltimateDamageBreakdown"), (DBD, "entries"),
             (DBE, "min"), (DBE, "max"), (IQ, "getLocalizationKey"), (IQ, "getId"), (ILT, "getIndex"), (ILT, "getAsset"),
             (PAGE, "rebuild"), (PAGE, "build"), (PAGE, "handleDataEvent"), (LIFE, "CanDismiss"), (PLA, "getPageManager"),
             ("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager", "openCustomPage"),
             (UCB, "appendInline"), (UCB, "set"), (UEB, "addEventBinding"), (EVD, "of"), (BT, "Activating"),
             (AC, "setPermissionGroups"), (IC, "setItemStackForSlot"), (INV, "getActiveToolsSlot"), (JP, "getDataDirectory"),
             (IS, "getQuantity")):
    B.probe(pool, c, m)

PKG = "com.skyy.rolls"
rl  = pool.makeClass(PKG + ".Rolls")
rdc = pool.makeClass(PKG + ".RollsReadCmd", pool.get(APC))
rrc = pool.makeClass(PKG + ".RollsRerollCmd", pool.get(APC))
clc = pool.makeClass(PKG + ".RollsClearCmd", pool.get(APC))
gvc = pool.makeClass(PKG + ".RollsGiveVariantCmd", pool.get(APC))
gvr = pool.makeClass(PKG + ".RollsGiveCmd", pool.get(APC))
cmd = pool.makeClass(PKG + ".RollsCmd", pool.get(APC))
rft = pool.makeClass(PKG + ".RollsRefreshTask")
rdy = pool.makeClass(PKG + ".RollsReady")
pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))
rfg = pool.makeClass(PKG + ".Reforge")                          # 0.1.4: costs config, coins bridge, gear scan (pure static)
rpg = pool.makeClass(PKG + ".ReforgePage", pool.get(PAGE))      # 0.1.4: /reforge inline page
rfc = pool.makeClass(PKG + ".ReforgeCmd", pool.get(APC))        # 0.1.4: /reforge (hytale:Adventurer)

# 0.1.4: new Java is written as raw strings with @NAME@ placeholders (SkyyGuilds style): no f-string brace doubling, and a Java \"
# is written as-is. J() fails the build on any placeholder it cannot resolve.
import re as _re
T = {"PKG": PKG, "IS": IS, "BD": BD, "BV": BV, "MSG": MSG, "ITM": ITM, "IQ": IQ, "IWP": IWP, "DBD": DBD, "DBE": DBE, "INV": INV,
     "IC": IC, "PLA": PLA, "PR": PR, "REF": REF, "ST": ST, "WLD": WLD, "CTX": CTX, "TXN": TXN, "PAGE": PAGE, "LIFE": LIFE,
     "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT}


def J(src):
    for k, v in T.items():
        src = src.replace("@" + k + "@", v)
    left = _re.findall(r"@[A-Z]+@", src)
    assert not left, "unresolved placeholder(s): %s" % left
    return src


def M(c, src):
    c.addMethod(CtNewMethod.make(J(src), c))


def F(c, src):
    c.addField(CtField.make(J(src), c))


def C(c, src):
    c.addConstructor(CtNewConstructor.make(J(src), c))


# ================= Rolls (pure helpers) =================
rl.addField(CtField.make(f"public static {LOG} LOG;", rl))
rl.addField(CtField.make('public static final String[] REFORGES = new String[] { "Sharp", "Heroic", "Spicy", "Legendary", "Fabled", "Gentle", "Odd", "Fast", "Epic", "Withered" };', rl))
rl.addField(CtField.make('public static final String DEFAULT_ITEM = "Weapon_Longsword_Copper";', rl))
# 0.1.3: our marker key next to the engine's "ItemDisplay" key, its version, and the Weapon_* id tokens that mean ammo
rl.addField(CtField.make('public static final String VIEW_KEY = "SkyyRollsView";', rl))
rl.addField(CtField.make('public static final int VIEW_V = 2;', rl))   # 0.1.4: 2 = base value + (roll) lines -> old tooltips refresh
# ---------------- 0.1.4 STAT TABLE (Skyy is still designing the SkyyGear stats - this is the placeholder set) ----------------
# One row per rolled stat: (metadata key in "SkyyRolls", label on the tooltip / page, max roll (rolled 0..max), unit, base source).
# base source: "damage" = the weapon's base damage range from the engine's weapon damage data (Rolls.damageText);
#              ""       = the stat has no base value, its line shows only the roll ("Strength: +12").
# A new stat = one row here (+ a branch in Rolls.baseText when it has a base value). roll(), the tooltip, the /reforge page, the
# chat line and the "Before" summary all loop over these arrays. Items rolled before a row existed simply do not show that line.
# "reforge", "quality" and "rolledAt" are fixed keys (the reforge name, the 0-100 roll quality, the roll time), not stats.
STATS = [
    # key     label       max  unit  base
    ("dmg",  "Damage",    30,  "%",  "damage"),
    ("str",  "Strength",  25,  "",   ""),
    ("crit", "Crit",      15,  "",   ""),
]
assert len(set(r[0] for r in STATS)) == len(STATS), "duplicate stat key"
for _r in STATS:
    assert _re.match(r"^[a-z][a-zA-Z0-9]*$", _r[0]) and _r[0] not in ("reforge", "quality", "rolledAt"), _r
    assert _r[2] > 0 and _r[3] in ("", "%") and _r[4] in ("", "damage"), _r
    assert '"' not in _r[1] and "\\" not in _r[1], _r


def _jstr(vals):
    return "new String[] { " + ", ".join('"%s"' % v for v in vals) + " }"


F(rl, "public static final String[] STAT_KEY = " + _jstr([r[0] for r in STATS]) + ";")
F(rl, "public static final String[] STAT_LABEL = " + _jstr([r[1] for r in STATS]) + ";")
F(rl, "public static final int[] STAT_MAX = new int[] { " + ", ".join(str(r[2]) for r in STATS) + " };")
F(rl, "public static final String[] STAT_UNIT = " + _jstr([r[3] for r in STATS]) + ";")
F(rl, "public static final String[] STAT_BASE = " + _jstr([r[4] for r in STATS]) + ";")
rl.addField(CtField.make('public static final String[] AMMO = new String[] { "arrow", "arrows", "bolt", "bolts", "bomb", "bombs", "dart", "darts", "grenade", "grenades", "ammo", "bullet", "bullets", "shell", "shells", "shuriken", "shurikens", "thrown" };', rl))
rl.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyRolls] " + msg); } catch (Throwable t) { }
}""", rl))
rl.addMethod(CtNewMethod.make("""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyRolls] " + msg); } catch (Throwable t) { }
}""", rl))
# SkyyProfiles contract: profile:busy:<uuid> is set while the live inventory may not belong to the active profile (crash recovery)
rl.addMethod(CtNewMethod.make("""
public static boolean busy(java.util.UUID u) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (u != null && b instanceof java.util.Map) return ((java.util.Map) b).get("profile:busy:" + u) != null;
  } catch (Throwable t) { }
  return false;
}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static int num({BD} d, String k) {{
  try {{ {BV} v = d == null ? null : d.get(k); if (v != null && v.isNumber()) return v.asNumber().intValue(); }} catch (Throwable t) {{ }}
  return 0;
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String str({BD} d, String k) {{
  try {{ {BV} v = d == null ? null : d.get(k); if (v != null && v.isString()) return v.asString().getValue(); }} catch (Throwable t) {{ }}
  return "?";
}}""", rl))
# 0.1.3 rule (Skyy): only weapons, armor and tools; no ammo; never a Skyy item. null = rollable, else the reason for the chat line.
rl.addMethod(CtNewMethod.make("""
public static String refuseId(String id) {
  if (id == null || id.length() == 0) return "hold a weapon, armor piece or tool first";
  String low = id.toLowerCase();
  if (low.startsWith("skyy") || low.indexOf("_skyy") >= 0) return id + " is a Skyy item - Skyy items never get rolls";
  boolean w = id.startsWith("Weapon_");
  if (!w && !id.startsWith("Armor_") && !id.startsWith("Tool_")) return id + " can't have rolls - only weapons, armor and tools (Weapon_*, Armor_*, Tool_* items) get them";
  if (w) {
    String[] parts = id.split("_");
    for (int i = 1; i < parts.length; i++) {
      String p = parts[i].toLowerCase();
      for (int j = 0; j < AMMO.length; j++) {
        if (p.equals(AMMO[j])) return id + " is ammo (" + parts[i] + ") - arrows, bombs, darts, grenades and other ammo never get rolls";
      }
    }
  }
  return null;
}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String refuse({IS} it) {{
  if (it == null || it.isEmpty()) return "hold a weapon, armor piece or tool first";
  return refuseId(it.getItemId());
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static boolean hasRolls({IS} it) {{
  if (it == null || it.isEmpty()) return false;
  {BD} md = it.getMetadata();
  if (md == null) return false;
  {BV} v = md.get("SkyyRolls");
  return v != null && v.isDocument();
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String hex({PCOL} c) {{
  if (c == null) return null;
  return "#" + Integer.toHexString(256 | (c.red & 255)).substring(1) + Integer.toHexString(256 | (c.green & 255)).substring(1)
    + Integer.toHexString(256 | (c.blue & 255)).substring(1);
}}""", rl))
# rarity = the stack's engine quality (Server/Item/Qualities/*.json TextColor: Common #c9d2dd, Uncommon #3e9049, Rare #2770b7,
# Epic #8b339e, Legendary #bb8a2c); the client already frames the tooltip in that quality and prints its label
rl.addMethod(CtNewMethod.make(f"""
public static String rarityColor({IS} it) {{
  try {{
    Object q = {IQ}.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof {IQ}) {{
      String h = hex((({IQ}) q).getTextColor());
      if (h != null) return h;
    }}
  }} catch (Throwable t) {{ }}
  return "#c9d2dd";
}}""", rl))
# en-US text of a translation key, null when missing (SimpleEnchantments NativeTooltipManager.resolveServerTranslation/isMissingTranslation)
rl.addMethod(CtNewMethod.make(f"""
public static String tr(String key) {{
  if (key == null) return null;
  try {{
    {I18N} m = {I18N}.get();
    if (m == null) return null;
    String s = m.getMessage("en-US", key);
    if (s == null || s.trim().length() == 0 || s.equals(key)) return null;
    return s;
  }} catch (Throwable t) {{ return null; }}
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static {MSG} statLine(String label, String value, String col) {{
  {MSG} m = {MSG}.empty();
  m.insert({MSG}.raw(label + ": ").color("#AAAAAA"));
  m.insert({MSG}.raw(value).color(col));
  return m;
}}""", rl))
rl.addMethod(CtNewMethod.make("""
public static String qualityColor(int q) {
  if (q >= 90) return "#55FFFF";
  if (q >= 70) return "#55FF55";
  if (q >= 30) return "#FFFF55";
  return "#FF5555";
}""", rl))
# Name: one raw coloured line "<Reforge> <English item name>"; if the name has no en-US text (or has {params}) the item's own
# translation Message is inserted as a child instead
rl.addMethod(CtNewMethod.make(f"""
public static {MSG} nameMsg({IS} it, String reforge, String col) {{
  String base = null;
  try {{ base = tr(it.getItem().getTranslationKey()); }} catch (Throwable t) {{ base = null; }}
  if (base != null && base.indexOf(123) < 0) return {MSG}.raw(reforge + " " + base).color(col);
  {MSG} m = {MSG}.empty().color(col);
  m.insert({MSG}.raw(reforge + " ").color(col));
  try {{ m.insert(it.getItem().getTranslationMessage().color(col)); }} catch (Throwable t) {{ m.insert({MSG}.raw(it.getItemId()).color(col)); }}
  return m;
}}""", rl))
# ---- 0.1.4: base values. The engine computes every weapon's damage at asset load (ItemModule.computeWeaponData ->
# WeaponDamageDataCollector.calculate(item, Primary / Ability1) -> ItemWeapon.setBasicDamageBreakdown / setUltimateDamageBreakdown;
# DamageBreakdown.entries() = records (labelKey, min, max)). Base damage = lowest min .. highest max of the basic (Primary) breakdown;
# the ultimate (signature) breakdown only when the basic one is empty. A min of 0 counts, a min below 0 (a RandomPercentageModifier
# of 1 or more; computeDamageRange has no clamp) counts as 0. Evidence: tools/rolls_0_1_4_patch.py.
M(rl, """
public static String fnum(float f) {
  long r = Math.round((double) f);
  if (Math.abs(f - (float) r) < 0.05f) return String.valueOf(r);
  return String.valueOf(Math.round((double) f * 10.0) / 10.0);
}""")
M(rl, """
public static @BD@ rollsDoc(@IS@ it) {
  if (it == null || it.isEmpty()) return null;
  @BD@ md = it.getMetadata();
  if (md == null) return null;
  @BV@ v = md.get("SkyyRolls");
  if (v == null || !v.isDocument()) return null;
  return v.asDocument();
}""")
M(rl, """
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
M(rl, """
public static float[] damageRange(@IS@ it) {
  try {
    if (it == null || it.isEmpty()) return null;
    @ITM@ item = it.getItem();
    if (item == null) return null;
    @IWP@ w = item.getWeapon();
    if (w == null) return null;
    float[] r = rangeOf(w.getBasicDamageBreakdown());
    if (r == null) r = rangeOf(w.getUltimateDamageBreakdown());
    return r;
  } catch (Throwable t) { return null; }
}""")
M(rl, """
public static String damageText(@IS@ it) {
  float[] r = damageRange(it);
  if (r == null) return null;
  String a = fnum(r[0]);
  String z = fnum(r[1]);
  return a.equals(z) ? a : a + "-" + z;
}""")
# base value text of one stat, null = no base (the line shows only the roll). New base sources go here.
M(rl, """
public static String baseText(@IS@ it, String src) {
  if (src == null || src.length() == 0 || it == null) return null;
  if (src.equals("damage")) return damageText(it);
  return null;
}""")
M(rl, """
public static boolean hasStat(@BD@ d, int i) {
  return d != null && i >= 0 && i < STAT_KEY.length && d.containsKey(STAT_KEY[i]);
}""")
M(rl, """
public static String bonus(@BD@ d, int i) {
  int v = num(d, STAT_KEY[i]);
  return (v >= 0 ? "+" : "") + v + STAT_UNIT[i];
}""")
M(rl, """
public static @MSG@ baseLine(String label, String base, String bon, String bc) {
  @MSG@ m = @MSG@.empty();
  m.insert(@MSG@.raw(label + ": ").color("#AAAAAA"));
  m.insert(@MSG@.raw(base).color("#FFFFFF"));
  m.insert(@MSG@.raw(" (" + bon + ")").color(bc));
  return m;
}""")
# what the base values were when the tooltip was written (part of sig: a game update that changes a weapon's damage re-writes it)
M(rl, """
public static String baseSig(@IS@ it) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < STAT_KEY.length; i++) {
    String b = baseText(it, STAT_BASE[i]);
    if (b != null) sb.append(STAT_KEY[i]).append('=').append(b).append(';');
  }
  return sb.toString();
}""")
# plain-text stat lines (the /reforge page and the /rolls chat line); d == null = an item that was never rolled
M(rl, """
public static String[] statLines(@IS@ it, @BD@ d) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (d != null) {
    out.add("Reforge: " + str(d, "reforge"));
    for (int i = 0; i < STAT_KEY.length; i++) {
      if (!hasStat(d, i)) continue;
      String b = baseText(it, STAT_BASE[i]);
      out.add(STAT_LABEL[i] + ": " + (b != null ? b + " (" + bonus(d, i) + ")" : bonus(d, i)));
    }
    out.add("Roll Quality: " + num(d, "quality") + "%");
  } else {
    StringBuilder names = new StringBuilder();
    for (int i = 0; i < STAT_KEY.length; i++) {
      String b = baseText(it, STAT_BASE[i]);
      if (b != null) out.add(STAT_LABEL[i] + ": " + b);
      if (names.length() > 0) names.append(i == STAT_KEY.length - 1 ? " and " : ", ");
      names.append(STAT_LABEL[i]);
    }
    out.add("Not reforged yet - a reforge rolls " + names.toString() + " bonuses.");
  }
  String[] arr = new String[out.size()];
  for (int i = 0; i < arr.length; i++) arr[i] = (String) out.get(i);
  return arr;
}""")
# one-line roll summary (the page's "Before:" line and the reforge log line)
M(rl, """
public static String summary(@BD@ d) {
  if (d == null) return "not reforged";
  StringBuilder sb = new StringBuilder(str(d, "reforge"));
  for (int i = 0; i < STAT_KEY.length; i++) {
    if (!hasStat(d, i)) continue;
    sb.append("   ").append(STAT_LABEL[i]).append(' ').append(bonus(d, i));
  }
  sb.append("   Quality ").append(num(d, "quality")).append('%');
  return sb.toString();
}""")
# Description: the vanilla description (only when the item has one - otherwise the client would print the raw key), a blank line,
# then the Reforge line, one line per rolled stat from the STATS table - "Label: <base> (<roll>)" when the stat has a base value,
# "Label: <roll>" otherwise - and Roll Quality. Same shape as SimpleEnchantments composeDescription (base + "\n" + coloured raw lines).
M(rl, """
public static @MSG@ descMsg(@IS@ it, @BD@ d, String col) {
  @MSG@ m = @MSG@.empty();
  try {
    @ITM@ item = it.getItem();
    if (item != null && tr(item.getDescriptionTranslationKey()) != null) {
      m.insert(item.getDescriptionTranslationMessage());
      m.insert(@MSG@.raw("\\n\\n"));
    }
  } catch (Throwable t) { }
  m.insert(statLine("Reforge", str(d, "reforge"), col));
  for (int i = 0; i < STAT_KEY.length; i++) {
    if (!hasStat(d, i)) continue;
    int v = num(d, STAT_KEY[i]);
    String bc = v > 0 ? "#55FF55" : "#AAAAAA";
    String base = baseText(it, STAT_BASE[i]);
    m.insert(@MSG@.raw("\\n"));
    if (base != null) m.insert(baseLine(STAT_LABEL[i], base, bonus(d, i), bc));
    else m.insert(statLine(STAT_LABEL[i], bonus(d, i), bc));
  }
  int vq = num(d, "quality");
  m.insert(@MSG@.raw("\\n"));
  m.insert(statLine("Roll Quality", vq + "%", qualityColor(vq)));
  return m;
}""")
rl.addMethod(CtNewMethod.make(f"""
public static String sig({IS} it, {BD} d) {{
  return VIEW_V + ":" + it.getItemId() + ":" + it.getQualityIndex() + ":" + Integer.toHexString(d.toJson().hashCode())
    + ":" + Integer.toHexString(baseSig(it).hashCode());
}}""", rl))
# fingerprint of the stack's CURRENT ItemDisplay, decoded and re-encoded through the engine codec (so a save round trip that only
# changes BSON number types is not a change); null = no ItemDisplay or one the codec cannot read
rl.addMethod(CtNewMethod.make(f"""
public static String dispHash({IS} s) {{
  try {{
    if (s == null || s.isEmpty()) return null;
    Object o = s.getFromMetadataOrNull({IDM}.KEYED_CODEC);
    if (o == null) return null;
    {BD} md = s.withMetadata({IDM}.KEYED_CODEC, o).getMetadata();
    {BV} v = md == null ? null : md.get({IDM}.KEY);
    if (v == null || !v.isDocument()) return null;
    return Integer.toHexString(v.asDocument().toJson().hashCode());
  }} catch (Throwable t) {{ return null; }}
}}""", rl))
# true when the ItemDisplay on the stack is still the one we wrote (our marker's "disp" fingerprint matches). False when another
# mod wrote or removed ItemDisplay after us (Aetherhaven, Tamework, Hexcode, MMOSkillTree, ScarVoicePhones, SimpleEnchantments and
# TheArmory all write it; none is enabled in the HUD mod world today).
rl.addMethod(CtNewMethod.make(f"""
public static boolean ours({IS} s, {BD} view) {{
  if (view == null) return false;
  {BV} h = view.get("disp");
  if (h == null || !h.isString()) return false;
  String now = dispHash(s);
  return now != null && now.equals(h.asString().getValue());
}}""", rl))
# true when the item's ItemDisplay was written by us from exactly these rolls AND nobody replaced it since (then nothing needs
# rewriting)
rl.addMethod(CtNewMethod.make(f"""
public static boolean upToDate({IS} it) {{
  if (it == null || it.isEmpty()) return false;
  {BD} md = it.getMetadata();
  if (md == null || !md.containsKey({IDM}.KEY)) return false;
  {BV} r = md.get("SkyyRolls");
  {BV} v = md.get(VIEW_KEY);
  if (r == null || !r.isDocument() || v == null || !v.isDocument()) return false;
  {BV} g = v.asDocument().get("sig");
  if (g == null || !g.isString() || !g.asString().getValue().equals(sig(it, r.asDocument()))) return false;
  return ours(it, v.asDocument());
}}""", rl))
# writes ItemDisplay {Name, Description} + our SkyyRollsView marker {v, sig, disp, prev?}. prev = the newest ItemDisplay that was
# not ours (the one before our first write, or one another mod wrote over ours since); /rolls clear puts it back.
# On any failure the stack is returned unchanged (the rolls are still in "SkyyRolls").
rl.addMethod(CtNewMethod.make(f"""
public static {IS} withDisplay({IS} s) {{
  try {{
    if (s == null || s.isEmpty()) return s;
    {BD} md = s.getMetadata();
    if (md == null) return s;
    {BV} v = md.get("SkyyRolls");
    if (v == null || !v.isDocument()) return s;
    {BD} d = v.asDocument();
    String col = rarityColor(s);
    {MSG} name = nameMsg(s, str(d, "reforge"), col);
    {MSG} desc = descMsg(s, d, col);
    {BV} old = md.get(VIEW_KEY);
    {BV} cur = md.get({IDM}.KEY);
    {BV} keep = null;
    if (old != null && old.isDocument() && ours(s, old.asDocument())) {{
      {BV} p = old.asDocument().get("prev");
      if (p != null && !p.isNull()) keep = p;
    }} else if (cur != null && !cur.isNull()) {{
      keep = cur;
      if (old != null && old.isDocument()) info("another mod replaced the rolls tooltip on " + s.getItemId() + " - writing the rolls tooltip again (their tooltip is kept for /rolls clear)");
    }}
    {IS} out = s.withMetadata({IDM}.KEYED_CODEC, new {IDM}(name, desc));
    {BD} view = new {BD}();
    view.append("v", new org.bson.BsonInt32(VIEW_V));
    view.append("sig", new org.bson.BsonString(sig(s, d)));
    String h = dispHash(out);
    if (h != null) view.append("disp", new org.bson.BsonString(h));
    if (keep != null) view.append("prev", keep);
    return out.withMetadata(VIEW_KEY, ({BV}) view);
  }} catch (Throwable t) {{
    warn("could not write the rolls tooltip for " + (s == null ? "null" : s.getItemId()) + ": " + t);
    return s;
  }}
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static {BD} roll() {{
  java.util.concurrent.ThreadLocalRandom r = java.util.concurrent.ThreadLocalRandom.current();
  {BD} d = new {BD}();
  d.append("reforge", new org.bson.BsonString(REFORGES[r.nextInt(REFORGES.length)]));
  for (int i = 0; i < STAT_KEY.length; i++) d.append(STAT_KEY[i], new org.bson.BsonInt32(r.nextInt(STAT_MAX[i] + 1)));   // 0.1.4: STATS table
  d.append("quality", new org.bson.BsonInt32(r.nextInt(101)));
  d.append("rolledAt", new org.bson.BsonInt64(System.currentTimeMillis()));
  return d;
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static {IS} applyRolls({IS} base) {{
  return withDisplay(base.withMetadata("SkyyRolls", ({BV}) roll()));
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String describe({IS} it) {{
  if (it == null || it.isEmpty()) return "no item in hand";
  {BD} md = it.getMetadata();
  if (md == null) return it.getItemId() + ": no metadata at all";
  {BV} v = md.get("SkyyRolls");
  if (v == null || !v.isDocument()) return it.getItemId() + ": no rolls (metadata keys: " + md.keySet() + ")";
  String[] ls = statLines(it, v.asDocument());   // 0.1.4: same lines as the tooltip / page (base value + (roll))
  StringBuilder sb = new StringBuilder(it.getItemId());
  for (int i = 0; i < ls.length; i++) sb.append("  ").append(ls[i]);
  sb.append(upToDate(it) ? "  [shown on the tooltip]" : "  [not on the tooltip]");
  return sb.toString();
}}""", rl))
# 0.1.2: item name -> real item id (or null + suggestions)
rl.addMethod(CtNewMethod.make(f"""
public static String resolve(String q, StringBuilder sugg) {{
  if (q == null) return null;
  String t = q.trim();
  if (t.length() == 0) return null;
  try {{ if ({ITM}.getAssetMap().getAsset(t) != null) return t; }} catch (Throwable e) {{ }}
  String norm = t.toLowerCase().replace(' ', '_');
  String[] words = t.toLowerCase().replace('_', ' ').trim().split(" ");
  java.util.ArrayList hits = new java.util.ArrayList();
  java.util.ArrayList good = new java.util.ArrayList();
  try {{
    java.util.Iterator it = {ITM}.getAssetMap().getAssetMap().keySet().iterator();
    while (it.hasNext()) {{
      String id = String.valueOf(it.next());
      if (id.length() == 0 || id.charAt(0) == '*') continue;
      String low = id.toLowerCase();
      if (low.equals(norm)) return id;
      boolean all = true;
      for (int i = 0; i < words.length; i++) {{ if (words[i].length() > 0 && low.indexOf(words[i]) < 0) {{ all = false; break; }} }}
      if (all) {{ hits.add(id); if (refuseId(id) == null) good.add(id); }}
    }}
  }} catch (Throwable e) {{ warn("item lookup failed: " + e); return null; }}
  if (hits.size() == 1) return (String) hits.get(0);
  if (good.size() == 1) return (String) good.get(0);
  java.util.ArrayList show = hits;
  if (good.size() > 0) show = good;
  java.util.Collections.sort(show);
  for (int i = 0; i < show.size() && i < 8; i++) {{ if (sugg.length() > 0) sugg.append(", "); sugg.append((String) show.get(i)); }}
  if (show.size() > 8) sugg.append(" ... (" + show.size() + " matches)");
  return null;
}}""", rl))
# The three actions, moved out of the 0.1 RollsCmd.execute unchanged so the subcommands, the variant and the
# legacy --action path all share them.
# 0.1.3: the hand = the same container + slot for reading AND writing (Inventory.getItemInHand() returns the TOOLS item while
# usingToolsItem, so writing the 0.1.2 way into the active hotbar slot could overwrite a different item)
rl.addMethod(CtNewMethod.make(f"""
public static {IC} handContainer({INV} inv) {{
  if (inv.usingToolsItem()) return inv.getTools();
  return inv.getHotbar();
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static short handSlot({INV} inv) {{
  if (inv.usingToolsItem()) return (short) inv.getActiveToolsSlot();
  return (short) inv.getActiveHotbarSlot();
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static {IS} hand({INV} inv) {{
  {IC} c = handContainer(inv);
  short s = handSlot(inv);
  if (c == null || s < 0 || s >= c.getCapacity()) return null;
  return c.getItemStack(s);
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static Object putHand({INV} inv, {IS} it) {{
  {IC} c = handContainer(inv);
  return c.setItemStackForSlot(handSlot(inv), it);
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String ok(Object tx) {{
  if (tx instanceof {TXN} && !(({TXN}) tx).succeeded()) return "  (the inventory REFUSED the change)";
  return "";
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static boolean needsDisplay({IS} it) {{
  return it != null && !it.isEmpty() && refuse(it) == null && hasRolls(it) && !upToDate(it);
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static int refreshContainer({IC} c) {{
  int n = 0;
  try {{
    if (c == null) return 0;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {{
      {IS} it = c.getItemStack((short) i);
      if (!needsDisplay(it)) continue;
      {IS} nu = withDisplay(it);
      if (nu == it) continue;
      c.setItemStackForSlot((short) i, nu);
      n++;
    }}
  }} catch (Throwable t) {{ warn("tooltip refresh of a container failed: " + t); }}
  return n;
}}""", rl))
# rolled items from before 0.1.3 (or an older display version) in every player section get their tooltip; up-to-date items are
# only read. World thread only (RollsRefreshTask / commands).
rl.addMethod(CtNewMethod.make(f"""
public static int refreshInventory({INV} inv) {{
  if (inv == null) return 0;
  int n = 0;
  n += refreshContainer(inv.getHotbar());
  n += refreshContainer(inv.getStorage());
  n += refreshContainer(inv.getBackpack());
  n += refreshContainer(inv.getArmor());
  n += refreshContainer(inv.getUtility());
  n += refreshContainer(inv.getTools());
  return n;
}}""", rl))
# /rolls clear: drop SkyyRolls + our marker + our ItemDisplay (or restore the ItemDisplay that was there before us); an ItemDisplay
# another mod wrote after us is left alone; everything else stays - withMetadata(BsonDocument) keeps itemId, quantity, durability,
# maxDurability and qualityIndex (bytecode)
rl.addMethod(CtNewMethod.make(f"""
public static {IS} cleared({IS} it) {{
  {BD} md = it.getMetadata();
  if (md == null) return it;
  {BD} c = ({BD}) md.clone();
  c.remove("SkyyRolls");
  {BV} view = ({BV}) c.remove(VIEW_KEY);
  if (view != null && view.isDocument() && ours(it, view.asDocument())) {{
    {BV} prev = view.asDocument().get("prev");
    if (prev != null && !prev.isNull()) c.append({IDM}.KEY, prev);
    else c.remove({IDM}.KEY);
  }}
  if (c.isEmpty()) return it.withMetadata(({BD}) null);
  return it.withMetadata(c);
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String rollsJson({IS} it) {{
  {BD} md = it == null ? null : it.getMetadata();
  {BV} v = md == null ? null : md.get("SkyyRolls");
  return v == null || !v.isDocument() ? "none" : v.asDocument().toJson();
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static void give({PR} pr, {INV} inv, String q) {{
  StringBuilder sugg = new StringBuilder();
  String id = resolve(q, sugg);
  if (id == null) {{
    pr.sendMessage({MSG}.raw("[Rolls] no item matches '" + q + "'" + (sugg.length() > 0 ? ". Did you mean: " + sugg : " - use an item id like Weapon_Shortbow_Mithril")));
    return;
  }}
  String why = refuseId(id);
  if (why != null) {{ pr.sendMessage({MSG}.raw("[Rolls] not given: " + why)); return; }}
  {IS} it = applyRolls(new {IS}(id, 1));
  Object tx = inv.getStorage().addItemStack(it);
  pr.sendMessage({MSG}.raw("[Rolls] gave (into your inventory storage): " + describe(it) + ok(tx)));
  pr.sendMessage({MSG}.raw("[Rolls] raw SkyyRolls: " + rollsJson(it)));
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static void reroll({PR} pr, {INV} inv) {{
  {IS} hand = hand(inv);
  String why = refuse(hand);
  if (why != null) {{
    pr.sendMessage({MSG}.raw("[Rolls] not rerolled: " + why + (hasRolls(hand) ? ". It still carries old rolls - /rolls clear removes them" : "")));
    return;
  }}
  {IS} fresh = applyRolls(hand);
  Object tx = putHand(inv, fresh);
  pr.sendMessage({MSG}.raw("[Rolls] rerolled: " + describe(fresh) + ok(tx)));
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static void read({PR} pr, {INV} inv) {{
  {IS} hand = hand(inv);
  if (needsDisplay(hand)) {{
    {IS} nu = withDisplay(hand);
    if (nu != hand) {{
      Object tx = putHand(inv, nu);
      hand = nu;
      pr.sendMessage({MSG}.raw("[Rolls] tooltip updated - the item now shows its rolls" + ok(tx)));
    }}
  }}
  pr.sendMessage({MSG}.raw("[Rolls] " + describe(hand)));
  if (hasRolls(hand) && refuse(hand) != null) pr.sendMessage({MSG}.raw("[Rolls] " + refuse(hand) + " - /rolls clear removes these rolls"));
  if (hand != null && !hand.isEmpty()) pr.sendMessage({MSG}.raw("[Rolls] raw: " + (hand.getMetadata() == null ? "null" : hand.getMetadata().toJson())));
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static void clear({PR} pr, {INV} inv) {{
  {IS} hand = hand(inv);
  if (hand == null || hand.isEmpty()) {{ pr.sendMessage({MSG}.raw("[Rolls] hold the item you want to clear first")); return; }}
  {BD} md = hand.getMetadata();
  if (md == null || (!md.containsKey("SkyyRolls") && !md.containsKey(VIEW_KEY))) {{
    pr.sendMessage({MSG}.raw("[Rolls] " + hand.getItemId() + " has no rolls - nothing to clear"));
    return;
  }}
  {IS} nu = cleared(hand);
  Object tx = putHand(inv, nu);
  {BD} after = nu.getMetadata();
  pr.sendMessage({MSG}.raw("[Rolls] cleared the rolls from " + nu.getItemId() + " x" + nu.getQuantity() + " (durability " + nu.getDurability() + "/" + nu.getMaxDurability()
    + ", other metadata kept: " + (after == null ? "none" : String.valueOf(after.keySet())) + ")" + ok(tx)));
}}""", rl))
# action: "give" | "reroll" | "clear" | anything else = read (same fallback as 0.1). id is only used by give.
rl.addMethod(CtNewMethod.make(f"""
public static void run({ST} store, {REF} ref, {PR} pr, String action, String id) {{
  try {{
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p == null || p.getInventory() == null) {{ pr.sendMessage({MSG}.raw("[Rolls] no player inventory")); return; }}
    {INV} inv = p.getInventory();
    if (action.equals("give")) {{ give(pr, inv, id); return; }}
    if (action.equals("reroll")) {{ reroll(pr, inv); return; }}
    if (action.equals("clear")) {{ clear(pr, inv); return; }}
    read(pr, inv);
  }} catch (Throwable t) {{
    warn("/rolls failed: " + t);
    pr.sendMessage({MSG}.raw("[Rolls] error: " + t));
  }}
}}""", rl))


# ================= 0.1.4 Reforge: costs config, coins bridge, gear scan (static; world thread except load at setup) =================
F(rfg, "public static volatile java.nio.file.Path FILE;")
F(rfg, "public static volatile java.util.HashMap COSTS = new java.util.HashMap();")
F(rfg, "public static volatile long MTIME = -1L;")
# Hypixel SkyBlock reforge-anvil ladder by rarity; every other quality id (Tool, Technical, Developer, ...) pays cost.default
F(rfg, 'public static final String[] QIDS = new String[] { "Junk", "Common", "Uncommon", "Rare", "Epic", "Legendary" };')
F(rfg, "public static final long[] QDEF = new long[] { 100L, 250L, 500L, 1000L, 2500L, 5000L };")
F(rfg, "public static final long DEF_OTHER = 1000L;")
# inventory sections: 0 hotbar, 1 storage, 2 backpack, 3 armor, 4 utility, 5 tools; listed hotbar, armor, tools, utility, storage, backpack
F(rfg, "public static final int[] SCAN = new int[] { 0, 3, 5, 4, 1, 2 };")
F(rfg, 'public static final String[] SEC_NAME = new String[] { "Hotbar", "Inventory", "Backpack", "Armor", "Utility", "Tools" };')
M(rfg, """
public static String defaultsText() {
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyRolls - Reforge Anvil (/reforge) cost in coins, by the item's quality (rarity) id.\\n");
  sb.append("# Coins are taken through SkyyCoins before the reroll and refunded if the reroll fails. 0 = free.\\n");
  sb.append("# Quality ids = Server/Item/Qualities (Junk, Common, Uncommon, Rare, Epic, Legendary; mods can add more).\\n");
  sb.append("# cost.default is used for every other quality (Tool, Technical, ...).\\n");
  sb.append("# This file is re-read automatically when it changes (checked every time someone opens /reforge).\\n");
  for (int i = 0; i < QIDS.length; i++) sb.append("cost." + QIDS[i] + "=" + QDEF[i] + "\\n");
  sb.append("cost.default=" + DEF_OTHER + "\\n");
  return sb.toString();
}""")
# First-run default file, crash-safe (SkyyCoins 0.1.5 saveK / SkyyProfiles pattern): write reforge.properties.tmp, then move it
# into place, retried 5 x 20 ms on a FileSystemException (Windows sharing violation from a scanner / indexer). A crash mid-write
# leaves only the .tmp, never a half-written reforge.properties (a truncated "cost.Legendary=50" would be a valid, wrong price);
# the next start simply writes it again. No REPLACE_EXISTING: a file that appeared meanwhile (an admin's own) is never overwritten.
M(rfg, """
public static void writeDefaults(java.nio.file.Path dst) throws Exception {
  java.nio.file.Files.createDirectories(dst.getParent(), new java.nio.file.attribute.FileAttribute[0]);
  java.nio.file.Path tmp = dst.resolveSibling(dst.getFileName().toString() + ".tmp");
  java.nio.file.Files.write(tmp, defaultsText().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
  Throwable last = null;
  int i = 0;
  while (i < 5) {
    try {
      java.nio.file.Files.move(tmp, dst, new java.nio.file.CopyOption[0]);
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
  throw new java.io.IOException("could not create " + dst + ": " + last);
}""")
M(rfg, """
public static synchronized void load() {
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < QIDS.length; i++) m.put(QIDS[i].toLowerCase(), Long.valueOf(QDEF[i]));
  m.put("default", Long.valueOf(DEF_OTHER));
  try {
    if (FILE != null) {
      if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) writeDefaults(FILE);
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
      try { p.load(in); } finally { in.close(); }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String k = (String) it.next();
        if (!k.startsWith("cost.")) continue;
        try {
          long v = Long.parseLong(p.getProperty(k).trim().replace(",", "").replace(" ", ""));
          if (v < 0L) v = 0L;
          if (v > 1000000000000L) v = 1000000000000L;
          m.put(k.substring(5).trim().toLowerCase(), Long.valueOf(v));
        } catch (Throwable e) { @PKG@.Rolls.warn("reforge.properties: " + k + " is not a whole number - the default is used"); }
      }
      MTIME = java.nio.file.Files.getLastModifiedTime(FILE, new java.nio.file.LinkOption[0]).toMillis();
    }
  } catch (Throwable t) { @PKG@.Rolls.warn("could not read reforge.properties - the default costs are used: " + t); }
  COSTS = m;
}""")
M(rfg, """
public static void maybeReload() {
  try {
    java.nio.file.Path f = FILE;
    if (f == null) return;
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { load(); return; }
    long t = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis();
    if (t != MTIME) { load(); @PKG@.Rolls.info("reforge.properties changed - reforge costs re-read"); }
  } catch (Throwable e) { }
}""")
M(rfg, """
public static String qualityId(@IS@ it) {
  try {
    Object q = @IQ@.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof @IQ@) { String id = ((@IQ@) q).getId(); if (id != null) return id; }
  } catch (Throwable t) { }
  return "";
}""")
M(rfg, """
public static String qualityName(@IS@ it) {
  try {
    Object q = @IQ@.getAssetMap().getAsset(it.getQualityIndex());
    if (q instanceof @IQ@) {
      String n = @PKG@.Rolls.tr(((@IQ@) q).getLocalizationKey());
      if (n != null) return n;
      String id = ((@IQ@) q).getId();
      if (id != null) return id;
    }
  } catch (Throwable t) { }
  return "Common";
}""")
M(rfg, """
public static String qcolor(String qid) {
  try {
    int ix = @IQ@.getAssetMap().getIndex(qid);
    Object q = @IQ@.getAssetMap().getAsset(ix);
    if (q instanceof @IQ@) { String h = @PKG@.Rolls.hex(((@IQ@) q).getTextColor()); if (h != null) return h; }
  } catch (Throwable t) { }
  return "#c9d2dd";
}""")
M(rfg, """
public static long costOf(String qid) {
  java.util.HashMap m = COSTS;
  Object v = qid == null ? null : m.get(qid.toLowerCase());
  if (v == null) v = m.get("default");
  return v instanceof Long ? ((Long) v).longValue() : DEF_OTHER;
}""")
M(rfg, """
public static long cost(@IS@ it) {
  return costOf(qualityId(it));
}""")
M(rfg, """
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
M(rfg, """
public static Object bridgeGet(String k) {
  try {
    Object b = System.getProperties().get("skyy.bridge");
    if (b instanceof java.util.Map) return ((java.util.Map) b).get(k);
  } catch (Throwable t) { }
  return null;
}""")
# SkyyCoins 0.1.5 bridge (build_skyycoins_0.1.5.py docstring): coins:fn:get apply(UUID) -> Long; coins:fn:take
# apply(Object[]{UUID, Long}) -> Boolean (false = not enough, nothing taken); coins:fn:add apply(Object[]{UUID, Long}) -> Long.
# All three act on the ACTIVE profile and return null while that profile's balance file cannot be read (frozen key).
M(rfg, """
public static long purse(java.util.UUID u) {
  try {
    Object f = bridgeGet("coins:fn:get");
    if (!(f instanceof java.util.function.Function)) return -1L;
    Object r = ((java.util.function.Function) f).apply(u);
    if (r instanceof Number) return ((Number) r).longValue();
  } catch (Throwable t) { @PKG@.Rolls.warn("coins:fn:get failed: " + t); }
  return -1L;
}""")
# 1 = taken, 0 = not enough coins (nothing taken), -1 = coins unavailable (no SkyyCoins, unreadable balance, error)
M(rfg, """
public static int take(java.util.UUID u, long amt) {
  try {
    Object f = bridgeGet("coins:fn:take");
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(amt) });
    if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  } catch (Throwable t) { @PKG@.Rolls.warn("coins:fn:take failed: " + t); }
  return -1;
}""")
M(rfg, """
public static boolean refund(java.util.UUID u, long amt) {
  try {
    Object f = bridgeGet("coins:fn:add");
    if (!(f instanceof java.util.function.Function)) return false;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, Long.valueOf(amt) });
    return r instanceof Number;
  } catch (Throwable t) { @PKG@.Rolls.warn("coins:fn:add (refund) failed: " + t); }
  return false;
}""")
M(rfg, """
public static String epoch(java.util.UUID u) {
  Object e = bridgeGet("profile:epoch:" + u);
  return e == null ? "" : String.valueOf(e);
}""")
M(rfg, """
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
M(rfg, """
public static @IS@ at(@INV@ inv, int s, int slot) {
  @IC@ c = section(inv, s);
  if (c == null || slot < 0 || slot >= c.getCapacity()) return null;
  return c.getItemStack((short) slot);
}""")
# what must still be in the slot for a reforge click to go through: the same item id AND the same rolls
M(rfg, """
public static String fp(@IS@ it) {
  if (it == null || it.isEmpty()) return "";
  return it.getItemId() + "|" + @PKG@.Rolls.rollsJson(it);
}""")
M(rfg, """
public static boolean same(@IS@ it, String id, String f) {
  if (it == null || it.isEmpty() || id == null || f == null) return false;
  return id.equals(it.getItemId()) && f.equals(fp(it));
}""")
M(rfg, """
public static java.util.ArrayList gear(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < SCAN.length; k++) {
    @IC@ c = section(inv, SCAN[k]);
    if (c == null) continue;
    int cap = c.getCapacity();
    for (int i = 0; i < cap; i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || @PKG@.Rolls.refuse(it) != null) continue;
      out.add(new int[] { SCAN[k], i });
    }
  }
  return out;
}""")
M(rfg, """
public static String where(int s, int slot) {
  if (s < 0 || s >= SEC_NAME.length) return "inventory";
  return SEC_NAME[s] + " " + (slot + 1);
}""")
M(rfg, """
public static String pretty(String id) {
  if (id == null) return "?";
  String s = id;
  if (s.startsWith("Weapon_")) s = s.substring(7);
  else if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Tool_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
M(rfg, """
public static String itemName(@IS@ it) {
  String n = null;
  try { n = @PKG@.Rolls.tr(it.getItem().getTranslationKey()); } catch (Throwable t) { n = null; }
  if (n != null && n.indexOf(123) < 0) return n;
  return pretty(it == null ? null : it.getItemId());
}""")
M(rfg, """
public static String displayName(@IS@ it, @BD@ d) {
  return (d != null ? @PKG@.Rolls.str(d, "reforge") + " " : "") + itemName(it);
}""")

# ================= 0.1.4 ReforgePage (inline, rebuilt only after a click) =================
for f in ("public java.util.ArrayList rows;", "public int pageNo;", "public int selSec;", "public int selSlot;", "public String selId;",
          "public String selFp;", "public String info;", "public String before;", "public boolean fresh;", "public String epoch;",
          "public long lastForge;"):
    F(rpg, f)
C(rpg, """
public ReforgePage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.rows = new java.util.ArrayList();
  this.pageNo = 0;
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null;
  this.info = ""; this.before = null; this.fresh = false; this.lastForge = 0L;
  this.epoch = @PKG@.Reforge.epoch(pr.getUuid());
}""")
M(rpg, r"""
public static String safe(String t) {
  if (t == null) return "";
  return t.replace(':', ' ').replace(';', ' ').replace(',', ' ').replace('{', '(').replace('}', ')').replace('"', ' ').replace('\\', ' ');
}""")
M(rpg, """
public static String style(String bg, String hov, String press, String fg, int fs) {
  String ls = "LabelStyle: (FontSize: " + fs + ", TextColor: " + fg + ", RenderBold: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  return "Style: TextButtonStyle(Default: (Background: " + bg + ", " + ls + "), Hovered: (Background: " + hov + ", " + ls + "), Pressed: (Background: " + press + ", " + ls + "));";
}""")
# one string value out of the page event JSON (SkyySacks 0.7.3 CraftPage.jsonStr / SkyyGuilds 0.1 GuildPage.jsonStr)
M(rpg, """
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
# info line: "+" good (green), "-" refused / failed (orange), "=" neutral
M(rpg, """
public static String colorOf(String res) {
  if (res == null || res.length() == 0) return "#cfe3ff";
  char c = res.charAt(0);
  if (c == '+') return "#8fe39a";
  if (c == '-') return "#ff9d6b";
  return "#cfe3ff";
}""")
M(rpg, """
public static String textOf(String res) {
  if (res == null) return "";
  if (res.length() > 0 && (res.charAt(0) == '+' || res.charAt(0) == '-' || res.charAt(0) == '=')) return res.substring(1);
  return res;
}""")
M(rpg, """
public void clearSel() {
  this.selSec = -1; this.selSlot = -1; this.selId = null; this.selFp = null; this.before = null; this.fresh = false;
}""")
# Re-picking the item that is ALREADY on the anvil (its "On the anvil" button stays clickable) changes nothing: same slot, same
# fingerprint (item id + rolls, selFp is updated after every reforge) and same profile epoch -> keep before / fresh / info, so the
# last reforge's "New roll" + "Before:" lines do not vanish. Any other pick (other slot, changed item, other profile) resets them.
M(rpg, """
public boolean pick(@INV@ inv, int s, int slot) {
  @IS@ it = @PKG@.Reforge.at(inv, s, slot);
  if (it == null || it.isEmpty() || @PKG@.Rolls.refuse(it) != null) return false;
  String ep = @PKG@.Reforge.epoch(this.playerRef.getUuid());
  String f = @PKG@.Reforge.fp(it);
  if (s == this.selSec && slot == this.selSlot && f.equals(this.selFp) && ep.equals(this.epoch)) return true;
  this.selSec = s; this.selSlot = slot; this.selId = it.getItemId(); this.selFp = f;
  this.before = null; this.fresh = false;
  this.epoch = ep;
  this.info = "=" + @PKG@.Reforge.itemName(it) + " is on the anvil. Click Reforge to reroll it.";
  return true;
}""")
# /reforge with a rollable item in hand puts it on the anvil (hand = tools section while usingToolsItem, else the active hotbar slot)
M(rpg, """
public void preselect(@INV@ inv) {
  try {
    if (inv == null) return;
    if (inv.usingToolsItem()) pick(inv, 5, (int) inv.getActiveToolsSlot());
    else pick(inv, 0, (int) inv.getActiveHotbarSlot());
  } catch (Throwable t) { }
}""")
M(rpg, """
public void anvil(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel) {
  String gs = style("#1f5a34", "#2c7a48", "#133a22", "#e6ffe8", 22);
  String rs = style("#5a2424", "#7a3030", "#3a1414", "#ffe6e6", 22);
  b.appendInline("#SkyyRfMain", "Group #SkyyRfAnvil { Anchor: (Width: 580, Height: 620); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 10); Background: #142030(0.92); }");
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 34); Text: \\"Anvil\\"; Style: (FontSize: 21, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfAnvil", "Group #SkyyRfSel { Anchor: (Height: 122); LayoutMode: Left; }");
  b.appendInline("#SkyyRfSel", "Group #SkyyRfSlot { Anchor: (Width: 120, Height: 118); Background: #0b1524(0.95); }");
  if (sel != null) b.appendInline("#SkyyRfSlot", "ItemIcon { Anchor: (Width: 100, Height: 100, Left: 10, Top: 9); ItemId: \\"" + safe(sel.getItemId()) + "\\"; }");
  else b.appendInline("#SkyyRfSlot", "Label { Anchor: (Full: 0); Text: \\"?\\"; Style: (FontSize: 48, RenderBold: true, TextColor: #3a4a60, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfSel", "Label { Anchor: (Width: 16, Height: 118); Text: \\"\\"; }");
  b.appendInline("#SkyyRfSel", "Group #SkyyRfSelTxt { Anchor: (Width: 412, Height: 118); LayoutMode: Top; }");
  String col = sel == null ? "#9fb8d0" : @PKG@.Rolls.rarityColor(sel);
  b.appendInline("#SkyyRfSelTxt", "Label #SkyyRfName { Anchor: (Height: 46); Text: \\"\\"; Style: (FontSize: 22, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfSelTxt", "Label #SkyyRfRar { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
  b.appendInline("#SkyyRfSelTxt", "Label #SkyyRfWhere { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
  if (sel == null) {
    b.set("#SkyyRfName.Text", "The anvil is empty");
    b.set("#SkyyRfRar.Text", "Pick an item from Your gear");
    b.set("#SkyyRfWhere.Text", "It stays in its own slot while you reforge it.");
    b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 16); Text: \\"\\"; }");
    b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 32); Text: \\"Reforge cost by rarity\\"; Style: (FontSize: 18, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
    int n = 0;
    for (int i = 0; i < @PKG@.Reforge.QIDS.length; i++) {
      String q = @PKG@.Reforge.QIDS[i];
      b.appendInline("#SkyyRfAnvil", "Label #SkyyRfCost" + n + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + @PKG@.Reforge.qcolor(q) + ", VerticalAlignment: Center); }");
      b.set("#SkyyRfCost" + n + ".Text", q + ": " + @PKG@.Reforge.fmt(@PKG@.Reforge.costOf(q)) + " coins");
      n++;
    }
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfCost" + n + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 16, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfCost" + n + ".Text", "Other items: " + @PKG@.Reforge.fmt(@PKG@.Reforge.costOf("default")) + " coins");
    b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 14); Text: \\"\\"; }");
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfHow1 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfHow1.Text", "A reforge rerolls the reforge name and every stat of the item.");
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfHow2 { Anchor: (Height: 26); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfHow2.Text", "Tip: hold the item when you type /reforge to put it on the anvil.");
    return;
  }
  @BD@ d = @PKG@.Rolls.rollsDoc(sel);
  b.set("#SkyyRfName.Text", @PKG@.Reforge.displayName(sel, d));
  b.set("#SkyyRfRar.Text", @PKG@.Reforge.qualityName(sel).toUpperCase() + (sel.getQuantity() > 1 ? "   x" + sel.getQuantity() : ""));
  b.set("#SkyyRfWhere.Text", "In your " + @PKG@.Reforge.where(this.selSec, this.selSlot) + " - it stays there while you reforge it.");
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 10); Text: \\"\\"; }");
  b.appendInline("#SkyyRfAnvil", "Label #SkyyRfStHdr { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + (this.fresh ? "#8fe39a" : "#e6f2ff") + ", VerticalAlignment: Center); }");
  b.set("#SkyyRfStHdr.Text", this.fresh ? "New roll" : (d == null ? "Not reforged yet" : "Current roll"));
  String[] lines = @PKG@.Rolls.statLines(sel, d);
  for (int i = 0; i < lines.length && i < 8; i++) {
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfSt" + i + " { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 18, TextColor: " + (this.fresh ? "#c8ffd0" : "#dfe8f2") + ", VerticalAlignment: Center); }");
    b.set("#SkyyRfSt" + i + ".Text", lines[i]);
  }
  if (this.before != null) {
    b.appendInline("#SkyyRfAnvil", "Label #SkyyRfBefore { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 14, TextColor: #8a9bb0, VerticalAlignment: Center); }");
    b.set("#SkyyRfBefore.Text", "Before: " + this.before);
  }
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 12); Text: \\"\\"; }");
  long cost = @PKG@.Reforge.cost(sel);
  long have = @PKG@.Reforge.purse(u);
  b.appendInline("#SkyyRfAnvil", "Label #SkyyRfCostTxt { Anchor: (Height: 32); Text: \\"\\"; Style: (FontSize: 19, RenderBold: true, TextColor: #ffd070, VerticalAlignment: Center); }");
  b.set("#SkyyRfCostTxt.Text", cost > 0L ? "Cost: " + @PKG@.Reforge.fmt(cost) + " coins (" + @PKG@.Reforge.qualityName(sel) + ")" : "Cost: free");
  b.appendInline("#SkyyRfAnvil", "Label #SkyyRfPurse { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #cfe3ff, VerticalAlignment: Center); }");
  b.set("#SkyyRfPurse.Text", have >= 0L ? "Your purse: " + @PKG@.Reforge.fmt(have) + " coins" : "Your purse: unavailable (SkyyCoins)");
  b.appendInline("#SkyyRfAnvil", "Label { Anchor: (Height: 8); Text: \\"\\"; }");
  boolean poor = cost > 0L && have >= 0L && have < cost;
  String bt = poor ? "Not enough coins" : (cost > 0L ? "Reforge (" + cost + " coins)" : "Reforge");
  b.appendInline("#SkyyRfAnvil", "Group #SkyyRfGo { Anchor: (Height: 60); LayoutMode: Left; }");
  b.appendInline("#SkyyRfGo", "Label { Anchor: (Width: 94, Height: 56); Text: \\"\\"; }");
  b.appendInline("#SkyyRfGo", "TextButton #SkyyRfForge { Anchor: (Width: 360, Height: 56); Text: \\"" + safe(bt) + "\\"; " + (poor ? rs : gs) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyRfForge", @EVD@.of("a", "reforge"));
}""")
M(rpg, """
public void gearList(@UCB@ b, @UEB@ ev, @INV@ inv) {
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  String ss = style("#6e5a1c", "#8a7224", "#4a3c10", "#fff0c8", 16);
  b.appendInline("#SkyyRfMain", "Group #SkyyRfList { Anchor: (Width: 596, Height: 620); LayoutMode: Top; Padding: (Horizontal: 16, Vertical: 10); Background: #142030(0.92); }");
  b.appendInline("#SkyyRfList", "Label #SkyyRfGearHdr { Anchor: (Height: 34); Text: \\"\\"; Style: (FontSize: 21, RenderBold: true, TextColor: #e6f2ff, VerticalAlignment: Center); }");
  b.set("#SkyyRfGearHdr.Text", "Your gear (" + this.rows.size() + ")");
  int per = 9;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyRfList", "Label #SkyyRfEmpty1 { Anchor: (Height: 40); Text: \\"\\"; Style: (FontSize: 17, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyRfEmpty1.Text", "No weapons, armor or tools on you.");
    b.appendInline("#SkyyRfList", "Label #SkyyRfEmpty2 { Anchor: (Height: 30); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyRfEmpty2.Text", "Carry one (hotbar, inventory, backpack or worn) and click Refresh.");
  }
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] r = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.Reforge.at(inv, r[0], r[1]);
    if (it == null || it.isEmpty()) continue;
    int idx = i - start;
    boolean on = r[0] == this.selSec && r[1] == this.selSlot;
    String rid = "#SkyyRfRow" + idx;
    @BD@ d = @PKG@.Rolls.rollsDoc(it);
    String col = @PKG@.Rolls.rarityColor(it);
    b.appendInline("#SkyyRfList", "Group #SkyyRfRow" + idx + " { Anchor: (Height: 52); LayoutMode: Left; Padding: (Top: 4); Background: " + (on ? "#2c3a1e(0.95)" : "#0f1a2a(0.9)") + "; }");
    b.appendInline(rid, "Group { Anchor: (Width: 56, Height: 44); ItemIcon { Anchor: (Width: 40, Height: 40, Left: 8, Top: 2); ItemId: \\"" + safe(it.getItemId()) + "\\"; } }");
    b.appendInline(rid, "Group #SkyyRfRowTxt" + idx + " { Anchor: (Width: 334, Height: 44); LayoutMode: Top; }");
    b.appendInline("#SkyyRfRowTxt" + idx, "Label #SkyyRfRowName" + idx + " { Anchor: (Height: 24); Text: \\"\\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center); }");
    b.set("#SkyyRfRowName" + idx + ".Text", @PKG@.Reforge.displayName(it, d) + (it.getQuantity() > 1 ? "  x" + it.getQuantity() : ""));
    b.appendInline("#SkyyRfRowTxt" + idx, "Label #SkyyRfRowSub" + idx + " { Anchor: (Height: 20); Text: \\"\\"; Style: (FontSize: 13, TextColor: #9fb8d0, VerticalAlignment: Center); }");
    b.set("#SkyyRfRowSub" + idx + ".Text", @PKG@.Reforge.qualityName(it) + "  -  " + (d == null ? "not reforged" : "reforged: " + @PKG@.Rolls.str(d, "reforge")) + "  -  " + @PKG@.Reforge.where(r[0], r[1]));
    b.appendInline(rid, "Label { Anchor: (Width: 20, Height: 44); Text: \\"\\"; }");
    b.appendInline(rid, "TextButton #SkyyRfPick" + idx + " { Anchor: (Width: 150, Height: 42); Text: \\"" + (on ? "On the anvil" : "Select") + "\\"; " + (on ? ss : bs) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyRfPick" + idx, @EVD@.of("a", "sel:" + i));
    b.appendInline("#SkyyRfList", "Label { Anchor: (Height: 4); Text: \\"\\"; }");
  }
  if (pages > 1) {
    b.appendInline("#SkyyRfList", "Group #SkyyRfNav { Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyRfNav", "Label { Anchor: (Width: 92, Height: 34); Text: \\"\\"; }");
    b.appendInline("#SkyyRfNav", "TextButton #SkyyRfPrev { Anchor: (Width: 110, Height: 34); Text: \\"< Prev\\"; " + bs + " }");
    b.appendInline("#SkyyRfNav", "Label #SkyyRfPageTxt { Anchor: (Width: 150, Height: 34); Text: \\"\\"; Style: (FontSize: 15, TextColor: #9fb8d0, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyRfPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyRfNav", "TextButton #SkyyRfNext { Anchor: (Width: 110, Height: 34); Text: \\"Next >\\"; " + bs + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyRfPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyRfNext", @EVD@.of("a", "next"));
  }
}""")
M(rpg, """
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  @IS@ sel = null;
  if (this.selSec >= 0) {
    sel = @PKG@.Reforge.at(inv, this.selSec, this.selSlot);
    if (!@PKG@.Reforge.same(sel, this.selId, this.selFp)) {
      sel = null;
      clearSel();
      if (this.info == null || this.info.length() == 0 || this.info.charAt(0) != '-') this.info = "-The item on the anvil moved or changed - pick it again.";
    }
  }
  this.rows = @PKG@.Reforge.gear(inv);
  String bs = style("#1d3a5f", "#2f5a8f", "#0f2038", "#e6f2ff", 16);
  b.appendInline((String) null, "Group #SkyyRf { Anchor: (Width: 1240, Height: 860); Background: #0b1524(0.96); Padding: (Horizontal: 24, Vertical: 14); LayoutMode: Top; }");
  b.appendInline("#SkyyRf", "Group { Anchor: (Height: 3); Background: #ffd070; }");
  b.appendInline("#SkyyRf", "Label { Anchor: (Height: 50); Text: \\"Reforge Anvil\\"; Style: (FontSize: 30, RenderBold: true, TextColor: #ffe08a, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyyRf", "Label #SkyyRfSub { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #cfe3ff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyRfSub.Text", "Pick a weapon, armor piece or tool from Your gear. A reforge rerolls its reforge and stats for coins.");
  b.appendInline("#SkyyRf", "Label { Anchor: (Height: 8); Text: \\"\\"; }");
  b.appendInline("#SkyyRf", "Group #SkyyRfMain { Anchor: (Height: 620); LayoutMode: Left; }");
  anvil(b, ev, u, sel);
  b.appendInline("#SkyyRfMain", "Label { Anchor: (Width: 16, Height: 620); Text: \\"\\"; }");
  gearList(b, ev, inv);
  b.appendInline("#SkyyRf", "Label #SkyyRfInfo { Anchor: (Height: 36); Text: \\"\\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + colorOf(this.info) + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyRfInfo.Text", textOf(this.info));
  b.appendInline("#SkyyRf", "Group #SkyyRfBottom { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyRfBottom", "Label { Anchor: (Width: 526, Height: 40); Text: \\"\\"; }");
  b.appendInline("#SkyyRfBottom", "TextButton #SkyyRfRefresh { Anchor: (Width: 140, Height: 40); Text: \\"Refresh\\"; " + bs + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyRfRefresh", @EVD@.of("a", "refresh"));
}""")
# The reforge click. Order: guard -> profile:busy -> epoch -> same item still in the slot -> rollable -> one item -> cost -> coins
# TAKEN FIRST -> reroll + write the same slot -> on any failure REFUND. World thread (page events), same thread as SkyyCoins' callers.
M(rpg, """
public void forge(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastForge < 400L) return;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Rolls.busy(u)) { this.info = "-Your profile is still loading - nothing was reforged. Try again in a moment."; return; }
  if (this.selSec < 0) { this.info = "-Pick an item from Your gear first."; return; }
  String ep = @PKG@.Reforge.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.epoch = ep; this.info = "-Your profile changed - pick the item again."; return; }
  @IS@ it = @PKG@.Reforge.at(inv, this.selSec, this.selSlot);
  if (!@PKG@.Reforge.same(it, this.selId, this.selFp)) { clearSel(); this.info = "-That item moved or changed - pick it again."; return; }
  String why = @PKG@.Rolls.refuse(it);
  if (why != null) { this.info = "-" + why; return; }
  if (it.getQuantity() > 1) { this.info = "-A reforge works on one item at a time - split this stack of " + it.getQuantity() + " first."; return; }
  long cost = @PKG@.Reforge.cost(it);
  String name = @PKG@.Reforge.itemName(it);
  if (cost > 0L) {
    int t = @PKG@.Reforge.take(u, cost);
    if (t < 0) { this.info = "-Coins are not available right now (SkyyCoins missing or your balance cannot be read). Nothing was taken."; return; }
    if (t == 0) {
      long have = @PKG@.Reforge.purse(u);
      this.info = "-Not enough coins: this reforge costs " + @PKG@.Reforge.fmt(cost) + (have >= 0L ? " and you have " + @PKG@.Reforge.fmt(have) : "") + ".";
      return;
    }
  }
  @BD@ old = @PKG@.Rolls.rollsDoc(it);
  @IS@ nu = null;
  Object tx = null;
  Throwable err = null;
  try {
    nu = @PKG@.Rolls.applyRolls(it);
    tx = @PKG@.Reforge.section(inv, this.selSec).setItemStackForSlot((short) this.selSlot, nu);
  } catch (Throwable t) { err = t; }
  boolean ok = err == null && nu != null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded());
  if (!ok) {
    boolean back = cost <= 0L || @PKG@.Reforge.refund(u, cost);
    String what = err != null ? String.valueOf(err) : "the inventory refused the change";
    @PKG@.Rolls.warn("REFORGE FAILED for " + this.playerRef.getUsername() + " (" + u + ") on " + this.selId + ": " + what
      + (cost > 0L ? (back ? " - refunded " + cost + " coins" : " - REFUND FAILED, give back " + cost + " coins by hand") : ""));
    this.info = back ? "-The reforge failed and nothing changed" + (cost > 0L ? " - your " + @PKG@.Reforge.fmt(cost) + " coins were refunded." : ".")
      : "-The reforge failed and the refund did not go through - an admin can find it in the server log.";
    return;
  }
  this.lastForge = now;
  this.selFp = @PKG@.Reforge.fp(nu);
  this.before = @PKG@.Rolls.summary(old);
  this.fresh = true;
  @BD@ nd = @PKG@.Rolls.rollsDoc(nu);
  this.info = "+Reforged! Your " + name + " is now " + @PKG@.Rolls.str(nd, "reforge") + (cost > 0L ? " (-" + @PKG@.Reforge.fmt(cost) + " coins)." : ".");
  @PKG@.Rolls.info("reforge: " + this.playerRef.getUsername() + " " + this.selId + " [" + @PKG@.Rolls.summary(old) + "] -> [" + @PKG@.Rolls.summary(nd) + "] cost " + cost);
}""")
M(rpg, """
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = jsonStr(data, "a");
    if (a.length() == 0) return;
    if (a.equals("refresh")) { this.info = ""; rebuild(); return; }   // rescans Your gear; the anvil's last result stays (build() drops it if the item moved)
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
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
    if (a.equals("reforge")) { forge(inv); rebuild(); return; }
  } catch (Throwable t) { @PKG@.Rolls.warn("reforge page click failed: " + t); }
}""")

# ================= 0.1.4 /reforge (player command) =================
C(rfc, """
public ReforgeCmd() {
  super("reforge", "Open the Reforge Anvil: reroll the reforge and stats of a weapon, armor piece or tool for coins");
  setPermissionGroups(new String[] { "hytale:Adventurer" });   // COMMAND RULES: ordinary players lack the auto node
}""")
M(rfc, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    @PKG@.Reforge.maybeReload();
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Reforge] no player found")); return; }
    @PKG@.ReforgePage page = new @PKG@.ReforgePage(pr);
    page.preselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Rolls.warn("/reforge failed: " + t);
    pr.sendMessage(@MSG@.raw("[Reforge] could not open the Reforge Anvil - the server log has the details"));
  }
}""")

EXEC = f"protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{"

# ================= /rolls read =================
rdc.addConstructor(CtNewConstructor.make('public RollsReadCmd() { super("read", "Show the rolls on the item in your hand"); }', rdc))
rdc.addMethod(CtNewMethod.make(f"""
{EXEC}
  {PKG}.Rolls.run(store, ref, pr, "read", null);
}}""", rdc))

# ================= /rolls reroll =================
rrc.addConstructor(CtNewConstructor.make('public RollsRerollCmd() { super("reroll", "Re-roll the item in your hand (same slot)"); }', rrc))
rrc.addMethod(CtNewMethod.make(f"""
{EXEC}
  {PKG}.Rolls.run(store, ref, pr, "reroll", null);
}}""", rrc))

# ================= /rolls clear (0.1.3) =================
clc.addConstructor(CtNewConstructor.make('public RollsClearCmd() { super("clear", "Remove the rolls from the item in your hand (keeps the item, durability and other data)"); }', clc))
clc.addMethod(CtNewMethod.make(f"""
{EXEC}
  {PKG}.Rolls.run(store, ref, pr, "clear", null);
}}""", clc))

# ================= /rolls give <itemId>  (usage variant of give: description-only constructor) =================
gvc.addField(CtField.make(f"public {RA} itemArg;", gvc))
gvc.addConstructor(CtNewConstructor.make(f"""
public RollsGiveVariantCmd() {{
  super("Give this item with random rolls");
  this.itemArg = withRequiredArg("itemId", "Item id, e.g. Weapon_Longsword_Copper", {ATY}.STRING);
}}""", gvc))
gvc.addMethod(CtNewMethod.make(f"""
{EXEC}
  Object v = ctx.get(this.itemArg);
  String id = v == null ? "" : String.valueOf(v).trim();
  if (id.length() == 0) id = {PKG}.Rolls.DEFAULT_ITEM;
  {PKG}.Rolls.run(store, ref, pr, "give", id);
}}""", gvc))

# ================= /rolls give =================
gvr.addConstructor(CtNewConstructor.make(f"""
public RollsGiveCmd() {{
  super("give", "Give an item with random rolls: /rolls give [item name or id] (default Weapon_Longsword_Copper)");
  setAllowsExtraArguments(true);
}}""", gvr))
gvr.addMethod(CtNewMethod.make(f"""
{EXEC}
  String line = "";
  try {{ line = ctx.getInputString(); }} catch (Throwable t) {{ line = ""; }}
  if (line == null) line = "";
  String q = line.trim();
  String low = q.toLowerCase();
  int at = low.indexOf("give ");
  if (at >= 0) q = q.substring(at + 5).trim();
  else if (low.equals("give") || low.endsWith(" give")) q = "";
  if (q.length() == 0) q = {PKG}.Rolls.DEFAULT_ITEM;
  {PKG}.Rolls.run(store, ref, pr, "give", q);
}}""", gvr))

# ================= /rolls (root; alone = read; keeps the 0.1 --action/--item flags) =================
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addField(CtField.make(f"public {OA} itemArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public RollsCmd() {{
  super("rolls", "SkyyRolls spike (admin): /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear");
  this.actionArg = withOptionalArg("action", "old 0.1 form: give | read | reroll | clear", {ATY}.STRING);
  this.itemArg = withOptionalArg("item", "old 0.1 form: item id for give (default Weapon_Longsword_Copper)", {ATY}.STRING);
  addSubCommand(new {PKG}.RollsReadCmd());
  addSubCommand(new {PKG}.RollsRerollCmd());
  addSubCommand(new {PKG}.RollsGiveCmd());
  addSubCommand(new {PKG}.RollsClearCmd());
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
{EXEC}
  try {{
    String a = ctx.provided(this.actionArg) ? String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase() : "read";
    String id = ctx.provided(this.itemArg) ? String.valueOf(ctx.get(this.itemArg)).trim() : {PKG}.Rolls.DEFAULT_ITEM;
    {PKG}.Rolls.run(store, ref, pr, a, id);
  }} catch (Throwable t) {{
    {PKG}.Rolls.warn("/rolls failed: " + t);
    pr.sendMessage({MSG}.raw("[Rolls] error: " + t));
  }}
}}""", cmd))

# ================= join refresh (0.1.3): rolled items from before 0.1.3 get their tooltip =================
# PlayerReadyEvent (every world switch) -> 3 s later on the scheduler -> hop to the player's CURRENT world thread -> re-check the
# world there -> skip while SkyyProfiles' profile:busy:<uuid> is set (crash recovery reloads the inventory) -> Rolls.refreshInventory.
# Up to 15 tries, 2 s apart; giving up is logged with the last reason. Items that already show their rolls are only read.
rft.addInterface(pool.get("java.lang.Runnable"))
rft.addField(CtField.make(f"public {PR} pr;", rft))
rft.addField(CtField.make("public boolean onWorld;", rft))
rft.addField(CtField.make("public int tries;", rft))
rft.addField(CtField.make("public java.util.UUID hopWorld;", rft))
rft.addConstructor(CtNewConstructor.make(f"public RollsRefreshTask({PR} pr) {{ this.pr = pr; this.onWorld = false; this.tries = 0; this.hopWorld = null; }}", rft))
rft.addMethod(CtNewMethod.make(f"""
public void later(long ms) {{
  this.onWorld = false;
  {HSV}.SCHEDULED_EXECUTOR.schedule(this, ms, java.util.concurrent.TimeUnit.MILLISECONDS);
}}""", rft))
rft.addMethod(CtNewMethod.make(f"""
public void again(String why) {{
  this.tries = this.tries + 1;
  if (this.tries < 15) {{ later(2000L); return; }}
  String who = "?";
  try {{ who = this.pr.getUsername(); }} catch (Throwable t) {{ who = "?"; }}
  {PKG}.Rolls.warn("tooltip refresh gave up for " + who + " after " + this.tries + " tries (" + why + "); /rolls read on a held item or a relog tries again");
}}""", rft))
rft.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.pr == null || !this.pr.isValid()) return;
    if (!this.onWorld) {{
      java.util.UUID wu = this.pr.getWorldUuid();
      if (wu == null) {{ again("player is in no world"); return; }}
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) {{ again("world " + wu + " is not loaded"); return; }}
      this.onWorld = true;
      this.hopWorld = wu;
      w.execute(this);
      return;
    }}
    java.util.UUID now = this.pr.getWorldUuid();
    if (now == null || !now.equals(this.hopWorld)) {{ again("player changed world"); return; }}
    if ({PKG}.Rolls.busy(this.pr.getUuid())) {{ again("SkyyProfiles profile:busy is still set"); return; }}
    {REF} r = this.pr.getReference();
    if (r == null || !r.isValid()) {{ again("player entity not ready"); return; }}
    {ST} st = r.getStore();
    if (st == null) {{ again("player entity not ready"); return; }}
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null || p.getInventory() == null) {{ again("player inventory not ready"); return; }}
    int n = {PKG}.Rolls.refreshInventory(p.getInventory());
    if (n > 0) {PKG}.Rolls.info("tooltip refresh: " + n + " rolled item(s) of " + this.pr.getUsername() + " now show their rolls");
  }} catch (Throwable t) {{ {PKG}.Rolls.warn("tooltip refresh failed: " + t); }}
}}""", rft))

rdy.addInterface(pool.get("java.util.function.Consumer"))
rdy.addConstructor(CtNewConstructor.make("public RollsReady() { }", rdy))
rdy.addMethod(CtNewMethod.make(f"""
public void accept(Object ev) {{
  try {{
    {PRE} e = ({PRE}) ev;
    {REF} r = e.getPlayerRef();
    if (r == null) return;
    {ST} st = r.getStore();
    if (st == null) return;
    {PR} pr = ({PR}) st.getComponent(r, {PR}.getComponentType());
    if (pr == null) return;
    new {PKG}.RollsRefreshTask(pr).later(3000L);
  }} catch (Throwable t) {{ {PKG}.Rolls.warn("ready handler failed: " + t); }}
}}""", rdy))

# ================= plugin =================
pl.addConstructor(CtNewConstructor.make(f"public SkyyRollsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.Rolls.LOG = getLogger();
  // 0.1.4: stable data folder (HANDOFF: never the versioned default dir) + reforge costs
  {PKG}.Reforge.FILE = getDataDirectory().resolveSibling("Skyy_SkyyRolls").resolve("reforge.properties");
  {PKG}.Reforge.load();
  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getCommandRegistry().registerCommand(new {PKG}.ReforgeCmd());
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.RollsReady());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /reforge (players) opens the Reforge Anvil; /rolls [read] | reroll | give [itemId] | clear (admin only); tooltip = base value (+roll)");
}}""", pl))

for c in (rl, rfg, rpg, rfc, rdc, rrc, clc, gvc, gvr, cmd, rft, rdy, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyRolls-%s.jar" % VERSION)
m = B.manifest("SkyyRolls", VERSION, "SkyWynn item rolls: reforge + stats stored in ItemStack metadata, shown on the tooltip as base value (+roll); /reforge Reforge Anvil page (coins via SkyyCoins, optional); /rolls admin tools. Zero dependencies.", PKG + ".SkyyRollsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyRolls.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyRolls" % VERSION, disable_prefix="Skyy:")
