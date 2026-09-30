"""Derive SkyyEssentials/build_skyyessentials_0.1.6.py from the LIVE 0.1.5 (build_skyyessentials_0.1.5.py = the tools/deploy_set.py SET pin).
Run:  python tools/essentials_0_1_6_patch.py   then   python SkyyEssentials/build_skyyessentials_0.1.6.py   (never --deploy: coordinated deploy)
Check: python SkyyEssentials/test_skyyessentials_0.1.6.py   (bare JVM, -Xverify:all; nothing is deployed)
SkyyEssentials uses patch scripts since 0.1.4: edit THIS file, never the generated build script.

0.1.6 = Skyy 2026-09-30 (OPEN-QUESTIONS "LOCKED 2026-09-30"): "make durability a toggle in the server setup settings. off by default. so
your tools/ weapons, and armor never break." Design + engine facts: research/Durability-Switch-Research.md (sections 2, 5, 6, 7).
 1. Server Setup -> Essentials -> Gameplay: row gameplay.durability "Item durability" (bool, default OFF, live, danger + confirm=on: only
    turning it ON asks, with its own question through the check= hook). File key gameplay.durability in config.properties (appended to an
    older file with its default by TCfg.appendMissing, like 0.1.5's privacy.staffBypass).
 2. The switch (class EssDur): while OFF the four durability costs the engine reads from loaded assets are 0 - Item.durabilityLossOnHit
    (weapon hits, armor hits, bows, hammer cycling, the tool fallback), ItemTool$DurabilityLossBlockTypes.durabilityLossOnHit (tool per
    block), BlockSelectorToolData.durabilityLossOnUse (hammer block-set switch) and ModifyInventoryInteraction.adjustHeldItemDurability
    (hatchet / pickaxe on mobs, hoe, sickle, staff casts - only the ones WITHOUT a BrokenItem: cans, buckets, mugs, fertilizer keep using
    charges). Each positive cost is remembered before it is set to 0; ON puts back exactly the remembered value (only where the number is
    still our 0). Reflection on the asset objects only: no item stack is ever rewritten, no metadata touched (SkyyGear rolls safe).
    The client packet caches of the changed hammer items / interactions are cleared with SoftReference.clear() (what the GC does; no
    packet is sent) so a player joining after a runtime switch gets the current numbers.
    Death (10 % by default): EssDurDeath (RefChangeSystem on DeathComponent, AFTER DeathSystems$PlayerDropItemsConfig, BEFORE
    DeathSystems$DropPlayerDeathItems and BEFORE DeathSystems$PlayerDeathScreen, world thread) sets the component's durability-loss
    percentage to 0 while OFF (the respawn page then reads 0 %; also covers a world's own DeathConfigOverride). An UNAVAILABLE switch
    (engine fields changed by a game update) leaves death wear vanilla too, so the whole switch is off, not half of it.
 3. Lifecycle: setup() probes the engine fields (the ready line says so when the switch is UNAVAILABLE) and registers EssDurDeath +
    LoadedAssetsEvent listeners for Item and Interaction (the listener only raises a rescan flag: it runs inside the engine's asset
    write lock, so the scan itself is done by EssDurTick, at most a second later, outside that lock); start() applies the switch (every
    asset pack is loaded by then) and starts a 1 s idempotent re-check (EssDurTick: nothing happens while the applied state equals the
    switch and no rescan is flagged; the check and the apply share the EssDur monitor, so two callers never log the same change twice)
    so a hand edit + reload, import, restore or undo is followed within a second; the row's after= hook and TCfg.reloadKit apply at
    once. shutdown() puts the original costs back (a /plugin unload leaves vanilla behind) and stops the re-check.
 4. Optional admin action gameplay.repairOnline "Repair gear of online players" (danger: always asks): on each online player's own world
    thread, every worn tool / weapon / armor piece (wear item: armor, weapon, tool or hammer config, repairable, not consumable,
    loses durability on death - so cans, buckets, mugs and fertilizer are skipped) goes back to its current max durability with
    ItemStack.withDurability (same id, quantity, quality, METADATA) through a compare-and-set replaceItemStackInSlot (a slot that changed
    meanwhile is left alone: no duplication, no loss); armor stats are recalculated like the engine does when armor breaks. The admin
    gets "Repaired N worn item(s) for M player(s)." Items that are already worn are NEVER repaired by the switch itself.
    Deviation from the research: no "or a Utility config" in the wear rule - every Item carries ItemUtility.DEFAULT (never null).
 5. Ready line names the switch state; version 0.1.6. Everything else (commands, /trade, /r, warps editor, tpa, player switches, the other
    rows, files, bridge keys) stays 0.1.5's.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.5.py")
dst = os.path.join(ROOT, "SkyyEssentials", "build_skyyessentials_0.1.6.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)


# ================================================================================================ docstring + version
DOC = '''SkyyEssentials 0.1.6 - build script (javassist via jpype). GENERATED by tools/essentials_0_1_6_patch.py from the LIVE 0.1.5
(build_skyyessentials_0.1.5.py, the tools/deploy_set.py SET pin) - edit the patch, never this file.
Run:   python build_skyyessentials_0.1.6.py            -> SkyyEssentials/SkyyEssentials-0.1.6.jar   (never --deploy: tools/deploy_set.py)
Check: python test_skyyessentials_0.1.6.py            (bare JVM, -Xverify:all, the switch paths, the config row, two starts on a copy)

0.1.6 (2026-09-30, Skyy: "make durability a toggle in the server setup settings. off by default. so your tools/ weapons, and armor never
break." - OPEN-QUESTIONS LOCKED 2026-09-30; engine research: research/Durability-Switch-Research.md):
  ITEM DURABILITY SWITCH (Server Setup -> Essentials -> Gameplay -> "Item durability", key gameplay.durability, default OFF, live):
    OFF = tools, weapons and armor never lose durability, so they never break. ON = vanilla. Items that are already worn keep their value
    (the switch never repairs anything). Turning it ON asks first ("Turn item durability ON? ..."), turning it OFF does not.
    HOW (EssDur): the engine has no durability switch and no cancellable durability event, but every vanilla loss multiplies one of four
    numbers on loaded assets. While OFF each positive one is remembered and set to 0 by reflection (no item stack is written, no metadata
    touched, the client gets nothing new):
      Item.durabilityLossOnHit                              weapon hits (DamageAttackerTool), armor hits (DamageArmor), bow / crossbow
                                                            shots (LaunchProjectileInteraction), hammer cycling, the tool fallback
      ItemTool$DurabilityLossBlockTypes.durabilityLossOnHit tools breaking / damaging blocks (BlockHarvestUtils, also SkyySkills /
                                                            SkyyTrees / SkyyCollections block breaks and vein-mining style mods)
      BlockSelectorToolData.durabilityLossOnUse             hammer switching the held block set
      ModifyInventoryInteraction.adjustHeldItemDurability   hatchet / pickaxe hitting mobs, hoe, sickle, staff and fire stick casts -
                                                            ONLY interactions without a BrokenItem (watering cans, buckets, mugs,
                                                            fertilizer keep using their charges; an interrupted drink does not)
    ON writes back exactly the remembered values (only where the number is still 0). After a change the client packet caches of the
    changed assets are cleared (SoftReference.clear(), what the GC does; no packet is sent) so players joining later get the current
    numbers. Death: EssDurDeath (RefChangeSystem on DeathComponent, AFTER DeathSystems$PlayerDropItemsConfig, BEFORE
    DeathSystems$DropPlayerDeathItems and DeathSystems$PlayerDeathScreen, world thread) sets the death durability-loss percentage to 0
    while OFF (respawn page reads 0 %; per-world DeathConfigOverride included). Creative is unchanged.
    WHEN: setup() probes the engine fields and registers EssDurDeath and LoadedAssetsEvent listeners (Item, Interaction); start()
    applies the switch (all asset packs, mods included, are loaded by then) and starts EssDurTick, a 1 s idempotent re-check (nothing
    happens while the applied state equals the switch and no rescan is flagged) - so a hand edit + reload, import, restore or undo is
    followed within a second; the row's after= hook and TCfg.reloadKit apply at once. An asset reload while OFF zeroes the new asset
    objects within a second (the listener runs inside the engine's asset write lock, so it only flags a rescan; EssDurTick scans).
    shutdown() puts every original cost back and stops the re-check. A missing engine field (a game update) = one warning at setup, the
    ready line says "UNAVAILABLE", vanilla wear everywhere (death included); never throws.
    Thread safety: the asset numbers are global (not ECS): single 8-byte writes under the EssDur monitor, read by the engine on the
    world threads (the engine's own asset reload replaces them the same way); the death rule runs on the world thread as a system.
  OPTIONAL ACTION "Repair gear of online players" (gameplay.repairOnline, danger = always asks): per online player on their own world
    thread, every worn wear item (armor / weapon / tool / hammer config, repairable, not consumable, loses durability on death)
    in InventoryComponent.EVERYTHING goes to its current max with ItemStack.withDurability (id, quantity, quality and METADATA kept -
    SkyyGear rolls safe) via compare-and-set replaceItemStackInSlot (a slot that changed meanwhile is skipped: no duplication, no loss);
    armor stats recalculated (StatModifiersManager.scheduleRecalculate, as the engine does when armor breaks). Answer: "working on it",
    then "Repaired N worn item(s) for M player(s)." to the admin. Offline players, chests, vaults and snapshots are not touched.
  SkyyGear: nothing changes there. BrokenPenalties is untouched and no new piece breaks, so an already broken piece stays x0.75 in the
    engine and in SkyyGear's armor locks; no stack is rewritten, so rolls / identify state / craft signatures are untouched.
  Do not enable Serilum DisabledDurability next to it (it refills every item to full on every inventory change).
  Nothing else changes: commands, permission nodes, /trade, /r, the warps editor, tpa, player switches, the other rows, files, bridge keys.

'''
first = s.index('"""') + 3
s = s[:first] + DOC + s[first:]
rep('\nVERSION = "0.1.5"\n', '\nVERSION = "0.1.6"\n')

