"""SkyyRolls 0.1.3 - build script (javassist via jpype). P0 spike #3: prove ItemStack metadata survives save/reload.
Run:   python build_skyyrolls_0.1.3.py            -> SkyyRolls/SkyyRolls-0.1.3.jar
       python build_skyyrolls_0.1.3.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
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
Permissions: SkyyRolls is a test spike and /rolls give creates items, so it stays ADMIN-ONLY on purpose: there is NO
  setPermissionGroups(new String[] { "hytale:Adventurer" }) here (unlike the player commands in SkyyEssentials and the other
  Skyy mods). AbstractCommand.setOwner() gives the root, every subcommand and the variant an auto node (plugin base
  "<group>.<name>" lower-cased, spaces -> "_"; a subcommand appends ".<name>", a variant reuses its parent's node):
  skyy.0.1.3_skyyrolls.command.rolls, ...command.rolls.read, ...command.rolls.reroll, ...command.rolls.give, ...command.rolls.clear.
  hasPermission() on a subcommand without permission groups also requires the parent's node. Default players
  (hytale:Adventurer) have none of these; only "*" admins do. The version is part of the node, so it changes on every bump.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.3"
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

# ================= Rolls (pure helpers) =================
rl.addField(CtField.make(f"public static {LOG} LOG;", rl))
rl.addField(CtField.make('public static final String[] REFORGES = new String[] { "Sharp", "Heroic", "Spicy", "Legendary", "Fabled", "Gentle", "Odd", "Fast", "Epic", "Withered" };', rl))
rl.addField(CtField.make('public static final String DEFAULT_ITEM = "Weapon_Longsword_Copper";', rl))
# 0.1.3: our marker key next to the engine's "ItemDisplay" key, its version, and the Weapon_* id tokens that mean ammo
rl.addField(CtField.make('public static final String VIEW_KEY = "SkyyRollsView";', rl))
rl.addField(CtField.make('public static final int VIEW_V = 1;', rl))
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
# Description: the vanilla description (only when the item has one - otherwise the client would print the raw key), a blank line,
# then one line per roll. Same shape as SimpleEnchantments composeDescription (base + "\n" + coloured raw lines).
rl.addMethod(CtNewMethod.make(f"""
public static {MSG} descMsg({IS} it, {BD} d, String col) {{
  {MSG} m = {MSG}.empty();
  try {{
    {ITM} item = it.getItem();
    if (item != null && tr(item.getDescriptionTranslationKey()) != null) {{
      m.insert(item.getDescriptionTranslationMessage());
      m.insert({MSG}.raw("\\n\\n"));
    }}
  }} catch (Throwable t) {{ }}
  int vd = num(d, "dmg");
  int vs = num(d, "str");
  int vc = num(d, "crit");
  int vq = num(d, "quality");
  m.insert(statLine("Reforge", str(d, "reforge"), col));
  m.insert({MSG}.raw("\\n"));
  m.insert(statLine("Damage", "+" + vd + "%", vd > 0 ? "#55FF55" : "#AAAAAA"));
  m.insert({MSG}.raw("\\n"));
  m.insert(statLine("Strength", "+" + vs, vs > 0 ? "#55FF55" : "#AAAAAA"));
  m.insert({MSG}.raw("\\n"));
  m.insert(statLine("Crit", "+" + vc, vc > 0 ? "#55FF55" : "#AAAAAA"));
  m.insert({MSG}.raw("\\n"));
  m.insert(statLine("Roll Quality", vq + "%", qualityColor(vq)));
  return m;
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String sig({IS} it, {BD} d) {{
  return VIEW_V + ":" + it.getItemId() + ":" + it.getQualityIndex() + ":" + Integer.toHexString(d.toJson().hashCode());
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
  d.append("dmg", new org.bson.BsonInt32(r.nextInt(31)));
  d.append("str", new org.bson.BsonInt32(r.nextInt(26)));
  d.append("crit", new org.bson.BsonInt32(r.nextInt(16)));
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
  {BD} d = v.asDocument();
  return str(d, "reforge") + " " + it.getItemId()
    + "  dmg +" + num(d, "dmg") + "%"
    + "  str " + num(d, "str")
    + "  crit " + num(d, "crit")
    + "  quality " + num(d, "quality")
    + (upToDate(it) ? "  [shown on the tooltip]" : "  [not on the tooltip]");
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
  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.RollsReady());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear (admin only); rolls shown on the item tooltip");
}}""", pl))

for c in (rl, rdc, rrc, clc, gvc, gvr, cmd, rft, rdy, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyRolls-%s.jar" % VERSION)
m = B.manifest("SkyyRolls", VERSION, "SkyWynn item rolls spike: random stats stored in ItemStack metadata and shown on the item tooltip (/rolls give|read|reroll|clear). Zero dependencies.", PKG + ".SkyyRollsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyRolls.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyRolls" % VERSION, disable_prefix="Skyy:")
