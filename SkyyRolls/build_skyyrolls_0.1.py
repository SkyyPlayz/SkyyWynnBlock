"""SkyyRolls 0.1 - build script (javassist via jpype). P0 spike #3: prove ItemStack metadata survives save/reload.
Run:   python build_skyyrolls_0.1.py            -> SkyyRolls/SkyyRolls-0.1.jar
       python build_skyyrolls_0.1.py --deploy   -> also copies to Mods/SkyyRolls.jar and enables it in the HUD mod world
Commands:
  /rolls give [itemId]   gives one item (default Weapon_Longsword_Copper) with random rolls stored in metadata key "SkyyRolls"
                         {reforge: <name>, dmg: +%, str: n, crit: n, quality: 0..100, rolledAt: millis}
  /rolls read            prints the rolls on the item in your hand + the raw metadata JSON (shows what vanilla stores too)
  /rolls reroll          replaces the item in your hand with the same item + fresh rolls (same slot)
Test protocol: give -> read -> relog -> read again (must match) -> drop + pick up -> read -> put in a chest and take out -> read.
API: ItemStack.withMetadata(String, BsonValue) returns a NEW stack; ItemStack.getMetadata() -> org.bson.BsonDocument;
Inventory.getItemInHand(), getActiveHotbarSlot(), getHotbar().setItemStackForSlot(short, ItemStack).
"""
import sys, os
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
WLD = "com.hypixel.hytale.server.core.universe.world.World"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
MSG = "com.hypixel.hytale.server.core.Message"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
OA  = "com.hypixel.hytale.server.core.command.system.arguments.system.OptionalArg"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
BD  = "org.bson.BsonDocument"
BV  = "org.bson.BsonValue"

for c, m in ((IS, "withMetadata"), (IS, "getMetadata"), (INV, "getItemInHand"), (INV, "getActiveHotbarSlot"), (INV, "getHotbar"),
             (IC, "setItemStackForSlot"), (IC, "addItemStack"), (PLA, "getInventory"), (CTX, "provided"), (BD, "append")):
    B.probe(pool, c, m)

PKG = "com.skyy.rolls"
rl  = pool.makeClass(PKG + ".Rolls")
cmd = pool.makeClass(PKG + ".RollsCmd", pool.get(APC))
pl  = pool.makeClass(PKG + ".SkyyRollsPlugin", pool.get(JP))

# ================= Rolls (pure helpers) =================
rl.addField(CtField.make(f"public static {LOG} LOG;", rl))
rl.addField(CtField.make('public static final String[] REFORGES = new String[] { "Sharp", "Heroic", "Spicy", "Legendary", "Fabled", "Gentle", "Odd", "Fast", "Epic", "Withered" };', rl))
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

# ================= /rolls =================
cmd.addField(CtField.make(f"public {OA} actionArg;", cmd))
cmd.addField(CtField.make(f"public {OA} itemArg;", cmd))
cmd.addConstructor(CtNewConstructor.make(f"""
public RollsCmd() {{
  super("rolls", "SkyyRolls spike: /rolls give [itemId] | /rolls read | /rolls reroll");
  this.actionArg = withOptionalArg("action", "give | read | reroll", {ATY}.STRING);
  this.itemArg = withOptionalArg("item", "item id for give (default Weapon_Longsword_Copper)", {ATY}.STRING);
}}""", cmd))
cmd.addMethod(CtNewMethod.make(f"""
protected void execute({CTX} ctx, {ST} store, {REF} ref, {PR} pr, {WLD} world) {{
  try {{
    {PLA} p = ({PLA}) store.getComponent(ref, {PLA}.getComponentType());
    if (p == null || p.getInventory() == null) {{ pr.sendMessage({MSG}.raw("[Rolls] no player inventory")); return; }}
    {INV} inv = p.getInventory();
    String a = ctx.provided(this.actionArg) ? String.valueOf(ctx.get(this.actionArg)).trim().toLowerCase() : "read";
    if (a.equals("give")) {{
      String id = ctx.provided(this.itemArg) ? String.valueOf(ctx.get(this.itemArg)).trim() : "Weapon_Longsword_Copper";
      {IS} it = {PKG}.Rolls.applyRolls(new {IS}(id, 1));
      Object tx = inv.getStorage().addItemStack(it);
      pr.sendMessage({MSG}.raw("[Rolls] gave: " + {PKG}.Rolls.describe(it) + "  (tx " + (tx == null ? "null" : tx.getClass().getSimpleName()) + ")"));
      pr.sendMessage({MSG}.raw("[Rolls] raw: " + (it.getMetadata() == null ? "null" : it.getMetadata().toJson())));
      return;
    }}
    if (a.equals("reroll")) {{
      {IS} hand = inv.getItemInHand();
      if (hand == null || hand.isEmpty()) {{ pr.sendMessage({MSG}.raw("[Rolls] hold an item first")); return; }}
      {IS} fresh = {PKG}.Rolls.applyRolls(hand);
      Object tx = inv.getHotbar().setItemStackForSlot((short) inv.getActiveHotbarSlot(), fresh);
      pr.sendMessage({MSG}.raw("[Rolls] rerolled: " + {PKG}.Rolls.describe(fresh) + "  (tx " + (tx == null ? "null" : tx.getClass().getSimpleName()) + ")"));
      return;
    }}
    {IS} hand = inv.getItemInHand();
    pr.sendMessage({MSG}.raw("[Rolls] " + {PKG}.Rolls.describe(hand)));
    if (hand != null && !hand.isEmpty()) pr.sendMessage({MSG}.raw("[Rolls] raw: " + (hand.getMetadata() == null ? "null" : hand.getMetadata().toJson())));
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
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyRolls] {VERSION} ready - /rolls give|read|reroll");
}}""", pl))

for c in (rl, cmd, pl):
    c.writeFile(OUT)
print("classes written")

jar = os.path.join(HERE, "SkyyRolls-%s.jar" % VERSION)
m = B.manifest("SkyyRolls", VERSION, "SkyWynn item rolls spike: random stats stored in ItemStack metadata (/rolls give|read|reroll). Zero dependencies.", PKG + ".SkyyRollsPlugin")
m["IncludesAssetPack"] = False
B.assemble(jar, m, OUT)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyRolls.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyRolls" % VERSION, disable_prefix="Skyy:")