# ================================================================================================ probes (0.1.6 durability switch)
rep('''PKG = "com.skyy.essentials"
ES = PKG + ".EssStore"
rq   = pool.makeClass(PKG + ".TpReq")''', '''# 0.1.6: the item durability switch (research/Durability-Switch-Research.md 5.6): every engine member EssDur / EssDurDeath /
# EssRepairTask touch. The four cost fields are protected / private, so they are checked as declared fields (double, not static, not
# final) - B.probe only sees public members.
DITEM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
DTOOL = "com.hypixel.hytale.server.core.asset.type.item.config.ItemTool"
DDLBT = "com.hypixel.hytale.server.core.asset.type.item.config.ItemTool$DurabilityLossBlockTypes"
DBSTD = "com.hypixel.hytale.server.core.asset.type.item.config.BlockSelectorToolData"
DINTR = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction"
DMINV = "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.ModifyInventoryInteraction"
DDSYS = "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems"
DINVC = "com.hypixel.hytale.server.core.inventory.InventoryComponent"
for c, m in ((DITEM, "getAssetMap"), (DITEM, "getTool"), (DITEM, "getBlockSelectorToolData"), (DITEM, "getDurabilityLossOnHit"),
             (DITEM, "getArmor"), (DITEM, "getWeapon"), (DITEM, "isRepairable"), (DITEM, "isConsumable"),
             (DITEM, "getDurabilityLossOnDeath"), (DITEM, "getId"), (DTOOL, "getDurabilityLossBlockTypes"),
             (DDLBT, "getDurabilityLossOnHit"), (DBSTD, "getDurabilityLossOnUse"), (DINTR, "getAssetMap"), (DINTR, "getId"),
             ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAssetMap"),
             ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAssetMap"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "setItemsDurabilityLossPercentage"),
             ("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent", "getItemsDurabilityLossPercentage"),
             (DDSYS + "$OnDeathSystem", "componentType"), ("com.hypixel.hytale.component.system.RefChangeSystem", "onComponentAdded"),
             ("com.hypixel.hytale.component.system.ISystem", "getDependencies"),
             ("com.hypixel.hytale.component.dependency.Order", "AFTER"), ("com.hypixel.hytale.component.dependency.Order", "BEFORE"),
             ("com.hypixel.hytale.assetstore.event.LoadedAssetsEvent", "getAssetClass"), ("com.hypixel.hytale.event.EventRegistry", "register"),
             ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem"), (PB, "getEntityStoreRegistry"),
             (DINVC, "getCombined"), (DINVC, "EVERYTHING"),
             ("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer", "getCapacity"),
             ("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer", "getItemStack"),
             ("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer", "replaceItemStackInSlot"),
             ("com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction", "succeeded"),
             ("com.hypixel.hytale.server.core.inventory.ItemStack", "withDurability"),
             ("com.hypixel.hytale.server.core.inventory.ItemStack", "getItem"),
             ("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap", "getStatModifiersManager"),
             ("com.hypixel.hytale.server.core.entity.StatModifiersManager", "scheduleRecalculate"),
             (UNI, "getPlayers"), (HSV, "SCHEDULED_EXECUTOR")):
    B.probe(pool, c, m)
for c, f, t in ((DITEM, "durabilityLossOnHit", "double"), (DDLBT, "durabilityLossOnHit", "double"), (DBSTD, "durabilityLossOnUse", "double"),
                (DMINV, "adjustHeldItemDurability", "double"), (DMINV, "brokenItem", "java.lang.String")):
    _fd = pool.get(c).getDeclaredField(f)
    _md = _fd.getModifiers()
    assert str(_fd.getType().getName()) == t and not J["Modifier"].isStatic(_md) and not J["Modifier"].isFinal(_md), \\
        "durability field %s.%s is not a non-final %s" % (c, f, t)
assert pool.get(DMINV).subclassOf(pool.get(DINTR)), "ModifyInventoryInteraction no longer extends Interaction"
# the engine orders PlayerDropItemsConfig BEFORE DropPlayerDeathItems itself; EssDurDeath sits between them (AFTER / BEFORE) and also
# BEFORE PlayerDeathScreen (it reads the percentage for the respawn page when the component is added; it declares no dependencies of its
# own and no engine system names it, so the extra edge adds no cycle - bytecode 2026-09-30)
for _n in ("$PlayerDropItemsConfig", "$DropPlayerDeathItems", "$PlayerDeathScreen"):
    assert pool.get(DDSYS + _n).subclassOf(pool.get(DDSYS + "$OnDeathSystem")), DDSYS + _n + " is no OnDeathSystem"
    assert J["Modifier"].isPublic(pool.get(DDSYS + _n).getModifiers()), DDSYS + _n + " is not public"

PKG = "com.skyy.essentials"
ES = PKG + ".EssStore"
# 0.1.6: the switch class exists (with its kit field) before TCfg compiles its get / put and before the config kit is emitted
edur = pool.makeClass(PKG + ".EssDur")
edur.addField(CtField.make("public static volatile boolean ON = false;", edur))
rq   = pool.makeClass(PKG + ".TpReq")''')

