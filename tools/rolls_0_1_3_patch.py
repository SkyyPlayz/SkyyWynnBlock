r"""Derive SkyyRolls/build_skyyrolls_0.1.3.py from 0.1.2.
0.1.3 (Skyy 2026-09-24 live test of 0.1.2: "/rolls reroll" wrote 'Withered ... dmg +24% str 12 crit 11 quality 68' into the metadata
of a Mithril Shortbow but "item doesn't show what the reroll did"; and Skyy "accidentally rerolled my farming sack"):

1. ROLLS ON THE TOOLTIP. The client never renders an unknown metadata key ("SkyyRolls" was invisible). It DOES know one key:
   "ItemDisplay" = com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata {Name: Message, Description:
   Message}. Evidence (2026-09-24, read-only):
   - HytaleServer.jar 0.6.8: ItemDisplayMetadata.<clinit> = KeyedCodec "ItemDisplay" over a BuilderCodec with "Name" and
     "Description" (both Message.CODEC = FormattedMessage fields RawText/MessageId/Params/Children/Bold/.../Color/Link);
     ItemStack.getDisplayName()/getDisplayDescription() read it first and fall back to the item's translation; ItemStack.toPacket()
     sends the whole metadata document as JSON (ItemWithAllMetadata.metadata), so the key reaches every client.
   - HytaleClient.exe: the client's item stack has GetDisplayName/GetDisplayDescription and a ClientItemMetadata type whose
     JSON properties are Adventure, CapturedEntity, ItemDisplay and Extra, with an ItemDisplayMetadata type of FormattedMessages
     (System.Text.Json source-gen names Create_ItemDisplayMetadata / ItemDisplayMetadataPropInit). So the client parses
     "ItemDisplay" out of the metadata JSON itself.
   - SimpleEnchantments-1.2.0.jar (org.herolias - the same author as DynamicTooltipsLib, ServerVersion >=0.6.0-pre.13 <0.7.0, this
     server is 0.6.8) shows its enchantments ONLY this way: NativeTooltipManager.writeDisplay = stack.withMetadata(
     ItemDisplayMetadata.KEYED_CODEC, new ItemDisplayMetadata(name, description)); description = the item's own description
     (Message.translation of getDescriptionTranslationKey, skipped when I18nModule.getMessage("en-US", key) is missing) + "\n" +
     coloured Message.raw lines; it logs "Using native per-stack ItemDisplay metadata for enchantment tooltips". Copied here.
   - DynamicTooltipsLib is NOT needed (it swaps per-player virtual item ids in packet filters; it is disabled in the HUD mod world).
   What is written: Name = "<Reforge> <item name>" in the item's rarity colour (ItemQuality.getTextColor() of the stack's quality,
   e.g. Epic #8b339e), Description = the item's vanilla description (if it has one), a blank line, then one line per roll:
   Reforge, Damage, Strength, Crit, Roll Quality. Written by give and reroll; items that already carry SkyyRolls metadata get it
   from /rolls read (held item) and from a join refresh (PlayerReadyEvent -> 3 s later on the player's world thread: hotbar,
   storage, backpack, armor, utility, tools; skipped while SkyyProfiles' profile:busy:<uuid> is set; read-only when every
   rolled item is already up to date).
   Metadata stays backwards compatible: "SkyyRolls" keeps exactly {reforge, dmg, str, crit, quality, rolledAt}; new keys are
   "ItemDisplay" (engine key) and "SkyyRollsView" {v, sig, prev?} = our marker: v = display version, sig = what the display was
   built from (skip rewrites when unchanged), prev = an ItemDisplay that was on the item BEFORE we wrote ours (restored by clear).
2. ONLY WEAPONS, ARMOR AND TOOLS: give and reroll refuse anything that is not Weapon_* / Armor_* / Tool_*, refuse Weapon_* ammo
   (any id token Arrow, Bolt, Bomb, Dart, Grenade, Ammo, Bullet, Shell, Shuriken, Thrown - checked against Assets.zip and every
   installed mod: Weapon_Arrow_*, Weapon_Bomb_*, Weapon_Dart_Tribal, Weapon_Grenade_Frag, Weapon_Spirit_Bomb, ...), and refuse any
   Skyy item (id starting with Skyy, e.g. Skyy_Sack_*) by name, with a chat line saying why. Spears (stack 5/30), spellbooks and claws
   are real weapons and stay rollable. /rolls give prefers a rollable match and only suggests rollable ids.
3. /rolls clear (admin, auto node ...command.rolls.clear): removes "SkyyRolls" and our "SkyyRollsView" from the held item and our
   "ItemDisplay" (or puts back the one that was there before), keeping item id, quantity, durability, max durability, quality and
   every other metadata key (ItemStack.withMetadata(BsonDocument) = new ItemStack(itemId, quantity, durability, maxDurability,
   qualityIndex, doc) - HytaleServer.jar bytecode). For Skyy's rerolled farming sack.
4. Held-item fix: 0.1.2 read the hand with Inventory.getItemInHand() (the TOOLS section item while usingToolsItem) but wrote the
   reroll into the HOTBAR slot - that could overwrite a hotbar item with a copy of the tools item. read/reroll/clear now read and
   write the same container + slot (tools section when usingToolsItem, else the active hotbar slot).
5. Numbers are read with isNumber()/asNumber() (0.1.2 getInt32 would throw on an Int64/Double after a save round trip).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.2.py")
dst = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.3.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


# ---------------- docstring ----------------
rep('''"""SkyyRolls 0.1.1 - build script (javassist via jpype). P0 spike #3: prove ItemStack metadata survives save/reload.
Run:   python build_skyyrolls_0.1.1.py            -> SkyyRolls/SkyyRolls-0.1.1.jar
       python build_skyyrolls_0.1.1.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Commands (ADMIN ONLY, see Permissions below):
  /rolls                 same as /rolls read
  /rolls read            prints the rolls on the item in your hand + the raw metadata JSON (shows what vanilla stores too)
  /rolls reroll          replaces the item in your hand with the same item + fresh rolls (same slot)
  /rolls give [itemId]   gives one item (default Weapon_Longsword_Copper) with random rolls stored in metadata key "SkyyRolls"
                         {reforge: <name>, dmg: +%, str: n, crit: n, quality: 0..100, rolledAt: millis}''',
    '''"""SkyyRolls 0.1.3 - build script (javassist via jpype). P0 spike #3: prove ItemStack metadata survives save/reload.
Run:   python build_skyyrolls_0.1.3.py            -> SkyyRolls/SkyyRolls-0.1.3.jar
       python build_skyyrolls_0.1.3.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Commands (ADMIN ONLY, see Permissions below):
  /rolls                 same as /rolls read
  /rolls read            prints the rolls on the item in your hand + the raw metadata JSON (shows what vanilla stores too);
                         an item rolled before 0.1.3 gets its tooltip written here
  /rolls reroll          replaces the item in your hand with the same item + fresh rolls (same slot) - weapons, armor, tools only
  /rolls give [itemId]   gives one item (default Weapon_Longsword_Copper) with random rolls stored in metadata key "SkyyRolls"
                         {reforge: <name>, dmg: +%, str: n, crit: n, quality: 0..100, rolledAt: millis} - weapons, armor, tools only
  /rolls clear           removes the rolls (and the rolls tooltip) from the item in your hand, keeps everything else''')
rep("0.1.2: /rolls give takes a plain name",
    "0.1.3: the rolls are SHOWN on the item: native ItemDisplay metadata (Name = rarity-coloured '<Reforge> <item>', Description =" + LF +
    "  vanilla description + one line per roll), written by give/reroll, by /rolls read and by a join refresh for older rolled items;" + LF +
    "  only Weapon_* (no ammo) / Armor_* / Tool_* items can be given or rerolled (never Skyy_* items); new /rolls clear; hand read and" + LF +
    "  write use the same slot. Evidence + details in tools/rolls_0_1_3_patch.py." + LF +
    "0.1.2: /rolls give takes a plain name")

# ---------------- constants + probes ----------------
rep('ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"',
    'ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"' + LF +
    'IDM = "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata"' + LF +
    'IQ  = "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality"' + LF +
    'I18N = "com.hypixel.hytale.server.core.modules.i18n.I18nModule"' + LF +
    'PCOL = "com.hypixel.hytale.protocol.Color"' + LF +
    'TXN = "com.hypixel.hytale.server.core.inventory.transaction.Transaction"' + LF +
    'HSV = "com.hypixel.hytale.server.core.HytaleServer"' + LF +
    'UNI = "com.hypixel.hytale.server.core.universe.Universe"' + LF +
    'PRE = "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent"')
rep('''             (AC, "setAllowsExtraArguments"), (CTX, "getInputString"), (ITM, "getAssetMap")):''',
    '''             (AC, "setAllowsExtraArguments"), (CTX, "getInputString"), (ITM, "getAssetMap"),
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
             ("com.hypixel.hytale.event.EventRegistry", "registerGlobal")):''')

# ---------------- classes ----------------
rep('rrc = pool.makeClass(PKG + ".RollsRerollCmd", pool.get(APC))',
    'rrc = pool.makeClass(PKG + ".RollsRerollCmd", pool.get(APC))' + LF +
    'clc = pool.makeClass(PKG + ".RollsClearCmd", pool.get(APC))')
rep('pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))',
    'rft = pool.makeClass(PKG + ".RollsRefreshTask")' + LF +
    'rdy = pool.makeClass(PKG + ".RollsReady")' + LF +
    'pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))')

# ---------------- Rolls: fields + display helpers (before roll(), which does not need them; applyRolls does) ----------------
rep('''rl.addField(CtField.make('public static final String DEFAULT_ITEM = "Weapon_Longsword_Copper";', rl))''',
    '''rl.addField(CtField.make('public static final String DEFAULT_ITEM = "Weapon_Longsword_Copper";', rl))
# 0.1.3: our marker key next to the engine's "ItemDisplay" key, its version, and the Weapon_* id tokens that mean ammo
rl.addField(CtField.make('public static final String VIEW_KEY = "SkyyRollsView";', rl))
rl.addField(CtField.make('public static final int VIEW_V = 1;', rl))
rl.addField(CtField.make('public static final String[] AMMO = new String[] { "arrow", "arrows", "bolt", "bolts", "bomb", "bombs", "dart", "darts", "grenade", "grenades", "ammo", "bullet", "bullets", "shell", "shells", "shuriken", "shurikens", "thrown" };', rl))''')

HELPERS = r'''rl.addMethod(CtNewMethod.make("""
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
# true when the item's ItemDisplay was written by us from exactly these rolls (then nothing needs rewriting)
rl.addMethod(CtNewMethod.make(f"""
public static boolean upToDate({IS} it) {{
  if (it == null || it.isEmpty()) return false;
  {BD} md = it.getMetadata();
  if (md == null || !md.containsKey({IDM}.KEY)) return false;
  {BV} r = md.get("SkyyRolls");
  {BV} v = md.get(VIEW_KEY);
  if (r == null || !r.isDocument() || v == null || !v.isDocument()) return false;
  {BV} g = v.asDocument().get("sig");
  return g != null && g.isString() && g.asString().getValue().equals(sig(it, r.asDocument()));
}}""", rl))
# writes ItemDisplay {Name, Description} + our SkyyRollsView marker (keeps "prev" = an ItemDisplay that was not ours).
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
    {BD} view = new {BD}();
    view.append("v", new org.bson.BsonInt32(VIEW_V));
    view.append("sig", new org.bson.BsonString(sig(s, d)));
    {BV} old = md.get(VIEW_KEY);
    if (old != null && old.isDocument()) {{
      {BV} p = old.asDocument().get("prev");
      if (p != null && !p.isNull()) view.append("prev", p);
    }} else {{
      {BV} cur = md.get({IDM}.KEY);
      if (cur != null && !cur.isNull()) view.append("prev", cur);
    }}
    {IS} out = s.withMetadata({IDM}.KEYED_CODEC, new {IDM}(name, desc));
    return out.withMetadata(VIEW_KEY, ({BV}) view);
  }} catch (Throwable t) {{
    warn("could not write the rolls tooltip for " + (s == null ? "null" : s.getItemId()) + ": " + t);
    return s;
  }}
}}""", rl))
'''
rep('''rl.addMethod(CtNewMethod.make(f"""
public static {BD} roll() {{''', HELPERS + '''rl.addMethod(CtNewMethod.make(f"""
public static {BD} roll() {{''')

rep('''public static {IS} applyRolls({IS} base) {{
  return base.withMetadata("SkyyRolls", ({BV}) roll());
}}''', '''public static {IS} applyRolls({IS} base) {{
  return withDisplay(base.withMetadata("SkyyRolls", ({BV}) roll()));
}}''')

rep('''  return d.getString("reforge", new org.bson.BsonString("?")).getValue() + " " + it.getItemId()
    + "  dmg +" + d.getInt32("dmg", new org.bson.BsonInt32(0)).getValue() + "%"
    + "  str " + d.getInt32("str", new org.bson.BsonInt32(0)).getValue()
    + "  crit " + d.getInt32("crit", new org.bson.BsonInt32(0)).getValue()
    + "  quality " + d.getInt32("quality", new org.bson.BsonInt32(0)).getValue();''',
    '''  return str(d, "reforge") + " " + it.getItemId()
    + "  dmg +" + num(d, "dmg") + "%"
    + "  str " + num(d, "str")
    + "  crit " + num(d, "crit")
    + "  quality " + num(d, "quality")
    + (upToDate(it) ? "  [shown on the tooltip]" : "  [not on the tooltip]");''')

# resolve(): prefer (and only suggest) ids that can have rolls
rep('''  java.util.ArrayList weapons = new java.util.ArrayList();''', '''  java.util.ArrayList good = new java.util.ArrayList();''')
rep('''      if (all) {{ hits.add(id); if (id.startsWith("Weapon_")) weapons.add(id); }}''',
    '''      if (all) {{ hits.add(id); if (refuseId(id) == null) good.add(id); }}''')
rep('''  if (weapons.size() == 1) return (String) weapons.get(0);
  java.util.Collections.sort(hits);
  for (int i = 0; i < hits.size() && i < 8; i++) {{ if (sugg.length() > 0) sugg.append(", "); sugg.append((String) hits.get(i)); }}
  if (hits.size() > 8) sugg.append(" ... (" + hits.size() + " matches)");''',
    '''  if (good.size() == 1) return (String) good.get(0);
  java.util.ArrayList show = hits;
  if (good.size() > 0) show = good;
  java.util.Collections.sort(show);
  for (int i = 0; i < show.size() && i < 8; i++) {{ if (sugg.length() > 0) sugg.append(", "); sugg.append((String) show.get(i)); }}
  if (show.size() > 8) sugg.append(" ... (" + show.size() + " matches)");''')

# ---------------- Rolls: hand slot, refresh, clear, and the actions ----------------
OLD_ACTIONS = '''rl.addMethod(CtNewMethod.make(f"""
public static void give({PR} pr, {INV} inv, String q) {{
  StringBuilder sugg = new StringBuilder();
  String id = resolve(q, sugg);
  if (id == null) {{
    pr.sendMessage({MSG}.raw("[Rolls] no item matches '" + q + "'" + (sugg.length() > 0 ? ". Did you mean: " + sugg : " - use an item id like Weapon_Shortbow_Mithril")));
    return;
  }}
  {IS} it = applyRolls(new {IS}(id, 1));
  Object tx = inv.getStorage().addItemStack(it);
  pr.sendMessage({MSG}.raw("[Rolls] gave: " + describe(it) + "  (tx " + (tx == null ? "null" : tx.getClass().getSimpleName()) + ")"));
  pr.sendMessage({MSG}.raw("[Rolls] raw: " + (it.getMetadata() == null ? "null" : it.getMetadata().toJson())));
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static void reroll({PR} pr, {INV} inv) {{
  {IS} hand = inv.getItemInHand();
  if (hand == null || hand.isEmpty()) {{ pr.sendMessage({MSG}.raw("[Rolls] hold an item first")); return; }}
  {IS} fresh = applyRolls(hand);
  Object tx = inv.getHotbar().setItemStackForSlot((short) inv.getActiveHotbarSlot(), fresh);
  pr.sendMessage({MSG}.raw("[Rolls] rerolled: " + describe(fresh) + "  (tx " + (tx == null ? "null" : tx.getClass().getSimpleName()) + ")"));
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static void read({PR} pr, {INV} inv) {{
  {IS} hand = inv.getItemInHand();
  pr.sendMessage({MSG}.raw("[Rolls] " + describe(hand)));
  if (hand != null && !hand.isEmpty()) pr.sendMessage({MSG}.raw("[Rolls] raw: " + (hand.getMetadata() == null ? "null" : hand.getMetadata().toJson())));
}}""", rl))'''

NEW_ACTIONS = r'''# 0.1.3: the hand = the same container + slot for reading AND writing (Inventory.getItemInHand() returns the TOOLS item while
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
# /rolls clear: drop SkyyRolls + our marker + our ItemDisplay (or restore the ItemDisplay that was there before us); everything
# else stays - withMetadata(BsonDocument) keeps itemId, quantity, durability, maxDurability and qualityIndex (bytecode)
rl.addMethod(CtNewMethod.make(f"""
public static {IS} cleared({IS} it) {{
  {BD} md = it.getMetadata();
  if (md == null) return it;
  {BD} c = ({BD}) md.clone();
  c.remove("SkyyRolls");
  {BV} view = ({BV}) c.remove(VIEW_KEY);
  if (view != null && view.isDocument()) {{
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
}}""", rl))'''
rep(OLD_ACTIONS, NEW_ACTIONS)

rep('''# action: "give" | "reroll" | anything else = read (same fallback as 0.1). id is only used by give.''',
    '''# action: "give" | "reroll" | "clear" | anything else = read (same fallback as 0.1). id is only used by give.''')
rep('''    if (action.equals("reroll")) {{ reroll(pr, inv); return; }}''',
    '''    if (action.equals("reroll")) {{ reroll(pr, inv); return; }}
    if (action.equals("clear")) {{ clear(pr, inv); return; }}''')

# ---------------- /rolls clear ----------------
rep('''# ================= /rolls give <itemId>  (usage variant of give: description-only constructor) =================''',
    '''# ================= /rolls clear (0.1.3) =================
clc.addConstructor(CtNewConstructor.make('public RollsClearCmd() { super("clear", "Remove the rolls from the item in your hand (keeps the item, durability and other data)"); }', clc))
clc.addMethod(CtNewMethod.make(f"""
{EXEC}
  {PKG}.Rolls.run(store, ref, pr, "clear", null);
}}""", clc))

# ================= /rolls give <itemId>  (usage variant of give: description-only constructor) =================''')
rep('''  super("rolls", "SkyyRolls spike (admin): /rolls [read] | /rolls reroll | /rolls give [itemId]");
  this.actionArg = withOptionalArg("action", "old 0.1 form: give | read | reroll", {ATY}.STRING);''',
    '''  super("rolls", "SkyyRolls spike (admin): /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear");
  this.actionArg = withOptionalArg("action", "old 0.1 form: give | read | reroll | clear", {ATY}.STRING);''')
rep('''  addSubCommand(new {PKG}.RollsGiveCmd());''', '''  addSubCommand(new {PKG}.RollsGiveCmd());
  addSubCommand(new {PKG}.RollsClearCmd());''')

# ---------------- join refresh (SkyyProfiles OpenTask/ProfReady pattern: scheduler delay -> hop to the player's world thread) ----------------
REFRESH = r'''# ================= join refresh (0.1.3): rolled items from before 0.1.3 get their tooltip =================
# PlayerReadyEvent (every world switch) -> 3 s later on the scheduler -> hop to the player's CURRENT world thread -> re-check the
# world there -> skip while SkyyProfiles' profile:busy:<uuid> is set (crash recovery reloads the inventory) -> Rolls.refreshInventory.
# Up to 15 tries, 2 s apart. Items that already show their rolls are only read.
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
rft.addMethod(CtNewMethod.make("""
public void again() {
  this.tries = this.tries + 1;
  if (this.tries < 15) later(2000L);
}""", rft))
rft.addMethod(CtNewMethod.make(f"""
public void run() {{
  try {{
    if (this.pr == null || !this.pr.isValid()) return;
    if (!this.onWorld) {{
      java.util.UUID wu = this.pr.getWorldUuid();
      if (wu == null) {{ again(); return; }}
      {WLD} w = {UNI}.get().getWorld(wu);
      if (w == null) {{ again(); return; }}
      this.onWorld = true;
      this.hopWorld = wu;
      w.execute(this);
      return;
    }}
    java.util.UUID now = this.pr.getWorldUuid();
    if (now == null || !now.equals(this.hopWorld)) {{ again(); return; }}
    if ({PKG}.Rolls.busy(this.pr.getUuid())) {{ again(); return; }}
    {REF} r = this.pr.getReference();
    if (r == null || !r.isValid()) {{ again(); return; }}
    {ST} st = r.getStore();
    if (st == null) {{ again(); return; }}
    {PLA} p = ({PLA}) st.getComponent(r, {PLA}.getComponentType());
    if (p == null || p.getInventory() == null) {{ again(); return; }}
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

# ================= plugin ================='''
rep('''# ================= plugin =================''', REFRESH)
rep('''  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /rolls [read] | /rolls reroll | /rolls give [itemId] (admin only)");''',
    '''  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getEventRegistry().registerGlobal({PRE}.class, new {PKG}.RollsReady());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /rolls [read] | /rolls reroll | /rolls give [itemId] | /rolls clear (admin only); rolls shown on the item tooltip");''')

rep('''for c in (rl, rdc, rrc, gvc, gvr, cmd, pl):''', '''for c in (rl, rdc, rrc, clc, gvc, gvr, cmd, rft, rdy, pl):''')
rep('''"SkyWynn item rolls spike: random stats stored in ItemStack metadata (/rolls give|read|reroll). Zero dependencies."''',
    '''"SkyWynn item rolls spike: random stats stored in ItemStack metadata and shown on the item tooltip (/rolls give|read|reroll|clear). Zero dependencies."''')

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
