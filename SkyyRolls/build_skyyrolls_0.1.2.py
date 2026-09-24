"""SkyyRolls 0.1.1 - build script (javassist via jpype). P0 spike #3: prove ItemStack metadata survives save/reload.
Run:   python build_skyyrolls_0.1.1.py            -> SkyyRolls/SkyyRolls-0.1.1.jar
       python build_skyyrolls_0.1.1.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Commands (ADMIN ONLY, see Permissions below):
  /rolls                 same as /rolls read
  /rolls read            prints the rolls on the item in your hand + the raw metadata JSON (shows what vanilla stores too)
  /rolls reroll          replaces the item in your hand with the same item + fresh rolls (same slot)
  /rolls give [itemId]   gives one item (default Weapon_Longsword_Copper) with random rolls stored in metadata key "SkyyRolls"
                         {reforge: <name>, dmg: +%, str: n, crit: n, quality: 0..100, rolledAt: millis}
  The 0.1 flag forms still work: /rolls --action give|read|reroll [--item <itemId>]
Test protocol: give -> read -> relog -> read again (must match) -> drop + pick up -> read -> put in a chest and take out -> read.
API: ItemStack.withMetadata(String, BsonValue) returns a NEW stack; ItemStack.getMetadata() -> org.bson.BsonDocument;
Inventory.getItemInHand(), getActiveHotbarSlot(), getHotbar().setItemStackForSlot(short, ItemStack).

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
  skyy.0.1.1_skyyrolls.command.rolls, ...command.rolls.read, ...command.rolls.reroll, ...command.rolls.give.
  hasPermission() on a subcommand without permission groups also requires the parent's node. Default players
  (hytale:Adventurer) have none of these; only "*" admins do. The version is part of the node, so it changes on every bump.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B

VERSION = "0.1.2"
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

for c, m in ((IS, "withMetadata"), (IS, "getMetadata"), (INV, "getItemInHand"), (INV, "getActiveHotbarSlot"), (INV, "getHotbar"),
             (IC, "setItemStackForSlot"), (IC, "addItemStack"), (PLA, "getInventory"), (CTX, "provided"), (BD, "append"),
             (AC, "addSubCommand"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "withOptionalArg"),
             (AC, "setAllowsExtraArguments"), (CTX, "getInputString"), (ITM, "getAssetMap")):
    B.probe(pool, c, m)

PKG = "com.skyy.rolls"
rl  = pool.makeClass(PKG + ".Rolls")
rdc = pool.makeClass(PKG + ".RollsReadCmd", pool.get(APC))
rrc = pool.makeClass(PKG + ".RollsRerollCmd", pool.get(APC))
gvc = pool.makeClass(PKG + ".RollsGiveVariantCmd", pool.get(APC))
gvr = pool.makeClass(PKG + ".RollsGiveCmd", pool.get(APC))
cmd = pool.makeClass(PKG + ".RollsCmd", pool.get(APC))
pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))

# ================= Rolls (pure helpers) =================
rl.addField(CtField.make(f"public static {LOG} LOG;", rl))
rl.addField(CtField.make('public static final String[] REFORGES = new String[] { "Sharp", "Heroic", "Spicy", "Legendary", "Fabled", "Gentle", "Odd", "Fast", "Epic", "Withered" };', rl))
rl.addField(CtField.make('public static final String DEFAULT_ITEM = "Weapon_Longsword_Copper";', rl))
rl.addMethod(CtNewMethod.make("""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyRolls] " + msg); } catch (Throwable t) { }
}""", rl))
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
  return base.withMetadata("SkyyRolls", ({BV}) roll());
}}""", rl))
rl.addMethod(CtNewMethod.make(f"""
public static String describe({IS} it) {{
  if (it == null || it.isEmpty()) return "no item in hand";
  {BD} md = it.getMetadata();
  if (md == null) return it.getItemId() + ": no metadata at all";
  {BV} v = md.get("SkyyRolls");
  if (v == null || !v.isDocument()) return it.getItemId() + ": no rolls (metadata keys: " + md.keySet() + ")";
  {BD} d = v.asDocument();
  return d.getString("reforge", new org.bson.BsonString("?")).getValue() + " " + it.getItemId()
    + "  dmg +" + d.getInt32("dmg", new org.bson.BsonInt32(0)).getValue() + "%"
    + "  str " + d.getInt32("str", new org.bson.BsonInt32(0)).getValue()
    + "  crit " + d.getInt32("crit", new org.bson.BsonInt32(0)).getValue()
    + "  quality " + d.getInt32("quality", new org.bson.BsonInt32(0)).getValue();
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
  java.util.ArrayList weapons = new java.util.ArrayList();
  try {{
    java.util.Iterator it = {ITM}.getAssetMap().getAssetMap().keySet().iterator();
    while (it.hasNext()) {{
      String id = String.valueOf(it.next());
      if (id.length() == 0 || id.charAt(0) == '*') continue;
      String low = id.toLowerCase();
      if (low.equals(norm)) return id;
      boolean all = true;
      for (int i = 0; i < words.length; i++) {{ if (words[i].length() > 0 && low.indexOf(words[i]) < 0) {{ all = false; break; }} }}
      if (all) {{ hits.add(id); if (id.startsWith("Weapon_")) weapons.add(id); }}
    }}
  }} catch (Throwable e) {{ warn("item lookup failed: " + e); return null; }}
  if (hits.size() == 1) return (String) hits.get(0);
  if (weapons.size() == 1) return (String) weapons.get(0);
  java.util.Collections.sort(hits);
  for (int i = 0; i < hits.size() && i < 8; i++) {{ if (sugg.length() > 0) sugg.append(", "); sugg.append((String) hits.get(i)); }}
  if (hits.size() > 8) sugg.append(" ... (" + hits.size() + " matches)");
  return null;
}}""", rl))
# The three actions, moved out of the 0.1 RollsCmd.execute unchanged so the subcommands, the variant and the
# legacy --action path all share them.
rl.addMethod(CtNewMethod.make(f"""
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
}}""", rl))
# action: "give" | "reroll" | anything else = read (same fallback as 0.1). id is only used by give.
rl.addMethod(CtNewMethod.make(f"""
public static void run({ST} store, {REF} ref, {PR} pr, String action, String id) {{
  try {{
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p == null || p.getInventory() == null) {{ pr.sendMessage({MSG}.raw("[Rolls] no player inventory")); return; }}
    {INV} inv = p.getInventory();
    if (action.equals("give")) {{ give(pr, inv, id); return; }}
    if (action.equals("reroll")) {{ reroll(pr, inv); return; }}
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
  super("rolls", "SkyyRolls spike (admin): /rolls [read] | /rolls reroll | /rolls give [itemId]");
  this.actionArg = withOptionalArg("action", "old 0.1 form: give | read | reroll", {ATY}.STRING);
  this.itemArg = withOptionalArg("item", "old 0.1 form: item id for give (default Weapon_Longsword_Copper)", {ATY}.STRING);
  addSubCommand(new {PKG}.RollsReadCmd());
  addSubCommand(new {PKG}.RollsRerollCmd());
  addSubCommand(new {PKG}.RollsGiveCmd());
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

# ================= plugin =================
pl.addConstructor(CtNewConstructor.make(f"public SkyyRollsPlugin({JPI} init) {{ super(init); }}", pl))
pl.addMethod(CtNewMethod.make(f"""
public void setup() {{
  {PKG}.Rolls.LOG = getLogger();
  getCommandRegistry().registerCommand(new {PKG}.RollsCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /rolls [read] | /rolls reroll | /rolls give [itemId] (admin only)");
}}""", pl))

for c in (rl, rdc, rrc, gvc, gvr, cmd, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyRolls-%s.jar" % VERSION)
m = B.manifest("SkyyRolls", VERSION, "SkyWynn item rolls spike: random stats stored in ItemStack metadata (/rolls give|read|reroll). Zero dependencies.", PKG + ".SkyyRollsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyRolls.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyRolls" % VERSION, disable_prefix="Skyy:")