# ================================================================================================ EssDur + the small classes (compiled before TCfg:
# TCfg.reloadKit calls EssDur.sync)
ESSDUR = r'''# =====================================================================================================================================
# 0.1.6 the item durability switch (research/Durability-Switch-Research.md 5.1-5.7 + 6). Classes: EssDur (the switch, the kit hooks, the
# repair action), EssDurTick (1 s re-check), EssDurAssetL (asset reload listener), EssRepairJob / EssRepairTask (the optional repair
# action, world thread), EssDurDeath (RefChangeSystem on DeathComponent). Compiled callee-first (javassist: no forward references).
# =====================================================================================================================================
T.update({
    "ITEM": DITEM, "ITL": DTOOL, "DLBT": DDLBT, "BSTD": DBSTD, "INTR": DINTR, "MII": DMINV, "INVC": DINVC,
    "DTHC": "com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent",
    "PDIC": DDSYS + "$PlayerDropItemsConfig", "DPDI": DDSYS + "$DropPlayerDeathItems", "PDSC": DDSYS + "$PlayerDeathScreen",
    "SDEP": "com.hypixel.hytale.component.dependency.SystemDependency", "ORD": "com.hypixel.hytale.component.dependency.Order",
    "QRY": "com.hypixel.hytale.component.query.Query", "CMP": "com.hypixel.hytale.component.Component",
    "CB": "com.hypixel.hytale.component.CommandBuffer", "CIC": "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer",
    "ISST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction",
    "LAE": "com.hypixel.hytale.assetstore.event.LoadedAssetsEvent",
})
edt  = pool.makeClass(PKG + ".EssDurTick")
eral = pool.makeClass(PKG + ".EssDurAssetL")
erj  = pool.makeClass(PKG + ".EssRepairJob")
ert  = pool.makeClass(PKG + ".EssRepairTask")
edd  = pool.makeClass(PKG + ".EssDurDeath", pool.get(DDSYS + "$OnDeathSystem"))
DUR_ALL = [edur, edt, eral, erj, ert, edd]
edt.addInterface(pool.get("java.lang.Runnable"))
ert.addInterface(pool.get("java.lang.Runnable"))
eral.addInterface(pool.get("java.util.function.Consumer"))

# ---- EssDur state. ON = the kit field (gameplay.durability; false = durability OFF = the default). APPLIED = what the asset numbers
# show now: -1 nothing applied yet, 0 = OFF applied (costs are 0), 1 = ON applied (vanilla). The four maps remember each asset object's
# original cost (IdentityHashMap object -> Double); they are only touched inside the static synchronized methods (the EssDur monitor).
# RESCAN = an asset reload happened while OFF (set by the listener, which runs inside the engine's asset write lock; EssDurTick scans).
# BROKEN / STATE / DEATH_OK are diagnostics (BROKEN is also read by sync, the listener and the death rule).
for _f in ("public static volatile boolean STARTED = false;", "public static volatile int APPLIED = -1;",
           "public static volatile boolean RESCAN = false;",
           "public static volatile boolean BROKEN = false;", "public static volatile boolean DEATH_OK = false;",
           'public static volatile String STATE = "not started";', "public static volatile boolean IDS_LOGGED = false;",
           "public static volatile long WARNED_AT = 0L;",
           "public static final java.util.IdentityHashMap O_HIT = new java.util.IdentityHashMap();",
           "public static final java.util.IdentityHashMap O_BLK = new java.util.IdentityHashMap();",
           "public static final java.util.IdentityHashMap O_USE = new java.util.IdentityHashMap();",
           "public static final java.util.IdentityHashMap O_INT = new java.util.IdentityHashMap();",
           "public static java.lang.reflect.Field F_HIT;", "public static java.lang.reflect.Field F_BLK;",
           "public static java.lang.reflect.Field F_USE;", "public static java.lang.reflect.Field F_ADJ;",
           "public static java.lang.reflect.Field F_BRK;", "public static java.util.concurrent.ScheduledFuture WATCH;",
           "public static volatile int N_HIT = 0;", "public static volatile int N_BLK = 0;", "public static volatile int N_USE = 0;",
           "public static volatile int N_INT = 0;", "public static int CHG = 0;",
           "public static final java.util.IdentityHashMap PKT = new java.util.IdentityHashMap();",
           "public static java.lang.reflect.Field F_IPK;", "public static java.lang.reflect.Field F_NPK;",
           "public static java.lang.reflect.Field F_SPK;", "public static volatile boolean PK_TRIED = false;",
           'public static final String ASK_ON = "Turn item durability ON? Tools, weapons and armor wear out and can break again.";'):
    F(edur, _f)
M(edur, r"""
public static void info(String m) {
  try { if (@ES@.LOG != null) @ES@.LOG.at(java.util.logging.Level.INFO).log("[SkyyEssentials] " + m); } catch (Throwable t) { }
}""")
# a failing apply is retried every second by EssDurTick: warn at most once a minute
M(edur, r"""
public static void warnRate(String m) {
  long now = System.currentTimeMillis();
  if (now - WARNED_AT < 60000L) return;
  WARNED_AT = now;
  @ES@.warn(m);
}""")
M(edur, r"""
public static java.lang.reflect.Field fld(Class c, String n) throws Exception {
  java.lang.reflect.Field f = c.getDeclaredField(n);
  int md = f.getModifiers();
  if (java.lang.reflect.Modifier.isFinal(md) || java.lang.reflect.Modifier.isStatic(md)) throw new IllegalStateException(c.getName() + "." + n + " is final or static");
  f.setAccessible(true);
  return f;
}""")
# the five engine fields (research 5.2 / 5.6). Missing or changed (a game update) -> BROKEN: one warning, vanilla wear, never throws.
M(edur, r"""
public static synchronized boolean fields() {
  if (F_HIT != null) return true;
  if (BROKEN) return false;
  try {
    java.lang.reflect.Field a = fld(@ITEM@.class, "durabilityLossOnHit");
    java.lang.reflect.Field b = fld(@DLBT@.class, "durabilityLossOnHit");
    java.lang.reflect.Field c = fld(@BSTD@.class, "durabilityLossOnUse");
    java.lang.reflect.Field d = fld(@MII@.class, "adjustHeldItemDurability");
    java.lang.reflect.Field e = fld(@MII@.class, "brokenItem");
    if (a.getType() != Double.TYPE || b.getType() != Double.TYPE || c.getType() != Double.TYPE || d.getType() != Double.TYPE || e.getType() != String.class) throw new IllegalStateException("a durability field changed its type");
    F_BLK = b;
    F_USE = c;
    F_ADJ = d;
    F_BRK = e;
    F_HIT = a;
    return true;
  } catch (Throwable t) {
    BROKEN = true;
    STATE = "unavailable";
    @ES@.warn("Item durability switch UNAVAILABLE - this game version changed the engine's durability fields (" + t + "). Items wear as in vanilla, whatever Server Setup says.");
    return false;
  }
}""")
# OFF on one cost number: a positive cost is remembered (its CURRENT value is what ON puts back) and set to 0. 1 = the number is 0 by us.
M(edur, r"""
public static int off(java.util.IdentityHashMap orig, java.lang.reflect.Field f, Object o) throws Exception {
  if (o == null) return 0;
  double v = f.getDouble(o);
  if (v > 0.0) {
    orig.put(o, Double.valueOf(v));
    f.setDouble(o, 0.0);
    CHG++;
    return 1;
  }
  if (v == 0.0 && orig.containsKey(o)) return 1;
  return 0;
}""")
# rule R1 (research 2.3 / 5.2 step 4): a ModifyInventory durability LOSS without a BrokenItem is wear (hatchet / pickaxe on mobs, hoe,
# sickle, staffs, fire sticks, drinks' Failed branch); with a BrokenItem it is a charge (cans, buckets, mugs, fertilizer) and stays.
M(edur, r"""
public static int offInt(Object o) throws Exception {
  if (!(o instanceof @MII@)) return 0;
  double v = F_ADJ.getDouble(o);
  if (v < 0.0) {
    if (F_BRK.get(o) != null) return 0;
    O_INT.put(o, Double.valueOf(v));
    F_ADJ.setDouble(o, 0.0);
    CHG++;
    return 1;
  }
  if (v == 0.0 && O_INT.containsKey(o)) return 1;
  return 0;
}""")
# ON: every remembered cost goes back - only where the number is still our 0 (a value somebody changed meanwhile is left alone). The
# maps are kept, so the next OFF remembers the same objects again.
M(edur, r"""
public static int restore(java.util.IdentityHashMap orig, java.lang.reflect.Field f) {
  int n = 0;
  java.util.Iterator it = orig.keySet().iterator();
  while (it.hasNext()) {
    Object k = it.next();
    Object v = orig.get(k);
    try {
      if (v instanceof Double && f.getDouble(k) == 0.0) {
        f.setDouble(k, ((Double) v).doubleValue());
        n++;
      }
    } catch (Throwable t) { }
  }
  return n;
}""")
# a copy of an asset map's values (the maps are fastutil maps the asset loader writes under its own lock; a copy that fails while an
# asset reload writes throws, the caller keeps the old state and EssDurTick retries within a second)
M(edur, r"""
public static java.util.ArrayList snap(java.util.Map m) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (m != null) out.addAll(m.values());
  return out;
}""")
# ---- client packet caches. The client learns the hammer cost (Item packet -> BlockSelectorToolData.durabilityLossOnUse) and the
# ModifyInventory cost (Interaction packet) when it joins; the engine builds those packets lazily and keeps them in SoftReferences
# (Item.cachedPacket, Interaction.cachedPacket, HytaleAssetStore.cachedInitPackets). After a change the references of the changed assets
# are CLEARED (Reference.clear() = exactly what the garbage collector does; the engine rebuilds a cleared packet on the next join). The
# fields themselves are never written: the engine reads them twice (Interaction.toPacket offsets 1 and 12), so nulling them could race
# with a join. Players who are online already keep their login copy (the server's inventory stays authoritative). Missing fields (a game
# update) = one INFO line, the switch itself still works.
M(edur, r"""
public static synchronized void pkFields() {
  if (PK_TRIED) return;
  PK_TRIED = true;
  try {
    java.lang.reflect.Field a = fld(@ITEM@.class, "cachedPacket");
    java.lang.reflect.Field b = fld(@INTR@.class, "cachedPacket");
    if (!java.lang.ref.Reference.class.isAssignableFrom(a.getType()) || !java.lang.ref.Reference.class.isAssignableFrom(b.getType())) throw new IllegalStateException("a packet cache changed its type");
    F_NPK = b;
    F_IPK = a;
  } catch (Throwable t) {
    info("Item durability: the client packet caches were not found (" + t + ") - players joining after a switch made while the server runs keep the old hammer / tool-interaction numbers until a restart (inventories stay right)");
    return;
  }
  // the per-store cache of the whole asset packet (optional; looked up without initialising the class)
  try {
    java.lang.reflect.Field c = fld(Class.forName("com.hypixel.hytale.server.core.asset.HytaleAssetStore", false, @ITEM@.class.getClassLoader()), "cachedInitPackets");
    if (java.lang.ref.Reference.class.isAssignableFrom(c.getType())) F_SPK = c;
  } catch (Throwable t) { info("Item durability: the asset store packet cache was not found (" + t + ") - players joining after a runtime switch may keep old tool-interaction numbers until a restart"); }
}""")
M(edur, r"""
public static void clearRef(java.lang.reflect.Field f, Object o) {
  if (f == null || o == null) return;
  try {
    Object r = f.get(o);
    if (r instanceof java.lang.ref.Reference) ((java.lang.ref.Reference) r).clear();
  } catch (Throwable t) { }
}""")
M(edur, r"""
public static void dropPackets() {
  pkFields();
  if (F_IPK == null) return;
  java.util.Iterator it = PKT.keySet().iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof @ITEM@) clearRef(F_IPK, o);
    else clearRef(F_NPK, o);
  }
  if (F_SPK == null) return;
  try {
    Object s1 = @ITEM@.getAssetStore();
    if (F_SPK.getDeclaringClass().isInstance(s1)) clearRef(F_SPK, s1);
    Object s2 = @INTR@.getAssetStore();
    if (F_SPK.getDeclaringClass().isInstance(s2)) clearRef(F_SPK, s2);
  } catch (Throwable t) { }
}""")
M(edur, r"""
public static int remembered() {
  return O_HIT.size() + O_BLK.size() + O_USE.size() + O_INT.size();
}""")
# the whole switch, under the EssDur monitor. on = vanilla (restore), !on = every durability cost 0. rescan = an asset reload while OFF
# (log only when new asset objects were zeroed). Returns the log line, or null (nothing to say). May throw (the map copy); callers catch.
M(edur, r"""
public static synchronized String applyLocked(boolean on, boolean rescan) {
  if (!fields()) return null;
  if (on) {
    int n = restore(O_HIT, F_HIT) + restore(O_BLK, F_BLK) + restore(O_USE, F_USE) + restore(O_INT, F_ADJ);
    if (n > 0) dropPackets();
    boolean was = APPLIED == 0;
    APPLIED = 1;
    STATE = "on";
    if (!was && n == 0) return "Item durability ON (vanilla): tools, weapons and armor wear and can break";
    return "Item durability ON (vanilla): " + n + " durability costs put back - tools, weapons and armor wear and can break again";
  }
  int before = remembered();
  CHG = 0;
  java.util.ArrayList items = snap(@ITEM@.getAssetMap().getAssetMap());
  java.util.ArrayList ints = snap(@INTR@.getAssetMap().getAssetMap());
  int a = 0;
  int b = 0;
  int c = 0;
  int d = 0;
  int bad = 0;
  for (int i = 0; i < items.size(); i++) {
    Object o = items.get(i);
    if (!(o instanceof @ITEM@)) continue;
    try {
      @ITEM@ it = (@ITEM@) o;
      a += off(O_HIT, F_HIT, it);
      @ITL@ tl = it.getTool();
      if (tl != null) {
        @DLBT@[] arr = tl.getDurabilityLossBlockTypes();
        if (arr != null) {
          for (int k = 0; k < arr.length; k++) b += off(O_BLK, F_BLK, arr[k]);
        }
      }
      int u = off(O_USE, F_USE, it.getBlockSelectorToolData());
      c += u;
      if (u == 1) PKT.put(it, Boolean.TRUE);
    } catch (Throwable t) { bad++; }
  }
  StringBuilder ids = new StringBuilder();
  int nid = 0;
  for (int i = 0; i < ints.size(); i++) {
    Object o = ints.get(i);
    int z = 0;
    try { z = offInt(o); } catch (Throwable t) { bad++; }
    d += z;
    if (z == 1) PKT.put(o, Boolean.TRUE);
    if (z == 1 && !IDS_LOGGED) {
      nid++;
      if (ids.length() < 1500) {
        if (ids.length() > 0) ids.append(", ");
        ids.append(((@INTR@) o).getId());
      }
    }
  }
  int added = remembered() - before;
  if (CHG > 0) dropPackets();
  APPLIED = 0;
  STATE = "off";
  N_HIT = a;
  N_BLK = b;
  N_USE = c;
  N_INT = d;
  if (rescan && added == 0) return null;
  String m = "Item durability OFF: " + a + " hit costs, " + b + " tool block costs, " + c + " hammer costs and " + d + " interaction costs set to 0 - tools, weapons and armor never lose durability (worn items keep their value)";
  if (rescan) m = m + " (after an asset reload: " + added + " new)";
  if (bad > 0) m = m + " (" + bad + " assets could not be read)";
  if (!IDS_LOGGED && nid > 0) {
    m = m + ". Interaction costs set to 0 (" + nid + "): " + ids.toString();
    IDS_LOGGED = true;
  }
  return m;
}""")
M(edur, r"""
public static String apply(boolean on) {
  String r = null;
  try { r = applyLocked(on, false); }
  catch (Throwable t) {
    warnRate("Item durability: could not switch " + (on ? "ON" : "OFF") + " yet (" + t + ") - retried every second");
    return null;
  }
  if (r != null) info(r);
  return r;
}""")
# the check and the apply under ONE monitor hold (0.1.6 review: the kit hook and EssDurTick racing could both see the old state and log
# the same change twice). A switch change = the full apply; OFF with a flagged asset reload = a rescan (only new objects are logged);
# otherwise nothing. RESCAN is cleared BEFORE the scan, so a reload that lands during the scan flags the next one. May throw (the map
# copy); sync() catches and re-flags.
M(edur, r"""
public static synchronized String syncLocked(boolean on) {
  if (!STARTED || BROKEN) return null;
  int want = on ? 1 : 0;
  boolean again = RESCAN;
  if (want == APPLIED && (on || !again)) return null;
  RESCAN = false;
  return applyLocked(on, want == APPLIED);
}""")
# idempotent: nothing happens while the applied state equals the switch and no rescan is flagged (EssDurTick every second, the kit's
# after= hook, reloadKit)
M(edur, r"""
public static void sync() {
  if (!STARTED || BROKEN) return;
  boolean on = ON;
  String r = null;
  try { r = syncLocked(on); }
  catch (Throwable t) {
    if (!on) RESCAN = true;
    warnRate("Item durability: could not apply " + (on ? "ON" : "OFF") + " yet (" + t + ") - retried every second");
    return;
  }
  if (r != null) info(r);
}""")
# the kit's after= hook of gameplay.durability (a menu / command / import / restore / undo change): apply at once
M(edur, r"""
public static void changed(String key) { sync(); }""")
# the kit's check= hook: only turning durability ON asks (its own words; confirm=on keeps the kit's own question to the same case)
M(edur, r"""
public static String check(String key, String value) {
  if ("true".equals(value)) return "?" + ASK_ON;
  return null;
}""")
# a LoadedAssetsEvent for Item or Interaction (asset editor / hot reload): while OFF the new asset objects must be zeroed. The engine
# dispatches this event INSIDE AssetStore.loadAssets0 while it holds AssetRegistry.ASSET_LOCK (0.1.6 review), so the listener only raises
# the flag - no scan, no EssDur monitor, no engine call under that lock; EssDurTick does the rescan outside it, at most a second later.
# Ignored before start().
M(edur, r"""
public static void assetsLoaded() {
  if (!STARTED || BROKEN || ON) return;
  RESCAN = true;
}""")
# a wear item (research 6): armor / weapon / tool / hammer config, repairable, not consumable, loses durability on death. Watering cans
# (not repairable), buckets / mugs (consumable or no death loss) and fertilizer (no death loss) are not wear. NOT the research's
# "or a Utility config": the engine gives EVERY item ItemUtility.DEFAULT (Item.<init> offset 20, bytecode 2026-09-30), so getUtility()
# is never null and would make every item count (the 0.1.6 harness caught it); vanilla utility items (shields) have no durability.
M(edur, r"""
public static boolean isWear(@ITEM@ it) {
  if (it == null || it == @ITEM@.UNKNOWN) return false;
  if (it.getArmor() == null && it.getWeapon() == null && it.getTool() == null && it.getBlockSelectorToolData() == null) return false;
  return it.isRepairable() && !it.isConsumable() && it.getDurabilityLossOnDeath();
}""")
M(edur, r"""
public static boolean needsRepair(@IS@ s) {
  if (s == null || s.isEmpty()) return false;
  double mx = s.getMaxDurability();
  if (!(mx > 0.0) || !(s.getDurability() < mx)) return false;
  return isWear(s.getItem());
}""")

# ---- EssRepairJob: one "Repair gear of online players" press. done() is called once per player (their world thread, or at once when
# they have no world); the last one reports to the admin (and the server log).
for _f in ("public java.util.UUID who;", "public String name;", "public java.util.concurrent.atomic.AtomicInteger left;",
           "public java.util.concurrent.atomic.AtomicInteger items;", "public java.util.concurrent.atomic.AtomicInteger players;",
           "public java.util.concurrent.atomic.AtomicInteger moved;"):
    F(erj, _f)
C(erj, r"""
public EssRepairJob(java.util.UUID who, String name, int n) {
  this.who = who;
  this.name = name;
  this.left = new java.util.concurrent.atomic.AtomicInteger(n);
  this.items = new java.util.concurrent.atomic.AtomicInteger(0);
  this.players = new java.util.concurrent.atomic.AtomicInteger(0);
  this.moved = new java.util.concurrent.atomic.AtomicInteger(0);
}""")
M(erj, r"""
public void done(int n, boolean mv) {
  if (n > 0) {
    this.items.addAndGet(n);
    this.players.incrementAndGet();
  }
  if (mv) this.moved.incrementAndGet();
  if (this.left.decrementAndGet() != 0) return;
  int mo = this.moved.get();
  String m = "Repaired " + this.items.get() + " worn item(s) for " + this.players.get() + " player(s)." + (mo > 0 ? " " + mo + " player(s) changed worlds meanwhile - press again for them." : "");
  @PKG@.EssDur.info("Repair gear of online players (" + (this.name == null ? "console" : this.name) + "): " + m);
  if (this.who != null) @ES@.sayTo(this.who, "[Server Setup] " + m, @ES@.OK);
}""")
# ---- EssRepairTask: one player, on the world thread it was scheduled on (a player who moved to another world meanwhile is skipped and
# counted). Compare-and-set per slot: replaceItemStackInSlot only writes when the slot still holds the stack that was read.
for _f in ("public @PKG@.EssRepairJob job;", "public @PR@ pr;", "public @WLD@ w;"):
    F(ert, _f)
C(ert, r"""
public EssRepairTask(@PKG@.EssRepairJob job, @PR@ pr, @WLD@ w) {
  this.job = job;
  this.pr = pr;
  this.w = w;
}""")
M(ert, r"""
public void run() {
  int n = 0;
  boolean mv = false;
  try {
    @REF@ ref = this.pr.getReference();
    if (ref != null && ref.isValid()) {
      @ST@ st = ref.getStore();
      Object ext = st.getExternalData();
      if (!(ext instanceof @EST@) || ((@EST@) ext).getWorld() != this.w) mv = true;
      else {
        @CIC@ c = @INVC@.getCombined(st, ref, @INVC@.EVERYTHING);
        boolean armor = false;
        if (c != null) {
          int cap = c.getCapacity();
          for (int i = 0; i < cap; i++) {
            @IS@ s = c.getItemStack((short) i);
            if (!@PKG@.EssDur.needsRepair(s)) continue;
            @IS@ ns = s.withDurability(s.getMaxDurability());
            @ISST@ tx = c.replaceItemStackInSlot((short) i, s, ns);
            if (tx != null && tx.succeeded()) {
              n++;
              if (s.getItem().getArmor() != null) armor = true;
            }
          }
        }
        if (armor) {
          @ESM@ sm = (@ESM@) st.getComponent(ref, @ESM@.getComponentType());
          if (sm != null) sm.getStatModifiersManager().scheduleRecalculate();
        }
      }
    }
  } catch (Throwable t) { @ES@.warn("repair gear of " + this.pr.getUsername() + " failed: " + t); }
  this.job.done(n, mv);
}""")
# the kit action gameplay.repairOnline (danger: the kit always asks first). Answers at once; the work runs on each player's world thread.
M(edur, r"""
public static Object[] repairAction(java.util.UUID who, String name) {
  if (!STARTED) return new Object[] { "bad", null, "The server is still starting - try again in a moment." };
  java.util.ArrayList list = new java.util.ArrayList();
  try { list.addAll(@UNI@.get().getPlayers()); }
  catch (Throwable t) { @ES@.warn("repair gear: could not list the online players: " + t); return new Object[] { "error", null, "Could not list the online players - see the server log." }; }
  if (list.isEmpty()) return new Object[] { "ok", null, "Nobody is online - nothing was repaired." };
  @PKG@.EssRepairJob job = new @PKG@.EssRepairJob(who, name, list.size());
  for (int i = 0; i < list.size(); i++) {
    @PR@ pr = (@PR@) list.get(i);
    @WLD@ w = @ES@.worldOf(pr);
    if (pr == null || w == null || !w.isAlive()) { job.done(0, false); continue; }
    try { w.execute(new @PKG@.EssRepairTask(job, pr, w)); }
    catch (Throwable t) { job.done(0, false); }
  }
  return new Object[] { "ok", null, "Repairing the worn tools, weapons and armor of " + list.size() + " online player(s) - working on it." };
}""")
# ---- EssDurTick: the 1 s idempotent re-check (a hand edit + reload / import / restore / undo reaches the switch within a second)
C(edt, "public EssDurTick() { }")
M(edt, r"""
public void run() {
  try { @PKG@.EssDur.sync(); } catch (Throwable t) { }
}""")
# ---- EssDurAssetL: LoadedAssetsEvent keyed by Item.class / Interaction.class (the CraftingPlugin registration pattern)
C(eral, "public EssDurAssetL() { }")
M(eral, r"""
public void accept(Object e) {
  try { @PKG@.EssDur.assetsLoaded(); } catch (Throwable t) { }
}""")
# ---- start (plugin start(): every asset pack is loaded) / stop (plugin shutdown(): the original costs go back)
M(edur, r"""
public static void start() {
  RESCAN = false;
  STARTED = true;
  apply(ON);
  try { WATCH = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.EssDurTick(), 1L, 1L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @ES@.warn("Item durability: the 1 s re-check could not be scheduled (" + t + ") - changes still apply from Server Setup"); }
}""")
M(edur, r"""
public static void stop() {
  try { if (WATCH != null) WATCH.cancel(false); } catch (Throwable t) { }
  WATCH = null;
  boolean was = STARTED;
  STARTED = false;
  if (!was || APPLIED != 0) return;
  try {
    applyLocked(true, false);
    info("Item durability: the original durability costs were put back (SkyyEssentials stopped)");
  } catch (Throwable t) { @ES@.warn("Item durability: could not put the original costs back at shutdown: " + t); }
  APPLIED = -1;
  STATE = "stopped";
}""")
# ---- EssDurDeath: RefChangeSystem on DeathComponent for players (DeathSystems$OnDeathSystem gives componentType() and empty set /
# removed). AFTER PlayerDropItemsConfig (it copies the world's death config into the component), BEFORE DropPlayerDeathItems (it
# lowers every stack by max x percentage / 100 when the percentage is > 0) and BEFORE PlayerDeathScreen (it reads the percentage for the
# respawn page when the component is added; explicit instead of relying on DamageModule's registration order). World thread. One
# registerSystem (setup). An UNAVAILABLE switch (EssDur.BROKEN: a game update changed the engine fields) = vanilla death wear too.
F(edd, "public java.util.Set deps;")
C(edd, r"""
public EssDurDeath() {
  super();
  this.deps = new java.util.HashSet();
  this.deps.add(new @SDEP@(@ORD@.AFTER, @PDIC@.class));
  this.deps.add(new @SDEP@(@ORD@.BEFORE, @DPDI@.class));
  this.deps.add(new @SDEP@(@ORD@.BEFORE, @PDSC@.class));
}""")
M(edd, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
M(edd, "public java.util.Set getDependencies() { return this.deps; }")
M(edd, r"""
public void onComponentAdded(@REF@ r, @CMP@ c, @ST@ s, @CB@ b) {
  try {
    if (!@PKG@.EssDur.ON && !@PKG@.EssDur.BROKEN && c instanceof @DTHC@) ((@DTHC@) c).setItemsDurabilityLossPercentage(0.0);
  } catch (Throwable t) { }
}""")

'''
rep('''# ================= TCfg: config.properties (replyShortcut, the 0.1.3 teleport/message keys, the /trade keys), logger, bridge, atomic files, trade.log =================''',
    ESSDUR + '''# ================= TCfg: config.properties (replyShortcut, the 0.1.3 teleport/message keys, the /trade keys), logger, bridge, atomic files, trade.log =================''')

