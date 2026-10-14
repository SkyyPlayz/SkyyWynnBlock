"""Derive SkyySacks/build_skyysacks_0.8.3.py from the SET pin 0.8.2 (the GENERATED build_skyysacks_0.8.2.py; edit THIS file, then
regenerate: python tools/sacks_0_8_3_patch.py; never re-run sacks_0_8_2_patch.py on top of it).
Run:  python tools/sacks_0_8_3_patch.py   then   python SkyySacks/build_skyysacks_0.8.3.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.3.py

0.8.3 = AUTO-PICKUP (docs/answered/bags.md 2026-10-13, Skyy word for word: "ohhh yeahhh! in hypixle skyblock, items go straight in your
inventory, they never fall on the ground. can we do that too?" -> "Blocks + mob drops, Void first"; kill credit: "both. more loot to top
damager."). Pairs with SkyyMobs 0.1.7 (mob:fn:credit = who hurt which mob); without it a mob's whole drop goes to its killer.

WHAT HAPPENS
  - Every BLOCK DROP a player causes (mining, chopping, harvesting by breaking, Tree Feller / vein abilities = one BreakBlockEvent per
    block, felled-tree logs that SkyySkills' skill:fn:felledBy names) and every MOB DROP goes straight to its player: its SkyyVoid
    category first (catOf + the category's space = level x rarity, exactly the /pd Deposit rule: plain stacks only, cooked food stays
    out unless bags.cookedFood), then the inventory (the vanilla pickup container: InventoryUtils.getContainerForItemPickup with the
    player's PlayerSettings, = where a walk-over pickup would go), and ONLY what fits nowhere stays an item on the ground - moved to the
    player's feet (never lost; the vanilla walk-over pickup takes it once there is room).
  - KILL CREDIT (the rule, also in the Server Setup row help): the TOP DAMAGER (most damage that really came off the mob's health,
    SkyyMobs 0.1.7) gets the mob's WHOLE drop - the vanilla roll, the mob's own carried items, SkyyGear's extra mystery roll and its
    unidentified-gear conversion (unchanged: those are SkyyGear's). If a DIFFERENT player dealt the killing blow, the killer gets an EXTRA
    share: a second roll of the mob's drop list with every stack's amount x pickup.killerShare % (default 50; fractions round up by
    chance, so 50 % of 1 = a coin flip) - spawned through the same engine call, so SkyyGear converts its gear too. Same player = one roll.
    No damage record (SkyyMobs 0.1.6 or older, an environment kill after a player hit) = the killer gets it; no player at all = vanilla.
    Party loot rules are unchanged (there is no party loot split today; party XP is SkyySkills').
  - The top damager / killer only count while online in the SAME world (same Store): a top damager who left (or is in another world)
    is skipped and the killer gets the drop; neither here = the drop stays on the ground (vanilla).
  - PROTECTED AREAS: before anything moves, SkyyIslands' island:perm:fn {player, world, "pickup"} is asked (cached 5 s); FALSE (a visitor
    who may not pick up items there) = the drop stays where it fell, exactly as without auto-pickup. A break that was cancelled (island
    guard, tool gate) spawns no drops, so nothing is claimed.
  - NO VANILLA PICKUP POPUP: our path never calls Player.notifyPickupItem (the vanilla "picked up" notification + its sound); one SkyyHud
    feed card per stack instead (feed:fn:push kind "pickup" = the player's own "Item pickups" route from msgroute:fn:get; "chat" = a
    chat line at most every 3 s; "off" = nothing), the card merges by item id ("Cobblestone x9"); the text names the destination
    ("Cobblestone > Void", "Iron Ore - full, at your feet"). Feed missing / refused + something landed at the feet = one chat warning per
    30 s. The vanilla pickup sound (SFX_Player_Pickup_Item, UI, 2D) plays at most every 120 ms per player.

THE ENGINE HOOK (0.7.0 HytaleServer.jar, read only with javassist - VERIFIED bytecode):
  - Block drops: BlockHarvestUtils.performBlockBreak fires BreakBlockEvent on the breaker BEFORE removing the block, then
    naturallyRemoveBlock -> getDrops -> spawnDrops(accessor, drops, block + (0.5, 0, 0.5)) -> ItemComponent.generateItemDrops (every holder
    at exactly that position) -> accessor.addEntities(holders, SPAWN). Physics drops (a felled tree) take the same spawnDrops path with no
    event and no player.
  - Mob drops: NPCDamageSystems$DropDeathItems (AFTER DeathSystems$TickCorpseRemoval, BEFORE DeathSystems$CorpseRemoval) spawns at exactly
    the NPC position + (0, 1, 0) through the same generateItemDrops + CommandBuffer.addEntities(SPAWN); SkyyGear's GearDeathMark (BEFORE
    DropDeathItems) spawns its extra roll at the same spot.
  - Store.addEntities: HolderSystem.onEntityAdd for all holders, then the refs, then every RefSystem.onEntityAdded(ref, reason, store, cb)
    with ONE CommandBuffer taken for the whole add, consumed (CommandBuffer.consume = queued ops in order, a run(Consumer) gets the
    Store) right after - before the entity ever ticks or is sent to a client. A RefSystem that removes the ref through that buffer hides it
    from the rest. EntityTickingSystems consume their own buffer right after their tick.
  So: PickBreakSys (EntityEventSystem<BreakBlockEvent>, players) CLAIMS {world, block + (0.5, 0, 0.5)} for the breaker (1.5 s); PickDeathMark
  (EntityTickingSystem NPCEntity + DeathComponent, AFTER TickCorpseRemoval, BEFORE DropDeathItems, the DropDeathItems condition copied
  like SkyyGear's GearDeathMark) claims {world, position + (0, 1, 0)} for the top damager and notes the killer's share; PickShareSys
  (AFTER DropDeathItems, BEFORE CorpseRemoval) spawns the killer's share at position + (0, 1 + 1/64, 0) with its own claim; PickItemSys
  (RefSystem ItemComponent + TransformComponent, AddReason.SPAWN only, never a PickupItemComponent = vanilla's flying "picked up"
  animation) looks the new item's exact position up in the claims (no claim at a block-drop spot -> skill:fn:felledBy) and queues ONE
  cb.run(PickDeliver) - it runs when that add's buffer is consumed, so every other RefSystem has already seen the item (SkyyGear's
  GearDropSys turns gear into mystery items in its onEntityAdded, before or after ours - either way we deliver the converted stack). The
  item entity then leaves the store inside the same addEntities call: it never ticks, never reaches a client, nothing is swept from the
  ground. The job first re-queues itself at the TAIL of that buffer, so any operation a later system queued for the item during the add
  (a component put / add on its ref) runs before the removal - an operation on a removed ref would throw inside CommandBuffer.consume. A drop that arrived BEFORE its death claim (SkyyGear's extra roll when GearDeathMark ran before PickDeathMark) waits in a
  32-slot ring of unclaimed spawns of that world (position + time, refs only) and is picked by the claim the same tick.
  Lag: event-driven only - one map write per break, one map read per item spawn, the death systems visit only dying NPCs and return at
  once while nothing is pending; no tick scan, no file on the world thread (the pool is saved by the private writer, like every deposit);
  the feed push is the HUD's lock-free queue.

NO DUPE, NO LOSS (PickGive.split / undo / settle; the harness proves it for Void full, inventory full, both full and a fault after every
step): the item entity is the source of truth until the end. split books the Void part (SackPool.add) and adds the rest to the inventory
(what really arrived = the container's count of that id after - before); any Throwable takes the inventory part back out
(removeItemStack) and un-books the Void, the entity is untouched (stays where it fell). settle changes the entity LAST and in one step
(remove when nothing is left, else teleport to the feet, then setItemStack(rest)); a failure there undoes the split. A crash (process
death) can only lose the items of the last second (the Void writer / the engine's player save had not run yet) - it can never duplicate
them: the item entity was never saved in a chunk.

REVIEW FIXES (2026-10-13 critic round):
  1. deliver moves NOTHING while SkyySacks has item moves paused for that player (settledKey null: profile switch settling, SkyyProfiles
     crash recovery pending (profile:busy), unreadable pool, shutdown) - the drop stays where it fell (vanilla walk-over pickup), so a
     snapshot reload can never overwrite an auto-picked item (PROFILES-CONTRACT rule 5). Counter 13.
  2. The break claim, the death mark and the killer's share only run while the item hook (PickItemSys) is registered (ITEM_OK) - no
     un-deliverable extra roll lying on the ground when that register failed.
  3. Two claims of the same kind at the SAME exact spot for DIFFERENT players while the first is still unused (two mobs dying in one tick
     at one position) = CONTESTED: neither gets those drops (they stay on the ground, vanilla) - never the wrong player. A used claim
     (its drops already arrived) is simply replaced. Counter 12.
  4. Card text names a split ("Cobblestone > Void + inventory"); "off" route = no pickup sound either; no feed (SkyyHud missing / the push
     refused) on the "feed" route falls back to the rate-limited chat line; the master row is "Auto-pickup (master switch)".

SERVER SETUP (SkyyVoid and Crafting > Auto-pickup, all live): pickup.on, pickup.blocks, pickup.mobs (true), pickup.killerShare (50 %, 0 =
the killer gets nothing extra). New keys only - a file without them uses the defaults (no migration).
Classes: new PickClaim, PickRing, PickBook, PickGive, PickDeliver, PickItemSys, PickBreakSys, PickDeathMark, PickShareSys; SackCfg
(+ PICK_* fields, + pickKeys, ~ reload); the plugin (~ setup: 4 systems, ready line; ~ shutdown); the config kit classes (4 new rows).
Saved data, bridge keys, commands and assets are 0.8.2's. Rollback to 0.8.2: safe (no data written by 0.8.3 that 0.8.2 does not read;
the four config lines stay, unread).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyySacks")
src = os.path.join(HERE, "build_skyysacks_0.8.2.py")
dst = os.path.join(HERE, "build_skyysacks_0.8.3.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.8.2"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"
assert 'VERSION = "0.8.2"' in s and "PickGive" not in s, "not the live generated 0.8.2"
SYS0 = s.count("registerSystem(")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:90]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:90])
    s = s.replace(old, new)


GONE_OK = set()


def gone(*lines):
    for ln in lines:
        GONE_OK.add(ln)


# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''Void rarity (testing / support); lowering never deletes a stored item - only new deposits stop while a category is over its space.
Details: the patch docstring.
"""
''', '''Void rarity (testing / support); lowering never deletes a stored item - only new deposits stop while a category is over its space.
Details: the patch docstring.
0.8.3 (derived from 0.8.2 by tools/sacks_0_8_3_patch.py - edit the patch, not this file; Skyy 2026-10-13 "in hypixle skyblock, items go
straight in your inventory, they never fall on the ground. can we do that too?" + "both. more loot to top damager."): AUTO-PICKUP - block
drops and mob drops go straight to the player (the Void category first, then the inventory, the feet only when both are full), caught
inside the engine's own entity add (never swept from the ground); mob drops to the top damager (SkyyMobs 0.1.7 mob:fn:credit), a different
killer gets pickup.killerShare % of a second roll; island pickup rules respected; SkyyHud feed cards instead of the vanilla pickup popup.
Server Setup > SkyyVoid and Crafting > Auto-pickup. Details: the patch docstring.
"""
''')
rep('VERSION = "0.8.2"\n', 'VERSION = "0.8.3"\n')
gone('VERSION = "0.8.2"')

# ---------------------------------------------------------------------------------------------------------------- engine aliases (jt tokens)
rep('''       "EES": EES, "ICE": ICE, "ACH": ACH, "CBF": CBF, "EVE": EVE, "QRY": QRY}   # 0.7.18: SackInvSys
''', '''       "EES": EES, "ICE": ICE, "ACH": ACH, "CBF": CBF, "EVE": EVE, "QRY": QRY}   # 0.7.18: SackInvSys
# 0.8.3 auto-pickup (tools/sacks_0_8_3_patch.py): the engine classes of the drop hook (VERIFIED against the 0.7.0 HytaleServer.jar)
_JT.update({"ITC": "com.hypixel.hytale.server.core.modules.entity.item.ItemComponent",
            "PIC": "com.hypixel.hytale.server.core.modules.entity.item.PickupItemComponent",
            "TC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
            "RSYS": "com.hypixel.hytale.component.system.RefSystem",
            "ETS": "com.hypixel.hytale.component.system.tick.EntityTickingSystem",
            "ADDR": "com.hypixel.hytale.component.AddReason",
            "REMR": "com.hypixel.hytale.component.RemoveReason",
            "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency",
            "ORD": "com.hypixel.hytale.component.dependency.Order",
            "HLDR": "com.hypixel.hytale.component.Holder",
            "NPCE": "com.hypixel.hytale.server.npc.entities.NPCEntity",
            "ROLE": "com.hypixel.hytale.server.npc.role.Role",
            "DTHC": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
            "DCR": "com.hypixel.hytale.server.core.modules.entity.damage.DeferredCorpseRemoval",
            "ILM": "com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode",
            "DMG": "com.hypixel.hytale.server.core.modules.entity.damage.Damage",
            "DENT": "com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource",
            "UUIDC": "com.hypixel.hytale.server.core.entity.UUIDComponent",
            "BBE": "com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent",
            "V3I": "org.joml.Vector3i",
            "VEC": "org.joml.Vector3d",
            "RTF": "com.hypixel.hytale.math.vector.Rotation3f",
            "IMOD": "com.hypixel.hytale.server.core.modules.item.ItemModule",
            "INVU": "com.hypixel.hytale.server.core.inventory.InventoryUtils",
            "PSET": "com.hypixel.hytale.server.core.modules.entity.player.PlayerSettings",
            "EST": "com.hypixel.hytale.server.core.universe.world.storage.EntityStore",
            "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
            "IST": IST})
''')

# ---------------------------------------------------------------------------------------------------------------- config file template (new files only)
rep('''    "#bags.pocketCraft=true",
''', '''    "#bags.pocketCraft=true",
    "# Auto-pickup (true or false): block drops and mob drops go straight to the player - the Void first, then the inventory,",
    "# the ground at their feet only when both are full. pickup.blocks / pickup.mobs switch the two kinds on their own.",
    "#pickup.on=true",
    "#pickup.blocks=true",
    "#pickup.mobs=true",
    "# Kill credit: the player who did the most damage gets a mob's whole drop. If another player dealt the killing blow, they get",
    "# this percent (0-100) of a second roll of the mob's drop list. 0 = nothing extra for the killer.",
    "#pickup.killerShare=50",
''')

# ---------------------------------------------------------------------------------------------------------------- SackCfg fields + pickKeys + reload
rep('''scfg.addField(CtField.make("public static volatile boolean REFILL_ON = true;", scfg))
''', '''scfg.addField(CtField.make("public static volatile boolean REFILL_ON = true;", scfg))
# 0.8.3 auto-pickup (Server Setup rows pickup.on / pickup.blocks / pickup.mobs / pickup.killerShare; read by the four Pick systems live)
scfg.addField(CtField.make("public static volatile boolean PICK_ON = true;", scfg))
scfg.addField(CtField.make("public static volatile boolean PICK_BLOCKS = true;", scfg))
scfg.addField(CtField.make("public static volatile boolean PICK_MOBS = true;", scfg))
scfg.addField(CtField.make("public static volatile int PICK_SHARE = 50;", scfg))
''')
rep('''# 0.8.0: the live Void settings as one string (SweepTask.cfgSig: a changed row re-sweeps every player once)
''', '''# 0.8.3: the auto-pickup rows from the file (hand edits + the first load); one log line when they change
scfg.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void pickKeys(java.util.Properties p, boolean first) {
  boolean on = boolKey(p, "pickup.on", true);
  boolean bl = boolKey(p, "pickup.blocks", true);
  boolean mo = boolKey(p, "pickup.mobs", true);
  int sh = intKey(p, "pickup.killerShare", 50, 0, 100);
  boolean ch = first || on != PICK_ON || bl != PICK_BLOCKS || mo != PICK_MOBS || sh != PICK_SHARE;
  PICK_ON = on;
  PICK_BLOCKS = bl;
  PICK_MOBS = mo;
  PICK_SHARE = sh;
  if (!ch) return;
  try { if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: auto-pickup " + (on ? "ON (block drops " + (bl ? "on" : "off") + ", mob drops " + (mo ? "on" : "off") + "; top damager gets the drop, a different killer " + sh + " % of a second roll)" : "OFF (pickup.on - drops fall on the ground as in vanilla)")); } catch (Throwable t) { }
}\'\'\'), scfg))
# 0.8.0: the live Void settings as one string (SweepTask.cfgSig: a changed row re-sweeps every player once)
''')
rep('''    pdKeys(p, first);       // 0.8.0: the Void rows (levels, multipliers, gates, costs, Omni)
''', '''    pdKeys(p, first);       // 0.8.0: the Void rows (levels, multipliers, gates, costs, Omni)
    pickKeys(p, first);     // 0.8.3: auto-pickup
''')

# ---------------------------------------------------------------------------------------------------------------- Server Setup rows
rep('''SACK_CFG_CATS = [("craft", "Craft page"), ("bags", "The Void"), ("void", "Void levels"), ("voidcost", "Upgrade costs"),
                 ("benches", "Furnace and Tannery")]''', '''SACK_CFG_CATS = [("craft", "Craft page"), ("bags", "The Void"), ("void", "Void levels"), ("voidcost", "Upgrade costs"),
                 ("benches", "Furnace and Tannery"), ("pickup", "Auto-pickup")]   # 0.8.3: + Auto-pickup''')
gone('''                 ("benches", "Furnace and Tannery")]   # 0.8.0: + the Void rows (the bag caps and free recipes rows are retired)''')
rep('''            "PD_COST_%s_%s" % (c.upper(), PD_RAR[r].upper()), ";check=SackCfg.checkCost")
     for c in PD_CATS for r in (1, 2, 3)]
''', '''            "PD_COST_%s_%s" % (c.upper(), PD_RAR[r].upper()), ";check=SackCfg.checkCost")
     for c in PD_CATS for r in (1, 2, 3)]
# 0.8.3 auto-pickup (all live: the Pick systems read the SackCfg fields on every break / spawn / death). The kill credit rule is the help
# text of the share row (Skyy: "both. more loot to top damager.").
PICK_ROWS = [
    ("pickup.on", "Auto-pickup (master switch)", "pickup", "bool", "true", "", "", "", "", "live",
     "On: block and mob drops go straight to the player - the Void first, then the inventory.",
     "field:SackCfg.PICK_ON@config.properties:pickup.on"),
    ("pickup.blocks", "Auto-pickup: block drops", "pickup", "bool", "true", "", "", "", "", "live",
     "Mined, chopped and harvested blocks, felled trees too. Off: they drop on the ground.",
     "field:SackCfg.PICK_BLOCKS@config.properties:pickup.blocks"),
    ("pickup.mobs", "Auto-pickup: mob drops", "pickup", "bool", "true", "", "", "", "", "live",
     "Mob drops go to the player who did the most damage. Off: they drop on the ground.",
     "field:SackCfg.PICK_MOBS@config.properties:pickup.mobs"),
    ("pickup.killerShare", "Killer's extra share", "pickup", "int", "50", "0", "100", "", "%", "live",
     "Top damager gets the full drop. A different killer gets this % of a second roll. 0 = none.",
     "field:SackCfg.PICK_SHARE@config.properties:pickup.killerShare"),
]
for _r in PICK_ROWS:
    assert len(_r[1]) <= 40 and len(_r[10]) <= 100, (_r[0], len(_r[1]), len(_r[10]))
SACK_CFG_ROWS += PICK_ROWS
''')

# ---------------------------------------------------------------------------------------------------------------- classes
rep('''vac = pool.makeClass(PKG + ".PdAdminCmd", pool.get(APC))
''', '''vac = pool.makeClass(PKG + ".PdAdminCmd", pool.get(APC))
# 0.8.3 auto-pickup (tools/sacks_0_8_3_patch.py docstring)
pcl = pool.makeClass(PKG + ".PickClaim")
prg = pool.makeClass(PKG + ".PickRing")
pbk = pool.makeClass(PKG + ".PickBook")
pgv = pool.makeClass(PKG + ".PickGive")
pdl = pool.makeClass(PKG + ".PickDeliver")
pis = pool.makeClass(PKG + ".PickItemSys", pool.get(_JT["RSYS"]))
pbs = pool.makeClass(PKG + ".PickBreakSys", pool.get(EES))
pdm = pool.makeClass(PKG + ".PickDeathMark", pool.get(_JT["ETS"]))
pss = pool.makeClass(PKG + ".PickShareSys", pool.get(_JT["ETS"]))
''')

PICK = r'''
# ================= 0.8.3 AUTO-PICKUP (tools/sacks_0_8_3_patch.py docstring) =================
for _c, _m in ((_JT["ITC"], "getItemStack"), (_JT["ITC"], "setItemStack"), (_JT["ITC"], "generateItemDrops"), (_JT["TC"], "teleportPosition"),
               (_JT["TC"], "getPosition"), (_JT["BBE"], "getTargetBlock"), (_JT["INVU"], "getContainerForItemPickup"), (_JT["PSET"], "defaults"),
               (_JT["ROLE"], "getDropListId"), (_JT["ROLE"], "hasDroppedDeathItems"), (_JT["ROLE"], "isDropDeathItemsInstantly"),
               (_JT["IMOD"], "getRandomItemDrops"), (_JT["DTHC"], "getDeathInfo"), (_JT["DTHC"], "getItemsLossMode"), (_JT["DCR"], "shouldRemove"),
               (_JT["RSYS"], "onEntityAdded"), (IC, "removeItemStack"), (IC, "addItemStack"), (IS, "withQuantity"), (ST, "removeEntity"),
               (SNDU, "playSoundEvent2dToPlayer"), (_JT["I18N"], "getMessage"), (_JT["ITM"], "getTranslationKey"), (UNI, "getPlayer"),
               (_JT["IMOD"], "isEnabled"), (_JT["IMOD"], "get")):
    B.probe(pool, _c, _m)
for _c in ("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems",
           "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$TickCorpseRemoval",
           "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$CorpseRemoval"):
    pool.get(_c)   # the systems PickDeathMark / PickShareSys order against (looked up again at runtime with Class.forName)

# ---- PickClaim: who gets the items spawning at one exact spot (kind 1 block, 2 mob drop, 3 the killer's share), until exp (nanoTime)
pcl.addField(CtField.make("public java.util.UUID owner;", pcl))
pcl.addField(CtField.make("public long exp;", pcl))
pcl.addField(CtField.make("public int kind;", pcl))
# review fix 3: true once an item matched this claim (its drops arrived) - an unused claim of another player at the same spot = contested
pcl.addField(CtField.make("public volatile boolean used;", pcl))
pcl.addConstructor(CtNewConstructor.make("public PickClaim(java.util.UUID o, long exp, int kind) { this.owner = o; this.exp = exp; this.kind = kind; this.used = false; }", pcl))

# ---- PickDeliver (fields + constructor here: PickBook.mark queues it; accept() comes after PickGive): the cb.run job of one claimed item
pdl.addInterface(pool.get("java.util.function.Consumer"))
pdl.addField(CtField.make(jt("public @REF@ ref;"), pdl))
pdl.addField(CtField.make("public java.util.UUID owner;", pdl))
pdl.addField(CtField.make("public int kind;", pdl))
pdl.addField(CtField.make("public int result;", pdl))
# cb = the CommandBuffer this job was queued on: when it first runs it queues itself AGAIN at the tail of that buffer, so every operation
# another system queued for this item during the same add (systems after ours in the order) runs BEFORE the item may be removed
pdl.addField(CtField.make(jt("public @CBF@ cb;"), pdl))
pdl.addConstructor(CtNewConstructor.make(jt("public PickDeliver(@REF@ ref, java.util.UUID owner, int kind, @CBF@ cb) { this.ref = ref; this.owner = owner; this.kind = kind; this.result = -9; this.cb = cb; }"), pdl))

# ---- PickRing: the last 32 UNCLAIMED item spawns of one world (ref + exact position + nanoTime) - a death claim made after its drops
# arrived (SkyyGear's extra roll when GearDeathMark ran first) takes them from here the same tick. World thread; synchronized methods.
for _f in ("public Object[] refs;", "public double[] xs;", "public double[] ys;", "public double[] zs;", "public long[] at;", "public int pos;"):
    prg.addField(CtField.make(_f, prg))
prg.addField(CtField.make("public static final int SIZE = 32;", prg))
prg.addField(CtField.make("public static final long FRESH_NS = 1000000000L;", prg))
prg.addConstructor(CtNewConstructor.make("public PickRing() { this.refs = new Object[32]; this.xs = new double[32]; this.ys = new double[32]; this.zs = new double[32]; this.at = new long[32]; this.pos = 0; }", prg))
prg.addMethod(CtNewMethod.make(jt(r\'\'\'
public synchronized void push(Object ref, double x, double y, double z, long now) {
  int i = this.pos;
  this.refs[i] = ref;
  this.xs[i] = x;
  this.ys[i] = y;
  this.zs[i] = z;
  this.at[i] = now;
  this.pos = (i + 1) % SIZE;
}\'\'\'), prg))
prg.addMethod(CtNewMethod.make(jt(r\'\'\'
public synchronized java.util.ArrayList take(double x, double y, double z, long now) {
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < SIZE; i++) {
    if (this.refs[i] == null) continue;
    if (now - this.at[i] > FRESH_NS) { this.refs[i] = null; continue; }
    if (this.xs[i] == x && this.ys[i] == y && this.zs[i] == z) { out.add(this.refs[i]); this.refs[i] = null; }
  }
  return out;
}\'\'\'), prg))

# ---- PickBook: the claims, the rings, the deaths already marked, the killer shares waiting, counters, the bridge reads
for _f in ("public static final java.util.concurrent.ConcurrentHashMap CL = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap RINGS = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap SHARE = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.atomic.AtomicLongArray N = new java.util.concurrent.atomic.AtomicLongArray(16);",
           "public static final long CLAIM_NS = 1500000000L;",
           "public static final double SHARE_DY = 0.015625;",
           "public static volatile boolean ITEM_OK = false;",
           "public static volatile boolean BREAK_OK = false;",
           "public static volatile boolean DEATH_OK = false;",
           # harness seams (always null in the game): UUID -> Ref of that player; UUID -> the inventory container; dropListId -> List
           "public static volatile java.util.function.Function PLAYERS;",
           "public static volatile java.util.function.Function INVS;",
           "public static volatile java.util.function.Function ROLLS;",
           # harness seam: (List of stacks, Vector3d) -> Holder[] instead of ItemComponent.generateItemDrops (that one needs the world's
           # GameplayConfig asset for the item lifetime); the engine call is used whenever this is null (always in the game)
           "public static volatile java.util.function.BiFunction SPAWN;"):
    pbk.addField(CtField.make(_f, pbk))
# counters N: 0 block claims, 1 mob claims, 2 killer shares spawned, 3 drops delivered, 4 items to the Void, 5 items to the inventory,
# 6 items left at the feet, 7 refused by island rules, 8 rolled back, 9 late matches (ring), 10 felled-log claims, 11 owner not here,
# 12 contested claims (review fix 3), 13 skipped while item moves are paused for that player (review fix 1)
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void n(int i, long v) { N.addAndGet(i, v); }\'\'\'), pbk))
# one log line per kind of failure (0.8.2's KnowSync.warnOnce is one line per MINUTE for all messages together); LAST = the newest
pbk.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();", pbk))
pbk.addField(CtField.make("public static volatile String LAST = null;", pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void warnOnce(String key, String msg) {
  LAST = msg;
  if (WARNED.putIfAbsent(key, Boolean.TRUE) == null) @PKG@.SackPool.warn(msg);
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static Class cls(String n) {
  try { return Class.forName(n); } catch (Throwable t) { return null; }
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String world(Object ext) {
  try {
    if (!(ext instanceof @EST@)) return null;
    @WLD@ w = ((@EST@) ext).getWorld();
    return w == null ? null : w.getName();
  } catch (Throwable t) { return null; }
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String key(String w, double x, double y, double z) { return w + "|" + x + "|" + y + "|" + z; }\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void prune(long now) {
  Object[] ks = CL.keySet().toArray();
  for (int i = 0; i < ks.length; i++) {
    @PKG@.PickClaim c = (@PKG@.PickClaim) CL.get(ks[i]);
    if (c != null && now - c.exp > 0L) CL.remove(ks[i]);
  }
  if (DONE.size() > 512) DONE.clear();
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @PKG@.PickClaim claim(String w, double x, double y, double z, java.util.UUID o, int kind, long now) {
  if (w == null || o == null) return null;
  if (CL.size() > 256) prune(now);
  String k = key(w, x, y, z);
  @PKG@.PickClaim c = new @PKG@.PickClaim(o, now + CLAIM_NS, kind);
  if (kind != 1) {
    @PKG@.PickClaim old = (@PKG@.PickClaim) CL.get(k);
    if (old != null && old.kind == kind && !old.used && now - old.exp <= 0L && (old.owner == null || !old.owner.equals(o))) {
      c = new @PKG@.PickClaim(null, now + CLAIM_NS, kind);
      n(12, 1L);
    }
  }
  CL.put(k, c);
  return c;
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @PKG@.PickClaim find(String w, double x, double y, double z, long now) {
  if (w == null || CL.isEmpty()) return null;
  String k = key(w, x, y, z);
  @PKG@.PickClaim c = (@PKG@.PickClaim) CL.get(k);
  if (c == null) return null;
  if (now - c.exp > 0L) { CL.remove(k); return null; }
  return c;
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @PKG@.PickRing ring(String w) {
  if (w == null) return null;
  @PKG@.PickRing r = (@PKG@.PickRing) RINGS.get(w);
  if (r == null) {
    r = new @PKG@.PickRing();
    Object had = RINGS.putIfAbsent(w, r);
    if (had != null) r = (@PKG@.PickRing) had;
  }
  return r;
}\'\'\'), pbk))
# a block drop spot: x and z at .5, y whole (spawnDrops = block + (0.5, 0, 0.5))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean blockSpot(double x, double y, double z) {
  return x - Math.floor(x) == 0.5 && z - Math.floor(z) == 0.5 && y == Math.floor(y);
}\'\'\'), pbk))
# a felled-tree drop: SkyySkills skill:fn:felledBy names the player whose cut is felling (or felled, within a minute) that block
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.UUID felled(String w, double x, double y, double z) {
  Object f = @PKG@.SackPool.bridge().get("skill:fn:felledBy");
  if (!(f instanceof java.util.function.Function) || w == null) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { w, Integer.valueOf((int) Math.floor(x)), Integer.valueOf((int) Math.floor(y)), Integer.valueOf((int) Math.floor(z)) });
    if (!(r instanceof Object[])) return null;
    Object[] a = (Object[]) r;
    if (a.length < 1 || !(a[0] instanceof java.util.UUID)) return null;
    if (a.length > 2 && a[2] instanceof Long && System.currentTimeMillis() - ((Long) a[2]).longValue() > 60000L) return null;
    return (java.util.UUID) a[0];
  } catch (Throwable t) { return null; }
}\'\'\'), pbk))
# the Ref of an online player IN THIS store (null = offline / another world)
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @REF@ here(java.util.UUID u, @ST@ st) {
  if (u == null || st == null) return null;
  try {
    @REF@ r = null;
    java.util.function.Function pf = PLAYERS;
    if (pf != null) r = (@REF@) pf.apply(u);
    else {
      @PR@ pr = @UNI@.get().getPlayer(u);
      r = pr == null ? null : pr.getReference();
    }
    if (r == null || !r.isValid() || r.getStore() != st) return null;
    return r;
  } catch (Throwable t) { return null; }
}\'\'\'), pbk))
# SkyyMobs 0.1.7 mob:fn:credit (take): Object[] { top, topDamage, total, killing blow, players } or null
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.UUID top(String mob) {
  Object f = @PKG@.SackPool.bridge().get("mob:fn:credit");
  if (!(f instanceof java.util.function.Function) || mob == null) return null;
  try {
    Object r = ((java.util.function.Function) f).apply(new Object[] { mob, Boolean.TRUE });
    if (!(r instanceof Object[]) || ((Object[]) r).length < 1 || !(((Object[]) r)[0] instanceof String)) return null;
    return java.util.UUID.fromString((String) ((Object[]) r)[0]);
  } catch (Throwable t) { return null; }
}\'\'\'), pbk))
# THE KILL CREDIT RULE (pure): Object[] { owner of the whole drop, killer who gets the extra share or null }; null = nobody (vanilla)
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static Object[] split(java.util.UUID killer, java.util.UUID top, int sharePct) {
  java.util.UUID owner = top != null ? top : killer;
  if (owner == null) return null;
  java.util.UUID extra = (killer != null && top != null && !killer.equals(top) && sharePct > 0) ? killer : null;
  return new Object[] { owner, extra };
}\'\'\'), pbk))
# the killer's share of one roll: every stack x pct / 100, the fraction rounds up with that chance (u01 = one uniform draw per stack)
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.ArrayList scale(java.util.List rolled, int pct, java.util.Random rnd) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (rolled == null || pct <= 0) return out;
  for (int i = 0; i < rolled.size(); i++) {
    Object o = rolled.get(i);
    if (!(o instanceof @IS@)) continue;
    @IS@ s = (@IS@) o;
    if (s.isEmpty() || s.getItemId() == null || s.getQuantity() <= 0) continue;
    double want = (double) s.getQuantity() * (double) (pct > 100 ? 100 : pct) / 100.0;
    int q = (int) Math.floor(want);
    if (rnd.nextDouble() < want - (double) q) q++;
    if (q > 0) out.add(s.withQuantity(q));
  }
  return out;
}\'\'\'), pbk))
# the death mark (PickDeathMark, the tick DropDeathItems drops): claim position + (0, 1, 0) for the owner of the drop, take drops that
# already arrived (the ring) and note the killer's share for PickShareSys. Returns the owner (null = none).
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.UUID mark(@ST@ st, @CBF@ cb, String w, double x, double y, double z, String mob, java.util.UUID killer, long now) {
  if (w == null || mob == null) return null;
  long ms = System.currentTimeMillis();
  Long seen = (Long) DONE.get(mob);
  if (seen != null && ms - seen.longValue() < 10000L) return null;
  DONE.put(mob, Long.valueOf(ms));
  java.util.UUID t = top(mob);
  if (t != null && here(t, st) == null) t = null;
  java.util.UUID k = killer != null && here(killer, st) != null ? killer : null;
  Object[] sp = split(k, t, @PKG@.SackCfg.PICK_SHARE);
  if (sp == null) return null;
  java.util.UUID owner = (java.util.UUID) sp[0];
  @PKG@.PickClaim cl = claim(w, x, y, z, owner, 2, now);
  n(1, 1L);
  if (sp[1] != null) SHARE.put(mob, sp[1]);
  if (cl == null || cl.owner == null) return null;
  @PKG@.PickRing r = (@PKG@.PickRing) RINGS.get(w);
  if (r != null) {
    java.util.ArrayList late = r.take(x, y, z, now);
    if (!late.isEmpty()) cl.used = true;
    for (int i = 0; i < late.size(); i++) { cb.run(new @PKG@.PickDeliver((@REF@) late.get(i), owner, 2, cb)); n(9, 1L); }
  }
  return owner;
}\'\'\'), pbk))
# the killer's share (PickShareSys, after DropDeathItems): a second roll of the drop list x pickup.killerShare %, spawned like vanilla at
# position + (0, 1 + 1/64, 0) with the killer's claim (SkyyGear's GearDropSys converts its gear: within 2 blocks of its mark). Returns stacks.
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int share(@ST@ st, @CBF@ cb, String w, double x, double y, double z, String mob, String dropList, long now) {
  Object k = mob == null ? null : SHARE.remove(mob);
  if (!(k instanceof java.util.UUID) || dropList == null || w == null) return 0;
  java.util.List rolled = null;
  java.util.function.Function rf = ROLLS;
  if (rf != null) rolled = (java.util.List) rf.apply(dropList);
  else if (@IMOD@.get() != null && @IMOD@.get().isEnabled()) rolled = @IMOD@.get().getRandomItemDrops(dropList);
  java.util.ArrayList out = scale(rolled, @PKG@.SackCfg.PICK_SHARE, java.util.concurrent.ThreadLocalRandom.current());
  if (out.isEmpty()) return 0;
  double sy = y + SHARE_DY;
  claim(w, x, sy, z, (java.util.UUID) k, 3, now);   // contested (another share at this spot this tick) = those items stay on the ground
  java.util.function.BiFunction sf = SPAWN;
  @HLDR@[] hs = sf != null ? (@HLDR@[]) sf.apply(out, new @VEC@(x, sy, z)) : @ITC@.generateItemDrops(st, out, new @VEC@(x, sy, z), @RTF@.IDENTITY);
  if (hs == null || hs.length == 0) return 0;
  cb.addEntities(hs, @ADDR@.SPAWN);
  n(2, 1L);
  return out.size();
}\'\'\'), pbk))
# a new item entity (PickItemSys.onEntityAdded): the claim at its exact spot (else a felled log), or into the ring
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @PKG@.PickClaim match(String w, double x, double y, double z, @REF@ ref, long now) {
  @PKG@.PickClaim c = find(w, x, y, z, now);
  if (c == null && @PKG@.SackCfg.PICK_BLOCKS && blockSpot(x, y, z)) {
    java.util.UUID f = felled(w, x, y, z);
    if (f != null) { c = new @PKG@.PickClaim(f, now + CLAIM_NS, 1); n(10, 1L); }
  }
  if (c != null && c.owner == null) { n(12, 1L); return null; }   // contested spot: nobody gets it (review fix 3)
  if (c != null && ((c.kind == 1 && !@PKG@.SackCfg.PICK_BLOCKS) || (c.kind != 1 && !@PKG@.SackCfg.PICK_MOBS))) return null;
  if (c != null) c.used = true;
  if (c == null && @PKG@.SackCfg.PICK_MOBS && ref != null) {
    @PKG@.PickRing r = ring(w);
    if (r != null) r.push(ref, x, y, z, now);
  }
  return c;
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String state() {
  if (!@PKG@.SackCfg.PICK_ON) return "OFF (pickup.on)";
  return "on (block drops " + (BREAK_OK && ITEM_OK && @PKG@.SackCfg.PICK_BLOCKS ? "on" : "OFF") + ", mob drops "
    + (DEATH_OK && ITEM_OK && @PKG@.SackCfg.PICK_MOBS ? "on" : "OFF") + ", killer share " + @PKG@.SackCfg.PICK_SHARE + " %, kill credit "
    + (@PKG@.SackPool.bridge().get("mob:fn:credit") instanceof java.util.function.Function ? "SkyyMobs" : "killer only (no mob:fn:credit yet)") + ")";
}\'\'\'), pbk))
pbk.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String stats() {
  return "claims " + N.get(0) + " block / " + N.get(1) + " mob / " + N.get(10) + " felled, " + N.get(3) + " drops delivered (" + N.get(4)
    + " items to the Void, " + N.get(5) + " to inventories, " + N.get(6) + " at feet), " + N.get(2) + " killer shares, " + N.get(9)
    + " late, " + N.get(7) + " refused by island rules, " + N.get(11) + " owner gone, " + N.get(13) + " paused (profile settling), "
    + N.get(12) + " contested, " + N.get(8) + " rolled back";
}\'\'\'), pbk))

# ---- PickGive: the split (Void -> inventory -> feet), its undo, the entity update, the feed card / sound
for _f in ("public static volatile int FAULT = 0;",   # harness only: 1 after the Void booking, 2 after the inventory add, 3 before the entity update
           "public static final java.util.concurrent.ConcurrentHashMap NAMES = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap PERM = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap SND = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap CHAT = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap FULL = new java.util.concurrent.ConcurrentHashMap();"):
    pgv.addField(CtField.make(_f, pgv))
# what the Void takes of this stack now (0 = none): the /pd Deposit rule - a plain stack, a category (catOf), the category's free space
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long voidRoom(java.util.UUID u, String k, @IS@ s) {
  if (u == null || k == null || s == null || s.isEmpty() || s.getItemId() == null) return 0L;
  if (s.getItemId().startsWith("Skyy_Sack_") || !@PKG@.SweepTask.plainFresh(s)) return 0L;
  String cat = @PKG@.SackDefs.catOf(s.getItemId());
  if (cat == null) return 0L;
  int ci = @PKG@.SackDefs.catIndex(cat);
  if (ci < 0) return 0L;
  Integer cc = (Integer) @PKG@.VoidStore.capsK(u, k).get(cat);
  if (cc == null) return 0L;
  long room = cc.longValue() - @PKG@.VoidStore.usedAll(k)[ci];
  return room > 0L ? room : 0L;
}\'\'\'), pgv))
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long countId(@IC@ inv, String id) {
  long t = 0L;
  if (inv == null || id == null) return 0L;
  int cap = (int) inv.getCapacity();
  for (int i = 0; i < cap; i++) {
    @IS@ it = inv.getItemStack((short) i);
    if (it != null && !it.isEmpty() && id.equals(it.getItemId())) t += (long) it.getQuantity();
  }
  return t;
}\'\'\'), pgv))
# take back what one split did (Throwable anywhere after it): the inventory part out again, the Void booking undone
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void undo(String k, @IS@ s, @IC@ inv, long v, long i) {
  if (i > 0L && inv != null) {
    try { inv.removeItemStack(s.withQuantity((int) i)); }
    catch (Throwable t) { @PKG@.SackPool.warn("auto-pickup rollback could not take " + i + " " + s.getItemId() + " back out of an inventory: " + t); }
  }
  if (v > 0L && k != null) @PKG@.SackPool.add(k, s.getItemId(), -v);
  @PKG@.PickBook.n(8, 1L);
}\'\'\'), pgv))
# THE SPLIT: Void first (booked), then the inventory; long[] { to the Void, to the inventory, left over } or null = nothing moved
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long[] split(java.util.UUID u, String k, @IS@ s, @IC@ inv) {
  if (s == null || s.isEmpty() || s.getItemId() == null || s.getQuantity() <= 0) return null;
  String id = s.getItemId();
  int total = s.getQuantity();
  long room = voidRoom(u, k, s);
  long toVoid = room < (long) total ? room : (long) total;
  long booked = 0L;
  long toInv = 0L;
  try {
    if (toVoid > 0L) { @PKG@.SackPool.add(k, id, toVoid); booked = toVoid; }
    if (FAULT == 1) throw new IllegalStateException("harness fault 1 (after the Void booking)");
    long rest = (long) total - toVoid;
    if (rest > 0L && inv != null) {
      long before = countId(inv, id);
      try { inv.addItemStack(s.withQuantity((int) rest)); }
      finally { toInv = countId(inv, id) - before; }
      if (toInv < 0L) toInv = 0L;
      if (toInv > rest) throw new IllegalStateException("the inventory gained " + toInv + " of " + id + " but only " + rest + " were given");
    }
    if (FAULT == 2) throw new IllegalStateException("harness fault 2 (after the inventory add)");
    return new long[] { toVoid, toInv, (long) total - toVoid - toInv };
  } catch (Throwable t) {
    undo(k, s, inv, booked, toInv);
    @PKG@.SackPool.warn("auto-pickup of " + total + " " + id + " failed and was rolled back (the drop stays where it fell): " + t);
    return null;
  }
}\'\'\'), pgv))
# the entity after the split - LAST and in one step: nothing left = removed; else moved to the feet, then the rest set
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static void settle(@ST@ st, @REF@ item, @ITC@ ic, @IS@ s, long left, @VEC@ feet) {
  if (left <= 0L) { st.removeEntity(item, @REMR@.REMOVE); return; }
  if (feet != null) {
    @TC@ tc = (@TC@) st.getComponent(item, @TC@.getComponentType());
    if (tc != null) tc.teleportPosition(feet);
  }
  if (left != (long) s.getQuantity()) ic.setItemStack(s.withQuantity((int) left));
}\'\'\'), pgv))
# SkyyIslands' pickup rule for this player in this world (island:perm:fn "pickup"; null / no SkyyIslands = allowed), cached 5 s
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean denied(java.util.UUID u, String w) {
  if (u == null || w == null) return false;
  Object f = @PKG@.SackPool.bridge().get("island:perm:fn");
  if (!(f instanceof java.util.function.Function)) return false;
  String key = u.toString() + "|" + w;
  long now = System.currentTimeMillis();
  Object[] c = (Object[]) PERM.get(key);
  if (c != null && now - ((Long) c[1]).longValue() < 5000L) return Boolean.FALSE.equals(c[0]);
  Object r = null;
  try { r = ((java.util.function.Function) f).apply(new Object[] { u, w, "pickup" }); } catch (Throwable t) { r = null; }
  if (PERM.size() > 1024) PERM.clear();
  PERM.put(key, new Object[] { r instanceof Boolean ? r : Boolean.TRUE, Long.valueOf(now) });
  return Boolean.FALSE.equals(r);
}\'\'\'), pgv))
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String name(String id) {
  if (id == null) return "";
  Object c = NAMES.get(id);
  if (c instanceof String) return (String) c;
  String n = null;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (o instanceof @ITM@) {
      String tk = ((@ITM@) o).getTranslationKey();
      @I18N@ m = @I18N@.get();
      if (tk != null && m != null) {
        n = m.getMessage("en-US", tk);
        if ((n == null || n.length() == 0) && tk.startsWith("server.")) n = m.getMessage("en-US", tk.substring(7));
      }
    }
  } catch (Throwable t) { n = null; }
  if (n == null || n.length() == 0 || n.indexOf('.') > 0 && n.indexOf(' ') < 0) n = id.startsWith("Skyy_Unid") ? "Unidentified item" : @PKG@.SacksPage.pretty(id);
  if (NAMES.size() < 4096) NAMES.put(id, n);
  return n;
}\'\'\'), pgv))
# the card text: where it went
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String text(String nm, long[] r, int qty) {
  String t;
  if (r[2] > 0L) t = nm + " - full, at your feet";
  else if (r[0] >= (long) qty) t = nm + " > Void";
  else if (r[0] > 0L) t = nm + " > Void + inventory";
  else t = nm;
  return t.length() > 48 ? t.substring(0, 48) : t;
}\'\'\'), pgv))
# feed card (SkyyHud feed:fn:push, kind "pickup" = the player's "Item pickups" route) / chat fallback / sound; never throws
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int tell(java.util.UUID u, @PR@ pr, String id, int qty, long[] r) {
  int how = 0;
  try {
    java.util.Map b = @PKG@.SackPool.bridge();
    String route = "feed";
    Object rf = b.get("msgroute:fn:get");
    if (rf instanceof java.util.function.Function) {
      Object v = ((java.util.function.Function) rf).apply(new Object[] { u, "pickup" });
      if (v instanceof String) route = (String) v;
    }
    String txt = text(name(id), r, qty);
    long now = System.currentTimeMillis();
    if (route.equals("feed")) {
      Object ff = b.get("feed:fn:push");
      if (ff instanceof java.util.function.Function && Boolean.TRUE.equals(((java.util.function.Function) ff).apply(new Object[] { u, "pickup", id, txt, Long.valueOf((long) qty) }))) how = 1;
      else route = "chat";   // review fix: no SkyyHud / the push refused -> the rate-limited chat line, never silent
    }
    if (route.equals("chat") && pr != null) {
      Long last = (Long) CHAT.get(u);
      if (last == null || now - last.longValue() >= 3000L) { CHAT.put(u, Long.valueOf(now)); pr.sendMessage(@MSG@.raw("+" + qty + " " + txt).color("#b7cedd")); how = 2; }
    }
    if (how != 1 && r[2] > 0L && pr != null) {
      Long lf = (Long) FULL.get(u);
      if (lf == null || now - lf.longValue() >= 30000L) { FULL.put(u, Long.valueOf(now)); pr.sendMessage(@MSG@.raw("Your Void and inventory are full - drops land at your feet.").color("#ffcc00")); how = how | 4; }
    }
    if (pr != null && !route.equals("off")) {   // review fix: "Item pickups: Off" = no sound either
      Long ls = (Long) SND.get(u);
      if (ls == null || now - ls.longValue() >= 120L) { SND.put(u, Long.valueOf(now)); @SNDU@.playSoundEvent2dToPlayer(pr, "SFX_Player_Pickup_Item", @SCAT@.UI); }
    }
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick1", "auto-pickup feed / sound failed (logged once): " + t); }
  return how;
}\'\'\'), pgv))
# the vanilla pickup container of that player for this item (= Player.giveItem's), else the storage
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @IC@ pickInv(@ST@ st, @REF@ pref, @IS@ s) {
  java.util.function.Function f = @PKG@.PickBook.INVS;
  if (f != null) return (@IC@) f.apply(pref);
  try {
    @PSET@ ps = (@PSET@) st.getComponent(pref, @PSET@.getComponentType());
    if (ps == null) ps = @PSET@.defaults();
    @IC@ c = @INVU@.getContainerForItemPickup(pref, s.getItem(), ps, st);
    if (c != null) return c;
  } catch (Throwable t) { }
  try {
    @PLA@ p = (@PLA@) st.getComponent(pref, @PLA@.getComponentType());
    return p == null || p.getInventory() == null ? null : p.getInventory().getStorage();
  } catch (Throwable t2) { return null; }
}\'\'\'), pgv))
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static @VEC@ feetOf(@ST@ st, @REF@ pref) {
  try {
    @TC@ tc = (@TC@) st.getComponent(pref, @TC@.getComponentType());
    return tc == null || tc.getPosition() == null ? null : new @VEC@(tc.getPosition());
  } catch (Throwable t) { return null; }
}\'\'\'), pgv))
# ONE claimed item entity -> its player (runs when the add's CommandBuffer is consumed; world thread). Returns 1 all delivered, 2 part at
# the feet, 3 all at the feet, -1 refused (island rules), 0 nothing moved (the drop stays as it fell)
pgv.addMethod(CtNewMethod.make(jt(r\'\'\'
public static int deliver(@ST@ st, @REF@ item, java.util.UUID owner, int kind) {
  try {
    if (st == null || item == null || !item.isValid() || owner == null || !@PKG@.SackCfg.PICK_ON) return 0;
    @ITC@ ic = (@ITC@) st.getComponent(item, @ITC@.getComponentType());
    if (ic == null) return 0;
    @IS@ s = ic.getItemStack();
    if (s == null || s.isEmpty() || s.getItemId() == null || s.getQuantity() <= 0) return 0;
    @REF@ pref = @PKG@.PickBook.here(owner, st);
    if (pref == null) { @PKG@.PickBook.n(11, 1L); return 0; }
    if (denied(owner, @PKG@.PickBook.world(st.getExternalData()))) { @PKG@.PickBook.n(7, 1L); return -1; }
    String k = @PKG@.SackPool.settledKey(owner);
    // review fix 1: item moves paused for this player (profile switch settling / crash recovery pending / pool unreadable / shutdown)
    // -> move nothing: a snapshot reload could overwrite an inventory add; the drop stays where it fell
    if (k == null) { @PKG@.PickBook.n(13, 1L); return 0; }
    try { @PKG@.BagMirror.beforeTake(k); } catch (Throwable tb) { }
    @IC@ inv = pickInv(st, pref, s);
    long[] r = split(owner, k, s, inv);
    if (r == null) return 0;
    @VEC@ feet = r[2] > 0L ? feetOf(st, pref) : null;
    try {
      if (FAULT == 3) throw new IllegalStateException("harness fault 3 (before the entity update)");
      settle(st, item, ic, s, r[2], feet);
    } catch (Throwable te) {
      undo(k, s, inv, r[0], r[1]);
      @PKG@.SackPool.warn("auto-pickup could not update the dropped " + s.getItemId() + " - rolled back, the drop stays where it fell: " + te);
      return 0;
    }
    if (r[0] > 0L) {
      @PKG@.VoidStore.noteIntake(k, @PKG@.SackDefs.catIndex(@PKG@.SackDefs.catOf(s.getItemId())), r[0]);
      try { @PKG@.SackPool.saveSoon(k); } catch (Throwable ts) { @PKG@.SackPool.DIRTY.put(k, Boolean.TRUE); }
    }
    @PKG@.PickBook.n(3, 1L);
    @PKG@.PickBook.n(4, r[0]);
    @PKG@.PickBook.n(5, r[1]);
    @PKG@.PickBook.n(6, r[2]);
    @PR@ pr = null;
    try { pr = (@PR@) st.getComponent(pref, @PR@.getComponentType()); } catch (Throwable tp) { pr = null; }
    tell(owner, pr, s.getItemId(), s.getQuantity(), r);
    if (r[2] <= 0L) return 1;
    return r[0] + r[1] > 0L ? 2 : 3;
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick2", "auto-pickup failed (logged once; drops stay on the ground): " + t); return 0; }
}\'\'\'), pgv))

# ---- PickDeliver: the cb.run job of one claimed item (Consumer<Store>)
pdl.addMethod(CtNewMethod.make(jt(r\'\'\'
public void accept(Object o) {
  @CBF@ c = this.cb;
  if (c != null) {
    this.cb = null;
    try { c.run(this); return; } catch (Throwable t) { }
  }
  if (o instanceof @ST@) this.result = @PKG@.PickGive.deliver((@ST@) o, this.ref, this.owner, this.kind);
}\'\'\'), pdl))

# ---- PickItemSys: RefSystem on ItemComponent + TransformComponent - a new item at a claimed spot -> ONE PickDeliver on the add's buffer
pis.addField(CtField.make(jt("public @QRY@ query;"), pis))
pis.addConstructor(CtNewConstructor.make("public PickItemSys() { super(); this.query = null; }", pis))
pis.addMethod(CtNewMethod.make(jt(r\'\'\'
public @QRY@ getQuery() {
  if (this.query == null) this.query = @QRY@.and(new @QRY@[] { (@QRY@) @ITC@.getComponentType(), (@QRY@) @TC@.getComponentType() });
  return this.query;
}\'\'\'), pis))
pis.addMethod(CtNewMethod.make(jt(r\'\'\'
public void onEntityAdded(@REF@ ref, @ADDR@ reason, @ST@ st, @CBF@ cb) {
  try {
    if (!@PKG@.SackCfg.PICK_ON || reason != @ADDR@.SPAWN) return;
    if (!@PKG@.SackCfg.PICK_BLOCKS && !@PKG@.SackCfg.PICK_MOBS) return;
    if (st.getComponent(ref, @PIC@.getComponentType()) != null) return;
    @TC@ tc = (@TC@) st.getComponent(ref, @TC@.getComponentType());
    if (tc == null || tc.getPosition() == null) return;
    @VEC@ p = tc.getPosition();
    @PKG@.PickClaim c = @PKG@.PickBook.match(@PKG@.PickBook.world(st.getExternalData()), p.x, p.y, p.z, ref, System.nanoTime());
    if (c == null) return;
    cb.run(new @PKG@.PickDeliver(ref, c.owner, c.kind, cb));
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick3", "auto-pickup: item spawn check failed (logged once): " + t); }
}\'\'\'), pis))
pis.addMethod(CtNewMethod.make(jt("public void onEntityRemove(@REF@ ref, @REMR@ reason, @ST@ st, @CBF@ cb) { }"), pis))

# ---- PickBreakSys: BreakBlockEvent on a player -> claim block + (0.5, 0, 0.5) for them (the drops spawn right after, same thread)
pbs.addConstructor(CtNewConstructor.make(jt("public PickBreakSys() { super(@BBE@.class); }"), pbs))
pbs.addMethod(CtNewMethod.make(jt("public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }"), pbs))
pbs.addMethod(CtNewMethod.make(jt(r\'\'\'
public void handle(int idx, @ACH@ chunk, @ST@ st, @CBF@ buf, @EVE@ ev) {
  try {
    if (!@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_BLOCKS || !@PKG@.PickBook.ITEM_OK || !(ev instanceof @BBE@)) return;
    @BBE@ e = (@BBE@) ev;
    if (e.isCancelled()) return;
    @V3I@ b = e.getTargetBlock();
    if (b == null) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null || pr.getUuid() == null) return;
    @PKG@.PickBook.claim(@PKG@.PickBook.world(st.getExternalData()), (double) b.x() + 0.5, (double) b.y(), (double) b.z() + 0.5, pr.getUuid(), 1, System.nanoTime());
    @PKG@.PickBook.n(0, 1L);
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick4", "auto-pickup: block break claim failed (logged once): " + t); }
}\'\'\'), pbs))

# ---- the two death systems (EntityTickingSystem NPCEntity + DeathComponent; only dying NPCs are visited)
def _dsys(cls, name, first, second):
    """first / second = (Order, static Class field) of the two SystemDependency edges"""
    for f in ("public static Class DDI;", "public static Class TCR;", "public static Class CR;", "public java.util.Set deps;"):
        cls.addField(CtField.make(f, cls))
    cls.addConstructor(CtNewConstructor.make(jt(r\'\'\'
public %s() {
  super();
  this.deps = new java.util.HashSet();
  this.deps.add(new @SDEP@(@ORD@.%s, %s));
  this.deps.add(new @SDEP@(@ORD@.%s, %s));
}\'\'\' % (name, first[0], first[1], second[0], second[1])), cls))
    cls.addMethod(CtNewMethod.make(jt("public @QRY@ getQuery() { return @QRY@.and(new @QRY@[] { (@QRY@) @NPCE@.getComponentType(), (@QRY@) @DTHC@.getComponentType() }); }"), cls))
    cls.addMethod(CtNewMethod.make("public java.util.Set getDependencies() { return this.deps; }", cls))
    cls.addMethod(CtNewMethod.make("public boolean isParallel(int a, int b) { return false; }", cls))
_dsys(pdm, "PickDeathMark", ("AFTER", "TCR"), ("BEFORE", "DDI"))
_dsys(pss, "PickShareSys", ("AFTER", "DDI"), ("BEFORE", "CR"))
# the DropDeathItems condition, copied (0.7 bytecode; SkyyGear's GearDeathMark): items-loss mode ALL, a role that has not dropped yet,
# dropping instantly or with a DeferredCorpseRemoval that is due (or none), not a player
pdm.addMethod(CtNewMethod.make(jt(r\'\'\'
public static boolean dropsNow(@ACH@ chunk, int idx) {
  @DTHC@ dc = (@DTHC@) chunk.getComponent(idx, @DTHC@.getComponentType());
  if (dc == null || dc.getItemsLossMode() != @ILM@.ALL) return false;
  @NPCE@ npc = (@NPCE@) chunk.getComponent(idx, @NPCE@.getComponentType());
  if (npc == null) return false;
  @ROLE@ role = npc.getRole();
  if (role == null || role.hasDroppedDeathItems()) return false;
  if (!role.isDropDeathItemsInstantly()) {
    @DCR@ dcr = (@DCR@) chunk.getComponent(idx, @DCR@.getComponentType());
    if (dcr != null && !dcr.shouldRemove()) return false;
  }
  return chunk.getComponent(idx, @PLA@.getComponentType()) == null;
}\'\'\'), pdm))
# the killer: Damage$EntitySource (a projectile's = its shooter) whose ref is a player in the SAME store
pdm.addMethod(CtNewMethod.make(jt(r\'\'\'
public static java.util.UUID killer(@DTHC@ dc, @ST@ st) {
  try {
    @DMG@ d = dc == null ? null : dc.getDeathInfo();
    if (d == null || !(d.getSource() instanceof @DENT@)) return null;
    @REF@ r = ((@DENT@) d.getSource()).getRef();
    if (r == null || !r.isValid() || r.getStore() != st) return null;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    return pr == null ? null : pr.getUuid();
  } catch (Throwable t) { return null; }
}\'\'\'), pdm))
pdm.addMethod(CtNewMethod.make(jt(r\'\'\'
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CBF@ cb) {
  try {
    if (!@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_MOBS || !@PKG@.PickBook.ITEM_OK || !dropsNow(chunk, idx)) return;
    @TC@ tc = (@TC@) chunk.getComponent(idx, @TC@.getComponentType());
    @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
    if (tc == null || tc.getPosition() == null || uc == null || uc.getUuid() == null) return;
    @VEC@ p = tc.getPosition();
    @DTHC@ dc = (@DTHC@) chunk.getComponent(idx, @DTHC@.getComponentType());
    @PKG@.PickBook.mark(st, cb, @PKG@.PickBook.world(st.getExternalData()), p.x, p.y + 1.0, p.z, uc.getUuid().toString(), killer(dc, st), System.nanoTime());
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick5", "auto-pickup: death mark failed (logged once; that mob's drops stay on the ground): " + t); }
}\'\'\'), pdm))
pss.addMethod(CtNewMethod.make(jt(r\'\'\'
public void tick(float dt, int idx, @ACH@ chunk, @ST@ st, @CBF@ cb) {
  try {
    if (@PKG@.PickBook.SHARE.isEmpty()) return;
    @UUIDC@ uc = (@UUIDC@) chunk.getComponent(idx, @UUIDC@.getComponentType());
    if (uc == null || uc.getUuid() == null || !@PKG@.PickBook.SHARE.containsKey(uc.getUuid().toString())) return;
    String mob = uc.getUuid().toString();
    @NPCE@ npc = (@NPCE@) chunk.getComponent(idx, @NPCE@.getComponentType());
    @TC@ tc = (@TC@) chunk.getComponent(idx, @TC@.getComponentType());
    if (npc == null || npc.getRole() == null || tc == null || tc.getPosition() == null || !@PKG@.SackCfg.PICK_ON || !@PKG@.SackCfg.PICK_MOBS || !@PKG@.PickBook.ITEM_OK) { @PKG@.PickBook.SHARE.remove(mob); return; }
    @VEC@ p = tc.getPosition();
    @PKG@.PickBook.share(st, cb, @PKG@.PickBook.world(st.getExternalData()), p.x, p.y + 1.0, p.z, mob, npc.getRole().getDropListId(), System.nanoTime());
  } catch (Throwable t) { @PKG@.PickBook.warnOnce("pick6", "auto-pickup: killer share failed (logged once): " + t); }
}\'\'\'), pss))

'''
PICK = PICK.replace(chr(92) + "'" + chr(92) + "'" + chr(92) + "'", "'" * 3)
rep('''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))''', PICK.lstrip("\n") + '''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))''')

# ---------------------------------------------------------------------------------------------------------------- plugin setup / shutdown
rep('''  catch (Throwable te) {{ {PKG}.SweepTask.EVENTS_OK = false; {PKG}.SackPool.warn("inventory-change listener not registered - every player is swept every 2 s (0.7.17): " + te); }}
''', '''  catch (Throwable te) {{ {PKG}.SweepTask.EVENTS_OK = false; {PKG}.SackPool.warn("inventory-change listener not registered - every player is swept every 2 s (0.7.17): " + te); }}
  // 0.8.3 AUTO-PICKUP (tools/sacks_0_8_3_patch.py): ONE registerSystem per class; a system that cannot register leaves that kind of drop
  // on the ground (vanilla) - never an unordered death system (it could miss the drop tick or claim another mob's spot)
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickItemSys()); {PKG}.PickBook.ITEM_OK = true; }}
  catch (Throwable tp1) {{ {PKG}.SackPool.warn("auto-pickup: the item spawn hook could not be registered - every drop stays on the ground this start: " + tp1); }}
  try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickBreakSys()); {PKG}.PickBook.BREAK_OK = true; }}
  catch (Throwable tp2) {{ {PKG}.SackPool.warn("auto-pickup: the block break claim could not be registered - block drops stay on the ground this start: " + tp2); }}
  {PKG}.PickDeathMark.DDI = {PKG}.PickBook.cls("com.hypixel.hytale.server.npc.systems.NPCDamageSystems$DropDeathItems");
  {PKG}.PickDeathMark.TCR = {PKG}.PickBook.cls("com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$TickCorpseRemoval");
  {PKG}.PickDeathMark.CR = {PKG}.PickBook.cls("com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$CorpseRemoval");
  {PKG}.PickShareSys.DDI = {PKG}.PickDeathMark.DDI;
  {PKG}.PickShareSys.TCR = {PKG}.PickDeathMark.TCR;
  {PKG}.PickShareSys.CR = {PKG}.PickDeathMark.CR;
  if ({PKG}.PickDeathMark.DDI == null || {PKG}.PickDeathMark.TCR == null || {PKG}.PickDeathMark.CR == null) {PKG}.SackPool.warn("auto-pickup: NPCDamageSystems$DropDeathItems / DeathSystems not found - mob drops stay on the ground this start");
  else {{
    try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickDeathMark()); {PKG}.PickBook.DEATH_OK = true; }}
    catch (Throwable tp3) {{ {PKG}.SackPool.warn("auto-pickup: could not order the death mark before DropDeathItems - mob drops stay on the ground this start: " + tp3); }}
    if ({PKG}.PickBook.DEATH_OK) {{
      try {{ getEntityStoreRegistry().registerSystem(new {PKG}.PickShareSys()); }}
      catch (Throwable tp4) {{ {PKG}.SackPool.warn("auto-pickup: the killer's share could not be ordered after DropDeathItems - the top damager still gets the drop, a different killer gets no extra share this start: " + tp4); }}
    }}
  }}
''')
rep('''/pdadmin legacybags | omni; storage per profile (pkey); settings: SkyWynn Menu -> Server Setup -> SkyyVoid and Crafting (skyysacks.admin); UI kit {KIT_ID}");
''', '''/pdadmin legacybags | omni; storage per profile (pkey); settings: SkyWynn Menu -> Server Setup -> SkyyVoid and Crafting (skyysacks.admin); UI kit {KIT_ID}; auto-pickup " + {PKG}.PickBook.state());
''')
rep('''  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  super.shutdown();''', '''  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] auto-pickup this run: " + {PKG}.PickBook.stats()); }} catch (Throwable t) {{ }}   // 0.8.3
  try {{ {PKG}.PickBook.CL.clear(); {PKG}.PickBook.RINGS.clear(); {PKG}.PickBook.SHARE.clear(); {PKG}.PickBook.DONE.clear(); }} catch (Throwable t) {{ }}
  super.shutdown();''')
rep('''          vss, vst, vjob, vat, vac):   # 0.8.0: + VoidState, VoidStore, VoidJob, VoidAdminTask, PdAdminCmd
''', '''          vss, vst, vjob, vat, vac,    # 0.8.0: + VoidState, VoidStore, VoidJob, VoidAdminTask, PdAdminCmd
          pcl, prg, pbk, pgv, pdl, pis, pbs, pdm, pss):   # 0.8.3: auto-pickup
''')
gone('''          vss, vst, vjob, vat, vac):   # 0.8.0: + VoidState, VoidStore, VoidJob, VoidAdminTask, PdAdminCmd''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerSystem(") == SYS0 + 4, "exactly four new registerSystem calls"
assert s.index("public static long[] split(java.util.UUID u") < s.index("public static int deliver(")
assert s.index("public static int deliver(") < s.index("PickGive.deliver((@ST@) o")
assert s.index("public static @PKG@.PickClaim match(") < s.index("PickBook.match(@PKG@.PickBook.world")
assert s.index("public static java.util.UUID mark(") < s.index("PickBook.mark(st, cb")
assert s.index("public static int share(") < s.index("PickBook.share(st, cb")
assert s.index("public static void pickKeys(") < s.index("    pickKeys(p, first);")
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_bad = [ln for ln in _gone if ln not in GONE_OK and "storage per profile (pkey); settings: SkyWynn Menu" not in ln]
assert not _bad, "0.8.2 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.8.2 had %d)" % (s.count(LF), OLD.count(LF)))