# ================================================================================================ TCfg loader row + default file
rep('''     "privacy.staffBypass: true = players with skyyessentials.bypass (ops included) still reach a player who turned Teleport requests or Private messages off in /settings. false = those switches refuse everyone."),
]''', '''     "privacy.staffBypass: true = players with skyyessentials.bypass (ops included) still reach a player who turned Teleport requests or Private messages off in /settings. false = those switches refuse everyone."),
    # 0.1.6 (field in EssDur): the item durability switch, default OFF (Skyy 2026-09-30)
    ("gameplay.durability", "Item durability", "bool", "@PKG@.EssDur.ON", 0, 1, "false", "",
     "gameplay.durability: false (the default) = tools, weapons and armor never lose durability, so they never break; items that are already worn keep their value. true = vanilla wear and breaking. Applies at once."),
]''')
rep('''FILE_ORDER = [REPLY_IDX, IDX["part.tpa"], IDX["part.msg"], IDX["tpa.expireSeconds"], IDX["tpa.cooldownSeconds"],
              IDX["privacy.staffBypass"]] + list(range(0, 13))
FILE_BLOCKS = {1: "# ---- teleports and private messages (SkyyEssentials 0.1.3) ----", 6: "# ---- /trade (SkyyEssentials 0.1.2) ----"}''',
    '''FILE_ORDER = [REPLY_IDX, IDX["part.tpa"], IDX["part.msg"], IDX["tpa.expireSeconds"], IDX["tpa.cooldownSeconds"],
              IDX["privacy.staffBypass"]] + list(range(0, 13)) + [IDX["gameplay.durability"]]
FILE_BLOCKS = {1: "# ---- teleports and private messages (SkyyEssentials 0.1.3) ----", 6: "# ---- /trade (SkyyEssentials 0.1.2) ----",
               19: "# ---- gameplay (SkyyEssentials 0.1.6) ----"}''')
# a hand edit + reload applies the switch at once (EssDurTick would within a second anyway)
rep('''      if (c == null) { warn("config.properties: " + KEYS[i] + "=" + raw + " is not valid (" + rule(i) + ") - keeping " + get(i)); continue; }
      put(i, c);
    }
    BROKEN = false;
  } catch (Throwable t) { warn("could not re-read " + @ES@.CFG + " after a hand edit (values kept): " + t); }
}""")''', '''      if (c == null) { warn("config.properties: " + KEYS[i] + "=" + raw + " is not valid (" + rule(i) + ") - keeping " + get(i)); continue; }
      put(i, c);
    }
    BROKEN = false;
  } catch (Throwable t) { warn("could not re-read " + @ES@.CFG + " after a hand edit (values kept): " + t); }
  // 0.1.6: gameplay.durability may have changed by hand - apply it now (idempotent; EssDurTick checks every second too)
  try { @PKG@.EssDur.sync(); } catch (Throwable t2) { }
}""")''')

# ================================================================================================ config kit rows
rep('KIT_CATS = [("parts", "Parts"), ("tpa", "Teleports"), ("msg", "Messages"), ("privacy", "Privacy"), ("warps", "Warps"), ("trade", "Trade")]',
    'KIT_CATS = [("parts", "Parts"), ("gameplay", "Gameplay"), ("tpa", "Teleports"), ("msg", "Messages"), ("privacy", "Privacy"), ("warps", "Warps"),\n'
    '            ("trade", "Trade")]')
rep('''     "field:TCfg.ENABLED" + CF + "tradeEnabled"),
    ("tpa.expireSeconds",''', '''     "field:TCfg.ENABLED" + CF + "tradeEnabled"),
    # 0.1.6: the item durability switch (Skyy 2026-09-30: off by default - tools, weapons and armor never break). live: EssDur zeroes /
    # restores the engine's durability costs at once (after= hook; EssDurTick re-checks every second for hand edits, import, restore,
    # undo). Only turning it ON asks (check= gives the question, confirm=on).
    ("gameplay.durability", "Item durability", "gameplay", "bool", "false", "", "", "", "", "live,danger",
     "Off: tools, weapons and armor never lose durability or break. Worn items keep their current value.",
     "field:EssDur.ON" + CF + "gameplay.durability;after=EssDur.changed;check=EssDur.check;confirm=on"),
    # 0.1.6: optional, separate from the switch (research 6): worn gear of everyone ONLINE back to full (world thread, compare-and-set,
    # metadata kept); cans, buckets, mugs and fertilizer are not wear and are skipped. danger = always asks.
    ("gameplay.repairOnline", "Repair gear of online players", "gameplay", "action", "", "", "", "Repair now", "", "danger",
     "Fills worn tools, weapons and armor of everyone online to full. Cans, buckets and charges skipped.",
     "action:EssDur.repairAction"),
    ("tpa.expireSeconds",''')

# ================================================================================================ plugin: setup / start / shutdown / ready line
rep('''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.EssTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  // 0.1.3: the admin config kit LAST''', '''  this.ticker = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.EssTick(), 2L, 2L, java.util.concurrent.TimeUnit.SECONDS);
  // 0.1.6: the item durability switch (gameplay.durability, default OFF). The death rule and the asset reload listeners are registered
  // here, each in its own try (a problem costs only that part); the asset costs are zeroed in start(), when every asset is loaded.
  // The engine fields are probed now (reflection only, nothing is written): a game update that changed them = the one UNAVAILABLE
  // warning here and the ready line says so (the Server Setup row cannot show it).
  String dNote = "item durability " + (@PKG@.EssDur.ON ? "ON - vanilla wear" : "OFF - tools, weapons and armor never wear or break");
  try { if (!@PKG@.EssDur.fields()) dNote = "item durability switch UNAVAILABLE on this game version - vanilla wear, whatever Server Setup says"; }
  catch (Throwable t6) { }
  try {
    getEntityStoreRegistry().registerSystem(new @PKG@.EssDurDeath());
    @PKG@.EssDur.DEATH_OK = true;
  } catch (Throwable t4) {
    dNote = dNote + ", death wear stays vanilla";
    @ES@.warn("could not order the item durability death rule between DeathSystems$PlayerDropItemsConfig and DeathSystems$DropPlayerDeathItems (" + t4 + ") - dying still costs durability while Item durability is OFF");
  }
  try {
    getEventRegistry().register(@LAE@.class, @ITEM@.class, new @PKG@.EssDurAssetL());
    getEventRegistry().register(@LAE@.class, @INTR@.class, new @PKG@.EssDurAssetL());
  } catch (Throwable t5) { @ES@.warn("could not listen for asset reloads (" + t5 + ") - items changed by a live asset reload keep their durability costs until a restart"); }
  // 0.1.3: the admin config kit LAST''')
rep('''+ rNote + "; " + tNote + "; " + wNote + "; config in SkyWynn Menu -> Server Setup (node skyyessentials.admin)");''',
    '''+ rNote + "; " + tNote + "; " + wNote + "; " + dNote + " (Server Setup > Essentials > Gameplay); config in SkyWynn Menu -> Server Setup (node skyyessentials.admin)");''')
rep('''protected void start() {
  @ES@.claimR();
}""")''', '''protected void start() {
  @ES@.claimR();
  // 0.1.6: every asset pack (mods included) is loaded now: apply the item durability switch + start its 1 s re-check
  try { @PKG@.EssDur.start(); } catch (Throwable t) { @ES@.warn("the item durability switch could not start: " + t); }
}""")''')
rep('''  @ES@.releaseR();
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''', '''  @ES@.releaseR();
  // 0.1.6: the original durability costs go back (a /plugin unload leaves vanilla behind) and the re-check stops
  try { @PKG@.EssDur.stop(); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }''')
rep('''MINE = [rq, es, hop, mv, rd, fly, tick] + OLD_CMDS + TRADE_ALL + TCMDS + [eperm, EWARP, wpage, pl]''',
    '''MINE = [rq, es, hop, mv, rd, fly, tick] + OLD_CMDS + TRADE_ALL + TCMDS + [eperm, EWARP, wpage] + DUR_ALL + [pl]''')
rep('''player switches that refuse /tpa and /msg (staff bypass), every setting in game''',
    '''player switches that refuse /tpa and /msg (staff bypass), an item durability switch (off by default: tools, weapons and armor never break), every setting in game''')

# ================================================================================================ checks on the result
code = s[s.index('\nimport sys, os\n'):]              # everything after the docstring
code_nc = "\n".join(l for l in code.split("\n") if not l.lstrip().startswith("#"))
assert s.count('"0.1.5"') == 0, "a 0.1.5 version string is left"
assert s.count("registerCommand(") == REG0, "no command added or removed"
assert s.count("registerSystem(") == SYS0 + 1 and code_nc.count("registerSystem(new @PKG@.EssDurDeath())") == 1, "exactly one new system"
# every registerSystem call registers a different class (engine rule: ONE registerSystem per class)
_rs = re.findall(r"registerSystem\(new ([\w@.]+)\(", code_nc)
assert len(_rs) == len(set(_rs)), "a class is registered twice: %s" % _rs
# EssDur is compiled before TCfg (reloadKit calls EssDur.sync) and every EssDur method before its first caller
_order = ["public static void info(String m) {\n  try { if (@ES@.LOG", "public static java.lang.reflect.Field fld(", "public static synchronized boolean fields(",
          "public static int off(", "public static int offInt(", "public static int restore(", "public static java.util.ArrayList snap(",
          "public static synchronized void pkFields(", "public static void clearRef(", "public static void dropPackets(",
          "public static int remembered(", "public static synchronized String applyLocked(", "public static String apply(boolean on)",
          "public static synchronized String syncLocked(boolean on)",
          "public static void sync()", "public static void changed(String key)", "public static String check(String key, String value)",
          "public static void assetsLoaded()", "public static boolean isWear(", "public static boolean needsRepair(",
          "public void done(int n, boolean mv)", "public EssRepairTask(", "public static Object[] repairAction(",
          "public EssDurTick()", "public static void start() {\n  RESCAN = false;\n  STARTED","public static void stop() {", "public EssDurDeath()",
          "# ================= TCfg: config.properties", "public static void reloadKit()"]
_ix = [code.index(x) for x in _order]
assert _ix == sorted(_ix), "EssDur methods out of order: %s" % [x[:40] for x, i in zip(_order, _ix) if i != sorted(_ix)[_order.index(x)]]
assert code.index('edur.addField(CtField.make("public static volatile boolean ON = false;", edur))') < code.index("kit = CFG.emit(")
# the kit row: default OFF, live + danger, only ON asks, bound to EssDur.ON with the after= / check= hooks; the loader key matches
assert '("gameplay.durability", "Item durability", "gameplay", "bool", "false", "", "", "", "", "live,danger",' in code
assert '"field:EssDur.ON" + CF + "gameplay.durability;after=EssDur.changed;check=EssDur.check;confirm=on"' in code
assert '("gameplay.durability", "Item durability", "bool", "@PKG@.EssDur.ON", 0, 1, "false", "",' in code
for _h in ("Off: tools, weapons and armor never lose durability or break. Worn items keep their current value.",
           "Fills worn tools, weapons and armor of everyone online to full. Cans, buckets and charges skipped."):
    assert code.count('"%s"' % _h) == 1 and len(_h) <= 100, "help text: " + _h
assert len("Turn item durability ON? Tools, weapons and armor wear out and can break again.") <= 200
# setup: the death system + listeners before the kit starts (nothing registered after CfgPub.start); start() applies; shutdown restores
_su = code[code.index("public void setup() {"):]
_su = _su[:_su.index('}""")')]
assert _su.index("registerSystem(new @PKG@.EssDurDeath())") < _su.index("CfgPub.start(")
assert _su.index("new @PKG@.EssDurAssetL()") < _su.index("CfgPub.start(") and _su.count("new @PKG@.EssDurAssetL()") == 2
assert "dNote" in _su[_su.index("CfgPub.start("):], "the ready line names the switch"
_st = code[code.index("protected void start() {"):]
_st = _st[:_st.index('}""")')]
assert "@PKG@.EssDur.start();" in _st and _st.index("@ES@.claimR();") < _st.index("@PKG@.EssDur.start();")
_sd = code[code.index("protected void shutdown() {"):]
_sd = _sd[:_sd.index('}""")')]
assert _sd.index("@PKG@.EssDur.stop();") < _sd.index("CfgPub.shutdown();") < _sd.index("super.shutdown();")
# the switch never writes an item stack: only the repair action does, and only through compare-and-set replaceItemStackInSlot
_ed = code[code.index("# 0.1.6 the item durability switch (research"):code.index("# ================= TCfg: config.properties")]
assert _ed.count("withDurability(") == 1 and _ed.count("replaceItemStackInSlot(") == 1 and "setItemStackForSlot" not in _ed
assert _ed.count("withIncreasedDurability") == 0 and "addItemStack" not in _ed and "removeItemStack" not in _ed
# 0.1.6 review: the asset reload listener (inside the engine's ASSET_LOCK) only raises the flag; the death rule honours BROKEN; the death
# rule is ordered before the respawn page explicitly; the ready line probes the fields before the kit starts
_al = _ed[_ed.index("public static void assetsLoaded() {"):]
_al = _al[:_al.index('}""")')]
assert "RESCAN = true;" in _al and "applyLocked" not in _al and "sync" not in _al and "getAssetMap" not in _al and "synchronized" not in _al
assert "if (!@PKG@.EssDur.ON && !@PKG@.EssDur.BROKEN && c instanceof @DTHC@)" in _ed
assert "this.deps.add(new @SDEP@(@ORD@.BEFORE, @PDSC@.class));" in _ed
assert _su.index("@PKG@.EssDur.fields()") < _su.index("CfgPub.start(") and "UNAVAILABLE" in _su
assert "B.deploy(" not in code and "enable_in_world(" not in code
for ident in re.findall(r"#(Skyy[A-Za-z0-9_]*)", code):
    assert "_" not in ident, "UI id with an underscore: " + ident

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(line endings %s)" % ("CRLF" if NL == CR + LF else "LF"))
